from training_plan_management import TrainingPlanManager
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from models.session import PracticeSession, Game, StrengthConditioningSession
from datetime import datetime, timedelta, date, time
from utils import format_datetime
from tests.testing_utilities import TestUtilities
from models.daily_readiness import DailyReadiness


def create_plan():
    user_id = "tester"

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    daily_readiness_datastore = DailyReadinessDatastore()

    soreness_list = [TestUtilities().body_part_soreness(12, 1)]

    survey = DailyReadiness(current_date_time.strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, soreness_list, 7, 9)

    daily_readiness_datastore.side_load_surveys([survey])

    mgr = TrainingPlanManager(user_id, ExerciseLibraryDatastore(), daily_readiness_datastore,
                              PostSessionSurveyDatastore(), DailyPlanDatastore())

    daily_plan = mgr.create_daily_plan()

    return daily_plan


def test_find_earlier_practice_sessions():

    daily_plan = create_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    practice_session = PracticeSession()
    practice_session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    practice_session_2 = PracticeSession()
    practice_session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.practice_sessions.append(practice_session)
    daily_plan.practice_sessions.append(practice_session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_practice_sessions():

    daily_plan = create_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    practice_session = PracticeSession()
    practice_session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    practice_session_2 = PracticeSession()
    practice_session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.practice_sessions.append(practice_session)
    daily_plan.practice_sessions.append(practice_session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)


def test_find_earlier_game_sessions():

    daily_plan = create_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    game_session = Game()
    game_session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    game_session_2 = Game()
    game_session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.practice_sessions.append(game_session)
    daily_plan.practice_sessions.append(game_session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_game_sessions():

    daily_plan = create_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    game_session = Game()
    game_session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    game_session_2 = Game()
    game_session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.practice_sessions.append(game_session)
    daily_plan.practice_sessions.append(game_session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)


def test_find_earlier_cross_training_sessions():

    daily_plan = create_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    session = StrengthConditioningSession()
    session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    session_2 = StrengthConditioningSession()
    session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.practice_sessions.append(session)
    daily_plan.practice_sessions.append(session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_cross_training_sessions():

    daily_plan = create_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    session = StrengthConditioningSession()
    session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    session_2 = StrengthConditioningSession()
    session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.practice_sessions.append(session)
    daily_plan.practice_sessions.append(session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)


