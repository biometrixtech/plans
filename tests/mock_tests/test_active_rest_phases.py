
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import pytest
from models.session import SportTrainingSession, MixedActivitySession
from datetime import datetime, timedelta
from models.sport import SportName
from models.soreness import Soreness
from models.body_parts import BodyPart
from models.soreness_base import BodyPartLocation, BodyPartSide
from models.stats import AthleteStats
from logic.injury_risk_processing import InjuryRiskProcessor
from logic.exercise_assignment import ExerciseAssignment
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from models.movement_tags import AdaptationType, TrainingType
from models.movement_actions import MuscleAction, ExerciseAction, PrioritizedJointAction, ExerciseSubAction, CompoundAction
from models.workout_program import WorkoutProgramModule, WorkoutSection, WorkoutExercise
from models.functional_movement_type import FunctionalMovementType
from models.exercise_phase import ExercisePhaseType
from models.training_volume import StandardErrorRange


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


def test_check_active_rest_phases_soreness_no_session():

    now_date = datetime.now()

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(6), None)
    soreness.side = 1
    soreness.sharp = 3
    soreness.reported_date_time = now_date

    proc = InjuryRiskProcessor(now_date, [soreness], [], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore, now_date)

    active_rest = calc.get_active_rest()[0]
    assert active_rest.exercise_phases[0].type == ExercisePhaseType.inhibit
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert active_rest.exercise_phases[1].type == ExercisePhaseType.static_stretch
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert active_rest.exercise_phases[2].type == ExercisePhaseType.isolated_activate
    assert len(active_rest.exercise_phases[2].exercises) == 0
    assert active_rest.exercise_phases[3].type == ExercisePhaseType.static_integrate
    assert len(active_rest.exercise_phases[3].exercises) == 0


def test_check_active_rest_phases_soreness_with_simple_session():

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

    calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        dates[0])

    active_rest = calc.get_active_rest()[0]
    assert active_rest.exercise_phases[0].type == ExercisePhaseType.inhibit
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert active_rest.exercise_phases[1].type == ExercisePhaseType.static_stretch
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert active_rest.exercise_phases[2].type == ExercisePhaseType.isolated_activate
    assert len(active_rest.exercise_phases[2].exercises) > 0
    assert active_rest.exercise_phases[3].type == ExercisePhaseType.static_integrate
    assert len(active_rest.exercise_phases[3].exercises) == 0


def test_check_active_rest_phases_no_soreness_with_simple_session():

    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]

    sessions = get_sessions(dates, rpes, durations, sport_names)

    proc = InjuryRiskProcessor(dates[0], [], sessions, {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        dates[0])

    active_rest = calc.get_active_rest()[0]
    assert active_rest.exercise_phases[0].type == ExercisePhaseType.inhibit
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert active_rest.exercise_phases[1].type == ExercisePhaseType.static_stretch
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert active_rest.exercise_phases[2].type == ExercisePhaseType.isolated_activate
    assert len(active_rest.exercise_phases[2].exercises) > 0
    assert active_rest.exercise_phases[3].type == ExercisePhaseType.static_integrate
    assert len(active_rest.exercise_phases[3].exercises) == 0


def test_check_active_rest_phases_no_inputs_default_force_on_demand():

    dates = [datetime.now()]

    proc = InjuryRiskProcessor(dates[0], [], [], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        dates[0])

    active_rest = calc.get_active_rest()[0]
    assert active_rest.exercise_phases[0].type == ExercisePhaseType.inhibit
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert active_rest.exercise_phases[1].type == ExercisePhaseType.static_stretch
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert active_rest.exercise_phases[2].type == ExercisePhaseType.isolated_activate
    assert len(active_rest.exercise_phases[2].exercises) > 0
    assert active_rest.exercise_phases[3].type == ExercisePhaseType.static_integrate
    assert len(active_rest.exercise_phases[3].exercises) > 0


def test_check_active_rest_phases_no_inputs_force_on_demand_false():

    dates = [datetime.now()]

    proc = InjuryRiskProcessor(dates[0], [], [], {}, AthleteStats("tester"), "tester")
    injury_risk_dict = proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()

    calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        dates[0])

    active_rest = calc.get_active_rest(force_on_demand=False)
    assert len(active_rest) == 0
    # active_rest = calc.get_active_rest(force_on_demand=False)[0]
    # assert active_rest.exercise_phases[0].type == ExercisePhaseType.inhibit
    # assert len(active_rest.exercise_phases[0].exercises) == 0
    # assert active_rest.exercise_phases[1].type == ExercisePhaseType.static_stretch
    # assert len(active_rest.exercise_phases[1].exercises) == 0
    # assert active_rest.exercise_phases[2].type == ExercisePhaseType.isolated_activate
    # assert len(active_rest.exercise_phases[2].exercises) == 0
    # assert active_rest.exercise_phases[3].type == ExercisePhaseType.static_integrate
    # assert len(active_rest.exercise_phases[3].exercises) == 0


def test_check_active_rest_phases_no_soreness_with_mixed_session():

    session = MixedActivitySession()
    session.event_date = datetime.now()

    sub_action_1 = ExerciseSubAction("1", "flail")
    sub_action_1.primary_muscle_action = MuscleAction.concentric
    sub_action_1.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    sub_action_1.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    sub_action_1.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    #exercise_action_1.tissue_load_left = StandardErrorRange(observed_value=100)
    #exercise_action_1.tissue_load_right = StandardErrorRange(observed_value=200)
    sub_action_1.power_load_left = StandardErrorRange(observed_value=100)
    sub_action_1.power_load_right = StandardErrorRange(observed_value=200)
    sub_action_1.lower_body_stability_rating = 1.1
    sub_action_1.upper_body_stability_rating = 0.6
    sub_action_1.adaptation_type = AdaptationType.strength_endurance_strength
    sub_action_1.training_type = TrainingType.strength_cardiorespiratory
    action_1 = ExerciseAction("test", "test")
    action_1.sub_actions.append(sub_action_1)
    compound_action_1 = CompoundAction("test", "test")
    compound_action_1.actions.append(action_1)

    sub_action_2 = ExerciseSubAction("1", "flail")
    sub_action_2.primary_muscle_action = MuscleAction.concentric
    sub_action_2.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    sub_action_2.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    sub_action_2.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    #exercise_action_2.tissue_load_left = StandardErrorRange(observed_value=200)
    #exercise_action_2.tissue_load_right = StandardErrorRange(observed_value=100)
    sub_action_2.power_load_left = StandardErrorRange(observed_value=200)
    sub_action_2.power_load_right = StandardErrorRange(observed_value=100)
    sub_action_2.lower_body_stability_rating = 1.1
    sub_action_2.upper_body_stability_rating = 0.6
    sub_action_2.adaptation_type = AdaptationType.power_explosive_action
    sub_action_2.training_type = TrainingType.strength_cardiorespiratory
    action_2 = ExerciseAction("test", "test")
    action_2.sub_actions.append(sub_action_2)
    compound_action_2 = CompoundAction("test", "test")
    compound_action_2.actions.append(action_2)

    exercise_1 = WorkoutExercise()
    exercise_1.rpe = StandardErrorRange(observed_value=5)
    exercise_1.duration = 90
    exercise_1.power_load = StandardErrorRange(observed_value=300)
    exercise_1.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    exercise_1.primary_actions.append(compound_action_1)

    exercise_2 = WorkoutExercise()
    exercise_2.rpe = StandardErrorRange(observed_value=5)
    exercise_2.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    exercise_2.duration = 90
    exercise_2.power_load = StandardErrorRange(observed_value=300)
    exercise_2.primary_actions.append(compound_action_2)

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

    calc = ExerciseAssignment(consolidated_injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                                        session.event_date)

    active_rest = calc.get_active_rest()[0]
    assert active_rest.exercise_phases[0].type == ExercisePhaseType.inhibit
    assert len(active_rest.exercise_phases[0].exercises) > 0
    assert active_rest.exercise_phases[1].type == ExercisePhaseType.static_stretch
    assert len(active_rest.exercise_phases[1].exercises) > 0
    assert active_rest.exercise_phases[2].type == ExercisePhaseType.isolated_activate
    assert len(active_rest.exercise_phases[2].exercises) > 0
    assert active_rest.exercise_phases[3].type == ExercisePhaseType.static_integrate
    assert len(active_rest.exercise_phases[3].exercises) == 0
