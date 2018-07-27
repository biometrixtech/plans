from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore


def test_get_readiness_survey_test_data():
    athlete_dao = DailyReadinessDatastore()
    last_daily_readiness_survey = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad")
    assert None is not last_daily_readiness_survey


def test_get_daily_plan_many():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad","2018-06-01","2018-08-13")
    assert None is not plans


def test_get_daily_plan_doesnt_exist():
    athlete_dao = DailyPlanDatastore()
    plans = athlete_dao.get("02cb7965-7921-493a-80d4-6b278c928fad","2018-08-01","2018-08-13")
    assert None is not plans


def test_get_post_session_surveys():
    athlete_dao = PostSessionSurveyDatastore()
    surveys = athlete_dao.get("morning_practice_2", "2018-07-10", "2018-07-11")
    assert None is surveys
