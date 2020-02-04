from models.workout_program import Movement, WorkoutExercise, WorkoutSection
from models.movement_tags import AdaptationType, TrainingType, CardioAction
from models.exercise import UnitOfMeasure

import os
import json

def get_cardio_data(provider='soflete'):
    file_name = f'cardiorespiratory_data_{provider}.json'
    file_path = os.path.join("../../apigateway/models", file_name)
    with open(file_path, 'r') as f:
        cardio_data = json.load(f)
    return cardio_data

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


def test_get_training_volume_cardioresp_swim_mile():
    cardio_data = get_cardio_data()
    workout_exercise = WorkoutExercise()
    workout_exercise.distance_params = cardio_data['distance_conversion']
    workout_exercise.calorie_params = cardio_data['calorie_conversion']
    workout_exercise.cardio_action = CardioAction.swim  # swim=4*run
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 1
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.miles  # mile=1609.34

    assert workout_exercise.get_training_volume() == 1 * 1609.34 * 4 * .336


def test_get_training_volume_cardioresp_rowyards():
    cardio_data = get_cardio_data()
    workout_exercise = WorkoutExercise()
    workout_exercise.distance_params = cardio_data['distance_conversion']
    workout_exercise.calorie_params = cardio_data['calorie_conversion']
    workout_exercise.cardio_action = CardioAction.row  # row=2*run
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 100
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.yards  # yard = .9144m

    assert workout_exercise.get_training_volume() == 100 * .9144 * 2 * .336


def test_get_training_volume_cardioresp_cycle_mile():
    cardio_data = get_cardio_data()
    workout_exercise = WorkoutExercise()
    workout_exercise.distance_params = cardio_data['distance_conversion']
    workout_exercise.calorie_params = cardio_data['calorie_conversion']
    workout_exercise.cardio_action = CardioAction.cycle  # cycle=.33*run
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 5
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.miles  # mile=1609.34

    assert workout_exercise.get_training_volume() == 5 * 1609.34 * .33 * .336


def test_get_training_volume_cardioresp_ruck_feet():
    cardio_data = get_cardio_data()
    workout_exercise = WorkoutExercise()
    workout_exercise.distance_params = cardio_data['distance_conversion']
    workout_exercise.calorie_params = cardio_data['calorie_conversion']
    workout_exercise.cardio_action = CardioAction.ruck  # ruck=2*run
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 5000
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.feet  # feet=.3048m

    assert workout_exercise.get_training_volume() == 5000 * 0.3048 * 2 * .336


def test_get_training_volume_cardioresp_row_calories():
    cardio_data = get_cardio_data()
    workout_exercise = WorkoutExercise()
    workout_exercise.distance_params = cardio_data['distance_conversion']
    workout_exercise.calorie_params = cardio_data['calorie_conversion']
    workout_exercise.cardio_action = CardioAction.row
    workout_exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    workout_exercise.reps_per_set = 500
    workout_exercise.sets = 1
    workout_exercise.unit_of_measure = UnitOfMeasure.calories

    assert workout_exercise.get_training_volume() == 500 / 311 * 1800


def test_no_load_section_warmup():
    cardio_data = get_cardio_data()
    workout_section = WorkoutSection()
    workout_section.name = "Warmup"

    assert workout_section.should_assess_load(cardio_data['no_load_sections']) == False

def test_laod_section_stamina():
    cardio_data = get_cardio_data()
    workout_section = WorkoutSection()
    workout_section.name = "stamina 2"

    assert workout_section.should_assess_load(cardio_data['no_load_sections']) == True


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
