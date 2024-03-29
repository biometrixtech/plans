from models.chart_data import WorkoutChart, TrainingVolumeChart, BodyPartChartCollection, MuscularStrainChart, HighRelativeLoadChart, DOMSChart, BodyResponseChart
from utils import parse_date
from math import floor
from models.historic_soreness import HistoricSoreness, HistoricSeverity, SorenessCause
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.session import SessionType, HighLoadSession, SportTrainingSession, SessionSource
from models.sport import SportName
from models.stats import SportMaxLoad
from logic.stats_processing import StatsProcessing
from datetime import datetime, timedelta
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from tests.testing_utilities import TestUtilities
from models.post_session_survey import PostSurvey, PostSessionSurvey
from models.daily_readiness import DailyReadiness
from models.data_series import DataSeries
from models.load_stats import LoadStats
import random


def get_dates(start_date, days):

    dates = []

    for i in range(days + 1):
        if i % 2 == 0:
            dates.append(start_date + timedelta(days=i))

    return dates


def get_all_dates(start_date, days):

    dates = []

    for i in range(days + 1):
        dates.append(start_date + timedelta(days=i))

    return dates


def get_training_sessions(start_date, days):

    dates = get_all_dates(start_date, days)

    sessions = []

    for d in dates:
        session = SportTrainingSession()
        session.sport_name = SportName.basketball
        session.source = SessionSource.user
        session.event_date = d
        session.end_date = d
        session.session_RPE = 5
        session.duration_minutes = 90
        sessions.append(session)

    return sessions


def get_daily_readiness_surveys(start_date, historic_soreness_list, days, co_occurence_ratio):

    surveys = []

    dates = get_dates(start_date, days)

    factor = floor(co_occurence_ratio * len(dates))

    factor_goal = 0
    i = 0
    for d in dates:
        soreness_list = []
        part_list = 0
        for h in historic_soreness_list:
            if factor_goal >= factor and part_list > 0 and i % 2 == 0:
                pass
            else:
                soreness = TestUtilities().body_part_soreness(h.body_part_location.value, 1, h.side)
                soreness_list.append(soreness)
            factor_goal += 1
            part_list += 1
            i += 1
        daily_readiness = DailyReadiness(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", soreness_list, 4, 5)
        surveys.append(daily_readiness)

    return surveys


def get_post_session_surveys(start_date, historic_soreness_list, days, co_occurence_ratio, severity_list=[1]):

    surveys = []

    dates = get_dates(start_date, days)

    factor = floor(co_occurence_ratio * len(dates))

    factor_goal = 0
    i = 0
    for d in dates:
        soreness_list = []
        part_list = 0
        for h in historic_soreness_list:
            if factor_goal >= factor and part_list > 0 and i % 2 == 0:
                pass
            else:
                severity = random.choice(severity_list)
                soreness = TestUtilities().body_part_soreness(h.body_part_location.value, severity, h.side)
                soreness_list.append(soreness)
            factor_goal += 1
            part_list += 1
            i += 1

        post_survey = TestUtilities().get_post_survey(2, soreness_list)

        post_session = PostSessionSurvey(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", None, SessionType.sport_training, post_survey )
        surveys.append(post_session)

    return surveys


def get_symmetric_historic_soreness_list(body_part_location):

    historic_soreness_1 = HistoricSoreness(body_part_location, 1, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_soreness_1.average_severity = 4

    historic_soreness_2 = HistoricSoreness(body_part_location, 2, False)
    historic_soreness_2.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
    historic_soreness_2.average_severity = 3

    historic_soreness_list = [historic_soreness_1, historic_soreness_2]

    return historic_soreness_list


def get_doms_list():

    historic_soreness_1 = HistoricSoreness(BodyPartLocation.calves, 1, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.doms
    historic_soreness_1.average_severity = 3

    historic_soreness_2 = HistoricSoreness(BodyPartLocation.calves, 2, False)
    historic_soreness_2.historic_soreness_status = HistoricSorenessStatus.doms
    historic_soreness_2.average_severity = 2

    historic_soreness_list = [historic_soreness_1, historic_soreness_2]

    return historic_soreness_list


def get_asymmetric_historic_soreness_list(body_part_location_1, body_part_location_2):

    historic_soreness_1 = HistoricSoreness(body_part_location_1, 1, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_soreness

    historic_soreness_2 = HistoricSoreness(body_part_location_2, 2, False)
    historic_soreness_2.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness

    historic_soreness_list = [historic_soreness_1, historic_soreness_2]

    return historic_soreness_list


def get_single_historic_soreness(body_part_location):

    historic_soreness_1 = HistoricSoreness(body_part_location, 1, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_soreness

    historic_soreness_list = [historic_soreness_1]

    return historic_soreness_list


def test_14_days_empty_data():

    chart = TrainingVolumeChart(parse_date("2019-01-31"))

    chart_data = chart.get_output_list()

    assert len(chart_data) == 14
    assert chart_data[13].date == parse_date("2019-01-31").date()
    assert chart_data[0].date == parse_date("2019-01-18").date()


def test_muscular_strain_chart():

    muscular_strain = [DataSeries(parse_date("2019-01-01"), 50),
                       DataSeries(parse_date("2019-01-02"), 60),
                       DataSeries(parse_date("2019-01-06"), 70)]

    chart = MuscularStrainChart(parse_date("2019-01-10"))

    for m in muscular_strain:
        chart.add_muscular_strain(m)

    chart_data = chart.get_output_list()

    assert len(chart_data) == 14
    assert chart_data[8].value == 70


def test_high_relative_load_chart():
    high_load = [HighLoadSession(parse_date("2019-01-01"), SportName.cycling),
                 HighLoadSession(parse_date("2019-01-02"), SportName.basketball),
                 HighLoadSession(parse_date("2019-01-06"), SportName.basketball)]

    chart = HighRelativeLoadChart(parse_date("2019-01-10"))

    for m in high_load:
        chart.add_relative_load(m)

    chart_data = chart.get_output_list()

    assert len(chart_data) == 14
    assert chart_data[9].value is True
    assert chart_data[10].value is False


def test_doms_chart():

    base_date_time = datetime.now()

    acute_readiness_surveys = []
    acute_post_session_surveys = []
    chronic_readiness_surveys = []
    chronic_post_session_surveys = []
    historic_soreness_list = []

    datastore_collection = DatastoreCollection()
    athlete_stats_datastore = AthleteStatsDatastore()
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    stats_processing = StatsProcessing("test", base_date_time, datastore_collection)

    co_occurrence_ratio = 0.9

    doms_list = get_doms_list()

    historic_soreness_list.extend(get_symmetric_historic_soreness_list(BodyPartLocation.calves))

    acute_readiness_surveys.extend(get_daily_readiness_surveys(base_date_time - timedelta(days=7),
                                                               historic_soreness_list, 7, 1.00))
    chronic_readiness_surveys.extend(get_daily_readiness_surveys(base_date_time - timedelta(days=35),
                                                                 historic_soreness_list, 28, co_occurrence_ratio))
    acute_post_session_surveys.extend(get_post_session_surveys(base_date_time - timedelta(days=7),
                                                               historic_soreness_list, 7, 1.00,
                                                               severity_list=[4, 3, 2]))
    chronic_post_session_surveys.extend(get_post_session_surveys(base_date_time - timedelta(days=35),
                                                                 historic_soreness_list, 28, co_occurrence_ratio,
                                                                 severity_list=[4, 3, 2]))

    stats_processing.acute_readiness_surveys = acute_readiness_surveys
    stats_processing.chronic_readiness_surveys = chronic_readiness_surveys
    stats_processing.acute_post_session_surveys = acute_post_session_surveys
    stats_processing.chronic_post_session_surveys = chronic_post_session_surveys

    acute_surveys = stats_processing.merge_soreness_from_surveys(
        stats_processing.get_readiness_soreness_list(stats_processing.acute_readiness_surveys),
        stats_processing.get_ps_survey_soreness_list(stats_processing.acute_post_session_surveys), [])
    chronic_surveys = stats_processing.merge_soreness_from_surveys(
        stats_processing.get_readiness_soreness_list(stats_processing.chronic_readiness_surveys),
        stats_processing.get_ps_survey_soreness_list(stats_processing.chronic_post_session_surveys), [])
    all_soreness = []
    all_soreness.extend(acute_surveys)
    all_soreness.extend(chronic_surveys)

    chart = DOMSChart(base_date_time)

    chart.process_doms(doms_list, all_soreness)

    chart_data = chart.get_output_list()

    assert len(chart_data) == 14
    assert chart_data[11].value == 2.65
    assert chart_data[12].value == 1.75
    assert chart_data[13].value == 0


def test_body_part_collection():

    base_date_time = datetime.now()

    acute_readiness_surveys = []
    acute_post_session_surveys = []
    chronic_readiness_surveys = []
    chronic_post_session_surveys = []

    datastore_collection = DatastoreCollection()
    athlete_stats_datastore = AthleteStatsDatastore()
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    stats_processing = StatsProcessing("test", base_date_time, datastore_collection)

    co_occurrence_ratio = 0.9

    historic_soreness_list = []
    historic_soreness_list.extend(get_symmetric_historic_soreness_list(BodyPartLocation.calves))

    acute_readiness_surveys.extend(get_daily_readiness_surveys(base_date_time - timedelta(days=7),
                                                               historic_soreness_list, 7, 1.00))
    chronic_readiness_surveys.extend(get_daily_readiness_surveys(base_date_time - timedelta(days=35),
                                                                 historic_soreness_list, 28, co_occurrence_ratio))
    acute_post_session_surveys.extend(get_post_session_surveys(base_date_time - timedelta(days=7),
                                                               historic_soreness_list, 7, 1.00))
    chronic_post_session_surveys.extend(get_post_session_surveys(base_date_time - timedelta(days=35),
                                                                 historic_soreness_list, 28, co_occurrence_ratio))

    stats_processing.acute_readiness_surveys = acute_readiness_surveys
    stats_processing.chronic_readiness_surveys = chronic_readiness_surveys
    stats_processing.acute_post_session_surveys = acute_post_session_surveys
    stats_processing.chronic_post_session_surveys = chronic_post_session_surveys

    acute_surveys = stats_processing.merge_soreness_from_surveys(
        stats_processing.get_readiness_soreness_list(stats_processing.acute_readiness_surveys),
        stats_processing.get_ps_survey_soreness_list(stats_processing.acute_post_session_surveys), [])
    chronic_surveys = stats_processing.merge_soreness_from_surveys(
        stats_processing.get_readiness_soreness_list(stats_processing.chronic_readiness_surveys),
        stats_processing.get_ps_survey_soreness_list(stats_processing.chronic_post_session_surveys), [])
    all_soreness = []
    all_soreness.extend(acute_surveys)
    all_soreness.extend(chronic_surveys)

    body_part_chart_collection = BodyPartChartCollection(base_date_time)
    body_part_chart_collection.process_soreness_list(all_soreness)

    soreness_dictionary = body_part_chart_collection.get_soreness_dictionary()
    pain_dictionary = body_part_chart_collection.get_pain_dictionary()

    assert len(soreness_dictionary) > 0
    assert len(pain_dictionary) == 0


def test_body_response():

    base_date_time = datetime.now()

    acute_readiness_surveys = []
    acute_post_session_surveys = []
    chronic_readiness_surveys = []
    chronic_post_session_surveys = []

    datastore_collection = DatastoreCollection()
    athlete_stats_datastore = AthleteStatsDatastore()
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    stats_processing = StatsProcessing("test", base_date_time, datastore_collection)

    co_occurrence_ratio = 0.9

    historic_soreness_list = []
    historic_soreness_list.extend(get_symmetric_historic_soreness_list(BodyPartLocation.calves))

    acute_readiness_surveys.extend(get_daily_readiness_surveys(base_date_time - timedelta(days=7),
                                                               historic_soreness_list, 7, 1.00))
    chronic_readiness_surveys.extend(get_daily_readiness_surveys(base_date_time - timedelta(days=35),
                                                                 historic_soreness_list, 28, co_occurrence_ratio))
    acute_post_session_surveys.extend(get_post_session_surveys(base_date_time - timedelta(days=7),
                                                               historic_soreness_list, 7, 1.00))
    chronic_post_session_surveys.extend(get_post_session_surveys(base_date_time - timedelta(days=35),
                                                                 historic_soreness_list, 28, co_occurrence_ratio))

    stats_processing.acute_readiness_surveys = acute_readiness_surveys
    stats_processing.chronic_readiness_surveys = chronic_readiness_surveys
    stats_processing.acute_post_session_surveys = acute_post_session_surveys
    stats_processing.chronic_post_session_surveys = chronic_post_session_surveys

    acute_surveys = stats_processing.merge_soreness_from_surveys(
        stats_processing.get_readiness_soreness_list(stats_processing.acute_readiness_surveys),
        stats_processing.get_ps_survey_soreness_list(stats_processing.acute_post_session_surveys), [])
    chronic_surveys = stats_processing.merge_soreness_from_surveys(
        stats_processing.get_readiness_soreness_list(stats_processing.chronic_readiness_surveys),
        stats_processing.get_ps_survey_soreness_list(stats_processing.chronic_post_session_surveys), [])
    all_soreness = []
    all_soreness.extend(acute_surveys)
    all_soreness.extend(chronic_surveys)

    body_response_chart = BodyResponseChart(base_date_time)
    for s in all_soreness:
        body_response_chart.add_soreness(s)

    yesterday = (base_date_time - timedelta(days=1)).date()
    assert len(body_response_chart.data[base_date_time.date()].body_parts) == 0
    assert len(body_response_chart.data[yesterday].body_parts) == 2


def test_workload_new_user():

    base_date_time = datetime.now()

    start_date = base_date_time - timedelta(days=13)

    sessions = get_training_sessions(start_date, 13)

    workload_chart = WorkoutChart(base_date_time)

    load_stats = LoadStats()

    sport_max_load = {}

    growing_sessions = []

    for s in sessions:
        growing_sessions.append(s)
        load_stats.set_min_max_values(growing_sessions)
        training_load = s.training_load(load_stats)

        if s.sport_name.value in sport_max_load:
            if training_load.observed_value > sport_max_load[s.sport_name.value].load:
                sport_max_load[s.sport_name.value].load = training_load.observed_value
                sport_max_load[s.sport_name.value].event_date_time = s.event_date
                sport_max_load[s.sport_name.value].first_time_logged = False
        else:
            sport_max_load[s.sport_name.value] = SportMaxLoad(s.event_date, training_load.observed_value)
            sport_max_load[s.sport_name.value].first_time_logged = True
        workload_chart.add_training_volume(s, load_stats, sport_max_load)

    assert workload_chart.status == "Today's workout was 100% of your Basketball PR"

def test_workload_new_sport():

    base_date_time = datetime.now()

    start_date = base_date_time - timedelta(days=13)

    sessions = get_training_sessions(start_date, 13)

    workload_chart = WorkoutChart(base_date_time)

    load_stats = LoadStats()

    sport_max_load = {}

    growing_sessions = []

    session_count = 0

    for s in sessions:
        if session_count == 13:
            s.sport_name = SportName.cycling
        growing_sessions.append(s)
        load_stats.set_min_max_values(growing_sessions)
        training_load = s.training_load(load_stats)

        if s.sport_name.value in sport_max_load:
            if training_load.observed_value > sport_max_load[s.sport_name.value].load:
                sport_max_load[s.sport_name.value].load = training_load.observed_value
                sport_max_load[s.sport_name.value].event_date_time = s.event_date
                sport_max_load[s.sport_name.value].first_time_logged = False
        else:
            sport_max_load[s.sport_name.value] = SportMaxLoad(s.event_date, training_load.observed_value)
            sport_max_load[s.sport_name.value].first_time_logged = True
        workload_chart.add_training_volume(s, load_stats, sport_max_load)
        session_count += 1

    assert workload_chart.status == "First Cycling workout recorded!"


def test_workload_new_max():

    base_date_time = datetime.now()

    start_date = base_date_time - timedelta(days=13)

    sessions = get_training_sessions(start_date, 13)

    workload_chart = WorkoutChart(base_date_time)

    load_stats = LoadStats()

    sport_max_load = {}

    growing_sessions = []

    session_count = 0

    for s in sessions:
        if session_count == 12:
            s.sport_name = SportName.cycling
        if session_count == 13:
            s.sport_name = SportName.cycling
            s.duration_minutes = s.duration_minutes * 2
        growing_sessions.append(s)
        load_stats.set_min_max_values(growing_sessions)
        session_count += 1

    for s in sessions:
        training_load = s.training_load(load_stats)

        if s.sport_name.value in sport_max_load:
            if training_load.observed_value > sport_max_load[s.sport_name.value].load:
                sport_max_load[s.sport_name.value].load = training_load.observed_value
                sport_max_load[s.sport_name.value].event_date_time = s.event_date
            sport_max_load[s.sport_name.value].first_time_logged = False
        else:
            sport_max_load[s.sport_name.value] = SportMaxLoad(s.event_date, training_load.observed_value)
            sport_max_load[s.sport_name.value].first_time_logged = True
        workload_chart.add_training_volume(s, load_stats, sport_max_load)

    assert workload_chart.status == "You set a new personal record for Cycling load!"


