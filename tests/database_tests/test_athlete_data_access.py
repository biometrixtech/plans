import pytest
import os
import json
from aws_xray_sdk.core import xray_recorder
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from models.exercise import CompletedExercise
from datetime import datetime
from config import get_secret


@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):
    os.environ["ENVIRONMENT"] = "dev"

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
    os.environ["MONGO_COLLECTION_FUNCTIONALSTRENGTH"] = config['collection_functionalstrength']

def test_get_readiness_survey_test_data():
    athlete_dao = DailyReadinessDatastore()
    last_daily_readiness_survey = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad")
    assert None is not last_daily_readiness_survey


def test_get_daily_plan_many():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad","2018-06-01","2018-08-13")
    assert None is not plans


def test_get_daily_plan_doesnt_exist():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad","2018-08-01","2018-08-13")
    assert None is not plans


def test_get_post_session_surveys():
    athlete_dao = PostSessionSurveyDatastore()
    surveys = athlete_dao.get("morning_practice_2", "2018-07-10", "2018-07-11")
    assert None is surveys

def test_put_completed_exercises():
    data_store = CompletedExerciseDatastore()
    exercise = CompletedExercise("test_user", "79", datetime(2018, 8, 11, 2, 0, 0))
    data_store.put(exercise)
    exercise_summary = data_store.get("test_user",  datetime(2018, 7, 11, 2, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                      datetime(2018, 8, 11, 2, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"))
    assert None is not exercise_summary

