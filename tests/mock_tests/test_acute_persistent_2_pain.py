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


def test_no_flag_acute_pain_6_days_3_day_gap():

    dates = ["2018-05-12", "2018-05-16", "2018-05-17"]
    severity = [1,2,3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-17", DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, soreness_list, [], [], [])

    assert(HistoricSorenessStatus.dormant_cleared is historic_soreness[0].historic_soreness_status)


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

