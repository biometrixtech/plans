from models.daily_plan import DailyPlan
from models.session import PracticeSession, SessionType
from models.post_session_survey import PostSurvey, PostSessionSurvey
from models.daily_readiness import DailyReadiness
from models.stats import AthleteStats
from datetime import datetime, timedelta
from tests.testing_utilities import TestUtilities
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from logic.stats_processing import StatsProcessing
from logic.training_volume_processing import TrainingVolumeProcessing


def get_dates(start_date, days):

    dates = []

    for i in range(days + 1):
        dates.append(start_date + timedelta(days=i))

    return dates


def get_daily_plans(start_date, rpe_list, time_list):

    plans = []

    dates = get_dates(start_date, len(rpe_list) - 1)

    for d in range(0, len(dates)):
        daily_plan = DailyPlan(event_date=dates[d].strftime("%Y-%m-%d"))
        practice_session = PracticeSession()
        practice_session.event_date = dates[d]
        post_survey = TestUtilities().get_post_survey(rpe_list[d], [])
        post_session = PostSurvey(survey=post_survey, event_date=dates[d].strftime("%Y-%m-%dT%H:%M:%SZ"))
        practice_session.post_session_survey = post_session
        practice_session.duration_minutes = time_list[d]
        daily_plan.training_sessions.append(practice_session)
        plans.append(daily_plan)

    return plans

def get_daily_readiness_surveys(start_date, days):

    surveys = []

    dates = get_dates(start_date, days)

    for d in dates:
        soreness = TestUtilities().body_part_soreness(9, 1)
        daily_readiness = DailyReadiness(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", [soreness], 4, 5)
        surveys.append(daily_readiness)

    return surveys

def get_post_session_surveys(start_date, rpe_list):

    surveys = []

    dates = get_dates(start_date, len(rpe_list) - 1)

    for d in range(0, len(dates)):
        soreness_list = []

        post_survey = TestUtilities().get_post_survey(rpe_list[d], soreness_list)

        post_session = PostSessionSurvey(dates[d].strftime("%Y-%m-%dT%H:%M:%SZ"), "tester",None, SessionType.practice, post_survey )
        surveys.append(post_session)

    return surveys


'''
Liz Data
1-14-19 - 30, 3
1-14-19 - 120, 3
1-5-19 - 150, 3
1-4-19 - 135, 3
1-4-19 - 45, 3
1-3-19 - 150, 4
1-2-19 - 160, 5
1-2-19 - 30, 5
12-31-18 - 30, 4
12-30-18 - 60, 1
12-29-19 - 60, 2
12-28-18 - 120, 3
12-27-18 - 110, 4
12-26-18 - 170, 6
12-24-18 - 120, 3
12-21-18 - 120, 2
12-20-18 - 120, 5
12-19-18 - 120, 4
12-18-18 - 85, 3
12-17-18 - 90, 1
12-16-18 - 120, 3
12-15-18 - NONE
'''

def test_strain_works():

    rpe_list = [4, 6, 8, 4, 7, 4, 3, 3, 5, 6, 5, 5, 4, 3, 7, 4, 6, 4, 7, 4, 4, 3, 3, 4, 5, 6, 8, 4, 8, 4, 5, 7, 5, 4, 8]
    min_list = [40, 60, 80, 40, 70, 40, 30, 30, 50, 60, 50, 50, 40, 30, 70, 40, 60, 40, 70, 40, 40, 30, 30, 40, 50, 60, 80, 40, 80, 40, 50, 70, 50, 40, 80]

    plans_28_days = get_daily_plans(datetime(2018, 7, 10, 0, 0, 0), rpe_list, min_list)
    surveys = get_daily_readiness_surveys(datetime(2018, 7, 10, 12, 0, 0), len(rpe_list) - 1)
    ps_surveys = get_post_session_surveys(datetime(2018, 7, 10, 12, 0, 0), rpe_list)
    daily_plan_datastore = DailyPlanDatastore()
    daily_plan_datastore.side_load_plans(plans_28_days)
    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(surveys)
    post_session_datastore = PostSessionSurveyDatastore()
    post_session_datastore.side_load_surveys(ps_surveys)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_plan_datastore = daily_plan_datastore
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore
    datastore_collection.post_session_survey_datastore = post_session_datastore

    stats = StatsProcessing("tester", "2018-08-13", datastore_collection)
    stats.set_start_end_times()
    stats.set_acute_chronic_periods()
    stats.all_plans = plans_28_days
    stats.update_start_times(surveys, [], stats.all_plans)
    stats.set_acute_chronic_periods()
    #stats.load_historical_readiness_surveys(surveys)
    #stats.load_historical_post_session_surveys([])
    stats.load_historical_plans()
    athlete_stats = AthleteStats("Tester")
    training_volume_processing = TrainingVolumeProcessing(stats.start_date, stats.end_date)
    training_volume_processing.load_plan_values(stats.last_7_days_plans,
                                                stats.days_8_14_plans,
                                                stats.acute_daily_plans,
                                                stats.get_chronic_weeks_plans(),
                                                stats.chronic_daily_plans)
    athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)
    '''deprecated
    daily_plans = []
    daily_plans.extend(list(x for x in
                            training_volume_processing.get_session_attributes_product_sum_tuple_list("session_RPE",
                                                                                                     "duration_minutes",
                                                                                                     stats.acute_daily_plans)
                            if x is not None))
    daily_plans.extend(list(x for x in
                            training_volume_processing.get_session_attributes_product_sum_tuple_list("session_RPE",
                                                                                                     "duration_minutes",
                                                                                                     stats.chronic_daily_plans)
                            if x is not None))

    all_plans = []
    all_plans.extend(stats.acute_daily_plans)
    all_plans.extend(stats.chronic_daily_plans)

    historical_internal_strain = training_volume_processing.get_historical_internal_strain("2018-07-10", "2018-08-06",
                                                                                           all_plans)


    report = training_volume_processing.get_training_report(athlete_stats.athlete_id,
                                                            stats.acute_start_date_time,
                                                            stats.chronic_start_date_time,
                                                            daily_plans,
                                                            historical_internal_strain,
                                                            stats.end_date_time)
    '''
    assert len(athlete_stats.historical_internal_strain) == 29
