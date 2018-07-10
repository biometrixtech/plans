import pytest
import datetime
import logic.training_plan_management as tpm

# => deprioritize: readiness, sleep quality, RPE, freshness index?, prior completed recovery sessions?
# => deprioritize: heightened priority relative to bed time

# 10, 20, 30 min sessions, limit to 15 min

# limit only to exercise library
# unscheduled
# maybe exclude injury altogether (maybe just include ACL later?) then > 1 injury
# excluded 72 hour monitoring

# need to include days of no reporting by athlete within 72 hour window
# need to include prioritization of exercises based on injury

# how does marking complete affect scoring?
# how does the prioritization of exercise by body part play a role?
# need to include short term events (7 days) and long term events (28 days)


def test_get_start_time_from_morning_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 27, 0, 0, 0) == start_time


def test_get_end_time_from_morning_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 27, 12, 0, 0) == end_time


def test_get_start_time_from_afternoon_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 27, 12, 0, 0) == start_time


def test_get_end_time_from_afternoon_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == end_time


def test_get_start_time_from_evening_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 27, 12, 0, 0) == start_time


def test_get_end_time_from_evening_trigger_recovery_0():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == end_time


def test_get_start_time_from_morning_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 27, 12, 0, 0) == start_time


def test_get_end_time_from_morning_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == end_time


def test_get_start_time_from_afternoon_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == start_time


def test_get_end_time_from_afternoon_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == end_time


def test_get_start_time_from_evening_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == start_time


def test_get_end_time_from_evening_trigger_recovery_1():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 1)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == end_time


def test_get_start_time_from_morning_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 28, 0, 0, 0) == start_time


def test_get_end_time_from_morning_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == end_time


def test_get_start_time_from_afternoon_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == start_time


def test_get_end_time_from_afternoon_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == end_time


def test_get_start_time_from_evening_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == start_time


def test_get_end_time_from_evening_trigger_recovery_2():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 2)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == end_time


def test_get_start_time_from_morning_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 28, 12, 0, 0) == start_time


def test_get_end_time_from_morning_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == end_time


def test_get_start_time_from_afternoon_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == start_time


def test_get_end_time_from_afternoon_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 14, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 12, 0, 0) == end_time


def test_get_start_time_from_evening_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 0, 0, 0) == start_time


def test_get_end_time_from_evening_trigger_recovery_3():
    date_time_trigger = datetime.datetime(2018, 6, 27, 20, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 3)
    assert datetime.datetime(2018, 6, 29, 12, 0, 0) == end_time


'''Business related tests

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