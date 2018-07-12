import pytest
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_schedule_datastore import DailyScheduleDatastore
import logic.soreness_and_injury as soreness_and_injury


def test_get_readiness_survey_test_data():
    athlete_dao = DailyReadinessDatastore()
    last_daily_readiness_survey = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad")
    assert None is not last_daily_readiness_survey


def test_get_training_schedule_test_data():
    athlete_dao = DailyScheduleDatastore()
    scheduled_sessions = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad", "2018-07-10")
    assert None is not scheduled_sessions