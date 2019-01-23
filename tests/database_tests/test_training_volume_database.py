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
from logic.stats_processing import StatsProcessing
from logic.training_volume_processing import TrainingVolumeProcessing
from models.stats import AthleteStats
from models.training_volume import TrainingLevel
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from models.soreness import CompletedExercise
from datetime import datetime
from config import get_secret
from utils import parse_date

@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):
    os.environ["ENVIRONMENT"] = "production"

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

    okay_list = []
    okay_optimal_list = []
    risk_list = []
    rate_limiting_factor = []
    risk_rate_limitiing_factor = []
    okay_severity_list = []
    risk_severity_list = []

    users = []
    users.append('93176a69-2d5d-4326-b986-ca6b04a9a29d') #liz
    users.append('e4fff5dc-6467-4717-8cef-3f2cb13e5c33')  #abbey
    users.append('82ccf294-7c1e-48e6-8149-c5a001e76f78')  #pene
    users.append('8bca10bf-8bdd-4971-85ca-cb2712c32478') #rhonda
    users.append('5e516e2e-ac2d-425e-ba4d-bf2689c28cec')  #td
    users.append('4f5567c7-a592-4c26-b89d-5c1287884d37')  #megan
    users.append('fac4be57-35d6-4952-8af9-02aadf979982')  #bay
    for user_id in users:
        start_date = "2018-10-31"
        end_date = "2019-01-16"
        run_date = "2019-01-16"
        drs_dao = DailyReadinessDatastore()
        daily_readiness_surveys = drs_dao.get(user_id, parse_date(start_date), parse_date(end_date), False)
        dpo_dao = DailyPlanDatastore()
        plans = dpo_dao.get(user_id, start_date, end_date)
        pss_dao = PostSessionSurveyDatastore()
        surveys = pss_dao.get(user_id, parse_date(start_date), parse_date(end_date))
        stats_dao = AthleteStatsDatastore()
        ath_stats = stats_dao.get(user_id)

        daily_plan_datastore = mock_plans()
        daily_plan_datastore.side_load_plans(plans)
        daily_readiness_datastore = mock_readiness()
        daily_readiness_datastore.side_load_surveys(daily_readiness_surveys)
        post_session_datastore = mock_pss()
        post_session_datastore.side_load_surveys(surveys)

        datastore_collection = DatastoreCollection()
        datastore_collection.daily_plan_datastore = daily_plan_datastore
        datastore_collection.daily_readiness_datastore = daily_readiness_datastore
        datastore_collection.post_session_survey_datastore = post_session_datastore

        stats = StatsProcessing(user_id, run_date, datastore_collection)
        success = stats.set_start_end_times()
        stats.load_historical_data()
        athlete_stats = AthleteStats(user_id)
        athlete_stats.historic_soreness = ath_stats.historic_soreness
        training_volume_processing = TrainingVolumeProcessing(stats.start_date, stats.end_date)
        athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats, stats.last_7_days_plans,
                                                                                stats.days_8_14_plans,
                                                                                stats.acute_daily_plans,
                                                                                stats.get_chronic_weeks_plans(),
                                                                                stats.chronic_daily_plans)
        report = training_volume_processing.get_training_report(athlete_stats,
                                                                stats.last_7_days_plans,
                                                                stats.days_8_14_plans,
                                                                stats.acute_start_date_time,
                                                                stats.chronic_start_date_time,
                                                                stats.acute_daily_plans,
                                                                stats.chronic_daily_plans,
                                                                stats.end_date_time)

        if report.high_threshold > 0:
            okay_list.append(user_id)
            rate_limiting_factor.append(report.most_limiting_gap_type_high)
            okay_severity_list.append(report.average_hs_severity)
            if report.training_level != TrainingLevel.undertraining:
                okay_optimal_list.append(user_id)
        else:
            risk_list.append(user_id)
            risk_rate_limitiing_factor.append(report.most_limiting_gap_type_high)
            risk_severity_list.append(report.average_hs_severity)

    assert athlete_stats.acute_internal_total_load == 2590