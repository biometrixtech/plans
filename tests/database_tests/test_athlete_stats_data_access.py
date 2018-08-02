import pytest
from aws_xray_sdk.core import xray_recorder
from config import get_secret
import os
import json
from logic.stats_processing import StatsProcessing
from models.stats import AthleteStats
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore


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

def test_ryan_robbins_athlete_stats_day_after_week():
    user_id = "rrobbins@fakemail.com"
    athlete_stats_datastore = AthleteStatsDatastore()
    calc = StatsProcessing(user_id, "2018-07-19", DailyReadinessDatastore(), PostSessionSurveyDatastore(),
                           athlete_stats_datastore)
    calc.process_athlete_stats()
    athlete_stats_retrieved = athlete_stats_datastore.get(user_id)
    assert None is not athlete_stats_retrieved


def test_ryan_robbins_athlete_stats_last_day_of_week():
    user_id = "rrobbins@fakemail.com"
    athlete_stats_datastore = AthleteStatsDatastore()
    calc = StatsProcessing(user_id, "2018-07-18", DailyReadinessDatastore(), PostSessionSurveyDatastore(),
                           AthleteStatsDatastore())
    calc.process_athlete_stats()
    athlete_stats_retrieved = athlete_stats_datastore.get(user_id)
    assert None is not athlete_stats_retrieved