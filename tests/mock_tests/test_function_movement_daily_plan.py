
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from models.session import SportTrainingSession
from datetime import datetime, timedelta
from models.sport import SportName
from models.functional_movement import ActivityFunctionalMovementFactory, FunctionalMovementFactory, BodyPartFunctionalMovement, SessionFunctionalMovement
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation, BodyPartSide
from models.stats import AthleteStats
from logic.injury_risk_processing import InjuryRiskProcessor
from logic.functional_exercise_mapping import ExerciseAssignmentCalculator
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def get_sessions(dates, rpes, durations, sport_names):

    if len(dates) != len(rpes) != len(durations) != len(sport_names):
        raise Exception("dates, rpes, durations must match in length")

    sessions = []

    for d in range(0, len(dates)):
        session = SportTrainingSession()
        session.event_date = dates[d]
        session.session_RPE = rpes[d]
        session.duration_minutes = durations[d]
        session.sport_name = sport_names[d]
        sessions.append(session)

    return sessions

def test_create_plan_no_session():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.sharp = 3
    soreness.reported_date_time = now_date

    proc = InjuryRiskProcessor (now_date, [soreness], [], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignmentCalculator(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore, now_date)

    active_rest = calc.get_pre_active_rest()[0]
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert len(active_rest.exercise_phases[2].exercises) > 0

    # assert len(active_rest[0].inhibit_exercises) > 0
    # assert len(active_rest[0].static_stretch_exercises) > 0
    # assert len(active_rest[0].active_stretch_exercises) > 0

def test_create_plan_with_session():

    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.tight = 1
    soreness.reported_date_time = dates[0]

    soreness_2 = Soreness()
    soreness_2.body_part = BodyPart(BodyPartLocation(7), None)
    soreness_2.side = 1
    soreness_2.sharp = 2
    soreness_2.reported_date_time = dates[0]

    proc = InjuryRiskProcessor(dates[0], [soreness, soreness_2], sessions, {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignmentCalculator(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        dates[0])

    active_rest = calc.get_pre_active_rest()[0]
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert len(active_rest.exercise_phases[2].exercises) > 0

    # assert len(active_rest[0].inhibit_exercises) > 0
    # assert len(active_rest[0].static_stretch_exercises) >0
    # assert len(active_rest[0].active_stretch_exercises) > 0