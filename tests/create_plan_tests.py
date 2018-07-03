import pytest
import training
import datetime
import training_plan_management


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
def blank_plan(trigger_date_time):
    mgr = training_plan_management.TrainingPlanManager()
    daily_plan = mgr.create_daily_plan(trigger_date_time)
    return daily_plan


def test_daily_plan_am_recovery_has_am_start():
    assert blank_plan(get_morning_time()).recovery_am.start_time == get_morning_midnight()


def test_daily_plan_am_recovery_has_am_end():
    assert blank_plan(get_morning_time()).recovery_am.end_time == get_noon()


def test_daily_plan_am_recovery_has_pm_start():
    assert blank_plan(get_morning_time()).recovery_pm.start_time == get_noon()


def test_daily_plan_am_recovery_has_pm_end():
    assert blank_plan(get_morning_time()).recovery_pm.end_time == get_evening_midnight()


def test_daily_plan_pm_recovery_has_no_am_start():
    assert blank_plan(get_afternoon_time()).recovery_am is None


def test_daily_plan_pm_recovery_pm_start():
    assert blank_plan(get_afternoon_time()).recovery_pm.start_time == get_noon()


def test_daily_plan_has_pm_recovery_pm_end():
    assert blank_plan(get_afternoon_time()).recovery_pm.end_time == get_evening_midnight()

