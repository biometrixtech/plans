import pytest
import datetime
import logic.training_plan_management as tpm
from tests.mocks.mock_daily_plan_datastore import DailyPlanDatastore
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from tests.mocks.mock_post_session_survey_datastore import PostSessionSurveyDatastore
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from tests.testing_utilities import TestUtilities
from models.post_session_survey import PostSessionSurvey


def training_plan_manager():
    mgr = tpm.TrainingPlanManager("test", ExerciseLibraryDatastore(), DailyReadinessDatastore(),
                                  PostSessionSurveyDatastore(), DailyPlanDatastore(), AthleteStatsDatastore())
    return mgr


def test_no_surveys_available_with_date():

    mgr = training_plan_manager()
    surveys_today = mgr.post_session_surveys_today([], "2018-07-01")

    assert False is surveys_today


def test_one_survey_available_with_date():
    user_id = "tester"

    mgr = training_plan_manager()

    soreness_list = [TestUtilities().body_part_soreness(12, 1)]

    post_survey = TestUtilities().get_post_survey(4, soreness_list)
    post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 12, 17, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          1, post_survey)

    surveys_today = mgr.post_session_surveys_today([post_session_survey], "2018-07-12")

    assert True is surveys_today

def test_no_surveys_available_wrong_date_format():

    mgr = training_plan_manager()
    surveys_today = mgr.post_session_surveys_today([], datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

    assert False is surveys_today


def test_one_survey_available_wrong_date_format():
    user_id = "tester"

    mgr = training_plan_manager()

    soreness_list = [TestUtilities().body_part_soreness(12, 1)]

    post_survey = TestUtilities().get_post_survey(4, soreness_list)
    post_session_survey = \
        PostSessionSurvey(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          1, post_survey)

    surveys_today = mgr.post_session_surveys_today([post_session_survey], datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ"))

    assert True is surveys_today




'''
def test_get_start_time_from_morning_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 27, 0, 0, 0) == start_time


def test_get_end_time_from_morning_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 27, 12, 0, 0) == end_time


def test_get_start_time_from_afternoon_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 27, 12, 0, 0) == start_time


def test_get_end_time_from_afternoon_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == end_time


def test_get_start_time_from_evening_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 27, 12, 0, 0) == start_time


def test_get_end_time_from_evening_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == end_time


def test_get_start_time_from_morning_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 27, 12, 0, 0) == start_time


def test_get_end_time_from_morning_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == end_time


def test_get_start_time_from_afternoon_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == start_time


def test_get_end_time_from_afternoon_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == end_time


def test_get_start_time_from_evening_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == start_time


def test_get_end_time_from_evening_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == end_time


def test_get_start_time_from_morning_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == start_time


def test_get_end_time_from_morning_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == end_time


def test_get_start_time_from_afternoon_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == start_time


def test_get_end_time_from_afternoon_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == end_time


def test_get_start_time_from_evening_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == start_time


def test_get_end_time_from_evening_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == end_time


def test_get_start_time_from_morning_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == start_time


def test_get_end_time_from_morning_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == end_time


def test_get_start_time_from_afternoon_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == start_time


def test_get_end_time_from_afternoon_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 12, 0, 0) == end_time


def test_get_start_time_from_evening_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == start_time


def test_get_end_time_from_evening_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = training_plan_manager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 12, 0, 0) == end_time


Business related tests

# am tests

def get_recovery_for_no_injury_no_soreness():   # everyone should get some recovery, should be general in nature

def get_recovery_for_no_injury_1_day_soreness():

def get_recovery_for_no_injury_2_day_soreness():

def get_recovery_for_no_injury_3_day_soreness():

# pm tests

def get_recovery_for_no_injury_no_soreness():

def get_recovery_for_no_injury_1_day_soreness():

def get_recovery_for_no_injury_2_day_soreness():

def get_recovery_for_no_injury_3_day_soreness():


# get am, pm

def get_recovery_for_no_injury_no_soreness():

def get_recovery_for_no_injury_1_day_soreness():

def get_recovery_for_no_injury_2_day_soreness():

def get_recovery_for_no_injury_3_day_soreness():


# consecutive soreness
# am tests

def get_recovery_for_no_injury_2_day_consecutive_soreness():

def get_recovery_for_no_injury_3_day_consecutive_soreness():

# pm tests

def get_recovery_for_no_injury_2_day_consecutive_soreness():

def get_recovery_for_no_injury_3_day_consecutive_soreness():

# get am, pm

def get_recovery_for_no_injury_2_day_consecutive_soreness():

def get_recovery_for_no_injury_3_day_consecutive_soreness():

# more than 1 soreness, severity ranking

# am tests

def get_recovery_for_no_injury_2_day_multi_staggered_soreness():


def get_recovery_for_no_injury_3_day_multi_staggered_soreness():

def get_recovery_for_no_injury_4_day_multi_staggered_soreness():


# pm tests


def get_recovery_for_no_injury_2_day_multi_staggered_soreness():


def get_recovery_for_no_injury_3_day_multi_staggered_soreness():

def get_recovery_for_no_injury_4_day_multi_staggered_soreness():

# get am, pm


def get_recovery_for_no_injury_2_day_multi_staggered_soreness():


def get_recovery_for_no_injury_3_day_multi_staggered_soreness():

def get_recovery_for_no_injury_4_day_multi_staggered_soreness():


# consecutive soreness, more than 1 soreness, severity ranking
# am tests

def get_recovery_for_no_injury_2_day_consecutive_multi_staggered_soreness():


def get_recovery_for_no_injury_3_day_consecutive_multi_staggered_soreness():

def get_recovery_for_no_injury_4_day_consecutive_multi_staggered_soreness():

# pm tests

def get_recovery_for_no_injury_2_day_consecutive_multi_staggered_soreness():


def get_recovery_for_no_injury_3_day_consecutive_multi_staggered_soreness():

def get_recovery_for_no_injury_4_day_consecutive_multi_staggered_soreness():


# get am, pm

def get_recovery_for_no_injury_2_day_consecutive_multi_staggered_soreness():


def get_recovery_for_no_injury_3_day_consecutive_multi_staggered_soreness():

def get_recovery_for_no_injury_4_day_consecutive_multi_staggered_soreness():

'''