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


def get_soreness_list(body_part_location, side, severity, is_pain, length):

    soreness_list = []

    for x in range(0, length):
        soreness = Soreness()
        soreness.side = side
        soreness.body_part = BodyPart(body_part_location, 1)
        soreness.severity = severity
        soreness.pain = is_pain
        soreness_list.append(soreness)

    return soreness_list

def get_daily_readiness_surveys(start_date, end_date):

    surveys = []

    dates = get_dates(start_date, end_date)

    for d in dates:
        soreness = TestUtilities().body_part_soreness(9, 1)
        daily_readiness = DailyReadiness(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", [soreness], 4, 5)
        surveys.append(daily_readiness)

    return surveys


def get_daily_readiness_survey_high_pain(date, soreness_level):

    soreness = TestUtilities().body_part_pain(9, soreness_level, 1)

    daily_readiness = DailyReadiness(date.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", [soreness], 4, 5)

    return daily_readiness


def get_post_session_surveys(start_date, end_date):

    surveys = []

    dates = get_dates(start_date, end_date)

    for d in dates:
        soreness = TestUtilities().body_part_soreness(9, 1)

        soreness_list = [soreness]

        post_survey = TestUtilities().get_post_survey(6, soreness_list)

        post_session = PostSessionSurvey(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester",None, SessionType.practice, post_survey )
        surveys.append(post_session)

    return surveys


def test_build_dictionary_from_soreness():

    soreness_a = Soreness()
    soreness_a.side = 1
    soreness_a.body_part = BodyPart(BodyPartLocation.ankle, 1)
    soreness_a.severity = 2
    soreness_a.is_pain = False

    soreness_b = Soreness()
    soreness_b.side = 1
    soreness_b.body_part = BodyPart(BodyPartLocation.ankle, 1)
    soreness_b.severity = 1
    soreness_b.is_pain = False

    soreness_c = Soreness()
    soreness_c.side = 2
    soreness_c.body_part = BodyPart(BodyPartLocation.ankle, 1)
    soreness_c.severity = 1
    soreness_c.is_pain = False

    soreness_list = [soreness_a, soreness_b, soreness_c]

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    hs_dict = stats_processing.get_hs_dictionary(soreness_list)

    assert(2 is len(hs_dict.keys()))

def test_find_persistent_soreness():

    soreness_list_1 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 2)
    soreness_list_2 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 2)
    soreness_list_3 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 2)
    soreness_list_4 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 2)

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness(soreness_list_1,
                                                               soreness_list_2,
                                                               soreness_list_3,
                                                               soreness_list_4)

    assert(HistoricSorenessStatus.persistent is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].is_pain)


def test_find_chronic_soreness():

    soreness_list_1 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 3)
    soreness_list_2 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 3)
    soreness_list_3 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 3)
    soreness_list_4 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 3)

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness(soreness_list_1,
                                                               soreness_list_2,
                                                               soreness_list_3,
                                                               soreness_list_4)

    assert(HistoricSorenessStatus.chronic is historic_soreness[0].historic_soreness_status)
    assert (False is historic_soreness[0].is_pain)


def test_find_persistent_pain():

    soreness_list_1 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 2)
    soreness_list_2 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 2)
    soreness_list_3 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 2)
    soreness_list_4 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 2)

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness(soreness_list_1,
                                                               soreness_list_2,
                                                               soreness_list_3,
                                                               soreness_list_4)

    assert(HistoricSorenessStatus.persistent is historic_soreness[0].historic_soreness_status)
    assert (True is historic_soreness[0].is_pain)


def test_find_chronic_pain():

    soreness_list_1 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 3)
    soreness_list_2 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 3)
    soreness_list_3 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 3)
    soreness_list_4 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 3)

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness(soreness_list_1,
                                                               soreness_list_2,
                                                               soreness_list_3,
                                                               soreness_list_4)

    assert(HistoricSorenessStatus.chronic is historic_soreness[0].historic_soreness_status)
    assert (True is historic_soreness[0].is_pain)


def test_find_no_soreness():

    soreness_list_1 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 0)
    soreness_list_2 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 0)
    soreness_list_3 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 0)
    soreness_list_4 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 0)

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness(soreness_list_1,
                                                               soreness_list_2,
                                                               soreness_list_3,
                                                               soreness_list_4)

    assert(0 is len(historic_soreness))


def test_find_no_pain():

    soreness_list_1 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 0)
    soreness_list_2 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 0)
    soreness_list_3 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 0)
    soreness_list_4 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 0)

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness(soreness_list_1,
                                                               soreness_list_2,
                                                               soreness_list_3,
                                                               soreness_list_4)

    assert(0 is len(historic_soreness))

def test_find_no_soreness_3_weeks():

    soreness_list_1 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 1)
    soreness_list_2 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 1)
    soreness_list_3 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 1)
    soreness_list_4 = get_soreness_list(BodyPartLocation.ankle, 1, 2, False, 0)

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness(soreness_list_1,
                                                               soreness_list_2,
                                                               soreness_list_3,
                                                               soreness_list_4)

    assert(0 is len(historic_soreness))


def test_find_no_pain_3_weeks():

    soreness_list_1 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 1)
    soreness_list_2 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 1)
    soreness_list_3 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 1)
    soreness_list_4 = get_soreness_list(BodyPartLocation.ankle, 1, 2, True, 0)

    stats_processing = StatsProcessing("tester", "2018-01-01", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness(soreness_list_1,
                                                               soreness_list_2,
                                                               soreness_list_3,
                                                               soreness_list_4)

    assert(0 is len(historic_soreness))

def test_consecutive_pain_3_days():

    readiness_list = []

    readiness_list.append(get_daily_readiness_survey_high_pain(datetime(2018, 7, 17, 11, 0, 0), 3))
    readiness_list.append(get_daily_readiness_survey_high_pain(datetime(2018, 7, 18, 11, 0, 0), 4))
    readiness_list.append(get_daily_readiness_survey_high_pain(datetime(2018, 7, 19, 11, 0, 0), 3))

    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(readiness_list)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats_processing = StatsProcessing("tester", "2018-07-19", datastore_collection)

    stats_processing.set_start_end_times()
    stats_processing.load_historical_data()

    consecutive_pain_list = stats_processing.get_three_days_consecutive_pain_list()

    assert(len(consecutive_pain_list) > 0)

def test_consecutive_pain_not_3_days():

    readiness_list = []

    readiness_list.append(get_daily_readiness_survey_high_pain(datetime(2018, 7, 17, 11, 0, 0), 3))
    readiness_list.append(get_daily_readiness_survey_high_pain(datetime(2018, 7, 19, 11, 0, 0), 3))

    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(readiness_list)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats_processing = StatsProcessing("tester", "2018-07-19", datastore_collection)

    stats_processing.set_start_end_times()
    stats_processing.load_historical_data()

    consecutive_pain_list = stats_processing.get_three_days_consecutive_pain_list()

    assert(len(consecutive_pain_list) == 0)