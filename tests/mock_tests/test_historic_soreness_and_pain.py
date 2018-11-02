from models.soreness import BodyPart, BodyPartLocation, HistoricSoreness, HistoricSorenessStatus,Soreness
from logic.stats_processing import StatsProcessing
from tests.mocks.mock_datastore_collection import DatastoreCollection


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
