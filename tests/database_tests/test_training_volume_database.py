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

def test_get_training_plan_from_database():

    okay_list = []
    okay_optimal_list = []
    risk_list = []
    rate_limiting_factor = []
    risk_rate_limitiing_factor = []
    okay_severity_list = []
    risk_severity_list = []

    users = []
    users.append('0dd21808-55f9-45f2-a408-b1713d40681f') #mw
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
        stats.load_historical_data()
        athlete_stats = AthleteStats(user_id)
        athlete_stats.historic_soreness = ath_stats.historic_soreness
        training_volume_processing = TrainingVolumeProcessing(stats.start_date, stats.end_date)
        athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats, stats.last_7_days_plans,
                                                                                stats.days_8_14_plans,
                                                                                stats.acute_daily_plans,
                                                                                stats.get_chronic_weeks_plans(),
                                                                                stats.chronic_daily_plans)

        all_plans = []
        all_plans.extend(stats.acute_daily_plans)
        all_plans.extend(stats.chronic_daily_plans)

        historical_internal_strain = training_volume_processing.get_historical_internal_strain(start_date, end_date, all_plans)

        daily_plans = []
        daily_plans.extend(list(x for x in TrainingVolumeProcessing(
                                    stats.start_date,
            stats.end_date).get_session_attributes_product_sum_tuple_list("session_RPE",
                                                                                                 "duration_minutes",
                                                                          stats.acute_daily_plans)
                                if x is not None))
        daily_plans.extend(list(x for x in TrainingVolumeProcessing(
            stats.start_date,
            stats.end_date).get_session_attributes_product_sum_tuple_list("session_RPE",
                                                                                                 "duration_minutes",
                                                                                                 stats.chronic_daily_plans)
                                if x is not None))


        report = training_volume_processing.get_training_report(user_id,
                                                                stats.acute_start_date_time,
                                                                stats.chronic_start_date_time,
                                                                daily_plans,historical_internal_strain,
                                                                stats.end_date_time)
        #report = training_volume_processing.calc_report_stats(stats.acute_daily_plans, stats.acute_start_date_time,
        #                                                      athlete_stats, stats.chronic_daily_plans, report)

        '''deprecated
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
        '''
        j = 0

    assert athlete_stats.acute_internal_total_load == 2590


def test_missing_session_data():
    user_id = "slacker"
    run_date = "2019-01-23"
    start_date = datetime.strptime(run_date, "%Y-%m-%d")
    end_date = datetime.strptime(run_date, "%Y-%m-%d")
    end_date_time = end_date + timedelta(days=1)

    acute_days = None
    chronic_days = None
    acute_start_date_time = None
    chronic_start_date_time = None

    results = {}
    load_values = {}

    load_values[0] = [50, None, 250, None, 600, None, None,
                                450, None, 185, None, 350, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[1] = [50, None, 250, None, 600, None, None,
                                450, None, None, None, 350, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[2] = [50, None, 250, None, 600, None, None,
                                450, None, None, None, 350, None, None,
                                250, None, None, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[3] = [50, None, 250, None, None, None, None,
                                450, None, None, None, 350, None, None,
                                250, None, None, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[4] = [50, None, 250, None, None, None, None,
                                450, None, None, None, 350, None, None,
                                250, None, None, None, 700, None, None,
                                650, None, None, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[5] = [50, None, 250, None, None, None, None,
                                450, None, None, None, 350, None, None,
                                250, None, None, None, 700, None, None,
                                650, None, None, None, None, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[6] = [50, None, 250, None, None, None, None,
                                450, None, None, None, 350, None, None,
                                250, None, None, None, 700, None, None,
                                650, None, None, None, None, None, None,
                                350, None, None, None, 400, None, None]

    load_values[7] = [50, None, 250, None, None, None, None,
                                450, None, None, None, 350, None, None,
                                None, None, None, None, 700, None, None,
                                650, None, None, None, None, None, None,
                                350, None, None, None, 400, None, None]

    load_values[8] = [50, None, 250, None, None, None, None,
                                450, None, None, None, 350, None, None,
                                None, None, None, None, None, None, None,
                                650, None, None, None, None, None, None,
                                350, None, None, None, 400, None, None]

    load_values[9] = [50, None, 250, None, None, None, None,
                                450, None, None, None, 350, None, None,
                                None, None, None, None, None, None, None,
                                650, None, None, None, None, None, None,
                                None, None, None, None, 400, None, None]

    load_values[10] = [50, None, None, None, None, None, None,
                                450, None, None, None, 350, None, None,
                                None, None, None, None, None, None, None,
                                650, None, None, None, None, None, None,
                                None, None, None, None, 400, None, None]

    load_values[11] = [50, None, None, None, None, None, None,
                       None, None, None, None, 350, None, None,
                       None, None, None, None, None, None, None,
                       650, None, None, None, None, None, None,
                       None, None, None, None, 400, None, None]

    load_values[12] = [50, None, None, None, None, None, None,
                       None, None, None, None, 350, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, 400, None, None]

    load_values[13] = [50, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, 400, None, None]

    load_values[14] = [None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, 400, None, None]

    for r in range(0, 15):

        daily_plans = []

        internal_load_values = load_values[r]

        dates = get_dates(parse_date(run_date) - timedelta(days=(len(internal_load_values))), parse_date(run_date))

        for v in range(0, len(internal_load_values)):
            if internal_load_values[v] is not None:
                daily_plans.append((dates[v], internal_load_values[v]))


        earliest_plan_date = daily_plans[0][0]
        latest_plan_date = daily_plans[len(daily_plans) - 1][0]

        days_difference = (end_date_time - earliest_plan_date).days + 1

        if 7 <= days_difference < 14:
            acute_days = 3
            chronic_days = int(days_difference)
        elif 14 <= days_difference <= 28:
            acute_days = 7
            chronic_days = int(days_difference)
        elif days_difference > 28:
            acute_days = 7
            chronic_days = 28

        adjustment_factor = 0
        if latest_plan_date is not None and parse_date(run_date) > latest_plan_date:
            adjustment_factor = (parse_date(run_date) - latest_plan_date).days

        if acute_days is not None and chronic_days is not None:
            acute_start_date_time = end_date_time - timedelta(days=acute_days + 1 + adjustment_factor)
            chronic_start_date_time = end_date_time - timedelta(
                days=chronic_days + 1 + acute_days + adjustment_factor)

        training_volume_processing = TrainingVolumeProcessing(start_date, end_date)

        historical_internal_strain = calc_historical_internal_strain(format_date(start_date), format_date(end_date), daily_plans)

        report = training_volume_processing.get_training_report(user_id,
                                                                acute_start_date_time,
                                                                chronic_start_date_time,
                                                                daily_plans,historical_internal_strain,
                                                                end_date_time)

        results[r] = (report.suggested_training_days[0].low_optimal_threshold,
                        report.suggested_training_days[0].low_overreaching_threshold,
                        report.suggested_training_days[0].low_excessive_threshold)

    assert report is not None


def test_progressive_missing_session_data():
    user_id = "slacker"
    run_date = "2019-01-23"
    start_date = datetime.strptime(run_date, "%Y-%m-%d")
    end_date = datetime.strptime(run_date, "%Y-%m-%d")
    end_date_time = end_date + timedelta(days=1)

    acute_days = None
    chronic_days = None
    acute_start_date_time = None
    chronic_start_date_time = None

    results = {}
    load_values = {}

    load_values[0] = [50, None, 250, None, 600, None, None,
                                450, None, 185, None, 350, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[1] = [None, None, 250, None, 600, None, None,
                                450, None, 185, None, 350, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[2] = [None, None, None, None, 600, None, None,
                                450, None, 185, None, 350, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[3] = [None, None, None, None, None, None, None,
                                450, None, 185, None, 350, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[4] = [None, None, None, None, None, None, None,
                                None, None, 185, None, 350, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[5] = [None, None, None, None, None, None, None,
                                None, None, None, None, 350, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]


    load_values[6] = [None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                250, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[7] = [None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, 450, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[8] = [None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, 700, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[9] = [None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                650, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[10] = [None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, 375, None, 200, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[11] = [None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, 200, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[12] = [None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                350, None, 250, None, 400, None, None]

    load_values[13] = [None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, None, None, None, None, None,
                                None, None, 250, None, 400, None, None]

    load_values[14] = [None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, None, None, None,
                       None, None, None, None, 400, None, None]

    for r in range(0, 15):

        daily_plans = []

        internal_load_values = load_values[r]

        dates = get_dates(parse_date(run_date) - timedelta(days=(len(internal_load_values))), parse_date(run_date))

        for v in range(0, len(internal_load_values)):
            if internal_load_values[v] is not None:
                daily_plans.append((dates[v], internal_load_values[v]))


        earliest_plan_date = daily_plans[0][0]
        latest_plan_date = daily_plans[len(daily_plans) - 1][0]

        days_difference = (end_date_time - earliest_plan_date).days + 1

        if 7 <= days_difference < 14:
            acute_days = 3
            chronic_days = int(days_difference)
        elif 14 <= days_difference <= 28:
            acute_days = 7
            chronic_days = int(days_difference)
        elif days_difference > 28:
            acute_days = 7
            chronic_days = 28

        adjustment_factor = 0
        if latest_plan_date is not None and parse_date(run_date) > latest_plan_date:
            adjustment_factor = (parse_date(run_date) - latest_plan_date).days

        if acute_days is not None and chronic_days is not None:
            acute_start_date_time = end_date_time - timedelta(days=acute_days + 1 + adjustment_factor)
            chronic_start_date_time = end_date_time - timedelta(
                days=chronic_days + 1 + acute_days + adjustment_factor)

        training_volume_processing = TrainingVolumeProcessing(start_date, end_date)

        historical_internal_strain = calc_historical_internal_strain(format_date(start_date), format_date(end_date), daily_plans)

        report = training_volume_processing.get_training_report(user_id,
                                                                acute_start_date_time,
                                                                chronic_start_date_time,
                                                                daily_plans,historical_internal_strain,
                                                                end_date_time)

        results[r] = (report.suggested_training_days[0].low_optimal_threshold,
                        report.suggested_training_days[0].low_overreaching_threshold,
                        report.suggested_training_days[0].low_excessive_threshold)

    assert report is not None