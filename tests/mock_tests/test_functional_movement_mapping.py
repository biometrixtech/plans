from models.functional_movement import FunctionalMovementPairs, FunctionalMovementType
from models.movement_actions import MuscleAction


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
