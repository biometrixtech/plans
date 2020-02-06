from models.workout_program import WorkoutExercise, WorkoutSection
from models.movement_actions import Movement
from models.movement_tags import AdaptationType, TrainingType, CardioAction
from models.exercise import UnitOfMeasure
from datastores.movement_library_datastore import MovementLibraryDatastore
from models.cardio_data import get_cardio_data


movement_library = MovementLibraryDatastore().get()
cardio_data = get_cardio_data()

def test_training_type_flexibility():

    movement = Movement("1", "test")
    movement.training_type = TrainingType.flexibility

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.not_tracked


def test_training_type_cardiorespiratory():

    movement = Movement("1", "test")
    movement.training_type = TrainingType.strength_cardiorespiratory

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory


def test_training_type_strength_endurance():

    movement = Movement("1", "test")
    movement.training_type = TrainingType.strength_endurance

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.strength_endurance_strength


# def test_training_type_balance():
#     movement = Movement("1", "test")
#     movement.training_type = TrainingType.balance
#
#     workout_exercise = WorkoutExercise()
#     workout_exercise.process_movement(movement)
#
#     assert workout_exercise.adaptation_type == AdaptationType.strength_endurance_strength


def test_training_type_power_action_plyometrics():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.power_action_plyometrics

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.power_explosive_action


def test_training_type_plyometrics_drills():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.power_drills_plyometrics

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.power_drill


# def test_training_type_speed_agility_quickness():
#     movement = Movement("1", "test")
#     movement.training_type = TrainingType.speed_agility_quickness
#
#     workout_exercise = WorkoutExercise()
#     workout_exercise.process_movement(movement)
#
#     assert workout_exercise.adaptation_type == AdaptationType.power_drill


def test_training_type_integrated_resistance_high():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.strength_integrated_resistance

    workout_exercise = WorkoutExercise()
    workout_exercise.intensity_pace = 80
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic


def test_training_type_integrated_resistance_low():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.strength_integrated_resistance

    workout_exercise = WorkoutExercise()
    workout_exercise.intensity_pace = 60
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.strength_endurance_strength


def test_training_type_olympic_lifting_high():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.power_action_olympic_lift
    movement.explosive = 3

    workout_exercise = WorkoutExercise()

    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.power_explosive_action


def test_training_type_olympic_lifting_low():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.power_action_olympic_lift
    movement.explosive = 1

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.power_explosive_action


def test_get_training_volume_reps():

    workout_exercise = WorkoutExercise()
    workout_exercise.reps_per_set = 5
    workout_exercise.unit_of_measure = UnitOfMeasure.count
    workout_exercise.sets = 1

    assert workout_exercise.get_training_volume() == 5


def test_get_training_volume_reps_sets():

    workout_exercise = WorkoutExercise()
    workout_exercise.reps_per_set = 5
    workout_exercise.sets = 2
    workout_exercise.unit_of_measure = UnitOfMeasure.count

    assert workout_exercise.get_training_volume() == 10


def test_get_training_volume_reps_sets_yards():
    workout_exercise = WorkoutExercise()
    workout_exercise.reps_per_set = 50
    workout_exercise.sets = 2
    workout_exercise.unit_of_measure = UnitOfMeasure.yards

    assert workout_exercise.get_training_volume() == 20


def test_get_training_volume_reps_sets_feet():
    workout_exercise = WorkoutExercise()
    workout_exercise.reps_per_set = 150
    workout_exercise.sets = 2
    workout_exercise.unit_of_measure = UnitOfMeasure.feet

    assert workout_exercise.get_training_volume() == 20


def test_convert_distance_seconds_cardioresp_swim_mile():
    workout_exercise = WorkoutExercise()
    workout_exercise.cardio_action = CardioAction.swim  # swim=4*run
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 1
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.miles  # mile=1609.34
    # workout_exercise.movement_id = "5a4d3b5d5a0778000fd6a4c6"  # freestyle swim

    workout_exercise.convert_reps_to_duration(cardio_data)
    assert workout_exercise.reps_per_set == int(1609.34 * 4 * .336)


def test_get_training_volume_cardioresp_rowyards():
    workout_exercise = WorkoutExercise()
    workout_exercise.cardio_action = CardioAction.row  # row=2*run
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 100
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.yards  # yard = .9144m
    # workout_exercise.movement_id = '582cb0d8dcab1710003331e9'  # rowing movement

    workout_exercise.convert_reps_to_duration(cardio_data)
    assert workout_exercise.reps_per_set == int(100 * .9144 * 2 * .336)


def test_get_training_volume_cardioresp_cycle_mile():
    workout_exercise = WorkoutExercise()
    workout_exercise.cardio_action = CardioAction.cycle  # cycle=.33*run
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 5
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.miles  # mile=1609.34
    # workout_exercise.movement_id = "57e2fd3a4c6a031dc777e90c"  # airdyne

    workout_exercise.convert_reps_to_duration(cardio_data)
    assert workout_exercise.reps_per_set == int(5 * 1609.34 * .33 * .336)


def test_get_training_volume_cardioresp_ruck_feet():
    workout_exercise = WorkoutExercise()
    workout_exercise.cardio_action = CardioAction.ruck  # ruck=2*run
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 5000
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.feet  # feet=.3048m
    # workout_exercise.movement_id = "5873d05eb06dc50011d08796"

    workout_exercise.convert_reps_to_duration(cardio_data)
    assert workout_exercise.reps_per_set == int(5000 * 0.3048 * 2 * .336)


def test_get_training_volume_cardioresp_row_calories():
    workout_exercise = WorkoutExercise()
    workout_exercise.cardio_action = CardioAction.row
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 500
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.calories
    # workout_exercise.movement_id = '582cb0d8dcab1710003331e9'  # rowing movement

    workout_exercise.convert_reps_to_duration(cardio_data)
    assert workout_exercise.reps_per_set== int(500 / 311 * 1800)


def test_no_load_section_warmup():
    workout_section = WorkoutSection()
    workout_section.name = "Warmup"

    workout_section.should_assess_load(cardio_data['no_load_sections'])
    assert workout_section.assess_load is False


def test_laod_section_stamina():
    workout_section = WorkoutSection()
    workout_section.name = "stamina 2"

    workout_section.should_assess_load(cardio_data['no_load_sections'])
    assert workout_section.assess_load is True


def test_training_intensity_cardioresp():
    workout_exercise = WorkoutExercise()
    workout_exercise.cardio_action = CardioAction.row
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.rpe = 5

    assert workout_exercise.get_training_intensity() == workout_exercise.rpe


def test_training_intensity_cardioresp_ro_rpe():
    workout_exercise = WorkoutExercise()
    workout_exercise.cardio_action = CardioAction.row
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory

    assert workout_exercise.get_training_intensity() == 4
