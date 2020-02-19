
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from models.session import SportTrainingSession, MixedActivitySession
from datetime import datetime, timedelta
from models.sport import SportName
from models.functional_movement import ActivityFunctionalMovementFactory, FunctionalMovementFactory, BodyPartFunctionalMovement, SessionFunctionalMovement
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation, BodyPartSide
from models.stats import AthleteStats
from logic.injury_risk_processing import InjuryRiskProcessor
from logic.functional_exercise_mapping import ExerciseAssignmentCalculator
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from models.movement_tags import AdaptationType
from models.movement_actions import MuscleAction, ExerciseAction, PrioritizedJointAction
from models.workout_program import WorkoutProgramModule, WorkoutSection, WorkoutExercise
from models.functional_movement_type import FunctionalMovementType

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def get_sessions(dates, rpes, durations, sport_names):

    if len(dates) != len(rpes) != len(durations) != len(sport_names):
        raise Exception("dates, rpes, durations must match in length")

    sessions = []

    for d in range(0, len(dates)):
        session = SportTrainingSession()
        session.event_date = dates[d]
        session.session_RPE = rpes[d]
        session.duration_minutes = durations[d]
        session.sport_name = sport_names[d]
        sessions.append(session)

    return sessions

def test_create_plan_no_session():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.sharp = 3
    soreness.reported_date_time = now_date

    proc = InjuryRiskProcessor (now_date, [soreness], [], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignmentCalculator(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore, now_date)

    active_rest = calc.get_pre_active_rest()[0]
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert len(active_rest.exercise_phases[2].exercises) > 0

    # assert len(active_rest[0].inhibit_exercises) > 0
    # assert len(active_rest[0].static_stretch_exercises) > 0
    # assert len(active_rest[0].active_stretch_exercises) > 0

def test_create_plan_with_session():

    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.tight = 1
    soreness.reported_date_time = dates[0]

    soreness_2 = Soreness()
    soreness_2.body_part = BodyPart(BodyPartLocation(7), None)
    soreness_2.side = 1
    soreness_2.sharp = 2
    soreness_2.reported_date_time = dates[0]

    proc = InjuryRiskProcessor(dates[0], [soreness, soreness_2], sessions, {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignmentCalculator(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        dates[0])

    active_rest = calc.get_pre_active_rest()[0]
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert len(active_rest.exercise_phases[2].exercises) > 0

    # assert len(active_rest[0].inhibit_exercises) > 0
    # assert len(active_rest[0].static_stretch_exercises) >0
    # assert len(active_rest[0].active_stretch_exercises) > 0

def test_create_plan_with_mixed_session():

    session = MixedActivitySession()
    session.event_date = datetime.now()

    exercise_action_1 = ExerciseAction("1", "flail")
    exercise_action_1.primary_muscle_action = MuscleAction.concentric
    exercise_action_1.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    exercise_action_1.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    exercise_action_1.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    exercise_action_1.total_load_left = 100
    exercise_action_1.total_load_right = 200
    exercise_action_1.lower_body_stability_rating = 1.1
    exercise_action_1.upper_body_stability_rating = 0.6
    exercise_action_1.adaptation_type = AdaptationType.strength_endurance_strength

    exercise_action_2 = ExerciseAction("1", "flail")
    exercise_action_2.primary_muscle_action = MuscleAction.concentric
    exercise_action_2.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    exercise_action_2.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    exercise_action_2.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    exercise_action_2.total_load_left = 200
    exercise_action_2.total_load_right = 100
    exercise_action_2.lower_body_stability_rating = 1.1
    exercise_action_2.upper_body_stability_rating = 0.6
    exercise_action_2.adaptation_type = AdaptationType.power_explosive_action

    exercise_1 = WorkoutExercise()
    exercise_1.primary_actions.append(exercise_action_1)

    exercise_2 = WorkoutExercise()
    exercise_2.primary_actions.append(exercise_action_2)

    section_1 = WorkoutSection()
    section_1.exercises.append(exercise_1)

    section_2 = WorkoutSection()
    section_2.exercises.append(exercise_2)

    program_module = WorkoutProgramModule()
    program_module.workout_sections.append(section_1)
    program_module.workout_sections.append(section_2)

    session.workout_program_module = program_module

    proc = InjuryRiskProcessor(session.event_date, [], [session], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignmentCalculator(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        session.event_date)

    active_rest = calc.get_post_active_rest()[0]
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert len(active_rest.exercise_phases[2].exercises) > 0
