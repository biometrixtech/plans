from datetime import datetime, timedelta
from models.daily_plan import DailyPlan
from models.session import PracticeSession
from models.daily_readiness import DailyReadiness
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

    for d in dates:
        daily_plan = DailyPlan(event_date=d.strftime("%Y-%m-%dT%H:%M:%SZ"))
        practice_session = PracticeSession()
        practice_session.event_date = d
        practice_session.external_load = 100
        practice_session.high_intensity_load = 20
        practice_session.mod_intensity_load = 50
        practice_session.low_intensity_load = 30
        daily_plan.practice_sessions.append(practice_session)
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
    pass

def test_acute_correct_dates_10_days():
    pass

def test_acute_correct_dates_14_days():
    pass

def test_acute_correct_dates_20_days():
    pass

def test_acute_correct_dates_21_days():
    pass

def test_acute_correct_dates_25_days():
    pass

def test_acute_correct_dates_28_days():
    pass

def test_acute_correct_dates_33_days():
    pass

def test_chronic_correct_dates_7_days():
    pass

def test_chronic_correct_dates_10_days():
    pass

def test_chronic_correct_dates_14_days():
    pass

def test_chronic_correct_dates_20_days():
    pass

def test_chronic_correct_dates_21_days():
    pass

def test_chronic_correct_dates_25_days():
    pass

def test_chronic_correct_dates_28_days():
    pass

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




