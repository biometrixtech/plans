from models.functional_movement import FunctionalMovementPairs, FunctionalMovementActionMapping, FunctionalMovementFactory
from models.functional_movement_type import FunctionalMovementType
from models.movement_actions import MuscleAction, ExerciseAction, PrioritizedJointAction
from models.workout_program import WorkoutExercise
from models.soreness_base import BodyPartLocation, BodyPartSide


from logic.workout_processing import WorkoutProcessor
from models.workout_program import WorkoutExercise, WorkoutSection, WorkoutProgramModule
from models.movement_tags import AdaptationType, CardioAction, TrainingType
from models.movement_actions import ExerciseAction, Movement, Explosiveness
from models.exercise import UnitOfMeasure
import datetime
from utils import format_datetime



def create_and_process_wokout(exercises):
    section = WorkoutSection()
    section.name = 'stamina'
    section.exercises = exercises

    workout = WorkoutProgramModule()
    workout.workout_sections = [section]
    processor = WorkoutProcessor()
    processor.process_workout(workout)

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


def test_run():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="5823768d473c06100052ed9a")  # run
    create_and_process_wokout([exercise])

    factory = FunctionalMovementFactory()
    functional_movement_dict = factory.get_functional_movement_dictinary()
    total_loads = {}
    for exercise_action in exercise.primary_actions:
        try:
            functional_movement_action_mapping = FunctionalMovementActionMapping(exercise_action, {}, datetime.datetime.now(), functional_movement_dict)
            action_load = 0
            for muscle_load in functional_movement_action_mapping.muscle_load.values():
                action_load += muscle_load.eccentric_load
                action_load += muscle_load.concentric_load
            total_loads[exercise_action.id] = action_load
        except:
            pass
    assert total_loads['1_a'] > total_loads ['1_b'] > total_loads['1_c']


def test_sprint():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459de6dc2ce90011f93d86")  # sprint
    create_and_process_wokout([exercise])

    factory = FunctionalMovementFactory()
    functional_movement_dict = factory.get_functional_movement_dictinary()
    total_loads = {}
    for exercise_action in exercise.primary_actions:
        try:
            functional_movement_action_mapping = FunctionalMovementActionMapping(exercise_action, {}, datetime.datetime.now(), functional_movement_dict)
            action_load = 0
            for muscle_load in functional_movement_action_mapping.muscle_load.values():
                action_load += muscle_load.eccentric_load
                action_load += muscle_load.concentric_load
            total_loads[exercise_action.id] = action_load
        except:
            pass
    assert total_loads['2_a'] > total_loads ['2_b'] > total_loads['2_c']

