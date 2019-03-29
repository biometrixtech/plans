import pytest
import os
import json
from aws_xray_sdk.core import xray_recorder
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore as mock_readiness
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore as mock_plans
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore as mock_pss
from tests.mocks.mock_datastore_collection import DatastoreCollection
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from logic.insights_processing import InsightsProcessing
from logic.stats_processing import StatsProcessing
from logic.training_volume_processing import TrainingVolumeProcessing
from models.stats import AthleteStats
# from models.training_volume import TrainingLevel
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from models.soreness import CompletedExercise
from datetime import datetime, timedelta
from config import get_secret
from utils import parse_date, format_date

@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):
    os.environ["ENVIRONMENT"] = "production"

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


def test_get_training_plan_from_database():

    users = []
    #users.append('0dd21808-55f9-45f2-a408-b1713d40681f') #mw
    users.append('93176a69-2d5d-4326-b986-ca6b04a9a29d') #liz
    users.append('e4fff5dc-6467-4717-8cef-3f2cb13e5c33')  #abbey
    users.append('82ccf294-7c1e-48e6-8149-c5a001e76f78')  #pene
    users.append('8bca10bf-8bdd-4971-85ca-cb2712c32478') #rhonda
    users.append('5e516e2e-ac2d-425e-ba4d-bf2689c28cec')  #td
    users.append('4f5567c7-a592-4c26-b89d-5c1287884d37')  #megan
    users.append('fac4be57-35d6-4952-8af9-02aadf979982')  #bay
    users.append('e9d78b6f-8695-4556-9369-d6a5702c6cc7') #mwoodard
    users.append('5756fac1-3080-4979-9746-9d4c9a700acf') #lillian

    for user_id in users:
        start_date = "2018-11-23"
        end_date = "2019-03-23"

        drs_dao = DailyReadinessDatastore()
        daily_readiness_surveys = drs_dao.get(user_id, parse_date(start_date), parse_date(end_date), False)
        dpo_dao = DailyPlanDatastore()
        plans = dpo_dao.get(user_id, start_date, end_date)
        #pss_dao = PostSessionSurveyDatastore()
        #surveys = pss_dao.get(user_id, parse_date(start_date), parse_date(end_date))
        #stats_dao = AthleteStatsDatastore()
        #ath_stats = stats_dao.get(user_id)

        #daily_plan_datastore = mock_plans()
        #daily_plan_datastore.side_load_plans(plans)
        #daily_readiness_datastore = mock_readiness()
        #daily_readiness_datastore.side_load_surveys(daily_readiness_surveys)
        #post_session_datastore = mock_pss()
        #post_session_datastore.side_load_surveys(surveys)

        #datastore_collection = DatastoreCollection()
        #datastore_collection.daily_plan_datastore = daily_plan_datastore
        #datastore_collection.daily_readiness_datastore = daily_readiness_datastore
        #datastore_collection.post_session_survey_datastore = post_session_datastore

        insights_processing = InsightsProcessing(user_id)
        insights_processing.load_surveys(daily_readiness_surveys, plans)
        contingency_tables = insights_processing.get_contingency_tables(datetime(2018, 11, 23), datetime(2019, 3, 23), 5)
        for c in contingency_tables:
            if c.chi_square_significant_05:
                k=1
            elif c.chi_square_significant_10:
                k=1

