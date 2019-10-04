import pytest
import os
import json
from aws_xray_sdk.core import xray_recorder
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.asymmetry_datastore import AsymmetryDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from datastores.heart_rate_datastore import HeartRateDatastore
from datastores.sleep_history_datastore import SleepHistoryDatastore
from models.soreness import CompletedExercise
from datetime import datetime, timedelta
from config import get_secret
from models.asymmetry import AsymmetryType
from routes.three_sensor import get_sessions_detail
from utils import format_datetime
from fathomapi.utils.exceptions import NoSuchEntityException
from utils import format_date

@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):
    os.environ["ENVIRONMENT"] = "test"

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
    os.environ["MONGO_COLLECTION_ASYMMETRY"] = config['collection_asymmetry']

    os.environ["MONGO_COLLECTION_DAILYREADINESSTEST"] = config['collection_dailyreadinesstest']
    os.environ["MONGO_COLLECTION_DAILYPLANTEST"] = config['collection_dailyplantest']
    os.environ["MONGO_COLLECTION_ATHLETESTATSTEST"] = config['collection_athletestatstest']
    os.environ["MONGO_COLLECTION_COMPLETEDEXERCISESTEST"] = config['collection_completedexercisestest']


def test_biomechanics_detail_0_asymmetry_type():
    #user_id = "2b4a1792-42c7-460e-9e4c-98627e72cc6f"
    user_id = "bdb8b194-e748-4197-819b-b356f1fb0629"
    event_date = datetime.now()
    sessions = get_sessions_detail(user_id, event_date, 0)
    assert len(sessions) > 0


def test_biomechanics_detail_1_asymmetry_type():
    #user_id = "2b4a1792-42c7-460e-9e4c-98627e72cc6f"
    user_id = "bdb8b194-e748-4197-819b-b356f1fb0629"
    event_date = datetime.now()
    sessions = get_sessions_detail(user_id, event_date, 1)
    assert len(sessions) > 1

def test_biomechanics_detail_2_asymmetry_type():
    #user_id = "2b4a1792-42c7-460e-9e4c-98627e72cc6f"
    user_id = "bdb8b194-e748-4197-819b-b356f1fb0629"
    event_date = datetime.now()
    sessions = get_sessions_detail(user_id, event_date, 2)
    assert len(sessions) > 1


def test_biomechanics_detail_no_asymmetry_type():
    #user_id = "917e94bc-3f56-4519-8d25-ae54878748f2"
    user_id = "bdb8b194-e748-4197-819b-b356f1fb0629"
    event_date = datetime.now()
    sessions = get_sessions_detail(user_id, event_date, 3)
    assert len(sessions) == 0