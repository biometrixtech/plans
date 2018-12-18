from models.soreness import BodyPart, BodyPartLocation, HistoricSoreness, HistoricSorenessStatus,Soreness
from logic.stats_processing import StatsProcessing
from tests.mocks.mock_datastore_collection import DatastoreCollection
from models.daily_readiness import DailyReadiness
from models.post_session_survey import PostSessionSurvey
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from models.session import SessionType
from tests.testing_utilities import TestUtilities
from datetime import datetime, timedelta
from utils import parse_date, format_date


def get_dates(start_date, end_date):

    dates = []

    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates


def get_soreness_list(body_part_location, side, severity, is_pain, days=None, date=None):

    soreness_list = []

    initial_reported_date = parse_date(date) - timedelta(days=(len(severity)-1))

    for x in range(0, len(severity)):

        if severity[x] is not None:
            soreness = Soreness()
            soreness.side = side
            soreness.body_part = BodyPart(body_part_location, 1)
            soreness.severity = severity[x]
            soreness.pain = is_pain

            current_date = initial_reported_date + timedelta(days=x)

            soreness.reported_date_time = format_date(current_date)
            soreness_list.append(soreness)

    return soreness_list

def extend_with_nones(existing_list, number_of_nones):

    none_list = []

    for x in range(0, number_of_nones):
        none_list.append(None)

    existing_list.extend(none_list)

    return existing_list


def get_historic_soreness(severity_list, date, historic_soreness=None, is_pain=True):

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity_list, is_pain, date=date)

    stats_processing = StatsProcessing("tester", date, DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list,historic_soreness)

    return historic_soreness


def get_historic_soreness_and_answer_acute_question(severity_list, date, historic_soreness=None):

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity_list, True, date=date)

    stats_processing = StatsProcessing("tester", date, DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list,historic_soreness)

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, soreness_list, BodyPartLocation.achilles, 1,
                                                                    date, True)

    return historic_soreness


def get_historic_soreness_and_answer_pers2_question(severity_list, date, historic_soreness=None, is_pain=True):

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity_list, is_pain, date=date)

    stats_processing = StatsProcessing("tester", date, DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list,historic_soreness)

    historic_soreness = stats_processing.answer_persistent_2_question(historic_soreness, BodyPartLocation.achilles, 1,
                                                                      is_pain, date, True)

    return historic_soreness


def test_flag_acute_pain_3_days():

    historic_soreness = get_historic_soreness([1, 2, 3], "2018-05-14")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_5_days():

    historic_soreness = get_historic_soreness([1, None, 2, None, 3], "2018-05-16")

    assert(HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_5_days_v2():

    historic_soreness = get_historic_soreness([1, 2, None, None, 3], "2018-05-16")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_7_days():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3], "2018-05-18")

    assert(HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_7_days_3_day_gap():

    historic_soreness = get_historic_soreness([1, None, None, None, 2, 3, 2], "2018-05-18")

    assert(HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, None, 2, 3, 2, None], "2018-05-19", historic_soreness)

    # this is acute pain (and not almost_persistent_2_acute) because the acute pain start doesn't begin until the fifth element of the soreness list
    assert(HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

def test_almost_acute_pain_6_days_3_day_gap():

    historic_soreness = get_historic_soreness([1, None, None, None, 2, 3], "2018-05-17")

    assert(HistoricSorenessStatus.almost_acute_pain is historic_soreness[0].historic_soreness_status)


def test_no_flag_acute_pain_7_days_5_day_gap():

    historic_soreness = get_historic_soreness([1, None, None, None, None, None, 2], "2018-05-18")

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


def test_no_flag_almost_acute_pain_7_days_3_day_gap():

    historic_soreness = get_historic_soreness([1, None, 2, None], "2018-05-15")

    assert (HistoricSorenessStatus.almost_acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, 2, None, None], "2018-05-16")

    assert (HistoricSorenessStatus.almost_acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, 2, None, None, None], "2018-05-17")

    assert (HistoricSorenessStatus.almost_acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, 2, None, None, None, None], "2018-05-18")

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, 2, None, None, None, 3], "2018-05-18", historic_soreness)

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


def test_no_flag_acute_pain_7_days_3_day_gap():

    historic_soreness = get_historic_soreness([1, 2, None, None], "2018-05-15")

    assert (HistoricSorenessStatus.almost_acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, 2, None, None, None], "2018-05-16")

    assert (HistoricSorenessStatus.almost_acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, 2, None, None, None, None], "2018-05-17")

    assert (HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, 2, None, None, None, 3], "2018-05-17")

    assert (HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, 2, None, None, None, 3, None], "2018-05-18")

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


def test_almost_acute_pain_7_days_3_day_gap():

    historic_soreness = get_historic_soreness([1, None, None, None, 2, None, 3], "2018-05-18")

    assert(HistoricSorenessStatus.almost_acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_7_days_3_day_gap_question():

    historic_soreness = get_historic_soreness([1, None, None, 2, 3], "2018-05-16")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None], "2018-05-17", historic_soreness)

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None, None], "2018-05-18", historic_soreness)

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None, None, None], "2018-05-19", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_acute_pain_question)

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None, None, None, None], "2018-05-20", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_7_days_5_day_gap_question():

    historic_soreness = get_historic_soreness([1, None, None, 2, 3], "2018-05-18")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None], "2018-05-19", historic_soreness)

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None, None], "2018-05-20", historic_soreness)

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None, None, None], "2018-05-21", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None, None, None, None], "2018-05-22", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_7_days_2_2_3_day_gap_question():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3], "2018-05-18")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None], "2018-05-19", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, None, None], "2018-05-22", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_6_days_3_day_gap_question():

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, None], "2018-05-18")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, None, None], "2018-05-19",historic_soreness)

    # this is okay to be acute_pain because the question will change the status
    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_10_days_3_day_gaps_last_reported():

    # System processes on 2018-05-18 at 1am
    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, None], "2018-05-18")

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3], "2018-05-18", historic_soreness)

    assert("2018-05-18" == historic_soreness[0].last_reported)


def test_flag_acute_pain_10_days_3_day_gaps_question():

    # System processes on 2018-05-18 at 1am

    # ask the question on survey, answer yes
    historic_soreness = get_historic_soreness_and_answer_acute_question([1, 2, 3, None, None, None, None], "2018-05-18")

    # make sure ask question is now false
    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_acute_pain_question)

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3, None, None, None, None], "2018-05-22", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_9_days_3_day_gap_question():

    # System processes on 2018-05-20 at 1am

    historic_soreness = get_historic_soreness([1, 2, None, None, 3, None, None, None, None], "2018-05-20")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)
    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_9_days_3_day_gap_question_v2():

    historic_soreness = get_historic_soreness([1, 2, 3, 2, 3, None, None, None, None], "2018-05-20")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)
    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_11_days_3_day_gap_question():

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, 2, 3, None, None, None, None], "2018-05-22")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)
    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_migrate_acute_pain_to_persistent2_9_days_3_day_gap():

    historic_soreness = get_historic_soreness([1, None, None, 2, 3], "2018-05-16")

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, None, None, 2, 3, None, None, None, None], "2018-05-20", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, None, None, 2, 3, None, None, None, 3,2], "2018-05-21", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_auto_migrate_acute_pain_to_persistent2_9_days_3_day_gap():

    historic_soreness = get_historic_soreness([1, 2, 3], "2018-05-14")
    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)
    historic_soreness = get_historic_soreness_and_answer_acute_question([1, 2, 3, None, None, None, None], "2018-05-18", historic_soreness)
    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3], "2018-05-18", historic_soreness)
    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3, None], "2018-05-19", historic_soreness)
    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3, None, None], "2018-05-20", historic_soreness)
    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3, None, 3], "2018-05-20", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3, None, None, 3, None], "2018-05-21", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_migrate_acute_pain_to_persistent2_11_days_3_day_gap():


    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3], "2018-05-18")

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, None, None, 2, None, None, 3, None, None, None, None],
                                                                  "2018-05-22", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, None, 2, 3],
                                                                  "2018-05-23", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, None, 2, 3, 2],
                                                                  "2018-05-24", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)



def test_migrate_acute_pain_to_persistent2_11_days_3_day_gaps():

    historic_soreness = get_historic_soreness([1, 2, 3], "2018-05-14")

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, 2, 3, None, None, None, None], "2018-05-18", historic_soreness)

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3, None, None, None, None], "2018-05-22",
                                              historic_soreness)
    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)
    assert (True is historic_soreness[0].ask_acute_pain_question)

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, 2, 3, None, None, None, 3, None, None, None, None], "2018-05-22",
                                                                        historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, None, 3, None, None, None, 2], "2018-05-22",
                                                                        historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

def test_migrate_acute_pain_to_persistent2_9_days_3_day_gap_v2():

    historic_soreness = get_historic_soreness([1, 2, None, None, 3], "2018-05-16")

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, 2, None, None, 3, None, None, None, None], "2018-05-20",
                                                                        historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_migrate_acute_pain_to_persistent2_9_days_3_day_gap_v3():

    historic_soreness = get_historic_soreness([1, 2, 3, 2, 3], "2018-05-16")

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, 2, 3, 2, 3, None, None, None, None], "2018-05-20",
                                                                        historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_migrate_acute_pain_to_persistent2_9_days_3_day_gap_v4():

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, 2, 3], "2018-05-18")

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, 2, 3, None, None, 2, 3, None, None, None, None], "2018-05-22",
                                                                        historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps():

    historic_soreness = get_historic_soreness([1, None, None, 2, 3], "2018-05-16")

    historic_soreness = get_historic_soreness([1, None, None, 2, 3, None, None, 2], "2018-05-19", historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps_v2():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3], "2018-05-18")

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, 2], "2018-05-21", historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps_v3():

    historic_soreness = get_historic_soreness([1, 2, 3], "2018-05-14")

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, 2], "2018-05-17", historic_soreness)

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, 2, 3], "2018-05-18", historic_soreness)

    historic_soreness = get_historic_soreness([1, 2, 3, None, None, 2, 3, None, None, 2], "2018-05-21", historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps_v4():

    historic_soreness = get_historic_soreness([1, 2, None, None, 3], "2018-05-16")

    historic_soreness = get_historic_soreness([1, 2, None, None, 3, None, None, 2], "2018-05-19", historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps_v5():

    historic_soreness = get_historic_soreness([1, 2, None, None, 3], "2018-05-16")

    historic_soreness = get_historic_soreness([1, 2, None, None, 3, 2], "2018-05-17", historic_soreness)

    historic_soreness = get_historic_soreness([1, 2, None, None, 3, 2, 3], "2018-05-18", historic_soreness)

    historic_soreness = get_historic_soreness([1, 2, None, None, 3, 2, 3, None, None, 2], "2018-05-21", historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_perisistent_2_pain_ask_persistent_2_Q3():

    historic_soreness = get_historic_soreness([1, None, 2, None, 3], "2018-05-16")

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None, None, None, None], "2018-05-22", historic_soreness)

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness_and_answer_acute_question([1, None, 2, None, 3, None, 2, None, None, None, None], "2018-05-22",
                                                                        historic_soreness)
    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)
    assert(False is historic_soreness[0].ask_persistent_2_question)

    #put in 15 days because it will process on the next day at 1am to prompt the question that day (with 14 non-report days
    historic_soreness = get_historic_soreness(extend_with_nones([1, None, 2, None, 3, None, 2, None, None, None, 3, None, None, 3,3, None, 2], 15), "2018-06-08",
                                              historic_soreness)

    assert(True is historic_soreness[0].ask_persistent_2_question)
    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_perisistent_soreness_ask_persistent_2_Q3():

    historic_soreness = get_historic_soreness([1, None, 2, None, 3], "2018-05-16", [], False)

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None], "2018-05-21",
                                              historic_soreness, False)

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None, None, None, None], "2018-05-22", historic_soreness, False)

    assert (HistoricSorenessStatus.almost_persistent_soreness is historic_soreness[0].historic_soreness_status)
    assert(False is historic_soreness[0].ask_persistent_2_question)

    #put in 15 days because it will process on the next day at 1am to prompt the question that day (with 14 non-report days
    historic_soreness = get_historic_soreness(extend_with_nones([1, None, 2, None, 3, None, 2, None, None, None, 3, None, None, 3,3, None, 2], 8), "2018-06-08",
                                              historic_soreness, False)

    assert(False is historic_soreness[0].ask_persistent_2_question)
    assert (HistoricSorenessStatus.persistent_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(extend_with_nones([1, None, 2, None, 3, None, 2, None, None, None, 3, None, None, 3,3, None, 2], 15), "2018-06-15",
                                              historic_soreness, False)

    assert (True is historic_soreness[0].ask_persistent_2_question)
    assert (HistoricSorenessStatus.persistent_soreness is historic_soreness[0].historic_soreness_status)


def test_perisistent_pain_2_auto_downgrade_persistent():

    historic_soreness = get_historic_soreness([1, None, 2, None, 3], "2018-05-16")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None, 3], "2018-05-20",
                                              historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None, 3, None], "2018-05-21",
                                              historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None, 3, None, 3, None, None, 3, 3, None, 3, None, None, 2, None, None, None, None, None, None, None, 2], "2018-06-08",
                                              historic_soreness)

    assert (HistoricSorenessStatus.persistent_pain is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)


def test_perisistent_soreness_2_auto_downgrade_persistent():

    historic_soreness = get_historic_soreness([1, None, 2, None, 3], "2018-05-16", [], False)

    assert (HistoricSorenessStatus.acute_pain is not historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None, 3], "2018-05-20",
                                              historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None, 3, None], "2018-05-21",
                                              historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)

    historic_soreness = get_historic_soreness([1, None, 2, None, 3, None, 2, None, 3, None, 3, None, None, 3, 3, None, 3, None, None, 2, None, None, None, None, None, None, None, 2], "2018-06-08",
                                              historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_soreness is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)


def test_persistent_pain_flagged_from_reporting():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, 2, None, 3, None, None, 2, None, None, None, 3, None, None, 2, None, None, None], "2018-05-21")
    assert (HistoricSorenessStatus.persistent_pain is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)
    assert (False is historic_soreness[0].ask_acute_pain_question)


def test_persistent_soreness_flagged_from_reporting():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, 2, None, 3, None, None, 2, None, None, None, 3, None, None, 2, None, None, None], "2018-05-21", [], False)
    assert (HistoricSorenessStatus.persistent_soreness is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)
    assert (False is historic_soreness[0].ask_acute_pain_question)


def test_almost_persistent_soreness_flagged_from_reporting():

    historic_soreness = get_historic_soreness([None, None, None, 2, None, None, 3, None, None, None, None, 3, None, None, 2, None, None, None, None, None, None], "2018-05-21", [], False)
    assert (HistoricSorenessStatus.almost_persistent_soreness is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)
    assert (False is historic_soreness[0].ask_acute_pain_question)


def test_persistent_pain_upgraded_to_persistent_2():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, 2, None, None, 3, None, 2, None, None,3,None,None, None, 3, None, None, None], "2018-05-21")
    assert (HistoricSorenessStatus.persistent_pain is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)
    assert (False is historic_soreness[0].ask_acute_pain_question)

    historic_soreness = get_historic_soreness(
        [None, None, 3, None, 2, None, None, 3, None, None, None, 3, None,
         None, None, 2, None, 2, None, 3, None, 2, None, None, 2], "2018-05-31", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_acute_pain_question)
    assert (False is historic_soreness[0].ask_persistent_2_question)


def test_persistent_soreness_upgraded_to_persistent_2():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, 2, None, None, 3, None, 2, None, None,3,None,None, None, 3, None, None, None], "2018-05-21", [], False)
    assert (HistoricSorenessStatus.persistent_soreness is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)
    assert (False is historic_soreness[0].ask_acute_pain_question)

    historic_soreness = get_historic_soreness(
        [None, None, 3, None, 2, None, None, 3, None, None, None, 3, None,
         None, None, 2, None, 2, None, 3, None, 2, None, None, 2], "2018-05-31", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_acute_pain_question)
    assert (False is historic_soreness[0].ask_persistent_2_question)


def test_almost_persistent_2_soreness_flagged_from_reporting():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, 2, None, 3, None, None, 2, 2, None, None, 3, None, None, 2, None, None, 2], "2018-05-21", [], False)
    assert (HistoricSorenessStatus.almost_persistent_2_soreness is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)
    assert (False is historic_soreness[0].ask_acute_pain_question)


def test_persistent_2_soreness_flagged_from_reporting():

    historic_soreness = get_historic_soreness([1, None, None, 2, None, None, 3, None, None, 2, None, 3, None, None, 2, 2, None, None, 3, 2, None, 2, None, None, 2], "2018-05-21", [], False)
    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_question)
    assert (False is historic_soreness[0].ask_acute_pain_question)


def test_persistent_2_upgraded_from_acute():

    historic_soreness = get_historic_soreness(
        [None, None, 3, None, None, None, 3, None, None, None, 3, None,
         None, None, 2, None, 2, None, 3], "2018-05-29")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [None, None, 3, None, None, None, 3, None, None, None, 3, None,
         None, None, 2, None, 2, None, 3, None, 2, None, None], "2018-05-29")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [None, None, 3, None, None, None, 3, None, None, None, 3, None,
         None, None, 2, None, 2, None, 3, None, 2, None, None, 2, None], "2018-05-31", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_persistent_2_pain():

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3], "2018-05-29")

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None], "2018-05-30", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None], "2018-05-31", historic_soreness)

    assert (HistoricSorenessStatus.almost_persistent_2_pain_acute is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2], "2018-06-01", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None], "2018-06-02", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3], "2018-06-03", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None], "2018-06-04", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None], "2018-06-05", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2], "2018-06-06", historic_soreness)

    assert (HistoricSorenessStatus.persistent_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2], "2018-06-07", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None], "2018-06-08", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None], "2018-06-09", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3], "2018-06-10", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2], "2018-06-11", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None], "2018-06-12", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None, 2], "2018-06-13", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None, 2, None], "2018-06-14", historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None, 2, None,
         None], "2018-06-15", historic_soreness, True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None, 2, None,
         None, 2], "2018-06-16", historic_soreness, True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_persistent_2_soreness_over_time():

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3], "2018-05-29", [], False)

    assert (HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None], "2018-05-30", historic_soreness, False)

    assert (HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None], "2018-05-31", historic_soreness, False)

    assert (HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2], "2018-06-01", historic_soreness, False)

    assert (HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None], "2018-06-02", historic_soreness, False)

    assert (HistoricSorenessStatus.almost_persistent_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3], "2018-06-03", historic_soreness, False)

    assert (HistoricSorenessStatus.almost_persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None], "2018-06-04", historic_soreness, False)

    assert (HistoricSorenessStatus.almost_persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None], "2018-06-05", historic_soreness, False)

    assert (HistoricSorenessStatus.almost_persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2], "2018-06-06", historic_soreness, False)

    assert (HistoricSorenessStatus.almost_persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2], "2018-06-07", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None], "2018-06-08", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None], "2018-06-09", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3], "2018-06-10", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2], "2018-06-11", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None], "2018-06-12", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None, 2], "2018-06-13", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None, 2, None], "2018-06-14", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None, 2, None,
         None], "2018-06-15", historic_soreness,False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

    historic_soreness = get_historic_soreness(
        [1, None, None, 2, None, None, 3, None, None, 2, None, 3,
         None, None, 2, 2, None, None, 3, 2, None, 2, None,
         None, 2], "2018-06-16", historic_soreness, False)

    assert (HistoricSorenessStatus.persistent_2_soreness is historic_soreness[0].historic_soreness_status)

