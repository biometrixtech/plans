import os
os.environ['ENVIRONMENT'] = 'dev'
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from models.session import SportTrainingSession
from datetime import datetime, timedelta
from models.sport import SportName
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation
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


def test_historical_update_single_day_data():

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

    proc = InjuryRiskProcessor(dates[0], [soreness, soreness_2], sessions, {})
    injury_risk_dict = proc.process(update_historical_data=True)
    assert len(injury_risk_dict) > 0


def test_historical_update_multiple_day_data():
    user_id = 'test'
    now_date = datetime.now()
    one_day_ago = now_date - timedelta(days=1)
    ten_days_ago = now_date - timedelta(days=10)
    dates = [ten_days_ago, one_day_ago, now_date]
    rpes = [5, 5, 3]
    durations = [100, 100, 100]
    sport_names = [SportName.distance_running, SportName.distance_running, SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.tight = 1
    soreness.reported_date_time = ten_days_ago

    soreness_2 = Soreness()
    soreness_2.body_part = BodyPart(BodyPartLocation(7), None)
    soreness_2.side = 1
    soreness_2.sharp = 2
    soreness_2.reported_date_time = one_day_ago

    soreness_3 = Soreness()
    soreness_3.body_part = BodyPart(BodyPartLocation(7), None)
    soreness_3.side = 1
    soreness_3.sharp = 2
    soreness_3.reported_date_time = now_date

    # make historical update
    proc = InjuryRiskProcessor(one_day_ago, [soreness, soreness_2], sessions[:2], {})
    injury_risk_dict = proc.process(update_historical_data=True)

    # update with new information
    proc = InjuryRiskProcessor(now_date, [soreness_3], [sessions[2]], injury_risk_dict)
    injury_risk_dict = proc.process(aggregate_results=True)

    calc = ExerciseAssignmentCalculator(injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        dates[0])

    active_rest = calc.get_pre_active_rest()

    assert len(active_rest[0].inhibit_exercises) > 0
    assert len(active_rest[0].active_stretch_exercises) > 0
    assert len(active_rest[0].isolated_activate_exercises) > 0

