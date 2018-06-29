import pytest
import datetime
import training_plan_management as tpm

# => deprioritize: readiness, sleep quality, RPE, freshness index?, prior completed recovery sessions?
# => deprioritize: heightened priority relative to bed time

# 10, 20, 30 min sessions, limit to 15 min

# limit only to exercise library
# maybe exclude unscheduled
# maybe exclude injury altogether (maybe just include ACL later?) then > 1 injury

# severity ranking

# > 1 soreness

# date of update

def test_get_morning_start_time():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert start_time == datetime.datetime(2018, 6, 27, 0, 0, 0)

def test_get_morning_end_time():
    date_time_trigger = datetime.datetime(2018, 6, 27, 11, 0, 0)
    mgr = tpm.TrainingPlanManager()
    start_time, end_time = mgr.get_recovery_start_end_times(date_time_trigger, 0)
    assert end_time == datetime.datetime(2018, 6, 27, 12, 0, 0)


'''Business related tests

# am tests

def get_recovery_for_no_injury_no_soreness():

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