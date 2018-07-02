import pytest
import soreness_and_injury
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
    survey = soreness_and_injury.DailyReadinessSurvey()
    survey.report_date_time = datetime.datetime(2018, 6, 27, 14, 30, 0)

    soreness_item = soreness_and_injury.DailySoreness()
    soreness_item.severity = severity_score
    soreness_item.body_part = soreness_and_injury.BodyPart(9)
    survey.soreness.append(soreness_item)
    return survey


@pytest.fixture(scope="module")
def readiness_survey_0_hours_ankle_foot(severity_score_1, severity_score_2):
    survey = soreness_and_injury.DailyReadinessSurvey()
    survey.report_date_time = datetime.datetime(2018, 6, 27, 14, 30, 0)

    soreness_item_1 = soreness_and_injury.DailySoreness()
    soreness_item_1.severity = severity_score_1
    soreness_item_1.body_part = soreness_and_injury.BodyPart(9)
    survey.soreness.append(soreness_item_1)

    soreness_item_2 = soreness_and_injury.DailySoreness()
    soreness_item_2.severity = severity_score_2
    soreness_item_2.body_part = soreness_and_injury.BodyPart(10)
    survey.soreness.append(soreness_item_2)
    return survey


@pytest.fixture(scope="module")
def post_session_survey_24_hours_ankle(severity_score):
    survey = soreness_and_injury.PostSessionSurvey()
    survey.report_date_time = datetime.datetime(2018, 6, 26, 17, 0, 0)

    soreness_item = soreness_and_injury.DailySoreness()
    soreness_item.severity = severity_score
    soreness_item.body_part = soreness_and_injury.BodyPart(9)
    survey.soreness.append(soreness_item)
    return survey


@pytest.fixture(scope="module")
def post_session_survey_24_hours_foot(severity_score):
    survey = soreness_and_injury.PostSessionSurvey()
    survey.report_date_time = datetime.datetime(2018, 6, 26, 17, 0, 0)

    soreness_item = soreness_and_injury.DailySoreness()
    soreness_item.severity = severity_score
    soreness_item.body_part = soreness_and_injury.BodyPart(10)
    survey.soreness.append(soreness_item)
    return survey


@pytest.fixture(scope="module")
def post_session_survey_24_hrs_ankle_foot(severity_score_1, severity_score_2):
    survey = soreness_and_injury.PostSessionSurvey()
    survey.report_date_time = datetime.datetime(2018, 6, 26, 17, 0, 0)

    soreness_item_1 = soreness_and_injury.DailySoreness()
    soreness_item_1.severity = severity_score_1
    soreness_item_1.body_part = soreness_and_injury.BodyPart(9)
    survey.soreness.append(soreness_item_1)

    soreness_item_2 = soreness_and_injury.DailySoreness()
    soreness_item_2.severity = severity_score_2
    soreness_item_2.body_part = soreness_and_injury.BodyPart(10)
    survey.soreness.append(soreness_item_2)
    return survey


@pytest.fixture(scope="module")
def post_session_survey_48_hours_ankle(severity_score):
    survey = soreness_and_injury.PostSessionSurvey()
    survey.report_date_time = datetime.datetime(2018, 6, 25, 17, 0, 0)

    soreness_item = soreness_and_injury.DailySoreness()
    soreness_item.severity = severity_score
    soreness_item.body_part = soreness_and_injury.BodyPart(9)
    survey.soreness.append(soreness_item)
    return survey


@pytest.fixture(scope="module")
def post_session_survey_49_hours_ankle(severity_score):
    survey = soreness_and_injury.PostSessionSurvey()
    survey.report_date_time = datetime.datetime(2018, 6, 25, 14, 0, 0)

    soreness_item = soreness_and_injury.DailySoreness()
    soreness_item.severity = severity_score
    soreness_item.body_part = soreness_and_injury.BodyPart(9)
    survey.soreness.append(soreness_item)
    return survey


@pytest.fixture(scope="module")
def post_session_survey_24_hours_no_soreness():
    survey = soreness_and_injury.PostSessionSurvey()
    survey.report_date_time = datetime.datetime(2018, 6, 26, 17, 0, 0)

    return survey


@pytest.fixture(scope="module")
def body_part(body_enum, severity_score):
    soreness_item = soreness_and_injury.DailySoreness()
    soreness_item.severity = severity_score
    soreness_item.body_part = soreness_and_injury.BodyPart(body_enum)
    return soreness_item


def test_soreness_from_readiness_survey_1_day_only():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2), None,
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part


def test_soreness_from_readiness_and_post_session_1_day_only_no_number():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_no_soreness(),
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part


def test_soreness_from_readiness_and_post_session_1_day_only_lower_number():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(3),
                                                                            post_session_survey_24_hours_ankle(2),
                                                                            trigger_date_time())
    assert body_part(9, 3).severity == soreness_list[0].severity
    assert body_part(9, 3).body_part == soreness_list[0].body_part


def test_soreness_from_readiness_and_post_session_1_day_only_same_number():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_ankle(2),
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part

            
def test_soreness_from_readiness_and_post_session_1_day_only_higher_number():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_ankle(3),
                                                                            trigger_date_time())
    assert body_part(9, 3).severity == soreness_list[0].severity
    assert body_part(9, 3).body_part == soreness_list[0].body_part


def test_day_3_readiness_plus_past_1_post_session_survey_48_hours_old():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_48_hours_ankle(3),
                                                                            trigger_date_time())
    assert body_part(9, 3).severity == soreness_list[0].severity
    assert body_part(9, 3).body_part == soreness_list[0].body_part


def test_day_3_readiness_plus_past_1_post_session_survey_49_hours_old(): #ignored
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_49_hours_ankle(3),
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part
    
# def day_3_readiness_plus_past_2_post_session_survey_48_hours_old():
    
# 2 body part


def test_soreness_2_body_parts_from_readiness_survey_1_day_only_same_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(2, 2),
                                                                            None,
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part
    assert body_part(10, 2).severity == soreness_list[1].severity
    assert body_part(10, 2).body_part == soreness_list[1].body_part


def test_soreness_2_body_parts_from_readiness_survey_1_day_only_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(3, 2),
                                                                            None,
                                                                            trigger_date_time())
    assert body_part(9, 3).severity == soreness_list[0].severity
    assert body_part(9, 3).body_part == soreness_list[0].body_part
    assert body_part(10, 2).severity == soreness_list[1].severity
    assert body_part(10, 2).body_part == soreness_list[1].body_part


def test_soreness_2_body_parts_from_readiness_survey_post_session_1_day_only_same_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_foot(2),
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part
    assert body_part(10, 2).severity == soreness_list[1].severity
    assert body_part(10, 2).body_part == soreness_list[1].body_part


def test_soreness_2_body_parts_from_readiness_survey_post_session_1_day_only_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hours_foot(3),
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part
    assert body_part(10, 3).severity == soreness_list[1].severity
    assert body_part(10, 3).body_part == soreness_list[1].body_part


def test_soreness_2_body_parts_from_readiness_survey_post_session_1_day_only_same_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hrs_ankle_foot(2, 3),
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part
    assert body_part(10, 3).severity == soreness_list[1].severity
    assert body_part(10, 3).body_part == soreness_list[1].body_part


def test_soreness_2_body_parts_from_readiness_survey_post_session_1_day_only_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle(2),
                                                                            post_session_survey_24_hrs_ankle_foot(3, 3),
                                                                            trigger_date_time())
    assert body_part(9, 3).severity == soreness_list[0].severity
    assert body_part(9, 3).body_part == soreness_list[0].body_part
    assert body_part(10, 3).severity == soreness_list[1].severity
    assert body_part(10, 3).body_part == soreness_list[1].body_part


def test_soreness_2_body_parts_from_2_readiness_survey_post_session_1_day_only_same_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(2, 3),
                                                                            post_session_survey_24_hours_ankle(2),
                                                                            trigger_date_time())
    assert body_part(9, 2).severity == soreness_list[0].severity
    assert body_part(9, 2).body_part == soreness_list[0].body_part
    assert body_part(10, 3).severity == soreness_list[1].severity
    assert body_part(10, 3).body_part == soreness_list[1].body_part


def test_soreness_2_body_parts_from_2_readiness_survey_post_session_1_day_only_diff_severity():
    soreness_list = soreness_calculator().get_soreness_summary_from_surveys(readiness_survey_0_hours_ankle_foot(2, 3),
                                                                            post_session_survey_24_hours_ankle(3),
                                                                            trigger_date_time())
    assert body_part(9, 3).severity == soreness_list[0].severity
    assert body_part(9, 3).body_part == soreness_list[0].body_part
    assert body_part(10, 3).severity == soreness_list[1].severity
    assert body_part(10, 3).body_part == soreness_list[1].body_part
