import os
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False, context_missing='LOG_ERROR')
xray_recorder.begin_segment(name="none")
from fathomapi.api.config import Config
os.environ['CODEBUILD_RUN'] = 'TRUE'

os.environ['ENVIRONMENT'] = 'dev'
Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                             'body_part_mapping_filename': 'body_part_mapping_fathom.json',
                             'movement_library_filename': 'movement_library_demo.json',
                             'cardio_data_filename': 'cardiorespiratory_data_soflete.json',
                             'hr_rpe_model_filename': 'hr_rpe.joblib',
                             'bodyweight_ratio_model_filename': 'bodyweight_ratio.joblib',
                             'model_bucket': 'biometrix-globalmodels',
                             'action_library_filename': 'actions_library.json',
                             }
           )

from copy import deepcopy
import pandas as pd
import numpy as np
import json
from models.planned_exercise import PlannedWorkoutLoad
from logic.periodization_processor import WorkoutScoringManager
from models.ranked_types import RankedAdaptationType
from models.soreness_base import BodyPartLocation
from models.movement_tags import AdaptationDictionary, AdaptationTypeMeasure, DetailedAdaptationType
from sklearn.model_selection import train_test_split
from ml_training.workout_scoring.workout_scoring_utilities import get_template_workouts, randomize_template_workout

all_muscles = list(BodyPartLocation.muscle_groups())


########## Scoring #######
def is_workout_selected(test_workout, template_workout, event: dict):
    if template_workout.acceptable_session_rpe is not None:
        if template_workout.acceptable_session_rpe.upper_bound is not None and (
                template_workout.acceptable_session_rpe.lower_bound <= test_workout.projected_session_rpe.lower_bound and test_workout.projected_rpe_load.upper_bound <= template_workout.acceptable_session_rpe.upper_bound):
            rpe_score = 1.0
        elif template_workout.acceptable_session_rpe.upper_bound is not None and (
                test_workout.projected_session_rpe.upper_bound > template_workout.acceptable_session_rpe.upper_bound):
            rpe_score = 0.0
        elif template_workout.acceptable_session_rpe.lower_bound <= test_workout.projected_session_rpe.lower_bound:
            rpe_score = 1.0
        elif test_workout.projected_session_rpe.upper_bound > template_workout.acceptable_session_rpe.upper_bound:
            rpe_score = 0.0
        else:
            rpe_score = test_workout.projected_session_rpe.lower_bound / template_workout.acceptable_session_rpe.lower_bound
    else:
        rpe_score = 1.0

    if template_workout.acceptable_session_duration is not None:
        if template_workout.acceptable_session_duration.lower_bound <= test_workout.duration <= template_workout.acceptable_session_duration.upper_bound:
            duration_score = 1.0
        elif test_workout.duration > template_workout.acceptable_session_duration.upper_bound:
            duration_score = template_workout.acceptable_session_duration.upper_bound / test_workout.duration

        else:
            duration_score = test_workout.duration / template_workout.acceptable_session_duration.lower_bound
    else:
        duration_score = 1.0

    if template_workout.acceptable_session_rpe_load is not None:
        if template_workout.acceptable_session_rpe_load.upper_bound is not None and (
                template_workout.acceptable_session_rpe_load.lower_bound <= test_workout.projected_rpe_load.lower_bound and test_workout.projected_rpe_load.upper_bound <= template_workout.acceptable_session_rpe_load.upper_bound):
            rpe_load_score = 1.0
        elif template_workout.acceptable_session_rpe_load.upper_bound is not None and (test_workout.projected_rpe_load.upper_bound > template_workout.acceptable_session_rpe_load.upper_bound):
            rpe_load_score = 0.0
        elif template_workout.acceptable_session_rpe_load.lower_bound <= test_workout.projected_rpe_load.lower_bound:
            rpe_load_score = 1.0
        elif test_workout.projected_rpe_load.upper_bound > template_workout.acceptable_session_rpe_load.upper_bound:
            rpe_load_score = 0.0
        else:
            rpe_load_score = test_workout.projected_rpe_load.lower_bound / template_workout.acceptable_session_rpe_load.lower_bound
    else:
        rpe_load_score = 1.0


    template_workout.adaptation_type_ranking = convert_sub_to_detail_adaptation_type(template_workout.adaptation_type_ranking)

    adaptation_type_score = WorkoutScoringManager.cosine_similarity(
            test_workout.session_detailed_load.detailed_adaptation_types,
            template_workout.adaptation_type_ranking
    )

    muscle_score =  WorkoutScoringManager.muscle_cosine_similarity(test_workout.ranked_muscle_detailed_load, template_workout.muscle_load_ranking)

    composite_score = (
            rpe_score * .2 +
            duration_score * .2 +
            rpe_load_score * .2 +
            adaptation_type_score * .2 +
            muscle_score * .2
    )

    workout_match = np.random.binomial(1, composite_score)
    # if composite_score >= .5:
    #     workout_match = 1.0
    # else:
    #     workout_match = 0.0

    event['rpe_score'] = rpe_score
    event['duration_score'] = duration_score
    event['rpe_load_score'] = rpe_load_score
    event['adaptation_type_score'] = adaptation_type_score
    event['muscle_score'] = muscle_score
    event['score'] = composite_score
    event['match'] = workout_match
    return workout_match, composite_score


def convert_sub_to_detail_adaptation_type(adaptation_type_ranking):
    adaptation_dictionary = AdaptationDictionary().detailed_types
    sub_adaptation_dictionary = {}
    for detail_type, sub_type in adaptation_dictionary.items():
        if sub_type not in sub_adaptation_dictionary:
            sub_adaptation_dictionary[sub_type] = [detail_type]
        else:
            sub_adaptation_dictionary[sub_type].append(detail_type)

    new_adaptation_type_rankings = []
    for ranked_adaptation_type in adaptation_type_ranking:
        if ranked_adaptation_type.adaptation_type_measure == AdaptationTypeMeasure.sub_adaptation_type:
            detail_types = sub_adaptation_dictionary.get(ranked_adaptation_type.adaptation_type)
            for detail_type in detail_types:
                new_ranked_type = RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, detail_type, ranked_adaptation_type.ranking, ranked_adaptation_type.duration)
                new_adaptation_type_rankings.append(new_ranked_type)

    adaptation_type_ranking.extend(new_adaptation_type_rankings)
    adaptation_type_ranking = [rat for rat in adaptation_type_ranking if rat.adaptation_type_measure != AdaptationTypeMeasure.sub_adaptation_type]
    adaptation_type_ranking.sort(key=lambda x: x.ranking)
    return adaptation_type_ranking


def get_normalized_muscle_load(test_workout):

    highest_muscle_load = 0
    for s in test_workout.ranked_muscle_detailed_load:
        highest_muscle_load = max(s.power_load.highest_value(), highest_muscle_load)
    test_workout_muscle_load_ranking = {}
    ranked_muscles = [rb.body_part_location for rb in test_workout.ranked_muscle_detailed_load]
    for muscle in all_muscles:
        if muscle in ranked_muscles:
            muscle_load = [ranked_muscle.power_load.highest_value() for ranked_muscle in test_workout.ranked_muscle_detailed_load if ranked_muscle.body_part_location == muscle][0]
            muscle_load = muscle_load / highest_muscle_load * 100
            test_workout_muscle_load_ranking[muscle] = muscle_load
        else:
            test_workout_muscle_load_ranking[muscle] = 0.0
    test_workout.ranked_muscle_detailed_load = test_workout_muscle_load_ranking


#########SCORING#############
def get_template_workout_features(template_workout):
    features = {}
    for attribute in ['rpe', 'duration', 'rpe_load', 'power_load']:
        for limit in ['lower', 'upper']:
            features[f'{attribute}_{limit}_template'] = getattr(getattr(template_workout, f'acceptable_session_{attribute}'), f'{limit}_bound') or 0

    for muscle, required_load in template_workout.muscle_load_ranking.items():
        features[f'{muscle.name}_template'] = required_load or 0

    at_features = {}
    ranked_types = [rat.adaptation_type for rat in template_workout.adaptation_type_ranking]
    for detailed_adaptation_type in DetailedAdaptationType:
        if detailed_adaptation_type not in ranked_types:
            at_features[f'{detailed_adaptation_type.name}_template'] = 0
            at_features[f'{detailed_adaptation_type.name}_duration_template'] = 0
        else:
            ranked_adaptation_type = [rat for rat in template_workout.adaptation_type_ranking if rat.adaptation_type == detailed_adaptation_type][0]
            at_features[f'{detailed_adaptation_type.name}_template'] = ranked_adaptation_type.ranking or 0
            at_features[f'{detailed_adaptation_type.name}_duration_template'] = ranked_adaptation_type.duration or 0

    features.update(at_features)

    return features


def get_library_workout_features(library_workout):
    features = {}
    features['duration_library'] = library_workout.duration
    features['rpe_lower_library'] = library_workout.projected_session_rpe.lower_bound or 0
    features['rpe_observed_library'] = library_workout.projected_session_rpe.observed_value or 0
    features['rpe_upper_library'] = library_workout.projected_session_rpe.upper_bound or 0

    for attribute in ['rpe_load', 'power_load']:
        for limit in ['lower', 'upper']:
            features[f'{attribute}_{limit}_library'] = getattr(getattr(library_workout, f'projected_{attribute}'), f'{limit}_bound') or 0


    for muscle, muscle_load in library_workout.ranked_muscle_detailed_load.items():
        features[f'{muscle.name}_library'] = muscle_load or 0

    at_features = {}
    ranked_dat = [rat.adaptation_type for rat in library_workout.session_detailed_load.detailed_adaptation_types]
    for detailed_adaptation_type in DetailedAdaptationType:
        if detailed_adaptation_type not in ranked_dat:
            at_features[f'{detailed_adaptation_type.name}_library'] = 0
            at_features[f'{detailed_adaptation_type.name}_duration_library'] = 0
        else:
            ranked_adaptation_type = [rat for rat in library_workout.session_detailed_load.detailed_adaptation_types if rat.adaptation_type == detailed_adaptation_type][0]
            at_features[f'{detailed_adaptation_type.name}_library'] = ranked_adaptation_type.ranking or 0
            at_features[f'{detailed_adaptation_type.name}_duration_library'] = ranked_adaptation_type.duration or 0

    features.update(at_features)
    return features


def read_library():
    with open('../../apigateway/models/planned_workout_library.json', 'r') as f:
        json_data = json.load(f)
    workouts = list(json_data.values())
    all_library_workouts = []
    all_library_workout_features = []

    for workout in workouts:
        library_workout = PlannedWorkoutLoad.json_deserialise(workout)
        get_normalized_muscle_load(library_workout)
        all_library_workouts.append(library_workout)
        all_library_workout_features.append(get_library_workout_features(library_workout))

    return all_library_workouts, all_library_workout_features

def run():
    all_events = []
    workout_library, workout_library_features = read_library()

    template_workouts = get_template_workouts()
    count = 0
    for library_workout, features_lw in zip(workout_library, workout_library_features):
        for t_w in template_workouts:
            template_workout = deepcopy(t_w)
            count += 1
            randomize_template_workout(template_workout)
            event = {}
            event.update(features_lw)
            event.update(get_template_workout_features(template_workout))
            workout_match, score = is_workout_selected(library_workout, template_workout, event)
            all_events.append(event)
    data = pd.DataFrame(all_events)
    np.random.seed(1000)
    training_data, validation_data = train_test_split(data, test_size=0.2)
    training_data.to_csv('data/training_data_binom.csv', index=False)
    validation_data.to_csv('data/validation_data_binom.csv', index=False)
run()
