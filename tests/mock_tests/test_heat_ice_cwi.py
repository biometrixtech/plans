from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from datetime import datetime, timedelta
from utils import format_datetime, parse_datetime
from models.soreness import BodyPart, BodyPartLocation, HistoricSoreness, HistoricSorenessStatus, Soreness
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


def test_get_ice_historic_soreness():

    current_date_time = datetime.today()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation.ankle, None)
    soreness.severity = 3
    soreness.side = 1
    soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
    historic_date_time = current_date_time - timedelta(days=31)
    soreness.first_reported_date = historic_date_time

    calc = ExerciseAssignmentCalculator("tester", exercise_library_datastore, completed_exercise_datastore, False)

    ice_session = calc.get_ice([soreness], current_date_time)

    assert len(ice_session.body_parts) > 0