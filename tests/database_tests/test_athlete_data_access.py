import pytest
import os
import json
from aws_xray_sdk.core import xray_recorder
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from datastores.heart_rate_datastore import HeartRateDatastore
from datastores.sleep_history_datastore import SleepHistoryDatastore
from models.soreness import CompletedExercise
from datetime import datetime
from config import get_secret


@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):
    os.environ["ENVIRONMENT"] = "dev"

    xray_recorder.configure(sampling=False)
    xray_recorder.begin_segment(name="test")

    config = get_secret('mongo')
    os.environ["MONGO_HOST"] = config['host']
    os.environ["MONGO_REPLICASET"] = config['replicaset']
    os.environ["MONGO_DATABASE"] = config['database']
    os.environ["MONGO_USER"] = config['user']
    os.environ["MONGO_PASSWORD"] = config['password']
    os.environ["MONGO_COLLECTION_DAILYREADINESS"] = config['collection_dailyreadiness']
    os.environ["MONGO_COLLECTION_DAILYPLAN"] = config['collection_dailyplan']
    os.environ["MONGO_COLLECTION_EXERCISELIBRARY"] = config['collection_exerciselibrary']
    os.environ["MONGO_COLLECTION_TRAININGSCHEDULE"] = config['collection_trainingschedule']
    os.environ["MONGO_COLLECTION_ATHLETESEASON"] = config['collection_athleteseason']
    os.environ["MONGO_COLLECTION_ATHLETESTATS"] = config['collection_athletestats']
    os.environ["MONGO_COLLECTION_COMPLETEDEXERCISES"] = config['collection_completedexercises']
    os.environ["MONGO_COLLECTION_HEARTRATE"] = config['collection_heartrate']

def test_get_readiness_survey_test_data():
    athlete_dao = DailyReadinessDatastore()
    last_daily_readiness_survey = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad")
    assert None is not last_daily_readiness_survey

def test_multi_get_readiness_survey_test_data():
    athlete_dao = DailyReadinessDatastore()
    last_daily_readiness_survey = athlete_dao.get(["jjones@email.com", "rrobbins@fakemail.com"], datetime(2018, 7, 12, 3, 0, 0), datetime(2018, 7, 12, 23, 59, 59), False)
    assert None is not last_daily_readiness_survey
    assert len(last_daily_readiness_survey) == 2

def test_get_daily_plan_many():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad","2018-06-01","2018-08-13")
    assert None is not plans

def test_get_daily_plan_users_list():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get(["02cb7965-7921-493a-80d4-6b278c928fad"],"2018-06-01","2018-08-13")
    assert None is not plans

def test_get_daily_plan_users_list_no_plans():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get(["02cb7965"],"2018-06-01","2018-08-13")
    assert None is not plans
    assert plans == []

def test_get_daily_plan_doesnt_exist():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad","2018-08-01","2018-08-13")
    assert None is not plans


def test_get_post_session_surveys():
    athlete_dao = PostSessionSurveyDatastore()
    surveys = athlete_dao.get("morning_practice_2", datetime(2018, 7, 10, 0, 0, 0), datetime(2018, 7, 11, 0, 0, 0))
    assert len(surveys) == 2


def test_get_session_heartrate_data():
    athlete_dao = HeartRateDatastore()
    session_heart_rates = athlete_dao.get(user_id='hr_test', session_id='hr_session_1')
    assert len(session_heart_rates) == 1
    assert len(session_heart_rates[0].hr_workout) == 7


def test_get_heartrate_data_range():
    athlete_dao = HeartRateDatastore()
    session_heart_rates = athlete_dao.get(user_id='hr_test', start_date='2018-01-09', end_date="2018-01-15")
    assert len(session_heart_rates) == 3
    assert len(session_heart_rates[0].hr_workout) == 7

def test_get_sleep_data_day():
    athlete_dao = SleepHistoryDatastore()
    sleep_history = athlete_dao.get(user_id='test_sleep', start_date='2018-01-09')
    assert len(sleep_history) == 1
    assert len(sleep_history[0].sleep_events) == 10


def test_get_sleep_data_range():
    athlete_dao = SleepHistoryDatastore()
    sleep_history = athlete_dao.get(user_id='test_sleep', start_date='2018-01-09', end_date="2018-01-15")
    assert len(sleep_history) == 2
    assert len(sleep_history[0].sleep_events) == 10

def test_put_completed_exercises():
    data_store = CompletedExerciseDatastore()
    exercise = CompletedExercise("test_user", "79", datetime(2018, 8, 11, 2, 0, 0))
    data_store.put(exercise)
    exercise_summary = data_store.get("test_user",  datetime(2018, 7, 11, 2, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                      datetime(2018, 8, 11, 2, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"))
    assert None is not exercise_summary

