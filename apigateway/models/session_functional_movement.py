import statistics

from models.body_parts import BodyPartFactory
from models.compensation_source import CompensationSource
from models.functional_movement import ActivityFunctionalMovementFactory, FunctionalMovementFactory, BodyPartFunctionalMovement, FunctionalMovementActionMapping, BodyPartFunction
from models.body_part_injury_risk import BodyPartInjuryRisk
from models.movement_tags import AdaptationType
from models.session import SessionType
from models.soreness_base import BodyPartLocation, BodyPartSide
from models.training_volume import StandardErrorRange
from datetime import timedelta
from fathomapi.utils.xray import xray_recorder


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
                functional_movement_factory = FunctionalMovementFactory()
                functional_movement_dict = functional_movement_factory.get_functional_movement_dictinary()
                total_load_dict = self.process_workout_load(self.session.workout_program_module, event_date, functional_movement_dict)
                consolidated_dict = self.consolidate_load(total_load_dict, event_date)

                self.session_load_dict = consolidated_dict

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

                m.attribute_training_load(self.session.training_load(load_stats), self.injury_risk_dict, event_date)
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

                session_load_dict[body_part_side].body_part_function = BodyPartFunction.merge(body_part_functional_movement.body_part_function, session_load_dict[body_part_side].body_part_function)
                session_load_dict[body_part_side].concentric_load.add(body_part_functional_movement.concentric_load)
                session_load_dict[body_part_side].eccentric_load.add(body_part_functional_movement.eccentric_load)
                session_load_dict[body_part_side].compensated_concentric_load.add(body_part_functional_movement.compensated_concentric_load)
                session_load_dict[
                    body_part_side].compensated_eccentric_load.add(body_part_functional_movement.compensated_eccentric_load)

                session_load_dict[body_part_side].compensating_causes_load.extend(body_part_functional_movement.compensating_causes_load)
                session_load_dict[body_part_side].compensating_causes_load = list(set(session_load_dict[body_part_side].compensating_causes_load))
                #session_load_dict[body_part_side].compensation_source_load = CompensationSource.internal_processing

                # session_load_dict[body_part_side].concentric_intensity = max(body_part_functional_movement.concentric_intensity, session_load_dict[body_part_side].concentric_intensity)
                # session_load_dict[body_part_side].eccentric_intensity = max(body_part_functional_movement.eccentric_intensity, session_load_dict[body_part_side].eccentric_intensity)

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

    @xray_recorder.capture('logic.SessionFunctionalMovement.process_workout_load')
    def process_workout_load(self, workout_program, event_date, function_movement_dict):

        workout_load = {}

        for workout_section in workout_program.workout_sections:
            if workout_section.assess_load:
                section_load = {}  # load by adaptation type
                for workout_exercise in workout_section.exercises:
                    #exercise_load = self.apply_load(workout_exercise.primary_actions, event_date)
                    exercise_load = {}  # load by adaptation type

                    for action in workout_exercise.primary_actions:
                        functional_movement_action_mapping = FunctionalMovementActionMapping(action,
                                                                                             self.injury_risk_dict,
                                                                                             event_date, function_movement_dict)
                        # functional_movement_action_mapping.set_compensation_load(self.injury_risk_dict, event_date)
                        self.functional_movement_mappings.append(functional_movement_action_mapping)
                        if action.adaptation_type.value not in exercise_load:
                            exercise_load[action.adaptation_type.value] = functional_movement_action_mapping.muscle_load
                        else:
                            for muscle, load in functional_movement_action_mapping.muscle_load.items():
                                if muscle not in exercise_load[action.adaptation_type.value]:
                                    exercise_load[action.adaptation_type.value][muscle] = load
                                else:
                                    exercise_load[action.adaptation_type.value][muscle].merge(load)

                    #return total_load

                    for adaptation_type, muscle_load in exercise_load.items():
                        if adaptation_type not in section_load:
                            section_load[adaptation_type] = muscle_load
                        else:
                            for muscle, load in muscle_load.items():
                                if muscle not in section_load[adaptation_type]:
                                    section_load[adaptation_type][muscle] = load
                                else:
                                    section_load[adaptation_type][muscle].merge(load)

                for adaptation_type, muscle_load in section_load.items():
                    if adaptation_type not in workout_load:
                        workout_load[adaptation_type] = muscle_load
                    else:
                        for muscle, load in muscle_load.items():
                            if muscle not in workout_load[adaptation_type]:
                                workout_load[adaptation_type][muscle] = load
                            else:
                                workout_load[adaptation_type][muscle].merge(load)

        return workout_load

    # def apply_load(self, action_list, event_date):
    #
    #     total_load = {}  # load by adaptation type
    #
    #     for action in action_list:
    #         functional_movement_action_mapping = FunctionalMovementActionMapping(action, self.injury_risk_dict, event_date)
    #         #functional_movement_action_mapping.set_compensation_load(self.injury_risk_dict, event_date)
    #         self.functional_movement_mappings.append(functional_movement_action_mapping)
    #         if action.adaptation_type.value not in total_load:
    #             total_load[action.adaptation_type.value] = functional_movement_action_mapping.muscle_load
    #         else:
    #             for muscle, load in functional_movement_action_mapping.muscle_load.items():
    #                 if muscle not in total_load[action.adaptation_type.value]:
    #                     total_load[action.adaptation_type.value][muscle] = load
    #                 else:
    #                     total_load[action.adaptation_type.value][muscle].merge(load)
    #
    #     return total_load

    @xray_recorder.capture('logic.SessionFunctionalMovement.normalize_and_consolidate_load')
    def consolidate_load(self, total_load_dict, event_date):

        consolidated_dict = {}

        # initialize session values
        self.session.strength_endurance_cardiorespiratory_load = StandardErrorRange(observed_value=0)
        self.session.strength_endurance_strength_load = StandardErrorRange(observed_value=0)
        self.session.power_drill_load = StandardErrorRange(observed_value=0)
        self.session.maximal_strength_hypertrophic_load = StandardErrorRange(observed_value=0)
        self.session.power_explosive_action_load = StandardErrorRange(observed_value=0)
        self.session.not_tracked_load = StandardErrorRange(observed_value=0)

        for adaptation_type, muscle_load_dict in total_load_dict.items():
            #scalar = self.get_adaption_type_scalar(adaptation_type)

            all_values = [c.total_load() for c in muscle_load_dict.values() if c.total_load().observed_value > 0]

            if len(all_values) > 0:
                #minimum = StandardErrorRange().get_min_from_error_range_list(all_values)

                for muscle_string in muscle_load_dict:
                    muscle = BodyPartSide.from_string(muscle_string)
                    maximum = self.get_body_part_injury_risk_max(adaptation_type, muscle, event_date)
                    max_current_load = muscle_load_dict[muscle_string].total_load().highest_value()

                    if maximum < max_current_load:
                        self.set_body_part_injury_risk_max(adaptation_type, muscle, max_current_load, event_date)
                        maximum = max_current_load

                    # value_range = maximum - minimum

                    # if muscle_load_dict[muscle_string].total_load().observed_value > 0 and value_range > 0:
                    #     total_load = muscle_load_dict[muscle_string].total_load()
                    #     total_load.subtract_value(minimum)
                    #     total_load.divide(value_range)
                    #     total_load.multiply(scalar)
                    #     muscle_load_dict[muscle_string].total_normalized_load = total_load

                    # if muscle not in normalized_dict:
                    #     normalized_dict[muscle] = muscle_load_dict[muscle_string]
                    # else:
                    #     normalized_dict[muscle].total_normalized_load.add(muscle_load_dict[muscle_string].total_normalized_load)
                    if muscle not in consolidated_dict:
                        consolidated_dict[muscle] = muscle_load_dict[muscle_string]
                    else:
                        consolidated_dict[muscle].merge(muscle_load_dict[muscle_string])

                    # saved normalized load to the session while we're looping through
                    if adaptation_type == AdaptationType.strength_endurance_cardiorespiratory.value:
                        self.session.strength_endurance_cardiorespiratory_load.add(muscle_load_dict[muscle_string].total_load())
                    elif adaptation_type == AdaptationType.strength_endurance_strength.value:
                        self.session.strength_endurance_strength_load.add(muscle_load_dict[muscle_string].total_load())
                    elif adaptation_type == AdaptationType.power_drill.value:
                        self.session.power_drill_load.add(muscle_load_dict[muscle_string].total_load())
                    elif adaptation_type == AdaptationType.maximal_strength_hypertrophic.value:
                        self.session.maximal_strength_hypertrophic_load.add(muscle_load_dict[muscle_string].total_load())
                    elif adaptation_type == AdaptationType.power_explosive_action.value:
                        self.session.power_explosive_action_load.add(muscle_load_dict[muscle_string].total_load())
                    else:
                        self.session.not_tracked_load.add(muscle_load_dict[muscle_string].total_load())

        return consolidated_dict

    def get_adaption_type_scalar(self, adaptation_type):

        if adaptation_type == AdaptationType.strength_endurance_cardiorespiratory.value:
            return 0.20
        elif adaptation_type == AdaptationType.strength_endurance_strength.value:
            return 0.40
        elif adaptation_type == AdaptationType.power_drill.value:
            return 0.60
        elif adaptation_type == AdaptationType.maximal_strength_hypertrophic.value:
            return 0.80
        elif adaptation_type == AdaptationType.power_explosive_action.value:
            return 1.00
        else:
            return 0.00

    def get_body_part_injury_risk_max(self, adaptation_type, muscle, event_date):

        max = 0.0

        if muscle in self.injury_risk_dict:
            if adaptation_type == AdaptationType.strength_endurance_cardiorespiratory.value:
                if self.is_max_date_valid(self.injury_risk_dict[muscle].max_strength_endurance_cardiorespiratory_date, event_date):
                    max = self.injury_risk_dict[muscle].max_strength_endurance_cardiorespiratory
            elif adaptation_type == AdaptationType.strength_endurance_strength.value:
                if self.is_max_date_valid(self.injury_risk_dict[muscle].max_strength_endurance_strength_date, event_date):
                    max = self.injury_risk_dict[muscle].max_strength_endurance_strength
            elif adaptation_type == AdaptationType.power_drill.value:
                if self.is_max_date_valid(self.injury_risk_dict[muscle].max_power_drill_date, event_date):
                    max = self.injury_risk_dict[muscle].max_power_drill
            elif adaptation_type == AdaptationType.maximal_strength_hypertrophic.value:
                if self.is_max_date_valid(self.injury_risk_dict[muscle].max_maximal_strength_hypertrophic_date, event_date):
                    max = self.injury_risk_dict[muscle].max_maximal_strength_hypertrophic
            elif adaptation_type == AdaptationType.power_explosive_action.value:
                if self.is_max_date_valid(self.injury_risk_dict[muscle].max_power_explosive_action_date,
                                          event_date):
                    max = self.injury_risk_dict[muscle].max_power_explosive_action
            else:
                if self.is_max_date_valid(self.injury_risk_dict[muscle].max_not_tracked_date,
                                          event_date):
                    max = self.injury_risk_dict[muscle].max_not_tracked

        return max

    def is_max_date_valid(self, date_attribute, test_date):

        four_weeks_ago = test_date - timedelta(days=28)

        if date_attribute is not None and date_attribute >= four_weeks_ago:
            return True
        else:
            return False


    def set_body_part_injury_risk_max(self, adaptation_type, muscle, max, event_date):

        if muscle not in self.injury_risk_dict:
            self.injury_risk_dict[muscle] = BodyPartInjuryRisk()

        if adaptation_type == AdaptationType.strength_endurance_cardiorespiratory.value:
            self.injury_risk_dict[muscle].max_strength_endurance_cardiorespiratory = max
            self.injury_risk_dict[muscle].max_strength_endurance_cardiorespiratory_date = event_date
        elif adaptation_type == AdaptationType.strength_endurance_strength.value:
            self.injury_risk_dict[muscle].max_strength_endurance_strength = max
            self.injury_risk_dict[muscle].max_strength_endurance_strength_date = event_date
        elif adaptation_type == AdaptationType.power_drill.value:
            self.injury_risk_dict[muscle].max_power_drill = max
            self.injury_risk_dict[muscle].max_power_drill_date = event_date
        elif adaptation_type == AdaptationType.maximal_strength_hypertrophic.value:
            self.injury_risk_dict[muscle].max_maximal_strength_hypertrophic = max
            self.injury_risk_dict[muscle].max_maximal_strength_hypertrophic_date = event_date
        elif adaptation_type == AdaptationType.power_explosive_action.value:
            self.injury_risk_dict[muscle].max_power_explosive_action = max
            self.injury_risk_dict[muscle].max_power_explosive_action_date = event_date
        else:
            self.injury_risk_dict[muscle].max_not_tracked = max
            self.injury_risk_dict[muscle].max_not_tracked_date = event_date

