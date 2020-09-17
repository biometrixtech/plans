import statistics

from models.body_parts import BodyPartFactory
from models.compensation_source import CompensationSource
from models.functional_movement import ActivityFunctionalMovementFactory, FunctionalMovementFactory, BodyPartFunctionalMovement, FunctionalMovementActionMapping, BodyPartFunction
from models.body_part_injury_risk import BodyPartInjuryRisk
from models.movement_tags import AdaptationType
from models.session import SessionType
from models.soreness_base import BodyPartLocation, BodyPartSide
from models.training_load import CompletedSessionDetails
from logic.detailed_load_processing import DetailedLoadProcessor
from models.training_load import DetailedTrainingLoad
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
        self.completed_session_details = None

    def process(self, event_date, load_stats):
        activity_factory = ActivityFunctionalMovementFactory()
        movement_factory = FunctionalMovementFactory()

        provider_id=None
        workout_id=None
        user_id = self.session.user_id

        if self.session.workout_program_module is not None:  # completed
            provider_id = self.session.workout_program_module.program_id
            workout_id = self.session.workout_program_module.program_module_id

        self.completed_session_details = CompletedSessionDetails(self.session.event_date, provider_id=provider_id, workout_id=workout_id, user_id=user_id)

        if self.session.session_type() == SessionType.mixed_activity:
            if self.session.workout_program_module is not None:
                functional_movement_factory = FunctionalMovementFactory()
                functional_movement_dict = functional_movement_factory.get_functional_movement_dictionary()
                total_load_dict = self.process_workout_load(self.session.workout_program_module, event_date, functional_movement_dict)
                #consolidated_dict = self.consolidate_load(total_load_dict, event_date)

                #self.session_load_dict = consolidated_dict

                # this is now a muscle load only, aggregated by muscle
                self.session_load_dict = total_load_dict
        elif self.session.session_type() == SessionType.planned:
            if self.session.workout is not None:
                functional_movement_factory = FunctionalMovementFactory()
                functional_movement_dict = functional_movement_factory.get_functional_movement_dictionary()
                total_load_dict = self.process_planned_workout_load(self.session.workout, event_date, functional_movement_dict)
                self.completed_session_details.planned = True
                #consolidated_dict = self.consolidate_load(total_load_dict, event_date)

                #self.session_load_dict = consolidated_dict

                # this is now a muscle load only, aggregated by muscle
                self.session_load_dict = total_load_dict

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
                session_load_dict[body_part_side].isometric_load.add(body_part_functional_movement.isometric_load)
                session_load_dict[body_part_side].eccentric_load.add(body_part_functional_movement.eccentric_load)
                session_load_dict[body_part_side].compensated_concentric_load.add(body_part_functional_movement.compensated_concentric_load)
                session_load_dict[body_part_side].compensated_isometric_load.add(
                    body_part_functional_movement.compensated_isometric_load)
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

        detailed_load_processor = DetailedLoadProcessor()

        for workout_section in workout_program.workout_sections:
            if workout_section.assess_load:
                #section_load = {}  # load by adaptation type
                for workout_exercise in workout_section.exercises:
                    #exercise_load = self.apply_load(workout_exercise.primary_actions, event_date)
                    #exercise_load = {}  # load by adaptation type

                    for compound_action in workout_exercise.compound_actions:
                        for action in compound_action.actions:
                            for sub_action in action.sub_actions:
                                functional_movement_action_mapping = FunctionalMovementActionMapping(sub_action,
                                                                                                     self.injury_risk_dict,
                                                                                                     event_date, function_movement_dict)
                                # functional_movement_action_mapping.set_compensation_load(self.injury_risk_dict, event_date)
                                # detailed_load_processor.add_load(functional_movement_action_mapping,
                                #                                  workout_exercise.adaptation_type,
                                #                                  sub_action,
                                #                                  workout_exercise.power_load,
                                #                                  reps=workout_exercise.reps_per_set,
                                #                                  duration=workout_exercise.total_volume,
                                #                                  rpe_range=workout_exercise.rpe,
                                #                                  percent_max_hr=None)

                                self.functional_movement_mappings.append(functional_movement_action_mapping)

                                # new
                                for muscle_string, load in functional_movement_action_mapping.muscle_load.items():
                                    muscle = BodyPartSide.from_string(muscle_string)
                                    if muscle not in workout_load:
                                        workout_load[muscle] = load
                                    else:
                                        workout_load[muscle].merge(load)

        # detailed_load_processor.rank_types()
        # self.completed_session_details.session_detailed_load = detailed_load_processor.session_detailed_load
        # self.completed_session_details.training_type_load = detailed_load_processor.session_training_type_load
        # self.completed_session_details.ranked_muscle_load = detailed_load_processor.ranked_muscle_load
        # if self.session is not None:
        #     self.completed_session_details.power_load = self.session.power_load
        #     self.completed_session_details.rpe_load = self.session.rpe_load
        #     if self.session.session_RPE is not None:
        #         if isinstance(self.session.session_RPE, StandardErrorRange):
        #             self.completed_session_details.session_RPE = self.session.session_RPE
        #         else:
        #             self.completed_session_details.session_RPE = StandardErrorRange(observed_value=self.session.session_RPE)
        #     else:
        #         self.completed_session_details.session_RPE = StandardErrorRange()
        #     self.completed_session_details.training_volume = self.session.training_volume
        #     if self.session.duration_minutes is not None:
        #         self.completed_session_details.duration = self.session.duration_minutes * 60
        # else:
        #     # TODO - is this the best way to handle this?
        #     self.completed_session_details.power_load = StandardErrorRange()
        #     self.completed_session_details.rpe_load = StandardErrorRange()
        #     self.completed_session_details.session_RPE = StandardErrorRange()
        return workout_load

    @xray_recorder.capture('logic.SessionFunctionalMovement.process_workout_load')
    def process_planned_workout_load(self, workout, event_date, function_movement_dict):


        self.completed_session_details.provider_id = workout.program_id
        self.completed_session_details.workout_id =  workout.program_module_id
        workout_load = {}

        detailed_load_processor = DetailedLoadProcessor()

        for workout_section in workout.sections:
            if workout_section.assess_load:
                #section_load = {}  # load by adaptation type
                for workout_exercise in workout_section.exercises:
                    #exercise_load = self.apply_load(workout_exercise.primary_actions, event_date)
                    #exercise_load = {}  # load by adaptation type

                    for compound_action in workout_exercise.compound_actions:
                        for action in compound_action.actions:
                            for sub_action in action.sub_actions:
                                functional_movement_action_mapping = FunctionalMovementActionMapping(sub_action,
                                                                                                     self.injury_risk_dict,
                                                                                                     event_date, function_movement_dict)
                                # functional_movement_action_mapping.set_compensation_load(self.injury_risk_dict, event_date)
                                # detailed_load_processor.add_load(functional_movement_action_mapping,
                                #                                  workout_exercise.adaptation_type,
                                #                                  sub_action,
                                #                                  workout_exercise.power_load,
                                #                                  reps=workout_exercise.reps_per_set,
                                #                                  duration=workout_exercise.duration.lowest_value(),
                                #                                  rpe_range=workout_exercise.rpe,
                                #                                  percent_max_hr=None)

                                self.functional_movement_mappings.append(functional_movement_action_mapping)

                                # new
                                for muscle_string, load in functional_movement_action_mapping.muscle_load.items():
                                    muscle = BodyPartSide.from_string(muscle_string)
                                    if muscle not in workout_load:
                                        workout_load[muscle] = load
                                    else:
                                        workout_load[muscle].merge(load)

        # detailed_load_processor.rank_types()
        # self.completed_session_details.session_detailed_load = detailed_load_processor.session_detailed_load
        # self.completed_session_details.training_type_load = detailed_load_processor.session_training_type_load
        # self.completed_session_details.muscle_detailed_load = detailed_load_processor.muscle_detailed_load
        # self.completed_session_details.ranked_muscle_load = detailed_load_processor.ranked_muscle_load
        # if self.session is not None:
        #     self.completed_session_details.power_load = self.session.power_load
        #     self.completed_session_details.rpe_load = self.session.rpe_load
        #     if self.session.session_RPE is not None:
        #         if isinstance(self.session.session_RPE, StandardErrorRange):
        #             self.completed_session_details.session_RPE = self.session.session_RPE
        #         else:
        #             self.completed_session_details.session_RPE = StandardErrorRange(observed_value=self.session.session_RPE)
        #     else:
        #         self.completed_session_details.session_RPE = StandardErrorRange()
        #     if self.session.duration_minutes is not None:
        #         self.completed_session_details.duration = self.session.duration_minutes * 60
        # else:
        #     # TODO - is this the best way to handle this?
        #     self.completed_session_details.power_load = StandardErrorRange()
        #     self.completed_session_details.rpe_load = StandardErrorRange()
        #     self.completed_session_details.session_RPE = StandardErrorRange()
        return workout_load

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

