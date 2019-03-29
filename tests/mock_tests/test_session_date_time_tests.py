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
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def create_plan():
    user_id = "tester"

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    daily_plan_datastore = DailyPlanDatastore()

    soreness_list = [TestUtilities().body_part_soreness(12, 1)]

    survey = DailyReadiness(current_date_time.strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 7, 9)

    daily_plan = DailyPlan(format_date(current_date))
    daily_plan.user_id = user_id
    daily_plan.daily_readiness_survey = survey
    daily_plan_datastore.side_load_plans([daily_plan])

    mgr = TrainingPlanManager(user_id, DatastoreCollection())

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


