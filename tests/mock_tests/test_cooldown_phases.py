from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from datetime import datetime, timedelta
from utils import format_datetime, parse_datetime
from models.soreness import BodyPart, BodyPartLocation, Soreness, HistoricSorenessStatus
from models.historic_soreness import HistoricSoreness
from models.modalities import CoolDown
from models.sport import SportName
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def test_cooldown_check_soreness_severity_3():

    cooldown = CoolDown(True, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    cooldown.check_recover_from_sport([soreness], SportName.cycling, False, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) > 0
    assert len(cooldown.dynamic_integrate_exercises) > 0


def test_cooldown_check_soreness_severity_3_no_high_volume():

    cooldown = CoolDown(False, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    cooldown.check_recover_from_sport([soreness], SportName.cycling, False, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) == 0
    assert len(cooldown.dynamic_integrate_exercises) == 0


def test_cooldown_check_soreness_severity_3_high_intensity():

    cooldown = CoolDown(False, True, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    cooldown.check_recover_from_sport([soreness], SportName.cycling, False, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) > 0
    assert len(cooldown.dynamic_integrate_exercises) > 0


def test_cooldown_check_soreness_severity_3_muscular_strain():

    cooldown = CoolDown(False, False, True, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    cooldown.check_recover_from_sport([soreness], SportName.cycling, False, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) == 0
    assert len(cooldown.dynamic_integrate_exercises) == 0


def test_cooldown_check_soreness_severity_4():

    cooldown = CoolDown(True, False, False, event_date_time=datetime.today())

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 4
    soreness.side = 1
    exercise_library = exercise_library_datastore.get()
    cooldown.check_recover_from_sport([soreness], SportName.cycling, False, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) == 0
    assert len(cooldown.dynamic_integrate_exercises) == 0


def test_cooldown_check_corrective_soreness_severity_3():

    current_date_time = datetime.today()
    cooldown = CoolDown(True, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.lower_back, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    exercise_library = exercise_library_datastore.get()
    cooldown.check_corrective(soreness, current_date_time, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) > 0
    # dynamic integrate not defined yet
    # assert len(cooldown.dynamic_integrate_exercises) > 0


def test_cooldown_check_corrective_soreness_severity_4():

    current_date_time = datetime.today()
    cooldown = CoolDown(True, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.hip_flexor, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    exercise_library = exercise_library_datastore.get()
    cooldown.check_corrective(soreness, current_date_time, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) == 0
    assert len(cooldown.dynamic_integrate_exercises) == 0


def test_cooldown_check_corrective_pain_severity_3():

    current_date_time = datetime.today()
    cooldown = CoolDown(True, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.lower_back, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    exercise_library = exercise_library_datastore.get()
    cooldown.check_corrective(soreness, current_date_time, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) > 0
    # dynamic integrate not defined yet
    # assert len(cooldown.dynamic_integrate_exercises) > 0


def test_cooldown_check_corrective_pain_severity_4():

    current_date_time = datetime.today()
    cooldown = CoolDown(True, False, False, event_date_time=current_date_time)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.hip_flexor, None)
    soreness.severity = 4
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date_time = historic_date_time
    exercise_library = exercise_library_datastore.get()
    cooldown.check_corrective(soreness, current_date_time, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) == 0
    assert len(cooldown.dynamic_integrate_exercises) == 0


def test_cooldown_check_recover_sport_high_volume_logged():

    current_date_time = datetime.today()
    cooldown = CoolDown(True, False, False, event_date_time=current_date_time)

    exercise_library = exercise_library_datastore.get()
    cooldown.check_recover_from_sport([], SportName.cycling, False, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) > 0
    assert len(cooldown.dynamic_integrate_exercises) > 0


def test_cooldown_check_recover_sport_no_high_volume_logged():

    current_date_time = datetime.today()
    cooldown = CoolDown(False, False, False, event_date_time=current_date_time)

    exercise_library = exercise_library_datastore.get()
    cooldown.check_recover_from_sport([], SportName.cycling, False, exercise_library)

    assert len(cooldown.dynamic_stretch_exercises) == 0
    assert len(cooldown.dynamic_integrate_exercises) == 0