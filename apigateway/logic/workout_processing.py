from fathomapi.utils.xray import xray_recorder
from datastores.movement_library_datastore import MovementLibraryDatastore
from datastores.action_library_datastore import ActionLibraryDatastore
from logic.heart_rate_processing import HeartRateProcessing
from models.cardio_data import get_cardio_data
from models.bodyweight_coefficients import get_bodyweight_coefficients
from models.movement_tags import AdaptationType, TrainingType, MovementSurfaceStability, Equipment, CardioAction
from models.movement_actions import ExternalWeight, LowerBodyStance, UpperBodyStance, ExerciseAction, Movement
from models.exercise import UnitOfMeasure, WeightMeasure
from models.functional_movement import FunctionalMovementFactory

movement_library = MovementLibraryDatastore().get()
cardio_data = get_cardio_data()
action_library = ActionLibraryDatastore().get()
bodyweight_coefficients = get_bodyweight_coefficients()


class WorkoutProcessor(object):

    @xray_recorder.capture('logic.WorkoutProcessor.process_workout')
    def process_workout(self, workout_program, hr_data=None, user_age=20):

        for workout_section in workout_program.workout_sections:
            workout_section.should_assess_load(cardio_data['no_load_sections'])
            heart_rate_processing = HeartRateProcessing(user_age)
            if hr_data is not None and workout_section.start_date_time is not None and workout_section.end_date_time is not None:
                # assumption here is that all exercises in the section are of similar training/adaptation types
                # such that a single shrz can be calculated for each section
                section_hr = [hr for hr in hr_data if workout_section.start_date_time <= hr.start_date <= workout_section.end_date_time]
                if len(section_hr) > 0:
                    workout_section.shrz = heart_rate_processing.get_shrz(section_hr)
            for workout_exercise in workout_section.exercises:
                workout_exercise.shrz = workout_section.shrz
                self.add_movement_detail_to_exercise(workout_exercise)

            workout_section.should_assess_shrz()


    def add_movement_detail_to_exercise(self, exercise):
        if exercise.movement_id in movement_library:
            movement_json = movement_library[exercise.movement_id]
            movement = Movement.json_deserialise(movement_json)
            exercise.initialize_from_movement(movement)
            self.add_action_details_to_exercise(exercise, movement)

            # if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            #     exercise.convert_reps_to_duration(cardio_data)

    def add_action_details_to_exercise(self, exercise, movement):
        for action_id in movement.primary_actions:
            action_json = action_library.get(action_id)
            if action_json is not None:
                action = ExerciseAction.json_deserialise(action_json)
                self.initialize_action_from_exercise(action, exercise)
                exercise.primary_actions.append(action)
        self.set_action_explosiveness_from_exercise(exercise, exercise.primary_actions)
        for action in exercise.primary_actions:
            action.set_training_load()

        for action_id in movement.secondary_actions:
            action_json = action_library.get(action_id)
            if action_json is not None:
                action = ExerciseAction.json_deserialise(action_json)
                self.initialize_action_from_exercise(action, exercise)
                exercise.secondary_actions.append(action)
        self.set_action_explosiveness_from_exercise(exercise, exercise.secondary_actions)
        for action in exercise.secondary_actions:
            action.set_training_load()

    def initialize_action_from_exercise(self, action, exercise):
        # athlete_bodyweight = 100
        # estimated_rpe = self.get_rpe_from_weight(exercise, action, athlete_bodyweight)
        # sooooo, now what do we do with this estimated_rpe value !?!?!

        action.external_weight = [ExternalWeight(equipment, exercise.weight) for equipment in exercise.equipments]

        if action.training_type == TrainingType.strength_cardiorespiratory:
            if exercise.duration is not None:
                action.reps = exercise.duration
            elif exercise.reps_per_set is not None:
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
        action.shrz = exercise.shrz
        action.bilateral = exercise.bilateral
        action.cardio_action = exercise.cardio_action

        if action.cardio_action is not None:
            action.rep_tempo = self.get_rep_tempo(exercise)
            speed, pace = self.get_speed_pace(exercise)
            action.speed = speed
            action.pace = pace
            # copy over duration and distance from exercise to action
            if exercise.duration is not None:
                action.duration = exercise.duration
            elif speed is not None and exercise.distance is not None:
                action.duration = exercise.distance / speed
            if exercise.distance is not None:
                action.distance = exercise.distance
            elif speed is not None and exercise.duration is not None:
                action.distance = exercise.duration * speed
            # copy other variables
            action.power = exercise.power  # power for rowing/other cardio in watts
            action.grade = exercise.grade  # for biking/running
            # final check if duration was derived, update action reps with duration
            if action.duration is not None and action.reps != action.duration:
                action.reps = action.duration

        # not using these for now in action level
        # action.calories = exercise.calories  # for rowing/other cardio

        # action.get_training_load()

    @staticmethod
    def get_rpe_from_rep_max(rep_max, reps):

        # assume 100 bodyweight as we just want relative percentages
        one_rep_max_weight = (96.7 * 0.033 * rep_max) + 96.7
        actual_reps_weight = (96.7 * 0.033 * reps) + 96.7

        rep_max_percentage = round(min((float(actual_reps_weight) / one_rep_max_weight) * 96.7, 100), 0)

        # even though we base it on 100, math is off by ~ 3.3%

        rpe_lookup_tuples = []
        rpe_lookup_tuples.append((10, 97, 100))
        rpe_lookup_tuples.append((9, 94, 97))
        rpe_lookup_tuples.append((8, 91, 94))
        rpe_lookup_tuples.append((7, 89, 91))
        rpe_lookup_tuples.append((6, 86, 89))
        rpe_lookup_tuples.append((5, 83, 86))
        rpe_lookup_tuples.append((4, 81, 83))
        rpe_lookup_tuples.append((3, 79, 81))
        rpe_lookup_tuples.append((2, 77, 79))
        rpe_lookup_tuples.append((1, 75, 77))
        rpe_lookup_tuples.append((0, 73, 75))

        rpe_tuple = [r for r in rpe_lookup_tuples if r[1] <= rep_max_percentage <= r[2]]

        if len(rpe_tuple) > 0:

            perc_diff = rep_max_percentage - rpe_tuple[0][1]
            rpe_diff = perc_diff / float(rpe_tuple[0][2] - rpe_tuple[0][1])
            rpe = rpe_tuple[0][0] + rpe_diff

            rpe = min(10, rpe)
            rpe = max(0, rpe)

        else:
            rpe = 0

        return round(rpe, 1)

    @staticmethod
    def get_reps_for_percent_rep_max(rep_max_percent):

        if rep_max_percent >= 100:
            return 1

        rep_max = 1
        one_rep_max_weight_1 = (96.7 * 0.033 * rep_max) + 96.7
        # one_rep_max_weight = 100
        rebased_percent = one_rep_max_weight_1 / (float(rep_max_percent)/96.7)

        actual_reps_weight = (rebased_percent - 96.7)
        unrounded_reps = actual_reps_weight / (96.7 * .033)
        # ceil_reps = ceil(unrounded_reps)

        reps = max(round(unrounded_reps, 0), 1)

        return reps

    @staticmethod
    def get_prime_movers_from_joint_actions(joint_action_list, prime_movers):

        functional_movement_factory = FunctionalMovementFactory()
        # prime_movers = []

        # for prioritized_joint_action in joint_action_list:
        #     joint_action_type = prioritized_joint_action.joint_action
        #     functional_movement = functional_movement_factory.get_functional_movement(joint_action_type)
        #     prime_movers.extend(functional_movement.prime_movers)
        #     prime_movers.extend(functional_movement.prime_movers)
        #     prime_movers.extend(functional_movement.prime_movers)
        #     prime_movers.extend(functional_movement.prime_movers)
        # return prime_movers

        for prioritized_joint_action in joint_action_list:
            joint_action_type = prioritized_joint_action.joint_action
            functional_movement = functional_movement_factory.get_functional_movement(joint_action_type)
            if prioritized_joint_action.priority == 1:
                prime_movers['first_prime_movers'].extend(functional_movement.prime_movers)
            elif prioritized_joint_action.priority == 2:
                prime_movers['second_prime_movers'].extend(functional_movement.prime_movers)
            elif prioritized_joint_action.priority == 3:
                prime_movers['third_prime_movers'].extend(functional_movement.prime_movers)
            elif prioritized_joint_action.priority == 4:
                prime_movers['fourth_prime_movers'].extend(functional_movement.prime_movers)

    @staticmethod
    def get_bodyweight_ratio_from_model(bodyweight, prime_movers, equipment):
        bodyweight_ratio = bodyweight_coefficients['const']
        if equipment == Equipment.dumbbells:
            bodyweight_ratio += bodyweight_coefficients['equipment_dumbbells']
        elif equipment == Equipment.cable:
            bodyweight_ratio += bodyweight_coefficients['equipment_cable']
        elif equipment == Equipment.machine:
            bodyweight_ratio += bodyweight_coefficients['equipment_machine']
        bodyweight_ratio += bodyweight * bodyweight_coefficients['bodyweight']

        for prime_mover in prime_movers['first_prime_movers']:
            var = f'prime_mover_{prime_mover}'
            if var in bodyweight_coefficients:
                bodyweight_ratio += bodyweight_coefficients[var]
        for prime_mover in prime_movers['second_prime_movers']:
            var = f'second_prime_mover_{prime_mover}'
            if var in bodyweight_coefficients:
                bodyweight_ratio += bodyweight_coefficients[var]
        return bodyweight_ratio

    def get_action_rep_max_bodyweight_ratio(self, athlete_bodyweight, exercise):

        # # if weight_used = 0, assume it's a bodyweight only exercise
        # # TODO - test this assumption
        # if weight_used == 0:
        #     weight_used = athlete_bodyweight

        # get prime movers from action
        prime_movers = {
            "first_prime_movers": [],
            "second_prime_movers": [],
            "third_prime_movers": [],
            "fourth_prime_movers": []
            }
        for action in exercise.primary_actions:
            self.get_prime_movers_from_joint_actions(action.hip_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.knee_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.ankle_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.trunk_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.shoulder_scapula_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.elbow_joint_action, prime_movers)

        bodyweight_ratio = self.get_bodyweight_ratio_from_model(athlete_bodyweight, prime_movers, exercise.equipment)

        return bodyweight_ratio

    def get_rpe_from_weight(self, workout_exercise, athlete_bodyweight):

        rpe = 0

        reps = workout_exercise.reps_per_set * workout_exercise.sets

        if workout_exercise.weight_measure == WeightMeasure.rep_max:

            rpe = self.get_rpe_from_rep_max(workout_exercise.weight, reps)

        else:
            if workout_exercise.weight_measure == WeightMeasure.percent_bodyweight:

                weight = workout_exercise.weight * athlete_bodyweight

            elif workout_exercise.weight_measure == WeightMeasure.actual_weight:

                weight = workout_exercise.weight

            else:
                return rpe

            bodyweight_ratio = self.get_action_rep_max_bodyweight_ratio(athlete_bodyweight, workout_exercise)
            one_rep_max_weight = bodyweight_ratio * athlete_bodyweight

            # find the % 1RM value
            percent_one_rep_max_weight = min(100, (weight/one_rep_max_weight) * 100)

            # find the n of nRM that corresponds to the % 1RM value.  For example, n = 10 for 75% 1RM aka 10RM = 75% of 1RM
            rep_max_reps = self.get_reps_for_percent_rep_max(percent_one_rep_max_weight)

            # given the amount of reps they completed and the n of nRM, find the RPE
            rpe = self.get_rpe_from_rep_max(rep_max_reps, reps)

        return rpe

    def convert_reps_to_duration(self, reps, unit_of_measure, cardio_action):
        # distance to duration
        if unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            reps = self.convert_distance_to_meters(reps, unit_of_measure)
            reps = self.convert_meters_to_seconds(reps, cardio_action)
        elif unit_of_measure == UnitOfMeasure.calories:
            reps = self.convert_calories_to_seconds(reps, cardio_action)
        return reps

    @staticmethod
    def get_rep_tempo(exercise):
        if exercise.cardio_action == CardioAction.row:
            if exercise.stroke_rate is None or exercise.stroke_rate <= 23:
                return 1
            elif exercise.stroke_rate <= 28:
                return 2
            elif exercise.stroke_rate <= 36:
                return 3
            else:
                return 4
        elif exercise.cardio_action == CardioAction.run:
            if exercise.cadence is None or exercise.cadence <= 130:
                return 1  # walking
            elif exercise.cadence <= 165:
                return 2  # jogging
            elif exercise.cadence <= 195:
                return 3  # running
            else:
                return 4  # sprinting
        elif exercise.cardio_action == CardioAction.cycle:
            if exercise.cadence is None or exercise.cadence <= 70:
                return 1
            elif exercise.cadence <= 90:
                return 2
            elif exercise.cadence <= 110:
                return 3
            else:
                return 4
        else:
            return 1

    @staticmethod
    def get_speed_pace(exercise):
        speed = None
        pace = None
        # get pace
        if exercise.pace is not None:
            if exercise.cardio_action == CardioAction.row:
                pace = exercise.pace / 500
            elif exercise.cardio_action == CardioAction.run:
                pace = exercise.pace / 1609.34
            else:
                pace = exercise.pace
        elif exercise.speed is not None:
            pace = 1 / exercise.speed
        elif exercise.duration is not None and exercise.distance is not None:
            pace = exercise.duration / exercise.distance
        elif exercise.power is not None:
            if exercise.cardio_action == CardioAction.row:
                pace = (2.8 / exercise.power) ** (1 / 3)
        elif exercise.calories is not None and exercise.duration is not None:
            if exercise.cardio_action == CardioAction.row:
                exercise.power = (4200 * exercise.calories - .35 * exercise.duration) / (4 * exercise.duration)  # based on formula used by concept2 rower; reps is assumed to be in seconds
                # watts = exercise.calories / exercise.duration * 1000  # approx calculation; reps is assumed to be in seconds
                pace = (2.8 / exercise.power) ** (1 / 3)

        # get speed
        if exercise.speed is not None:
            speed = exercise.speed
        elif exercise.duration is not None and exercise.distance is not None:
            speed = exercise.distance / exercise.duration
        elif pace is not None:
            speed = 1 / pace
        return speed, pace

    @staticmethod
    def convert_to_pace(pace, watts, calories, reps):
        if pace is not None:
            pace /= 500
        elif watts is not None:
            pace = (2.8 / watts) ** (1 / 3)
        elif calories is not None:
            watts = (4200 * calories - .35 * reps) / (4 * reps)  # based on formula used by concept2 rower; reps is assumed to be in seconds
            # watts = calories / reps * 1000  # approx calculation; reps is assumed to be in seconds
            pace = (2.8 / watts) ** (1 / 3)
        return pace

    @staticmethod
    def calculate_lower_body_stability_rating(exercise, action):

        if exercise.surface_stability is None or action.lower_body_stance is None:
            return 0.0

        if exercise.surface_stability == MovementSurfaceStability.stable:
            if action.lower_body_stance == LowerBodyStance.double_leg:
                return 0.0
            elif action.lower_body_stance == LowerBodyStance.staggered_leg:
                return 0.3
            elif action.lower_body_stance == LowerBodyStance.split_leg:
                return 0.8
            elif action.lower_body_stance == LowerBodyStance.single_leg:
                return 1.0
            else:
                return 0.0
        elif exercise.surface_stability == MovementSurfaceStability.unstable or exercise.surface_stability == MovementSurfaceStability.very_unstable:
            if action.lower_body_stance == LowerBodyStance.double_leg:
                return 1.2
            elif action.lower_body_stance == LowerBodyStance.staggered_leg:
                return 1.3
            elif action.lower_body_stance == LowerBodyStance.split_leg:
                return 1.5
            elif action.lower_body_stance == LowerBodyStance.single_leg:
                return 2.0
            else:
                return 0.0

    @staticmethod
    def calculate_upper_body_stability_rating(exercise, action):
        if len(exercise.equipments) == 0 or action.upper_body_stance is None:
            return 0.0
        equipment = exercise.equipments[0]
        if equipment in [Equipment.machine, Equipment.assistance_resistence_bands, Equipment.sled]:
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
        elif equipment in [Equipment.atlas_stones, Equipment.yoke, Equipment.dip_belt,
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
        elif equipment in [Equipment.barbells, Equipment.plate, Equipment.sandbags, Equipment.medicine_balls,
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
        elif equipment in [Equipment.dumbbells, Equipment.double_kettlebell, Equipment.resistence_bands]:
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

    def set_action_explosiveness_from_exercise(self, exercise, action_list):

        if len(action_list) > 0:
            action_explosiveness = [a.explosiveness for a in action_list if a.explosiveness is not None]
            if len(action_explosiveness) > 0:
                max_action_explosiveness = max(action_explosiveness)
                for a in action_list:
                    if a.explosiveness is not None:
                        if a.explosiveness.value == max_action_explosiveness:
                            a.explosiveness_rating = exercise.explosiveness_rating
                        else:
                            explosive_factor = self.get_scaled_explosiveness_factor(max_action_explosiveness, a.explosiveness)
                            a.explosiveness_rating = explosive_factor * exercise.explosiveness_rating

    @staticmethod
    def get_scaled_explosiveness_factor(explosive_value_1, explosive_value_2):

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
