from models.movement_tags import DetailedAdaptationType, AdaptationType
from models.training_load import DetailedTrainingLoad
from models.movement_actions import MovementSpeed, ExerciseAction, MovementResistance
from models.soreness_base import BodyPartSystems, BodyPartSide, BodyPartGeneralLocation
from models.functional_movement import BodyPartFunctionalMovement, FunctionalMovementActionMapping


class DetailedLoadProcessor(object):
    def __init__(self):
        self.session_detailed_load = DetailedTrainingLoad()
        self.muscle_detailed_load = {}

    def add_muscle_load(self, muscle, detailed_adaptation_type, load_range):

        if muscle not in self.muscle_detailed_load.keys():
            self.muscle_detailed_load[muscle] = DetailedTrainingLoad()
        self.muscle_detailed_load[muscle].add_load(detailed_adaptation_type, load_range)

    def add_load(self, functional_movement_action_mapping: FunctionalMovementActionMapping , adaptation_type,
                 movement_action: ExerciseAction, training_load_range, reps=None, duration=None, rpe=None):

        includes_lower_body = False
        includes_upper_body = False
        planes_of_movement = set()
        types_of_actions = set()

        for muscle, body_part_functional_movement in functional_movement_action_mapping.muscle_load:

            if body_part_functional_movement.total_load() > 0:  # TODO - this might be temporary and not a detailed enough condition (it's essentially any concentric or eccentric load)

                # only interested in body part regions with both lower / upper load assigned (concentric and eccentric)

                includes_lower_body = max(includes_lower_body,
                                          BodyPartGeneralLocation().is_lower_body(muscle.body_part_location))
                includes_upper_body = max(includes_upper_body,
                                          BodyPartGeneralLocation().is_upper_body(muscle.body_part_location))

                planes_of_movement.update(functional_movement_action_mapping.get_planes_of_movement())

                types_of_actions.update(functional_movement_action_mapping.get_types_of_joint_actions())

                if (muscle.body_part_location in BodyPartSystems().local_stabilizer_system or
                        muscle.body_part_location in BodyPartSystems().global_stabilization_system):

                    if reps is not None and rpe is not None:
                        # stabilization endurance
                        if 12 <= reps <= 20 and movement_action.speed == MovementSpeed.slow and 5 <= rpe <= 7:
                            if adaptation_type in [AdaptationType.strength_endurance_strength,
                                                   AdaptationType.maximal_strength_hypertrophic]:
                                self.session_detailed_load.add_load(DetailedAdaptationType.stabilization_endurance,
                                                                    training_load_range)
                                self.add_muscle_load(muscle, DetailedAdaptationType.stabilization_endurance,
                                                     training_load_range)

                        # stabilization strength
                        if 8 <= reps <= 12 and movement_action.speed == MovementSpeed.mod and rpe >= 7:
                            if adaptation_type in [AdaptationType.strength_endurance_strength,
                                                   AdaptationType.maximal_strength_hypertrophic]:
                                self.session_detailed_load.add_load(DetailedAdaptationType.stabilization_strength,
                                                                    training_load_range)
                                self.add_muscle_load(muscle, DetailedAdaptationType.stabilization_strength,
                                                     training_load_range)

                    # stabilization power
                    if reps is not None:
                        if 8 <= reps <= 12 and movement_action.speed == MovementSpeed.fast:
                            if adaptation_type in [AdaptationType.power_drill, AdaptationType.power_explosive_action]:
                                self.session_detailed_load.add_load(DetailedAdaptationType.stabilization_power,
                                                                    training_load_range)
                                self.add_muscle_load(muscle, DetailedAdaptationType.stabilization_power,
                                                     training_load_range)

                # muscular endurance
                if adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
                    if rpe is not None and duration is not None:
                        if 5 <= rpe <= 7 and duration >= 240:
                            self.session_detailed_load.add_load(DetailedAdaptationType.muscular_endurance,
                                                                training_load_range)
                            self.add_muscle_load(muscle, DetailedAdaptationType.muscular_endurance,
                                                 training_load_range)

                # strength endurance
                if adaptation_type == AdaptationType.strength_endurance_strength:
                    if rpe is not None and reps is not None:
                        if 8 <= reps <= 12 and 7 <= rpe <= 8 and movement_action.speed == MovementSpeed.mod:
                            self.session_detailed_load.add_load(DetailedAdaptationType.strength_endurance,
                                                                training_load_range)
                            self.add_muscle_load(muscle, DetailedAdaptationType.strength_endurance,
                                                 training_load_range)
                # hypertrophy
                if adaptation_type == AdaptationType.maximal_strength_hypertrophic:
                    if rpe is not None and reps is not None:
                        if 6 <= reps <= 12 and 7.5 <= rpe <= 8.5 and movement_action.speed == MovementSpeed.mod:
                            self.session_detailed_load.add_load(DetailedAdaptationType.hypertrophy,
                                                                training_load_range)
                            self.add_muscle_load(muscle, DetailedAdaptationType.hypertrophy,
                                                 training_load_range)

                # maximal strength
                if adaptation_type == AdaptationType.maximal_strength_hypertrophic:
                    if rpe is not None and reps is not None:
                        if 1 <= reps <= 5 and 8.5 <= rpe <= 10.0 and movement_action.speed == MovementSpeed.fast:
                            self.session_detailed_load.add_load(DetailedAdaptationType.maximal_strength,
                                                                training_load_range)
                            self.add_muscle_load(muscle, DetailedAdaptationType.maximal_strength,
                                                 training_load_range)


                if adaptation_type == AdaptationType.power_drill or adaptation_type == AdaptationType.power_explosive_action:
                    # speed
                    if ((movement_action.speed == MovementSpeed.fast or movement_action.speed == MovementSpeed.explosive) and
                            (movement_action.resistance == MovementResistance.none or movement_action.resistance == MovementResistance.low)):
                        self.session_detailed_load.add_load(DetailedAdaptationType.speed,
                                                            training_load_range)
                        self.add_muscle_load(muscle, DetailedAdaptationType.speed, training_load_range)

                    # sustained power
                    if (duration is not None and duration >= 45 and
                            (movement_action.speed == MovementSpeed.fast or movement_action.speed == MovementSpeed.explosive)):
                        self.session_detailed_load.add_load(DetailedAdaptationType.sustained_power,
                                                            training_load_range)
                        self.add_muscle_load(muscle, DetailedAdaptationType.sustained_power, training_load_range)

                    # power
                    if ((movement_action.speed == MovementSpeed.fast or movement_action.speed == MovementSpeed.explosive) and
                            movement_action.resistance == MovementResistance.mod):
                        self.session_detailed_load.add_load(DetailedAdaptationType.power,
                                                            training_load_range)
                        self.add_muscle_load(muscle, DetailedAdaptationType.power, training_load_range)

                if adaptation_type == AdaptationType.power_explosive_action and rpe is not None:

                    # maximal power
                    if 3 <= rpe <= 4.5 and (movement_action.speed == MovementSpeed.fast and movement_action.speed == MovementSpeed.explosive):
                        self.session_detailed_load.add_load(DetailedAdaptationType.maximal_power,
                                                            training_load_range)
                        self.add_muscle_load(muscle, DetailedAdaptationType.maximal_power, training_load_range)

        # Functional Strength (requires comprehensive look at all actions within functional movement action mapping
        for muscle, body_part_functional_movement in functional_movement_action_mapping.muscle_load:

            if body_part_functional_movement.total_load() > 0:
                if includes_lower_body and includes_upper_body and len(planes_of_movement) > 1 and len(types_of_actions) > 1:
                    if adaptation_type in [AdaptationType.strength_endurance_strength,
                                           AdaptationType.maximal_strength_hypertrophic]:
                        self.session_detailed_load.add_load(DetailedAdaptationType.functional_strength,
                                                            training_load_range)
                        self.add_muscle_load(muscle, DetailedAdaptationType.functional_strength,
                                             training_load_range)


