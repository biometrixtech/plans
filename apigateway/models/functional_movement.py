from enum import Enum
from collections import namedtuple
from models.session import SessionType
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.body_parts import BodyPartFactory
from datetime import timedelta
from models.functional_movement_mapping import ActionMappingMovementFactory
from models.movement_actions import MuscleAction
from models.functional_movement_type import FunctionalMovementType


# class FunctionalMovementType(Enum):
#     ankle_dorsiflexion = 0
#     ankle_plantar_flexion = 1
#     inversion_of_the_foot = 2
#     eversion_of_the_foot = 3
#     knee_flexion = 4
#     knee_extension = 5
#     tibial_external_rotation = 6
#     tibial_internal_rotation = 7
#     hip_adduction = 8
#     hip_abduction = 9
#     hip_internal_rotation = 10
#     hip_external_rotation = 11
#     hip_extension = 12
#     hip_flexion = 13
#     pelvic_anterior_tilt = 14
#     pelvic_posterior_tilt = 15
#     trunk_flexion = 16
#     trunk_extension = 17
#     trunk_lateral_flexion = 18
#     trunk_rotation = 19
#     trunk_flexion_with_rotation = 20
#     trunk_extension_with_rotation = 21
#     elbow_flexion = 22
#     elbow_extension = 23
#     shoulder_horizontal_adduction = 24
#     shoulder_horizontal_abduction = 25
#     shoulder_flexion_and_scapular_upward_rotation = 26
#     shoulder_extension_and_scapular_downward_rotation = 27
#     shoulder_abduction_and_scapular_upward_rotation = 28
#     shoulder_adduction_and_scapular_downward_rotation = 29
#     internal_rotation = 30
#     external_rotation = 31
#     scapular_elevation = 32
#     scapular_depression = 33


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


class FunctionalMovement(object):
    def __init__(self, functional_movement_type, priority=0):
        self.functional_movement_type = functional_movement_type
        self.priority = priority
        self.prime_movers = []
        self.antagonists = []
        self.synergists = []
        self.stabilizers = []
        self.parts_receiving_compensation = []


class CompensationSource(Enum):
    internal_processing = 0
    movement_patterns_3s = 1


class BodyPartFunctionalMovement(object):
    def __init__(self, body_part_side):
        self.body_part_side = body_part_side
        self.concentric_volume = 0
        self.eccentric_volume = 0
        self.compensated_concentric_volume = 0
        self.compensated_eccentric_volume = 0
        self.compensating_causes_volume = []
        self.concentric_intensity = 0
        self.eccentric_intensity = 0
        self.compensated_concentric_intensity = 0
        self.compensated_eccentric_intensity = 0
        self.compensating_causes_intensity = []
        self.concentric_ramp = 0.0
        self.eccentric_ramp = 0.0
        self.is_compensating = False
        self.compensation_source_volume = None
        self.compensation_source_intensity = None
        self.body_part_function = None
        self.inhibited = 0
        self.weak = 0
        self.tight = 0
        self.inflamed = 0
        self.long = 0

    def total_volume(self):

        return self.concentric_volume + self.eccentric_volume + self.compensated_concentric_volume + self.compensated_eccentric_volume

    def total_intensity(self):

        return max(self.concentric_intensity, self.eccentric_intensity, self.compensated_concentric_intensity, self.compensated_eccentric_intensity)

    def __hash__(self):
        return hash((self.body_part_side.body_part_location.value, self.body_part_side.side))

    def __eq__(self, other):
        return self.body_part_side.body_part_location == other.body_part_side.body_part_location and self.body_part_side.side == other.body_part_side.side

    def __ne__(self, other):
        # Not strictly necessary, but to avoid having both x==y and x!=y
        # True at the same time
        return not (self == other)


class SessionFunctionalMovement(object):
    def __init__(self, session, injury_risk_dict):
        self.body_parts = []
        self.session = session
        self.functional_movement_mappings = []
        self.injury_risk_dict = injury_risk_dict

    def process(self, event_date, load_stats):
        activity_factory = ActivityFunctionalMovementFactory()
        action_factory = ActionMappingMovementFactory()
        movement_factory = FunctionalMovementFactory()

        if self.session.session_type == SessionType.mixed_activity:

            for section in self.session.workout_program_module.workout_sections:
                for exercise in section.exercises:
                    for primary_action in exercise.primary_actions:
                        self.functional_movement_mappings.extend(action_factory.get_functional_movement_mappings(primary_action))
                    for secondary_action in exercise.secondary_actions:
                        self.functional_movement_mappings.extend(action_factory.get_functional_movement_mappings(secondary_action))

        else:

            self.functional_movement_mappings = activity_factory.get_functional_movement_mappings(self.session.sport_name)

        for m in self.functional_movement_mappings:
            functional_movement = movement_factory.get_functional_movement(m.functional_movement_type)
            for p in functional_movement.prime_movers:
                body_part_side_list = self.get_body_part_side_list(p)
                for b in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(b)
                    m.prime_movers.append(functional_movement_body_part_side)

            for a in functional_movement.synergists:
                body_part_side_list = self.get_body_part_side_list(a)
                for b in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(b)
                    m.synergists.append(functional_movement_body_part_side)

            for a in functional_movement.parts_receiving_compensation:
                body_part_side_list = self.get_body_part_side_list(a)
                for b in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(b)
                    m.parts_receiving_compensation.append(functional_movement_body_part_side)

            m.attribute_training_volume(self.session.training_load(load_stats), self.injury_risk_dict, event_date)
            # TODO - ensure we're using the correct (and all) intensity measures
            if self.session.session_RPE is not None:
                m.attribute_intensity(self.session.session_RPE, self.injury_risk_dict, event_date)

        #self.aggregate_body_parts()

        return self.session

    def aggregate_body_parts(self):

        body_part_sides = {}

        for m in self.functional_movement_mappings:
            for p in m.prime_movers:
                if p not in body_part_sides:
                    body_part_sides[p] = p
                else:
                    body_part_sides[p].concentric_volume += p.concentric_volume
                    body_part_sides[p].eccentric_volume += p.eccentric_volume
                    body_part_sides[p].concentric_intensity = max(p.concentric_intensity, body_part_sides[p].concentric_intensity)
                    body_part_sides[p].eccentric_intensity = max(p.eccentric_intensity, body_part_sides[p].eccentric_intensity)

        self.body_parts = list(body_part_sides.values())

    def get_body_part_side_list(self, body_part_enum):

        body_part_side_list = []

        body_part_factory = BodyPartFactory()
        #body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(body_part_enum), None))
        bilateral = body_part_factory.get_bilateral(BodyPartLocation(body_part_enum))

        # if bilateral:
        #     body_part_side = BodyPartSide(BodyPartLocation(p), side)
        # else:
        #     body_part_side = BodyPartSide(BodyPartLocation(p), 0)
        if not bilateral:
            sides = [0]
        else:
            sides = [1, 2]
        for side in sides:
            body_part_side = BodyPartSide(BodyPartLocation(body_part_enum), side=side)
            body_part_side_list.append(body_part_side)

        return body_part_side_list


class FunctionalMovementActionMapping(object):
    def __init__(self, exercise_action):
        self.exercise_action = exercise_action
        self.hip_joint_functional_movements = []
        self.knee_joint_functional_movements = []
        self.ankle_joint_functional_movements = []
        self.trunk_joint_functional_movements = []
        self.shoulder_scapula_joint_functional_movements = []
        self.elbow_joint_functional_movements = []
        self.muscle_load = {}

        self.set_functional_movements()
        self.set_muscle_load()

    def set_functional_movements(self):

        if self.exercise_action is not None:
            self.hip_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.hip_joint_action)
            self.knee_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.knee_joint_action)
            self.ankle_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.ankle_joint_action)
            self.trunk_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.trunk_joint_action)
            self.shoulder_scapula_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.shoulder_scapula_joint_action)
            self.elbow_joint_functional_movements = self.get_functional_movements_for_joint_action(self.exercise_action.elbow_joint_action)

    def get_functional_movements_for_joint_action(self, target_joint_action_list):

        movement_factory = FunctionalMovementFactory()
        pairs = FunctionalMovementPairs()

        functional_movement_list = []

        for target_joint_action in target_joint_action_list:
            functional_movement_type = pairs.get_functional_movement_for_muscle_action(
                self.exercise_action.primary_muscle_action, target_joint_action.joint_action)

            functional_movement = movement_factory.get_functional_movement(functional_movement_type)
            functional_movement.priority = target_joint_action.priority
            functional_movement_list.append(functional_movement)

        return functional_movement_list

    def set_muscle_load(self):

        self.apply_load_to_functional_movements(self.hip_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.knee_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.ankle_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.trunk_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.shoulder_scapula_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.elbow_joint_functional_movements, self.exercise_action)

    def get_matching_stability_rating(self, functional_movement_type, lower_stability_rating, upper_stability_rating):

        if functional_movement_type in [FunctionalMovementType.ankle_dorsiflexion,
                                        FunctionalMovementType.ankle_plantar_flexion,
                                        FunctionalMovementType.inversion_of_the_foot,
                                        FunctionalMovementType.eversion_of_the_foot,
                                        FunctionalMovementType.knee_flexion,
                                        FunctionalMovementType.knee_extension,
                                        FunctionalMovementType.tibial_internal_rotation,
                                        FunctionalMovementType.tibial_external_rotation]:
            return lower_stability_rating
        elif functional_movement_type in [FunctionalMovementType.elbow_extension,
                                          FunctionalMovementType.elbow_flexion,
                                          FunctionalMovementType.shoulder_horizontal_adduction,
                                          FunctionalMovementType.shoulder_horizontal_abduction,
                                          FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation,
                                          FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation,
                                          FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation,
                                          FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation,
                                          FunctionalMovementType.internal_rotation,
                                          FunctionalMovementType.external_rotation,
                                          FunctionalMovementType.scapular_depression,
                                          FunctionalMovementType.scapular_elevation]:
            return upper_stability_rating
        elif functional_movement_type in [FunctionalMovementType.hip_abduction,
                                          FunctionalMovementType.hip_adduction,
                                          FunctionalMovementType.hip_internal_rotation,
                                          FunctionalMovementType.hip_external_rotation,
                                          FunctionalMovementType.hip_extension,
                                          FunctionalMovementType.hip_flexion,
                                          FunctionalMovementType.pelvic_anterior_tilt,
                                          FunctionalMovementType.pelvic_posterior_tilt,
                                          FunctionalMovementType.trunk_flexion,
                                          FunctionalMovementType.trunk_extension,
                                          FunctionalMovementType.trunk_lateral_flexion,
                                          FunctionalMovementType.trunk_rotation,
                                          FunctionalMovementType.trunk_flexion_with_rotation,
                                          FunctionalMovementType.trunk_extension_with_rotation]:
            return max(lower_stability_rating, upper_stability_rating)

    def apply_load_to_functional_movements(self, functional_movement_list, exercise_action):

        body_part_factory = BodyPartFactory()

        left_load = exercise_action.total_left_load
        right_load = exercise_action.total_right_load

        for functional_movement in functional_movement_list:

            stability_rating = self.get_matching_stability_rating(functional_movement, exercise_action)

            for p in functional_movement.prime_movers:
                body_part_side_list = body_part_factory.get_body_part_side_list(p)
                for body_part_side in body_part_side_list:
                    if body_part_side.side == 1 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.prime_mover, left_load, stability_rating)
                        self.update_muscle_dictionary(body_part_side, attributed_muscle_load)
                    if body_part_side.side == 2 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.prime_mover, right_load, stability_rating)
                        self.update_muscle_dictionary(body_part_side, attributed_muscle_load)
            for s in functional_movement.synergists:
                body_part_side_list = body_part_factory.get_body_part_side_list(s)
                for body_part_side in body_part_side_list:
                    if body_part_side.side == 1 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.synergist, left_load, stability_rating)
                        self.update_muscle_dictionary(body_part_side, attributed_muscle_load)
                    if body_part_side.side == 2 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.synergist, right_load, stability_rating)
                        self.update_muscle_dictionary(body_part_side, attributed_muscle_load)
            for t in functional_movement.stabilizers:
                body_part_side_list = body_part_factory.get_body_part_side_list(t)
                for body_part_side in body_part_side_list:
                    if body_part_side.side == 1 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.stabilizer, left_load, stability_rating)
                        self.update_muscle_dictionary(body_part_side, attributed_muscle_load)
                    if body_part_side.side == 2 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.stabilizer, right_load, stability_rating)
                        self.update_muscle_dictionary(body_part_side, attributed_muscle_load)

    def update_muscle_dictionary(self, muscle, attributed_muscle_load):
        if muscle in self.muscle_load:
            self.muscle_load[muscle] += attributed_muscle_load
        else:
            self.muscle_load[muscle] = attributed_muscle_load

    def get_muscle_load(self, functional_movement_priority, muscle_role, load, stability_rating):

        if functional_movement_priority == 1:
            priority_ratio = 1.00
        elif functional_movement_priority == 2:
            priority_ratio = 0.6
        elif functional_movement_priority == 3:
            priority_ratio = 0.3
        else:
            priority_ratio = 0.00

        if muscle_role == BodyPartFunction.prime_mover:
            muscle_ratio = 1.00
        elif muscle_role == BodyPartFunction.synergist:
            muscle_ratio = 0.60
        elif muscle_role == BodyPartFunction.stabilizer:
            muscle_ratio = (0.15 * stability_rating) + 0.05
        else:
            muscle_ratio = 0.0

        scaled_load = load * priority_ratio * muscle_ratio

        return scaled_load


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

    def attribute_training_volume(self, training_volume, injury_risk_dict, event_date):

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

            compensated_concentric_volume = training_volume * self.concentric_level * factor
            compensated_eccentric_volume = training_volume * self.eccentric_level * factor

            for s in self.parts_receiving_compensation:
                if c.side == s.body_part_side.side or c.side == 0 or s.body_part_side.side == 0:
                    synergist_compensated_concentric_volume = compensated_concentric_volume / float(len(self.parts_receiving_compensation))
                    synergist_compensated_eccentric_volume = compensated_eccentric_volume / float(len(self.parts_receiving_compensation))
                    s.body_part_function = BodyPartFunction.synergist
                    s.compensated_concentric_volume += synergist_compensated_concentric_volume
                    s.compensated_eccentric_volume += synergist_compensated_eccentric_volume
                    s.compensating_causes_volume.append(c)
                    s.compensation_source_volume = CompensationSource.internal_processing

        for p in self.prime_movers:
            attributed_concentric_volume = training_volume * self.concentric_level * prime_mover_ratio
            attributed_eccentric_volume = training_volume * self.eccentric_level * prime_mover_ratio
            p.body_part_function = BodyPartFunction.prime_mover
            p.concentric_volume = attributed_concentric_volume
            p.eccentric_volume = attributed_eccentric_volume

        for s in self.synergists:
            attributed_concentric_volume = training_volume * self.concentric_level * synergist_ratio
            attributed_eccentric_volume = training_volume * self.eccentric_level * synergist_ratio
            s.body_part_function = BodyPartFunction.synergist
            s.concentric_volume = attributed_concentric_volume
            s.eccentric_volume = attributed_eccentric_volume

    def attribute_intensity(self, intensity, injury_risk_dict, event_date):

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

            compensated_concentric_intensity = intensity * self.concentric_level * factor
            compensated_eccentric_intensity = intensity * self.eccentric_level * factor

            for s in self.parts_receiving_compensation:
                if c.side == s.body_part_side.side or c.side == 0 or s.body_part_side.side == 0:
                    synergist_compensated_concentric_intensity = compensated_concentric_intensity / float(len(self.parts_receiving_compensation))
                    synergist_compensated_eccentric_intensity = compensated_eccentric_intensity / float(len(self.parts_receiving_compensation))
                    s.body_part_function = BodyPartFunction.synergist
                    s.compensated_concentric_intensity = synergist_compensated_concentric_intensity  # note this isn't a max or additive; one time only
                    s.compensated_eccentric_intensity = synergist_compensated_eccentric_intensity
                    s.compensating_causes_intensity.append(c)
                    s.compensation_source_intensity = CompensationSource.internal_processing

        for p in self.prime_movers:
            attributed_concentric_intensity = intensity * self.concentric_level * prime_mover_ratio
            attributed_eccentric_intensity = intensity * self.eccentric_level * prime_mover_ratio
            p.body_part_function = BodyPartFunction.prime_mover
            p.concentric_intensity = attributed_concentric_intensity
            p.eccentric_intensity = attributed_eccentric_intensity

        for s in self.synergists:
            attributed_concentric_intensity = intensity * self.concentric_level * synergist_ratio
            attributed_eccentric_intensity = intensity * self.eccentric_level * synergist_ratio
            s.body_part_function = BodyPartFunction.synergist
            s.concentric_intensity = attributed_concentric_intensity
            s.eccentric_intensity = attributed_eccentric_intensity

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

        #affected_list = list(set(affected_list))

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
        # elif movement_type == FunctionalMovementType.tibial_external_rotation:
        #     return self.get_tibial_external_rotation()
        # elif movement_type == FunctionalMovementType.tibial_internal_rotation:
        #     return self.get_tibial_internal_rotation()
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
        elif movement_type == FunctionalMovementType.pelvic_anterior_tilt:
            return self.get_pelvic_anterior_tilt()
        elif movement_type == FunctionalMovementType.pelvic_posterior_tilt:
            return self.get_pelvic_posterior_tilt()
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

    def get_ankle_dorsiflexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_dorsiflexion)
        functional_movement.prime_movers = [40]
        functional_movement.antagonists = [41, 43, 44, 61]
        functional_movement.synergists = []
        functional_movement.parts_receiving_compensation = []
        return functional_movement

    def get_ankle_plantar_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.ankle_plantar_flexion)
        functional_movement.prime_movers = [43, 44, 61]
        functional_movement.antagonists = [40]
        functional_movement.synergists = [41, 42]
        functional_movement.parts_receiving_compensation = [41, 42]
        return functional_movement

    def get_inversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.inversion_of_the_foot)
        functional_movement.prime_movers = [40, 42]
        functional_movement.antagonists = [41, 43, 61]
        functional_movement.synergists = [44]
        functional_movement.parts_receiving_compensation = [44]
        return functional_movement

    def get_eversion_of_the_foot(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.eversion_of_the_foot)
        functional_movement.prime_movers = [41]
        functional_movement.antagonists = [40, 42, 44]
        functional_movement.synergists = [43, 61]
        functional_movement.parts_receiving_compensation = [43, 61]
        return functional_movement

    def get_knee_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_flexion)
        functional_movement.prime_movers = [45, 46, 47, 48]
        functional_movement.antagonists = [55, 56, 57, 58]
        functional_movement.synergists = [44, 61, 53]
        functional_movement.parts_receiving_compensation = [44, 61, 53]
        return functional_movement

    def get_knee_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.knee_extension)
        functional_movement.prime_movers = [55, 56, 57, 58]
        functional_movement.antagonists = [44, 61, 45, 46, 47, 48, 53]
        functional_movement.synergists = []
        functional_movement.parts_receiving_compensation = []
        return functional_movement

    def get_hip_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_extension)
        functional_movement.prime_movers = [66]
        functional_movement.antagonists = [50, 54, 58, 59, 71]
        functional_movement.synergists = [45, 47, 48, 51]
        functional_movement.parts_receiving_compensation = [45, 47, 48, 51]
        return functional_movement

    def get_hip_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_flexion)
        functional_movement.prime_movers = [54, 71]
        functional_movement.antagonists = [45, 47, 48, 51, 66]
        functional_movement.synergists = [49, 50, 52, 53, 58, 59, 65]
        functional_movement.parts_receiving_compensation = [49, 50, 52, 53, 58, 59, 65]
        return functional_movement

    def get_hip_adduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_adduction)
        functional_movement.prime_movers = [49, 50, 51, 52, 53]
        functional_movement.antagonists = [55, 59, 63, 64, 65]
        functional_movement.synergists = [47, 48, 54, 67, 66]
        functional_movement.parts_receiving_compensation = [47, 48, 54, 67, 66]
        return functional_movement

    def get_hip_abduction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_abduction)
        functional_movement.prime_movers = [63, 64]
        functional_movement.antagonists = [49, 50, 51, 52, 53, 54, 67]
        functional_movement.synergists = [55, 59, 65, 66]
        functional_movement.parts_receiving_compensation = [55, 59, 65, 66]
        return functional_movement

    def get_hip_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_internal_rotation)
        functional_movement.prime_movers = [54, 65]
        functional_movement.antagonists = [45, 51, 67, 64, 66]
        functional_movement.synergists = [46, 47, 48, 49, 50, 52, 53, 59, 63]
        functional_movement.parts_receiving_compensation = [46, 47, 48, 49, 50, 52, 53, 59, 63]
        return functional_movement

    def get_hip_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.hip_external_rotation)
        functional_movement.prime_movers = [60]
        functional_movement.antagonists = [47, 48, 49, 50, 52, 53, 54, 59, 63, 65]
        functional_movement.synergists = [45, 51, 67, 64, 66]
        functional_movement.parts_receiving_compensation = [45, 51, 67, 64, 66]
        return functional_movement

    def get_pelvic_anterior_tilt(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.pelvic_anterior_tilt)
        functional_movement.prime_movers = [58, 71, 72, 26, 70, 21]
        functional_movement.antagonists = [74, 75]
        functional_movement.synergists = [54, 59]
        functional_movement.parts_receiving_compensation = [54, 59]
        return functional_movement

    def get_pelvic_posterior_tilt(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.pelvic_posterior_tilt)
        functional_movement.prime_movers = [74, 75]
        functional_movement.antagonists = [58, 71, 72, 26, 70, 21]
        functional_movement.synergists = [45, 69]
        functional_movement.parts_receiving_compensation = [45, 69]
        return functional_movement

    def get_trunk_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_flexion)
        functional_movement.prime_movers = []
        functional_movement.synergists = []
        functional_movement.parts_receiving_compensation = []

    def get_elbow_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.elbow_flexion)
        functional_movement.prime_movers = [126]
        functional_movement.synergists = [127, 128]
        functional_movement.antagonists = [130, 131, 132]
        functional_movement.parts_receiving_compensation = []

    def get_elbow_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.elbow_extension)
        functional_movement.prime_movers = [130, 131, 132]
        functional_movement.synergists = []
        functional_movement.antagonists = [126, 127, 128]
        functional_movement.parts_receiving_compensation = []

    def get_shoulder_horizontal_adduction_and_scapular_protraction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_horizontal_adduction)
        functional_movement.prime_movers = [125, 82]
        functional_movement.synergists = [83, 81]
        functional_movement.antagonists = [78, 80, 85]
        functional_movement.parts_receiving_compensation = []

    def get_shoulder_horizontal_abduction_and_scapular_retraction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_horizontal_abduction)
        functional_movement.prime_movers = [78, 85]
        functional_movement.synergists = [80]
        functional_movement.antagonists = [83, 125, 81, 82]
        functional_movement.parts_receiving_compensation = []

    def get_shoulder_flexion_and_scapular_upward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation)
        functional_movement.prime_movers = [83, 125]
        functional_movement.synergists = [76, 79, 82, 127, 129]
        functional_movement.antagonists = [21, 77, 80, 120, 85, 81, 132]
        functional_movement.parts_receiving_compensation = []

    def get_shoulder_extension_and_scapular_downward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation)
        functional_movement.prime_movers = [21, 81]
        functional_movement.synergists = [77, 80, 120, 85, 132]
        functional_movement.antagonists = [76, 79, 83, 125, 82, 127, 129]
        functional_movement.parts_receiving_compensation = []

    def get_shoulder_abduction_and_scapular_upward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation)
        functional_movement.prime_movers = [83, 84, 125]
        functional_movement.synergists = [76, 79, 121]
        functional_movement.antagonists = [21, 77, 80, 120, 122, 123, 124, 81, 82, 129, 132]
        functional_movement.parts_receiving_compensation = []

    def get_shoulder_adduction_and_scapular_downward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation)
        functional_movement.prime_movers = [21, 81]
        functional_movement.synergists = [77, 80, 120, 122, 123, 124, 82, 129, 132]
        functional_movement.antagonists = [76, 79, 121, 83, 84, 125]
        functional_movement.parts_receiving_compensation = []

    def get_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.internal_rotation)
        functional_movement.prime_movers = [122]
        functional_movement.synergists = [21, 120, 83, 82]
        functional_movement.antagonists = [123, 124, 85]
        functional_movement.parts_receiving_compensation = []

    def get_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.external_rotation)
        functional_movement.prime_movers = [123, 124]
        functional_movement.synergists = [85]
        functional_movement.antagonists = [21, 120, 122, 83, 82]
        functional_movement.parts_receiving_compensation = []

    def get_scapular_elevation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.scapular_elevation)
        functional_movement.prime_movers = [76]
        functional_movement.synergists = [77, 80]
        functional_movement.antagonists = [79, 81]
        functional_movement.parts_receiving_compensation = []

    def get_scapular_depression(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.scapular_elevation)
        functional_movement.prime_movers = [79]
        functional_movement.synergists = [81]
        functional_movement.antagonists = [76, 77, 80]
        functional_movement.parts_receiving_compensation = []
