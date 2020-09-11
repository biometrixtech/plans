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


import pandas as pd
import numpy as np
import json
from models.planned_exercise import PlannedWorkoutLoad
from logic.periodization_processor import WorkoutScoringManager
from models.periodization import PeriodizedExercise, RequiredExerciseFactory, PeriodizationModelFactory, PeriodizationPersona, TrainingPhaseType, TemplateWorkout
from models.periodization_goal import PeriodizationGoalType
from models.training_volume import StandardErrorRange
from models.ranked_types import RankedBodyPart, RankedAdaptationType
from models.soreness_base import BodyPartLocation
from models.movement_tags import AdaptationDictionary, AdaptationTypeMeasure, SubAdaptationType, DetailedAdaptationType

from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import *
from math import sqrt
from ml_training.workout_scoring.workout_scoring_utilities import get_template_workout


from keras.models import Sequential
from keras.layers import Dense
from keras.utils import to_categorical

from keras.wrappers.scikit_learn import KerasClassifier
########## Analyzing Data ##########
def get_muscle_distribution(workouts):
    muscles = {}
    for workout in workouts:
        lib_workout = PlannedWorkoutLoad.json_deserialise(workout)
        for ranked_body_part in lib_workout.ranked_muscle_detailed_load:
            body_part = ranked_body_part.body_part_location.name
            if body_part not in muscles:
                muscles[body_part] = {
                    'body_part': body_part
                }
                for ranking in range(1, 22):
                    muscles[body_part][f"rank_{ranking}"] = 0
            muscles[body_part][ f"rank_{ranked_body_part.ranking}"] += 1
    muscles_pd = pd.DataFrame(muscles.values())
    muscles_pd.to_csv('data/ranked_muscles.csv', index=False)


def get_detailed_adaptation_type_distribution(workouts):
    detailed_adaptation_types = {}
    for workout in workouts:
        lib_workout = PlannedWorkoutLoad.json_deserialise(workout)
        for ranked_detail_adaptation_type in lib_workout.session_detailed_load.detailed_adaptation_types:
            detailed_adaptation_type = ranked_detail_adaptation_type.adaptation_type.name
            if detailed_adaptation_type not in detailed_adaptation_types:
                detailed_adaptation_types[detailed_adaptation_type] = {
                    'detailed_adaptation_type': detailed_adaptation_type
                }
                for ranking in range(1, 18):
                    detailed_adaptation_types[detailed_adaptation_type][f"rank_{ranking}"] = 0
            detailed_adaptation_types[detailed_adaptation_type][ f"rank_{ranked_detail_adaptation_type.ranking}"] += 1
    detailed_adaptation_types_pd = pd.DataFrame(detailed_adaptation_types.values())
    detailed_adaptation_types_pd.to_csv('data/detailed_adaptation_types.csv', index=False)

######### Simulating data ##########

# def get_template_workout():
#     from logic.periodization_processor import PeriodizationPlanProcessor
#     from datetime import datetime
#     proc = PeriodizationPlanProcessor(datetime.now(), PeriodizationGoalType.increase_cardiovascular_health,
#                                       PeriodizationPersona.well_trained, TrainingPhaseType.increase, None, None)
#     model = proc.model
#     template_workout = TemplateWorkout()
    print('here')



def get_periodization_model():
    model = PeriodizationModelFactory().create(
            persona=PeriodizationPersona.well_trained,
            training_phase_type=TrainingPhaseType.slowly_increase,
            periodization_goal=PeriodizationGoalType.increase_cardiovascular_health
    )
    return model

def get_periodized_exercises():

    low_intensity_cardio = PeriodizedExercise(None, SubAdaptationType.cardiorespiratory_training,
                                       times_per_week_range=StandardErrorRange(lower_bound=5),
                                       duration_range=StandardErrorRange(lower_bound=30 * 60, upper_bound=60 * 60),
                                       rpe_range=StandardErrorRange(lower_bound=1, upper_bound=3))
    mod_intensity_cardio = PeriodizedExercise(None, SubAdaptationType.cardiorespiratory_training,
                                       times_per_week_range=StandardErrorRange(lower_bound=5),
                                       duration_range=StandardErrorRange(lower_bound=30 * 60, upper_bound=60 * 60),
                                       rpe_range=StandardErrorRange(lower_bound=3, upper_bound=5))

    vigorous_intensity_cardio = PeriodizedExercise(None, SubAdaptationType.cardiorespiratory_training,
                                            times_per_week_range=StandardErrorRange(lower_bound=3),
                                            duration_range=StandardErrorRange(lower_bound=20 * 60,
                                                                              upper_bound=60 * 60),
                                            rpe_range=StandardErrorRange(lower_bound=6, upper_bound=10))
    # define rpe and duration
    strength = PeriodizedExercise(None, SubAdaptationType.strength,
                                   times_per_week_range=StandardErrorRange(lower_bound=2), duration_range=None,
                                   rpe_range=None)

    # core strength
    core_strength = PeriodizedExercise(None, SubAdaptationType.core_strength,
                                   times_per_week_range=StandardErrorRange(lower_bound=2), duration_range=None,
                                   rpe_range=None)


    # power
    power = PeriodizedExercise(None, SubAdaptationType.power,
                                   times_per_week_range=StandardErrorRange(lower_bound=2), duration_range=None,
                                   rpe_range=None)


    return [low_intensity_cardio, mod_intensity_cardio, vigorous_intensity_cardio, strength, core_strength, power]

def add_detail_adaptation_type(recommended_workout):
    if recommended_workout.sub_adaptation_type == SubAdaptationType.cardiorespiratory_training:
        recommended_workout.detailed_adaptation_type = DetailedAdaptationType(np.random.choice([
            DetailedAdaptationType.base_aerobic_training,
            DetailedAdaptationType.anaerobic_threshold_training,
            DetailedAdaptationType.high_intensity_anaerobic_training
        ]))
    elif recommended_workout.sub_adaptation_type == SubAdaptationType.core_strength:
        recommended_workout.detailed_adaptation_type = DetailedAdaptationType(np.random.choice([
            DetailedAdaptationType.stabilization_endurance,
            DetailedAdaptationType.stabilization_strength,
            DetailedAdaptationType.sustained_power,
        ]))
    elif recommended_workout.sub_adaptation_type == SubAdaptationType.strength:
        recommended_workout.detailed_adaptation_type = DetailedAdaptationType(np.random.choice([
            DetailedAdaptationType.functional_strength,
            DetailedAdaptationType.strength_endurance,
            DetailedAdaptationType.muscular_endurance,
            DetailedAdaptationType.maximal_power
        ]))
    elif recommended_workout.sub_adaptation_type == SubAdaptationType.power:
        recommended_workout.detailed_adaptation_type = DetailedAdaptationType(np.random.choice([
            DetailedAdaptationType.sustained_power,
            DetailedAdaptationType.speed,
            DetailedAdaptationType.power,
            DetailedAdaptationType.maximal_power
        ]))


def get_ranked_muscle_needs():
    muscle_groups = list(BodyPartLocation.muscle_groups())
    muscle_groups_subset = np.random.choice(muscle_groups, replace=False, size=np.random.randint(2, 21, 1)[0])
    np.random.shuffle(muscle_groups_subset)
    ranked_muscles =  [RankedBodyPart(bp, i) for bp, i in zip(muscle_groups_subset, range(1, len(muscle_groups_subset)))]
    return ranked_muscles

    # print('here')


def get_target_range():
    values = np.random.uniform(50, 300, 10)
    target_range = StandardErrorRange(lower_bound=min(values), upper_bound=max(values))
    return target_range


def get_strain_and_monotony(workout):
    workout.projected_monotony = StandardErrorRange()
    # workout.projected_monotony.observed_value = np.random.choice([1, 1.75, 2.5])  # this will get score of [1, .5, 0]
    workout.projected_monotony.observed_value = np.random.uniform(1, 2.5, 1)[0]  # this will get score of [1, .5, 0]

    workout.projected_strain_event_level = StandardErrorRange()
    workout.projected_strain_event_level.observed_value = np.random.choice([0, 1, 2]) # this will get score of [1, .5, 0]
    # workout.projected_strain_event_level.observed_value = np.random.uniform([0, 1, 2]) # this will get score of [1, .5, 0]

########## Scoring #######
def is_workout_selected(test_workout, template_workout):
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


    if template_workout.acceptable_session_power_load is not None:
        if template_workout.acceptable_session_power_load.upper_bound is not None and (
                template_workout.acceptable_session_power_load.lower_bound <= test_workout.projected_rpe_load.lower_bound and test_workout.projected_rpe_load.upper_bound <= template_workout.acceptable_session_power_load.upper_bound):
            power_load_score = 1.0
        elif template_workout.acceptable_session_power_load.upper_bound is not None and (test_workout.projected_rpe_load.upper_bound > template_workout.acceptable_session_power_load.upper_bound):
            power_load_score = 0.0
        elif template_workout.acceptable_session_power_load.lower_bound <= test_workout.projected_rpe_load.lower_bound:
            power_load_score = 1.0
        elif test_workout.projected_rpe_load.upper_bound > template_workout.acceptable_session_power_load.upper_bound:
            power_load_score = 0.0
        else:
            power_load_score = test_workout.projected_rpe_load.lower_bound / template_workout.acceptable_session_power_load.lower_bound
    else:
        power_load_score = 1.0

    convert_sub_to_detail_adaptation_type(template_workout.adaptation_type_ranking)


    # cosine_similarity_sat = WorkoutScoringManager.cosine_similarity(
    #         test_workout.session_detailed_load.sub_adaptation_types,
    #         template_workout.adaptation_type_ranking
    # )
                                                                #
                                                                # [RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type,
                                                                #                       template_workout.sub_adaptation_type,
                                                                #                       1,
                                                                #                       np.random.choice([20, 25, 30], 1)[0])])

    cosine_similarity_dat = WorkoutScoringManager.cosine_similarity(
            test_workout.session_detailed_load.detailed_adaptation_types,
            template_workout.adaptation_type_ranking
    )
                                                                # [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,
                                                                #                       template_workout.detailed_adaptation_type,
                                                                #                       1,
                                                                #                       np.random.choice([20, 25, 30], 1)[0])])


    get_normalized_muscle_load(test_workout)

    muscle_score = get_muscle_cosine_similarity(test_workout.ranked_muscle_detailed_load, template_workout.muscle_load_ranking)

    composite_score = (
            rpe_score * .2 +
            duration_score * .2 +
            rpe_load_score * .2 +
            # power_load_score * .1 +
            # cosine_similarity_sat * .1 +
            cosine_similarity_dat * .2 +
            muscle_score * .2
    )
    print(f"rpe: {rpe_score},"
          f"duration: {duration_score},"
          f"rpe_load: {rpe_load_score},"
          # f"power_load: {power_load_score},"
          f"dat: {cosine_similarity_dat},"
          f"muscle: {muscle_score}"
          f"composite: {composite_score}")
    if composite_score < 0:
        print('here')
    if cosine_similarity_dat != 0.07106690545187014:
        print('here')

    workout_match = np.random.binomial(1, composite_score)
    # workout_match = np.round(composite_score, 0)
    return workout_match, composite_score


def convert_sub_to_detail_adaptation_type(adaptation_type_ranking):
    # adaptation_type_ranking.append(RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type, SubAdaptationType.power, 6, None))

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

def get_normalized_muscle_load(test_workout):

    highest_muscle_load = 0
    for s in test_workout.ranked_muscle_detailed_load:
        highest_muscle_load = max(s.power_load.highest_value(), highest_muscle_load)
    test_workout_muscle_load_ranking = {}
    all_muscles = list(BodyPartLocation.muscle_groups())
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
def get_muscle_cosine_similarity(test_muscle_load, template_muscle_load):
    # get the adaptation types separately so we can look for matches of type (but not necessarily ranking)
    candidate_muscles = [m for m, load in test_muscle_load.items() if load > 0]
    recommended_muscles = [m for m, load in template_muscle_load.items() if load > 0]
    all_used_muscles = set(candidate_muscles).union(recommended_muscles)


    all_muscles = list(template_muscle_load.keys())
    candidate_loads = [test_muscle_load.get(muscle, 0) or 0 for muscle in all_muscles]
    recommended_loads = [template_muscle_load.get(muscle, 0) or 0 for muscle in all_muscles]

    difference = [abs(cand - rec) for cand, rec in zip(candidate_loads, recommended_loads)]
    percent_covered = [max([1 - diff / rec, 0]) for diff, rec in zip(difference, recommended_loads) if rec > 0]
    if len(percent_covered) > 0:
        cosine_similarity_1 = sum(percent_covered) / len(percent_covered)
    else:
        cosine_similarity_1 = 0

    dotprod_2 = sum(
            (1 if k in candidate_muscles else 0) * (1 if k in recommended_muscles else 0) for k
            in all_used_muscles)
    magA_2 = sqrt(sum((1 if k in candidate_muscles else 0) ** 2 for k in all_used_muscles))
    magB_2 = sqrt(sum((1 if k in recommended_muscles else 0) ** 2 for k in all_used_muscles))
    if (magA_2 * magB_2) == 0:
        cosine_similarity_2 = 0
    else:
        cosine_similarity_2 = dotprod_2 / (magA_2 * magB_2)

    average_cosine_similarity = (cosine_similarity_1 + cosine_similarity_2) / 2

    return average_cosine_similarity




def get_workout_features(library_workout, recommended_workouts):
    events = []
    all_muscles = list(BodyPartLocation.muscle_groups())
    # recommended_workout = np.random.choice(periodization_model.one_required_exercises)
    for recommended_workout in recommended_workouts:
        if recommended_workout.duration is None:
            recommended_workout.duration = StandardErrorRange(lower_bound=(library_workout.duration - 1), upper_bound=(library_workout.duration + 1))
        if recommended_workout.rpe is None:
            recommended_workout.rpe = StandardErrorRange(lower_bound=library_workout.projected_session_rpe.lower_bound, upper_bound=library_workout.projected_session_rpe.upper_bound)
        # recommended_workout.duration.divide(60)
        # progression = np.random.choice(periodization_model.progressions)
        required_muscles = get_ranked_muscle_needs()

        target_load_range = get_target_range()

        # get_strain_and_monotony(library_workout)
        add_detail_adaptation_type(recommended_workout)

        for rdat in library_workout.session_detailed_load.detailed_adaptation_types:
            rdat.duration = np.random.choice([20, 25, 30], 1)[0]
        for rsat in library_workout.session_detailed_load.sub_adaptation_types:
            rsat.duration = np.random.choice([20, 25, 30], 1)[0]
        workout_match, score = is_workout_selected(library_workout, recommended_workout, target_load_range, required_muscles)

        sat_features_lw = {}
        lw_sub_adaptation_types = [sat.adaptation_type for sat in library_workout.session_detailed_load.sub_adaptation_types]
        for sub_adaptation_type in SubAdaptationType:
            if sub_adaptation_type in lw_sub_adaptation_types:
                sat_features_lw[f"{sub_adaptation_type.name}_lw"] = [sat.ranking for sat in library_workout.session_detailed_load.sub_adaptation_types if sat.adaptation_type == sub_adaptation_type][0]
            else:
                sat_features_lw[f"{sub_adaptation_type.name}_lw"] = 0

        dat_features_lw = {}
        lw_detailed_adaptation_types = [sat.adaptation_type for sat in library_workout.session_detailed_load.detailed_adaptation_types]
        for detailed_adaptation_type in DetailedAdaptationType:
            if detailed_adaptation_type in lw_detailed_adaptation_types:
                dat_features_lw[f"{detailed_adaptation_type.name}_lw"] = [dat.ranking for dat in library_workout.session_detailed_load.detailed_adaptation_types if dat.adaptation_type == detailed_adaptation_type][0]
            else:
                dat_features_lw[f"{detailed_adaptation_type.name}_lw"] = 0


        muscles_features_lw = {}
        lw_ranked_muscles = [rb.body_part_location for rb in library_workout.ranked_muscle_detailed_load]
        for muscle in all_muscles:
            if muscle in lw_ranked_muscles:
                muscles_features_lw[f"{muscle.name}_lw"] = [bp.ranking for bp in library_workout.ranked_muscle_detailed_load if bp.body_part_location == muscle][0]
            else:
                muscles_features_lw[f"{muscle.name}_lw"] = 0
        muscle_score = get_muscle_cosine_similarity(library_workout.ranked_muscle_detailed_load, required_muscles)



        cosine_similarity_detailed = WorkoutScoringManager.cosine_similarity(library_workout.session_detailed_load.detailed_adaptation_types,
                                                                             [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,
                                                                                                   recommended_workout.detailed_adaptation_type,
                                                                                                   1, np.random.choice([20, 25, 30], 1)[0])])


        cosine_similarity_sub = WorkoutScoringManager.cosine_similarity(library_workout.session_detailed_load.sub_adaptation_types,
                                                                             [RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type,
                                                                                                   recommended_workout.sub_adaptation_type,
                                                                                                   1, np.random.choice([20, 25, 30], 1)[0])])

        features_lw = {
            'duration_lw': library_workout.duration,
            'rpe_lower_lw': library_workout.projected_session_rpe.lower_bound,
            'rpe_observed_lw': library_workout.projected_session_rpe.observed_value,
            'rpe_upper_lw': library_workout.projected_session_rpe.upper_bound,
            'rpe_load_lower_lw': library_workout.projected_rpe_load.lower_bound,
            'rpe_load_upper_lw': library_workout.projected_rpe_load.upper_bound,
            'muscle_score': muscle_score,
            'detailed_adaptation_type_score': cosine_similarity_detailed,
            'sub_adaptation_type_score': cosine_similarity_sub
                # 'strain_lw': library_workout.projected_strain_event_level.observed_value,
                # 'monotony_lw': library_workout.projected_monotony.observed_value,
            }
        features_rw = {
            'duration_lower_rw': recommended_workout.duration.lower_bound,
            'duration_upper_rw': recommended_workout.duration.upper_bound,
            'rpe_lower_rw': recommended_workout.rpe.lower_bound,
            'rpe_upper_rw': recommended_workout.rpe.upper_bound,
            'rpe_load_lower_rw': target_load_range.lower_bound,
            'rpe_load_upper_rw': target_load_range.upper_bound,
        }
        sat_features_rw = {}
        # rw_sub_adaptation_tpes = [sat.adaptation_type for sat in recommended_workout.session_detailed_load.sub_adaptation_types]
        for sub_adaptation_type in SubAdaptationType:
            if sub_adaptation_type == recommended_workout.sub_adaptation_type:
                sat_features_rw[f"{sub_adaptation_type.name}_rw"] = 1
            else:
                sat_features_rw[f"{sub_adaptation_type.name}_rw"] = 0

        dat_features_rw = {}
        for detailed_adaptation_type in DetailedAdaptationType:
            if detailed_adaptation_type == recommended_workout.detailed_adaptation_type:
                dat_features_rw[f"{detailed_adaptation_type.name}_rw"] = 1
            else:
                dat_features_rw[f"{detailed_adaptation_type.name}_rw"] = 0

        muscles_features_rw = {}

        rw_ranked_muscles = [rb.body_part_location for rb in required_muscles]
        for muscle in all_muscles:
            if muscle in rw_ranked_muscles:
                muscles_features_rw[f"{muscle.name}_rw"] = [bp.ranking for bp in required_muscles if bp.body_part_location == muscle][0]
            else:
                muscles_features_rw[f"{muscle.name}_rw"] = 0
        features = {}
        features.update(features_lw)
        # features.update(sat_features_lw)
        # features.update(dat_features_lw)
        # features.update(muscles_features_lw)
        features.update(features_rw)
        # features.update(sat_features_rw)
        # features.update(dat_features_rw)
        # features.update(muscles_features_rw)

        features['match'] = workout_match
        features['score'] = score
        events.append(features)

    return events



def get_template_workout_features(template_workout):
    features = {}
    for attribute in ['rpe', 'duration', 'rpe_load', 'power_load']:
        for limit in ['lower', 'upper']:
            features[f'{attribute}_{limit}'] = getattr(getattr(template_workout, f'acceptable_session_{attribute}'), f'{limit}_bound')

    for muscle, required_load in template_workout.muscle_load_ranking.items():
        features[f'{muscle.name}'] = required_load

    at_features = {}
    ranked_types = [rat.adaptation_type for rat in template_workout.adaptation_type_ranking]
    for detailed_adaptation_type in DetailedAdaptationType:
        if detailed_adaptation_type not in ranked_types:
            at_features[f'detailed_{detailed_adaptation_type.name}'] = 0
            at_features[f'detailed_{detailed_adaptation_type.name}_duration'] = None
        else:
            ranked_adaptation_type = [rat for rat in template_workout.adaptation_type_ranking if rat.adaptation_type == detailed_adaptation_type][0]
            at_features[f'detailed_{detailed_adaptation_type.name}'] = ranked_adaptation_type.ranking
            at_features[f'detailed_{detailed_adaptation_type.name}_duration'] = ranked_adaptation_type.duration
    # for sub_adaptation_type in SubAdaptationType:
    #     if sub_adaptation_type not in ranked_types:
    #         at_features[f'sub_{sub_adaptation_type.name}'] = 0
    #         at_features[f'sub_{sub_adaptation_type.name}_duration'] = None
    #     else:
    #         ranked_adaptation_type = [rat for rat in template_workout.adaptation_type_ranking if rat.adaptation_type == sub_adaptation_type][0]
    #         at_features[f'sub_{sub_adaptation_type.name}'] = ranked_adaptation_type.ranking
    #         at_features[f'sub_{sub_adaptation_type.name}_duration'] = ranked_adaptation_type.duration

    features.update(at_features)
    return features


def get_library_workout_features(library_workout):
    features = {}
    features['duration'] = library_workout.duration
    features['rpe_lower'] = library_workout.projected_session_rpe.lower_bound
    features['rpe_observed'] = library_workout.projected_session_rpe.observed_value
    features['rpe_upper'] = library_workout.projected_session_rpe.upper_bound

    for attribute in ['rpe_load', 'power_load']:
        for limit in ['lower', 'upper']:
            features[f'{attribute}_{limit}'] = getattr(getattr(library_workout, f'projected_{attribute}'), f'{limit}_bound')

    highest_muscle_load = 0
    for s in library_workout.ranked_muscle_detailed_load:
        highest_muscle_load = max(s.power_load.highest_value(), highest_muscle_load)

    muscle_features = {}
    all_muscles = list(BodyPartLocation.muscle_groups())
    ranked_muscles = [rb.body_part_location for rb in library_workout.ranked_muscle_detailed_load]
    for muscle in all_muscles:
        if muscle in ranked_muscles:
            muscle_load = [ranked_muscle.power_load.highest_value() for ranked_muscle in library_workout.ranked_muscle_detailed_load if ranked_muscle.body_part_location == muscle][0]
            muscle_load = muscle_load / highest_muscle_load * 100
            muscle_features[f"{muscle.name}"] = muscle_load
        else:
            muscle_features[f"{muscle.name}"] = 0

    at_features = {}
    ranked_dat = [rat.adaptation_type for rat in library_workout.session_detailed_load.detailed_adaptation_types]
    for detailed_adaptation_type in DetailedAdaptationType:
        if detailed_adaptation_type not in ranked_dat:
            at_features[f'detailed_{detailed_adaptation_type.name}'] = 0
            at_features[f'detailed_{detailed_adaptation_type.name}_duration'] = None
        else:
            ranked_adaptation_type = [rat for rat in library_workout.session_detailed_load.detailed_adaptation_types if rat.adaptation_type == detailed_adaptation_type][0]
            at_features[f'detailed_{detailed_adaptation_type.name}'] = ranked_adaptation_type.ranking
            at_features[f'detailed_{detailed_adaptation_type.name}_duration'] = ranked_adaptation_type.duration

    # ranked_sat = [rat.adaptation_type for rat in library_workout.session_detailed_load.sub_adaptation_types]
    # for sub_adaptation_type in SubAdaptationType:
    #     if sub_adaptation_type not in ranked_sat:
    #         at_features[f'sub_{sub_adaptation_type.name}'] = 0
    #         at_features[f'sub_{sub_adaptation_type.name}_duration'] = None
    #     else:
    #         ranked_adaptation_type = [rat for rat in library_workout.session_detailed_load.sub_adaptation_types if rat.adaptation_type == sub_adaptation_type][0]
    #         at_features[f'sub_{sub_adaptation_type.name}'] = ranked_adaptation_type.ranking
    #         at_features[f'sub_{sub_adaptation_type.name}_duration'] = ranked_adaptation_type.duration
    features.update(muscle_features)
    features.update(at_features)
    return features



def load_data():
    # with open('data/planned_workout_library.json', 'r') as f:

    with open('../../apigateway/models/planned_workout_library.json', 'r') as f:
        json_data = json.load(f)
    workouts = json_data.values()
    # get_muscle_distribution(workouts)
    # get_detailed_adaptation_type_distribution(workouts)

    all_events = []

    # periodization_model = get_periodization_model()
    # recommended_workouts = []
    # recommended_workouts.extend(periodization_model.one_required_exercises)
    # recommended_workouts.extend(periodization_model.required_exercises)
    recommended_workouts = get_periodized_exercises()
    for recommended_workout in recommended_workouts:
        if recommended_workout.duration is not None:
            recommended_workout.duration.divide(60)
    for workout in workouts:
        lib_workout = PlannedWorkoutLoad.json_deserialise(workout)

        events = get_workout_features(lib_workout, recommended_workouts)
        all_events.extend(events)
    data = pd.DataFrame(all_events)
    print(data.shape, sum(data['match']))
    return data





def split_test_train(data):
    features_column = np.setdiff1d(data.columns, np.array(['match', 'score']))
    X = data[features_column]


    # x_columns = X.columns
    # from sklearn.preprocessing import scale
    # X = scale(X.values)
    # X = pd.DataFrame(X)
    # X.columns = x_columns

    y = data[['match', 'score']]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.2, random_state=1)
    test_score = y_test['score']
    del y_test['score'], y_train['score']
    return X_train, X_test, y_train, y_test, test_score

def get_predicted_outcome(model, data):
    return np.rint(model.predict(data))



def baseModel():
    seed = 7
    np.random.seed(seed)
    model = Sequential()
    init = 'normal'
    # dim = X.shape[1]

    # Y = to_categorical(Y)
    model.add(Dense(50, input_dim=96, kernel_initializer=init, activation='elu'))
    model.add(Dense(50, kernel_initializer=init, activation='elu'))
    # model.add(Dense(100, kernel_initializer=init, activation='elu'))
    # model.add(Dense(20, kernel_initializer=init, activation='elu'))
    # model.add(Dense(10, kernel_initializer=init, activation='elu'))
    model.add(Dense(5, kernel_initializer=init, activation='elu'))
    model.add(Dense(1, kernel_initializer=init, activation='sigmoid'))
    # Compile model
    model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model


def train_nn(X, Y):
    print(X.shape)

    estimator = KerasClassifier(build_fn=baseModel, epochs=20, batch_size=5, verbose=1)

    estimator.fit(X, Y)  #, epochs=20, batch_size=200, verbose=1)
    return estimator

def train_test(data):
    X_train, X_test, y_train, y_test, test_score = split_test_train(data)


    # model = LogisticRegression(max_iter=1000).fit(X_train, y_train)

    # model = GradientBoostingClassifier()
    # model.fit(X_train, y_train)
    model = train_nn(X_train, y_train)

    # y_train_pred = get_predicted_outcome(model, X_train)
    #
    # print('train precision: ' + str(precision_score(y_train, y_train_pred)))
    # print('train recall: ' + str(recall_score(y_train, y_train_pred)))
    # print('train accuracy: ' + str(accuracy_score(y_train, y_train_pred)))

    # y_test_pred = get_predicted_outcome(model, X_test)

    y_test_pred = model.predict(X_test)
    test_score_pred = model.predict_proba(X_test)
    # test_score_pred[:, 2] = test_score.values

    all_scores = pd.DataFrame(np.hstack((test_score_pred, test_score.values.reshape(-1, 1))))
    all_scores.columns = ['prob_0', 'test_score', 'real_score']
    all_scores['diff'] = np.abs(all_scores['real_score'] - all_scores['test_score'])
    all_scores['prediction'] = y_test_pred
    print(all_scores.describe(percentiles=[.25, .75, .9, .95, .99]))
    all_scores.to_csv('data/scores.csv')

    print('test precision: ' + str(precision_score(y_test, y_test_pred)))
    print('test recall: ' + str(recall_score(y_test, y_test_pred)))
    print('test accuracy: ' + str(accuracy_score(y_test, y_test_pred)))
    print('here')

def run():
    # # get_ranked_muscle_needs()
    # events = load_data()
    # events.to_csv('data/all_data.csv', index=False)
    events = pd.read_csv('data/all_data.csv')
    train_test(events)

    #
    # print(events.head())
    # print(events.columns)
    print('here')


def analyze_training_data():
    data = pd.read_csv('data/all_data.csv')
    import matplotlib.pyplot as plt
    plt.figure()
    plt.subplot(131)
    plt.hist(data.detailed_adaptation_type_score, weights=np.ones(len(data)) / len(data))
    plt.subplot(132)
    plt.hist(data.muscle_score, weights=np.ones(len(data)) / len(data))
    plt.subplot(133)
    plt.hist(data.sub_adaptation_type_score, weights=np.ones(len(data)) / len(data))
    print('here')



def cosine_sim():
    A = np.array([0, 30, 30, 0, 0])
    B = np.array([0, 25, 10, 0, 0])

    differences = np.abs(A - B)
    percent_covered = [ max([1 - diff / allotted, 0]) for diff, allotted in zip(differences, B) if allotted > 0]
    average_percent_covered = sum(percent_covered) / len(percent_covered)


    # A = np.array([0, 5, 30, 0, 0])
    # B = np.array([0, 0, 0, 0, 0])

    # A = A / sum(A)
    # A = list(A)
    # B = B / sum(B)
    # B = list(B)
    # from sklearn.metrics.pairwise import cosine_similarity
    # sim = cosine_similarity(A, B)


    mag_a = sqrt(sum([a**2 for a in A]))
    mag_b = sqrt(sum([b**2 for b in B]))

    dot_prod = sum([a * b for a,b in zip(A, B)])
    if mag_a * mag_b == 0:
        similarity = 0
    else:
        similarity = dot_prod / (mag_a * mag_b)
    print('here')


def read_library():
    with open('../../apigateway/models/planned_workout_library.json', 'r') as f:
        json_data = json.load(f)
    workouts = json_data.values()
    all_library_workouts = []
    for workout in workouts:
        all_library_workouts.append(PlannedWorkoutLoad.json_deserialise(workout))
    return all_library_workouts

def run2():
    workout_library = read_library()
    lw_features = get_library_workout_features(workout_library[0])

    template_workout = get_template_workout()
    tw_features = get_template_workout_features(template_workout)
    for library_workout in workout_library:
        workout_match, score = is_workout_selected(library_workout, template_workout)
        print(workout_match, score)

run2()
print('here')

# test_cosine()
# cosine_sim()
# run()
# analyze_training_data()


