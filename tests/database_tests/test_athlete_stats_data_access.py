import pytest
from aws_xray_sdk.core import xray_recorder
from config import get_secret
import os
import json
from logic.stats_processing import StatsProcessing
from models.stats import AthleteStats
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from datastores.datastore_collection import DatastoreCollection


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

def test_ryan_robbins_athlete_stats_day_after_week():
    user_id = "rrobbins@fakemail.com"
    athlete_stats_datastore = AthleteStatsDatastore()
    calc = StatsProcessing(user_id, "2018-07-19", DatastoreCollection())
    calc.process_athlete_stats()
    athlete_stats_retrieved = athlete_stats_datastore.get(user_id)
    assert None is not athlete_stats_retrieved


def test_ryan_robbins_athlete_stats_last_day_of_week():
    user_id = "rrobbins@fakemail.com"
    athlete_stats_datastore = AthleteStatsDatastore()
    calc = StatsProcessing(user_id, "2018-07-18", DatastoreCollection())
    calc.process_athlete_stats()
    athlete_stats_retrieved = athlete_stats_datastore.get(user_id)
    assert None is not athlete_stats_retrieved


def test_single_athlete_stats_query():
    user_id = "fd263811-b299-461f-9e79-895c69612bac"
    athlete_stats_datastore = AthleteStatsDatastore()
    athlete_stats_retrieved = athlete_stats_datastore.get(user_id)
    assert None is not athlete_stats_retrieved

def test_multi_athlete_stats_query():
    user_id = ["fd263811-b299-461f-9e79-895c69612bac", "d8e4d148-1918-4b7f-867e-72d2be319145"]
    athlete_stats_datastore = AthleteStatsDatastore()
    athlete_stats_retrieved = athlete_stats_datastore.get(user_id)
    assert None is not athlete_stats_retrieved


def test_delete_athlete_stats_one():
    athlete_dao = AthleteStatsDatastore(mongo_collection='athletestatstest')
    existing_stats = athlete_dao.get(athlete_id="persona1")
    athlete_dao.delete(athlete_id='persona1')
    new_stats = athlete_dao.get("persona1")
    athlete_dao.put(existing_stats)

    assert new_stats is None

def test_delete_athlete_stats_multi_users():
    athlete_dao = AthleteStatsDatastore(mongo_collection='athletestatstest')
    users = ['persona1', 'persona2']
    existing_stats = athlete_dao.get(athlete_id=users)
    athlete_dao.delete(athlete_id=users)
    new_stats = athlete_dao.get(athlete_id=users)
    athlete_dao.put(existing_stats)

    assert len(new_stats) == 0