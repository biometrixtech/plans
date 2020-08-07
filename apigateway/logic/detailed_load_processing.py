from models.movement_tags import DetailedAdaptationType, AdaptationType, TrainingType
from models.ranked_types import RankedBodyPart
from models.training_load import DetailedTrainingLoad, TrainingTypeLoad
from models.movement_actions import MovementSpeed, ExerciseAction, MovementResistance
from models.soreness_base import BodyPartSystems, BodyPartSide, BodyPartGeneralLocation, BodyPartLocation
from models.functional_movement import BodyPartFunctionalMovement, FunctionalMovementActionMapping
from models.training_volume import StandardErrorRange
from models.body_parts import BodyPartFactory


class DetailedLoadProcessor(object):
    def __init__(self):
        self.session_detailed_load = DetailedTrainingLoad()
        self.session_training_type_load = TrainingTypeLoad()
        self.muscle_detailed_load = {}
        self.ranked_muscle_load = []

    def rank_types(self):
        self.session_detailed_load.rank_adaptation_types()
        self.session_training_type_load.rank_types()
        self.rank_muscle_load()

    def rank_muscle_load(self):
        aggregated_muscle_load = {}
        for body_part_side, detailed_load in self.muscle_detailed_load.items():
            if body_part_side not in aggregated_muscle_load:
                muscle_group = BodyPartLocation.get_muscle_group(body_part_side.body_part_location)
                if isinstance(muscle_group, BodyPartLocation):
                    new_body_part_side = BodyPartSide(muscle_group, body_part_side.side)
                    if new_body_part_side not in aggregated_muscle_load:
                        aggregated_muscle_load[new_body_part_side] = detailed_load.total_load.plagiarize()
                    else:
                        aggregated_muscle_load[new_body_part_side].add(detailed_load.total_load)
                else:
                    aggregated_muscle_load[body_part_side] = detailed_load.total_load.plagiarize()
            else:
                aggregated_muscle_load[body_part_side].add(detailed_load.total_load.plagiarize())

        consolidated_muscle_load = {}

        body_part_factory = BodyPartFactory()

        for body_part_side, muscle_load in aggregated_muscle_load.items():
            body_part = body_part_factory.get_body_part(body_part_side)
            if body_part not in consolidated_muscle_load:
                consolidated_muscle_load[body_part] = muscle_load.plagiarize()
            else:
                consolidated_muscle_load[body_part].add(muscle_load.plagiarize())

        sorted_muscle_load = {k: v for k, v in sorted(consolidated_muscle_load.items(), key=lambda item: item[1].lowest_value(), reverse=True)}

        # sorted_muscles = {k: v for k, v in sorted(self.muscle_detailed_load.items(), key=lambda item: item[1].total_load.lowest_value(), reverse=True)}

        rank = 1
        last_value = None

        for body_part, load in sorted_muscle_load.items():
            if last_value is None:
                last_value = load.plagiarize()
            if load.highest_value() < last_value.highest_value():
                rank += 1
                last_value = load.plagiarize()
            ranked_body_part = RankedBodyPart(body_part.location, rank)
            ranked_body_part.power_load = load
            self.ranked_muscle_load.append(ranked_body_part)


    def add_muscle_load(self, muscle, detailed_adaptation_type, load_range):

        if muscle not in self.muscle_detailed_load.keys():
            self.muscle_detailed_load[muscle] = DetailedTrainingLoad()
        self.muscle_detailed_load[muscle].add_load(detailed_adaptation_type, load_range)

    def add_load(self, functional_movement_action_mapping: FunctionalMovementActionMapping, adaptation_type,
                 movement_action: ExerciseAction, training_load_range, reps=None, duration=None, rpe_range=None, percent_max_hr=None,
                 return_adaptation_types=False):

        includes_lower_body = False
        includes_upper_body = False
        planes_of_movement = set()
        types_of_actions = set()

        total_muscle_load = StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)

        adaptation_type_load = {}
        training_type_load = {}
        detailed_adaptation_types = list(DetailedAdaptationType)
        training_types = list(TrainingType)

        if rpe_range is not None:
            rpe = rpe_range.lowest_value()
        else:
            rpe = None

        for detailed_adaptation_type in detailed_adaptation_types:
            adaptation_type_load[detailed_adaptation_type] = StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)

        for training_type in training_types:
            training_type_load[training_type] = StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)

        for muscle_string, body_part_functional_movement in functional_movement_action_mapping.muscle_load.items():

            muscle = BodyPartSide.from_string(muscle_string)

            body_part_total_load = body_part_functional_movement.total_load()

            if body_part_total_load is not None and body_part_total_load.lowest_value() > 0:  # TODO - this might be temporary and not a detailed enough condition (it's essentially any concentric or eccentric load)

                # only interested in body part regions with both lower / upper load assigned (concentric and eccentric)

                total_muscle_load.add(body_part_total_load)

                includes_lower_body = max(includes_lower_body,
                                          BodyPartGeneralLocation().is_lower_body(muscle.body_part_location))
                includes_upper_body = max(includes_upper_body,
                                          BodyPartGeneralLocation().is_upper_body(muscle.body_part_location))

                planes_of_movement.update(functional_movement_action_mapping.get_planes_of_movement())

                types_of_actions.update(functional_movement_action_mapping.get_types_of_joint_actions())

                muscle_load = StandardErrorRange(observed_value=0)

                if muscle.body_part_location in BodyPartSystems().local_stabilizer_system:
                    muscle_load = body_part_total_load
                elif (muscle.body_part_location in BodyPartSystems().local_stabilizer_system or
                        muscle.body_part_location in BodyPartSystems().deep_longitudinal_subsystem or
                        muscle.body_part_location in BodyPartSystems().posterior_oblique_subsystem or
                        muscle.body_part_location in BodyPartSystems().anterior_oblique_subsystem or
                        muscle.body_part_location in BodyPartSystems().intrinsic_stabilization_subsystem or
                        muscle.body_part_location in BodyPartSystems().core_stabilizers):

                    muscle_load = body_part_functional_movement.total_isometric_load()

                if muscle_load.lowest_value() > 0:
                    # stabilization endurance - cardio
                    if adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
                        adaptation_type_load[DetailedAdaptationType.stabilization_endurance].add(muscle_load)
                        training_type_load[movement_action.training_type].add(muscle_load)
                        self.add_muscle_load(muscle, DetailedAdaptationType.stabilization_endurance,
                                             muscle_load)

                    if reps is not None and rpe is not None:
                        # stabilization endurance - strength
                        if 12 <= reps <= 20 and movement_action.speed in [MovementSpeed.slow, MovementSpeed.none] and 5 <= rpe <= 7:
                            if adaptation_type in [AdaptationType.strength_endurance_strength,
                                                   AdaptationType.maximal_strength_hypertrophic]:
                                adaptation_type_load[DetailedAdaptationType.stabilization_endurance].add(muscle_load)
                                training_type_load[movement_action.training_type].add(muscle_load)
                                self.add_muscle_load(muscle, DetailedAdaptationType.stabilization_endurance,
                                                     muscle_load)

                        # stabilization strength
                        if 8 <= reps <= 12 and movement_action.speed == MovementSpeed.mod and rpe >= 7:
                            if adaptation_type in [AdaptationType.strength_endurance_strength,
                                                   AdaptationType.maximal_strength_hypertrophic]:
                                adaptation_type_load[DetailedAdaptationType.stabilization_strength].add(muscle_load)
                                training_type_load[movement_action.training_type].add(muscle_load)
                                self.add_muscle_load(muscle, DetailedAdaptationType.stabilization_strength,
                                                     muscle_load)

                    # stabilization power
                    if reps is not None:
                        if 8 <= reps <= 12 and movement_action.speed == MovementSpeed.fast:
                            if adaptation_type in [AdaptationType.power_drill, AdaptationType.power_explosive_action]:
                                adaptation_type_load[DetailedAdaptationType.stabilization_power].add(muscle_load)
                                training_type_load[movement_action.training_type].add(muscle_load)
                                self.add_muscle_load(muscle, DetailedAdaptationType.stabilization_power,
                                                     muscle_load)

                if adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
                    if rpe is not None and duration is not None:
                        # muscular endurance
                        # TODO make this less than VO2Max
                        if rpe <= 7 and duration >= 240 * 60:
                            adaptation_type_load[DetailedAdaptationType.muscular_endurance].add(muscle_load)
                            training_type_load[movement_action.training_type].add(muscle_load)
                            self.add_muscle_load(muscle, DetailedAdaptationType.muscular_endurance,
                                                 body_part_total_load)
                        # sustained power
                        elif rpe > 7 and duration >= 15 * 60:
                            adaptation_type_load[DetailedAdaptationType.sustained_power].add(muscle_load)
                            training_type_load[movement_action.training_type].add(muscle_load)
                            self.add_muscle_load(muscle, DetailedAdaptationType.sustained_power,
                                                 body_part_total_load)

                if adaptation_type == AdaptationType.strength_endurance_strength:
                    if rpe is not None and reps is not None:
                        # strength endurance
                        if 8 <= reps <= 12 and 7 <= rpe <= 8 and movement_action.speed == MovementSpeed.mod:
                            adaptation_type_load[DetailedAdaptationType.strength_endurance].add(muscle_load)
                            training_type_load[movement_action.training_type].add(muscle_load)
                            self.add_muscle_load(muscle, DetailedAdaptationType.strength_endurance,
                                                 body_part_total_load)
                        # muscular endurance
                        if 5 <= rpe <= 7 and 12 <= reps <= 20 and movement_action.speed in [MovementSpeed.slow, MovementSpeed.none]:
                            adaptation_type_load[DetailedAdaptationType.muscular_endurance].add(muscle_load)
                            training_type_load[movement_action.training_type].add(muscle_load)
                            self.add_muscle_load(muscle, DetailedAdaptationType.muscular_endurance,
                                                 body_part_total_load)
                # hypertrophy
                if adaptation_type == AdaptationType.maximal_strength_hypertrophic:
                    if rpe is not None and reps is not None:
                        if 6 <= reps <= 12 and 7.5 <= rpe <= 8.5 and movement_action.speed == MovementSpeed.mod:
                            adaptation_type_load[DetailedAdaptationType.hypertrophy].add(muscle_load)
                            training_type_load[movement_action.training_type].add(muscle_load)
                            self.add_muscle_load(muscle, DetailedAdaptationType.hypertrophy,
                                                 body_part_total_load)

                # maximal strength
                if adaptation_type == AdaptationType.maximal_strength_hypertrophic:
                    if rpe is not None and reps is not None:
                        if 1 <= reps <= 5 and 8.5 <= rpe <= 10.0 and movement_action.speed == MovementSpeed.fast:
                            adaptation_type_load[DetailedAdaptationType.maximal_strength].add(muscle_load)
                            training_type_load[movement_action.training_type].add(muscle_load)
                            self.add_muscle_load(muscle, DetailedAdaptationType.maximal_strength,
                                                 body_part_total_load)

                if adaptation_type == AdaptationType.power_drill or adaptation_type == AdaptationType.power_explosive_action:
                    # speed
                    if ((movement_action.speed == MovementSpeed.fast or movement_action.speed == MovementSpeed.explosive) and
                            (movement_action.resistance == MovementResistance.none or movement_action.resistance == MovementResistance.low)):
                        adaptation_type_load[DetailedAdaptationType.speed].add(muscle_load)
                        training_type_load[movement_action.training_type].add(muscle_load)
                        self.add_muscle_load(muscle, DetailedAdaptationType.speed, body_part_total_load)

                    # sustained power
                    if (duration is not None and duration >= 45 * 60 and
                            (movement_action.speed == MovementSpeed.fast or movement_action.speed == MovementSpeed.explosive)):
                        adaptation_type_load[DetailedAdaptationType.sustained_power].add(muscle_load)
                        training_type_load[movement_action.training_type].add(muscle_load)
                        self.add_muscle_load(muscle, DetailedAdaptationType.sustained_power, body_part_total_load)

                    # power
                    if ((movement_action.speed == MovementSpeed.fast or movement_action.speed == MovementSpeed.explosive) and
                            movement_action.resistance == MovementResistance.mod):
                        adaptation_type_load[DetailedAdaptationType.power].add(muscle_load)
                        training_type_load[movement_action.training_type].add(muscle_load)
                        self.add_muscle_load(muscle, DetailedAdaptationType.power, body_part_total_load)

                if adaptation_type == AdaptationType.power_explosive_action and rpe is not None:

                    # maximal power
                    if (3 <= rpe <= 4.5 and (movement_action.speed == MovementSpeed.fast or movement_action.speed == MovementSpeed.explosive)
                            and (movement_action.resistance == MovementResistance.high or movement_action.resistance == MovementResistance.max)):
                        adaptation_type_load[DetailedAdaptationType.maximal_power].add(muscle_load)
                        training_type_load[movement_action.training_type].add(muscle_load)
                        self.add_muscle_load(muscle, DetailedAdaptationType.maximal_power, body_part_total_load)

        # Functional Strength (requires comprehensive look at all actions within functional movement action mapping
        for muscle_string, body_part_functional_movement in functional_movement_action_mapping.muscle_load.items():

            muscle = BodyPartSide.from_string(muscle_string)

            # TODO - likely flawed as in it probably doesnt apply to ALL muscles here, but not sure

            body_part_total_load = body_part_functional_movement.total_load()
            if body_part_total_load is not None and body_part_total_load.lowest_value() > 0:
                if includes_lower_body and includes_upper_body and len(planes_of_movement) > 1 and len(types_of_actions) > 1:
                    if adaptation_type in [AdaptationType.strength_endurance_strength,
                                           AdaptationType.maximal_strength_hypertrophic]:
                        adaptation_type_load[DetailedAdaptationType.functional_strength].add(body_part_total_load)
                        training_type_load[movement_action.training_type].add(body_part_total_load)
                        self.add_muscle_load(muscle, DetailedAdaptationType.functional_strength,
                                             body_part_total_load)

        action_detailed_adaptation_types = []
        # for cardiorespiratory load, we only add session load, not muscle-specific load
        if adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            # TODO - allow for rpe not hr
            if percent_max_hr is not None:
                # base aerobic
                if 65 <= percent_max_hr < 80:
                    training_type_load[movement_action.training_type].add(training_load_range)
                    self.session_detailed_load.add_load(DetailedAdaptationType.base_aerobic_training,
                                                        training_load_range)
                    action_detailed_adaptation_types.append(DetailedAdaptationType.base_aerobic_training)
                # anaerobic threshold
                if 80 <= percent_max_hr < 86:
                    training_type_load[movement_action.training_type].add(training_load_range)
                    self.session_detailed_load.add_load(DetailedAdaptationType.anaerobic_threshold_training,
                                                        training_load_range)
                    action_detailed_adaptation_types.append(DetailedAdaptationType.anaerobic_threshold_training)
                # anaerobic interval
                if 86 <= percent_max_hr:
                    training_type_load[movement_action.training_type].add(training_load_range)
                    self.session_detailed_load.add_load(DetailedAdaptationType.high_intensity_anaerobic_training,
                                                        training_load_range)
                    action_detailed_adaptation_types.append(DetailedAdaptationType.high_intensity_anaerobic_training)

        # scale non-cardio to be comparable with cardio
        if total_muscle_load.lowest_value() > 0:

            for detailed_adaptation_type, load in adaptation_type_load.items():
                if detailed_adaptation_type not in [DetailedAdaptationType.base_aerobic_training,
                                                    DetailedAdaptationType.anaerobic_threshold_training,
                                                    DetailedAdaptationType.high_intensity_anaerobic_training]:
                    adjusted_load = load.plagiarize()
                    adjusted_load.divide_range_simple(total_muscle_load)
                    adjusted_load.multiply_range(training_load_range)
                    self.session_detailed_load.add_load(detailed_adaptation_type, adjusted_load)

            for training_type, training_type_load in training_type_load.items():
                if training_type_load.lowest_value() > 0:
                    if training_type != TrainingType.strength_cardiorespiratory:
                        adjusted_training_type_load = training_type_load.plagiarize()
                        adjusted_training_type_load.divide_range_simple(total_muscle_load)
                        adjusted_training_type_load.multiply_range(training_load_range)
                        self.session_training_type_load.add_load(training_type, adjusted_training_type_load)
                    else:
                        self.session_training_type_load.add_load(training_type, training_type_load)

        if return_adaptation_types:
            action_detailed_adaptation_types.extend([dat for dat, dat_load in adaptation_type_load.items() if dat_load.observed_value > 0])
            return action_detailed_adaptation_types
