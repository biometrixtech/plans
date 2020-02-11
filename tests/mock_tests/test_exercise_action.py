from models.workout_program import WorkoutExercise
from models.movement_tags import Equipment, WeightDistribution, TrainingType, CardioAction
from models.exercise import UnitOfMeasure
from models.movement_actions import ExerciseAction
from logic.workout_processing import WorkoutProcessor


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


def get_action(action_id, name, exercise, training_type=TrainingType.strength_integrated_resistance, perc_bodyweight=0,
               weight_dist=WeightDistribution.bilateral, lateral_distribution=(50, 50)):
    action = ExerciseAction(action_id, name)
    action.percent_bodyweight = perc_bodyweight
    action.training_type = training_type
    action.lateral_distribution = lateral_distribution
    action.apply_resistance = True
    action.eligible_external_resistance = [Equipment.barbells, Equipment.dumbbells]
    action.lateral_distribution_pattern = weight_dist

    WorkoutProcessor().process_action(action, exercise)
    return action


def test_external_intensity_barbell():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise)
    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10

    assert action.total_load_left == action.total_load_right == 500


def test_external_intensity_barbell_unilateral_no_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, lateral_distribution=[100, 0])
    assert action.external_intensity_left == 100
    assert action.external_intensity_right == 100

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10

    assert action.total_load_left == action.total_load_right == 1000


def test_external_intensity_unilateral_alternating_barbell():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral_alternating, lateral_distribution=[100, 100])

    assert action.external_intensity_left == 100
    assert action.external_intensity_right == 100

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10

    assert action.total_load_left == action.total_load_right == 1000


def test_external_intensity_dumbell_bilateral():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise)

    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10

    assert action.total_load_left == action.total_load_right == 500


def test_external_intensity_dumbell_bilateral_uneven_no_side():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, lateral_distribution=[60, 40])

    assert action.external_intensity_left == 25
    assert action.external_intensity_right == 25

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10

    assert action.total_load_left == action.total_load_right == 250


def test_external_intensity_dumbell_bilateral_uneven_left_action_dominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, lateral_distribution=[60, 40])

    assert action.external_intensity_left == 30
    assert action.external_intensity_right == 20

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10

    assert action.total_load_left == 300
    assert action.total_load_right == 200


def test_external_intensity_unilateral_dumbbell_no_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, lateral_distribution=[100, 0])

    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_external_intensity_unilateral_dumbbell_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, lateral_distribution=[100, 0])

    assert action.external_intensity_left == 50
    assert action.external_intensity_right == 0

    assert action.training_volume_left == 10
    assert action.training_volume_right == 0


def test_external_intensity_unilateral_alternating_dumbbell():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral_alternating, lateral_distribution=[100, 100])

    assert action.external_intensity_left == 100
    assert action.external_intensity_right == 100

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_bodyweight_intensity_bilateral():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, perc_bodyweight=100, lateral_distribution=[50, 50])

    assert action.bodyweight_intensity_left == 50
    assert action.bodyweight_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_bodyweight_intensity_unilateral_no_side():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, perc_bodyweight=50, lateral_distribution=[100, 0])

    assert action.bodyweight_intensity_left == 50
    assert action.bodyweight_intensity_right == 50

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_bodyweight_intensity_unilateral_side():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, perc_bodyweight=30, lateral_distribution=[100, 0])

    assert action.bodyweight_intensity_left == 30
    assert action.bodyweight_intensity_right == 0

    assert action.training_volume_left == 10
    assert action.training_volume_right == 0


def test_bodyweight_intensity_unilateral_alternating():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral_alternating, perc_bodyweight=100, lateral_distribution=[100, 100])

    assert action.bodyweight_intensity_left == 100
    assert action.bodyweight_intensity_right == 100

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_bodyweight_intensity_bilateral_uneven_dominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, perc_bodyweight=100, lateral_distribution=[60, 0])

    assert action.bodyweight_intensity_left == 60
    assert action.bodyweight_intensity_right == 0

    assert action.training_volume_left == 10
    assert action.training_volume_right == 0


def test_bodyweight_intensity_bilateral_uneven_nondominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, perc_bodyweight=100, lateral_distribution=[0, 40])

    assert action.bodyweight_intensity_left == 0
    assert action.bodyweight_intensity_right == 40

    assert action.training_volume_left == 0
    assert action.training_volume_right == 10


def test_bodyweight_intensity_bilateral_uneven_dominant_2():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=2)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, perc_bodyweight=100, lateral_distribution=[60, 0])

    assert action.bodyweight_intensity_left == 0
    assert action.bodyweight_intensity_right == 60

    assert action.training_volume_left == 0
    assert action.training_volume_right == 10


def test_bodyweight_intensity_bilateral_uneven_nondominant_2():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=2)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, perc_bodyweight=50, lateral_distribution=[0, 40])

    assert action.bodyweight_intensity_left == 20
    assert action.bodyweight_intensity_right == 0

    assert action.training_volume_left == 10
    assert action.training_volume_right == 0


def test_bodyweight_intensity_bilateral_uneven_dominant_not_defined_dominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven,  perc_bodyweight=100, lateral_distribution=[60, 0])

    assert action.bodyweight_intensity_left == 30
    assert action.bodyweight_intensity_right == 30

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_bodyweight_intensity_bilateral_uneven_dominant_not_defined_nondominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven,  perc_bodyweight=100, lateral_distribution=[0, 40])

    assert action.bodyweight_intensity_left == 20
    assert action.bodyweight_intensity_right == 20

    assert action.training_volume_left == 10
    assert action.training_volume_right == 10


def test_training_volume_load_cardioresp():
    workout_exercise = get_exercise(reps=100, sets=1, unit=UnitOfMeasure.seconds)
    action = get_action('100', "test action", exercise=workout_exercise, training_type=TrainingType.strength_cardiorespiratory)
    # both sides get all the volume
    assert action.training_volume_left == 100
    assert action.training_volume_right == 100

    assert action.rpe == 4

    assert action.total_load_left == 400
    assert action.total_load_right == 400


def test_convert_distance_seconds_cardioresp_sandbag_run_mile():
    workout_exercise = get_exercise(reps=100, sets=1, unit=UnitOfMeasure.seconds)
    workout_exercise.cardio_action = CardioAction.run
    workout_exercise.reps_per_set = 1
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.miles  # mile=1609.34

    action1 = get_action('1', "run", exercise=workout_exercise, training_type=TrainingType.strength_cardiorespiratory)
    action2 = get_action('2005', "hold weight on shoulder", exercise=workout_exercise, training_type=TrainingType.strength_integrated_resistance)

    assert action1.reps == int(1609.34 * 1 * .336)
    assert action1.training_volume_left == int(1609.34 * 1 * .336) == action1.training_volume_right
    assert action2.reps == int(1609.34 / 5)  # 1 rep per 5 meters
    assert action2.training_volume_left == int(1609.34 / 5) == action2.training_volume_right
