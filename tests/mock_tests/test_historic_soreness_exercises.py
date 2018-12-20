import pytest
import logic.exercise_mapping as exercise_mapping
import models.session as session
from models.soreness import HistoricSorenessStatus
from pandas import DataFrame
import datetime

from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from models.soreness import Soreness, BodyPart, BodyPartLocation

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()
df = DataFrame()

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()

@pytest.fixture(scope="module")
def recovery_session(soreness_list, target_minutes, max_severity, historic_soreness_present=False,
                     functional_strength_active=False, is_active_prep=True):
    target_recovery_session = session.RecoverySession()
    target_recovery_session.set_exercise_target_minutes(soreness_list, target_minutes, max_severity,
                                                        historic_soreness_present=historic_soreness_present,
                                                        functional_strength_active=functional_strength_active,
                                                        is_active_prep=is_active_prep)
    return target_recovery_session


@pytest.fixture(scope="module")
def soreness_one_body_part(body_enum, severity_score, historic_soreness_status,treatment_priority=1):
    soreness_list = []
    soreness_item = Soreness()
    soreness_item.historic_soreness_status = historic_soreness_status
    soreness_item.severity = severity_score
    soreness_body_part = BodyPart(BodyPartLocation(body_enum),
                                                  treatment_priority)
    soreness_item.body_part = soreness_body_part
    soreness_list.append(soreness_item)
    return soreness_list

@pytest.fixture(scope="module")
def pain_one_body_part(body_enum, severity_score, historic_soreness_status, treatment_priority=1):
    soreness_list = []
    soreness_item = Soreness()
    soreness_item.historic_soreness_status = historic_soreness_status
    soreness_item.severity = severity_score
    soreness_item.pain = True
    soreness_body_part = BodyPart(BodyPartLocation(body_enum),
                                                  treatment_priority)
    soreness_item.body_part = soreness_body_part
    soreness_list.append(soreness_item)
    return soreness_list

def get_trigger_date_time():
    return datetime.datetime(2018, 7, 10, 2, 0, 0)


def is_status_pain(historic_soreness_status):

    if (historic_soreness_status == HistoricSorenessStatus.almost_acute_pain or
            historic_soreness_status == HistoricSorenessStatus.acute_pain or
            historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain or
            historic_soreness_status == HistoricSorenessStatus.persistent_pain or
            historic_soreness_status == HistoricSorenessStatus.almost_persistent_2_pain or
            historic_soreness_status == HistoricSorenessStatus.persistent_2_pain):
        return True
    else:
        return False


def convert_assigned_exercises(assigned_exercises):

    exercise_list = []

    for a in assigned_exercises:
        exercise_list.append(a.exercise.id)

    return exercise_list

def test_no_soreness_baseline_active_prep_no_fs():

    target_minutes = 15
    athlete_id = "tester"
    made_it_through = False

    max_severity = [1, 3, 5]
    fs_active = [False, True]
    is_active_prep = [False, True]
    is_pain = False
    body_parts = [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 18]

    historic_soreness_status = [HistoricSorenessStatus.dormant_cleared,
                                HistoricSorenessStatus.almost_acute_pain,
                                HistoricSorenessStatus.acute_pain,
                                HistoricSorenessStatus.almost_persistent_pain,
                                HistoricSorenessStatus.persistent_pain,
                                HistoricSorenessStatus.almost_persistent_2_pain_acute,
                                HistoricSorenessStatus.almost_persistent_2_pain,
                                HistoricSorenessStatus.persistent_2_pain,
                                HistoricSorenessStatus.almost_persistent_soreness,
                                HistoricSorenessStatus.persistent_soreness,
                                HistoricSorenessStatus.almost_persistent_2_soreness,
                                HistoricSorenessStatus.persistent_2_soreness]


    f = open('hs_status_plans.csv', 'w')
    line = ('is_active_prep,fs_active,BodyPart,is_pain,severity,hs_status,inhibit_target_minutes,' +
            'inhibit_max_percentage,inhibit_minutes,inhibit_percentage,inhibit_iterations,' +
            'inhibit_exercises,lengthen_target_minutes,lengthen_max_percentage,lengthen_minutes,' +
            'lengthen_percentage,lengthen_iterations,lengthen_exercises,activate_target_minutes,' +
            'activate_max_percentage,activate_minutes,activate_percentage,activate_iterations,' +
            'activate_exercises')
    f.write(line + '\n')

    for b in body_parts:
        for h in historic_soreness_status:
            for m in max_severity:
                if h != HistoricSorenessStatus.dormant_cleared:
                    is_pain = is_status_pain(h)
                    if not is_pain:
                        soreness_list = soreness_one_body_part(b, m, h)
                    else:
                        soreness_list = pain_one_body_part(b, m, h)
                    historic_soreness_present = True
                else:
                    soreness_list = []
                    historic_soreness_present = False
                for fs in fs_active:
                    for ap in is_active_prep:
                        recovery = recovery_session(soreness_list,
                                                    target_minutes,
                                                    m,
                                                    historic_soreness_present,
                                                    fs,
                                                    ap)
                        calc = exercise_mapping.ExerciseAssignmentCalculator(athlete_id,
                                                                             exercise_library_datastore,
                                                                             completed_exercise_datastore,
                                                                             historic_soreness_present)
                        exercise_assignments = calc.create_exercise_assignments(recovery, soreness_list,
                                                                                get_trigger_date_time(),
                                                                                target_minutes)
                        #line = ''
                        line = (str(ap)+',' + str(fs) + ',' + str(BodyPartLocation(b)) + ',' +
                                str(is_pain) + ',' + str(m) + ',' + str(h) + ',' +
                                str(round(exercise_assignments.inhibit_target_minutes if exercise_assignments.inhibit_target_minutes is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.inhibit_max_percentage if exercise_assignments.inhibit_max_percentage is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.inhibit_minutes, 2)) + ',' +
                                str(round(exercise_assignments.inhibit_percentage if exercise_assignments.inhibit_percentage is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.inhibit_iterations, 2)) + ',' +
                                ';'.join(convert_assigned_exercises(exercise_assignments.inhibit_exercises)) + ',' +

                                str(round(exercise_assignments.lengthen_target_minutes if exercise_assignments.lengthen_target_minutes is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.lengthen_max_percentage if exercise_assignments.lengthen_max_percentage is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.lengthen_minutes, 2)) + ',' +
                                str(round(exercise_assignments.lengthen_percentage if exercise_assignments.lengthen_percentage is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.lengthen_iterations, 2)) + ',' +
                                ';'.join(convert_assigned_exercises(exercise_assignments.lengthen_exercises)) + ',' +

                                str(round(exercise_assignments.activate_target_minutes if exercise_assignments.activate_target_minutes is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.activate_max_percentage if exercise_assignments.activate_max_percentage is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.activate_minutes, 2)) + ',' +
                                str(round(exercise_assignments.activate_percentage if exercise_assignments.activate_percentage is not None else 0, 2)) + ',' +
                                str(round(exercise_assignments.activate_iterations, 2)) + ',' +
                                ';'.join(convert_assigned_exercises(exercise_assignments.activate_exercises)))
                        f.write(line + '\n')
    f.close()

    made_it_through = True

    assert made_it_through is True