from models.load_stats import LoadStats
from models.session import MixedActivitySession
from models.training_volume import StandardErrorRange
from models.user_stats import UserStats
from logic.training_load_processing import TrainingLoadProcessing
from logic.user_stats_processing import UserStatsProcessing
from datetime import datetime, timedelta
from utils import format_date, format_datetime
from tests.mocks.mock_datastore_collection import DatastoreCollection
import pytz

def get_session_with_power_load_observed_value(session_event_date, observed_load_value):

    session = MixedActivitySession()
    session.event_date = session_event_date
    session.power_load = StandardErrorRange(observed_value=observed_load_value)
    session.rpe_load = StandardErrorRange(observed_value=observed_load_value)
    return session

def test_first_session_unknown_high_load():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    session_event_date = datetime.now().replace(tzinfo=pytz.utc)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True
    datastore_collection = DatastoreCollection()

    #user_stats_processing = UserStatsProcessing("tester",datetime.now().date(), datastore_collection)

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    session = get_session_with_power_load_observed_value(session_event_date, 100)
    training_load_processing.load_training_session_values([session], [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert training_load_processing.high_relative_load_score == 50

def test_several_sessions_high_load():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [0,1,3,5,8,9,10,14,15,17,19]
    tissue_loads = [200,150,125,130,140,135,110,100,90,110,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 100 == training_load_processing.high_relative_load_score

def test_several_sessions_high_load_2():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [0,1,3,5,8,9,10,14,15,17,19]
    tissue_loads = [175,150,125,130,140,135,110,100,90,110,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 70 == training_load_processing.high_relative_load_score

def test_sparse_sessions_mod_load():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [0,3,8,10,14,17]
    tissue_loads = [175,150,130,140,110,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 70 == training_load_processing.high_relative_load_score

def test_sparse_sessions_high_and_top():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [0,3,8,10,14,17]
    tissue_loads = [225,150,130,140,110,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 100 == training_load_processing.high_relative_load_score


def test_sparse_sessions_high_load_top():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [0,3,8,10,14,17]
    tissue_loads = [825,150,130,140,110,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 100 == training_load_processing.high_relative_load_score

def test_sparse_sessions_high_load_but_not_normal():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [0,3,8,10,14,17]
    tissue_loads = [325,350,130,140,110,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 50 == training_load_processing.high_relative_load_score

def test_very_sparse_sessions_mod_high_load():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [0,8,10,17]
    tissue_loads = [175,130,140,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 100 == training_load_processing.high_relative_load_score

def test_very_sparse_sessions_high_load():

    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [0,8,10,17]
    tissue_loads = [375,130,140,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 75 < training_load_processing.high_relative_load_score

def test_very_sparse_sessions_high_load_no_workout_last_day():

    #TODO this is indistinguishable from the workout today example
    start_date = format_date(datetime.now().date())
    end_date = format_date(datetime.now().date())
    time_deltas = [1,8,10,17]
    tissue_loads = [375,130,140,90]
    sessions = []
    for t in range(0,len(time_deltas)):
        session_event_date = (datetime.now()-timedelta(days=time_deltas[t])).replace(tzinfo=pytz.utc)
        session = get_session_with_power_load_observed_value(session_event_date, tissue_loads[t])
        sessions.append(session)
    load_stats = LoadStats()
    expected_weekly_workouts = 3
    user_stats = UserStats("tester")
    user_stats.eligible_for_high_load_trigger = True

    training_load_processing = TrainingLoadProcessing(start_date,end_date,load_stats,expected_weekly_workouts)

    training_load_processing.load_training_session_values(sessions, [], [])
    current_user_stats = training_load_processing.calc_training_load_metrics(user_stats)
    assert 50 == training_load_processing.high_relative_load_score
