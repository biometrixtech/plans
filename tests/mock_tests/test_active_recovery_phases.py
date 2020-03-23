import pytest
from datetime import datetime, timedelta
from models.soreness import Soreness
from models.soreness_base import BodyPartLocation
from models.body_parts import BodyPart
from logic.injury_risk_processing import InjuryRiskProcessor
from logic.exercise_assignment import ExerciseAssignment
from models.sport import SportName
from models.stats import AthleteStats
from models.session import SportTrainingSession
from models.exercise_phase import ExercisePhaseType
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()

body_parts_1 = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23]

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def get_session(event_date, rpe, duration_minutes, sport_name):
    session = SportTrainingSession()
    session.event_date = event_date
    session.session_RPE = rpe
    session.duration_minutes = duration_minutes
    session.sport_name = sport_name

    return session


def is_high_intensity_session(training_sessions):
    for session in training_sessions:
        if session.ultra_high_intensity_session() and session.high_intensity_RPE():
            return True
    return False


def test_active_recovery_check_soreness_severity_3():

    now_date = datetime.now()

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.side = 1
        soreness.sharp = 3
        soreness.reported_date_time = now_date

        session = get_session(datetime.today(), 8, 120, SportName.rowing)

        proc = InjuryRiskProcessor(now_date, [soreness], [session], {}, AthleteStats("tester"), "tester")
        injury_risk_dict = proc.process(aggregate_results=True)
        consolidated_injury_risk_dict = proc.get_consolidated_dict()

        calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore, now_date)
        calc.high_intensity_session = is_high_intensity_session([session])

        responsive_recovery = calc.get_responsive_recovery_modality("", ice_cwi=False)[0][0]

        assert ExercisePhaseType.dynamic_integrate == responsive_recovery.exercise_phases[0].type
        assert len(responsive_recovery.exercise_phases[0].exercises) > 0
        # for key, val in responsive_recovery.exercise_phases[0].exercises.items():
        #     print('exercise=' + key)
        #     for d in range(0, len(val.dosages)):
        #         print('priority=' + val.dosages[d].priority)
        #         print('ranking=' + str(val.dosages[d].ranking))


def test_active_recovery_check_no_soreness():

    now_date = datetime.now()

    session = get_session(datetime.today(), 8, 120, SportName.rowing)

    proc = InjuryRiskProcessor(now_date, [], [session], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore,
                              completed_exercise_datastore, now_date)
    calc.high_intensity_session = is_high_intensity_session([session])

    responsive_recovery = calc.get_responsive_recovery_modality("", ice_cwi=False)[0][0]

    assert ExercisePhaseType.dynamic_integrate == responsive_recovery.exercise_phases[0].type
    assert len(responsive_recovery.exercise_phases[0].exercises) > 0


def test_active_rest_check_no_high_intensity():

    now_date = datetime.now()

    session = get_session(datetime.today(), 8, 120, SportName.rowing)

    proc = InjuryRiskProcessor(now_date, [], [session], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore,
                              completed_exercise_datastore, now_date)
    #calc.high_intensity_session = is_high_intensity_session([session])

    responsive_recovery = calc.get_responsive_recovery_modality("", ice_cwi=False)[0][0]

    assert ExercisePhaseType.inhibit == responsive_recovery.exercise_phases[0].type
    assert len(responsive_recovery.exercise_phases[0].exercises) > 0


def test_active_rest_check_no_high_intensity_severity_3():

    now_date = datetime.now()

    for b in body_parts_1:
        soreness = Soreness()
        soreness.body_part = BodyPart(BodyPartLocation(b), None)
        soreness.side = 1
        soreness.sharp = 3
        soreness.reported_date_time = now_date

        session = get_session(datetime.today(), 8, 120, SportName.rowing)

        proc = InjuryRiskProcessor(now_date, [soreness], [session], {}, AthleteStats("tester"), "tester")
        injury_risk_dict = proc.process(aggregate_results=True)
        consolidated_injury_risk_dict = proc.get_consolidated_dict()

        calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore,
                                  completed_exercise_datastore, now_date)
        #calc.high_intensity_session = is_high_intensity_session([session])

        responsive_recovery = calc.get_responsive_recovery_modality("", ice_cwi=False)[0][0]

        assert ExercisePhaseType.inhibit == responsive_recovery.exercise_phases[0].type
        assert len(responsive_recovery.exercise_phases[0].exercises) > 0
