from datetime import datetime, timedelta
from models.daily_plan import DailyPlan
from models.session import PracticeSession
from models.daily_readiness import DailyReadiness
from models.stats import AthleteStats
from stats_processing import StatsProcessing
from tests.testing_utilities import TestUtilities
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore

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
        daily_plan = DailyPlan(event_date=d.strftime("%Y-%m-%dT%H:%M:%SZ"))
        practice_session = PracticeSession()
        practice_session.event_date = d
        practice_session.external_load = 10 * i
        practice_session.high_intensity_load = 2 * i
        practice_session.mod_intensity_load = 5 * i
        practice_session.low_intensity_load = 3 * i
        daily_plan.practice_sessions.append(practice_session)
        plans.append(daily_plan)
        i += 1

    return plans

def get_sessionless_daily_plans(start_date, end_date):

    plans = []

    dates = get_dates(start_date, end_date)

    for d in dates:
        daily_plan = DailyPlan(event_date=d.strftime("%Y-%m-%dT%H:%M:%SZ"))
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
    plans = get_daily_plans(datetime(2018, 6, 26, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 26, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                            daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-03T12:00:00Z' == stats.acute_daily_plans[2].event_date
    assert '2018-07-01T12:00:00Z' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_8_days():
    plans = get_daily_plans(datetime(2018, 6, 25, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 25, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-03T12:00:00Z' == stats.acute_daily_plans[2].event_date
    assert '2018-07-01T12:00:00Z' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_9_days():
    plans = get_daily_plans(datetime(2018, 6, 24, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 24, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-03T12:00:00Z' == stats.acute_daily_plans[2].event_date
    assert '2018-07-01T12:00:00Z' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_10_days():
    plans = get_daily_plans(datetime(2018, 6, 23, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 23, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert 3 == len(stats.acute_daily_plans)
    assert '2018-07-03T12:00:00Z' == stats.acute_daily_plans[2].event_date
    assert '2018-07-01T12:00:00Z' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_14_days():
    plans = get_daily_plans(datetime(2018, 6, 19, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 19, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert 7 == len(stats.acute_daily_plans)
    assert '2018-07-03T12:00:00Z' == stats.acute_daily_plans[6].event_date
    assert '2018-06-27T12:00:00Z' == stats.acute_daily_plans[0].event_date


def test_acute_correct_dates_28_days():
    plans = get_daily_plans(datetime(2018, 6, 6, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 6, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert 7 == len(stats.acute_daily_plans)
    assert '2018-07-03T12:00:00Z' == stats.acute_daily_plans[6].event_date
    assert '2018-06-27T12:00:00Z' == stats.acute_daily_plans[0].event_date


def test_chronic_correct_dates_7_days():
    plans = get_daily_plans(datetime(2018, 6, 26, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 26, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert 5 == len(weeks[0])
    assert '2018-06-30T12:00:00Z' == weeks[0][4].event_date
    assert '2018-06-26T12:00:00Z' == weeks[0][0].event_date


def test_chronic_correct_dates_28_days():
    plans = get_daily_plans(datetime(2018, 6, 6, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 6, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert weeks[0][6].event_date == '2018-06-26T12:00:00Z'
    assert weeks[0][0].event_date == '2018-06-20T12:00:00Z'
    assert weeks[1][6].event_date == '2018-06-19T12:00:00Z'
    assert weeks[1][0].event_date == '2018-06-13T12:00:00Z'
    assert weeks[2][6].event_date == '2018-06-12T12:00:00Z'
    assert weeks[2][0].event_date == '2018-06-06T12:00:00Z'
    assert 0 == len(weeks[3])


def test_chronic_correct_dates_33_days():
    plans = get_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert weeks[0][6].event_date == '2018-06-26T12:00:00Z'
    assert weeks[0][0].event_date == '2018-06-20T12:00:00Z'
    assert weeks[1][6].event_date == '2018-06-19T12:00:00Z'
    assert weeks[1][0].event_date == '2018-06-13T12:00:00Z'
    assert weeks[2][6].event_date == '2018-06-12T12:00:00Z'
    assert weeks[2][0].event_date == '2018-06-06T12:00:00Z'
    assert weeks[3][4].event_date == '2018-06-05T12:00:00Z'
    assert weeks[3][0].event_date == '2018-06-01T12:00:00Z'


def test_chronic_correct_dates_40_days():
    plans = get_daily_plans(datetime(2018, 5, 25, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 5, 25, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    weeks = stats.get_chronic_weeks_plans()
    assert weeks[0][6].event_date == '2018-06-26T12:00:00Z'
    assert weeks[0][0].event_date == '2018-06-20T12:00:00Z'
    assert weeks[1][6].event_date == '2018-06-19T12:00:00Z'
    assert weeks[1][0].event_date == '2018-06-13T12:00:00Z'
    assert weeks[2][6].event_date == '2018-06-12T12:00:00Z'
    assert weeks[2][0].event_date == '2018-06-06T12:00:00Z'
    assert weeks[3][6].event_date == '2018-06-05T12:00:00Z'
    assert weeks[3][0].event_date == '2018-05-30T12:00:00Z'


def test_correct_acute_chronic_load_33_days():
    plans = get_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    athlete_stats = AthleteStats("Tester")
    athlete_stats = stats.calc_training_volume_metrics(athlete_stats)
    assert 2100 == athlete_stats.acute_external_total_load
    assert 982.5 == athlete_stats.chronic_external_total_load

def test_correct_acute_chronic_empty_load_33_days():
    plans = get_sessionless_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    athlete_stats = AthleteStats("Tester")
    athlete_stats = stats.calc_training_volume_metrics(athlete_stats)
    assert None is athlete_stats.acute_external_total_load
    assert None is athlete_stats.chronic_external_total_load


def test_correct_acwr_load_33_days():
    plans = get_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    athlete_stats = AthleteStats("Tester")
    athlete_stats = stats.calc_training_volume_metrics(athlete_stats)
    assert 2100 / 982.5 == athlete_stats.acute_to_chronic_external_ratio()


def test_correct_acwr_empty_load_33_days():
    plans = get_sessionless_daily_plans(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    surveys = get_daily_readiness_surveys(datetime(2018, 6, 1, 12, 0, 0), datetime(2018, 7, 3, 12, 0, 0))
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)

    stats = StatsProcessing("Tester", "2018-07-03", daily_readiness_datastore, PostSessionSurveyDatastore(),
                 daily_plan_datastore, AthleteStatsDatastore())
    stats.set_start_end_times()
    stats.load_acute_chronic_data()
    athlete_stats = AthleteStats("Tester")
    athlete_stats = stats.calc_training_volume_metrics(athlete_stats)
    assert None is athlete_stats.acute_to_chronic_external_ratio()
