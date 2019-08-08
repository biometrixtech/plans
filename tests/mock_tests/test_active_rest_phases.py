from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from datetime import datetime, timedelta
from utils import format_datetime, parse_datetime
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus
from models.body_parts import BodyPart, BodyPartLocation
#from models.historic_soreness import HistoricSoreness
from models.modalities import ActiveRestAfterTraining, ActiveRestBeforeTraining
from logic.trigger_processing import TriggerFactory
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()

body_parts_1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()

# post active rest


def test_active_rest_after_training_check_soreness_severity_3():

    active_rest = ActiveRestAfterTraining(event_date_time=datetime.today())

    for b in body_parts_1:

        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_reactive_care_soreness(t, exercise_library, 3)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.isolated_activate_exercises) == 0
        assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_soreness_severity_4():

    active_rest = ActiveRestAfterTraining(event_date_time=datetime.today())

    for b in body_parts_1:

        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 4
        soreness.side = 1
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_reactive_care_soreness(t, exercise_library, 4)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) == 0
        assert len(active_rest.isolated_activate_exercises) == 0
        assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_prevention_soreness_severity_2():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(event_date_time=current_date_time)

    for b in body_parts_1:

        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 2
        soreness.side = 1
        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
        historic_date_time = current_date_time - timedelta(days=31)
        soreness.first_reported_date_time = historic_date_time
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_corrective_soreness(t, current_date_time, exercise_library, 2)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.isolated_activate_exercises) > 0
        assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_check_prevention_soreness_severity_3():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(event_date_time=current_date_time)

    for b in body_parts_1:

        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
        historic_date_time = current_date_time - timedelta(days=31)
        soreness.first_reported_date_time = historic_date_time
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_corrective_soreness(t, current_date_time, exercise_library, 2)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.isolated_activate_exercises) > 0
        assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_check_prevention_pain_severity_2():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(event_date_time=current_date_time)

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 2
        soreness.side = 1
        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
        historic_date_time = current_date_time - timedelta(days=31)
        soreness.first_reported_date_time = historic_date_time
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_corrective_pain(t, current_date_time, exercise_library, 2)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.isolated_activate_exercises) > 0
        assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_check_prevention_pain_severity_3():

    current_date_time = datetime.today()
    active_rest = ActiveRestAfterTraining(event_date_time=current_date_time)

    for b in body_parts_1:

        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
        historic_date_time = current_date_time - timedelta(days=31)
        soreness.first_reported_date_time = historic_date_time
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_corrective_pain(t, current_date_time, exercise_library, 2)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.isolated_activate_exercises) > 0
        assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_check_pain_severity_3():

    active_rest = ActiveRestAfterTraining(event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.pain = True
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_reactive_care_pain(t, exercise_library, 3)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.isolated_activate_exercises) == 0
        assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_check_pain_severity_4():

    active_rest = ActiveRestAfterTraining(event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 4
        soreness.side = 1
        soreness.pain = True
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_reactive_care_pain(t, exercise_library, 4)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) == 0
        assert len(active_rest.isolated_activate_exercises) == 0
        assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_empty_soreness_blank():

    active_rest = ActiveRestAfterTraining(event_date_time=datetime.today())

    exercise_library = exercise_library_datastore.get()
    active_rest.fill_exercises([], exercise_library, False, False, False, [])

    assert len(active_rest.inhibit_exercises) == 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_none_soreness_blank():

    active_rest = ActiveRestAfterTraining(event_date_time=datetime.today())

    exercise_library = exercise_library_datastore.get()
    active_rest.fill_exercises(None, exercise_library, False, False, False, [])

    assert len(active_rest.inhibit_exercises) == 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_after_training_empty_soreness_force_data():
    active_rest = ActiveRestAfterTraining(event_date_time=datetime.today(), force_data=True)

    exercise_library = exercise_library_datastore.get()
    active_rest.fill_exercises([], exercise_library, False, False, False, [])

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_after_training_none_soreness_force_data():
    active_rest = ActiveRestAfterTraining(event_date_time=datetime.today(), force_data=True)

    exercise_library = exercise_library_datastore.get()
    active_rest.fill_exercises(None, exercise_library, False, False, False, [])

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) > 0

# pre active rest


def test_active_rest_before_training_check_soreness_severity_3():

    active_rest = ActiveRestBeforeTraining(event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_reactive_care_soreness(t, exercise_library, 3)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.active_stretch_exercises) > 0
        assert len(active_rest.isolated_activate_exercises) == 0
        assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_soreness_severity_4():

    active_rest = ActiveRestBeforeTraining(event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 4
        soreness.side = 1
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_reactive_care_soreness(t, exercise_library, 4)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) == 0
        assert len(active_rest.active_stretch_exercises) == 0
        assert len(active_rest.isolated_activate_exercises) == 0
        assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_prevention_soreness_severity_2():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(event_date_time=current_date_time)

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 2
        soreness.side = 1
        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
        historic_date_time = current_date_time - timedelta(days=31)
        soreness.first_reported_date_time = historic_date_time
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_corrective_soreness(t, current_date_time, exercise_library, 2)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.active_stretch_exercises) == 0
        assert len(active_rest.isolated_activate_exercises) > 0
        assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_before_training_check_prevention_soreness_severity_3():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(event_date_time=current_date_time)

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
        historic_date_time = current_date_time - timedelta(days=31)
        soreness.first_reported_date_time = historic_date_time
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_corrective_soreness(t, current_date_time, exercise_library, 2)

        assert len(active_rest.inhibit_exercises) > 0, 'Error with ' + str(BodyPartLocation(b))
        assert len(active_rest.static_stretch_exercises) > 0, 'Error with ' + str(BodyPartLocation(b))
        assert len(active_rest.active_stretch_exercises) == 0, 'Error with ' + str(BodyPartLocation(b))
        assert len(active_rest.isolated_activate_exercises) > 0, 'Error with ' + str(BodyPartLocation(b))
        assert len(active_rest.static_integrate_exercises) > 0, 'Error with ' + str(BodyPartLocation(b))


def test_active_rest_before_training_check_prevention_pain_severity_2():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(event_date_time=current_date_time)

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 2
        soreness.side = 1
        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
        historic_date_time = current_date_time - timedelta(days=31)
        soreness.first_reported_date_time = historic_date_time
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_corrective_pain(t, current_date_time, exercise_library, 2)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.active_stretch_exercises) == 0
        assert len(active_rest.isolated_activate_exercises) > 0
        assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_before_training_check_prevention_pain_severity_3():

    current_date_time = datetime.today()
    active_rest = ActiveRestBeforeTraining(event_date_time=current_date_time)

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
        historic_date_time = current_date_time - timedelta(days=31)
        soreness.first_reported_date_time = historic_date_time
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_corrective_pain(t, current_date_time, exercise_library, 2)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.active_stretch_exercises) == 0
        assert len(active_rest.isolated_activate_exercises) > 0
        assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_before_training_check_pain_severity_3():

    active_rest = ActiveRestBeforeTraining(event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 3
        soreness.side = 1
        soreness.pain = True
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_reactive_care_pain(t, exercise_library, 3)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) > 0
        assert len(active_rest.active_stretch_exercises) > 0
        assert len(active_rest.isolated_activate_exercises) == 0
        assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_check_pain_severity_4():

    active_rest = ActiveRestBeforeTraining(event_date_time=datetime.today())

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.severity = 4
        soreness.side = 1
        soreness.pain = True
        exercise_library = exercise_library_datastore.get()

        factory = TriggerFactory(datetime.now(), None, [soreness], [])
        factory.load_triggers()

        for t in factory.triggers:
            active_rest.check_reactive_care_pain(t, exercise_library, 4)

        assert len(active_rest.inhibit_exercises) > 0
        assert len(active_rest.static_stretch_exercises) == 0
        assert len(active_rest.active_stretch_exercises) == 0
        assert len(active_rest.isolated_activate_exercises) == 0
        assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_empty_soreness_blank():

    active_rest = ActiveRestBeforeTraining(event_date_time=datetime.today())

    exercise_library = exercise_library_datastore.get()
    active_rest.fill_exercises([], exercise_library, False, False, False, [])

    assert len(active_rest.inhibit_exercises) == 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.active_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_none_soreness_blank():

    active_rest = ActiveRestBeforeTraining(event_date_time=datetime.today())

    exercise_library = exercise_library_datastore.get()
    active_rest.fill_exercises(None, exercise_library, False, False, False, [])

    assert len(active_rest.inhibit_exercises) == 0
    assert len(active_rest.static_stretch_exercises) == 0
    assert len(active_rest.active_stretch_exercises) == 0
    assert len(active_rest.isolated_activate_exercises) == 0
    assert len(active_rest.static_integrate_exercises) == 0


def test_active_rest_before_training_empty_soreness_force_data():
    active_rest = ActiveRestBeforeTraining(event_date_time=datetime.today(), force_data=True)

    exercise_library = exercise_library_datastore.get()
    active_rest.fill_exercises([], exercise_library, False, False, False, [])

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.active_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) > 0


def test_active_rest_before_training_none_soreness_force_data():
    active_rest = ActiveRestBeforeTraining(event_date_time=datetime.today(), force_data=True)

    exercise_library = exercise_library_datastore.get()
    active_rest.fill_exercises(None, exercise_library, False, False, False, [])

    assert len(active_rest.inhibit_exercises) > 0
    assert len(active_rest.static_stretch_exercises) > 0
    assert len(active_rest.active_stretch_exercises) > 0
    assert len(active_rest.isolated_activate_exercises) > 0
    assert len(active_rest.static_integrate_exercises) > 0




