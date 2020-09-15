from models.workout_program import WorkoutExercise
from models.movement_tags import Equipment, WeightDistribution, TrainingType, CardioAction
from models.exercise import UnitOfMeasure, WeightMeasure
from models.movement_actions import ExerciseAction, ExerciseSubAction, CompoundAction
from logic.workout_processing import WorkoutProcessor


def get_exercise(reps=1, sets=1, unit=UnitOfMeasure.seconds, equipment=Equipment.barbells, weight=100, side=0,
                 training_type=TrainingType.strength_integrated_resistance, explosiveness=1, movement_id="",):
    exercise = WorkoutExercise()
    exercise.reps_per_set = reps
    exercise.sets = sets
    exercise.unit_of_measure = unit
    exercise.movement_id = movement_id
    exercise.equipments = [equipment]
    exercise.weight = weight
    exercise.weight_measure = WeightMeasure.actual_weight
    exercise.side = side
    exercise.training_type = training_type
    exercise.explosiveness_rating = explosiveness
    exercise.set_intensity()
    exercise.set_adaptation_type()
    return exercise


def get_action(action_id, name, exercise,  perc_bodyweight=0,
               weight_dist=WeightDistribution.bilateral, lateral_distribution=(50, 50), cardio_action=None):

    sub_action = ExerciseSubAction(action_id, name)
    sub_action.percent_bodyweight = perc_bodyweight
    sub_action.lateral_distribution = lateral_distribution
    sub_action.apply_resistance = True
    sub_action.eligible_external_resistance = [Equipment.barbells, Equipment.dumbbells]
    sub_action.lateral_distribution_pattern = weight_dist
    sub_action.cardio_action = cardio_action
    if cardio_action is not None:
        exercise.cardio_action = cardio_action
    exercise.bilateral_distribution_of_resistance = weight_dist
    exercise = WorkoutProcessor().update_exercise_details(exercise)
    action = ExerciseAction('test', 'test')
    action.sub_actions = [sub_action]
    compound_action = CompoundAction('test', 'test')
    compound_action.actions = [action]
    WorkoutProcessor().add_action_details_from_exercise(exercise, [compound_action])
    # WorkoutProcessor().initialize_action_from_exercise(action, exercise)
    # WorkoutProcessor().set_action_explosiveness_from_exercise(exercise, [action])
    # action.training_intensity = exercise.training_intensity
    # action.set_external_weight_distribution()
    # action.set_body_weight_distribution()
    # action.set_training_load()
    return sub_action


def test_external_intensity_barbell():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise)
    assert action.external_weight_left == 50
    assert action.external_weight_right == 50

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40
    assert int(action.tissue_load_left.observed_value) == int(action.tissue_load_right.observed_value) == int(50 * 9.8 * 40)


def test_external_intensity_barbell_unilateral_no_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, lateral_distribution=[100, 0])
    assert action.external_weight_left == 100
    assert action.external_weight_right == 100

    assert action.training_volume_left == 20
    assert action.training_volume_right == 20

    assert int(action.tissue_load_left.observed_value) == int(action.tissue_load_right.observed_value) == int(100 * 9.8 * 20)


def test_external_intensity_unilateral_alternating_barbell():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral_alternating, lateral_distribution=[100, 100])

    assert action.external_weight_left == 100
    assert action.external_weight_right == 100

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40

    assert int(action.tissue_load_left.observed_value) == int(action.tissue_load_right.observed_value) == int(100 * 9.8 * 40)


def test_external_intensity_dumbbell_bilateral():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise)

    assert action.external_weight_left == 50
    assert action.external_weight_right == 50

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40

    assert int(action.tissue_load_left.observed_value) == int(action.tissue_load_right.observed_value) == int(50 * 9.8 * 40)


def test_external_intensity_dumbbell_bilateral_uneven_no_side():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, lateral_distribution=[60, 40])

    assert action.external_weight_left == 50
    assert action.external_weight_right == 50

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40

    assert int(action.tissue_load_left.observed_value) == int(action.tissue_load_right.observed_value) == int(50 * 9.8 * 40)


def test_external_intensity_dumbell_bilateral_uneven_left_action_dominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, lateral_distribution=[60, 40])

    assert action.external_weight_left == 60
    assert action.external_weight_right == 40

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40

    assert int(action.tissue_load_left.observed_value) == int(60 * 9.8 * 40)
    assert int(action.tissue_load_right.observed_value) == int(40 * 9.8 * 40)


def test_external_intensity_unilateral_dumbbell_no_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, lateral_distribution=[100, 0])

    assert action.external_weight_left == 50
    assert action.external_weight_right == 50

    assert action.training_volume_left == 20
    assert action.training_volume_right == 20


def test_external_intensity_unilateral_dumbbell_side_defined():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, lateral_distribution=[100, 0])

    assert action.external_weight_left == 50
    assert action.external_weight_right == 0

    assert action.training_volume_left == 40
    assert action.training_volume_right == 0


def test_external_intensity_unilateral_alternating_dumbbell():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral_alternating, lateral_distribution=[100, 100])

    assert action.external_weight_left == 100
    assert action.external_weight_right == 100

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40


def test_bodyweight_intensity_bilateral():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.barbells, weight=100)
    action = get_action('100', "test action", exercise=workout_exercise, perc_bodyweight=100, lateral_distribution=[50, 50])

    assert action.body_weight_left == 50
    assert action.body_weight_right == 50

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40


def test_bodyweight_intensity_unilateral_no_side():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, perc_bodyweight=50, lateral_distribution=[100, 0])

    assert action.body_weight_left == 50
    assert action.body_weight_right == 50

    assert action.training_volume_left == 20
    assert action.training_volume_right == 20


def test_bodyweight_intensity_unilateral_side():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral, perc_bodyweight=30, lateral_distribution=[100, 0])

    assert action.body_weight_left == 30
    assert action.body_weight_right == 0

    assert action.training_volume_left == 40
    assert action.training_volume_right == 0


def test_bodyweight_intensity_unilateral_alternating():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.unilateral_alternating, perc_bodyweight=100, lateral_distribution=[100, 100])

    assert action.body_weight_left == 100
    assert action.body_weight_right == 100

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40


def test_bodyweight_intensity_bilateral_uneven_dominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, perc_bodyweight=100, lateral_distribution=[60, 0])

    assert action.body_weight_left == 60
    assert action.body_weight_right == 0

    assert action.training_volume_left == 40
    assert action.training_volume_right == 0


def test_bodyweight_intensity_bilateral_uneven_nondominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=1)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, perc_bodyweight=100, lateral_distribution=[0, 40])

    assert action.body_weight_left == 0
    assert action.body_weight_right == 40

    assert action.training_volume_left == 0
    assert action.training_volume_right == 40


def test_bodyweight_intensity_bilateral_uneven_dominant_2():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=2)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, perc_bodyweight=100, lateral_distribution=[60, 0])

    assert action.body_weight_left == 0
    assert action.body_weight_right == 60

    assert action.training_volume_left == 0
    assert action.training_volume_right == 40


def test_bodyweight_intensity_bilateral_uneven_nondominant_2():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50, side=2)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven, perc_bodyweight=50, lateral_distribution=[0, 40])

    assert action.body_weight_left == 20
    assert action.body_weight_right == 0

    assert action.training_volume_left == 40
    assert action.training_volume_right == 0


def test_bodyweight_intensity_bilateral_uneven_dominant_not_defined_dominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven,  perc_bodyweight=100, lateral_distribution=[60, 0])

    assert action.body_weight_left == 30
    assert action.body_weight_right == 30

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40


def test_bodyweight_intensity_bilateral_uneven_dominant_not_defined_nondominant():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=50)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral_uneven,  perc_bodyweight=100, lateral_distribution=[0, 40])

    assert action.body_weight_left == 20
    assert action.body_weight_right == 20

    assert action.training_volume_left == 40
    assert action.training_volume_right == 40


def test_training_volume_load_cardioresp():
    workout_exercise = get_exercise(reps=100, sets=1, unit=UnitOfMeasure.seconds, training_type=TrainingType.strength_cardiorespiratory)
    action = get_action('100', "test action", exercise=workout_exercise, cardio_action=CardioAction.swim)
    # both sides get all the volume
    assert action.training_volume_left == 100
    assert action.training_volume_right == 100

    #assert action.rpe.observed_value == 4

    # assert action.tissue_load_left.observed_value == 44.84 * 100
    # assert action.tissue_load_right.observed_value == 44.84 * 100


def test_convert_distance_seconds_cardioresp_sandbag_run_mile():
    workout_exercise1 = get_exercise(reps=100, sets=1, unit=UnitOfMeasure.seconds, training_type=TrainingType.strength_cardiorespiratory)
    workout_exercise1.cardio_action = CardioAction.run
    workout_exercise1.reps_per_set = 1
    workout_exercise1.sets = 1
    workout_exercise1.unit_of_measure = UnitOfMeasure.miles  # mile=1609.34

    workout_exercise2 = get_exercise(reps=100, sets=1, unit=UnitOfMeasure.seconds, training_type=TrainingType.strength_integrated_resistance)
    workout_exercise2.cardio_action = CardioAction.run
    workout_exercise2.reps_per_set = 1
    workout_exercise2.sets = 1
    workout_exercise2.unit_of_measure = UnitOfMeasure.miles  # mile=1609.34

    action1 = get_action('1', "run", exercise=workout_exercise1)
    action2 = get_action('2005', "hold weight on shoulder", exercise=workout_exercise2)

    #assert action1.reps == int(1609.34 * 1 * .336)
    assert action1.training_volume_left == int(1609.34 * 1 * .336) == action1.training_volume_right
    #assert action2.reps == int(1609.34 / 5)  # 1 rep per 5 meters
    assert action2.training_volume_left == int(1609.34 / 5) * 4 == action2.training_volume_right


def test_power_intensity():
    workout_exercise = get_exercise(reps=10, sets=1, unit=UnitOfMeasure.count, equipment=Equipment.dumbbells, weight=100, training_type=TrainingType.power_drills_plyometrics, explosiveness=5)
    action = get_action('100', "test action", exercise=workout_exercise, weight_dist=WeightDistribution.bilateral)

    # assert int(action.force.observed_value) == int(100  * 9.8)

    assert action.training_volume_left == 50
    assert action.training_volume_right == 50

    assert int(action.tissue_load_left.observed_value) == int(action.tissue_load_right.observed_value) == int(100 * 9.8 * 50)
