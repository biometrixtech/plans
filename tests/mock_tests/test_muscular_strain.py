# from aws_xray_sdk.core import xray_recorder
# xray_recorder.configure(sampling=False)
# xray_recorder.begin_segment(name="test")
from datetime import datetime, timedelta
from models.session import SportTrainingSession
from models.historic_soreness import HistoricSoreness, SorenessCause
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.stats import AthleteStats
from tests.mocks.mock_datastore_collection import DatastoreCollection
from tests.mocks.mock_athlete_stats_datastore import AthleteStatsDatastore
from logic.stats_processing import StatsProcessing
from models.sport import SportName
from models.load_stats import LoadStats


def get_dates(start_date, days):

    dates = []

    for i in range(days + 1):
        if i % 2 == 0:
            dates.append(start_date + timedelta(days=i))

    return dates


def get_training_sessions(start_date, days):

    dates = get_dates(start_date, days)

    training_sessions = []

    for d in dates:
        session = SportTrainingSession()
        session.sport_name = SportName.basketball
        session.session_RPE = 2
        session.event_date = d
        session.duration_minutes = 100
        training_sessions.append(session)

    return training_sessions


def test_no_maintenance_load_overloading():

    base_date = datetime.now()

    training_sessions = get_training_sessions(base_date - timedelta(days=14), 14)

    historic_soreness_list = []
    historic_soreness_1 = HistoricSoreness(BodyPartLocation.calves, 1, False)
    historic_soreness_1.first_reported_date_time = base_date-timedelta(days=20)
    historic_soreness_1.last_reported_date_time = base_date
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
    historic_soreness_1.cause = SorenessCause.overloading
    historic_soreness_list.append(historic_soreness_1)

    datastore_collection = DatastoreCollection()
    athlete_stats_datastore = AthleteStatsDatastore()
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    stats_processing = StatsProcessing("test", base_date, datastore_collection)

    athlete_stats = AthleteStats("tester")
    athlete_stats.historic_soreness = historic_soreness_list
    athlete_stats.load_stats = LoadStats()

    muscular_strain = stats_processing.get_muscular_strain(athlete_stats, [], training_sessions)

    assert muscular_strain.value == 0.0


def test_no_overloading():

    base_date = datetime.now()

    training_sessions = get_training_sessions(base_date - timedelta(days=14), 14)

    historic_soreness_list = []
    historic_soreness_1 = HistoricSoreness(BodyPartLocation.calves, 1, False)
    historic_soreness_1.first_reported_date_time = base_date-timedelta(days=20)
    historic_soreness_1.last_reported_date_time = base_date
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
    historic_soreness_1.cause = SorenessCause.dysfunction
    historic_soreness_list.append(historic_soreness_1)

    datastore_collection = DatastoreCollection()
    athlete_stats_datastore = AthleteStatsDatastore()
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    stats_processing = StatsProcessing("test", base_date, datastore_collection)

    athlete_stats = AthleteStats("tester")
    athlete_stats.historic_soreness = historic_soreness_list
    athlete_stats.load_stats = LoadStats()

    muscular_strain = stats_processing.get_muscular_strain(athlete_stats, [], training_sessions)

    assert muscular_strain.value == 100.0


def test_maintenance_load_overloading():

    base_date = datetime.now()

    training_sessions = get_training_sessions(base_date - timedelta(days=14), 14)

    maintenance_session = SportTrainingSession()
    maintenance_session.sport_name = SportName.volleyball
    maintenance_session.session_RPE = 1
    maintenance_session.duration_minutes = 200
    maintenance_session.event_date = base_date - timedelta(days=1)

    training_sessions.append(maintenance_session)

    historic_soreness_list = []
    historic_soreness_1 = HistoricSoreness(BodyPartLocation.calves, 1, False)
    historic_soreness_1.first_reported_date_time = base_date-timedelta(days=20)
    historic_soreness_1.last_reported_date_time = base_date
    historic_soreness_1.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
    historic_soreness_1.cause = SorenessCause.overloading
    historic_soreness_list.append(historic_soreness_1)

    datastore_collection = DatastoreCollection()
    athlete_stats_datastore = AthleteStatsDatastore()
    datastore_collection.athlete_stats_datastore = athlete_stats_datastore

    stats_processing = StatsProcessing("test", base_date, datastore_collection)

    athlete_stats = AthleteStats("tester")
    athlete_stats.historic_soreness = historic_soreness_list
    athlete_stats.load_stats = LoadStats()

    muscular_strain = stats_processing.get_muscular_strain(athlete_stats, [], training_sessions)

    assert round(muscular_strain.value, 2) == (100 - 88.89)