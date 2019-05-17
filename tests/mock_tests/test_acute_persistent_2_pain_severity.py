from models.soreness import BodyPart, BodyPartLocation, Soreness, HistoricSorenessStatus
from models.historic_soreness import HistoricSoreness
from logic.stats_processing import StatsProcessing
from tests.mocks.mock_datastore_collection import DatastoreCollection
from utils import parse_date

def get_soreness_list(body_part_location, side, severity, is_pain, days):

    soreness_list = []

    for x in range(0, len(days)):
        soreness = Soreness()
        soreness.side = side
        soreness.body_part = BodyPart(body_part_location, 1)
        soreness.severity = severity[x]
        soreness.pain = is_pain
        soreness.reported_date_time = parse_date(days[x])
        soreness_list.append(soreness)

    return soreness_list


def test_flag_acute_pain_3_days_severity_1():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [2, 1, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-14"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (1.7 <= historic_soreness[0].average_severity <= 1.9)


def test_flag_acute_pain_3_days_severity_2():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [2, 4, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-14"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (3.1 <= historic_soreness[0].average_severity <= 3.4)


def test_avg_severity_persistent_2_pain():
    dates = ["2018-05-12", "2018-05-17", "2018-05-21", "2018-05-23", "2018-05-25"]
    severity = [3, 4, 2, 1, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-25", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-25"))

    assert (1.8 <= avg_severity<= 2.3)



def test_avg_severity_persistent_2_pain_v2():
    dates = ["2018-05-12", "2018-05-17", "2018-05-21", "2018-05-23", "2018-05-25", "2018-05-27", "2018-05-30", "2018-06-01"]
    severity = [3, 4, 2, 1, 2, 4, 3, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-06-01", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-06-01"))

    assert (3.0 <= avg_severity <= 3.3)


def test_avg_severity_persistent_2_pain_2_weeks():

    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18", "2018-05-22", "2018-05-25", "2018-05-26", "2018-05-28"]
    severity = [2, 1, 2, 4, 3, 3, 4, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-28", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-28"))

    assert (2.25 <= avg_severity <= 2.5)

    stats_processing = StatsProcessing("tester", "2018-06-08", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list,  parse_date("2018-06-08"))

    assert (0.0 <= avg_severity <= 0.0)


def test_avg_severity_persistent_2_pain_2_weeks_v2():
    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18", "2018-05-20", "2018-05-22", "2018-05-25",
             "2018-05-26", "2018-05-28"]
    severity = [3, 2, 2, 3, 2, 3, 1, 2, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-28", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-28"))

    assert (1.0 <= avg_severity <= 1.25)

    stats_processing = StatsProcessing("tester", "2018-06-08", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-06-08"))

    assert (0.0 <= avg_severity <= 0)


def test_avg_severity_persistent_2_pain_10_days_1():
    dates = ["2018-05-12", "2018-05-14"]
    severity = [2, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.1 <= avg_severity <= 1.5)
    print(avg_severity)

def test_avg_severity_persistent_2_pain_10_days_2():
    dates = ["2018-05-19", "2018-05-21"]
    severity = [2, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.1 <= avg_severity <= 1.5)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_10_days_3():
    dates = ["2018-05-13", "2018-05-16", "2018-05-19", "2018-05-21"]
    severity = [4,4,2,1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.2 <= avg_severity <= 1.6)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_10_days_4():
    dates = ["2018-05-13", "2018-05-16", "2018-05-19", "2018-05-21"]
    severity = [1, 2, 4, 4]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (3.7 <= avg_severity <= 4.1)
    print(avg_severity)



def test_avg_severity_persistent_2_pain_10_days_5():
    dates = ["2018-05-13", "2018-05-16", "2018-05-17", "2018-05-20"]
    severity = [1, 5, 5, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.6 <= avg_severity <= 2.0)
    print(avg_severity)



def test_avg_severity_persistent_2_pain_10_days_6():
    dates = ["2018-05-17", "2018-05-19", "2018-05-21"]
    severity = [2, 1, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.6 <= avg_severity <= 2.0)
    print(avg_severity)



def test_avg_severity_persistent_2_pain_10_days_7():
    dates = ["2018-05-19", "2018-05-20", "2018-05-21"]
    severity = [2, 4, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (3.1 <= avg_severity <= 3.5)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_10_days_8():
    dates = ["2018-05-13", "2018-05-17", "2018-05-19", "2018-05-21"]
    severity = [4, 2, 1, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.8 <= avg_severity <= 2.2)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_10_days_9():
    dates = ["2018-05-12", "2018-05-14", "2018-05-16","2018-05-19", "2018-05-21"]
    severity = [1, 2, 4, 3, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (2.9 <= avg_severity <= 3.3)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_1():
    dates = ["2018-05-13", "2018-05-15", "2018-05-17","2018-05-19", "2018-05-21"]
    severity = [1, 1, 1, 1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (4.0 <= avg_severity <= 4.2)
    print('cc1 - ' + str(avg_severity))


def test_avg_severity_persistent_2_pain_corner_case_2():
    dates = ["2018-05-12", "2018-05-14", "2018-05-16","2018-05-18", "2018-05-20"]
    severity = [1, 1, 1, 1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (4.0 <= avg_severity <= 4.2)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_3():
    dates = ["2018-05-15", "2018-05-16", "2018-05-17","2018-05-18", "2018-05-19"]
    severity = [1, 1, 1, 1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (2.9 <= avg_severity <= 3.3)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_4():
    dates = ["2018-05-13", "2018-05-15", "2018-05-17","2018-05-19", "2018-05-21"]
    severity = [5, 5, 5, 5, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.8 <= avg_severity <= 2.2)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_5():
    dates = ["2018-05-17", "2018-05-18", "2018-05-19","2018-05-20", "2018-05-21"]
    severity = [1, 2, 3, 4, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (4.1 <= avg_severity <= 4.2)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_6():
    dates = ["2018-05-17", "2018-05-18", "2018-05-19","2018-05-20", "2018-05-21"]
    severity = [5, 4, 3, 2, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.6 <= avg_severity <= 2.0)
    print(avg_severity)

# new starts here

def test_avg_severity_persistent_2_pain_corner_case_7():
    dates = ["2018-05-14","2018-05-21"]
    severity = [1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (4.8 <= avg_severity <= 5.0)
    print(avg_severity)

def test_avg_severity_persistent_2_pain_corner_case_8():
    dates = ["2018-05-14","2018-05-21"]
    severity = [5, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.0 <= avg_severity <= 1.2)
    print(avg_severity)

def test_avg_severity_persistent_2_pain_corner_case_9():
    dates = ["2018-05-14", "2018-05-15","2018-05-21"]
    severity = [1, 3, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (4.8 <= avg_severity <= 5.0)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_10():
    dates = ["2018-05-14", "2018-05-15","2018-05-21"]
    severity = [5, 3, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.0 <= avg_severity <= 1.2)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_11():
    dates = ["2018-05-20", "2018-05-21"]
    severity = [1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (3.5 <= avg_severity <= 3.7)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_12():
    dates = ["2018-05-12","2018-05-13","2018-05-14", "2018-05-15","2018-05-16","2018-05-17", "2018-05-18", "2018-05-19","2018-05-20", "2018-05-21"]
    severity = [1, 5, 1, 5, 1, 5, 1, 5, 1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (3.5 <= avg_severity <= 3.7)
    print(avg_severity)

def test_avg_severity_persistent_2_pain_corner_case_13():
    dates = ["2018-05-14", "2018-05-15","2018-05-16","2018-05-17", "2018-05-18", "2018-05-19","2018-05-20", "2018-05-21"]
    severity = [1, 5, 1, 5, 1, 5, 1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (3.5 <= avg_severity <= 3.7)
    print(avg_severity)

def test_avg_severity_persistent_2_pain_corner_case_14():
    dates = ["2018-05-13","2018-05-15","2018-05-17", "2018-05-19","2018-05-21"]
    severity = [5, 5, 5, 5, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (4.97 <= avg_severity <= 5.0)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_15():
    dates = ["2018-05-13","2018-05-15","2018-05-17", "2018-05-19","2018-05-21"]
    severity = [1, 2, 3, 4, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (4.5 <= avg_severity <= 4.8)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_16():
    dates = ["2018-05-13","2018-05-15", "2018-05-17","2018-05-19", "2018-05-21"]
    severity = [5, 4, 3, 2, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (1.2 <= avg_severity <= 1.4)
    print(avg_severity)



def test_avg_severity_persistent_2_pain_corner_case_17():
    dates = ["2018-05-15","2018-05-17", "2018-05-19", "2018-05-21"]
    severity = [5, 4, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (2.2 <= avg_severity <= 2.4)
    print(avg_severity)



def test_avg_severity_persistent_2_pain_corner_case_18():
    dates = ["2018-05-14","2018-05-15", "2018-05-18","2018-05-19"]
    severity = [5, 4, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (2.2 <= avg_severity <= 2.5)
    print(avg_severity)

def test_avg_severity_persistent_2_pain_corner_case_19():
    dates = ["2018-05-16","2018-05-17", "2018-05-18","2018-05-19"]
    severity = [5, 4, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (2.6 <= avg_severity <= 2.8)
    print(avg_severity)


def test_avg_severity_persistent_2_pain_corner_case_20():
    dates = ["2018-05-15","2018-05-16", "2018-05-17","2018-05-18"]
    severity = [5, 4, 3, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", "2018-05-21", DatastoreCollection())

    avg_severity = stats_processing.calc_avg_severity_persistent_2(soreness_list, parse_date("2018-05-21"))

    assert (2.6 <= avg_severity <= 2.8)
    print(avg_severity)

def test_flag_acute_pain_avg_severity_primary_1():

    dates = ["2018-05-12", "2018-05-15", "2018-05-16", "2018-05-18"]
    severity = [3, 3, 4, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (2.1 <= historic_soreness[0].average_severity <= 2.4)


def test_flag_acute_pain_avg_severity_primary_2():

    dates = ["2018-05-12", "2018-05-15", "2018-05-17", "2018-05-18"]
    severity = [4, 3, 3, 4]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (3.6 <= historic_soreness[0].average_severity <= 3.8)



def test_flag_acute_pain_avg_severity_primary_3():

    dates = ["2018-05-12", "2018-05-14", "2018-05-17", "2018-05-18"]
    severity = [2, 4, 3, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (2.9 <= historic_soreness[0].average_severity <= 3.2)



def test_flag_acute_pain_avg_severity_primary_4():

    dates = ["2018-05-12", "2018-05-14", "2018-05-17", "2018-05-18"]
    severity = [2, 3, 1, 2]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (1.6 <= historic_soreness[0].average_severity <= 1.8)


def test_flag_acute_pain_avg_severity_primary_5():

    dates = ["2018-05-12", "2018-05-14", "2018-05-16"]
    severity = [3, 2, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (2.7 <= historic_soreness[0].average_severity <= 2.9)



def test_flag_acute_pain_avg_severity_primary_6():

    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18"]
    severity = [2, 3, 2, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (2.7 <= historic_soreness[0].average_severity <= 2.9)



def test_flag_acute_pain_avg_severity_corner_case_1():

    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18"]
    severity = [1, 1, 1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (4.3 <= historic_soreness[0].average_severity <= 4.8)



def test_flag_acute_pain_avg_severity_corner_case_2():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-15", "2018-05-18"]
    severity = [1, 1, 1, 1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (4.6 <= historic_soreness[0].average_severity <= 4.8)



def test_flag_acute_pain_avg_severity_corner_case_3():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-15", "2018-05-16"]
    severity = [1, 1, 1, 1, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (3.5 <= historic_soreness[0].average_severity <= 3.6)


def test_flag_acute_pain_avg_severity_corner_case_4():

    dates = ["2018-05-12", "2018-05-14", "2018-05-16", "2018-05-18"]
    severity = [5, 5, 5, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (1.4 <= historic_soreness[0].average_severity <= 1.6)


def test_flag_acute_pain_avg_severity_corner_case_5():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-15", "2018-05-16"]
    severity = [1, 2, 3, 4, 5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (4.2 <= historic_soreness[0].average_severity <= 4.5)


def test_flag_acute_pain_avg_severity_corner_case_6():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-15", "2018-05-16"]
    severity = [5, 4, 3, 2, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (1.5 <= historic_soreness[0].average_severity <= 1.6)


def test_flag_acute_pain_avg_severity_corner_case_7():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1, 1, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    # dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-18"]
    # severity = [1, 1, 1, 5]

    # soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, soreness_list, BodyPartLocation.achilles, 1, True, parse_date("2018-05-18"), 5)

    # historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, historic_soreness)

    assert (4.8 <= historic_soreness[0].average_severity <= 5.0)


def test_flag_acute_pain_avg_severity_corner_case_8():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [5, 1, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    # dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-18"]
    # severity = [5, 1, 1, 1]
    #
    # soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)
    #
    # stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, soreness_list,BodyPartLocation.achilles, 1, True, parse_date("2018-05-18"), 1)

    # historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, historic_soreness)

    assert (1.0 <= historic_soreness[0].average_severity <= 1.2)


def test_flag_acute_pain_avg_severity_corner_case_9():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [1, 1, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    # dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-18"]
    # severity = [1, 1, 3, 5]

    # soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    # stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, soreness_list,BodyPartLocation.achilles, 1, True, parse_date("2018-05-18"), 5)

    # historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, historic_soreness)

    assert (4.8 <= historic_soreness[0].average_severity <= 5.0)


def test_flag_acute_pain_avg_severity_corner_case_10():

    dates = ["2018-05-12", "2018-05-13", "2018-05-14"]
    severity = [5, 1, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    # dates = ["2018-05-12", "2018-05-13", "2018-05-14", "2018-05-18"]
    # severity = [5, 1, 3, 1]
    #
    # soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)
    #
    # stats_processing = StatsProcessing("tester", "2018-05-18", DatastoreCollection())

    historic_soreness = stats_processing.answer_acute_pain_question(historic_soreness, soreness_list, BodyPartLocation.achilles, 1, True, parse_date("2018-05-18"), 1)

    # historic_soreness = stats_processing.get_historic_soreness_list(soreness_list, historic_soreness)

    assert (1.0 <= historic_soreness[0].average_severity <= 1.3)


def test_flag_acute_pain_avg_severity_corner_case_11():

    dates = ["2018-05-14", "2018-05-15", "2018-05-16", "2018-05-18"]
    severity = [5, 1, 3, 1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (1.2 <= historic_soreness[0].average_severity <= 1.4)


def test_flag_acute_pain_avg_severity_corner_case_12():

    dates = ["2018-05-14", "2018-05-15", "2018-05-16"]
    severity = [5, 1, 3]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (2.5 <= historic_soreness[0].average_severity <= 2.7)


def test_flag_acute_pain_avg_severity_corner_case_13():

    dates = ["2018-05-12","2018-05-13","2018-05-14", "2018-05-15", "2018-05-16","2018-05-17","2018-05-18"]
    severity = [1,5,1,5,1,5,1]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (2.0 <= historic_soreness[0].average_severity <= 2.2)


def test_flag_acute_pain_avg_severity_corner_case_14():

    dates = ["2018-05-12","2018-05-13","2018-05-14", "2018-05-15", "2018-05-16","2018-05-17","2018-05-18"]
    severity = [5,1,5,1,5,1,5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (3.8 <= historic_soreness[0].average_severity <= 4.0)


def test_flag_acute_pain_avg_severity_corner_case_15():

    dates = ["2018-05-12","2018-05-14", "2018-05-16","2018-05-18"]
    severity = [5,5,5,5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (5.0 <= historic_soreness[0].average_severity <= 5.0)


def test_flag_acute_pain_avg_severity_corner_case_16():

    dates = ["2018-05-12","2018-05-14", "2018-05-16","2018-05-17","2018-05-18"]
    severity = [1,2,3,4,5]

    soreness_list = get_soreness_list(BodyPartLocation.achilles, 1, severity, True, dates)

    stats_processing = StatsProcessing("tester", parse_date("2018-05-18"), DatastoreCollection())

    historic_soreness = stats_processing.get_historic_soreness_list(soreness_list)

    assert (4.5 <= historic_soreness[0].average_severity <= 4.7)