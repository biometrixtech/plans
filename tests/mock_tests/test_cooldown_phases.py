from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from fathomapi.api.config import Config
Config.set('FILENAMES', {'exercise_library': 'exercise_library_fathom.json',
                           'body_part_mapping': 'body_part_mapping_fathom.json'})


import pytest
from datetime import datetime, timedelta
from utils import format_datetime, parse_datetime
from logic.trigger_processing import TriggerFactory
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation
from models.body_parts import BodyPart
from models.historic_soreness import HistoricSoreness
from models.modalities import CoolDown
from models.sport import SportName
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()

body_parts_1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def test_cooldown_check_soreness_severity_3():

    cooldown = CoolDown(True, False, False, event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.pain = False
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.high_relative_load_session_sport_names = [SportName.cycling]
        factory.high_relative_load_session = True
        factory.load_triggers()

        cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 0)

        assert len(cooldown.dynamic_stretch_exercises) > 0
        assert len(cooldown.dynamic_integrate_exercises) > 0

def test_cooldown_check_soreness_severity_3_pain():

    cooldown = CoolDown(True, False, False, event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.pain = True
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.high_relative_load_session_sport_names = [SportName.cycling]
        factory.high_relative_load_session = True
        factory.load_triggers()

        cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 3)

        assert len(cooldown.dynamic_stretch_exercises) == 0
        assert len(cooldown.dynamic_integrate_exercises) == 0

def test_cooldown_check_soreness_severity_3_no_high_volume():

    cooldown = CoolDown(False, False, False, event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        exercise_library = exercise_library_datastore.get()
        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.high_relative_load_session_sport_names = [SportName.cycling]
        factory.high_relative_load_session = True
        factory.load_triggers()

        cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 3)

        assert len(cooldown.dynamic_stretch_exercises) == 0
        assert len(cooldown.dynamic_integrate_exercises) == 0


def test_cooldown_check_soreness_severity_3_high_intensity():

    cooldown = CoolDown(False, True, False, event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.pain = False
        exercise_library = exercise_library_datastore.get()
        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.high_relative_load_session_sport_names = [SportName.cycling]
        factory.high_relative_load_session = True
        factory.load_triggers()

        cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 0)

        assert len(cooldown.dynamic_stretch_exercises) > 0
        assert len(cooldown.dynamic_integrate_exercises) > 0

def test_cooldown_check_soreness_severity_3_high_intensity_pain():

    cooldown = CoolDown(False, True, False, event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.pain = True
        exercise_library = exercise_library_datastore.get()
        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.high_relative_load_session_sport_names = [SportName.cycling]
        factory.high_relative_load_session = True
        factory.load_triggers()

        cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 3)

        assert len(cooldown.dynamic_stretch_exercises) == 0
        assert len(cooldown.dynamic_integrate_exercises)== 0


def test_cooldown_check_soreness_severity_3_muscular_strain():

    cooldown = CoolDown(False, False, True, event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        exercise_library = exercise_library_datastore.get()
        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.high_relative_load_session_sport_names = [SportName.cycling]
        factory.high_relative_load_session = True
        factory.load_triggers()

        cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 3)

        assert len(cooldown.dynamic_stretch_exercises) == 0
        assert len(cooldown.dynamic_integrate_exercises) == 0


def test_cooldown_check_soreness_severity_4():

    cooldown = CoolDown(True, False, False, event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 4
        soreness.side = 1
        exercise_library = exercise_library_datastore.get()
        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.high_relative_load_session_sport_names = [SportName.cycling]
        factory.high_relative_load_session = True
        factory.load_triggers()

        cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 4)

        assert len(cooldown.dynamic_stretch_exercises) == 0
        assert len(cooldown.dynamic_integrate_exercises) == 0


# def test_cooldown_check_corrective_soreness_severity_3():
#
#     current_date_time = datetime.today()
#     cooldown = CoolDown(True, False, False, event_date_time=current_date_time)
#
#     for b in body_parts_1:
#         soreness = Soreness()
#         soreness.body_part = BodyPart(BodyPartLocation(b), None)
#         soreness.severity = 3
#         soreness.side = 1
#         soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
#         historic_date_time = current_date_time - timedelta(days=31)
#         soreness.first_reported_date_time = historic_date_time
#         exercise_library = exercise_library_datastore.get()
#
#         factory = TriggerFactory(datetime.now(), None, [soreness], [])
#         factory.load_triggers()
#
#         for t in factory.triggers:
#             cooldown.check_corrective(t, current_date_time, exercise_library)
#
#         # dynamic stretch not ready yet
#         #assert len(cooldown.dynamic_stretch_exercises) > 0, 'Error with ' + str(BodyPartLocation(b))
#         # dynamic integrate not defined yet
#         #assert len(cooldown.dynamic_integrate_exercises) > 0
#
#
# def test_cooldown_check_corrective_soreness_severity_4():
#
#     current_date_time = datetime.today()
#     cooldown = CoolDown(True, False, False, event_date_time=current_date_time)
#
#     for b in body_parts_1:
#         soreness = Soreness()
#         soreness.body_part = BodyPart(BodyPartLocation(b), None)
#         soreness.severity = 4
#         soreness.side = 1
#         soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
#         historic_date_time = current_date_time - timedelta(days=31)
#         soreness.first_reported_date_time = historic_date_time
#         exercise_library = exercise_library_datastore.get()
#         factory = TriggerFactory(datetime.now(), None, [soreness], [])
#         factory.load_triggers()
#
#         for t in factory.triggers:
#             cooldown.check_corrective(t, current_date_time, exercise_library)
#
#         # dynamic stretch not ready yet
#         #assert len(cooldown.dynamic_stretch_exercises) == 0, 'Error with ' + str(BodyPartLocation(b))
#         #assert len(cooldown.dynamic_integrate_exercises) == 0, 'Error with ' + str(BodyPartLocation(b))
#
#
# def test_cooldown_check_corrective_pain_severity_3():
#
#     current_date_time = datetime.today()
#     cooldown = CoolDown(True, False, False, event_date_time=current_date_time)
#
#     for b in body_parts_1:
#         soreness = Soreness()
#         soreness.body_part = BodyPart(BodyPartLocation(b), None)
#         soreness.severity = 3
#         soreness.side = 1
#         soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
#         historic_date_time = current_date_time - timedelta(days=31)
#         soreness.first_reported_date_time = historic_date_time
#         exercise_library = exercise_library_datastore.get()
#         factory = TriggerFactory(datetime.now(), None, [soreness], [])
#         factory.load_triggers()
#
#         for t in factory.triggers:
#             cooldown.check_corrective(t, current_date_time, exercise_library)
#
#         # dynamic stretch not ready yet
#         #assert len(cooldown.dynamic_stretch_exercises) > 0, 'Error with ' + str(BodyPartLocation(b))
#         # dynamic integrate not defined yet
#         # assert len(cooldown.dynamic_integrate_exercises) > 0
#
#
# def test_cooldown_check_corrective_pain_severity_4():
#
#     current_date_time = datetime.today()
#     cooldown = CoolDown(True, False, False, event_date_time=current_date_time)
#
#     for b in body_parts_1:
#         soreness = Soreness()
#         soreness.body_part = BodyPart(BodyPartLocation(b), None)
#         soreness.severity = 4
#         soreness.side = 1
#         soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
#         historic_date_time = current_date_time - timedelta(days=31)
#         soreness.first_reported_date_time = historic_date_time
#         exercise_library = exercise_library_datastore.get()
#         factory = TriggerFactory(datetime.now(), None, [soreness], [])
#         factory.load_triggers()
#
#         for t in factory.triggers:
#             cooldown.check_corrective(t, current_date_time, exercise_library)

        # dynamic stretch not ready yet
        #assert len(cooldown.dynamic_stretch_exercises) == 0, 'Error with ' + str(BodyPartLocation(b))
        #assert len(cooldown.dynamic_integrate_exercises) == 0, 'Error with ' + str(BodyPartLocation(b))


def test_cooldown_check_recover_sport_high_volume_logged():

    current_date_time = datetime.today()
    cooldown = CoolDown(True, False, False, event_date_time=current_date_time)

    exercise_library = exercise_library_datastore.get()

    factory = TriggerFactory(datetime.now(), None, [], [])
    factory.high_relative_load_session_sport_names = [SportName.cycling]
    factory.high_relative_load_session = True
    factory.load_triggers()

    cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 0)

    assert len(cooldown.dynamic_stretch_exercises) > 0
    assert len(cooldown.dynamic_integrate_exercises) > 0


def test_cooldown_check_recover_sport_no_high_volume_logged():

    current_date_time = datetime.today()
    cooldown = CoolDown(False, False, False, event_date_time=current_date_time)

    exercise_library = exercise_library_datastore.get()

    factory = TriggerFactory(datetime.now(), None, [], [])
    factory.high_relative_load_session_sport_names = []
    factory.high_relative_load_session = False
    factory.load_triggers()

    cooldown.check_recover_from_sport(factory.triggers, factory.high_relative_load_session_sport_names, False, exercise_library, 0)

    assert len(cooldown.dynamic_stretch_exercises) == 0
    assert len(cooldown.dynamic_integrate_exercises) == 0