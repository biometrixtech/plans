import os, json, pytest
import datetime
from logic.workout_processing import WorkoutProcessor
from logic.injury_risk_processing import InjuryRiskProcessor
from logic.exercise_assignment import ExerciseAssignment
from models.workout_program import WorkoutProgramModule
from models.planned_exercise import PlannedWorkout, PlannedWorkoutSection, PlannedExercise
from models.session import MixedActivitySession, PlannedSession
from models.sport import SportName
from models.user_stats import UserStats
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


# TODO: have this work with the planned_exercise models
# TODO: update plans logic and related to handle "planned load" vs actual

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def read_json(file_name):
    if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
        file_name = f"tests/data/otf/{file_name}.json"
    else:
        file_name = os.path.join(os.path.realpath(".."), f"data/otf/{file_name}.json")
    with open(file_name, 'r') as f:
        workout = json.load(f)
    return workout


# def get_workout_program(file_name):
#     workout_json = read_json(file_name)
#     workout_program_module = WorkoutProgramModule.json_deserialise(workout_json)
#     WorkoutProcessor().process_workout(workout_program_module)
#     return workout_program_module


def get_sport_body_parts(training_sessions):
    sport_body_parts = {}
    for session in training_sessions:
        sport_body_parts.update(session.get_load_body_parts())
    return sport_body_parts


def check_cardio_sport(training_sessions):
    sport_cardio_plyometrics = False
    for session in training_sessions:
        if session.is_cardio_plyometrics():
            sport_cardio_plyometrics = True
    return sport_cardio_plyometrics


def is_high_intensity_session(training_sessions):
    for session in training_sessions:
        if session.ultra_high_intensity_session() and session.high_intensity_RPE():
            return True
    return False


def get_session(date, rpe=5, duration=60, file_name=None, assignment_type='default'):
    # session = MixedActivitySession()
    # session.event_date = date
    # session.session_RPE = rpe
    # session.duration_minutes = duration
    # session.sport_name = SportName.high_intensity_interval_training

    planned_session = PlannedSession()
    planned_session.event_date = date
    workout_json = read_json(file_name)
    #workout_program_module = WorkoutProgramModule.json_deserialise(workout_json)
    planned_workout = PlannedWorkout.json_deserialise(workout_json)
    planned_session.workout = planned_workout
    WorkoutProcessor(user_weight=60).process_planned_workout(planned_session, assignment_type)

    return planned_session


def get_activity(event_date_time, symptoms, sessions):
    proc = InjuryRiskProcessor(event_date_time, symptoms, sessions, {}, UserStats("tester"), "tester")
    proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()
    calc = ExerciseAssignment(
            injury_risk_dict=consolidated_injury_risk_dict,
            exercise_library_datastore=exercise_library_datastore,
            completed_exercise_datastore=completed_exercise_datastore,
            event_date_time=event_date_time,
            relative_load_level=proc.relative_load_level,
            aggregated_injury_risk_dict=proc.aggregated_injury_risk_dict
    )
    calc.sport_cardio_plyometrics = check_cardio_sport(sessions)
    calc.sport_body_parts = get_sport_body_parts(sessions)
    movement_prep = calc.get_movement_integration_prep(force_on_demand=True)
    return movement_prep


def test_may1():
    session_power_walker = get_session(datetime.datetime.now(), file_name='may1_alt', assignment_type='power_walker')
    session_runner = get_session(datetime.datetime.now(), file_name='may1_alt', assignment_type='runner')
    session_jogger = get_session(datetime.datetime.now(), file_name='may1_alt', assignment_type='jogger')
    #session = get_session(datetime.datetime.now(), file_name='may1_alt')

    movement_prep_power_walker = get_activity(datetime.datetime.now(), [], [session_power_walker])
    movement_prep_runner = get_activity(datetime.datetime.now(), [], [session_runner])
    movement_prep_jogger = get_activity(datetime.datetime.now(), [], [session_jogger])
    assigned_exercises = {}
    for ex_phase in movement_prep_power_walker[0].exercise_phases:
        assigned_exercises[ex_phase.name] = list(ex_phase.exercises.keys())
    print('here')
#
#
# def test_may2():
#     session = get_session(datetime.datetime.now(), file_name='may2')
#     movement_prep = get_activity(datetime.datetime.now(), [], [session])
#     assigned_exercises = {}
#     for ex_phase in movement_prep[0].exercise_phases:
#         assigned_exercises[ex_phase.name] = list(ex_phase.exercises.keys())
#     print('here')
#
#
# def test_at_home1():
#     session = get_session(datetime.datetime.now(), file_name='at_home1')
#     movement_prep = get_activity(datetime.datetime.now(), [], [session])
#     assigned_exercises = {}
#     for ex_phase in movement_prep[0].exercise_phases:
#         assigned_exercises[ex_phase.name] = list(ex_phase.exercises.keys())
#     print('here')