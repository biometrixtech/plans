from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from logic.training_plan_management import TrainingPlanManager
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection
from models.session import PracticeSession, Game, StrengthConditioningSession
from models.stats import AthleteStats
from datetime import datetime, timedelta, date, time
from utils import format_datetime, format_date
from tests.testing_utilities import TestUtilities
from models.daily_readiness import DailyReadiness
from models.daily_plan import DailyPlan
from models.soreness import BodyPartLocation, HistoricSoreness, HistoricSorenessStatus
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def create_plan(body_part_list, severity_list, side_list, pain_list, historic_soreness_list=None):
    user_id = "tester"

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    daily_plan_datastore = DailyPlanDatastore()

    soreness_list = []
    for b in range(0, len(body_part_list)):
        if len(pain_list) > 0 and pain_list[b]:
            soreness_list.append(TestUtilities().body_part_pain(body_part_list[b], severity_list[b], side_list[b]))
        else:
            if len(severity_list) == 0:
                soreness_list.append(TestUtilities().body_part_soreness(body_part_list[b], 2))
            else:
                soreness_list.append(TestUtilities().body_part_soreness(body_part_list[b], severity_list[b]))




    survey = DailyReadiness(current_date_time.strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 7, 9)

    daily_plan = DailyPlan(format_date(current_date))
    daily_plan.user_id = user_id
    daily_plan.daily_readiness_survey = survey
    daily_plan_datastore.side_load_plans([daily_plan])
    data_store_collection = DatastoreCollection()
    data_store_collection.daily_plan_datastore = daily_plan_datastore
    data_store_collection.exercise_datastore = exercise_library_datastore

    if historic_soreness_list is not None and len(historic_soreness_list) > 0:
        athlete_stats_datastore = AthleteStatsDatastore()
        athlete_stats = AthleteStats(user_id)
        athlete_stats.historic_soreness = historic_soreness_list
        athlete_stats_datastore.side_load_athlete_stats(athlete_stats)
        data_store_collection.athlete_stats_datastore = athlete_stats_datastore

    mgr = TrainingPlanManager(user_id, data_store_collection)

    daily_plan = mgr.create_daily_plan(format_date(current_date), format_datetime(current_date_time))

    return daily_plan


def create_no_soreness_plan():
    user_id = "tester"

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    # daily_readiness_datastore = DailyReadinessDatastore()
    daily_plan_datastore = DailyPlanDatastore()
    athlete_stats_datastore = AthleteStatsDatastore()
    athlete_stats = AthleteStats("tester")

    soreness_list = []

    survey = DailyReadiness(current_date_time.strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 7, 9)
    daily_plan = DailyPlan(format_date(current_date))
    daily_plan.user_id = user_id
    daily_plan.daily_readiness_survey = survey
    daily_plan_datastore.side_load_plans([daily_plan])

    # daily_readiness_datastore.side_load_surveys([survey])
    athlete_stats_datastore.side_load_athlete_stats(athlete_stats)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    # datastore_collection.daily_readiness_datastore = daily_readiness_datastore
    datastore_collection.exercise_datastore = exercise_library_datastore
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    mgr = TrainingPlanManager(user_id, datastore_collection)

    daily_plan = mgr.create_daily_plan(format_date(current_date), last_updated=format_datetime(current_date_time))

    return daily_plan

def test_active_rest_after_training_knee():

    daily_plan = create_plan([7], [], [], [])
    assert len(daily_plan.post_active_rest.inhibit_exercises) > 0
    assert len(daily_plan.post_active_rest.static_stretch_exercises) > 0
    assert len(daily_plan.post_active_rest.isolated_activate_exercises) == 0
    assert len(daily_plan.post_active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_outer_thigh_hist_soreness_knee():

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(9, 0, 0))
    current_date_time = current_date_time - timedelta(days=16)

    historic_soreness = HistoricSoreness(BodyPartLocation(7), 1, True)
    historic_soreness.first_reported = current_date_time
    historic_soreness.historic_soreness_status = HistoricSorenessStatus.acute_pain
    historic_soreness_list = [historic_soreness]

    daily_plan = create_plan([11], [], [], [], historic_soreness_list)
    assert len(daily_plan.post_active_rest.inhibit_exercises) > 0
    assert len(daily_plan.post_active_rest.static_stretch_exercises) > 0
    assert len(daily_plan.post_active_rest.isolated_activate_exercises) > 0
    assert len(daily_plan.post_active_rest.static_integrate_exercises) > 0

def test_active_rest_after_training_outer_thigh_hist_soreness_glutes():

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(9, 0, 0))
    current_date_time = current_date_time - timedelta(days=16)

    historic_soreness = HistoricSoreness(BodyPartLocation(14), 1, True)
    historic_soreness.first_reported = current_date_time
    historic_soreness.historic_soreness_status = HistoricSorenessStatus.acute_pain
    historic_soreness_list = [historic_soreness]

    daily_plan = create_plan([11], [], [], [], historic_soreness_list)
    assert len(daily_plan.post_active_rest.inhibit_exercises) > 0
    assert len(daily_plan.post_active_rest.static_stretch_exercises) > 0
    assert len(daily_plan.post_active_rest.isolated_activate_exercises) > 0
    assert len(daily_plan.post_active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_various_hist_soreness_glutes():

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(9, 0, 0))
    current_date_time = current_date_time - timedelta(days=16)
    current_date_time_2 = current_date_time - timedelta(days=10)
    current_date_time_3 = current_date_time - timedelta(days=31)

    historic_soreness = HistoricSoreness(BodyPartLocation(14), 1, True)
    historic_soreness.first_reported = current_date_time
    historic_soreness.historic_soreness_status = HistoricSorenessStatus.acute_pain
    historic_soreness_2 = HistoricSoreness(BodyPartLocation(16), 1, False)
    historic_soreness_2.first_reported = current_date_time_2
    historic_soreness_2.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_soreness_3 = HistoricSoreness(BodyPartLocation(17), 1, False)
    historic_soreness_3.first_reported = current_date_time_3
    historic_soreness_3.historic_soreness_status = HistoricSorenessStatus.persistent_soreness

    historic_soreness_list = [historic_soreness, historic_soreness_2, historic_soreness_3]

    daily_plan = create_plan([6, 7, 11, 14, 16], [], [], [], historic_soreness_list)
    assert len(daily_plan.post_active_rest.inhibit_exercises) > 0
    assert len(daily_plan.post_active_rest.static_stretch_exercises) > 0
    assert len(daily_plan.post_active_rest.isolated_activate_exercises) > 0
    assert len(daily_plan.post_active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_quad_hist_soreness_knee():

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(9, 0, 0))
    current_date_time = current_date_time - timedelta(days=16)

    historic_soreness = HistoricSoreness(BodyPartLocation(7), 1, True)
    historic_soreness.first_reported = current_date_time
    historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
    historic_soreness.average_severity = 1.3

    historic_soreness_list = [historic_soreness]

    daily_plan = create_plan(body_part_list=[7, 6], severity_list=[2, 1], side_list=[1, 1], pain_list=[True, False], historic_soreness_list=historic_soreness_list)
    daily_plan_json = daily_plan.json_serialise()
    assert len(daily_plan.post_active_rest.inhibit_exercises) > 0
    assert len(daily_plan.post_active_rest.static_stretch_exercises) > 0
    assert len(daily_plan.post_active_rest.isolated_activate_exercises) > 0
    assert len(daily_plan.post_active_rest.static_integrate_exercises) > 0


def test_find_earlier_practice_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    practice_session = PracticeSession()
    practice_session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    practice_session_2 = PracticeSession()
    practice_session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.training_sessions.append(practice_session)
    daily_plan.training_sessions.append(practice_session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_practice_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    practice_session = PracticeSession()
    practice_session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    practice_session_2 = PracticeSession()
    practice_session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.training_sessions.append(practice_session)
    daily_plan.training_sessions.append(practice_session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)


def test_find_earlier_game_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    game_session = Game()
    game_session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    game_session_2 = Game()
    game_session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.training_sessions.append(game_session)
    daily_plan.training_sessions.append(game_session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_game_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    game_session = Game()
    game_session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    game_session_2 = Game()
    game_session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.training_sessions.append(game_session)
    daily_plan.training_sessions.append(game_session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)


def test_find_earlier_cross_training_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    session = StrengthConditioningSession()
    session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    session_2 = StrengthConditioningSession()
    session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.training_sessions.append(session)
    daily_plan.training_sessions.append(session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_cross_training_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    session = StrengthConditioningSession()
    session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    session_2 = StrengthConditioningSession()
    session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.training_sessions.append(session)
    daily_plan.training_sessions.append(session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)


