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
from datetime import datetime, timedelta
from config import get_secret
from utils import parse_date, format_date

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


def calc_historical_internal_strain(start_date, end_date, all_plans):

        target_dates = []

        all_plans.sort(key=lambda x: x[0])

        date_diff = parse_date(end_date) - parse_date(start_date)

        for i in range(1, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        index = 0
        strain_values = []

        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_plans = [p for p in all_plans if (p[0] + timedelta(index)) < p.get_event_datetime()[0] <= target_dates[t]]
                load_values.extend(list(x[1] for x in daily_plans if x is not None))
                strain = self.calculate_daily_strain(load_values)
                if strain is not None:
                    strain_values.append(strain)
                index += 1

        return strain_values


def get_dates(start_date, end_date):

    dates = []

    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates

'''deprecated for now
def test_get_training_plan_from_database():

    okay_list = []
    okay_optimal_list = []
    risk_list = []
    rate_limiting_factor = []
    risk_rate_limitiing_factor = []
    okay_severity_list = []
    risk_severity_list = []

    users = []
    #users.append('0dd21808-55f9-45f2-a408-b1713d40681f') #mw
    users.append('93176a69-2d5d-4326-b986-ca6b04a9a29d') #liz
    users.append('e4fff5dc-6467-4717-8cef-3f2cb13e5c33')  #abbey
    users.append('82ccf294-7c1e-48e6-8149-c5a001e76f78')  #pene
    users.append('8bca10bf-8bdd-4971-85ca-cb2712c32478') #rhonda
    users.append('5e516e2e-ac2d-425e-ba4d-bf2689c28cec')  #td
    users.append('4f5567c7-a592-4c26-b89d-5c1287884d37')  #megan
    users.append('fac4be57-35d6-4952-8af9-02aadf979982')  #bay
    for user_id in users:
        start_date = "2018-10-31"
        end_date = "2019-01-23"
        run_date = "2019-01-23"

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
        stats.all_plans = stats.daily_plan_datastore.get(stats.athlete_id, stats.start_date, stats.end_date)
        stats.update_start_times(daily_readiness_surveys, surveys, stats.all_plans)
        stats.set_acute_chronic_periods()
        stats.load_historical_plans()
        athlete_stats = AthleteStats(user_id)
        athlete_stats.historic_soreness = ath_stats.historic_soreness
        training_volume_processing = TrainingVolumeProcessing(stats.start_date, stats.end_date)
        all_plans = []
        all_plans.extend(stats.acute_daily_plans)
        all_plans.extend(stats.chronic_daily_plans)

        historical_internal_strain = training_volume_processing.get_historical_internal_strain(start_date, end_date, all_plans)
        athlete_stats.historical_internal_strain = historical_internal_strain
        training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                    stats.days_8_14_plans,
                                                    stats.acute_daily_plans,
                                                    stats.get_chronic_weeks_plans(),
                                                    stats.chronic_daily_plans)
        athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)

        training_volume_processing.update_allowable_loads(athlete_stats.internal_strain)

        training_volume_processing.get_training_recs(athlete_stats.internal_acwr, athlete_stats.internal_ramp)

        metrics_list = [athlete_stats.internal_acwr, athlete_stats.internal_strain, athlete_stats.internal_monotony,
                        athlete_stats.internal_ramp]

        filtered_metrics = list(m for m in metrics_list if not m.insufficient_data)

        training_status = training_volume_processing.get_training_status(filtered_metrics)

        new_athlete_stats = athlete_stats

        for d in range(1,8):
            # now let's do next day
            stats.increment_start_end_times(d)
            stats.set_acute_chronic_periods()
            stats.load_historical_plans()
            training_volume_processing = TrainingVolumeProcessing(stats.start_date, stats.end_date)

            training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                        stats.days_8_14_plans,
                                                        stats.acute_daily_plans,
                                                        stats.get_chronic_weeks_plans(),
                                                        stats.chronic_daily_plans)
            new_athlete_stats = training_volume_processing.calc_training_volume_metrics(new_athlete_stats)

            metrics_list = [new_athlete_stats.internal_acwr, new_athlete_stats.internal_strain, new_athlete_stats.internal_monotony,
                            new_athlete_stats.internal_ramp]

            filtered_metrics = list(m for m in metrics_list if not m.insufficient_data)

            new_training_status = training_volume_processing.get_training_status(filtered_metrics)

            if training_status.training_level.value != new_training_status.training_level.value:
                days = d
                break

        j = 0

    assert new_athlete_stats is not None
    '''

