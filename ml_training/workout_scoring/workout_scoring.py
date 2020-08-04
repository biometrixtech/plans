import pandas as pd
import numpy as np
import json
import os
from models.planned_exercise import PlannedWorkoutLoad
from logic.periodization_processor import WorkoutScoringManager
from models.periodization import PeriodizedExercise, RequiredExerciseFactory, PeriodizationGoal, PeriodizationModelFactory, PeriodizationPersona, TrainingPhaseType
from models.training_volume import StandardErrorRange
from models.movement_tags import AdaptationDictionary, RankedAdaptationType, AdaptationTypeMeasure, SubAdaptationType
from models.soreness_base import BodyPartLocation, RankedBodyPart

from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import *
from math import sqrt

def get_muscle_cosine_similarity(muscle_rank_library, muscle_rank_rec):
    # get the adaptation types separately so we can look for matches of type (but not necessarily ranking)
    # candidate_muscles = [c.adaptation_type for c in muscle_rank_library]
    # rec_muscles = [r.adaptation_type for r in muscle_rank_rec]
    # all_muscles = set(candidate_muscles).union(rec_muscles)

    all_muscle_priorities = set(muscle_rank_library).union(muscle_rank_rec)
    dotprod_1 = sum((1 if k in muscle_rank_library else 0) * (1 if k in muscle_rank_rec else 0) for k in all_muscle_priorities)
    magA_1 = sqrt(sum((1 if k in muscle_rank_library else 0) ** 2 for k in all_muscle_priorities))
    magB_1 = sqrt(sum((1 if k in muscle_rank_rec else 0) ** 2 for k in all_muscle_priorities))
    if (magA_1 * magB_1) == 0:
        cosine_similarity_1 = 0
    else:
        cosine_similarity_1 = dotprod_1 / (magA_1 * magB_1)

    # dotprod_2 = sum(
    #         (1 if k in candidate_adaptation_types else 0) * (1 if k in recommended_adaptation_types else 0) for k
    #         in all_adaptation_types)
    # magA_2 = sqrt(sum((1 if k in candidate_adaptation_types else 0) ** 2 for k in all_adaptation_types))
    # magB_2 = sqrt(sum((1 if k in recommended_adaptation_types else 0) ** 2 for k in all_adaptation_types))
    # if (magA_2 * magB_2) == 0:
    #     cosine_similarity_2 = 0
    # else:
    #     cosine_similarity_2 = dotprod_2 / (magA_2 * magB_2)

    # average_cosine_similarity = (cosine_similarity_1 + cosine_similarity_2) / 2

    return cosine_similarity_1



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


def get_workout_features(library_workout, recommended_workouts):
    events = []
    for recommended_workout in recommended_workouts:
    # recommended_workout = np.random.choice(periodization_model.one_required_exercises)
        if recommended_workout.duration is None:
            recommended_workout.duration = StandardErrorRange(lower_bound=(library_workout.duration - 1), upper_bound=(library_workout.duration + 1))
        if recommended_workout.rpe is None:
            recommended_workout.rpe = StandardErrorRange(lower_bound=library_workout.projected_session_rpe.lower_bound, upper_bound=library_workout.projected_session_rpe.upper_bound)
        # recommended_workout.duration.divide(60)
        # progression = np.random.choice(periodization_model.progressions)
        required_muscles = get_ranked_muscle_needs()
        library_workout_muscles = library_workout.ranked_muscle_detailed_load

        target_load_range = get_target_range()

        get_strain_and_monotony(library_workout)

        workout_match, score = is_workout_selected(library_workout, recommended_workout, target_load_range, required_muscles)
        sat_features_lw = {}
        lw_sub_adaptation_types = [sat.adaptation_type for sat in library_workout.session_detailed_load.sub_adaptation_types]
        for sub_adaptation_type in SubAdaptationType:
            if sub_adaptation_type in lw_sub_adaptation_types:
                sat_features_lw[f"{sub_adaptation_type.name}_lw"] = [sat.ranking for sat in library_workout.session_detailed_load.sub_adaptation_types if sat.adaptation_type == sub_adaptation_type][0]
            else:
                sat_features_lw[f"{sub_adaptation_type.name}_lw"] = 0

        features_lw = {
            'duration_lw': library_workout.duration,
            'rpe_lower_lw': library_workout.projected_session_rpe.lower_bound,
            'rpe_observed_lw': library_workout.projected_session_rpe.observed_value,
            'rpe_upper_lw': library_workout.projected_session_rpe.upper_bound,
            'rpe_load_lower_lw': library_workout.projected_rpe_load.lower_bound,
            'rpe_load_upper_lw': library_workout.projected_rpe_load.upper_bound,
            'strain_lw': library_workout.projected_strain_event_level.observed_value,
            'monotony_lw': library_workout.projected_monotony.observed_value,
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

        features = {}
        features.update(features_lw)
        features.update(sat_features_lw)
        features.update(features_rw)
        features.update(sat_features_rw)
        features['match'] = workout_match
        features['score'] = score
        events.append(features)

    return events


def load_data():
    with open('data/planned_workout_library.json', 'r') as f:
        json_data = json.load(f)
    workouts = json_data.values()
    # get_muscle_distribution(workouts)

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


def get_periodization_model():
    model = PeriodizationModelFactory().create(
            persona=PeriodizationPersona.well_trained,
            training_phase_type=TrainingPhaseType.slowly_increase,
            periodization_goal=PeriodizationGoal.improve_cardiovascular_health
    )

    # ex = RequiredExerciseFactory().get_one_required_exercises(PeriodizationGoal.improve_cardiovascular_health)
    # ex = np.random.choice(ex)
    # return ex
    return model

def is_workout_selected(test_workout, recommended_exercise, target_load_range, target_ranked_muscles):
    if recommended_exercise.rpe is not None:
        if recommended_exercise.rpe.upper_bound is not None and (
                recommended_exercise.rpe.lower_bound <= test_workout.projected_session_rpe.lower_bound and test_workout.projected_rpe_load.upper_bound <= recommended_exercise.rpe.upper_bound):
            rpe_score = 1.0
        elif recommended_exercise.rpe.upper_bound is not None and (
                test_workout.projected_session_rpe.upper_bound > recommended_exercise.rpe.upper_bound):
            rpe_score = 0.0
        elif recommended_exercise.rpe.lower_bound <= test_workout.projected_session_rpe.lower_bound:
            rpe_score = 1.0
        elif test_workout.projected_session_rpe.upper_bound > recommended_exercise.rpe.upper_bound:
            rpe_score = 0.0
        else:
            rpe_score = test_workout.projected_session_rpe.lower_bound / recommended_exercise.rpe.lower_bound
    else:
        rpe_score = 1.0

    if recommended_exercise.duration is not None:
        if recommended_exercise.duration.lower_bound <= test_workout.duration <= recommended_exercise.duration.upper_bound:
            duration_score = 1.0
        elif test_workout.duration > recommended_exercise.duration.upper_bound:
            duration_score = recommended_exercise.duration.upper_bound / test_workout.duration

        else:
            duration_score = test_workout.duration / recommended_exercise.duration.lower_bound
    else:
        duration_score = 1.0

    if target_load_range.upper_bound is not None and (
            target_load_range.lower_bound <= test_workout.projected_rpe_load.lower_bound and test_workout.projected_rpe_load.upper_bound <= target_load_range.upper_bound):
        load_score = 1.0
    elif target_load_range.upper_bound is not None and (test_workout.projected_rpe_load.upper_bound > target_load_range.upper_bound):
        load_score = 0.0
    elif target_load_range.lower_bound <= test_workout.projected_rpe_load.lower_bound:
        load_score = 1.0
    elif test_workout.projected_rpe_load.upper_bound > target_load_range.upper_bound:
        load_score = 0.0
    else:
        load_score = test_workout.projected_rpe_load.lower_bound / target_load_range.lower_bound

    cosine_similarity = WorkoutScoringManager.cosine_similarity(test_workout.session_detailed_load.sub_adaptation_types,
                                                                [RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type, recommended_exercise.sub_adaptation_type, 1)])

    # if cosine_similarity > 0:
    #     if one_required_combination is None:
    #         times_per_week_score = recommended_exercise.times_per_week.lower_bound / float(5)
    #     else:
    #         times_per_week_score = one_required_combination.lower_bound / float(5)
    # else:
    #     times_per_week_score = 0
    if cosine_similarity > 0:
        times_per_week_score = np.random.choice([0, .2, .4, .6, .8, 1.])
    else:
        times_per_week_score = 0

    if test_workout.projected_monotony is None or test_workout.projected_monotony.observed_value is None:
        monotony_score = 1.0
    elif test_workout.projected_monotony.observed_value < 1.5:
        monotony_score = 1.0
    elif 1.5 <= test_workout.projected_monotony.observed_value < 2:
        monotony_score = 0.5
    else:
        monotony_score = 0.0

    if test_workout.projected_strain_event_level is None or test_workout.projected_strain_event_level.observed_value is None:
        strain_event_score = 1.0
    elif test_workout.projected_strain_event_level.observed_value < 1:
        strain_event_score = 1.0
    elif 1 <= test_workout.projected_strain_event_level.observed_value < 2:
        strain_event_score = 0.5
    else:
        strain_event_score = 0.0

    muscle_score = get_muscle_cosine_similarity(test_workout.ranked_muscle_detailed_load, target_ranked_muscles)

    composite_score = (
            (monotony_score * .1) +
            (strain_event_score * .1) +
            (times_per_week_score * .1) +
            (rpe_score * .15) +
            (duration_score * .15) +
            (load_score * .2) +
            (cosine_similarity * .1) +
            muscle_score * .1
    )

    workout_match = np.round(composite_score, 0)
    return workout_match, composite_score


def test_train_split(data):
    features_column = np.setdiff1d(data.columns, np.array(['match']))
    X = data[features_column]
    x_columns = X.columns
    from sklearn.preprocessing import scale
    X = scale(X.values)
    X = pd.DataFrame(X)
    X.columns = x_columns
    y = data['match']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=.33, random_state=1)
    test_score = X_test['score']
    del X_test['score'], X_train['score']
    return X_train, X_test, y_train, y_test, test_score

def get_predicted_outcome(model, data):
    return np.rint(model.predict(data))

def train_test(data):
    X_train, X_test, y_train, y_test, test_score = test_train_split(data)


    model = LogisticRegression(max_iter=1000).fit(X_train, y_train)

    y_train_pred = get_predicted_outcome(model, X_train)

    print('train precision: ' + str(precision_score(y_train, y_train_pred)))
    print('train recall: ' + str(recall_score(y_train, y_train_pred)))
    print('train accuracy: ' + str(accuracy_score(y_train, y_train_pred)))

    y_test_pred = get_predicted_outcome(model, X_test)

    test_score_pred = model.predict_proba(X_test)
    # test_score_pred[:, 2] = test_score.values

    all_scores = pd.DataFrame(np.hstack((test_score_pred, test_score.values.reshape(-1, 1))))
    all_scores.columns = ['prob_0', 'test_score', 'real_score']
    all_scores['diff'] = all_scores['real_score'] - all_scores['test_score']
    all_scores['prediction'] = y_test_pred

    print('test precision: ' + str(precision_score(y_test, y_test_pred)))
    print('test recall: ' + str(recall_score(y_test, y_test_pred)))
    print('test accuracy: ' + str(accuracy_score(y_test, y_test_pred)))
    print('here')

def run():
    # get_ranked_muscle_needs()
    events = load_data()
    train_test(events)

    #
    # print(events.head())
    # print(events.columns)
    print('here')



run()

