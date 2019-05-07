from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from datetime import datetime, timedelta
from utils import format_datetime, parse_datetime
from models.soreness import BodyPart, BodyPartLocation, HistoricSoreness, HistoricSorenessStatus, Soreness
from models.modalities import ActiveRestAfterTraining, ActiveRestBeforeTraining
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()

# post active rest


def test_active_rest_after_training_check_soreness_severity_3():

    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    active_rest.check_reactive_care_soreness(soreness, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_soreness_severity_4():

    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    active_rest.check_reactive_care_soreness(soreness, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_prevention_soreness_severity_2():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 2
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_soreness(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_check_prevention_soreness_severity_3():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_soreness(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_prevention_soreness_severity_4():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_soreness(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_prevention_pain_severity_2():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 2
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_pain(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_check_prevention_pain_severity_3():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_pain(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_prevention_pain_severity_4():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_pain(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_pain_severity_3():

    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.pain = True
    exercise_library = exercise_library_datastore.get()
    active_rest.check_reactive_care_pain(soreness, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_pain_severity_4():

    active_rest = ActiveRestAfterTraining(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.pain = True
    exercise_library = exercise_library_datastore.get()
    active_rest.check_reactive_care_pain(soreness, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


# pre active rest


def test_active_rest_before_training_check_soreness_severity_3():

    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    active_rest.check_reactive_care_soreness(soreness, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_soreness_severity_4():

    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    active_rest.check_reactive_care_soreness(soreness, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_prevention_soreness_severity_2():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 2
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_soreness(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_before_training_check_prevention_soreness_severity_3():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_soreness(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_befpre_training_check_prevention_soreness_severity_4():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_soreness(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_prevention_pain_severity_2():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 2
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_pain(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_before_training_check_prevention_pain_severity_3():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_pain(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_prevention_pain_severity_4():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    exercise_library = exercise_library_datastore.get()
    active_rest.check_prevention_pain(soreness, current_date_time, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_pain_severity_3():

    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.pain = True
    exercise_library = exercise_library_datastore.get()
    active_rest.check_reactive_care_pain(soreness, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_pain_severity_4():

    active_rest = ActiveRestBeforeTraining(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.pain = True
    exercise_library = exercise_library_datastore.get()
    active_rest.check_reactive_care_pain(soreness, exercise_library)

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


'''deprecated
def test_find_earlier_practice_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    practice_session = PracticeSession()
    practice_session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    practice_session_2 = PracticeSession()
    practice_session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.training_sessions.append(practice_session)
    daily_plan.training_sessions.append(practice_session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_practice_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    practice_session = PracticeSession()
    practice_session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    practice_session_2 = PracticeSession()
    practice_session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.training_sessions.append(practice_session)
    daily_plan.training_sessions.append(practice_session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)


def test_find_earlier_game_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    game_session = Game()
    game_session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    game_session_2 = Game()
    game_session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.training_sessions.append(game_session)
    daily_plan.training_sessions.append(game_session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_game_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    game_session = Game()
    game_session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    game_session_2 = Game()
    game_session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.training_sessions.append(game_session)
    daily_plan.training_sessions.append(game_session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)


def test_find_earlier_cross_training_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    session = StrengthConditioningSession()
    session.event_date = format_datetime(current_date_time - timedelta(hours=1))
    session_2 = StrengthConditioningSession()
    session_2.event_date = format_datetime(current_date_time - timedelta(hours=2))

    daily_plan.training_sessions.append(session)
    daily_plan.training_sessions.append(session_2)

    past_sessions = daily_plan.get_past_sessions(current_date_time)

    assert 2 is len(past_sessions)


def test_find_later_cross_training_sessions():

    daily_plan = create_no_soreness_plan()
    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(12, 0, 0))

    session = StrengthConditioningSession()
    session.event_date = format_datetime(current_date_time + timedelta(hours=1))
    session_2 = StrengthConditioningSession()
    session_2.event_date = format_datetime(current_date_time + timedelta(hours=2))

    daily_plan.training_sessions.append(session)
    daily_plan.training_sessions.append(session_2)

    future_sessions = daily_plan.get_future_sessions(current_date_time)

    assert 2 is len(future_sessions)
'''

