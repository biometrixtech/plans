from models.functional_movement import FunctionalMovementActionMapping, FunctionalMovementFactory
from logic.workout_processing import WorkoutProcessor
from models.workout_program import WorkoutExercise, CompletedWorkoutSection, WorkoutProgramModule
from models.movement_tags import TrainingType
from models.movement_actions import ExerciseAction
from models.exercise import UnitOfMeasure
from models.session import MixedActivitySession
from utils import none_max
import datetime


def create_and_process_workout(exercises):
    section = CompletedWorkoutSection()
    section.name = 'stamina'
    section.exercises = exercises

    workout = WorkoutProgramModule()
    workout.workout_sections = [section]
    session = MixedActivitySession()
    processor = WorkoutProcessor()
    session.workout_program_module = workout
    processor.process_workout(session)


def get_exercise(reps=1, sets=1, unit=UnitOfMeasure.seconds, movement_id=""):
    exercise = WorkoutExercise()
    exercise.reps_per_set = reps
    exercise.sets = sets
    exercise.unit_of_measure = unit
    exercise.movement_id = movement_id
    if movement_id == "":
        action = ExerciseAction('0', 'test_action')
        action.training_type = TrainingType.strength_cardiorespiratory
        action.reps = reps
        action.lateral_distribution = [0, 0]
        action.apply_resistance = True
        action.eligible_external_resistance = []
        action.lateral_distribution_pattern = None
        exercise.primary_actions = [action]
    return exercise


def get_max_action_load(functional_movement_action_mapping):
    max_action_load = 0
    for muscle_load in functional_movement_action_mapping.muscle_load.values():
        max_action_load = none_max([max_action_load, muscle_load.eccentric_load.observed_value, muscle_load.concentric_load.observed_value])
    return max_action_load


def get_max_load(exercise):
    factory = FunctionalMovementFactory()
    functional_movement_dict = factory.get_functional_movement_dictinary()
    max_loads = {}
    for exercise_action in exercise.primary_actions:
        functional_movement_action_mapping = FunctionalMovementActionMapping(exercise_action, {}, datetime.datetime.now(), functional_movement_dict)
        max_action_load = get_max_action_load(functional_movement_action_mapping)
        max_loads[exercise_action.id] = max_action_load
    return max_loads


def test_run():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="5823768d473c06100052ed9a")  # run
    create_and_process_workout([exercise])
    max_loads = get_max_load(exercise)
    assert max_loads['1_a'] > max_loads['1_b'] > max_loads['1_c']


def test_sprint():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459de6dc2ce90011f93d86")  # sprint
    create_and_process_workout([exercise])
    max_loads = get_max_load(exercise)

    assert max_loads['2_a'] > max_loads['2_b'] > max_loads['2_c']
