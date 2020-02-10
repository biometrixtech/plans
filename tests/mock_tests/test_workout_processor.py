from logic.workout_processing import WorkoutProcessor
from models.workout_program import WorkoutExercise, WorkoutSection, WorkoutProgramModule
from models.movement_tags import AdaptationType, CardioAction, TrainingType
from models.movement_actions import ExerciseAction
from models.exercise import UnitOfMeasure


def get_exercise(reps=1, sets=1, unit=UnitOfMeasure.seconds, movement_id=""):
    exercise = WorkoutExercise()
    exercise.reps_per_set = reps
    exercise.sets = sets
    exercise.unit_of_measure = unit
    exercise.movement_id = movement_id
    action = ExerciseAction('0', 'test_action')
    action.training_type = TrainingType.strength_cardiorespiratory
    action.reps = reps
    action.percent_body_weight = [0, 0]
    action.apply_resistance = True
    action.eligible_external_resistance = []
    action.bilateral_distribution_of_weight = None
    exercise.primary_actions = [action]
    return exercise


def get_section(name, exercises):
    section = WorkoutSection()
    section.name = name
    section.exercises = exercises
    return section


def test_one_load_section_one_no_load():
    workout_exercise1 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.seconds, movement_id="582cb0d8dcab1710003331e9")  # row
    workout_exercise2 = get_exercise(reps=180, sets=1, unit=UnitOfMeasure.meters, movement_id="57e2fd3a4c6a031dc777e90c")  # airdyne

    workout_exercise3 = get_exercise(reps=500, sets=1, unit=UnitOfMeasure.meters, movement_id="582cb0d8dcab1710003331e9")  # row
    workout_exercise4 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.count, movement_id="5823768d473c06100052ed9a")  # run

    section1 = get_section('warm up', exercises=[workout_exercise1, workout_exercise2])
    section2 = get_section('stamina', exercises=[workout_exercise3, workout_exercise4])

    workout = WorkoutProgramModule()
    workout.workout_sections = [section1, section2]

    processor = WorkoutProcessor()
    processor.process_workout(workout)
    total_training_load = workout.get_training_load()

    assert workout_exercise1.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory
    assert workout_exercise1.cardio_action == CardioAction.row

    assert workout_exercise3.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory
    assert workout_exercise3.cardio_action == CardioAction.row

    assert workout_exercise4.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory
    assert workout_exercise4.cardio_action == CardioAction.run
    assert workout_exercise4.get_training_volume() == 90

    assert section1.assess_load is False
    assert section1.get_training_load() == 0
    assert section2.get_training_load() != 0
    assert section2.get_training_load() == workout_exercise3.get_training_load() + workout_exercise4.get_training_load()
    assert total_training_load == section2.get_training_load()
