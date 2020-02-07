from models.workout_program import WorkoutExercise
from models.movement_tags import Equipment, WeightDistribution
from models.exercise import UnitOfMeasure
from models.movement_actions import ExerciseAction, ExternalWeight


def get_exercise(reps=1, sets=1, unit=UnitOfMeasure.seconds, equipment=Equipment.barbells, weight=100, side=0, movement_id=""):
    exercise = WorkoutExercise()
    exercise.reps_per_set = reps
    exercise.sets = sets
    exercise.unit_of_measure = unit
    exercise.movement_id = movement_id
    exercise.equipment = equipment
    exercise.weight_in_lbs = weight
    exercise.side = side
    return exercise


def get_action(action_id, name, exercise, weight_dist=WeightDistribution.bilateral, body_weight=(0, 0)):
    action = ExerciseAction(action_id, name)

    external_weight = ExternalWeight(exercise.equipment, exercise.weight_in_lbs)
    action.external_weight = [external_weight]

    action.reps = exercise.reps_per_set
    action.side = exercise.side
    action.percent_body_weight = body_weight
    action.apply_resistance = True
    action.eligible_external_resistance = [Equipment.barbells, Equipment.dumbbells]
    action.bilateral_distribution_of_weight = weight_dist
    action.get_external_intensity()
    action.get_body_weight_intensity()
    action.get_training_volume()
    action.get_training_load()
    return action


def test_external_intensity_barbell():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise)
    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_external_intensity_barbell_unilateral_no_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral)
    assert action.external_intensity_left == 100
    assert action.external_intensity_right == 100

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_external_intensity_dumbell_bilateral():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise)

    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_external_intensity_dumbell_bilateral_uneven():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise)

    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_external_intensity_unilateral_dumbbell_no_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral)

    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_external_intensity_unilateral_dumbbell_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral)

    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 0

    assert action.training_volume_left == 10
    assert action.training_volume_right == 0


def test_bodyweight_intensity_bilateral():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, body_weight=[100])

    assert action.bodyweight_intensity_left == 50
    assert action.bodyweight_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_bodyweight_intensity_unilateral_no_side():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, body_weight=[50])

    assert action.bodyweight_intensity_left == 50
    assert action.bodyweight_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_bodyweight_intensity_unilateral_side():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, body_weight=[30])

    assert action.bodyweight_intensity_left == 30
    assert action.bodyweight_intensity_right == 0

    assert action.training_volume_left == 10
    assert action.training_volume_right == 0


def test_bodyweight_intensity_unilateral_alternating():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral_alternating, body_weight=[100])

    assert action.bodyweight_intensity_left == 100
    assert action.bodyweight_intensity_right == 100

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_bodyweight_intensity_bilateral_uneven_dominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, body_weight=[60, 0])

    assert action.bodyweight_intensity_left == 60
    assert action.bodyweight_intensity_right == 0

    assert action.training_volume_left == 10
    assert action.training_volume_right == 0


def test_bodyweight_intensity_bilateral_uneven_nondominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, body_weight=[0, 40])

    assert action.bodyweight_intensity_left == 0
    assert action.bodyweight_intensity_right == 40

    assert action.training_volume_left == 0
    assert action.training_volume_right == 10


def test_bodyweight_intensity_bilateral_uneven_dominant_2():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=2)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, body_weight=[60, 0])

    assert action.bodyweight_intensity_left == 0
    assert action.bodyweight_intensity_right == 60

    assert action.training_volume_left == 0
    assert action.training_volume_right == 10


def test_bodyweight_intensity_bilateral_uneven_nondominant_2():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=2)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, body_weight=[0, 40])

    assert action.bodyweight_intensity_left == 40
    assert action.bodyweight_intensity_right == 0

    assert action.training_volume_left == 10
    assert action.training_volume_right == 0
