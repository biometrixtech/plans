from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from fathomapi.api.config import Config
Config.set('FILENAMES', {'exercise_library': 'exercise_library_fathom.json',
                           'body_part_mapping': 'body_part_mapping_fathom.json'})


from models.daily_plan import DailyPlan
from models.session import SportTrainingSession, SessionType
from models.post_session_survey import PostSurvey, PostSessionSurvey
from models.daily_readiness import DailyReadiness
from models.stats import AthleteStats
from datetime import datetime, timedelta
from tests.testing_utilities import TestUtilities
from models.training_volume import StandardErrorRange
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from logic.stats_processing import StatsProcessing
from models.load_stats import LoadStats
from logic.training_volume_processing import TrainingVolumeProcessing
from utils import parse_date, format_date

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
        session = SportTrainingSession()
        session.event_date = dates[d]
        post_survey = TestUtilities().get_post_survey(rpe_list[d], [])
        post_session = PostSurvey(survey=post_survey, event_date=dates[d].strftime("%Y-%m-%dT%H:%M:%SZ"))
        session.post_session_survey = post_session
        session.duration_minutes = time_list[d]
        daily_plan.training_sessions.append(session)
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


def test_duration_minutes_load():

    load_stats = LoadStats()
    load_stats.min_duration_minutes = 0
    load_stats.max_duration_minutes = 100

    load = load_stats.get_duration_minutes_load(50)

    assert load == 50.0


def test_duration_minutes_load_min_max_none():

    load_stats = LoadStats()
    load_stats.min_duration_minutes = None
    load_stats.max_duration_minutes = None

    load = load_stats.get_duration_minutes_load(50)

    assert load == 50.0


def test_duration_minutes_load_min_max_high():

    load_stats = LoadStats()
    load_stats.min_duration_minutes = None
    load_stats.max_duration_minutes = None

    load = load_stats.get_duration_minutes_load(500)

    assert load == 100.00

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

def test_strain_events():

    athlete_stats = AthleteStats("tester")
    strain_list = []

    seed = [1000, 300, 1450, 250, 1700, 600, 1400, 800, 2000]
    seed_date = parse_date("2018-01-01")
    for s in range(0, 9):

        strain_list.append((seed_date, seed[s]))
        seed_date = seed_date + timedelta(days=1)

    tvp = TrainingVolumeProcessing("2018-01-01", "2018-01-09", athlete_stats.load_stats)
    tvp.internal_load_tuples = strain_list
    strain, strain_events = tvp.get_historical_internal_strain("2018-01-01", "2018-01-09", None)

    assert 0 < strain_events.observed_value

