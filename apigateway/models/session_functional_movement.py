import statistics

from models.body_parts import BodyPartFactory
from models.compensation_source import CompensationSource
from models.functional_movement import ActivityFunctionalMovementFactory, FunctionalMovementFactory, BodyPartFunctionalMovement, FunctionalMovementActionMapping
from models.movement_tags import AdaptationType
from models.session import SessionType
from models.soreness_base import BodyPartLocation, BodyPartSide


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
            if self.session.workout_program_module is not None:
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
                        total_load[action.adaptation_type.value][muscle].merge(load)

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