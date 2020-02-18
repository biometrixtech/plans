from models.functional_movement_type import FunctionalMovementType
from models.movement_actions import MuscleAction, ExerciseAction, PrioritizedJointAction
from models.workout_program import WorkoutProgramModule, WorkoutSection, WorkoutExercise
from logic.workout_processing import WorkoutProcessor
from models.movement_tags import AdaptationType, TrainingType, MovementSurfaceStability, Equipment


def test_aggregate_load_concentric():

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

    workout_processor = WorkoutProcessor()
    load_dict = workout_processor.process_workout_load(program_module)

    assert len(load_dict) == 2
    assert len(load_dict[AdaptationType.strength_endurance_strength.value]) == 67
    assert len(load_dict[AdaptationType.power_explosive_action.value]) == 67


def test_normalize_load_concentric():

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

    workout_processor = WorkoutProcessor()
    load_dict = workout_processor.process_workout_load(program_module)

    normalized_dict = workout_processor.normalize_and_consolidate_load(load_dict)

    assert len(normalized_dict) == 67