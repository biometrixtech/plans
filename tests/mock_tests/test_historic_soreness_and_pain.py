from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from models.soreness import BodyPart, BodyPartLocation, Soreness, HistoricSorenessStatus
from models.historic_soreness import HistoricSoreness
from logic.stats_processing import StatsProcessing
from tests.mocks.mock_datastore_collection import DatastoreCollection
from models.daily_readiness import DailyReadiness
from models.post_session_survey import PostSessionSurvey
from tests.mocks.mock_daily_readiness_datastore import DailyReadinessDatastore
from models.session import SessionType
from tests.testing_utilities import TestUtilities
from datetime import datetime, timedelta
from models.stats import AthleteStats
from utils import parse_date, format_date

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

    hs_dict, hs_dict_reported = stats_processing.get_hs_dictionary(soreness_list)

    assert(2 is len(hs_dict.keys()))


def test_consecutive_last_updated_2_days_with_break():

    readiness_list = []

    readiness_list.append(get_daily_readiness_survey_high_pain(datetime(2018, 7, 17, 11, 0, 0), 3))
    readiness_list.append(get_daily_readiness_survey_high_pain(datetime(2018, 7, 19, 11, 0, 0), 3))

    daily_readiness_datastore = DailyReadinessDatastore()
    daily_readiness_datastore.side_load_surveys(readiness_list)

    datastore_collection = DatastoreCollection()
    datastore_collection.daily_readiness_datastore = daily_readiness_datastore

    stats_processing = StatsProcessing("tester", parse_date("2018-07-19"), datastore_collection)

    stats_processing.set_start_end_times()
    stats_processing.update_start_times(readiness_list, [], [])
    stats_processing.latest_plan_date = parse_date("2018-07-18")
    stats_processing.acute_days = 7
    stats_processing.chronic_days = 28
    stats_processing.set_acute_chronic_periods()

    stats_processing.load_historical_readiness_surveys(readiness_list)
    # stats.load_historical_post_session_surveys([])
    soreness_list_25 = stats_processing.merge_soreness_from_surveys(
        stats_processing.get_readiness_soreness_list(stats_processing.last_25_days_readiness_surveys),
        stats_processing.get_ps_survey_soreness_list(stats_processing.last_25_days_ps_surveys)
    )

    consecutive_pain_list = stats_processing.get_historic_soreness_list(soreness_list_25)

    assert (datetime(2018, 7, 19, 11, 0) == consecutive_pain_list[0].last_reported_date_time)

def test_historical_soreness_trigger_update_almost_persistent_to_persistent():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-02")
    soreness = HistoricSoreness(BodyPartLocation(9), 1, True)
    soreness.historic_soreness_status = HistoricSorenessStatus.almost_persistent_pain
    soreness.streak = 2
    soreness.streak_start_date = parse_date("2018-12-01")
    soreness.average_severity = 2.0
    soreness.last_reported_date_time = parse_date("2018-12-02")
    athlete_stats.historic_soreness = [soreness]

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 3
    new_soreness.pain = True
    athlete_stats.update_historic_soreness(new_soreness, "2018-12-03")

    updated_soreness = athlete_stats.historic_soreness[0]

    assert updated_soreness.historic_soreness_status == HistoricSorenessStatus.persistent_pain
    assert updated_soreness.streak == 3
    assert updated_soreness.average_severity == 2.33


def test_historical_soreness_trigger_update_almost_persistent_to_persistent_2():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-02")
    soreness = HistoricSoreness(BodyPartLocation(9), 1, True)
    soreness.historic_soreness_status = HistoricSorenessStatus.almost_persistent_2_pain
    soreness.streak = 2
    soreness.streak_start_date = parse_date("2018-12-01")
    soreness.average_severity = 2.0
    soreness.last_reported_date_time = parse_date("2018-12-02")
    athlete_stats.historic_soreness = [soreness]

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 3
    new_soreness.pain = True
    athlete_stats.update_historic_soreness(new_soreness, "2018-12-03")

    updated_soreness = athlete_stats.historic_soreness[0]

    assert updated_soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain
    assert updated_soreness.streak == 3
    assert updated_soreness.average_severity == 2.33

def test_historical_soreness_trigger_update_almost_persistent_to_peristent_2_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-02")
    soreness = HistoricSoreness(BodyPartLocation(9), 1, False)
    soreness.historic_soreness_status = HistoricSorenessStatus.almost_persistent_2_soreness
    soreness.streak = 2
    soreness.streak_start_date = parse_date("2018-12-01")
    soreness.average_severity = 2.0
    soreness.last_reported_date_time = parse_date("2018-12-02")
    athlete_stats.historic_soreness = [soreness]

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 3
    new_soreness.pain = False
    athlete_stats.update_historic_soreness(new_soreness, "2018-12-03")

    updated_soreness = athlete_stats.historic_soreness[0]

    assert updated_soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness
    assert updated_soreness.streak == 3
    assert updated_soreness.average_severity == 2.33

def test_historical_soreness_trigger_update_same_day_pain():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")
    soreness = HistoricSoreness(BodyPartLocation(9), 1, True)
    soreness.historic_soreness_status = HistoricSorenessStatus.almost_persistent_2_pain
    soreness.streak = 2
    soreness.streak_start_date = parse_date("2018-12-01")
    soreness.average_severity = 2.0
    soreness.last_reported_date_time = parse_date("2018-12-03")
    athlete_stats.historic_soreness = [soreness]

    prev_soreness = Soreness()
    prev_soreness.side = 1
    prev_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    prev_soreness.severity = 3
    prev_soreness.pain = True
    prev_soreness.reported_date_time = parse_date("2018-12-03")
    athlete_stats.daily_severe_pain = [prev_soreness]
    athlete_stats.daily_severe_soreness = []

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 4
    new_soreness.pain = True
    athlete_stats.update_historic_soreness(new_soreness, parse_date("2018-12-03"))

    updated_soreness = athlete_stats.historic_soreness[0]

    assert updated_soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain
    assert updated_soreness.streak == 2
    assert updated_soreness.average_severity == 2.5


def test_historical_soreness_trigger_update_same_day_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")
    soreness = HistoricSoreness(BodyPartLocation(9), 1, False)
    soreness.historic_soreness_status = HistoricSorenessStatus.almost_persistent_2_pain
    soreness.streak = 2
    soreness.streak_start_date = parse_date("2018-12-01")
    soreness.average_severity = 3.0
    soreness.last_reported_date_time = parse_date("2018-12-03")
    athlete_stats.historic_soreness = [soreness]

    prev_soreness = Soreness()
    prev_soreness.side = 1
    prev_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    prev_soreness.severity = 3
    prev_soreness.pain = False
    prev_soreness.reported_date_time = parse_date("2018-12-03")
    athlete_stats.daily_severe_pain = [prev_soreness]
    athlete_stats.daily_severe_soreness = []

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 4
    new_soreness.pain = False
    athlete_stats.update_historic_soreness(new_soreness, parse_date("2018-12-03"))

    updated_soreness = athlete_stats.historic_soreness[0]

    assert updated_soreness.historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain
    assert updated_soreness.streak == 2
    assert updated_soreness.average_severity == 3.5


def test_historical_soreness_trigger_update_same_day_lower_severity():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")
    soreness = HistoricSoreness(BodyPartLocation(9), 1, True)
    soreness.historic_soreness_status = HistoricSorenessStatus.almost_persistent_2_pain
    soreness.streak = 2
    soreness.streak_start_date = parse_date("2018-12-01")
    soreness.average_severity = 2.0
    soreness.last_reported_date_time = parse_date("2018-12-02")
    athlete_stats.historic_soreness = [soreness]

    prev_soreness = Soreness()
    prev_soreness.side = 1
    prev_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    prev_soreness.severity = 3
    prev_soreness.pain = True
    athlete_stats.daily_severe_pain = [prev_soreness]
    athlete_stats.daily_severe_soreness = []

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.pain = True
    athlete_stats.update_historic_soreness(new_soreness, parse_date("2018-12-03"))

    updated_soreness = athlete_stats.historic_soreness[0]

    assert updated_soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain
    assert updated_soreness.streak == 3
    assert updated_soreness.average_severity == 2.0


def test_historical_soreness_trigger_update_same_day_no_hist():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.pain = False
    athlete_stats.update_historic_soreness(new_soreness, parse_date("2018-12-03"))

    assert len(athlete_stats.historic_soreness) == 0
