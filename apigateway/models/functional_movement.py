from enum import Enum
from collections import namedtuple

from models.compensation_source import CompensationSource
from models.soreness_base import BodyPartSide
from models.body_parts import BodyPartFactory
from models.training_volume import StandardErrorRange
from datetime import timedelta
from models.movement_actions import MuscleAction
from models.functional_movement_type import FunctionalMovementType
from serialisable import Serialisable


FunctionalMovementPair = namedtuple('FunctionalMovementPair',['movement_1', 'movement_2'])


class FunctionalMovementPairs(object):
    def __init__(self):
        self.pairs = []
        self.populate_pairs()

    def populate_pairs(self):

        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.ankle_dorsiflexion,
                                                 FunctionalMovementType.ankle_plantar_flexion))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.inversion_of_the_foot,
                                                 FunctionalMovementType.eversion_of_the_foot))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.knee_flexion,
                                                 FunctionalMovementType.knee_extension))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.tibial_external_rotation,
                                                 FunctionalMovementType.tibial_internal_rotation))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.hip_adduction,
                                                 FunctionalMovementType.hip_abduction))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.hip_internal_rotation,
                                                 FunctionalMovementType.hip_external_rotation))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.hip_extension,
                                                 FunctionalMovementType.hip_flexion))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.pelvic_anterior_tilt,
                                                 FunctionalMovementType.pelvic_posterior_tilt))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.trunk_flexion,
                                                 FunctionalMovementType.trunk_extension))
        # note no pair
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.trunk_lateral_flexion,
                                                 FunctionalMovementType.trunk_lateral_flexion))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.trunk_rotation,
                                                 FunctionalMovementType.trunk_rotation))

        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.trunk_flexion_with_rotation,
                                                 FunctionalMovementType.trunk_extension_with_rotation))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.elbow_flexion,
                                                 FunctionalMovementType.elbow_extension))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.shoulder_horizontal_abduction,
                                                 FunctionalMovementType.shoulder_horizontal_adduction))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation,
                                                 FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation,
                                                 FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.internal_rotation,
                                                 FunctionalMovementType.external_rotation))
        self.pairs.append(FunctionalMovementPair(FunctionalMovementType.scapular_elevation,
                                                 FunctionalMovementType.scapular_depression))

    def get_functional_movement_for_muscle_action(self, muscle_action, functional_movement_type):

        if muscle_action == MuscleAction.concentric or muscle_action == MuscleAction.isometric:
            return functional_movement_type
        elif muscle_action == MuscleAction.eccentric:
            pair = [i for i, v in enumerate(self.pairs) if v[0] == functional_movement_type or v[1] == functional_movement_type]
            pair_item = pair[0]
            if self.pairs[pair_item][0] == functional_movement_type:
                return self.pairs[pair_item][1]
            else:
                return self.pairs[pair_item][0]


class BodyPartFunction(Enum):
    prime_mover = 0
    antagonist = 1
    synergist = 2
    stabilizer = 3
    fixator = 4

    def get_ranking(self):
        rankings = {
            'prime_mover': 0,
            'antagonist': 3,
            'synergist': 2,
            'stabilizer': 1,
            'fixator': 4,
        }
        return rankings[self.name]

    @classmethod
    def merge(cls, function1, function2):
        if function1 is not None and function2 is not None:
            if function1 == function2:
                return function1
            elif function1.get_ranking() < function2.get_ranking():
                return function1
            else:
                return function2
        elif function1 is not None:
            return function1
        elif function2 is not None:
            return function2
        else:
            return None


class FunctionalMovement(object):
    def __init__(self, functional_movement_type, priority=0):
        self.functional_movement_type = functional_movement_type
        self.priority = priority
        self.prime_movers = []
        self.antagonists = []
        self.synergists = []
        self.stabilizers = []
        self.fixators = []
        self.parts_receiving_compensation = []


class BodyPartFunctionalMovement(Serialisable):
    def __init__(self, body_part_side):
        self.body_part_side = body_part_side
        self.concentric_load = StandardErrorRange()
        self.eccentric_load = StandardErrorRange()
        self.compensated_concentric_load = StandardErrorRange()
        self.compensated_eccentric_load = StandardErrorRange()
        self.compensating_causes_load = []
        self.is_compensating = False
        #self.compensation_source_load = None
        self.body_part_function = None
        #self.inhibited = 0
        #self.weak = 0
        #self.tight = 0
        #self.inflamed = 0
        #self.long = 0

        #self.total_normalized_load = StandardErrorRange()

    def total_load(self):

        total_load = StandardErrorRange(observed_value=0)
        total_load.add(self.concentric_load)
        total_load.add(self.eccentric_load)
        total_load.add(self.compensated_concentric_load)
        total_load.add(self.compensated_eccentric_load)

        return total_load

    def total_concentric_load(self):

        total_load = StandardErrorRange(observed_value=0)
        total_load.add(self.concentric_load)
        total_load.add(self.compensated_concentric_load)

        return total_load

    def total_eccentric_load(self):

        total_load = StandardErrorRange(observed_value=0)
        total_load.add(self.eccentric_load)
        total_load.add(self.compensated_eccentric_load)

        return total_load

    def __hash__(self):
        return hash((self.body_part_side.body_part_location.value, self.body_part_side.side))

    def __eq__(self, other):
        return self.body_part_side.body_part_location == other.body_part_side.body_part_location and self.body_part_side.side == other.body_part_side.side

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)

    def json_serialise(self):
        return {
                'body_part_side': self.body_part_side.json_serialise(),
                'concentric_load': self.concentric_load.json_serialise(),
                'eccentric_load': self.eccentric_load.json_serialise(),
                'compensated_concentric_load': self.compensated_concentric_load.json_serialise(),
                'compensated_eccentric_load': self.compensated_eccentric_load.json_serialise(),
                'compensating_causes_load': [c.json_serialise() for c in self.compensating_causes_load],
                'is_compensating': self.is_compensating,
                #'compensation_source_load': self.compensation_source_load.value if self.compensation_source_load is not None else None,
                'body_part_function': self.body_part_function.value if self.body_part_function is not None else None,
                #'inhibited': self.inhibited if self.inhibited is not None else None,
                #'weak': self.weak,
                #'tight': self.tight,
                #'inflamed': self.inflamed,
                #'long': self.long,
                #'total_normalized_load': self.total_normalized_load
            }

    @classmethod
    def json_deserialise(cls, input_dict):
        movement = cls(BodyPartSide.json_deserialise(input_dict['body_part_side']))
        movement.concentric_load = StandardErrorRange.json_deserialise(input_dict.get('concentric_load')) if input_dict.get('concentric_load') is not None else StandardErrorRange()
        movement.eccentric_load = StandardErrorRange.json_deserialise(input_dict.get('eccentric_load')) if input_dict.get('eccentric_load') is not None else StandardErrorRange()
        movement.compensated_concentric_load = StandardErrorRange.json_deserialise(input_dict.get('compensated_concentric_load')) if input_dict.get('compensated_concentric_load') is not None else StandardErrorRange()
        movement.compensated_eccentric_load = StandardErrorRange.json_deserialise(input_dict.get('compensated_eccentric_load')) if input_dict.get('compensated_eccentric_load') is not None else StandardErrorRange()
        movement.compensating_causes_load = [BodyPartSide.json_deserialise(b) for b in input_dict.get('compensating_causes_load', [])]  # I don't know what gets saved here!
        movement.is_compensating = input_dict.get('is_compensating', False)
        #movement.compensation_source_load = CompensationSource(input_dict['compensation_source_load']) if input_dict.get('compensation_source_load') is not None else None
        movement.body_part_function = BodyPartFunction(input_dict['body_part_function']) if input_dict.get('body_part_function') is not None else None
        #movement.inhibited = input_dict.get('inhibited', 0)
        #movement.weak = input_dict.get('weak', 0)
        #movement.tight = input_dict.get('tight', 0)
        #movement.inflamed = input_dict.get('inflamed', 0)
        #movement.long = input_dict.get('long', 0)
        #movement.total_normalized_load = input_dict.get('total_normalized_load', 0)
        return movement

    def merge(self, target):

        if self.body_part_side == target.body_part_side:

            self.concentric_load.add(target.concentric_load)
            self.eccentric_load.add(target.eccentric_load)
            self.compensated_concentric_load.add(target.compensated_concentric_load)
            self.compensated_eccentric_load.add(target.compensated_eccentric_load)
            self.compensating_causes_load.extend(target.compensating_causes_load)
            self.compensating_causes_load = list(set(self.compensating_causes_load))
            self.is_compensating = max(self.is_compensating, target.is_compensating)
            #self.compensation_source_load = self.merge_with_none(self.compensation_source_load, target.compensation_source_load)
            self.body_part_function = BodyPartFunction.merge(self.body_part_function, target.body_part_function)
            #self.total_normalized_load.add(target.total_normalized_load)

    def merge_with_none(self, value_a, value_b):

        if value_a is None and value_b is None:
            return None
        if value_a is not None and value_b is None:
            return CompensationSource(value_a.value)
        if value_b is not None and value_a is None:
            return CompensationSource(value_b.value)
        if value_a is not None and value_b is not None:
            return CompensationSource(max(value_a.value, value_b.value))


class FunctionalMovementLoad(object):
    def __init__(self, functional_movement, muscle_action):
        self.functional_movement = functional_movement
        self.muscle_action = muscle_action


class FunctionalMovementActionMapping(object):
    def __init__(self, exercise_action, injury_risk_dict, event_date, functional_movement_dict=None):
        self.exercise_action = exercise_action
        self.hip_joint_functional_movements = []
        self.knee_joint_functional_movements = []
        self.ankle_joint_functional_movements = []
        self.trunk_joint_functional_movements = []
        self.shoulder_scapula_joint_functional_movements = []
        self.elbow_joint_functional_movements = []
        self.muscle_load = {}
        self.functional_movement_dict = functional_movement_dict
        #self.injury_risk_dict = injury_risk_dict
        #self.event_date = event_date

        self.set_functional_movements()
        self.set_muscle_load(injury_risk_dict, event_date)

    def set_functional_movements(self):

        if self.exercise_action is not None:
            self.hip_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.hip_joint_action)
            self.knee_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.knee_joint_action)
            self.ankle_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.ankle_joint_action)
            self.trunk_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.trunk_joint_action)
            self.shoulder_scapula_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.shoulder_scapula_joint_action)
            self.elbow_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.elbow_joint_action)

    def get_functional_movements_for_joint_action(self, target_joint_action_list):

        #movement_factory = FunctionalMovementFactory()
        pairs = FunctionalMovementPairs()

        functional_movement_list = []

        for target_joint_action in target_joint_action_list:

            functional_movement_type = pairs.get_functional_movement_for_muscle_action(
                self.exercise_action.primary_muscle_action, target_joint_action.joint_action)

            #functional_movement = movement_factory.get_functional_movement(functional_movement_type)

            # functional_movement.prime_movers = self.convert_enums_to_body_part_side_list(
            #     functional_movement.prime_movers)
            # functional_movement.stabilizers = self.convert_enums_to_body_part_side_list(
            #     functional_movement.stabilizers)
            # functional_movement.synergists = self.convert_enums_to_body_part_side_list(
            #     functional_movement.synergists)
            # functional_movement.fixators = self.convert_enums_to_body_part_side_list(
            #     functional_movement.fixators)
            # functional_movement.parts_receiving_compensation = self.convert_enums_to_body_part_side_list(
            #     functional_movement.parts_receiving_compensation)

            functional_movement = self.functional_movement_dict[functional_movement_type.value]

            functional_movement.priority = target_joint_action.priority

            functional_movement_load = FunctionalMovementLoad(functional_movement, self.exercise_action.primary_muscle_action)

            functional_movement_list.append(functional_movement_load)

        return functional_movement_list

    def convert_enums_to_body_part_side_list(self, enum_list):

        body_part_factory = BodyPartFactory()
        body_part_list = []
        # if len(enum_list) > 0:
        #     body_part_list = [body_part_factory.get_body_part_side_list(e) for e in enum_list]
        #     body_part_list = [b for body_list in body_part_list for b in body_list]

        for p in range(0, len(enum_list)):
            body_part_side_list = body_part_factory.get_body_part_side_list(enum_list[p])
            body_part_list.extend(body_part_side_list)

        return body_part_list

    def set_muscle_load(self, injury_risk_dict, event_date):

        self.apply_load_to_functional_movements(injury_risk_dict, event_date, self.hip_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(injury_risk_dict, event_date, self.knee_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(injury_risk_dict, event_date, self.ankle_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(injury_risk_dict, event_date, self.trunk_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(injury_risk_dict, event_date, self.shoulder_scapula_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(injury_risk_dict, event_date, self.elbow_joint_functional_movements, self.exercise_action)


    def get_matching_stability_rating(self, functional_movement_load, exercise_action):

        functional_movement = functional_movement_load.functional_movement

        lower_stability_rating = exercise_action.lower_body_stability_rating / 2.0 # normalize
        upper_stability_rating = exercise_action.upper_body_stability_rating / 2.0 # normalize

        functional_movement_type = functional_movement.functional_movement_type

        if functional_movement_type in [FunctionalMovementType.ankle_dorsiflexion,
                                        FunctionalMovementType.ankle_plantar_flexion,
                                        FunctionalMovementType.inversion_of_the_foot,
                                        FunctionalMovementType.eversion_of_the_foot,
                                        FunctionalMovementType.tibial_internal_rotation,
                                        FunctionalMovementType.tibial_external_rotation,
                                        FunctionalMovementType.ankle_dorsiflexion_and_inversion,
                                        FunctionalMovementType.ankle_plantar_flexion_and_eversion]:
            return (.8 * lower_stability_rating) + (.2 * upper_stability_rating)

        elif functional_movement_type in [FunctionalMovementType.knee_flexion,
                                          FunctionalMovementType.knee_extension]:
            return (.7 * lower_stability_rating) + (.3 * upper_stability_rating)

        elif functional_movement_type in [FunctionalMovementType.elbow_extension,
                                          FunctionalMovementType.elbow_flexion]:
            return (.2 * lower_stability_rating) + (.8 * upper_stability_rating)

        elif functional_movement_type in [FunctionalMovementType.shoulder_horizontal_adduction,
                                          FunctionalMovementType.shoulder_horizontal_abduction,
                                          FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation,
                                          FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation,
                                          FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation,
                                          FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation,
                                          FunctionalMovementType.internal_rotation,
                                          FunctionalMovementType.external_rotation,
                                          FunctionalMovementType.scapular_depression,
                                          FunctionalMovementType.scapular_elevation]:
            return (.3 * lower_stability_rating) + (.7 * upper_stability_rating)

        elif functional_movement_type in [FunctionalMovementType.hip_abduction,
                                          FunctionalMovementType.hip_adduction,
                                          FunctionalMovementType.hip_internal_rotation,
                                          FunctionalMovementType.hip_external_rotation,
                                          FunctionalMovementType.hip_extension,
                                          FunctionalMovementType.hip_flexion,
                                          FunctionalMovementType.hip_horizontal_abduction,
                                          FunctionalMovementType.hip_horizontal_adduction]:
            return (.6 * lower_stability_rating) + (.4 * upper_stability_rating)

        elif functional_movement_type in [FunctionalMovementType.pelvic_anterior_tilt,
                                          FunctionalMovementType.pelvic_posterior_tilt]:
            return (.5 * lower_stability_rating) + (.5 * upper_stability_rating)

        elif functional_movement_type in [FunctionalMovementType.trunk_flexion,
                                          FunctionalMovementType.trunk_extension,
                                          FunctionalMovementType.trunk_lateral_flexion,
                                          FunctionalMovementType.trunk_rotation,
                                          FunctionalMovementType.trunk_flexion_with_rotation,
                                          FunctionalMovementType.trunk_extension_with_rotation]:
            return (.5 * lower_stability_rating) + (.5 * upper_stability_rating)

    # def set_compensation_load(self, injury_risk_dict, event_date):
    #
    #     self.set_compensation_load_for_functional_movements(injury_risk_dict, event_date, self.hip_joint_functional_movements)
    #     self.set_compensation_load_for_functional_movements(injury_risk_dict, event_date, self.knee_joint_functional_movements)
    #     self.set_compensation_load_for_functional_movements(injury_risk_dict, event_date, self.ankle_joint_functional_movements)
    #     self.set_compensation_load_for_functional_movements(injury_risk_dict, event_date, self.trunk_joint_functional_movements)
    #     self.set_compensation_load_for_functional_movements(injury_risk_dict, event_date, self.shoulder_scapula_joint_functional_movements)
    #     self.set_compensation_load_for_functional_movements(injury_risk_dict, event_date, self.elbow_joint_functional_movements)

    # def set_compensation_load_for_functional_movements(self, injury_risk_dict, event_date, functional_movement_list):
    #
    #     compensation_causing_prime_movers = self.get_compensating_body_parts(injury_risk_dict, event_date, functional_movement_list)
    #
    #     body_part_factory = BodyPartFactory()
    #
    #     for functional_movement_load in functional_movement_list:
    #         functional_movement = functional_movement_load.functional_movement
    #
    #         for c, severity in compensation_causing_prime_movers.items():
    #             if severity <= 2:
    #                 factor = .04
    #             elif 2 < severity <= 5:
    #                 factor = .08
    #             elif 5 < severity <= 8:
    #                 factor = .16
    #             else:
    #                 factor = .20
    #
    #             for s in functional_movement.parts_receiving_compensation:
    #                 body_part_side_list = body_part_factory.get_body_part_side_list(s)
    #                 for body_part_side in body_part_side_list:
    #                     if c.side == body_part_side.side or c.side == 0 or body_part_side.side == 0:
    #                         if body_part_side in self.muscle_load.keys():
    #                             concentric_load = self.muscle_load[body_part_side].concentric_load
    #                             eccentric_load = self.muscle_load[body_part_side].eccentric_load
    #                         else:
    #                             concentric_load = 0
    #                             eccentric_load = 0
    #
    #                         if functional_movement_load.muscle_action == MuscleAction.concentric or functional_movement_load.muscle_action == MuscleAction.isometric:
    #
    #                             compensated_concentric_load = concentric_load * factor
    #                             compensated_eccentric_load = 0
    #
    #                         else:
    #                             compensated_concentric_load = 0
    #                             compensated_eccentric_load = eccentric_load * factor
    #
    #                         functional_movement_body_part_side = BodyPartFunctionalMovement(body_part_side)
    #                         functional_movement_body_part_side.body_part_function = BodyPartFunction.synergist
    #
    #                         synergist_compensated_concentric_load = compensated_concentric_load / float(
    #                             len(functional_movement.parts_receiving_compensation))
    #                         synergist_compensated_eccentric_load = compensated_eccentric_load / float(
    #                             len(functional_movement.parts_receiving_compensation))
    #                         functional_movement_body_part_side.body_part_function = BodyPartFunction.synergist
    #                         functional_movement_body_part_side.compensated_concentric_load += synergist_compensated_concentric_load
    #                         functional_movement_body_part_side.compensated_eccentric_load += synergist_compensated_eccentric_load
    #                         functional_movement_body_part_side.compensating_causes_load.append(c)
    #                         functional_movement_body_part_side.compensation_source_load = CompensationSource.internal_processing
    #                         if body_part_side not in self.muscle_load:
    #                             self.muscle_load[body_part_side] = functional_movement_body_part_side
    #                         else:
    #                             self.muscle_load[
    #                                 body_part_side].compensated_concentric_load += synergist_compensated_concentric_load
    #                             self.muscle_load[
    #                                 body_part_side].compensated_eccentric_load += synergist_compensated_eccentric_load
    #                             self.muscle_load[body_part_side].compensating_causes_load.append(c)
    #                             self.muscle_load[
    #                                 body_part_side].compensation_source_load = CompensationSource.internal_processing

    def apply_load_to_functional_movements(self, injury_risk_dict, event_date, functional_movement_list, exercise_action):

        compensation_causing_prime_movers = self.get_compensating_body_parts(injury_risk_dict, event_date,
                                                                             functional_movement_list)

        # left_load = exercise_action.total_load_left
        # right_load = exercise_action.total_load_right
        left_load = exercise_action.tissue_load_left
        right_load = exercise_action.tissue_load_right

        for functional_movement_load in functional_movement_list:
            functional_movement = functional_movement_load.functional_movement

            if exercise_action.apply_instability:

                lower_stability_rating = exercise_action.lower_body_stability_rating / 2.0  # normalize
                upper_stability_rating = exercise_action.upper_body_stability_rating / 2.0  # normalize

                functional_movement_type = functional_movement.functional_movement_type

                if functional_movement_type in [FunctionalMovementType.ankle_dorsiflexion,
                                                FunctionalMovementType.ankle_plantar_flexion,
                                                FunctionalMovementType.inversion_of_the_foot,
                                                FunctionalMovementType.eversion_of_the_foot,
                                                FunctionalMovementType.tibial_internal_rotation,
                                                FunctionalMovementType.tibial_external_rotation,
                                                FunctionalMovementType.ankle_dorsiflexion_and_inversion,
                                                FunctionalMovementType.ankle_plantar_flexion_and_eversion]:
                    stability_rating = (.8 * lower_stability_rating) + (.2 * upper_stability_rating)

                elif functional_movement_type in [FunctionalMovementType.knee_flexion,
                                                  FunctionalMovementType.knee_extension]:
                    stability_rating = (.7 * lower_stability_rating) + (.3 * upper_stability_rating)

                elif functional_movement_type in [FunctionalMovementType.elbow_extension,
                                                  FunctionalMovementType.elbow_flexion]:
                    stability_rating = (.2 * lower_stability_rating) + (.8 * upper_stability_rating)

                elif functional_movement_type in [FunctionalMovementType.shoulder_horizontal_adduction,
                                                  FunctionalMovementType.shoulder_horizontal_abduction,
                                                  FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation,
                                                  FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation,
                                                  FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation,
                                                  FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation,
                                                  FunctionalMovementType.internal_rotation,
                                                  FunctionalMovementType.external_rotation,
                                                  FunctionalMovementType.scapular_depression,
                                                  FunctionalMovementType.scapular_elevation]:
                    stability_rating = (.3 * lower_stability_rating) + (.7 * upper_stability_rating)

                elif functional_movement_type in [FunctionalMovementType.hip_abduction,
                                                  FunctionalMovementType.hip_adduction,
                                                  FunctionalMovementType.hip_internal_rotation,
                                                  FunctionalMovementType.hip_external_rotation,
                                                  FunctionalMovementType.hip_extension,
                                                  FunctionalMovementType.hip_flexion,
                                                  FunctionalMovementType.hip_horizontal_abduction,
                                                  FunctionalMovementType.hip_horizontal_adduction]:
                    stability_rating = (.6 * lower_stability_rating) + (.4 * upper_stability_rating)

                elif functional_movement_type in [FunctionalMovementType.pelvic_anterior_tilt,
                                                  FunctionalMovementType.pelvic_posterior_tilt]:
                    stability_rating = (.5 * lower_stability_rating) + (.5 * upper_stability_rating)

                elif functional_movement_type in [FunctionalMovementType.trunk_flexion,
                                                  FunctionalMovementType.trunk_extension,
                                                  FunctionalMovementType.trunk_lateral_flexion,
                                                  FunctionalMovementType.trunk_rotation,
                                                  FunctionalMovementType.trunk_flexion_with_rotation,
                                                  FunctionalMovementType.trunk_extension_with_rotation]:
                    stability_rating = (.5 * lower_stability_rating) + (.5 * upper_stability_rating)
                else:
                    stability_rating = 0.0
            else:
                stability_rating = 0.0

            self.apply_load_to_list(functional_movement.prime_movers, functional_movement.priority,
                                    BodyPartFunction.prime_mover, functional_movement_load.muscle_action,
                                    left_load, right_load, stability_rating)

            self.apply_load_to_list(functional_movement.synergists, functional_movement.priority,
                                    BodyPartFunction.synergist, functional_movement_load.muscle_action,
                                    left_load, right_load, stability_rating)

            self.apply_load_to_list(functional_movement.stabilizers, functional_movement.priority,
                                    BodyPartFunction.stabilizer, functional_movement_load.muscle_action,
                                    left_load, right_load, stability_rating)

            self.apply_load_to_list(functional_movement.fixators, functional_movement.priority,
                                    BodyPartFunction.fixator, functional_movement_load.muscle_action,
                                    left_load, right_load, stability_rating)

            for c, severity in compensation_causing_prime_movers.items():
                if severity <= 2:
                    factor = .04
                elif 2 < severity <= 5:
                    factor = .08
                elif 5 < severity <= 8:
                    factor = .16
                else:
                    factor = .20

                for body_part_side in functional_movement.parts_receiving_compensation:
                    body_part_side_string = body_part_side.to_string()
                    if c.side == body_part_side.side or c.side == 0 or body_part_side.side == 0:
                        if body_part_side_string in self.muscle_load:
                            concentric_load = self.muscle_load[body_part_side_string].concentric_load
                            eccentric_load = self.muscle_load[body_part_side_string].eccentric_load
                        else:
                            concentric_load = StandardErrorRange(observed_value=0)
                            eccentric_load = StandardErrorRange(observed_value=0)

                        if functional_movement_load.muscle_action == MuscleAction.concentric or functional_movement_load.muscle_action == MuscleAction.isometric:
                            concentric_load.multiply(factor)
                            compensated_concentric_load = concentric_load
                            compensated_eccentric_load = StandardErrorRange(observed_value=0)

                        else:
                            eccentric_load.multiply(factor)
                            compensated_concentric_load = StandardErrorRange(observed_value=0)
                            compensated_eccentric_load = eccentric_load

                        functional_movement_body_part_side = BodyPartFunctionalMovement(body_part_side)
                        functional_movement_body_part_side.body_part_function = BodyPartFunction.synergist

                        compensated_concentric_load.divide(float(len(functional_movement.parts_receiving_compensation)))
                        synergist_compensated_concentric_load = compensated_concentric_load

                        compensated_eccentric_load.divide(float(len(functional_movement.parts_receiving_compensation)))
                        synergist_compensated_eccentric_load = compensated_eccentric_load

                        functional_movement_body_part_side.body_part_function = BodyPartFunction.synergist
                        functional_movement_body_part_side.compensated_concentric_load.add(synergist_compensated_concentric_load)
                        functional_movement_body_part_side.compensated_eccentric_load.add(synergist_compensated_eccentric_load)
                        functional_movement_body_part_side.compensating_causes_load.append(c)
                        #functional_movement_body_part_side.compensation_source_load = CompensationSource.internal_processing
                        if body_part_side_string not in self.muscle_load:
                            self.muscle_load[body_part_side_string] = functional_movement_body_part_side
                        else:
                            self.muscle_load[
                                body_part_side_string].compensated_concentric_load.add(synergist_compensated_concentric_load)
                            self.muscle_load[
                                body_part_side_string].compensated_eccentric_load.add(synergist_compensated_eccentric_load)
                            self.muscle_load[body_part_side_string].compensating_causes_load.append(c)
                            #self.muscle_load[
                            #    body_part_side_string].compensation_source_load = CompensationSource.internal_processing

    def apply_load_to_list(self, functional_movement_list, functional_movement_priority, target_body_part_function,
                           functional_movement_muscle_action, left_load, right_load, stability_rating):

        for body_part_side in functional_movement_list:
            functional_movement_body_part_side = BodyPartFunctionalMovement(body_part_side)
            functional_movement_body_part_side.body_part_function = target_body_part_function
            attributed_muscle_load = 0
            #load = 0
            load = StandardErrorRange()

            if body_part_side.side == 1 or body_part_side.side == 0:
                load.add(left_load)
            elif body_part_side.side == 2 or body_part_side.side == 0:
                load.add(right_load)

            if functional_movement_priority == 1:
                priority_ratio = 1.00
            elif functional_movement_priority == 2:
                priority_ratio = 0.6
            elif functional_movement_priority == 3:
                priority_ratio = 0.3
            elif functional_movement_priority == 4:
                priority_ratio = 0.15
            else:
                priority_ratio = 0.00

            if target_body_part_function == BodyPartFunction.prime_mover:
                muscle_ratio = 1.00
            elif target_body_part_function == BodyPartFunction.synergist:
                muscle_ratio = 0.60
            elif target_body_part_function == BodyPartFunction.stabilizer:
                muscle_ratio = (0.15 * stability_rating) + 0.05
            elif target_body_part_function == BodyPartFunction.fixator:
                muscle_ratio = (0.10 * stability_rating) + 0.20
            else:
                muscle_ratio = 0.0

            #attributed_muscle_load = load.multiply(priority_ratio * muscle_ratio)
            load.multiply(priority_ratio * muscle_ratio)
            attributed_muscle_load = load

                # self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load,
                #                               functional_movement_load.muscle_action)
            if attributed_muscle_load.observed_value is not None and attributed_muscle_load.observed_value > 0:
                body_part_side_string = body_part_side.to_string()
                if body_part_side_string in self.muscle_load:
                    if functional_movement_muscle_action == MuscleAction.concentric or functional_movement_muscle_action == MuscleAction.isometric:
                        self.muscle_load[body_part_side_string].concentric_load.add(attributed_muscle_load)
                    else:
                        self.muscle_load[body_part_side_string].eccentric_load.add(attributed_muscle_load)
                else:
                    self.muscle_load[body_part_side_string] = functional_movement_body_part_side
                    if functional_movement_muscle_action == MuscleAction.concentric or functional_movement_muscle_action == MuscleAction.isometric:
                        self.muscle_load[body_part_side_string].concentric_load.add(attributed_muscle_load)
                    else:
                        self.muscle_load[body_part_side_string].eccentric_load.add(attributed_muscle_load)
            # if body_part_side.side == 2 or body_part_side.side == 0:
            #     attributed_muscle_load = self.get_muscle_load(functional_movement_list_priority,
            #                                                   target_body_part_function, right_load,
            #                                                   stability_rating)
            #     self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load,
            #                                   functional_movement_load.muscle_action)

    # def update_muscle_dictionary(self, muscle, attributed_muscle_load, muscle_action):
    #     if attributed_muscle_load > 0:
    #         if muscle.body_part_side in self.muscle_load:
    #             if muscle_action == MuscleAction.concentric or muscle_action == MuscleAction.isometric:
    #                 self.muscle_load[muscle.body_part_side].concentric_load += attributed_muscle_load
    #             else:
    #                 self.muscle_load[muscle.body_part_side].eccentric_load += attributed_muscle_load
    #         else:
    #             self.muscle_load[muscle.body_part_side] = muscle
    #             if muscle_action == MuscleAction.concentric or muscle_action == MuscleAction.isometric:
    #                 self.muscle_load[muscle.body_part_side].concentric_load = attributed_muscle_load
    #             else:
    #                 self.muscle_load[muscle.body_part_side].eccentric_load = attributed_muscle_load

    # not using this just yet
    # def update_compensated_muscle_dictionary(self, muscle, attributed_muscle_load, muscle_action):
    #     if attributed_muscle_load > 0:
    #         if muscle.body_part_side in self.muscle_load:
    #             if muscle_action == MuscleAction.concentric or muscle_action == MuscleAction.isometric:
    #                 self.muscle_load[muscle.body_part_side].compensated_concentric_load += attributed_muscle_load
    #             else:
    #                 self.muscle_load[muscle.body_part_side].compensated_eccentric_load += attributed_muscle_load
    #         else:
    #             self.muscle_load[muscle.body_part_side] = muscle
    #             if muscle_action == MuscleAction.concentric or muscle_action == MuscleAction.isometric:
    #                 self.muscle_load[muscle.body_part_side].compensated_concentric_load = attributed_muscle_load
    #             else:
    #                 self.muscle_load[muscle.body_part_side].compensated_eccentric_load = attributed_muscle_load

    # def get_muscle_load(self, functional_movement_priority, muscle_role, load, stability_rating):
    #
    #     if functional_movement_priority == 1:
    #         priority_ratio = 1.00
    #     elif functional_movement_priority == 2:
    #         priority_ratio = 0.6
    #     elif functional_movement_priority == 3:
    #         priority_ratio = 0.3
    #     elif functional_movement_priority == 4:
    #         priority_ratio = 0.15
    #     else:
    #         priority_ratio = 0.00
    #
    #     if muscle_role == BodyPartFunction.prime_mover:
    #         muscle_ratio = 1.00
    #     elif muscle_role == BodyPartFunction.synergist:
    #         muscle_ratio = 0.60
    #     elif muscle_role == BodyPartFunction.stabilizer:
    #         muscle_ratio = (0.15 * stability_rating) + 0.05
    #     elif muscle_role == BodyPartFunction.fixator:
    #         muscle_ratio = (0.10 * stability_rating) + 0.20
    #     else:
    #         muscle_ratio = 0.0
    #
    #     scaled_load = load * priority_ratio * muscle_ratio
    #
    #     return scaled_load

    def get_compensating_body_parts(self, injury_risk_dict, event_date, functional_movement_list):

        affected_list = {}

        two_days_ago = event_date - timedelta(days=1)

        body_part_factory = BodyPartFactory()

        for functional_movement_load in functional_movement_list:
            functional_movement = functional_movement_load.functional_movement

            for body_part_side in functional_movement.prime_movers:
                #body_part_side_list = body_part_factory.get_body_part_side_list(f)
                #for body_part_side in body_part_side_list:
                # we are looking for recent statuses that we've determined, different than those reported in symptom intake
                if body_part_side in injury_risk_dict:
                    if (injury_risk_dict[body_part_side].last_weak_date is not None and
                            injury_risk_dict[body_part_side].last_weak_date == event_date):
                        if body_part_side not in affected_list:
                            affected_list[body_part_side] = 0
                    if (injury_risk_dict[body_part_side].last_muscle_spasm_date is not None and
                            injury_risk_dict[body_part_side].last_muscle_spasm_date == event_date):
                        if body_part_side not in affected_list:
                            affected_list[body_part_side] = 0
                        affected_list[body_part_side] = max(affected_list[body_part_side],
                                                              injury_risk_dict[body_part_side].get_muscle_spasm_severity(event_date))
                    if (injury_risk_dict[body_part_side].last_adhesions_date is not None and
                            injury_risk_dict[body_part_side].last_adhesions_date == event_date):
                        if body_part_side not in affected_list:
                            affected_list[body_part_side] = 0
                        affected_list[body_part_side] = max(affected_list[body_part_side],
                                                              injury_risk_dict[body_part_side].get_adhesions_severity(event_date))
                    if (injury_risk_dict[body_part_side].last_short_date is not None and
                            injury_risk_dict[body_part_side].last_short_date == event_date):
                        if body_part_side not in affected_list:
                            affected_list[body_part_side] = 0
                    if (injury_risk_dict[body_part_side].last_long_date is not None and
                            injury_risk_dict[body_part_side].last_long_date == event_date):
                        if body_part_side not in affected_list:
                            affected_list[body_part_side] = 0
                    if (injury_risk_dict[body_part_side].last_inhibited_date is not None and
                            injury_risk_dict[body_part_side].last_inhibited_date == event_date):
                        if body_part_side not in affected_list:
                            affected_list[body_part_side] = 0
                    if (injury_risk_dict[body_part_side].last_inflammation_date is not None and
                            injury_risk_dict[body_part_side].last_inflammation_date == event_date):
                        if body_part_side not in affected_list:
                            affected_list[body_part_side] = 0
                        affected_list[body_part_side] = max(affected_list[body_part_side],
                                                              injury_risk_dict[body_part_side].get_inflammation_severity(event_date))
                    if (injury_risk_dict[body_part_side].last_excessive_strain_date is not None and
                            injury_risk_dict[body_part_side].last_non_functional_overreaching_date is not None and
                            injury_risk_dict[body_part_side].last_excessive_strain_date >= two_days_ago and
                            injury_risk_dict[body_part_side].last_non_functional_overreaching_date >= two_days_ago):
                        if body_part_side not in affected_list:
                            affected_list[body_part_side] = 0

        return affected_list


class FunctionalMovementActivityMapping(object):
    def __init__(self, functional_movement_type, is_concentric, concentric_level, is_eccentric, eccentric_level):
        self.functional_movement_type = functional_movement_type
        self.is_concentric = is_concentric
        self.concentric_level = concentric_level
        self.is_eccentric = is_eccentric
        self.eccentric_level = eccentric_level
        self.prime_movers = []
        self.antagonists = []
        self.synergists = []
        self.parts_receiving_compensation = []
        self.muscle_load = {}

    def attribute_training_load(self, training_load, injury_risk_dict, event_date):

        prime_mover_ratio = 0.8
        synergist_ratio = 0.6

        compensation_causing_prime_movers = self.get_compensating_body_parts(injury_risk_dict, event_date)

        for c, severity in compensation_causing_prime_movers.items():
            if severity <= 2:
                factor = .04
            elif 2 < severity <= 5:
                factor = .08
            elif 5 < severity <= 8:
                factor = .16
            else:
                factor = .20

            compensated_concentric_load = training_load.plagiarize()
            compensated_eccentric_load = training_load.plagiarize()
            compensated_concentric_load.multiply(self.concentric_level * factor)
            compensated_eccentric_load.multiply(self.eccentric_level * factor)

            for s in self.parts_receiving_compensation:
                if c.side == s.body_part_side.side or c.side == 0 or s.body_part_side.side == 0:
                    synergist_compensated_concentric_load = compensated_concentric_load.plagiarize()
                    synergist_compensated_eccentric_load = compensated_eccentric_load.plagiarize()
                    synergist_compensated_concentric_load.divide(float(len(self.parts_receiving_compensation)))
                    synergist_compensated_eccentric_load.divide(float(len(self.parts_receiving_compensation)))
                    s.body_part_function = BodyPartFunction.synergist
                    s.compensated_concentric_load.add(synergist_compensated_concentric_load)
                    s.compensated_eccentric_load.add(synergist_compensated_eccentric_load)
                    s.compensating_causes_load.append(c)
                    #s.compensation_source_load = CompensationSource.internal_processing
                    if s.body_part_side not in self.muscle_load:
                        self.muscle_load[s.body_part_side] = s
                    else:
                        self.muscle_load[s.body_part_side].compensated_concentric_load.add(synergist_compensated_concentric_load)
                        self.muscle_load[s.body_part_side].compensated_eccentric_load.add(synergist_compensated_eccentric_load)
                        self.muscle_load[s.body_part_side].compensating_causes_load.append(c)
                        #self.muscle_load[s.body_part_side].compensation_source_load = CompensationSource.internal_processing

        for p in self.prime_movers:
            concentric_training_load = training_load.plagiarize()
            eccentric_training_load = training_load.plagiarize()
            concentric_training_load.multiply(self.concentric_level * prime_mover_ratio)
            eccentric_training_load.multiply(self.eccentric_level * prime_mover_ratio)
            attributed_concentric_load = concentric_training_load
            attributed_eccentric_load = eccentric_training_load
            p.body_part_function = BodyPartFunction.prime_mover
            p.concentric_load.add(attributed_concentric_load)
            p.eccentric_load.add(attributed_eccentric_load)
            if p.body_part_side not in self.muscle_load:
                self.muscle_load[p.body_part_side] = p
            else:
                self.muscle_load[p.body_part_side].concentric_load.add(p.concentric_load)
                self.muscle_load[p.body_part_side].eccentric_load.add(p.eccentric_load)

        for s in self.synergists:
            concentric_training_load = training_load.plagiarize()
            eccentric_training_load = training_load.plagiarize()
            concentric_training_load.multiply(self.concentric_level * prime_mover_ratio)
            eccentric_training_load.multiply(self.eccentric_level * prime_mover_ratio)
            attributed_concentric_load = concentric_training_load
            attributed_eccentric_load = eccentric_training_load
            s.body_part_function = BodyPartFunction.synergist
            s.concentric_load = attributed_concentric_load
            s.eccentric_load = attributed_eccentric_load
            if s.body_part_side not in self.muscle_load:
                self.muscle_load[s.body_part_side] = s
            else:
                self.muscle_load[s.body_part_side].concentric_load.add(s.concentric_load)
                self.muscle_load[s.body_part_side].eccentric_load.add(s.eccentric_load)

    def other_body_parts_affected(self, target_body_part, injury_risk_dict, event_date, prime_movers):

        # we want to look at both the prime movers and synergists
        body_part_list = []
        if prime_movers:
            body_part_list.extend(self.prime_movers)
        else:
            body_part_list.extend(self.synergists)

        affected_list = []

        filtered_list = [b for b in body_part_list if b.body_part_side.side == target_body_part.body_part_side.side]
        filtered_list = [b for b in filtered_list if b.body_part_side != target_body_part.body_part_side]

        two_days_ago = event_date - timedelta(days=1)

        for f in filtered_list:
            # we are looking for recent statuses that we've determined, different than those reported in symptom intake
            if f.body_part_side in injury_risk_dict:
                if (injury_risk_dict[f.body_part_side].last_weak_date is not None and
                        injury_risk_dict[f.body_part_side].last_weak_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_muscle_spasm_date is not None and
                        injury_risk_dict[f.body_part_side].last_muscle_spasm_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_adhesions_date is not None and
                        injury_risk_dict[f.body_part_side].last_adhesions_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_short_date is not None and
                        injury_risk_dict[f.body_part_side].last_short_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_long_date is not None and
                        injury_risk_dict[f.body_part_side].last_long_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_inhibited_date is not None and
                        injury_risk_dict[f.body_part_side].last_inhibited_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_inflammation_date is not None and
                        injury_risk_dict[f.body_part_side].last_inflammation_date == event_date):
                    affected_list.append(f.body_part_side)
                if (injury_risk_dict[f.body_part_side].last_excessive_strain_date is not None and
                        injury_risk_dict[f.body_part_side].last_non_functional_overreaching_date is not None and
                        injury_risk_dict[f.body_part_side].last_excessive_strain_date >= two_days_ago and
                        injury_risk_dict[f.body_part_side].last_non_functional_overreaching_date >= two_days_ago):
                    affected_list.append(f.body_part_side)

        return affected_list

    def get_compensating_body_parts(self, injury_risk_dict, event_date):

        affected_list = {}

        two_days_ago = event_date - timedelta(days=1)

        for f in self.prime_movers:
            # we are looking for recent statuses that we've determined, different than those reported in symptom intake
            if f.body_part_side in injury_risk_dict:
                if (injury_risk_dict[f.body_part_side].last_weak_date is not None and
                        injury_risk_dict[f.body_part_side].last_weak_date == event_date):
                    if f.body_part_side not in affected_list:
                        affected_list[f.body_part_side] = 0
                if (injury_risk_dict[f.body_part_side].last_muscle_spasm_date is not None and
                        injury_risk_dict[f.body_part_side].last_muscle_spasm_date == event_date):
                    if f.body_part_side not in affected_list:
                        affected_list[f.body_part_side] = 0
                    affected_list[f.body_part_side] = max(affected_list[f.body_part_side],
                                                          injury_risk_dict[f.body_part_side].get_muscle_spasm_severity(event_date))
                if (injury_risk_dict[f.body_part_side].last_adhesions_date is not None and
                        injury_risk_dict[f.body_part_side].last_adhesions_date == event_date):
                    if f.body_part_side not in affected_list:
                        affected_list[f.body_part_side] = 0
                    affected_list[f.body_part_side] = max(affected_list[f.body_part_side],
                                                          injury_risk_dict[f.body_part_side].get_adhesions_severity(event_date))
                if (injury_risk_dict[f.body_part_side].last_short_date is not None and
                        injury_risk_dict[f.body_part_side].last_short_date == event_date):
                    if f.body_part_side not in affected_list:
                        affected_list[f.body_part_side] = 0
                if (injury_risk_dict[f.body_part_side].last_long_date is not None and
                        injury_risk_dict[f.body_part_side].last_long_date == event_date):
                    if f.body_part_side not in affected_list:
                        affected_list[f.body_part_side] = 0
                if (injury_risk_dict[f.body_part_side].last_inhibited_date is not None and
                        injury_risk_dict[f.body_part_side].last_inhibited_date == event_date):
                    if f.body_part_side not in affected_list:
                        affected_list[f.body_part_side] = 0
                if (injury_risk_dict[f.body_part_side].last_inflammation_date is not None and
                        injury_risk_dict[f.body_part_side].last_inflammation_date == event_date):
                    if f.body_part_side not in affected_list:
                        affected_list[f.body_part_side] = 0
                    affected_list[f.body_part_side] = max(affected_list[f.body_part_side],
                                                          injury_risk_dict[f.body_part_side].get_inflammation_severity(event_date))
                if (injury_risk_dict[f.body_part_side].last_excessive_strain_date is not None and
                        injury_risk_dict[f.body_part_side].last_non_functional_overreaching_date is not None and
                        injury_risk_dict[f.body_part_side].last_excessive_strain_date >= two_days_ago and
                        injury_risk_dict[f.body_part_side].last_non_functional_overreaching_date >= two_days_ago):
                    if f.body_part_side not in affected_list:
                        affected_list[f.body_part_side] = 0

        return affected_list


class ActivityFunctionalMovementFactory(object):

    def get_functional_movement_mappings(self, sport_name):

        mapping = []

        # TODO: actually support sports
        # if sport_name == SportName.distance_running:
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.ankle_dorsiflexion, True, .0025, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.ankle_plantar_flexion, True, .019, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.inversion_of_the_foot, True, .0253, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.eversion_of_the_foot, False, 0, True, .03167))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.knee_flexion, True, 0.01, True, .079167))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.knee_extension, True, .1583, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.hip_adduction, False, 0, True, .0475))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.hip_abduction, True, .05067, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.hip_extension, True, .38, False, 0))
        mapping.append(
            FunctionalMovementActivityMapping(FunctionalMovementType.hip_flexion, True, .0375, True, .1583))

        return mapping


class FunctionalMovementFactory(object):

    def get_functional_movement_dictinary(self):

        dict = {}

        dict[FunctionalMovementType.ankle_dorsiflexion.value] = self.convert_ints_to_objects(self.get_ankle_dorsiflexion())
        dict[FunctionalMovementType.ankle_dorsiflexion_and_inversion.value] = self.convert_ints_to_objects(self.get_ankle_dorsiflexion_and_inversion())
        dict[FunctionalMovementType.ankle_plantar_flexion.value] = self.convert_ints_to_objects(self.get_ankle_plantar_flexion())
        dict[FunctionalMovementType.ankle_plantar_flexion_and_eversion.value] = self.convert_ints_to_objects(self.get_ankle_plantar_flexion_and_eversion())
        dict[FunctionalMovementType.inversion_of_the_foot.value] = self.convert_ints_to_objects(self.get_inversion_of_the_foot())
        dict[FunctionalMovementType.eversion_of_the_foot.value] = self.convert_ints_to_objects(self.get_eversion_of_the_foot())
        dict[FunctionalMovementType.knee_flexion.value] = self.convert_ints_to_objects(self.get_knee_flexion())
        dict[FunctionalMovementType.knee_extension.value] = self.convert_ints_to_objects(self.get_knee_extension())
        dict[FunctionalMovementType.tibial_external_rotation.value] = self.convert_ints_to_objects(self.get_tibial_external_rotation())
        dict[FunctionalMovementType.tibial_internal_rotation.value] = self.convert_ints_to_objects(self.get_tibial_internal_rotation())
        dict[FunctionalMovementType.hip_adduction.value] = self.convert_ints_to_objects(self.get_hip_adduction())
        dict[FunctionalMovementType.hip_horizontal_adduction.value] = self.convert_ints_to_objects(self.get_hip_horizontal_adduction())
        dict[FunctionalMovementType.hip_abduction.value] = self.convert_ints_to_objects(self.get_hip_abduction())
        dict[FunctionalMovementType.hip_horizontal_abduction.value] =  self.convert_ints_to_objects(self.get_hip_horizontal_abduction())
        dict[FunctionalMovementType.hip_internal_rotation.value] = self.convert_ints_to_objects(self.get_hip_internal_rotation())
        dict[FunctionalMovementType.hip_external_rotation.value] = self.convert_ints_to_objects(self.get_hip_external_rotation())
        dict[FunctionalMovementType.hip_extension.value] = self.convert_ints_to_objects(self.get_hip_extension())
        dict[FunctionalMovementType.hip_flexion.value] = self.convert_ints_to_objects(self.get_hip_flexion())
        dict[FunctionalMovementType.pelvic_anterior_tilt.value] = self.convert_ints_to_objects(self.get_pelvic_anterior_tilt())
        dict[FunctionalMovementType.pelvic_posterior_tilt.value] = self.convert_ints_to_objects(self.get_pelvic_posterior_tilt())
        dict[FunctionalMovementType.trunk_flexion.value] = self.convert_ints_to_objects(self.get_trunk_flexion())
        dict[FunctionalMovementType.trunk_extension.value] = self.convert_ints_to_objects(self.get_trunk_extension())
        dict[FunctionalMovementType.trunk_lateral_flexion.value] = self.convert_ints_to_objects(self.get_trunk_lateral_flexion())
        dict[FunctionalMovementType.trunk_rotation.value] = self.convert_ints_to_objects(self.get_trunk_rotation())
        dict[FunctionalMovementType.trunk_flexion_with_rotation.value] = self.convert_ints_to_objects(self.get_trunk_flexion_with_rotation())
        dict[FunctionalMovementType.trunk_extension_with_rotation.value] = self.convert_ints_to_objects(self.get_trunk_extension_with_rotation())
        dict[FunctionalMovementType.elbow_flexion.value] = self.convert_ints_to_objects(self.get_elbow_flexion())
        dict[FunctionalMovementType.elbow_extension.value] = self.convert_ints_to_objects(self.get_elbow_extension())
        dict[FunctionalMovementType.shoulder_horizontal_adduction.value] = self.convert_ints_to_objects(self.get_shoulder_horizontal_adduction_and_scapular_protraction())
        dict[FunctionalMovementType.shoulder_horizontal_abduction.value] = self.convert_ints_to_objects(self.get_shoulder_horizontal_abduction_and_scapular_retraction())
        dict[FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation.value] = self.convert_ints_to_objects(self.get_shoulder_flexion_and_scapular_upward_rotation())
        dict[FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation.value] = self.convert_ints_to_objects(self.get_shoulder_extension_and_scapular_downward_rotation())
        dict[FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation.value] = self.convert_ints_to_objects(self.get_shoulder_abduction_and_scapular_upward_rotation())
        dict[FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation.value] = self.convert_ints_to_objects(self.get_shoulder_adduction_and_scapular_downward_rotation())
        dict[FunctionalMovementType.internal_rotation.value] = self.convert_ints_to_objects(self.get_internal_rotation())
        dict[FunctionalMovementType.external_rotation.value] = self.convert_ints_to_objects(self.get_external_rotation())
        dict[FunctionalMovementType.scapular_elevation.value] = self.convert_ints_to_objects(self.get_scapular_elevation())
        dict[FunctionalMovementType.scapular_depression.value] = self.convert_ints_to_objects(self.get_scapular_depression())

        return dict

    def convert_ints_to_objects(self, functional_movement):

        functional_movement.prime_movers = self.convert_enum_list_to_body_part_list(
            functional_movement.prime_movers)
        functional_movement.stabilizers = self.convert_enum_list_to_body_part_list(
            functional_movement.stabilizers)
        functional_movement.synergists = self.convert_enum_list_to_body_part_list(
            functional_movement.synergists)
        functional_movement.fixators = self.convert_enum_list_to_body_part_list(
            functional_movement.fixators)
        functional_movement.parts_receiving_compensation = self.convert_enum_list_to_body_part_list(
            functional_movement.parts_receiving_compensation)

        return functional_movement

    def convert_enum_list_to_body_part_list(self, enum_list):

        body_part_factory = BodyPartFactory()
        body_part_list = []
        # if len(enum_list) > 0:
        #     body_part_list = [body_part_factory.get_body_part_side_list(e) for e in enum_list]
        #     body_part_list = [b for body_list in body_part_list for b in body_list]

        for p in range(0, len(enum_list)):
            body_part_side_list = body_part_factory.get_body_part_side_list(enum_list[p])
            body_part_list.extend(body_part_side_list)

        return body_part_list

    def get_functional_movement(self, movement_type):

        if movement_type == FunctionalMovementType.ankle_dorsiflexion:
            return self.get_ankle_dorsiflexion()
        elif movement_type == FunctionalMovementType.ankle_dorsiflexion_and_inversion:
            return self.get_ankle_dorsiflexion_and_inversion()
        elif movement_type == FunctionalMovementType.ankle_plantar_flexion:
            return self.get_ankle_plantar_flexion()
        elif movement_type == FunctionalMovementType.ankle_plantar_flexion_and_eversion:
            return self.get_ankle_plantar_flexion_and_eversion()
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
        elif movement_type == FunctionalMovementType.hip_horizontal_adduction:
            return self.get_hip_horizontal_adduction()
        elif movement_type == FunctionalMovementType.hip_abduction:
            return self.get_hip_abduction()
        elif movement_type == FunctionalMovementType.hip_horizontal_abduction:
            return self.get_hip_horizontal_abduction()
        elif movement_type == FunctionalMovementType.hip_internal_rotation:
            return self.get_hip_internal_rotation()
        elif movement_type == FunctionalMovementType.hip_external_rotation:
            return self.get_hip_external_rotation()
        elif movement_type == FunctionalMovementType.hip_extension:
            return self.get_hip_extension()
        elif movement_type == FunctionalMovementType.hip_flexion:
            return self.get_hip_flexion()

        elif movement_type == FunctionalMovementType.pelvic_anterior_tilt:
            return self.get_pelvic_anterior_tilt()
        elif movement_type == FunctionalMovementType.pelvic_posterior_tilt:
            return self.get_pelvic_posterior_tilt()

        elif movement_type == FunctionalMovementType.trunk_flexion:
            return self.get_trunk_flexion()
        elif movement_type == FunctionalMovementType.trunk_extension:
            return self.get_trunk_extension()
        elif movement_type == FunctionalMovementType.trunk_lateral_flexion:
            return self.get_trunk_lateral_flexion()
        elif movement_type == FunctionalMovementType.trunk_rotation:
            return self.get_trunk_rotation()
        elif movement_type == FunctionalMovementType.trunk_flexion_with_rotation:
            return self.get_trunk_flexion_with_rotation()
        elif movement_type == FunctionalMovementType.trunk_extension_with_rotation:
            return self.get_trunk_extension_with_rotation()

        elif movement_type == FunctionalMovementType.elbow_flexion:
            return self.get_elbow_flexion()
        elif movement_type == FunctionalMovementType.elbow_extension:
            return self.get_elbow_extension()

        elif movement_type == FunctionalMovementType.shoulder_horizontal_adduction:
            return self.get_shoulder_horizontal_adduction_and_scapular_protraction()
        elif movement_type == FunctionalMovementType.shoulder_horizontal_abduction:
            return self.get_shoulder_horizontal_abduction_and_scapular_retraction()
        elif movement_type == FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation:
            return self.get_shoulder_flexion_and_scapular_upward_rotation()
        elif movement_type == FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation:
            return self.get_shoulder_extension_and_scapular_downward_rotation()
        elif movement_type == FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation:
            return self.get_shoulder_abduction_and_scapular_upward_rotation()
        elif movement_type == FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation:
            return self.get_shoulder_adduction_and_scapular_downward_rotation()
        elif movement_type == FunctionalMovementType.internal_rotation:
            return self.get_internal_rotation()
        elif movement_type == FunctionalMovementType.external_rotation:
            return self.get_external_rotation()
        elif movement_type == FunctionalMovementType.scapular_elevation:
            return self.get_scapular_elevation()
        elif movement_type == FunctionalMovementType.scapular_depression:
            return self.get_scapular_depression()

    def get_ankle_fixators(self):

        return [44, 68, 47, 48, 53, 56, 61, 45, 46, 55, 59, 66, 57, 58]

    def get_knee_fixators(self):

        return [73, 74, 34, 35, 36, 70, 71, 66, 63, 64, 65, 40, 42]

    def get_hip_fixators(self):

        return [73, 74, 34, 35, 36, 70, 71, 26, 75, 69]

    def get_trunk_fixators(self):

        return [66, 63, 64, 65, 67, 60, 71, 72, 58, 59, 53, 54, 49, 50, 51, 52, 45, 46, 47, 48]

    def get_elbow_fixators(self):

        return [82, 81, 76, 78, 79, 85, 83, 84, 125, 21, 121, 122, 123, 124]

    def get_shoulder_fixators_1(self):

        return [73, 74, 34, 35, 36, 70, 71, 26, 75, 69, 125, 81, 76, 78, 79, 80]

    def get_shoulder_fixators_2(self):

        return [73, 74, 34, 35, 36, 67, 71, 26, 70, 75, 69]

    def get_ankle_dorsiflexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_dorsiflexion)
        functional_movement.prime_movers = [40]
        functional_movement.synergists = []
        functional_movement.antagonists = [41, 43, 44, 61]
        functional_movement.stabilizers = [41, 42]
        functional_movement.fixators = self.get_ankle_fixators()
        functional_movement.parts_receiving_compensation = []
        return functional_movement

    def get_ankle_dorsiflexion_and_inversion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_dorsiflexion_and_inversion)
        functional_movement.prime_movers = [40]
        functional_movement.synergists = []
        functional_movement.antagonists = [41, 43, 61]
        functional_movement.stabilizers = [41]
        functional_movement.fixators = self.get_ankle_fixators()
        functional_movement.parts_receiving_compensation = []
        return functional_movement

    def get_ankle_plantar_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_plantar_flexion)
        functional_movement.prime_movers = [43, 44, 61]
        functional_movement.synergists = [41, 42]
        functional_movement.antagonists = [40]
        functional_movement.stabilizers = [41, 42]
        functional_movement.fixators = self.get_ankle_fixators()
        functional_movement.parts_receiving_compensation = [41, 42]
        return functional_movement

    def get_ankle_plantar_flexion_and_eversion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_plantar_flexion_and_eversion)
        functional_movement.prime_movers = [43, 61]
        functional_movement.synergists = [41]
        functional_movement.antagonists = [40]
        functional_movement.stabilizers = [41, 42]
        functional_movement.fixators = self.get_ankle_fixators()
        functional_movement.parts_receiving_compensation = [41]
        return functional_movement

    def get_inversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.inversion_of_the_foot)
        functional_movement.prime_movers = [40, 42]
        functional_movement.synergists = [44]
        functional_movement.antagonists = [41, 43, 61]
        functional_movement.stabilizers = [41]
        functional_movement.fixators = self.get_ankle_fixators()
        functional_movement.parts_receiving_compensation = [44]
        return functional_movement

    def get_eversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.eversion_of_the_foot)
        functional_movement.prime_movers = [41]
        functional_movement.synergists = [43, 61]
        functional_movement.antagonists = [40, 42, 44]
        functional_movement.stabilizers = [40, 41, 42]
        functional_movement.fixators = self.get_ankle_fixators()
        functional_movement.parts_receiving_compensation = [43, 61]
        return functional_movement

    def get_tibial_external_rotation(self):
        functional_movement = FunctionalMovement(FunctionalMovementType.tibial_external_rotation)
        functional_movement.prime_movers = [45, 46]
        functional_movement.synergists = []
        functional_movement.antagonists = [47, 48]
        functional_movement.stabilizers = []
        functional_movement.fixators = self.get_ankle_fixators()
        functional_movement.parts_receiving_compensation = []
        return functional_movement

    def get_tibial_internal_rotation(self):
        functional_movement = FunctionalMovement(FunctionalMovementType.tibial_internal_rotation)
        functional_movement.prime_movers = [47, 48]
        functional_movement.synergists = [53, 68]
        functional_movement.antagonists = [45, 46]
        functional_movement.stabilizers = []
        functional_movement.fixators = self.get_ankle_fixators()
        functional_movement.parts_receiving_compensation = [53, 68]
        return functional_movement

    def get_knee_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_flexion)
        functional_movement.prime_movers = [45, 46, 47, 48]
        functional_movement.synergists = [44, 61, 53, 68]
        functional_movement.antagonists = [55, 56, 57, 58]
        functional_movement.stabilizers = [44, 68, 47, 48, 53, 56, 61, 45, 46, 55, 59, 66]
        functional_movement.fixators = self.get_knee_fixators()
        functional_movement.parts_receiving_compensation = [44, 61, 53]
        return functional_movement

    def get_knee_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_extension)
        functional_movement.prime_movers = [55, 56, 57, 58]
        functional_movement.synergists = []
        functional_movement.antagonists = [44, 61, 45, 46, 47, 48, 53, 68]
        functional_movement.stabilizers = [44, 47, 48, 53, 56, 61, 45, 46, 55, 59, 66]
        functional_movement.fixators = self.get_knee_fixators()
        functional_movement.parts_receiving_compensation = []
        return functional_movement

    def get_hip_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_extension)
        functional_movement.prime_movers = [66]
        functional_movement.synergists = [45, 47, 48, 51]
        functional_movement.antagonists = [50, 54, 58, 59, 71, 72, 49, 52]
        functional_movement.stabilizers = [60, 67]
        functional_movement.fixators = self.get_hip_fixators()
        functional_movement.parts_receiving_compensation = [45, 47, 48, 51]
        return functional_movement

    def get_hip_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_flexion)
        functional_movement.prime_movers = [71]
        functional_movement.synergists = [49, 50, 52, 54, 58, 59, 72]
        functional_movement.antagonists = [45, 47, 48, 51, 66]
        functional_movement.stabilizers = [60, 67]
        functional_movement.fixators = self.get_hip_fixators()
        functional_movement.parts_receiving_compensation = [49, 50, 52, 53, 58, 59, 65]
        return functional_movement

    def get_hip_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_internal_rotation)
        functional_movement.prime_movers = [65]
        functional_movement.synergists = [47, 48, 49, 50, 52, 54, 59, 63]
        functional_movement.antagonists = [45, 51, 60, 67, 64, 66]
        functional_movement.stabilizers = [60, 67]
        functional_movement.fixators = self.get_hip_fixators()
        functional_movement.parts_receiving_compensation = [46, 47, 48, 49, 50, 52, 53, 59, 63]
        return functional_movement

    def get_hip_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_external_rotation)
        functional_movement.prime_movers = [60]
        functional_movement.synergists = [45, 51, 67, 64, 66]
        functional_movement.antagonists = [47, 48, 49, 50, 52, 54, 59, 63, 65]
        functional_movement.stabilizers = [60, 67, 63, 64, 65]
        functional_movement.fixators = self.get_hip_fixators()
        functional_movement.parts_receiving_compensation = [45, 51, 67, 64, 66]
        return functional_movement

    def get_hip_abduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_abduction)
        functional_movement.prime_movers = [63, 64]
        functional_movement.synergists = [55, 59, 65, 66]
        functional_movement.antagonists = [49, 50, 51, 52, 53, 54, 67]
        functional_movement.stabilizers = [60, 67]
        functional_movement.fixators = self.get_hip_fixators()
        functional_movement.parts_receiving_compensation = [55, 59, 65, 66]
        return functional_movement

    def get_hip_adduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_adduction)
        functional_movement.prime_movers = [49, 50, 51, 52, 53, 54]
        functional_movement.synergists = [47, 48, 67, 66]
        functional_movement.antagonists = [55, 59, 63, 64, 65]
        functional_movement.stabilizers = [60, 67]
        functional_movement.fixators = self.get_hip_fixators()
        functional_movement.parts_receiving_compensation = [47, 48, 54, 67, 66]
        return functional_movement

    def get_hip_horizontal_abduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_horizontal_abduction)
        functional_movement.prime_movers = [60]
        functional_movement.synergists = [59, 67, 63, 64, 65, 66]
        functional_movement.antagonists = [49, 50, 51, 52, 53, 54]
        functional_movement.stabilizers = [54, 60, 67, 63, 64, 65]
        functional_movement.fixators = self.get_hip_fixators()
        functional_movement.parts_receiving_compensation = [59, 67, 63, 64, 65, 66]
        return functional_movement

    def get_hip_horizontal_adduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_horizontal_adduction)
        functional_movement.prime_movers = [49, 50, 52, 54]
        functional_movement.synergists = [51]
        functional_movement.antagonists = [59, 67, 60, 63, 64, 65, 66]
        functional_movement.stabilizers = [54, 60, 67, 63, 64, 65]
        functional_movement.fixators = self.get_hip_fixators()
        functional_movement.parts_receiving_compensation = [47, 48, 54, 67, 66]
        return functional_movement

    def get_pelvic_anterior_tilt(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.pelvic_anterior_tilt)
        functional_movement.prime_movers = [58, 71, 72, 26, 21]
        functional_movement.synergists = [34, 53, 49, 50, 52, 54, 59]
        functional_movement.antagonists = [74, 75]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71, 60, 63, 64, 65]
        functional_movement.parts_receiving_compensation = [54, 59]
        return functional_movement

    def get_pelvic_posterior_tilt(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.pelvic_posterior_tilt)
        functional_movement.prime_movers = [74, 75]
        functional_movement.synergists = [45, 69, 51, 66]
        functional_movement.antagonists = [58, 71, 72, 26, 70, 21]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71, 60, 63, 64, 65]
        functional_movement.parts_receiving_compensation = [45, 69]
        return functional_movement

    def get_trunk_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_flexion)
        functional_movement.prime_movers = [75]
        functional_movement.synergists = [71, 74, 69]
        functional_movement.antagonists = [26, 21]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [71, 74, 69]
        return functional_movement

    def get_trunk_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_extension)
        functional_movement.prime_movers = [26, 21, 34]
        functional_movement.synergists = []
        functional_movement.antagonists = [71, 74, 69, 75]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = []
        return functional_movement

    def get_trunk_lateral_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_lateral_flexion)
        functional_movement.prime_movers = [70]
        functional_movement.synergists = [26, 21, 74, 69]
        functional_movement.antagonists = [26, 70, 21, 74, 69]
        functional_movement.stabilizers = [58, 71, 73, 74, 34, 35, 36, 70]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [26, 21, 74, 69]
        return functional_movement

    def get_trunk_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_rotation)
        functional_movement.prime_movers = [74, 69]
        functional_movement.synergists = [21, 71]
        functional_movement.antagonists = [69, 74]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [21, 71]
        return functional_movement

    def get_trunk_flexion_with_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_flexion_with_rotation)
        functional_movement.prime_movers = [74, 75, 69]
        functional_movement.synergists = [21, 71]
        functional_movement.antagonists = [69, 26, 74]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [21, 71]
        return functional_movement

    def get_trunk_extension_with_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_extension_with_rotation)
        functional_movement.prime_movers = [26, 74, 69]
        functional_movement.synergists = [21, 71]
        functional_movement.antagonists = [71, 69, 75, 74]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [21, 71]
        return functional_movement

    def get_elbow_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.elbow_flexion)
        functional_movement.prime_movers = [126]
        functional_movement.synergists = [127, 128]
        functional_movement.antagonists = [130, 131, 132, 32]
        functional_movement.stabilizers = [33]
        functional_movement.fixators = self.get_elbow_fixators()
        functional_movement.parts_receiving_compensation = [127, 128]
        return functional_movement

    def get_elbow_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.elbow_extension)
        functional_movement.prime_movers = [130, 131, 132]
        functional_movement.synergists = [32]
        functional_movement.antagonists = [126, 127, 128]
        functional_movement.stabilizers = [33]
        functional_movement.fixators = self.get_elbow_fixators()
        functional_movement.parts_receiving_compensation = [32]
        return functional_movement

    def get_shoulder_horizontal_adduction_and_scapular_protraction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_horizontal_adduction)
        functional_movement.prime_movers = [125, 82]
        functional_movement.synergists = [83, 81]
        functional_movement.antagonists = [78, 80, 85]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [83, 81]
        return functional_movement

    def get_shoulder_horizontal_abduction_and_scapular_retraction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_horizontal_abduction)
        functional_movement.prime_movers = [78, 85]
        functional_movement.synergists = [80]
        functional_movement.antagonists = [83, 125, 81, 82]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [80]
        return functional_movement

    def get_shoulder_flexion_and_scapular_upward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation)
        functional_movement.prime_movers = [83, 125]
        functional_movement.synergists = [76, 79, 82, 127, 129]
        functional_movement.antagonists = [21, 77, 80, 120, 85, 81, 132]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [76, 79, 82, 127, 129]
        return functional_movement

    def get_shoulder_extension_and_scapular_downward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation)
        functional_movement.prime_movers = [21, 81]
        functional_movement.synergists = [77, 80, 120, 85, 132]
        functional_movement.antagonists = [76, 79, 83, 125, 82, 127, 129]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [77, 80, 120, 85, 132]
        return functional_movement

    def get_shoulder_abduction_and_scapular_upward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation)
        functional_movement.prime_movers = [83, 84, 125]
        functional_movement.synergists = [76, 79, 121]
        functional_movement.antagonists = [21, 77, 80, 120, 122, 123, 124, 81, 82, 129, 132]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [76, 79, 121]
        return functional_movement

    def get_shoulder_adduction_and_scapular_downward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation)
        functional_movement.prime_movers = [21, 81]
        functional_movement.synergists = [77, 80, 120, 122, 123, 124, 82, 129, 132]
        functional_movement.antagonists = [76, 79, 121, 83, 84, 125]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [77, 80, 120, 122, 123, 124, 82, 129, 132]
        return functional_movement

    def get_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.internal_rotation)
        functional_movement.prime_movers = [122]
        functional_movement.synergists = [21, 120, 83, 82]
        functional_movement.antagonists = [123, 124, 85]
        functional_movement.stabilizers = [121, 122, 123, 124]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [21, 120, 83, 82]
        return functional_movement

    def get_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.external_rotation)
        functional_movement.prime_movers = [123, 124]
        functional_movement.synergists = [85]
        functional_movement.antagonists = [21, 120, 122, 83, 82]
        functional_movement.stabilizers = [121, 122, 123, 124]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [85]
        return functional_movement

    def get_scapular_elevation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.scapular_elevation)
        functional_movement.prime_movers = [76]
        functional_movement.synergists = [77, 80]
        functional_movement.antagonists = [79, 81]
        functional_movement.stabilizers = [125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_2()
        functional_movement.parts_receiving_compensation = [77, 80]
        return functional_movement

    def get_scapular_depression(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.scapular_depression)
        functional_movement.prime_movers = [79]
        functional_movement.synergists = [81]
        functional_movement.antagonists = [76, 77, 80]
        functional_movement.stabilizers = [125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_2()
        functional_movement.parts_receiving_compensation = [81]
        return functional_movement
