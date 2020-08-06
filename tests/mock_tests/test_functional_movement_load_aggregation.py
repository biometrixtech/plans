from models.functional_movement_type import FunctionalMovementType
from models.functional_movement import FunctionalMovementFactory
from models.movement_actions import MuscleAction, ExerciseAction, PrioritizedJointAction
from models.workout_program import WorkoutProgramModule, WorkoutSection, WorkoutExercise
# from logic.workout_processing import WorkoutProcessor
from models.movement_tags import AdaptationType, TrainingType, MovementSurfaceStability, Equipment
from models.session_functional_movement import SessionFunctionalMovement
from models.session import MixedActivitySession
from models.exercise import WeightMeasure
from models.athlete_injury_risk import AthleteInjuryRisk
from models.training_volume import StandardErrorRange
from models.training_load import CompletedSessionDetails
from datetime import datetime

def test_aggregate_load_concentric():

    exercise_action_1 = ExerciseAction("1", "flail")
    exercise_action_1.primary_muscle_action = MuscleAction.concentric
    exercise_action_1.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    exercise_action_1.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    exercise_action_1.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    #exercise_action_1.tissue_load_left = StandardErrorRange(observed_value=100)
    #exercise_action_1.tissue_load_right = StandardErrorRange(observed_value=200)
    exercise_action_1.power_load_left = StandardErrorRange(observed_value=100)
    exercise_action_1.power_load_right = StandardErrorRange(observed_value=200)
    exercise_action_1.lower_body_stability_rating = 1.1
    exercise_action_1.upper_body_stability_rating = 0.6
    exercise_action_1.adaptation_type = AdaptationType.strength_endurance_strength

    exercise_action_2 = ExerciseAction("1", "flail")
    exercise_action_2.primary_muscle_action = MuscleAction.concentric
    exercise_action_2.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    exercise_action_2.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    exercise_action_2.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    #exercise_action_2.tissue_load_left = StandardErrorRange(observed_value=200)
    #exercise_action_2.tissue_load_right = StandardErrorRange(observed_value=100)
    exercise_action_2.power_load_left = StandardErrorRange(observed_value=200)
    exercise_action_2.power_load_right = StandardErrorRange(observed_value=100)
    exercise_action_2.lower_body_stability_rating = 1.1
    exercise_action_2.upper_body_stability_rating = 0.6
    exercise_action_2.adaptation_type = AdaptationType.power_explosive_action

    exercise_1 = WorkoutExercise()
    exercise_1.weight_measure = WeightMeasure.actual_weight
    exercise_1.weight = 100
    exercise_1.reps_per_set = 5
    exercise_1.power_load = StandardErrorRange(observed_value=300)
    exercise_1.equipment = Equipment.dumbbells
    exercise_1.primary_actions.append(exercise_action_1)
    exercise_1.training_type = TrainingType.strength_integrated_resistance

    exercise_2 = WorkoutExercise()
    exercise_2.power_load = StandardErrorRange(observed_value=300)
    exercise_2.primary_actions.append(exercise_action_2)
    exercise_2.training_type = TrainingType.power_action_plyometrics

    section_1 = WorkoutSection()
    section_1.exercises.append(exercise_1)

    section_2 = WorkoutSection()
    section_2.exercises.append(exercise_2)

    program_module = WorkoutProgramModule()
    program_module.workout_sections.append(section_1)
    program_module.workout_sections.append(section_2)

    factory = FunctionalMovementFactory()
    dict = factory.get_functional_movement_dictionary()

    session_functional_movement = SessionFunctionalMovement(None, {})
    session_functional_movement.completed_session_details = CompletedSessionDetails(datetime.now(), None, None)
    load_dict = session_functional_movement.process_workout_load(program_module, datetime.now(), dict)

    # assert len(load_dict) == 2
    # assert len(load_dict[AdaptationType.strength_endurance_strength.value]) == 67
    # assert len(load_dict[AdaptationType.power_explosive_action.value]) == 67
    assert len(load_dict) == 67


def test_normalize_load_concentric():

    exercise_action_1 = ExerciseAction("1", "flail")
    exercise_action_1.primary_muscle_action = MuscleAction.concentric
    exercise_action_1.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    exercise_action_1.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    exercise_action_1.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    #exercise_action_1.tissue_load_left = StandardErrorRange(observed_value=100)
    #exercise_action_1.tissue_load_right = StandardErrorRange(observed_value=200)
    exercise_action_1.power_load_left = StandardErrorRange(observed_value=100)
    exercise_action_1.power_load_right = StandardErrorRange(observed_value=200)
    exercise_action_1.lower_body_stability_rating = 1.1
    exercise_action_1.upper_body_stability_rating = 0.6
    exercise_action_1.adaptation_type = AdaptationType.strength_endurance_strength

    exercise_action_2 = ExerciseAction("1", "flail")
    exercise_action_2.primary_muscle_action = MuscleAction.concentric
    exercise_action_2.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    exercise_action_2.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    exercise_action_2.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    #exercise_action_2.total_load_left = StandardErrorRange(observed_value=200)
    #exercise_action_2.total_load_right = StandardErrorRange(observed_value=100)
    exercise_action_2.power_load_left = StandardErrorRange(observed_value=200)
    exercise_action_2.power_load_right = StandardErrorRange(observed_value=100)
    exercise_action_2.lower_body_stability_rating = 1.1
    exercise_action_2.upper_body_stability_rating = 0.6
    exercise_action_2.adaptation_type = AdaptationType.power_explosive_action

    exercise_1 = WorkoutExercise()
    exercise_1.power_load = StandardErrorRange(observed_value=300)
    exercise_1.primary_actions.append(exercise_action_1)
    exercise_1.training_type = TrainingType.strength_integrated_resistance

    exercise_2 = WorkoutExercise()
    exercise_2.power_load = StandardErrorRange(observed_value=300)
    exercise_2.primary_actions.append(exercise_action_2)
    exercise_2.training_type = TrainingType.power_action_plyometrics

    section_1 = WorkoutSection()
    section_1.exercises.append(exercise_1)

    section_2 = WorkoutSection()
    section_2.exercises.append(exercise_2)

    program_module = WorkoutProgramModule()
    program_module.workout_sections.append(section_1)
    program_module.workout_sections.append(section_2)

    factory = FunctionalMovementFactory()
    dict = factory.get_functional_movement_dictionary()

    athlete_injury_risk = AthleteInjuryRisk("tester")
    session_functional_movement = SessionFunctionalMovement(MixedActivitySession(), athlete_injury_risk.items)
    session_functional_movement.completed_session_details = CompletedSessionDetails(datetime.now(), None, None)
    load_dict = session_functional_movement.process_workout_load(program_module, datetime.now(), dict)

    # not used anymore
    #normalized_dict = session_functional_movement.consolidate_load(load_dict, datetime.now())

    assert len(load_dict) == 67