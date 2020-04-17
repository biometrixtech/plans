# from models.workout_program import WorkoutExercise, WorkoutSection, WorkoutProgramModule
# from models.movement_actions import ExerciseAction
# from models.movement_tags import AdaptationType, CardioAction, TrainingType
# from models.exercise import UnitOfMeasure
# from models.cardio_data import get_cardio_data
#
# cardio_data = get_cardio_data()
#
#
# def get_exercise(reps=1, sets=1, unit=UnitOfMeasure.seconds, adaptation_type=AdaptationType.strength_endurance_cardiorespiratory, cardio_action=None):
#     exercise = WorkoutExercise()
#     exercise.reps_per_set = reps
#     exercise.sets = sets
#     exercise.unit_of_measure = unit
#     exercise.adaptation_type = adaptation_type
#     exercise.cardio_action = cardio_action
#     action = ExerciseAction('0', 'test_action')
#     action.training_type = TrainingType.strength_cardiorespiratory
#     action.reps = reps
#     action.lateral_distribution = [0, 0]
#     action.apply_resistance = True
#     action.eligible_external_resistance = []
#     action.lateral_distribution_pattern = None
#     exercise.primary_actions = [action]
#
#     return exercise
#
#
# def get_section(name, exercises, assess_load=True):
#     section = WorkoutSection()
#     section.name = name
#     section.exercises = exercises
#     section.assess_load = assess_load
#     return section
#
#
# def test_one_load_section_one_no_load():
#     workout_exercise1 = get_exercise(reps=90, sets=1, unit=UnitOfMeasure.seconds, adaptation_type=AdaptationType.strength_endurance_cardiorespiratory, cardio_action=CardioAction.run)
#     workout_exercise2 = get_exercise(reps=90, sets=2, unit=UnitOfMeasure.seconds, adaptation_type=AdaptationType.strength_endurance_cardiorespiratory, cardio_action=CardioAction.run)
#
#     section1 = get_section('test_section1', exercises=[workout_exercise1, workout_exercise2], assess_load=False)
#     section2 = get_section('test_section2', exercises=[workout_exercise1, workout_exercise2])
#
#     workout = WorkoutProgramModule()
#     workout.workout_sections = [section1, section2]
#
#     total_training_load = workout.get_training_load()
#     assert section1.get_training_load() == 0
#     assert section2.get_training_load() != 0
#     assert section2.get_training_load() == workout_exercise1.get_training_load() + workout_exercise2.get_training_load()
#     assert total_training_load == section2.get_training_load()
