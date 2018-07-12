import pytest
import logic.training as training
import datetime
import logic.training_plan_management as training_plan_management
import logic.athlete_data_access as athlete_data_access
import athlete_data_access_mocks
import datastores.exercise_datastore as exercise_datastore
from datastores.daily_plan_datastore import DailyPlanDatastore

'''

get a training plan for the week


get a partial week training plan (starting mid-week)
each day should have an am/pm recovery session and any scheduled sessions
be able to get day youre on and next day
yesteday too
see whats completed/not completed
order: AM, PM at end, order to schedule sessions that user can change


'''
@pytest.fixture(scope="module")
def athlete_morning_dao():
    dao = athlete_data_access_mocks.AthleteDataAccessMorning()
    return dao

@pytest.fixture(scope="module")
def athlete_afternoon_dao():
    dao = athlete_data_access_mocks.AthleteDataAccessAfternoon()
    return dao

@pytest.fixture(scope="module")
def get_morning_midnight():
    start_time = datetime.datetime(2018, 6, 27, 0, 0, 0)
    return start_time

@pytest.fixture(scope="module")
def get_evening_midnight():
    start_time = datetime.datetime(2018, 6, 28, 0, 0, 0)
    return start_time

@pytest.fixture(scope="module")
def get_noon():
    start_time = datetime.datetime(2018, 6, 27, 12, 0, 0)
    return start_time

@pytest.fixture(scope="module")
def get_morning_time():
    start_time = datetime.datetime(2018, 6, 27, 11, 0, 0)
    return start_time


@pytest.fixture(scope="module")
def get_afternoon_time():
    start_time = datetime.datetime(2018, 6, 27, 15, 0, 0)
    return start_time


@pytest.fixture(scope="module")
def blank_plan(athlete_id, athlete_data_access_object):
    mgr = training_plan_management.TrainingPlanManager(athlete_id, athlete_data_access_object)
    daily_plan = mgr.create_daily_plan()
    return daily_plan


def test_daily_plan_am_recovery_has_am_start():
    athlete_id = "1"
    assert blank_plan(athlete_id, athlete_morning_dao()).recovery_am.start_time == get_morning_midnight()


def test_daily_plan_am_recovery_has_am_end():
    athlete_id = "1"
    assert blank_plan(athlete_id, athlete_morning_dao()).recovery_am.end_time == get_noon()


def test_daily_plan_am_recovery_has_pm_start():
    athlete_id = "1"
    assert blank_plan(athlete_id, athlete_morning_dao()).recovery_pm.start_time == get_noon()


def test_daily_plan_am_recovery_has_pm_end():
    athlete_id = "1"
    assert blank_plan(athlete_id, athlete_morning_dao()).recovery_pm.end_time == get_evening_midnight()


def test_daily_plan_pm_recovery_has_no_am_start():
    athlete_id = "1"
    assert blank_plan(athlete_id, athlete_afternoon_dao()).recovery_am is None


def test_daily_plan_pm_recovery_pm_start():
    athlete_id = "1"
    assert blank_plan(athlete_id, athlete_afternoon_dao()).recovery_pm.start_time == get_noon()


def test_daily_plan_has_pm_recovery_pm_end():
    athlete_id = "1"
    assert blank_plan(athlete_id, athlete_afternoon_dao()).recovery_pm.end_time == get_evening_midnight()


def test_daily_plan_am_recovery_has_practice_session():
    athlete_id = "1"
    athlete_dao = athlete_data_access_mocks.AthleteDataAccessMorningPractice()
    assert len(blank_plan(athlete_id, athlete_dao).practice_sessions) == 1


def test_create_plan():
    manager = \
        training_plan_management.TrainingPlanManager("test_user",
                                                     athlete_data_access_mocks.AthleteDataAccessMorningPractice("test_user"),
                                                     exercise_datastore)
    daily_plan = manager.create_daily_plan()
    daily_plan.last_updated = datetime.datetime(2018, 6, 27, 11, 30, 0)
    athlete_dao = DailyPlanDatastore()
    athlete_dao.put(daily_plan)
    assert None is not daily_plan


