import pytest
import logic.soreness_processing as soreness_and_injury
from models.soreness import Soreness, BodyPartLocation
from models.daily_readiness import DailyReadiness
from models.post_session_survey import PostSessionSurvey, PostSurvey
from tests.testing_utilities import TestUtilities
import datetime

# 1 body part


@pytest.fixture(scope="module")
def trigger_date_time():
    return datetime.datetime(2018, 6, 27, 14, 30, 0)


@pytest.fixture(scope="module")
def soreness_calculator():
    soreness_calc = soreness_and_injury.SorenessCalculator()
    return soreness_calc


@pytest.fixture(scope="module")
def readiness_survey_0_hours_ankle(severity_score):

    soreness_item = TestUtilities().body_part_soreness(9, severity_score)
    survey = DailyReadiness(datetime.datetime(2018, 6, 27, 14, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "tester", [soreness_item], 5, 5)

    return survey


@pytest.fixture(scope="module")
def readiness_survey_0_hours_ankle_foot(severity_score_1, severity_score_2):

    soreness_item_1 = TestUtilities().body_part_soreness(9, severity_score_1)
    soreness_item_2 = TestUtilities().body_part_soreness(10, severity_score_2)

    survey = DailyReadiness(datetime.datetime(2018, 6, 27, 14, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                            "tester", [soreness_item_1, soreness_item_2], 5, 5)

    return survey


@pytest.fixture(scope="module")
def post_session_survey_24_hours_ankle(severity_score):
    surveys = []

    soreness_list = [TestUtilities().body_part_soreness(9, severity_score)]

    post_survey = TestUtilities().get_post_survey(6, soreness_list)

    post_session_survey = PostSessionSurvey(datetime.datetime(2018, 6, 26, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey)

    surveys.append(post_session_survey)

    return surveys


@pytest.fixture(scope="module")
def post_session_survey_24_hours_foot(severity_score):
    surveys = []

    soreness_list = [TestUtilities().body_part_soreness(10, severity_score)]

    post_survey = TestUtilities().get_post_survey(6, soreness_list)

    post_session_survey = PostSessionSurvey(datetime.datetime(2018, 6, 26, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey)

    surveys.append(post_session_survey)

    return surveys


@pytest.fixture(scope="module")
def post_session_survey_24_hrs_ankle_foot(severity_score_1, severity_score_2):
    surveys = []

    soreness_list = [TestUtilities().body_part_soreness(9, severity_score_1), TestUtilities().body_part_soreness(10, severity_score_2)]

    post_survey = TestUtilities().get_post_survey(6, soreness_list)

    post_session_survey = PostSessionSurvey(datetime.datetime(2018, 6, 26, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey)

    surveys.append(post_session_survey)

    return surveys

@pytest.fixture(scope="module")
def post_session_survey_after_ankle_foot(severity_score_1, severity_score_2):
    surveys = []

    soreness_list = [TestUtilities().body_part_soreness(9, severity_score_1), TestUtilities().body_part_soreness(10, severity_score_2)]

    post_survey = TestUtilities().get_post_survey(6, soreness_list)

    post_session_survey = PostSessionSurvey(datetime.datetime(2018, 6, 27, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey)

    surveys.append(post_session_survey)

    return surveys

@pytest.fixture(scope="module")
def post_session_survey_48_hours_ankle(severity_score):
    surveys = []

    soreness_list = [TestUtilities().body_part_soreness(9, severity_score)]

    post_survey = TestUtilities().get_post_survey(6, soreness_list)

    post_session_survey = PostSessionSurvey(datetime.datetime(2018, 6, 25, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey)

    surveys.append(post_session_survey)

    return surveys


@pytest.fixture(scope="module")
def post_session_surveys_24_48_hours_foot(severity_score_1, severity_score_2):
    surveys = []

    soreness_list_1 = [TestUtilities().body_part_soreness(10, severity_score_1)]

    post_survey_1 = TestUtilities().get_post_survey(6, soreness_list_1)

    post_session_survey = PostSessionSurvey(datetime.datetime(2018, 6, 25, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey_1)

    surveys.append(post_session_survey)

    soreness_list_2 = [TestUtilities().body_part_soreness(10, severity_score_2)]

    post_survey_2 = TestUtilities().get_post_survey(6, soreness_list_2)

    post_session_survey_2 = PostSessionSurvey(datetime.datetime(2018, 6, 26, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey_2)

    surveys.append(post_session_survey_2)

    return surveys

@pytest.fixture(scope="module")
def post_session_survey_49_hours_ankle(severity_score):
    surveys = []

    soreness_list = [TestUtilities().body_part_soreness(9, severity_score)]

    post_survey = TestUtilities().get_post_survey(6, soreness_list)

    post_session_survey = PostSessionSurvey(datetime.datetime(2018, 6, 25, 14, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey)

    surveys.append(post_session_survey)

    return surveys


@pytest.fixture(scope="module")
def post_session_survey_24_hours_no_soreness():
    surveys = []

    soreness_list = []

    post_survey = TestUtilities().get_post_survey(6, soreness_list)

    post_session_survey = PostSessionSurvey(datetime.datetime(2018, 6, 26, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey)

    surveys.append(post_session_survey)

    return surveys

@pytest.fixture(scope="module")
def three_post_session_survey_24_hours_mixed_soreness():
    surveys = []

    soreness_list_1 = [TestUtilities().body_part_soreness(15, 1)]

    post_survey_1 = TestUtilities().get_post_survey(3, soreness_list_1)

    post_session_survey_1 = PostSessionSurvey(datetime.datetime(2018, 6, 26, 17, 0, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                            "tester",
                                            "test_session", 0, post_survey_1)

    surveys.append(post_session_survey_1)

    soreness_list_2 = [TestUtilities().body_part_soreness(15, 4)]

    post_survey_2 = TestUtilities().get_post_survey(6, soreness_list_2)

    post_session_survey_2 = PostSessionSurvey(datetime.datetime(2018, 6, 26, 17, 1, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                              "tester",
                                              "test_session", 0, post_survey_2)

    surveys.append(post_session_survey_2)

    soreness_list_3 = []

    post_survey_3 = TestUtilities().get_post_survey(4, soreness_list_3)

    post_session_survey_3 = PostSessionSurvey(datetime.datetime(2018, 6, 26, 17, 2, 0).strftime("%Y-%m-%dT%H:%M:%SZ"),
                                              "tester",
                                              "test_session", 0, post_survey_3)

    surveys.append(post_session_survey_3)

    return surveys



def test_soreness_from_readiness_survey_1_day_only():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2), None,
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location


def test_soreness_from_readiness_and_post_session_1_day_only_no_number():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_no_soreness(),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location


def test_soreness_from_readiness_and_post_session_1_day_only_lower_number():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(3),
                                                                            post_session_survey_24_hours_ankle(2),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 3).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 3).body_part == soreness_list[0].body_part.location


def test_soreness_from_readiness_and_post_session_1_day_only_same_number():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_ankle(2),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location

            
def test_soreness_from_readiness_and_post_session_1_day_only_higher_number():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_ankle(3),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 3).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 3).body_part == soreness_list[0].body_part.location


def test_day_3_readiness_plus_past_1_post_session_survey_48_hours_old():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_48_hours_ankle(3),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location


def test_day_3_readiness_plus_past_1_post_session_survey_49_hours_old(): #ignored
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_49_hours_ankle(3),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location
    
# def day_3_readiness_plus_past_2_post_session_survey_48_hours_old():
    
# 2 body part


def test_soreness_2_body_parts_from_readiness_survey_1_day_only_same_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(2, 2),
                                                                            None,
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 2).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 2).body_part == soreness_list[1].body_part.location


def test_soreness_2_body_parts_from_readiness_survey_1_day_only_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(3, 2),
                                                                            None,
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 3).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 3).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 2).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 2).body_part == soreness_list[1].body_part.location


def test_soreness_2_body_parts_from_readiness_survey_post_session_1_day_only_same_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_foot(2),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 2).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 2).body_part == soreness_list[1].body_part.location


def test_soreness_2_body_parts_from_readiness_survey_post_session_1_day_only_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_foot(3),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 3).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 3).body_part == soreness_list[1].body_part.location


def test_soreness_2_body_parts_from_readiness_survey_post_session_1_day_only_same_severity_between_surveys():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hrs_ankle_foot(2, 3),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 3).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 3).body_part == soreness_list[1].body_part.location


def test_soreness_2_body_parts_from_readiness_survey_post_session_1_day_only_diff_severity_between_surveys():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hrs_ankle_foot(3, 3),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 3).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 3).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 3).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 3).body_part == soreness_list[1].body_part.location


def test_soreness_2_body_parts_from_2_readiness_survey_post_session_1_day_only_same_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(2, 3),
                                                                            post_session_survey_24_hours_ankle(2),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 3).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 3).body_part == soreness_list[1].body_part.location


def test_soreness_2_body_parts_from_2_readiness_survey_post_session_1_day_only_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(2, 3),
                                                                            post_session_survey_24_hours_ankle(3),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 3).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 3).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 3).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 3).body_part == soreness_list[1].body_part.location

def test_soreness_2_body_parts_from_2_readiness_survey_post_session_after_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(2, 3),
                                                                            post_session_survey_after_ankle_foot(3, 2),
                                                                            trigger_date_time())
    assert TestUtilities().body_part(9, 3).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 3).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 3).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 3).body_part == soreness_list[1].body_part.location


def test_soreness_2_body_parts_from_2_post_session_one_readienss_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_surveys_24_48_hours_foot(4, 1),
                                                                            trigger_date_time())

    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(10, 1).severity == soreness_list[1].severity
    assert TestUtilities().body_part(10, 1).body_part == soreness_list[1].body_part.location

def test_soreness_from_3_post_session_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            three_post_session_survey_24_hours_mixed_soreness(),
                                                                            trigger_date_time())

    assert TestUtilities().body_part(9, 2).severity == soreness_list[0].severity
    assert TestUtilities().body_part(9, 2).body_part == soreness_list[0].body_part.location
    assert TestUtilities().body_part(15, 4).severity == soreness_list[1].severity
    assert TestUtilities().body_part(15, 4).body_part == soreness_list[1].body_part.location