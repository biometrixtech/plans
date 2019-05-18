from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from math import floor
from models.historic_soreness import HistoricSoreness, HistoricSorenessStatus, HistoricSeverity
from models.session import SessionType
from models.soreness import BodyPartLocation
from logic.stats_processing import StatsProcessing
from datetime import datetime, timedelta
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from tests.testing_utilities import TestUtilities
from models.post_session_survey import PostSurvey, PostSessionSurvey
from models.daily_readiness import DailyReadiness


def get_dates(start_date, days):

    dates = []

    for i in range(days + 1):
        if i % 2 == 0:
            dates.append(start_date + timedelta(days=i))

    return dates


def get_daily_readiness_surveys(start_date, historic_soreness_list, days, co_occurence_ratio):

    surveys = []

    dates = get_dates(start_date, days)

    factor = floor(co_occurence_ratio * len(dates))

    factor_goal = 0
    for d in dates:
        soreness_list = []
        part_list = 0
        for h in historic_soreness_list:
            if factor_goal >= factor and part_list > 1:
                pass
            else:
                soreness = TestUtilities().body_part_soreness(h.body_part_location.value, 1, h.side)
                soreness_list.append(soreness)
            factor_goal += 1
            part_list += 1
        daily_readiness = DailyReadiness(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", soreness_list, 4, 5)
        surveys.append(daily_readiness)

    return surveys


def get_post_session_surveys(start_date, historic_soreness_list, days, co_occurence_ratio):

    surveys = []

    dates = get_dates(start_date, days)

    factor = floor(co_occurence_ratio * len(dates))

    factor_goal = 0

    for d in dates:
        soreness_list = []
        part_list = 0
        for h in historic_soreness_list:
            if factor_goal >= factor and part_list > 1:
                pass
            else:
                soreness = TestUtilities().body_part_soreness(h.body_part_location.value, 1, h.side)
                soreness_list.append(soreness)
            factor_goal += 1
            part_list += 1

        post_survey = TestUtilities().get_post_survey(2, soreness_list)

        post_session = PostSessionSurvey(d.strftime("%Y-%m-%dT%H:%M:%SZ"), "tester", None, SessionType.sport_training, post_survey )
        surveys.append(post_session)

    return surveys


def get_symmetric_historic_soreness_list(body_part_location):

    historic_soreness_1 = HistoricSoreness(body_part_location, 1, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_soreness

    historic_soreness_2 = HistoricSoreness(body_part_location, 2, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness

    historic_soreness_list = [historic_soreness_1, historic_soreness_2]

    return historic_soreness_list


def get_asymmetric_historic_soreness_list(body_part_location_1, body_part_location_2):

    historic_soreness_1 = HistoricSoreness(body_part_location_1, 1, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_soreness

    historic_soreness_2 = HistoricSoreness(body_part_location_2, 2, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness

    historic_soreness_list = [historic_soreness_1, historic_soreness_2]

    return historic_soreness_list


def get_single_historic_soreness(body_part_location):

    historic_soreness_1 = HistoricSoreness(body_part_location, 1, False)
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_soreness

    historic_soreness_list = [historic_soreness_1]

    return historic_soreness_list


def test_symmetric_muscle_groups():

    base_date_time = datetime.now()

    acute_readiness_surveys = []
    acute_post_session_surveys = []
    chronic_readiness_surveys = []
    chronic_post_session_surveys = []

    datastore_collection = DatastoreCollection()
    athlete_stats_datastore = AthleteStatsDatastore()
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    stats_processing = StatsProcessing("test", base_date_time, datastore_collection)

    co_occurrence_ratio = 0.80

    historic_soreness_list = []
    historic_soreness_list.extend(get_symmetric_historic_soreness_list(BodyPartLocation.calves))

    acute_readiness_surveys.extend(get_daily_readiness_surveys(base_date_time - timedelta(days=7),
                                                               historic_soreness_list, 7, co_occurrence_ratio))
    chronic_readiness_surveys.extend(get_daily_readiness_surveys(base_date_time - timedelta(days=35),
                                                                 historic_soreness_list, 28, co_occurrence_ratio))
    acute_post_session_surveys.extend(get_post_session_surveys(base_date_time - timedelta(days=7),
                                                               historic_soreness_list, 7, co_occurrence_ratio))
    chronic_post_session_surveys.extend(get_post_session_surveys(base_date_time - timedelta(days=35),
                                                                 historic_soreness_list, 28, co_occurrence_ratio))

    stats_processing.acute_readiness_surveys = acute_readiness_surveys
    stats_processing.chronic_readiness_surveys = chronic_readiness_surveys
    stats_processing.acute_post_session_surveys = acute_post_session_surveys
    stats_processing.chronic_post_session_surveys = chronic_post_session_surveys

    historic_soreness_list = stats_processing.add_soreness_cause(historic_soreness_list)

    assert historic_soreness_list is not None