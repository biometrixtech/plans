import os
from logic.rpe_predictor import RPEPredictor
from logic.workout_processing import WorkoutProcessor
from models.workout_program import WorkoutExercise
from models.movement_tags import AdaptationType, Equipment
from models.exercise import WeightMeasure
from models.training_volume import Assignment


def get_exercise(movement_id='57e2fd3a4c6a031dc777e936'):
    exercise = WorkoutExercise()
    exercise.sets = 1
    exercise.movement_id = movement_id

    return exercise


def test_hr_rpe():
    predictor = RPEPredictor()
    rpe1 = predictor.predict_rpe(140)
    rpe2 = predictor.predict_rpe(160)
    if os.environ.get('CODEBUILD_RUN', '') != 'TRUE':
        assert rpe2 > rpe1


def test_bodyweight_ratio_rpe():
    exercise = get_exercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_strength
    exercise.reps_per_set = 10
    exercise.weight = 10
    exercise.weight_measure = WeightMeasure.actual_weight
    rpe1 = WorkoutProcessor().get_rpe_from_weight(exercise)

    exercise2 = get_exercise()
    exercise2.adaptation_type = AdaptationType.strength_endurance_strength
    exercise2.reps_per_set = 10
    exercise2.weight = 20
    exercise2.weight_measure = WeightMeasure.actual_weight
    rpe2 = WorkoutProcessor().get_rpe_from_weight(exercise2)

    if os.environ.get('CODEBUILD_RUN', '') != 'TRUE':
        assert rpe1.observed_value < rpe2.observed_value


def test_bodyweight_ratio_rpe_no_reps():
    exercise = get_exercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_strength
    exercise.duration = 30
    exercise.equipments = [Equipment.dumbbells]
    exercise.weight = 10
    exercise.weight_measure = WeightMeasure.actual_weight
    exercise.set_reps_duration()
    rpe = WorkoutProcessor().get_rpe_from_weight(exercise)
    assert rpe.lower_bound is not None
    assert rpe.upper_bound is not None
    assert rpe.observed_value is not None


def test_bodyweight_ratio_rpe_range_of_reps():
    exercise = get_exercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_strength
    exercise.equipments = [Equipment.dumbbells]
    exercise.weight_measure = WeightMeasure.actual_weight
    exercise.weight = 10
    prev_rpe = 0
    for reps in range(25):
        exercise.reps_per_set = reps
        rpe = WorkoutProcessor().get_rpe_from_weight(exercise).observed_value
        assert rpe >= prev_rpe
        prev_rpe = rpe


def test_get_rpe_from_weight_percent_rep_max():
    exercise = get_exercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_strength
    exercise.equipments = [Equipment.dumbbells]
    exercise.weight_measure = WeightMeasure.percent_rep_max
    exercise.weight = 67
    prev_rpe = 0
    for reps in range(25):
        exercise.reps_per_set = reps
        rpe = WorkoutProcessor().get_rpe_from_weight(exercise).observed_value
        assert rpe >= prev_rpe
        prev_rpe = rpe


def test_get_rpe_from_weight_percent_rep_max_assignment():
    exercise = get_exercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_strength
    exercise.equipments = [Equipment.dumbbells]
    exercise.weight_measure = WeightMeasure.percent_rep_max
    exercise.weight = Assignment(min_value=40, max_value=60)
    prev_rpe = 0
    for reps in range(25):
        exercise.reps_per_set = reps
        rpe = WorkoutProcessor().get_rpe_from_weight(exercise).observed_value
        assert rpe >= prev_rpe
        prev_rpe = rpe


def test_get_rpe_from_weight_rep_max():
    exercise = get_exercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_strength
    exercise.equipments = [Equipment.dumbbells]
    exercise.weight_measure = WeightMeasure.rep_max
    exercise.weight = Assignment(assigned_value=10)
    prev_rpe = 0
    for reps in range(25):
        exercise.reps_per_set = reps
        rpe = WorkoutProcessor().get_rpe_from_weight(exercise).observed_value
        assert rpe >= prev_rpe
        prev_rpe = rpe
