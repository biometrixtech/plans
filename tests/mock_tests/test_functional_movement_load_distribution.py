from models.functional_movement import FunctionalMovementActionMapping, FunctionalMovementFactory
from logic.workout_processing import WorkoutProcessor
from models.workout_program import WorkoutExercise, CompletedWorkoutSection, WorkoutProgramModule
from models.movement_tags import TrainingType
from models.movement_actions import ExerciseAction, CompoundAction, ExerciseSubAction
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
        sub_action = ExerciseSubAction('0', 'test_action')
        sub_action.training_type = TrainingType.strength_cardiorespiratory
        sub_action.reps = reps
        sub_action.lateral_distribution = [0, 0]
        sub_action.apply_resistance = True
        sub_action.eligible_external_resistance = []
        sub_action.lateral_distribution_pattern = None
        action = ExerciseAction('1', 'test')
        action.sub_actions = [sub_action]
        compound_action = CompoundAction('1', 'test')
        compound_action.actions = [action]
        exercise.compound_actions = [action]
    return exercise


def get_max_action_load(functional_movement_action_mapping):
    max_action_load = 0
    for muscle_load in functional_movement_action_mapping.muscle_load.values():
        max_action_load = none_max([max_action_load, muscle_load.eccentric_load.observed_value, muscle_load.concentric_load.observed_value, muscle_load.isometric_load.observed_value])
    return max_action_load


def get_max_load(exercise):
    factory = FunctionalMovementFactory()
    functional_movement_dict = factory.get_functional_movement_dictionary()
    max_loads = {}
    for compound_action in exercise.compound_actions:
        for action in compound_action.actions:
            for sub_action in action.sub_actions:
                functional_movement_action_mapping = FunctionalMovementActionMapping(sub_action, {}, datetime.datetime.now(), functional_movement_dict)
                max_action_load = get_max_action_load(functional_movement_action_mapping)
                max_loads[sub_action.id] = max_action_load
    return max_loads


def test_run():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="run")  # run
    create_and_process_workout([exercise])
    max_loads = get_max_load(exercise)
    assert max_loads['0_b'] > max_loads['0_a'] > max_loads['0_c']


def test_sprint():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="sprint")  # sprint
    create_and_process_workout([exercise])
    max_loads = get_max_load(exercise)

    assert max_loads['0_b'] > max_loads['0_a'] > max_loads['0_c']
