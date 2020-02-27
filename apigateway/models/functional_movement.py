from enum import Enum
from collections import namedtuple
from models.session import SessionType
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.body_parts import BodyPartFactory
from datetime import timedelta
from models.movement_actions import MuscleAction
from models.movement_tags import AdaptationType
from models.functional_movement_type import FunctionalMovementType
import statistics


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
        self.session_load_dict = {}

    def process(self, event_date, load_stats):
        activity_factory = ActivityFunctionalMovementFactory()
        movement_factory = FunctionalMovementFactory()

        if self.session.session_type() == SessionType.mixed_activity:

            total_load_dict = self.process_workout_load(self.session.workout_program_module)
            normalized_dict = self.normalize_and_consolidate_load(total_load_dict)
            self.session_load_dict = normalized_dict

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
                # if self.session.session_RPE is not None:
                #     m.attribute_intensity(self.session.session_RPE, self.injury_risk_dict, event_date)

                self.session_load_dict = self.aggregate_body_parts()

        return self.session

    def aggregate_body_parts(self):

        session_load_dict = {}

        for m in self.functional_movement_mappings:
            for body_part_side, body_part_functional_movement in m.muscle_load.items():
                if body_part_side not in session_load_dict:
                    session_load_dict[body_part_side] = BodyPartFunctionalMovement(body_part_side)

                session_load_dict[body_part_side].concentric_volume += body_part_functional_movement.concentric_volume
                session_load_dict[body_part_side].eccentric_volume += body_part_functional_movement.eccentric_volume
                session_load_dict[body_part_side].compensated_concentric_volume += body_part_functional_movement.compensated_concentric_volume
                session_load_dict[
                    body_part_side].compensated_eccentric_volume += body_part_functional_movement.compensated_eccentric_volume

                session_load_dict[body_part_side].compensating_causes_volume.extend(body_part_functional_movement.compensating_causes_volume)
                session_load_dict[body_part_side].compensating_causes_volume = list(set(session_load_dict[body_part_side].compensating_causes_volume))
                session_load_dict[body_part_side].compensation_source_volume = CompensationSource.internal_processing

                session_load_dict[body_part_side].concentric_intensity = max(body_part_functional_movement.concentric_intensity, session_load_dict[body_part_side].concentric_intensity)
                session_load_dict[body_part_side].eccentric_intensity = max(body_part_functional_movement.eccentric_intensity, session_load_dict[body_part_side].eccentric_intensity)

        return session_load_dict

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

    def process_workout_load(self, workout_program):

        workout_load = {}

        for workout_section in workout_program.workout_sections:
            if workout_section.assess_load:
                section_load = {}  # load by adaptation type
                for workout_exercise in workout_section.exercises:
                    exercise_load = self.apply_load(workout_exercise.primary_actions)
                    for adaptation_type, muscle_load in exercise_load.items():
                        if adaptation_type not in section_load:
                            section_load[adaptation_type] = muscle_load
                        else:
                            for muscle, load in muscle_load.items():
                                if muscle not in section_load[adaptation_type].items():
                                    section_load[adaptation_type][muscle] = load
                                else:
                                    section_load[adaptation_type][muscle] += load

                for adaptation_type, muscle_load in section_load.items():
                    if adaptation_type not in workout_load:
                        workout_load[adaptation_type] = muscle_load
                    else:
                        for muscle, load in muscle_load.items():
                            if muscle not in workout_load[adaptation_type].items():
                                workout_load[adaptation_type][muscle] = load
                            else:
                                workout_load[adaptation_type][muscle] += load

        return workout_load

    def apply_load(self, action_list):

        total_load = {}  # load by adaptation type

        for action in action_list:
            functional_movement_action_mapping = FunctionalMovementActionMapping(action)
            self.functional_movement_mappings.append(functional_movement_action_mapping)
            if action.adaptation_type.value not in total_load:
                total_load[action.adaptation_type.value] = functional_movement_action_mapping.muscle_load
            else:
                for muscle, load in functional_movement_action_mapping.muscle_load.items():
                    if muscle not in total_load[action.adaptation_type.value]:
                        total_load[action.adaptation_type.value][muscle] = load
                    else:
                        total_load[action.adaptation_type.value][muscle] += load

        return total_load

    def normalize_and_consolidate_load(self, total_load_dict):

        normalized_dict = {}

        for adaptation_type, muscle_load_dict in total_load_dict.items():
            scalar = self.get_adaption_type_scalar(adaptation_type)
            concentric_values = [c.concentric_volume for c in muscle_load_dict.values() if c.concentric_volume > 0]
            eccentric_values = [c.eccentric_volume for c in muscle_load_dict.values() if c.eccentric_volume > 0]
            all_values = []
            all_values.extend(concentric_values)
            all_values.extend(eccentric_values)
            if len(all_values) > 0:
                average = statistics.mean(all_values)
                std_dev = statistics.stdev(all_values)
                for muscle in muscle_load_dict.keys():
                    if muscle_load_dict[muscle].concentric_volume > 0:
                        muscle_load_dict[muscle].concentric_volume = scalar * ((muscle_load_dict[muscle].concentric_volume - average) / std_dev)
                    if muscle_load_dict[muscle].eccentric_volume > 0:
                        muscle_load_dict[muscle].eccentric_volume = scalar * ((muscle_load_dict[muscle].eccentric_volume - average) / std_dev)
                    if muscle not in normalized_dict:
                        normalized_dict[muscle] = muscle_load_dict[muscle]
                    else:
                        normalized_dict[muscle].concentric_volume += muscle_load_dict[muscle].concentric_volume
                        normalized_dict[muscle].eccentric_volume += muscle_load_dict[muscle].eccentric_volume

        return normalized_dict

    def get_adaption_type_scalar(self, adaption_type):

        if adaption_type == AdaptationType.strength_endurance_cardiorespiratory.value:
            return 0.20
        elif adaption_type == AdaptationType.strength_endurance_strength.value:
            return 0.40
        elif adaption_type == AdaptationType.power_drill.value:
            return 0.60
        elif adaption_type == AdaptationType.maximal_strength_hypertrophic.value:
            return 0.80
        elif adaption_type == AdaptationType.power_explosive_action.value:
            return 1.00
        else:
            return 0.00


class FunctionalMovementLoad(object):
    def __init__(self, functional_movement, muscle_action):
        self.functional_movement = functional_movement
        self.muscle_action = muscle_action


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

            functional_movement_load = FunctionalMovementLoad(functional_movement, self.exercise_action.primary_muscle_action)

            functional_movement_list.append(functional_movement_load)

        return functional_movement_list

    def set_muscle_load(self):

        self.apply_load_to_functional_movements(self.hip_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.knee_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.ankle_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.trunk_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.shoulder_scapula_joint_functional_movements, self.exercise_action)
        self.apply_load_to_functional_movements(self.elbow_joint_functional_movements, self.exercise_action)

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

    def apply_load_to_functional_movements(self, functional_movement_list, exercise_action):

        body_part_factory = BodyPartFactory()

        left_load = exercise_action.total_load_left
        right_load = exercise_action.total_load_right

        for functional_movement_load in functional_movement_list:

            functional_movement = functional_movement_load.functional_movement

            if exercise_action.apply_instability:
                stability_rating = self.get_matching_stability_rating(functional_movement_load, exercise_action)
            else:
                stability_rating = 0.0

            for p in functional_movement.prime_movers:
                body_part_side_list = body_part_factory.get_body_part_side_list(p)
                for body_part_side in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(body_part_side)
                    if body_part_side.side == 1 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.prime_mover, left_load, stability_rating)
                        self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load, functional_movement_load.muscle_action)
                    if body_part_side.side == 2 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.prime_mover, right_load, stability_rating)
                        self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load, functional_movement_load.muscle_action)
            for s in functional_movement.synergists:
                body_part_side_list = body_part_factory.get_body_part_side_list(s)
                for body_part_side in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(body_part_side)
                    if body_part_side.side == 1 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.synergist, left_load, stability_rating)
                        self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load, functional_movement_load.muscle_action)
                    if body_part_side.side == 2 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.synergist, right_load, stability_rating)
                        self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load, functional_movement_load.muscle_action)
            for t in functional_movement.stabilizers:
                body_part_side_list = body_part_factory.get_body_part_side_list(t)
                for body_part_side in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(body_part_side)
                    if body_part_side.side == 1 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.stabilizer, left_load, stability_rating)
                        self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load, functional_movement_load.muscle_action)
                    if body_part_side.side == 2 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.stabilizer, right_load, stability_rating)
                        self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load, functional_movement_load.muscle_action)

            for f in functional_movement.fixators:
                body_part_side_list = body_part_factory.get_body_part_side_list(f)
                for body_part_side in body_part_side_list:
                    functional_movement_body_part_side = BodyPartFunctionalMovement(body_part_side)
                    if body_part_side.side == 1 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.fixator, left_load, stability_rating)
                        self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load, functional_movement_load.muscle_action)
                    if body_part_side.side == 2 or body_part_side.side == 0:
                        attributed_muscle_load = self.get_muscle_load(functional_movement.priority,
                                                                      BodyPartFunction.fixator, right_load, stability_rating)
                        self.update_muscle_dictionary(functional_movement_body_part_side, attributed_muscle_load, functional_movement_load.muscle_action)

    def update_muscle_dictionary(self, muscle, attributed_muscle_load, muscle_action):
        if muscle.body_part_side in self.muscle_load:
            if muscle_action == MuscleAction.concentric or muscle_action == MuscleAction.isometric:
                self.muscle_load[muscle.body_part_side].concentric_volume += attributed_muscle_load
            else:
                self.muscle_load[muscle.body_part_side].eccentric_volume += attributed_muscle_load
        else:
            self.muscle_load[muscle.body_part_side] = muscle
            if muscle_action == MuscleAction.concentric or muscle_action == MuscleAction.isometric:
                self.muscle_load[muscle.body_part_side].concentric_volume = attributed_muscle_load
            else:
                self.muscle_load[muscle.body_part_side].eccentric_volume = attributed_muscle_load

    def get_muscle_load(self, functional_movement_priority, muscle_role, load, stability_rating):

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

        if muscle_role == BodyPartFunction.prime_mover:
            muscle_ratio = 1.00
        elif muscle_role == BodyPartFunction.synergist:
            muscle_ratio = 0.60
        elif muscle_role == BodyPartFunction.stabilizer:
            muscle_ratio = (0.15 * stability_rating) + 0.05
        elif muscle_role == BodyPartFunction.fixator:
            muscle_ratio = (0.10 * stability_rating) + 0.20
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
        self.muscle_load = {}

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
                    if s.body_part_side not in self.muscle_load:
                        self.muscle_load[s.body_part_side] = s
                    else:
                        self.muscle_load[s.body_part_side].compensated_concentric_volume += synergist_compensated_concentric_volume
                        self.muscle_load[s.body_part_side].compensated_eccentric_volume += synergist_compensated_eccentric_volume
                        self.muscle_load[s.body_part_side].compensating_causes_volume.append(c)
                        self.muscle_load[s.body_part_side].compensation_source_volume = CompensationSource.internal_processing

        for p in self.prime_movers:
            attributed_concentric_volume = training_volume * self.concentric_level * prime_mover_ratio
            attributed_eccentric_volume = training_volume * self.eccentric_level * prime_mover_ratio
            p.body_part_function = BodyPartFunction.prime_mover
            p.concentric_volume = attributed_concentric_volume
            p.eccentric_volume = attributed_eccentric_volume
            if p.body_part_side not in self.muscle_load:
                self.muscle_load[p.body_part_side] = p
            else:
                self.muscle_load[p.body_part_side].concentric_volume += p.concentric_volume
                self.muscle_load[p.body_part_side].eccentric_volume += p.eccentric_volume

        for s in self.synergists:
            attributed_concentric_volume = training_volume * self.concentric_level * synergist_ratio
            attributed_eccentric_volume = training_volume * self.eccentric_level * synergist_ratio
            s.body_part_function = BodyPartFunction.synergist
            s.concentric_volume = attributed_concentric_volume
            s.eccentric_volume = attributed_eccentric_volume
            if s.body_part_side not in self.muscle_load:
                self.muscle_load[s.body_part_side] = s
            else:
                self.muscle_load[s.body_part_side].concentric_volume += s.concentric_volume
                self.muscle_load[s.body_part_side].eccentric_volume += s.eccentric_volume

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
        # elif movement_type == FunctionalMovementType.tibial_external_rotation:
        #     return self.get_tibial_external_rotation()
        # elif movement_type == FunctionalMovementType.tibial_internal_rotation:
        #     return self.get_tibial_internal_rotation()

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

    def get_trunk_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_extension)
        functional_movement.prime_movers = [26, 21, 34]
        functional_movement.synergists = []
        functional_movement.antagonists = [71, 74, 69, 75]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = []

    def get_trunk_lateral_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_lateral_flexion)
        functional_movement.prime_movers = [70]
        functional_movement.synergists = [26, 21, 74, 69]
        functional_movement.antagonists = [26, 70, 21, 74, 69]
        functional_movement.stabilizers = [58, 71, 73, 74, 34, 35, 36, 70]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [26, 21, 74, 69]

    def get_trunk_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_rotation)
        functional_movement.prime_movers = [74, 69]
        functional_movement.synergists = [21, 71]
        functional_movement.antagonists = [69, 74]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [21, 71]

    def get_trunk_flexion_with_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_flexion_with_rotation)
        functional_movement.prime_movers = [74, 75, 69]
        functional_movement.synergists = [21, 71]
        functional_movement.antagonists = [69, 26, 74]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [21, 71]

    def get_trunk_extension_with_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.trunk_extension_with_rotation)
        functional_movement.prime_movers = [26, 74, 69]
        functional_movement.synergists = [21, 71]
        functional_movement.antagonists = [71, 69, 75, 74]
        functional_movement.stabilizers = [73, 74, 34, 35, 36, 70, 71]
        functional_movement.fixators = self.get_trunk_fixators()
        functional_movement.parts_receiving_compensation = [21, 71]

    def get_elbow_flexion(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.elbow_flexion)
        functional_movement.prime_movers = [126]
        functional_movement.synergists = [127, 128]
        functional_movement.antagonists = [130, 131, 132, 32]
        functional_movement.stabilizers = [33]
        functional_movement.fixators = self.get_elbow_fixators()
        functional_movement.parts_receiving_compensation = [127, 128]

    def get_elbow_extension(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.elbow_extension)
        functional_movement.prime_movers = [130, 131, 132]
        functional_movement.synergists = [32]
        functional_movement.antagonists = [126, 127, 128]
        functional_movement.stabilizers = [33]
        functional_movement.fixators = self.get_elbow_fixators()
        functional_movement.parts_receiving_compensation = [32]

    def get_shoulder_horizontal_adduction_and_scapular_protraction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_horizontal_adduction)
        functional_movement.prime_movers = [125, 82]
        functional_movement.synergists = [83, 81]
        functional_movement.antagonists = [78, 80, 85]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [83, 81]

    def get_shoulder_horizontal_abduction_and_scapular_retraction(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_horizontal_abduction)
        functional_movement.prime_movers = [78, 85]
        functional_movement.synergists = [80]
        functional_movement.antagonists = [83, 125, 81, 82]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [80]

    def get_shoulder_flexion_and_scapular_upward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_flexion_and_scapular_upward_rotation)
        functional_movement.prime_movers = [83, 125]
        functional_movement.synergists = [76, 79, 82, 127, 129]
        functional_movement.antagonists = [21, 77, 80, 120, 85, 81, 132]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [76, 79, 82, 127, 129]

    def get_shoulder_extension_and_scapular_downward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_extension_and_scapular_downward_rotation)
        functional_movement.prime_movers = [21, 81]
        functional_movement.synergists = [77, 80, 120, 85, 132]
        functional_movement.antagonists = [76, 79, 83, 125, 82, 127, 129]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [77, 80, 120, 85, 132]

    def get_shoulder_abduction_and_scapular_upward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_abduction_and_scapular_upward_rotation)
        functional_movement.prime_movers = [83, 84, 125]
        functional_movement.synergists = [76, 79, 121]
        functional_movement.antagonists = [21, 77, 80, 120, 122, 123, 124, 81, 82, 129, 132]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [76, 79, 121]

    def get_shoulder_adduction_and_scapular_downward_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.shoulder_adduction_and_scapular_downward_rotation)
        functional_movement.prime_movers = [21, 81]
        functional_movement.synergists = [77, 80, 120, 122, 123, 124, 82, 129, 132]
        functional_movement.antagonists = [76, 79, 121, 83, 84, 125]
        functional_movement.stabilizers = [121, 122, 123, 124, 125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [77, 80, 120, 122, 123, 124, 82, 129, 132]

    def get_internal_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.internal_rotation)
        functional_movement.prime_movers = [122]
        functional_movement.synergists = [21, 120, 83, 82]
        functional_movement.antagonists = [123, 124, 85]
        functional_movement.stabilizers = [121, 122, 123, 124]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [21, 120, 83, 82]

    def get_external_rotation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.external_rotation)
        functional_movement.prime_movers = [123, 124]
        functional_movement.synergists = [85]
        functional_movement.antagonists = [21, 120, 122, 83, 82]
        functional_movement.stabilizers = [121, 122, 123, 124]
        functional_movement.fixators = self.get_shoulder_fixators_1()
        functional_movement.parts_receiving_compensation = [85]

    def get_scapular_elevation(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.scapular_elevation)
        functional_movement.prime_movers = [76]
        functional_movement.synergists = [77, 80]
        functional_movement.antagonists = [79, 81]
        functional_movement.stabilizers = [125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_2()
        functional_movement.parts_receiving_compensation = [77, 80]

    def get_scapular_depression(self):

        functional_movement = FunctionalMovement(FunctionalMovementType.scapular_depression)
        functional_movement.prime_movers = [79]
        functional_movement.synergists = [81]
        functional_movement.antagonists = [76, 77, 80]
        functional_movement.stabilizers = [125, 77, 80]
        functional_movement.fixators = self.get_shoulder_fixators_2()
        functional_movement.parts_receiving_compensation = [81]
