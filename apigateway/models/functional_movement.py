from enum import IntEnum, Enum
from models.sport import SportName


class FunctionalMovementType(Enum):
    ankle_dorsiflexion = 0
    ankle_plantar_flexion = 1
    inversion_of_the_foot = 2
    eversion_of_the_foot = 3
    knee_flexion = 4
    knee_extension = 5
    tibial_external_rotation = 6
    tibial_internal_rotation = 7
    hip_adduction = 8
    hip_abduction = 9
    hip_internal_rotation = 10
    hip_external_rotation = 11
    hip_extension = 12
    hip_flexion = 13


class FunctionalMovement(object):
    def __init__(self, functional_movement_type):
        self.functional_movement_type = functional_movement_type
        self.prime_movers = []
        self.antagonists = []
        self.synergists = []


class FunctionalMovementActivityMapping(object):
    def __init__(self, functional_movement_type, is_concentric, concentric_level, is_eccentric, eccentric_level):
        self.functional_movement_type = functional_movement_type
        self.is_concentric = is_concentric
        self.concentric_level = concentric_level
        self.is_eccentric = is_eccentric
        self.eccentric_level = eccentric_level


class ActivityFunctionalMovementFactory(object):

    def get_functional_movement_mappings(self, sport_name):

        mapping = []

        if sport_name == SportName.distance_running:
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.ankle_dorsiflexion, True, 1, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.ankle_plantar_flexion, True, 1, True, 1))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.inversion_of_the_foot, True, 1, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.eversion_of_the_foot, False, 0, True, 1))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.knee_flexion, True, 1, True, 1))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.knee_extension, True, 1, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.hip_adduction, True, 2, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.hip_abduction, False, 0, True, 1))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.hip_extension, True, 5, False, 0))
            mapping.append(
                FunctionalMovementActivityMapping(FunctionalMovementType.hip_flexion, True, 2, True, 2))

            return mapping


class FunctionalMovementFactory(object):

    def get_functional_movement(self, movement_type):

        if movement_type == FunctionalMovementType.ankle_dorsiflexion:
            return self.get_ankle_dorsiflexion()
        elif movement_type == FunctionalMovementType.ankle_plantar_flexion:
            return self.get_ankle_plantar_flexion()
        elif movement_type == FunctionalMovementType.inversion_of_the_foot:
            return self.get_inversion_of_the_foot()
        elif movement_type == FunctionalMovementType.eversion_of_the_foot:
            return self.get_eversion_of_the_foot()
        elif movement_type == FunctionalMovementType.knee_flexion:
            return self.get_knee_flexion()
        elif movement_type == FunctionalMovementType.knee_extension:
            return self.get_knee_extension()
        elif movement_type == FunctionalMovementType.tibial_external_rotation:
            return self.get_tibial_external_rotation()
        elif movement_type == FunctionalMovementType.tibial_internal_rotation:
            return self.get_tibial_internal_rotation()
        elif movement_type == FunctionalMovementType.hip_adduction:
            return self.get_hip_adduction()
        elif movement_type == FunctionalMovementType.hip_abduction:
            return self.get_hip_abduction()
        elif movement_type == FunctionalMovementType.hip_internal_rotation:
            return self.get_hip_internal_rotation()
        elif movement_type == FunctionalMovementType.hip_external_rotation:
            return self.get_hip_external_rotation()
        elif movement_type == FunctionalMovementType.hip_extension:
            return self.get_hip_extension()
        elif movement_type == FunctionalMovementType.hip_flexion:
            return self.get_hip_flexion()


    def get_ankle_dorsiflexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_dorsiflexion)
        functional_movement.prime_movers = [40]
        functional_movement.antagonists = [41, 42, 43, 44]
        return functional_movement

    def get_ankle_plantar_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_plantar_flexion)
        functional_movement.prime_movers = [41, 42, 43, 44]
        functional_movement.antagonists = [40]
        return functional_movement

    def get_inversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.inversion_of_the_foot)
        functional_movement.prime_movers = [40, 42]
        functional_movement.antagonists = [41]
        return functional_movement

    def get_eversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.eversion_of_the_foot)
        functional_movement.prime_movers = [41]
        functional_movement.antagonists = [40, 42]
        return functional_movement

    def get_knee_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_flexion)
        functional_movement.prime_movers = [45, 46, 47, 48]
        functional_movement.antagonists = [55, 56, 57, 58]
        return functional_movement

    def get_knee_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_extension)
        functional_movement.prime_movers = [55, 56, 57, 58]
        functional_movement.antagonists = [45, 46, 47, 48]
        return functional_movement

    def get_tibial_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.tibial_external_rotation)
        functional_movement.prime_movers = [45, 46]
        functional_movement.antagonists = [47, 48]
        return functional_movement

    def get_tibial_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.tibial_internal_rotation)
        functional_movement.prime_movers = [47, 48]
        functional_movement.antagonists = [45, 46, 53]
        return functional_movement

    def get_hip_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_extension)
        functional_movement.prime_movers = [45, 47, 48, 51, 60, 66]
        functional_movement.antagonists = [49, 50, 52, 53, 54, 58, 59, 61, 62, 65]
        return functional_movement

    def get_hip_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_flexion)
        functional_movement.prime_movers = [49, 50, 52, 53, 54, 58, 59, 61, 62, 65]
        functional_movement.antagonists = [47, 48, 51, 60, 66]
        return functional_movement

    def get_hip_adduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_adduction)
        functional_movement.prime_movers = [49, 50, 51, 52, 53, 54]
        functional_movement.antagonists = [59, 60, 63, 64, 65]
        return functional_movement

    def get_hip_abduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_abduction)
        functional_movement.prime_movers = [59, 60, 62, 63, 64, 65]
        functional_movement.antagonists = [49, 50, 51, 52, 53, 54]
        return functional_movement

    def get_hip_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_internal_rotation)
        functional_movement.prime_movers = [49, 50, 52, 53, 54, 59, 63, 65]
        functional_movement.antagonists = [51, 60, 61, 64, 66]
        return functional_movement

    def get_hip_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_external_rotation)
        functional_movement.prime_movers = [51, 60, 61, 64, 66]
        functional_movement.antagonists = [49, 50, 52, 53, 54, 59, 62, 63, 65]
        return functional_movement