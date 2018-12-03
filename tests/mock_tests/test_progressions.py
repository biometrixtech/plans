import pytest
import logic.exercise_mapping as exercise_mapping
import models.session as session
import logic.soreness_processing as soreness_and_injury
import datetime
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from models.soreness import Soreness, BodyPart, BodyPartLocation, CompletedExerciseSummary

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


@pytest.fixture(scope="module")
def recovery_session(soreness_list, target_minutes):
    target_recovery_session = session.RecoverySession()
    target_recovery_session.set_exercise_target_minutes(soreness_list, target_minutes)
    return target_recovery_session


@pytest.fixture(scope="module")
def soreness_one_body_part(body_enum, severity_score, treatment_priority=1):
    soreness_list = []
    soreness_item = Soreness()
    soreness_item.severity = severity_score
    soreness_body_part = BodyPart(BodyPartLocation(body_enum), treatment_priority)
    soreness_item.body_part = soreness_body_part
    soreness_list.append(soreness_item)
    return soreness_list

def get_trigger_date_time():
    return datetime.datetime(2018, 7, 10, 2, 0, 0)


def test_first_progression_found():
    completed_exercises = []

    summary_1 = CompletedExerciseSummary("test_user", "10", 10)
    completed_exercises.append(summary_1)

    completed_exercise_datastore.side_load_completd_exercise_summaries(completed_exercises)

    calc = exercise_mapping.ExerciseAssignmentCalculator("test_user", exercise_library_datastore,
                                                         completed_exercise_datastore)
    soreness_list = soreness_one_body_part(12, 1)  # lower back
    target_recovery_session = recovery_session(soreness_one_body_part(12, 1), 15)
    exercise_assignments = calc.create_exercise_assignments(target_recovery_session, soreness_list,
                                                            get_trigger_date_time())
    assert "12" == exercise_assignments.activate_exercises[1].exercise.id


def test_next_progression_found():
    completed_exercises = []

    summary_1 = CompletedExerciseSummary("test_user", "10", 10)
    summary_2 = CompletedExerciseSummary("test_user", "12", 10)
    completed_exercises.append(summary_1)
    completed_exercises.append(summary_2)

    completed_exercise_datastore.side_load_completd_exercise_summaries(completed_exercises)

    calc = exercise_mapping.ExerciseAssignmentCalculator("test_user", exercise_library_datastore,
                                                         completed_exercise_datastore)
    soreness_list = soreness_one_body_part(12, 1)  # lower back
    target_recovery_session = recovery_session(soreness_one_body_part(12, 1), 15)
    exercise_assignments = calc.create_exercise_assignments(target_recovery_session, soreness_list,
                                                            get_trigger_date_time())
    assert "11" == exercise_assignments.activate_exercises[1].exercise.id

def test_last_progression_found():
    completed_exercises = []

    summary_1 = CompletedExerciseSummary("test_user", "10", 10)
    summary_2 = CompletedExerciseSummary("test_user", "12", 10)
    summary_3 = CompletedExerciseSummary("test_user", "11", 10)
    summary_4 = CompletedExerciseSummary("test_user", "13", 10)
    summary_5 = CompletedExerciseSummary("test_user", "120", 10)
    completed_exercises.append(summary_1)
    completed_exercises.append(summary_2)
    completed_exercises.append(summary_3)
    completed_exercises.append(summary_4)
    completed_exercises.append(summary_5)

    completed_exercise_datastore.side_load_completd_exercise_summaries(completed_exercises)

    calc = exercise_mapping.ExerciseAssignmentCalculator("test_user", exercise_library_datastore,
                                                         completed_exercise_datastore)
    soreness_list = soreness_one_body_part(12, 1)  # lower back
    target_recovery_session = recovery_session(soreness_one_body_part(12, 1), 15)
    exercise_assignments = calc.create_exercise_assignments(target_recovery_session, soreness_list,
                                                            get_trigger_date_time())
    assert "120" == exercise_assignments.activate_exercises[1].exercise.id

