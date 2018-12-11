from models.soreness import BodyPart, BodyPartLocation, HistoricSoreness, HistoricSorenessStatus,Soreness
from logic.stats_processing import StatsProcessing
from tests.mocks.mock_datastore_collection import DatastoreCollection
from models.daily_readiness import DailyReadiness
from models.post_session_survey import PostSessionSurvey
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from models.session import SessionType
from tests.testing_utilities import TestUtilities
from datetime import datetime, timedelta


def get_dates(start_date, end_date):

    dates = []

    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates


def get_soreness_list(body_part_location, side, severity, is_pain, days):

    soreness_list = []

    for x in range(0, len(days)):
        soreness = Soreness()
        soreness.side = side
        soreness.body_part = BodyPart(body_part_location, 1)
        soreness.severity = severity[x]
        soreness.pain = is_pain
        soreness.reported_date_time = days[x]
        soreness_list.append(soreness)

    return soreness_list


def test_flag_acute_pain_3_days():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1, 2, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-14", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([],soreness_list,  [],[], [])

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_5_days():

    dates = ["2018-05-12", "2018-05-15", "2018-05-16"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [],[], [])

    assert(HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_5_days_v2():

    dates = ["2018-05-12", "2018-05-13", "2018-05-16"]
    severity = [1, 2, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [],[], [])

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_7_days():

    dates = ["2018-05-12", "2018-05-15", "2018-05-18"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [])

    assert(HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_7_days_3_day_gap():

    dates = ["2018-05-12", "2018-05-16", "2018-05-17", "2018-05-18"]
    severity = [1,2,3,2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    assert(HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)


def test_no_flag_acute_pain_6_days_3_day_gap():

    dates = ["2018-05-12", "2018-05-16", "2018-05-17"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-17", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, soreness_list, [], [], [])

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


def test_no_flag_acute_pain_7_days_5_day_gap():

    dates = ["2018-05-12","2018-05-18"]
    severity = [1,2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, soreness_list, [], [], [])

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


def test_no_flag_acute_pain_7_days_3_day_gap():

    dates = ["2018-05-12", "2018-05-14", "2018-05-18"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, soreness_list, [], [], [])

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


def test_no_flag_acute_pain_7_days_3_day_gap_b():

    dates = ["2018-05-12", "2018-05-13", "2018-05-17"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, soreness_list, [], [], [])

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


def test_no_flag_acute_pain_7_days_3_day_gap_c():

    dates = ["2018-05-12", "2018-05-16", "2018-05-18"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, soreness_list, [], [], [])

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_7_days_3_day_gap_question():

    dates = ["2018-05-12", "2018-05-15", "2018-05-16"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-20", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_7_days_5_day_gap_question():

    dates = ["2018-05-12", "2018-05-15", "2018-05-16"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_7_days_2_2_3_day_gap_question():

    dates = ["2018-05-12", "2018-05-15", "2018-05-18"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_6_days_3_day_gap_question():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_10_days_3_day_gaps_last_reported():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1,2,3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # System processes on 2018-05-18 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list,[], [], [])

    historic_soreness[0].ask_acute_pain_question = False  # reset this to false as timer resets

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-18"]
    severity = [1, 2, 3, 3]
    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())  # user logs in again on 5-22
    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [], historic_soreness)

    assert("2018-05-18" == historic_soreness[0].last_reported)


def test_flag_acute_pain_10_days_3_day_gaps_question():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1,2,3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # System processes on 2018-05-18 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list,[], [], [])

    # ask the question on survey, answer yes
    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1,
                                                                    "2018-05-18", True)

    # make sure ask question is now false
    assert (False is historic_soreness[0].ask_acute_pain_question)

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-18"] # still within last 10 days
    severity = [1, 2, 3, 3]
    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())  # user logs in again on 5-22
    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [], historic_soreness)

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_9_days_3_day_gap_question():

    dates = ["2018-05-12", "2018-05-13", "2018-05-16"]
    severity = [1,2,3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # System processes on 2018-05-19 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-20", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list,[], [], [])

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_9_days_3_day_gap_question_v2():

    dates = ["2018-05-12", "2018-05-13","2018-05-14","2018-05-15", "2018-05-16"]
    severity = [1,2,3,2,3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # System processes on 2018-05-19 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-20", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list,[], [], [])

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_flag_acute_pain_11_days_3_day_gap_question():

    dates = ["2018-05-12", "2018-05-13","2018-05-14","2018-05-17", "2018-05-18"]
    severity = [1,2,3,2,3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # System processes on 2018-05-21 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list,[], [], [])

    assert(True is historic_soreness[0].ask_acute_pain_question)


def test_migrate_acute_pain_to_persistent2_9_days_3_day_gap():

    dates = ["2018-05-12", "2018-05-15", "2018-05-16"]
    severity = [1, 2, 3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    # System processes on 2018-05-20 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-20", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1, "2018-05-20", True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_migrate_acute_pain_to_persistent2_11_days_3_day_gap():

    dates = ["2018-05-12", "2018-05-15", "2018-05-18"]
    severity = [1, 2, 3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    # System processes on 2018-05-22 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1, "2018-05-22", True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_auto_migrate_acute_pain_to_persistent2_9_days_3_day_gap():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1, 2, 3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-14", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    # System processes on 2018-05-18 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1, "2018-05-18", True)

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-18"]
    severity = [1, 2, 3, 3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # System processes on 2018-05-21 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [], historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_migrate_acute_pain_to_persistent2_11_days_3_day_gaps():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1, 2, 3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-14", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    # System processes on 2018-05-18 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1, "2018-05-18", True)

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-18"]
    severity = [1, 2, 3, 3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # System processes on 2018-05-22 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [], historic_soreness)

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)
    assert (True is historic_soreness[0].ask_acute_pain_question)

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1,
                                                                    "2018-05-22", True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_migrate_acute_pain_to_persistent2_9_days_3_day_gap_v2():

    dates = ["2018-05-12", "2018-05-13", "2018-05-16"]
    severity = [1, 2, 3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    # System processes on 2018-05-20 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-20", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1, "2018-05-20", True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_migrate_acute_pain_to_persistent2_9_days_3_day_gap_v3():

    dates = ["2018-05-12", "2018-05-13","2018-05-14","2018-05-15", "2018-05-16"]
    severity = [1, 2, 3,2,3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    # System processes on 2018-05-20 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-20", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1, "2018-05-20", True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_migrate_acute_pain_to_persistent2_9_days_3_day_gap_v4():

    dates = ["2018-05-12", "2018-05-13","2018-05-14","2018-05-17", "2018-05-18"]
    severity = [1, 2, 3,2,3]

    ten_day_soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    # System processes on 2018-05-22 at 1am

    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], ten_day_soreness_list, [], [], [])

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1, "2018-05-22", True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps():

    dates = ["2018-05-12", "2018-05-15", "2018-05-16"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    dates = ["2018-05-12", "2018-05-15", "2018-05-16", "2018-05-19"]
    severity = [1, 2, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-19", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps_v2():

    dates = ["2018-05-12", "2018-05-15", "2018-05-18"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    dates = ["2018-05-12", "2018-05-15", "2018-05-18", "2018-05-21"]
    severity = [1, 2, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps_v3():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-14", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-17"]
    severity = [1, 2, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-17", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-17", "2018-05-18"]
    severity = [1, 2, 3, 2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-17", "2018-05-18", "2018-05-21"]
    severity = [1, 2, 3, 2, 3,2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps_v4():

    dates = ["2018-05-12", "2018-05-13", "2018-05-16"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    dates = ["2018-05-12", "2018-05-15", "2018-05-16", "2018-05-19"]
    severity = [1, 2, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-19", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_8_days_no_gaps_v5():

    dates = ["2018-05-12", "2018-05-13", "2018-05-16"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-16", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list,[], [], [])

    dates = ["2018-05-12", "2018-05-13", "2018-05-16", "2018-05-17"]
    severity = [1, 2, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-17", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    dates = ["2018-05-12", "2018-05-13", "2018-05-16", "2018-05-17", "2018-05-18"]
    severity = [1, 2, 3, 2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    dates = ["2018-05-12", "2018-05-13", "2018-05-16", "2018-05-17", "2018-05-18", "2018-05-21"]
    severity = [1, 2, 3, 2, 3,2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert(HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)


def test_flag_acute_pain_3_days_severity_1():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [2, 1, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-14", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([],soreness_list,  [],[], [])

    assert (1.7 <= historic_soreness[0].average_severity <= 1.9)


def test_flag_acute_pain_3_days_severity_2():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [2, 4, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-14", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([],soreness_list,  [],[], [])

    assert (3.1 <= historic_soreness[0].average_severity <= 3.4)


def test_perisistent_pain_2_question_after_acute_question():

    dates = ["2018-05-12", "2018-05-14", "2018-05-16"]
    severity = [1, 2, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # processed at midnight on 2018-05-16 for the next day
    stats_processing = StatsProcessing("tester", "2018-05-17", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [])

    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18"]
    severity = [1, 2, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # processed at midnight on 2018-05-22 at 1am
    stats_processing = StatsProcessing("tester", "2018-05-22", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, BodyPartLocation.achilles, 1,
                                                                    "2018-05-22", True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)
    assert(False is historic_soreness[0].ask_persistent_2_pain_question)

    dates = ["2018-05-12", "2018-05-14", "2018-05-16","2018-05-18","2018-05-22", "2018-05-25", "2018-05-26", "2018-05-28"]
    severity = [1,2,3,2,3,3,3,2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # processed at midnight on 2018-06-08 at 1am
    stats_processing = StatsProcessing("tester", "2018-06-08", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert(True is historic_soreness[0].ask_persistent_2_pain_question)

    historic_soreness = stats_processing.answer_persistent_2_pain_question(historic_soreness, BodyPartLocation.achilles, 1,
                                                                    "2018-06-08", True)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_pain_question)


def test_perisistent_pain_2_question_automigrate():

    dates = ["2018-05-12", "2018-05-14", "2018-05-16"]
    severity = [1, 2, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # processed at midnight on 2018-05-17 at 1am
    stats_processing = StatsProcessing("tester", "2018-05-17", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [])

    assert (HistoricSorenessStatus.acute_pain is historic_soreness[0].historic_soreness_status)

    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18", "2018-05-20"]
    severity = [1, 2, 3, 2, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # processed at midnight on 2018-05-21 at 1am
    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert (HistoricSorenessStatus.persistent_2_pain is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_pain_question)

    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18", "2018-05-20", "2018-05-22", "2018-05-25", "2018-05-26", "2018-05-28"]
    severity = [1,2,3,2,3,3,3,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # processed at midnight on 2018-06-08 at 1am
    stats_processing = StatsProcessing("tester", "2018-06-08", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list([], soreness_list, [], [], [], historic_soreness)

    assert(True is historic_soreness[0].ask_persistent_2_pain_question)

    historic_soreness = stats_processing.answer_persistent_2_pain_question(historic_soreness, BodyPartLocation.achilles, 1,
                                                                    "2018-06-08", False)

    assert (HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].ask_persistent_2_pain_question)


def test_avg_severity_persistent_2_pain():
    dates = ["2018-05-12", "2018-05-17", "2018-05-21", "2018-05-23", "2018-05-25"]
    severity = [3, 4, 2, 1, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-25", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2_pain(soreness_list, "2018-05-25")

    assert (1.9 <= avg_severity<= 2.3)


def test_avg_severity_persistent_2_pain_v2():
    dates = ["2018-05-12", "2018-05-17", "2018-05-21", "2018-05-23", "2018-05-25", "2018-05-27", "2018-05-30", "2018-06-01"]
    severity = [3, 4, 2, 1, 2, 4, 3, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-06-01", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2_pain(soreness_list, "2018-06-01")

    assert (3.0 <= avg_severity <= 3.3)


def test_avg_severity_persistent_2_pain_2_weeks():

    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18", "2018-05-22", "2018-05-25", "2018-05-26", "2018-05-28"]
    severity = [2, 1, 2, 4, 3, 3, 4, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-28", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2_pain(soreness_list, "2018-05-28")

    assert (2.0 <= avg_severity <= 2.25)

    stats_processing = StatsProcessing("tester", "2018-06-01", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2_pain(soreness_list, "2018-06-01")

    # Note: this is a problem.  We are no longer able to "age" the score to zero as it doesn't reconcile with
    # the other numbers
    assert (2.0 <= avg_severity <= 2.25)

def test_avg_severity_persistent_2_pain_2_weeks_v2():
    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18", "2018-05-20", "2018-05-22", "2018-05-25",
             "2018-05-26", "2018-05-28"]
    severity = [3, 2, 2, 3, 2, 3, 1, 2, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-28", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2_pain(soreness_list, "2018-05-28")

    assert (1.0 <= avg_severity <= 1.25)

    stats_processing = StatsProcessing("tester", "2018-06-01", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2_pain(soreness_list, "2018-06-01")

    # Note: this is a problem.  We are no longer able to "age" the score to zero as it doesn't reconcile with
    # the other numbers
    assert (1.0 <= avg_severity <= 1.25)