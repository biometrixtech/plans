from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from datetime import datetime, timedelta
from utils import format_datetime, parse_datetime
from models.soreness import AthleteGoalType, BodyPart, BodyPartLocation, HistoricSoreness, HistoricSorenessStatus, Soreness
from models.modalities import ColdWaterImmersion, Ice, IceSession
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from logic.exercise_mapping import ExerciseAssignmentCalculator
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


def test_get_heat():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    heat_session = calc.get_heat([soreness], current_date_time)

    assert len(heat_session.body_parts) > 0


def test_get_ice_historic_soreness_no_soreness_today():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    soreness.daily = False

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    ice_session = calc.get_ice([soreness], current_date_time)

    assert len(ice_session.body_parts) > 0
    for g in ice_session.body_parts[0].goals:
        assert g.goal_type == AthleteGoalType.preempt_corrective


def test_get_ice_historic_soreness_pain_today():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    soreness.daily = True
    soreness.pain = True

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    ice_session = calc.get_ice([soreness], current_date_time)

    assert len(ice_session.body_parts) > 0
    for g in ice_session.body_parts[0].goals:
        assert g.goal_type == AthleteGoalType.pain


def test_get_ice_historic_soreness_no_pain_today():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time
    soreness.daily = False
    soreness.pain = True

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    ice_session = calc.get_ice([soreness], current_date_time)

    assert len(ice_session.body_parts) > 0
    for g in ice_session.body_parts[0].goals:
        assert g.goal_type == AthleteGoalType.preempt_corrective


def test_get_no_ice_daily_soreness():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.daily = True

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    ice_session = calc.get_ice([soreness], current_date_time)

    assert ice_session is None


def test_get_ice_daily_pain():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    ice_session = calc.get_ice([soreness], current_date_time)

    assert len(ice_session.body_parts) > 0


def test_get_no_ice_daily_pain_severity_4():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    ice_session = calc.get_ice([soreness], current_date_time)

    assert ice_session is None


def test_get_ice_daily_pain_severity_4():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.shoulder, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    ice_session = calc.get_ice([soreness], current_date_time)

    assert ice_session is not None


def test_get_cwi_daily_pain_severity_4():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    cwi = calc.get_cold_water_immersion([soreness], current_date_time)

    assert cwi is not None


def test_get_no_cwi_daily_pain_severity_4_upper_body():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.shoulder, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    cwi = calc.get_cold_water_immersion([soreness], current_date_time)

    assert cwi is None


def test_remove_lower_body_parts():

    cwi = ColdWaterImmersion()
    ice_session = IceSession()
    ice = Ice(BodyPartLocation.ankle, 1)
    ice_session.body_parts.append(ice)
    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)
    ice_session = calc.adjust_ice_session(ice_session, cwi)

    assert ice_session is None

