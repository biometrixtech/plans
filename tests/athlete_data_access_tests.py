import pytest
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_schedule_datastore import DailyScheduleDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
import logic.soreness_and_injury as soreness_and_injury
import datetime


def test_get_readiness_survey_test_data():
    athlete_dao = DailyReadinessDatastore()
    last_daily_readiness_survey = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad")
    assert None is not last_daily_readiness_survey


def test_get_training_schedule_test_data():
    athlete_dao = DailyScheduleDatastore()
    scheduled_sessions = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad", datetime.datetime(2018, 7, 10))
    assert None is not scheduled_sessions

def test_get_daily_plan_many():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad","2018-06-01","2018-08-13")
    assert None is not plans

def test_get_daily_plan_doesnt_exist():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad","2018-08-01","2018-08-13")
    assert None is not plans