from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from fathomapi.api.config import Config
Config.set('FILENAMES', {'exercise_library': 'exercise_library_fathom.json',
                           'body_part_mapping': 'body_part_mapping_fathom.json'})

import pytest
from datetime import datetime, timedelta
from models.sport import SportName
from utils import format_datetime, parse_datetime
from logic.trigger_processing import TriggerFactory
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.body_parts import BodyPart
from models.goal import AthleteGoalType
from models.historic_soreness import HistoricSoreness
from models.modalities import ColdWaterImmersion, Ice, IceSession
from models.stats import AthleteStats
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
    soreness.first_reported_date_time = historic_date_time

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    heat_session = calc.get_heat()

    assert len(heat_session.body_parts) > 0


def test_get_ice_historic_soreness_no_soreness_today():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    soreness.pain = True
    soreness.daily = False

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.high_relative_intensity_session = True
    factory.high_relative_load_session_sport_names = [SportName.cycling]
    factory.eligible_for_high_load_trigger = True
    factory.load_triggers()  #re-run with new settings

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    #calc.high_relative_intensity_session = factory.high_relative_intensity_session

    ice_session = calc.get_ice()

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
    soreness.first_reported_date_time = historic_date_time
    soreness.daily = True
    soreness.pain = True

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    ice_session = calc.get_ice()

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
    soreness.first_reported_date_time = historic_date_time
    soreness.daily = False
    soreness.pain = True

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.high_relative_intensity_session = True
    factory.high_relative_load_session_sport_names = [SportName.cycling]
    factory.eligible_for_high_load_trigger = True
    factory.load_triggers()  #re-run with new settings

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)
    #calc.high_relative_intensity_session = True
    ice_session = calc.get_ice()

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

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    ice_session = calc.get_ice()

    assert ice_session is None


def test_get_ice_daily_pain():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    ice_session = calc.get_ice()

    assert len(ice_session.body_parts) > 0


def test_get_no_ice_daily_pain_severity_4():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    ice_session = calc.get_ice()

    assert ice_session is None


def test_get_ice_daily_pain_severity_4():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.shoulder, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    athlete_stats = AthleteStats("tester")
    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    ice_session = calc.get_ice()

    assert ice_session is not None


def test_get_cwi_daily_pain_severity_4():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    cwi = calc.get_cold_water_immersion()

    assert cwi is not None


def test_get_no_cwi_daily_pain_severity_4_upper_body():
    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.shoulder, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.daily = True
    soreness.pain = True

    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [soreness], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [soreness], current_date_time)

    cwi = calc.get_cold_water_immersion()

    assert cwi is None


def test_remove_lower_body_parts():

    cwi = ColdWaterImmersion()
    ice_session = IceSession()
    ice = Ice(BodyPartLocation.ankle, 1)
    ice_session.body_parts.append(ice)
    athlete_stats = AthleteStats("tester")

    factory = TriggerFactory(datetime.now(), None, [], [])
    factory.load_triggers()

    calc = ExerciseAssignmentCalculator(factory, exercise_library_datastore, completed_exercise_datastore, [],
                                        [], datetime.today())

    ice_session = calc.adjust_ice_session(ice_session, cwi)

    assert ice_session is None

