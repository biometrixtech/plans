from models.functional_movement import FunctionalMovementActionMapping, FunctionalMovementFactory
from models.session import MixedActivitySession
from models.session_functional_movement import SessionFunctionalMovement
from logic.workout_processing import WorkoutProcessor
from models.workout_program import WorkoutExercise, WorkoutSection, WorkoutProgramModule
from models.movement_tags import TrainingType
from models.movement_actions import ExerciseAction
from models.exercise import UnitOfMeasure
import datetime


def get_session(rpe=5, duration=100, workout_program=None):
    session = MixedActivitySession()
    session.event_date = datetime.datetime.now()
    session.session_RPE = rpe
    session.duration_minutes = duration
    session.workout_program_module = workout_program

    return session


def create_and_process_workout(exercises):
    section = WorkoutSection()
    section.name = 'stamina'
    section.exercises = exercises

    workout = WorkoutProgramModule()
    workout.workout_sections = [section]
    processor = WorkoutProcessor()
    processor.process_workout(workout)
    return workout


def get_exercise(reps=1, sets=1, unit=UnitOfMeasure.seconds, movement_id=""):
    exercise = WorkoutExercise()
    exercise.reps_per_set = reps
    exercise.sets = sets
    exercise.unit_of_measure = unit
    exercise.movement_id = movement_id
    exercise.pace = 120
    exercise.stroke_rate = 22
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


def get_session_load_dict(session):
    session_functional_movement = SessionFunctionalMovement(session, {})
    session_functional_movement.process(session.event_date.date(), None)
    return session_functional_movement.session_load_dict


def get_max_action_load(functional_movement_action_mapping):
    max_action_load = 0
    for muscle_load in functional_movement_action_mapping.muscle_load.values():
        max_action_load = max([max_action_load, muscle_load.eccentric_load, muscle_load.concentric_load])
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


def test_rowing():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459d9ddc2ce90011f93d84")  # rowing
    exercise.pace = .24
    workout_program = create_and_process_workout([exercise])
    for action in exercise.primary_actions:
        assert action.force == round(2.8 / (120 / 500) ** 2, 2)
    session = get_session(workout_program=workout_program, rpe=5, duration=5)
    session_load_dict = get_session_load_dict(session)
    for body_part, muscle_load in session_load_dict.items():
        assert muscle_load.total_normalized_load in [.2, 0]


def test_rowing_stroke_rate_25():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459d9ddc2ce90011f93d84")  # rowing
    exercise.stroke_rate = 25
    exercise.pace = .24
    create_and_process_workout([exercise])
    for action in exercise.primary_actions:
        assert action.force == round(2.8 / (120 / 500) ** 2, 2)


def test_running():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459df8dc2ce90011f93d87")  # running
    exercise.pace = None
    exercise.cadence = 170  # rep tempo = 3
    exercise.duration = 3000
    exercise.power = 100
    exercise.speed = 5
    create_and_process_workout([exercise])
    for action in exercise.primary_actions:
        assert action.force == round(100 / 5, 2)
        assert action.pace == .2
        assert action.distance == 5 * 3000


def test_walking():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="58459df8dc2ce90011f93d87")  # running
    exercise.pace = None
    exercise.cadence = 120  # rep tempo = 1
    exercise.duration = 3000
    exercise.power = 100
    exercise.speed = 5
    create_and_process_workout([exercise])
    for action in exercise.primary_actions:
        assert action.force == round(100 / 5, 2)
        assert action.pace == .2
        assert action.distance == 5 * 3000


def test_cycling():
    exercise = get_exercise(reps=3000, sets=1, unit=UnitOfMeasure.seconds, movement_id="57e2fd3a4c6a031dc777e90c")  # airdyne
    exercise.reps_per_set = None
    exercise.pace = None
    exercise.cadence = 120  # rep tempo = 4
    exercise.distance = 5000
    exercise.power = 100
    exercise.speed = 5
    create_and_process_workout([exercise])
    for action in exercise.primary_actions:
        assert action.force == round(100 / 5, 2)
        assert action.pace == .2
        assert action.duration == 1000
        assert action.training_volume_left == action.training_volume_right == 1000
