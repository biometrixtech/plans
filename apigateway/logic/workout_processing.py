from datastores.movement_library_datastore import MovementLibraryDatastore
from models.cardio_data import get_cardio_data
from models.movement_tags import AdaptationType, TrainingType, MovementSurfaceStability, Equipment
from models.movement_actions import ExternalWeight, LowerBodyStance, UpperBodyStance
from models.exercise import UnitOfMeasure
movement_library = MovementLibraryDatastore().get()
cardio_data = get_cardio_data()
action_library = {}


class WorkoutProcessor(object):

    def process_workout(self, workout_program):
        for workout_section in workout_program.workout_sections:
            workout_section.should_assess_load(cardio_data['no_load_sections'])
            for workout_exercise in workout_section.exercises:
                self.add_movement_detail_to_exercise(workout_exercise)

    def add_movement_detail_to_exercise(self, exercise):
        movement = movement_library[exercise.movement_id]
        exercise.process_movement(movement)
        self.add_action_details_to_exercise(exercise, movement)

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            exercise.convert_reps_to_duration(cardio_data)

    def add_action_details_to_exercise(self, exercise, movement):
        for action_id in movement.primary_actions:
            action = action_library.get(action_id)
            if action is not None:
                self.process_action(action, exercise)
                exercise.primary_actions.append(action)

        for action_id in movement.secondary_actions:
            action = action_library.get(action_id)
            if action is not None:
                self.process_action(action, exercise)
                exercise.secondary_actions.append(action)

        self.apply_explosiveness(exercise, exercise.primary_actions)
        self.apply_explosiveness(exercise, exercise.secondary_actions)

    def process_action(self, action, exercise):
        external_weight = ExternalWeight(exercise.equipment, exercise.weight_in_lbs)
        action.external_weight = [external_weight]

        # action.reps = exercise.reps_per_set
        if action.training_type == TrainingType.strength_cardiorespiratory:
            action.reps = self.convert_reps_to_duration(exercise.reps_per_set, exercise.unit_of_measure, exercise.cardio_action)
        elif exercise.unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            reps_meters = self.convert_distance_to_meters(exercise.reps_per_set, exercise.unit_of_measure)
            action.reps = int(reps_meters / 5)
        elif exercise.unit_of_measure == UnitOfMeasure.seconds:
            action.reps = self.convert_seconds_to_reps(exercise.reps_per_set)
        else:
            action.reps = exercise.reps_per_set

        action.lower_body_stability_rating = self.calculate_lower_body_stability_rating(exercise, action)
        action.upper_body_stability_rating = self.calculate_upper_body_stability_rating(exercise, action)

        action.side = exercise.side
        action.rpe = exercise.rpe
        action.get_training_load()

    def convert_reps_to_duration(self, reps, unit_of_measure, cardio_action):
        # distance to duration
        if unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            reps = self.convert_distance_to_meters(reps, unit_of_measure)
            reps = self.convert_meters_to_seconds(reps, cardio_action)
        elif unit_of_measure == UnitOfMeasure.calories:
            reps = self.convert_calories_to_seconds(reps, cardio_action)
        return reps

    def calculate_lower_body_stability_rating(self, exercise, action):

        if exercise.surface_stability is None or action.lower_body_stance is None:
            return 0.0

        if exercise.surface_stability == MovementSurfaceStability.stable:
            if action.lower_body_stance == LowerBodyStance.double_leg:
                return 0.0
            elif action.lower_body_stance == LowerBodyStance.staggered_stance:
                return 0.3
            elif action.lower_body_stance == LowerBodyStance.split_stance:
                return 0.8
            elif action.lower_body_stance == LowerBodyStance.single_leg:
                return 1.0
            else:
                return 0.0
        elif exercise.surface_stability == MovementSurfaceStability.unstable or exercise.surface_stability == MovementSurfaceStability.very_unstable:
            if action.lower_body_stance == LowerBodyStance.double_leg:
                return 1.2
            elif action.lower_body_stance == LowerBodyStance.staggered_stance:
                return 1.3
            elif action.lower_body_stance == LowerBodyStance.split_stance:
                return 1.5
            elif action.lower_body_stance == LowerBodyStance.single_leg:
                return 2.0
            else:
                return 0.0

    def calculate_upper_body_stability_rating(self, exercise, action):

        if exercise.equipment is None or action.upper_body_stance is None:
            return 0.0

        if exercise.equipment in [Equipment.machine, Equipment.assistance_resistence_bands, Equipment.sled]:
            if action.upper_body_stance == UpperBodyStance.double_arm:
                return 0.0
            elif action.upper_body_stance == UpperBodyStance.alternating_arms:
                return 0.1
            elif action.upper_body_stance == UpperBodyStance.single_arm:
                return 0.2
            elif action.upper_body_stance == UpperBodyStance.single_arm_with_trunk_rotation:
                return 0.3
            else:
                return 0.0
        elif exercise.equipment in [Equipment.atlas_stones, Equipment.yoke, Equipment.dip_belt,
                                    Equipment.medicine_balls, Equipment.farmers_carry_handles, Equipment.sandbags,
                                    Equipment.rower, Equipment.airbike, Equipment.bike, Equipment.ski_erg,
                                    Equipment.ruck]:
            if action.upper_body_stance == UpperBodyStance.double_arm:
                return 0.5
            # these were all improvised/estimated based on logic gaps
            elif action.upper_body_stance == UpperBodyStance.alternating_arms:
                return 0.6
            elif action.upper_body_stance == UpperBodyStance.single_arm:
                return 0.7
            elif action.upper_body_stance == UpperBodyStance.single_arm_with_trunk_rotation:
                return 0.8
            else:
                return 0.0
        elif exercise.equipment in [Equipment.barbells, Equipment.plate, Equipment.sandbags, Equipment.medicine_balls,
                                    Equipment.swimming]:
            if action.upper_body_stance == UpperBodyStance.double_arm:
                return 0.8
            elif action.upper_body_stance == UpperBodyStance.alternating_arms:
                return 1.0
            elif action.upper_body_stance == UpperBodyStance.single_arm:
                return 1.3
            elif action.upper_body_stance == UpperBodyStance.single_arm_with_trunk_rotation:
                return 1.5
            else:
                return 0.0
        elif exercise.equipment in [Equipment.dumbbells, Equipment.double_kettlebell, Equipment.resistence_bands]:
            # this first action is improvised/estimated based on logic gaps
            if action.upper_body_stance == UpperBodyStance.double_arm:
                return 1.3
            elif action.upper_body_stance == UpperBodyStance.alternating_arms:
                return 1.5
            elif action.upper_body_stance == UpperBodyStance.single_arm:
                return 1.8
            elif action.upper_body_stance == UpperBodyStance.single_arm_with_trunk_rotation:
                return 2.0
            else:
                return 0.0

    def apply_explosiveness(self, exercise, action_list):

        if len(action_list) > 0:
            action_explosiveness = [a.explosiveness for a in exercise.primary_actions if a.explosiveness is not None]
            if len(action_explosiveness) > 0:
                max_action_explosiveness = max(action_explosiveness)
                for a in exercise.primary_actions:
                    if a.explosiveness.value == max_action_explosiveness:
                        a.explosiveness_rating = exercise.explosiveness_rating
                    else:
                        explosive_factor = self.get_scaled_explosiveness_factor(max_action_explosiveness, a.explosiveness)
                        a.explosiveness_rating = explosive_factor * exercise.explosiveness_rating

    def get_scaled_explosiveness_factor(self, explosive_value_1, explosive_value_2):

        min_explosive_value = min(explosive_value_1, explosive_value_2)
        max_explosive_value = max(explosive_value_1, explosive_value_2)

        if max_explosive_value == 0:
            return 0

        scaled_explosion_factor = float(min_explosive_value) / float(max_explosive_value)

        return scaled_explosion_factor


    @staticmethod
    def convert_seconds_to_reps(reps):
        # TODO: need this conversion. Is it universal conversion?
        return reps

    @staticmethod
    def convert_distance_to_meters(reps, unit_of_measure):
        if unit_of_measure == UnitOfMeasure.yards:
            reps *= .9144
        elif unit_of_measure == UnitOfMeasure.feet:
            reps *= 0.3048
        elif unit_of_measure == UnitOfMeasure.miles:
            reps *= 1609.34
        elif unit_of_measure == UnitOfMeasure.kilometers:
            reps *= 1000
        return reps

    @staticmethod
    def convert_meters_to_seconds(reps, cardio_action):
        distance_parameters = cardio_data['distance_parameters']
        conversion_ratio = distance_parameters["normalizing_factors"][cardio_action.name]
        time_per_meter = distance_parameters['time_per_unit']
        reps = int(reps * conversion_ratio * time_per_meter)

        return reps

    @staticmethod
    def convert_calories_to_seconds(reps, cardio_action):
        calorie_parameters = cardio_data['calorie_parameters']
        time_per_unit = calorie_parameters['unit'] / calorie_parameters["calories_per_unit"][cardio_action.name]
        reps = int(reps * time_per_unit)

        return reps
