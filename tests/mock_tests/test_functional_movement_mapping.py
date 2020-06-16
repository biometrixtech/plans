from models.functional_movement import FunctionalMovementPairs, FunctionalMovementActionMapping, FunctionalMovementFactory
from models.functional_movement_type import FunctionalMovementType
from models.movement_actions import MuscleAction, ExerciseAction, PrioritizedJointAction
from models.training_volume import StandardErrorRange
from models.soreness_base import BodyPartLocation, BodyPartSide
from datetime import datetime


def test_get_eccentric_pair():
    pairs = FunctionalMovementPairs()
    eccentric_type = pairs.get_functional_movement_for_muscle_action(MuscleAction.eccentric, FunctionalMovementType.knee_extension)

    assert FunctionalMovementType.knee_flexion == eccentric_type


def test_get_concentric_pair():
    pairs = FunctionalMovementPairs()
    concentric_type = pairs.get_functional_movement_for_muscle_action(MuscleAction.concentric, FunctionalMovementType.knee_extension)

    assert FunctionalMovementType.knee_extension == concentric_type


def test_get_isometric_pair():
    pairs = FunctionalMovementPairs()
    isometric_type = pairs.get_functional_movement_for_muscle_action(MuscleAction.isometric, FunctionalMovementType.knee_extension)

    assert FunctionalMovementType.knee_extension == isometric_type


def test_apply_load_concentric():

    exercise_action = ExerciseAction("1", "flail")
    exercise_action.primary_muscle_action = MuscleAction.concentric
    exercise_action.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
    exercise_action.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
    exercise_action.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
    #exercise_action.tissue_load_left = StandardErrorRange(observed_value=100)
    #exercise_action.tissue_load_right = StandardErrorRange(observed_value=200)
    exercise_action.power_load_left = StandardErrorRange(observed_value=100)
    exercise_action.power_load_right = StandardErrorRange(observed_value=200)
    exercise_action.lower_body_stability_rating = 1.1
    exercise_action.upper_body_stability_rating = 0.6


    synergist_ratio = 0.6
    priority_2_ratio = 0.6
    priority_3_ratio = 0.3

    factory = FunctionalMovementFactory()
    dict = factory.get_functional_movement_dictinary()

    functional_movement_action_mapping = FunctionalMovementActionMapping(exercise_action, {}, datetime.now(), dict)
    assert len(functional_movement_action_mapping.muscle_load) == 67

    # # Priority 1, prime movers
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(66), 1)] == 100
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(66), 2)] == 200
    # # Priority 1, synergists
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(45), 1)] == 100 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(45), 2)] == 200 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(47), 1)] == 100 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(47), 2)] == 200 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(48), 1)] == 100 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(48), 2)] == 200 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(51), 1)] == 100 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(51), 2)] == 200 * synergist_ratio
    #
    # # Priority 2, prime movers
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(55), 1)] == 100 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(55), 2)] == 200 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(56), 1)] == 100 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(56), 2)] == 200 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(57), 1)] == 100 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(57), 2)] == 200 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(58), 1)] == 100 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(58), 2)] == 200 * priority_2_ratio
    #
    # # Priority 3, prime movers
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(43), 1)] == 100 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(43), 2)] == 200 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(44), 1)] == 100 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(44), 2)] == 200 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(61), 1)] == 100 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(61), 2)] == 200 * priority_3_ratio
    #
    # # Priority 3, synergists
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(41), 1)] == 100 * priority_3_ratio * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(41), 2)] == 200 * priority_3_ratio * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(42), 1)] == 100 * priority_3_ratio * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(42), 2)] == 200 * priority_3_ratio * synergist_ratio


def test_apply_load_eccentric():

    exercise_action = ExerciseAction("2", "flail")
    exercise_action.primary_muscle_action = MuscleAction.eccentric
    exercise_action.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_flexion)]
    exercise_action.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_flexion)]
    exercise_action.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_dorsiflexion)]
    #exercise_action.tissue_load_left = StandardErrorRange(observed_value=100)
    #exercise_action.tissue_load_right = StandardErrorRange(observed_value=200)
    exercise_action.power_load_left = StandardErrorRange(observed_value=100)
    exercise_action.power_load_right = StandardErrorRange(observed_value=200)
    exercise_action.lower_body_stability_rating = 1.1
    exercise_action.upper_body_stability_rating = 0.6

    synergist_ratio = 0.6
    priority_2_ratio = 0.6
    priority_3_ratio = 0.3

    factory = FunctionalMovementFactory()
    dict = factory.get_functional_movement_dictinary()

    functional_movement_action_mapping = FunctionalMovementActionMapping(exercise_action, {}, datetime.now(), dict)
    assert len(functional_movement_action_mapping.muscle_load) == 67

    # # Priority 1, prime movers
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(66), 1)] == 100
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(66), 2)] == 200
    # # Priority 1, synergists
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(45), 1)] == 100 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(45), 2)] == 200 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(47), 1)] == 100 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(47), 2)] == 200 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(48), 1)] == 100 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(48), 2)] == 200 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(51), 1)] == 100 * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(51), 2)] == 200 * synergist_ratio
    #
    # # Priority 2, prime movers
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(55), 1)] == 100 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(55), 2)] == 200 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(56), 1)] == 100 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(56), 2)] == 200 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(57), 1)] == 100 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(57), 2)] == 200 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(58), 1)] == 100 * priority_2_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(58), 2)] == 200 * priority_2_ratio
    #
    # # Priority 3, prime movers
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(43), 1)] == 100 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(43), 2)] == 200 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(44), 1)] == 100 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(44), 2)] == 200 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(61), 1)] == 100 * priority_3_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(61), 2)] == 200 * priority_3_ratio
    #
    # # Priority 3, synergists
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(41), 1)] == 100 * priority_3_ratio * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(41), 2)] == 200 * priority_3_ratio * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(42), 1)] == 100 * priority_3_ratio * synergist_ratio
    # assert functional_movement_action_mapping.muscle_load[BodyPartSide(BodyPartLocation(42), 2)] == 200 * priority_3_ratio * synergist_ratio
