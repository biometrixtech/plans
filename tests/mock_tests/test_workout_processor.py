from logic.workout_processing import WorkoutProcessor
from models.workout_program import WorkoutExercise, WorkoutSection, WorkoutProgramModule
from models.movement_tags import AdaptationType, CardioAction, TrainingType
from models.movement_actions import ExerciseAction, Movement, Explosiveness
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
    action.lateral_distribution = [0, 0]
    action.apply_resistance = True
    action.eligible_external_resistance = []
    action.lateral_distribution_pattern = None
    exercise.primary_actions = [action]
    return exercise


def get_section(name, exercises):
    section = WorkoutSection()
    section.name = name
    section.exercises = exercises
    return section


def test_one_load_section_one_no_load():
    workout_exercise1 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459d9ddc2ce90011f93d84")  # row
    workout_exercise2 = get_exercise(reps=180, sets=1, unit=UnitOfMeasure.meters, movement_id="57e2fd3a4c6a031dc777e90c")  # airdyne

    workout_exercise3 = get_exercise(reps=500, sets=1, unit=UnitOfMeasure.meters, movement_id="58459d9ddc2ce90011f93d84")  # row
    workout_exercise4 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.count, movement_id="58459df8dc2ce90011f93d87")  # run

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


def test_apply_explosiveness_to_actions():

    exercise = WorkoutExercise()
    exercise.explosiveness_rating = 8
    action_1 = ExerciseAction("2", "Action1")
    action_1.explosiveness = Explosiveness.high_force
    action_2 = ExerciseAction("3", "Action2")
    action_2.explosiveness = Explosiveness.max_force

    exercise.primary_actions.append(action_1)
    exercise.primary_actions.append(action_2)

    processor = WorkoutProcessor()

    processor.apply_explosiveness(exercise, exercise.primary_actions)

    assert action_1.explosiveness_rating == 8 * 0.75
    assert action_2.explosiveness_rating == 8 * 1.00
