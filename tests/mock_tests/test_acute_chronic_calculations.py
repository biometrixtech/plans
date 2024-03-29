# from aws_xray_sdk.core import xray_recorder
# xray_recorder.configure(sampling=False)
# xray_recorder.begin_segment(name="test")
from datetime import datetime, timedelta
from models.daily_plan import DailyPlan
from models.session import SportTrainingSession
from models.daily_readiness import DailyReadiness
from models.stats import AthleteStats
from models.load_stats import LoadStats
from logic.stats_processing import StatsProcessing
from tests.testing_utilities import TestUtilities
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection
from logic.training_volume_processing import TrainingVolumeProcessing
from utils import parse_date, format_date

def get_dates(start_date, end_date):

    dates = []

    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates

def get_daily_plans(start_date, end_date):

    plans = []

    dates = get_dates(start_date, end_date)

    i = 1

    for d in dates:
        daily_plan = DailyPlan(event_date=d.strftime("%Y-%m-%d"))
        session = SportTrainingSession()
        session.event_date = d
        session.duration_minutes = i
        session.session_RPE = 10 * i
        #session.high_intensity_load = 2 * i
        #session.mod_intensity_load = 5 * i
        #session.low_intensity_load = 3 * i
        daily_plan.training_sessions.append(session)
        plans.append(daily_plan)
        i += 1

    return plans

def get_daily_internal_plans(start_date, end_date):

    plans = []

    dates = get_dates(start_date, end_date)

    i = 1

    for d in dates:
        daily_plan = DailyPlan(event_date=d.strftime("%Y-%m-%d"))
        session = SportTrainingSession()
        session.event_date = d
        session.session_RPE = 5
        session.duration_minutes = 60
        daily_plan.training_sessions.append(session)
        plans.append(daily_plan)
        i += 1

    return plans

def get_sessionless_daily_plans(start_date, end_date):

    plans = []

    dates = get_dates(start_date, end_date)

    for d in dates:
        daily_plan = DailyPlan(event_date=d.strftime("%Y-%m-%d"))
        plans.append(daily_plan)

    return plans

def get_daily_readiness_surveys(start_date, end_date):

    surveys = []

    dates = get_dates(start_date, end_date)

    for d in dates:
        soreness = TestUtilities().body_part_soreness(9, 1)
        daily_readiness = DailyReadiness(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", [soreness], 4, 5)
        surveys.append(daily_readiness)

    return surveys


def test_acute_correct_dates_7_days():
    plans = get_daily_plans(datetime(2018, 6, 23, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 23, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-02' == stats.acute_daily_plans[2].event_date
    assert '2018-06-30' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_8_days():
    plans = get_daily_plans(datetime(2018, 6, 22, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 22, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-02' == stats.acute_daily_plans[2].event_date
    assert '2018-06-30' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_9_days():
    plans = get_daily_plans(datetime(2018, 6, 24, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 24, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-02' == stats.acute_daily_plans[2].event_date
    assert '2018-06-30' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_10_days():
    plans = get_daily_plans(datetime(2018, 6, 23, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 23, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-02' == stats.acute_daily_plans[2].event_date
    assert '2018-06-30' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_14_days():
    plans = get_daily_plans(datetime(2018, 6, 16, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 16, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-02' == stats.acute_daily_plans[2].event_date
    assert '2018-06-30' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_28_days():
    plans = get_daily_plans(datetime(2018, 6, 6, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 6, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert 7 == len(stats.acute_daily_plans)
    assert '2018-07-02' == stats.acute_daily_plans[6].event_date
    assert '2018-06-26' == stats.acute_daily_plans[0].event_date


def test_chronic_correct_dates_7_days():
    plans = get_daily_plans(datetime(2018, 6, 26, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 26, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert 4 == len(weeks[0])
    assert '2018-06-29' == weeks[0][3].event_date
    assert '2018-06-26' == weeks[0][0].event_date


def test_chronic_correct_dates_28_days():
    plans = get_daily_plans(datetime(2018, 6, 6, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 6, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert weeks[0][6].event_date == '2018-06-25'
    assert weeks[0][0].event_date == '2018-06-19'
    assert weeks[1][6].event_date == '2018-06-18'
    assert weeks[1][0].event_date == '2018-06-12'
    assert weeks[2][5].event_date == '2018-06-11'
    assert weeks[2][0].event_date == '2018-06-06'
    assert 0 == len(weeks[3])


def test_chronic_correct_dates_33_days():
    plans = get_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert weeks[0][6].event_date == '2018-06-25'
    assert weeks[0][0].event_date == '2018-06-19'
    assert weeks[1][6].event_date == '2018-06-18'
    assert weeks[1][0].event_date == '2018-06-12'
    assert weeks[2][6].event_date == '2018-06-11'
    assert weeks[2][0].event_date == '2018-06-05'
    assert weeks[3][3].event_date == '2018-06-04'
    assert weeks[3][0].event_date == '2018-06-01'


def test_chronic_correct_dates_40_days():
    plans = get_daily_plans(datetime(2018, 5, 25, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 5, 25, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    weeks = stats.get_chronic_weeks_plans()
    assert weeks[0][6].event_date == '2018-06-25'
    assert weeks[0][0].event_date == '2018-06-19'
    assert weeks[1][6].event_date == '2018-06-18'
    assert weeks[1][0].event_date == '2018-06-12'
    assert weeks[2][6].event_date == '2018-06-11'
    assert weeks[2][0].event_date == '2018-06-05'
    assert weeks[3][6].event_date == '2018-06-04'
    assert weeks[3][0].event_date == '2018-05-29'


def test_correct_acute_chronic_load_33_days():
    plans = get_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    athlete_stats = AthleteStats("Tester")
    athlete_stats.load_stats = LoadStats()
    training_volume_processing = TrainingVolumeProcessing(stats.start_date, format_date(stats.event_date),
                                                athlete_stats.load_stats)
    training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                stats.days_8_14_plans,
                                                stats.acute_daily_plans,
                                                stats.get_chronic_weeks_plans(),
                                                stats.chronic_daily_plans)
    athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)
    assert 59150 == athlete_stats.acute_internal_total_load.observed_value
    assert 55250 == athlete_stats.chronic_internal_total_load.observed_value

def test_correct_acute_chronic_empty_load_33_days():
    plans = get_sessionless_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    athlete_stats = AthleteStats("Tester")
    athlete_stats.load_stats = LoadStats()
    training_volume_processing = TrainingVolumeProcessing(stats.start_date, format_date(stats.event_date),
                                                athlete_stats.load_stats)
    training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                stats.days_8_14_plans,
                                                stats.acute_daily_plans,
                                                stats.get_chronic_weeks_plans(),
                                                stats.chronic_daily_plans)
    athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)
    assert None is athlete_stats.acute_internal_total_load.observed_value
    assert None is athlete_stats.chronic_internal_total_load.observed_value


def test_correct_acwr_load_33_days():
    plans = get_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    athlete_stats = AthleteStats("Tester")
    athlete_stats.load_stats = LoadStats()
    training_volume_processing = TrainingVolumeProcessing(stats.start_date, format_date(stats.event_date),
                                                athlete_stats.load_stats)
    training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                stats.days_8_14_plans,
                                                stats.acute_daily_plans,
                                                stats.get_chronic_weeks_plans(),
                                                stats.chronic_daily_plans)
    athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)
    assert 1.0705882352941176 == athlete_stats.internal_acwr.observed_value


def test_correct_acwr_empty_load_33_days():
    plans = get_sessionless_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    athlete_stats = AthleteStats("Tester")
    athlete_stats.load_stats = LoadStats()
    training_volume_processing = TrainingVolumeProcessing(stats.start_date, stats.end_date,
                                                athlete_stats.load_stats)
    training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                stats.days_8_14_plans,
                                                stats.acute_daily_plans,
                                                stats.get_chronic_weeks_plans(),
                                                stats.chronic_daily_plans)
    athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)
    assert None is athlete_stats.internal_acwr.observed_value

def test_correct_internal_acwr_load_33_days():
    plans = get_daily_internal_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 2, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    athlete_stats = AthleteStats("Tester")
    athlete_stats.load_stats = LoadStats()
    training_volume_processing = TrainingVolumeProcessing(stats.start_date, format_date(stats.event_date),
                                                athlete_stats.load_stats)
    training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                stats.days_8_14_plans,
                                                stats.acute_daily_plans,
                                                stats.get_chronic_weeks_plans(),
                                                stats.chronic_daily_plans)
    athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)
    assert 0.28 == athlete_stats.internal_acwr.observed_value


def test_correct_internal_acwr_empty_load_33_days():
    plans = get_sessionless_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats = StatsProcessing("Tester", parse_date("2018-07-03"), datastore_collection)
    stats.set_start_end_times()
    stats.all_plans = plans
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    athlete_stats = AthleteStats("Tester")
    athlete_stats.load_stats = LoadStats()
    training_volume_processing = TrainingVolumeProcessing(stats.start_date, stats.end_date,
                                                athlete_stats.load_stats)
    training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                stats.days_8_14_plans,
                                                stats.acute_daily_plans,
                                                stats.get_chronic_weeks_plans(),
                                                stats.chronic_daily_plans)
    athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)
    assert None is athlete_stats.internal_acwr.observed_value