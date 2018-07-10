import pytest
import logic.athlete_data_access as athlete_data_access
import logic.soreness_and_injury as soreness_and_injury


def test_get_readiness_survey_test_data():
    athlete_dao = athlete_data_access.AthleteDataAccess("02cb7965-7921-493a-80d4-6b278c928fad")
    last_daily_readiness_survey = athlete_dao.get_last_daily_readiness_survey()
    assert None is not last_daily_readiness_survey


def test_get_training_schedule_test_data():
    athlete_dao = athlete_data_access.AthleteDataAccess("02cb7965-7921-493a-80d4-6b278c928fad")
    scheduled_sessions = athlete_dao.get_scheduled_sessions("2018-06-27")
    assert None is not scheduled_sessions