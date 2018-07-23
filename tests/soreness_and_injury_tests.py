from logic.soreness_and_injury import SorenessCalculator
from models.daily_readiness import DailyReadiness
from models.post_session_survey import PostSessionSurvey
import datetime


def body_part_soreness(location_enum, severity):
    # soreness = DailySoreness()
    # body_part = BodyPart(body_part_location(location_enum), 0)
    # soreness.body_part = body_part
    # soreness.severity = severity

    soreness = {
        "body_part": location_enum,
        "severity": severity
    }

    return soreness


def get_post_survey(RPE, soreness_list):

    survey = {
        "RPE": RPE,
        "soreness": soreness_list
    }

    return survey


def test_no_soreness_cancels_out_existing_soreness():
    calc = SorenessCalculator()
    user_id = "Tester"
    july_14_soreness_list = [body_part_soreness(9, 1), body_part_soreness(7, 2)]

    july_14_survey = DailyReadiness(datetime.datetime(2018, 7, 14, 14, 15, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id,
                                    july_14_soreness_list, 3, 1)

    july_14_post_soreness_list = []

    july_14_post_survey = get_post_survey(8, july_14_post_soreness_list)
    july_14_post_session_survey = \
        PostSessionSurvey(datetime.datetime(2018, 7, 14, 17, 30, 0).strftime("%Y-%m-%dT%H:%M:%SZ"), user_id, None,
                          2, july_14_post_survey)

    soreness_list = calc.get_soreness_summary_from_surveys(july_14_survey, [july_14_post_session_survey],
                                                           july_14_survey.get_event_date())

    assert 0 is len(soreness_list)
