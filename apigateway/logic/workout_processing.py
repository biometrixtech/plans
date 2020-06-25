from fathomapi.utils.xray import xray_recorder
from datastores.movement_library_datastore import MovementLibraryDatastore
from datastores.action_library_datastore import ActionLibraryDatastore
from logic.calculators import Calculators
from logic.heart_rate_processing import HeartRateProcessing
from logic.rpe_predictor import RPEPredictor
from logic.bodyweight_ratio_predictor import BodyWeightRatioPredictor
from models.cardio_data import get_cardio_data
from models.bodyweight_coefficients import get_bodyweight_coefficients
from models.movement_tags import AdaptationType, TrainingType, MovementSurfaceStability, Equipment, CardioAction, Gender
from models.movement_actions import ExternalWeight, LowerBodyStance, UpperBodyStance, ExerciseAction, Movement
from models.exercise import UnitOfMeasure, WeightMeasure
from models.functional_movement import FunctionalMovementFactory
from models.training_volume import StandardErrorRange, Assignment

movement_library = MovementLibraryDatastore().get()
cardio_data = get_cardio_data()
action_library = ActionLibraryDatastore().get()
bodyweight_coefficients = get_bodyweight_coefficients()


class WorkoutProcessor(object):
    def __init__(self, user_age=20, user_weight=60.0, gender=Gender.female, hr_data=None, vo2_max=None):
        self.user_age = user_age
        self.user_weight = user_weight
        self.gender = gender
        self.hr_data = hr_data
        self.hr_rpe_predictor = RPEPredictor()
        self.bodyweight_ratio_predictor = BodyWeightRatioPredictor()
        self.vo2_max = vo2_max or Calculators.vo2_max_estimation_demographics(age=user_age, user_weight=user_weight, gender=gender)

    @xray_recorder.capture('logic.WorkoutProcessor.process_planned_workout')
    def process_planned_workout(self, session, assignment_type):
        for workout_section in session.workout.sections:
            workout_section.should_assess_load(cardio_data['no_load_sections'])

            for workout_exercise in workout_section.exercises:
                self.add_movement_detail_to_planned_exercise(workout_exercise, assignment_type)
                if workout_section.assess_load:
                    session.add_tissue_load(workout_exercise.tissue_load)
                    session.add_force_load(workout_exercise.force_load)
                    session.add_power_load(workout_exercise.power_load)
                    session.add_rpe_load(workout_exercise.rpe_load)
                    if workout_exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
                        session.add_strength_endurance_cardiorespiratory_load(workout_exercise.power_load)
                    elif workout_exercise.adaptation_type == AdaptationType.strength_endurance_strength:
                        session.add_strength_endurance_strength_load(workout_exercise.power_load)
                    elif workout_exercise.adaptation_type == AdaptationType.power_drill:
                        session.add_power_drill_load(workout_exercise.power_load)
                    elif workout_exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic:
                        session.add_maximal_strength_hypertrophic_load(workout_exercise.power_load)
                    elif workout_exercise.adaptation_type == AdaptationType.power_explosive_action:
                        session.add_power_explosive_action_load(workout_exercise.power_load)

    @xray_recorder.capture('logic.WorkoutProcessor.process_workout')
    def process_workout(self, session):

        heart_rate_processing = HeartRateProcessing(self.user_age)

        for workout_section in session.workout_program_module.workout_sections:
            workout_section.should_assess_load(cardio_data['no_load_sections'])
            section_hr = []
            if self.hr_data is not None and workout_section.start_date_time is not None and workout_section.end_date_time is not None:
                # assumption here is that all exercises in the section are of similar training/adaptation types
                # such that a single shrz can be calculated for each section
                section_hr = [hr for hr in self.hr_data if workout_section.start_date_time <= hr.start_date <= workout_section.end_date_time]
                if len(section_hr) > 0:
                    workout_section.shrz = heart_rate_processing.get_shrz(section_hr)
            for workout_exercise in workout_section.exercises:
                workout_exercise.shrz = workout_section.shrz
                if len(section_hr) > 0:
                    hr_values = sorted([hr.value for hr in section_hr])  # TODO: improve this to use eercise specific values, not inherit all from section
                    top_25_percentile_hr = hr_values[int(len(hr_values) * .75):]
                    workout_exercise.hr = round(sum(top_25_percentile_hr) / len(top_25_percentile_hr), 0)  # use the average of top 25% ideally this is the end of exercise HR
                self.add_movement_detail_to_exercise(workout_exercise)
                if workout_section.assess_load:
                    session.add_tissue_load(workout_exercise.tissue_load)
                    session.add_force_load(workout_exercise.force_load)
                    session.add_power_load(workout_exercise.power_load)
                    session.add_rpe_load(workout_exercise.rpe_load)
                    if workout_exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
                        session.add_strength_endurance_cardiorespiratory_load(workout_exercise.power_load)
                    elif workout_exercise.adaptation_type == AdaptationType.strength_endurance_strength:
                        session.add_strength_endurance_strength_load(workout_exercise.power_load)
                    elif workout_exercise.adaptation_type == AdaptationType.power_drill:
                        session.add_power_drill_load(workout_exercise.power_load)
                    elif workout_exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic:
                        session.add_maximal_strength_hypertrophic_load(workout_exercise.power_load)
                    elif workout_exercise.adaptation_type == AdaptationType.power_explosive_action:
                        session.add_power_explosive_action_load(workout_exercise.power_load)

            workout_section.should_assess_shrz()

        return session

    def add_movement_detail_to_exercise(self, exercise):
        if exercise.movement_id in movement_library:
            movement_json = movement_library[exercise.movement_id]
            movement = Movement.json_deserialise(movement_json)
            exercise.initialize_from_movement(movement)

            exercise = self.update_exercise_details(exercise)

            for action_id in movement.primary_actions:
                action_json = action_library.get(action_id)
                if action_json is not None:
                    action = ExerciseAction.json_deserialise(action_json)
                    exercise.primary_actions.append(action)
            for action_id in movement.secondary_actions:
                action_json = action_library.get(action_id)
                if action_json is not None:
                    action = ExerciseAction.json_deserialise(action_json)
                    exercise.secondary_actions.append(action)

            self.add_action_details_from_exercise(exercise, exercise.primary_actions)
            self.add_action_details_from_exercise(exercise, exercise.secondary_actions)
            # if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            #     exercise.convert_reps_to_duration(cardio_data)

    def add_movement_detail_to_planned_exercise(self, exercise, assignment_type):
        if exercise.movement_id in movement_library:
            movement_json = movement_library[exercise.movement_id]
            movement = Movement.json_deserialise(movement_json)
            exercise.initialize_from_movement(movement)

            exercise = self.update_planned_exercise_details(exercise, assignment_type)

            for action_id in movement.primary_actions:
                action_json = action_library.get(action_id)
                if action_json is not None:
                    action = ExerciseAction.json_deserialise(action_json)
                    exercise.primary_actions.append(action)
            for action_id in movement.secondary_actions:
                action_json = action_library.get(action_id)
                if action_json is not None:
                    action = ExerciseAction.json_deserialise(action_json)
                    exercise.secondary_actions.append(action)

            self.add_action_details_from_exercise(exercise, exercise.primary_actions)
            self.add_action_details_from_exercise(exercise, exercise.secondary_actions)

    def update_exercise_details(self, exercise):

        exercise.set_intensity()
        exercise.set_adaption_type()
        exercise.set_rep_tempo()
        exercise.set_reps_duration()

        if exercise.training_type == TrainingType.strength_cardiorespiratory:
            exercise.set_speed_pace()
            exercise = self.set_power_force_cardio(exercise)
            # if exercise.reps_per_set is not None and exercise.duration is None:
            #     exercise.duration = self.convert_reps_to_duration(exercise.reps_per_set, exercise.unit_of_measure, exercise.cardio_action)
            if exercise.speed is not None and exercise.distance is not None and exercise.duration is None:
                exercise.duration = exercise.distance / exercise.speed
            elif exercise.speed is not None and exercise.duration is not None and exercise.distance is None:
                exercise.distance = exercise.duration * exercise.speed
            exercise.predicted_rpe = StandardErrorRange()
            if exercise.hr is not None:
                exercise.predicted_rpe.observed_value = self.hr_rpe_predictor.predict_rpe(hr=exercise.hr)
            else:
                exercise.predicted_rpe.observed_value = exercise.shrz or 4
        else:
            # if exercise.unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles,
            #                                 UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            #     reps_meters = self.convert_distance_to_meters(exercise.reps_per_set, exercise.unit_of_measure)
            #     exercise.reps_per_set = int(reps_meters / 5)
            # elif exercise.unit_of_measure == UnitOfMeasure.seconds:
            #     exercise.reps_per_set = self.convert_seconds_to_reps(exercise.reps_per_set)
            exercise = self.set_force_power_weighted(exercise)
            exercise.predicted_rpe = self.get_rpe_from_weight(exercise)

        exercise = self.set_total_volume(exercise)
        exercise.set_training_loads()

        return exercise

    def update_planned_exercise_details(self, exercise, assignment_type):

        #exercise.set_intensity()
        exercise.set_adaption_type()
        #exercise.set_rep_tempo()
        exercise.update_primary_from_alternates(assignment_type)
        exercise.set_reps_duration()

        if exercise.training_type == TrainingType.strength_cardiorespiratory:
            exercise.set_speed_pace()
            exercise = self.set_planned_power(exercise)
            # if exercise.reps_per_set is not None and exercise.duration is None:
            #     exercise.duration = self.convert_reps_to_duration(exercise.reps_per_set, exercise.unit_of_measure, exercise.cardio_action)
            if exercise.speed is not None and exercise.distance is not None and exercise.duration is None:
                exercise.duration = Assignment.divide_assignments(exercise.distance, exercise.speed)
            elif exercise.speed is not None and exercise.duration is not None and exercise.distance is None:
                exercise.distance = Assignment.multiply_assignments(exercise.duration, exercise.speed)
            # TODO planned exercise predicted RPE?
            self.set_planned_cardio_rpe(exercise)
        else:
            # if exercise.unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles,
            #                                 UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            #     reps_meters = self.convert_distance_to_meters(exercise.reps_per_set, exercise.unit_of_measure)
            #     exercise.reps_per_set = int(reps_meters / 5)
            # elif exercise.unit_of_measure == UnitOfMeasure.seconds:
            #     exercise.reps_per_set = self.convert_seconds_to_reps(exercise.reps_per_set)
            exercise = self.set_force_power_weighted(exercise)
            # TODO this needs to handle planned exercises
            # exercise.predicted_rpe = self.get_rpe_from_weight(exercise)

        exercise = self.set_planned_total_volume(exercise)
        exercise.set_training_loads()

        # TODO - set detailed adaptation type

        return exercise

    def add_action_details_from_exercise(self, exercise, actions):

        for action in actions:
            self.initialize_action_from_exercise(action, exercise)

        self.set_action_explosiveness_from_exercise(exercise, actions)

        for action in actions:
            action.training_intensity = exercise.training_intensity
            action.set_external_weight_distribution()
            action.set_body_weight_distribution()
            action.set_training_load(exercise.total_volume)

        # for action_id in movement.secondary_actions:
        #     action_json = action_library.get(action_id)
        #     if action_json is not None:
        #         action = ExerciseAction.json_deserialise(action_json)
        #         self.initialize_action_from_exercise(action, exercise)
        #         exercise.secondary_actions.append(action)
        # self.set_action_explosiveness_from_exercise(exercise, exercise.secondary_actions)
        # for action in exercise.secondary_actions:
        #     action.training_intensity = exercise.training_intensity
        #     action.set_external_weight_distribution()
        #     action.set_body_weight_distribution()
        #     action.set_training_load(total_volume)

    def initialize_action_from_exercise(self, action, exercise):

        action.external_weight = [ExternalWeight(equipment, exercise.weight) for equipment in exercise.equipments]

        action.training_type = exercise.training_type
        action.adaptation_type = exercise.adaptation_type

        action.lower_body_stability_rating = self.calculate_lower_body_stability_rating(exercise, action)
        action.upper_body_stability_rating = self.calculate_upper_body_stability_rating(exercise, action)
        action.side = exercise.side
        # action.rpe = exercise.rpe
        # action.shrz = exercise.shrz
        #action.bilateral = exercise.bilateral
        action.cardio_action = exercise.cardio_action
        # copy other variables
        action.power = exercise.power  # power for rowing/other cardio in watts
        action.force = exercise.force
        # action.grade = exercise.grade  # for biking/running
        #
        # action.rep_tempo = exercise.rep_tempo
        # action.speed = exercise.speed
        # action.pace = exercise.pace
        # copy over duration and distance from exercise to action
        # action.duration = exercise.duration
        # action.distance = exercise.distance

    def set_force_power_weighted(self, exercise):
        if exercise.weight_measure == WeightMeasure.actual_weight:
            weight = exercise.weight
        elif exercise.weight_measure == WeightMeasure.percent_bodyweight:
            weight = exercise.weight * self.user_weight
        else:
            weight = 20  # TODO: need to change this
        exercise.force = StandardErrorRange(observed_value=Calculators.force_resistance_exercise(weight))

        # TODO: still need to differentiate distance traveled by exercise
        observed_power = Calculators.power_resistance_exercise(
            weight_used=weight,
            user_weight=self.user_weight,
            time_eccentric=exercise.duration_per_rep.observed_value / 2,
            time_concentric=exercise.duration_per_rep.observed_value / 2
            )
        exercise.power = StandardErrorRange(observed_value=observed_power)
        if exercise.reps_per_set is None:
            # TODO: still need to differentiate distance traveled by exercise
            power_1 = Calculators.power_resistance_exercise(
                weight_used=weight,
                user_weight=self.user_weight,
                time_eccentric=exercise.duration_per_rep.lower_bound / 2,
                time_concentric=exercise.duration_per_rep.lower_bound / 2
                )
            power_2 = Calculators.power_resistance_exercise(
                weight_used=weight,
                user_weight=self.user_weight,
                time_eccentric=exercise.duration_per_rep.upper_bound / 2,
                time_concentric=exercise.duration_per_rep.upper_bound / 2
                )
            exercise.power.lower_bound = min([power_1, power_2])
            exercise.power.upper_bound = max([power_1, power_2])

        return exercise

    def set_total_volume(self, exercise):

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            #total_volume = exercise.reps
            if exercise.duration is not None:
                total_volume = exercise.duration
            elif exercise.reps_per_set is not None:
                total_volume = self.convert_reps_to_duration(exercise.reps_per_set, exercise.unit_of_measure, exercise.cardio_action)
            else:
                total_volume = 0
        elif exercise.unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            reps_meters = self.convert_distance_to_meters(exercise.reps_per_set, exercise.unit_of_measure)
            total_volume = int(reps_meters / 5) * 4
        elif exercise.unit_of_measure == UnitOfMeasure.seconds:
            total_volume = exercise.reps_per_set
        else:
            # adaptation_type based volume
            if exercise.duration is not None:
                total_volume = exercise.duration
            elif exercise.reps_per_set is not None:
                if exercise.duration_per_rep is not None:
                    duration_per_rep = exercise.duration_per_rep.observed_value
                else:
                    duration_per_rep = 3
                total_volume = exercise.reps_per_set * duration_per_rep
            else:
                total_volume = 0

        exercise.total_volume = total_volume
        return exercise

    def set_planned_total_volume(self, exercise):

        total_volume = Assignment()

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            #total_volume = exercise.reps
            if exercise.duration is not None:
                total_volume = exercise.duration
            elif exercise.reps_per_set is not None:
                total_volume.assigned_value = self.convert_reps_to_duration(exercise.reps_per_set, exercise.unit_of_measure, exercise.cardio_action)
            else:
                total_volume.assigned_value = 0
        elif exercise.unit_of_measure in [UnitOfMeasure.yards, UnitOfMeasure.feet, UnitOfMeasure.miles, UnitOfMeasure.kilometers, UnitOfMeasure.meters]:
            reps_meters = self.convert_distance_to_meters(exercise.reps_per_set, exercise.unit_of_measure)
            total_volume.assigned_value = int(reps_meters / 5) * 4
        elif exercise.unit_of_measure == UnitOfMeasure.seconds:
            total_volume.assigned_value = exercise.reps_per_set
        else:
            # adaptation_type based volume
            if exercise.duration is not None:
                total_volume = exercise.duration
            elif exercise.reps_per_set is not None:
                if exercise.duration_per_rep is not None:
                    duration_per_rep = exercise.duration_per_rep.observed_value
                else:
                    duration_per_rep = 3
                total_volume.assigned_value = exercise.reps_per_set * duration_per_rep
            else:
                total_volume.assigned_value = 0

        exercise.total_volume = total_volume

        return exercise

    def set_power_force_cardio(self, exercise):
        # if power is not provided, calculate from available dta or estimate
        if exercise.power is None:
            if exercise.speed is not None:
                if exercise.cardio_action == CardioAction.row:
                    exercise.power = StandardErrorRange(observed_value=Calculators.power_rowing(exercise.speed))
                elif exercise.cardio_action == CardioAction.run:
                    exercise.power = StandardErrorRange(observed_value=Calculators.power_running(exercise.speed, exercise.grade, self.user_weight))
                elif exercise.cardio_action == CardioAction.cycle:
                    exercise.power = StandardErrorRange(observed_value=Calculators.power_cycling(exercise.speed, user_weight=self.user_weight, grade=exercise.grade))
                else:  # for all other cardio types
                    exercise.power = StandardErrorRange(observed_value=Calculators.power_cardio(exercise.cardio_action, self.user_weight, self.gender))
            else:
                exercise.power = StandardErrorRange(observed_value=Calculators.power_cardio(exercise.cardio_action, self.user_weight, self.gender))

        if exercise.cardio_action == CardioAction.row:
            exercise.force = StandardErrorRange(observed_value=Calculators.force_rowing(exercise.power.observed_value, exercise.speed))
            if exercise.power.lower_bound is not None:
                exercise.force.lower_bound = Calculators.force_rowing(exercise.power.lower_bound, exercise.speed)
            if exercise.power.upper_bound is not None:
                exercise.force.upper_bound = Calculators.force_rowing(exercise.power.upper_bound, exercise.speed)
        elif exercise.cardio_action == CardioAction.run:
            exercise.force = StandardErrorRange(
                observed_value=Calculators.force_running(exercise.power.observed_value, exercise.speed))
            if exercise.power.lower_bound is not None:
                exercise.force.lower_bound = Calculators.force_running(exercise.power.lower_bound, exercise.speed)
            if exercise.power.upper_bound is not None:
                exercise.force.upper_bound = Calculators.force_running(exercise.power.upper_bound, exercise.speed)
        elif exercise.cardio_action == CardioAction.cycle:
            exercise.force = StandardErrorRange(
                observed_value=Calculators.force_cycling(exercise.power.observed_value, exercise.speed))
            if exercise.power.lower_bound is not None:
                exercise.force.lower_bound = Calculators.force_cycling(exercise.power.lower_bound, exercise.speed)
            if exercise.power.upper_bound is not None:
                exercise.force.upper_bound = Calculators.force_cycling(exercise.power.upper_bound, exercise.speed)
        else:  # for all other cardio types
            exercise.force = StandardErrorRange(
                observed_value=Calculators.force_cardio(exercise.cardio_action, self.user_weight, self.gender))
            if exercise.power.lower_bound is not None:
                exercise.force.lower_bound = Calculators.force_cardio(exercise.cardio_action, self.user_weight, self.gender)
            if exercise.power.upper_bound is not None:
                exercise.force.upper_bound = Calculators.force_cardio(exercise.cardio_action, self.user_weight, self.gender)

        return exercise

    def set_planned_cardio_rpe(self, exercise):
        # assume planned power is already in place for some of cardio types
        work_vo2 = StandardErrorRange()
        if exercise.cardio_action == CardioAction.run:
            if exercise.power.lower_bound is not None:
                work_vo2.lower_bound = Calculators.work_vo2_running_from_power(exercise.power.lower_bound, self.user_weight)
            if exercise.power.observed_value is not None:
                work_vo2.observed_value = Calculators.work_vo2_running_from_power(exercise.power.observed_value, self.user_weight)
            if exercise.power.upper_bound is not None:
                work_vo2.upper_bound = Calculators.work_vo2_running_from_power(exercise.power.upper_bound, self.user_weight)
        elif exercise.cardio_action == CardioAction.cycle:
            if exercise.power.lower_bound is not None:
                work_vo2.lower_bound = Calculators.work_vo2_cycling_alternate(exercise.power.lower_bound, self.user_weight)
            if exercise.power.observed_value is not None:
                work_vo2.observed_value = Calculators.work_vo2_cycling_alternate(exercise.power.observed_value, self.user_weight)
            if exercise.power.upper_bound is not None:
                work_vo2.upper_bound = Calculators.work_vo2_cycling_alternate(exercise.power.upper_bound, self.user_weight)
        elif exercise.cardio_action == CardioAction.row:
            if exercise.power.lower_bound is not None:
                work_vo2.lower_bound = Calculators.work_vo2_rowing_from_power(exercise.power.lower_bound, self.user_weight)
            if exercise.power.observed_value is not None:
                work_vo2.observed_value = Calculators.work_vo2_rowing_from_power(exercise.power.observed_value, self.user_weight)
            if exercise.power.upper_bound is not None:
                work_vo2.upper_bound = Calculators.work_vo2_rowing_from_power(exercise.power.upper_bound, self.user_weight)
        else:
            work_vo2.observed_value = Calculators.work_vo2_cardio(exercise.cardio_action, self.gender)

        percent_vo2max = work_vo2.plagiarize()
        # self.vo2_max = StandardErrorRange(lower_bound=30, observed_value=32, upper_bound=35)
        percent_vo2max.divide_range(self.vo2_max)
        percent_vo2max.multiply(100)
        predicted_rpe = StandardErrorRange()
        if percent_vo2max.lower_bound is not None:
            predicted_rpe.lower_bound = Calculators.rpe_from_percent_vo2_max(percent_vo2max.lower_bound)
        if percent_vo2max.observed_value is not None:
            predicted_rpe.observed_value = Calculators.rpe_from_percent_vo2_max(percent_vo2max.observed_value)
        if percent_vo2max.upper_bound is not None:
            predicted_rpe.upper_bound = Calculators.rpe_from_percent_vo2_max(percent_vo2max.upper_bound)

        exercise.predicted_rpe = predicted_rpe

    def set_planned_power(self, exercise):
        # if power is not provided, calculate from available dta or estimate
        if exercise.power is None:
            if exercise.speed is not None:
                if exercise.cardio_action == CardioAction.row:
                    power_ranger = StandardErrorRange()
                    if exercise.speed.assigned_value is not None:
                        power_ranger.observed_value = Calculators.power_rowing(exercise.speed.assigned_value)
                    else:
                        power_ranger.lower_bound = Calculators.power_rowing(exercise.speed.min_value)
                        if exercise.speed.max_value is not None:
                            power_ranger.upper_bound = Calculators.power_rowing(exercise.speed.max_value)
                            average_speed = (exercise.speed.min_value + exercise.speed.max_value) / float(2)
                            power_ranger.observed_value = Calculators.power_rowing(average_speed)
                        else:
                            # TODO don't like this assumption
                            power_ranger.observed_value = Calculators.power_rowing(exercise.speed.min_value)
                    exercise.power = power_ranger
                elif exercise.cardio_action == CardioAction.run:

                    power_ranger = StandardErrorRange()
                    if exercise.speed.assigned_value is not None:
                        if exercise.grade.assigned_value is not None:
                            power_ranger.observed_value = Calculators.power_running(exercise.speed.assigned_value, exercise.grade.assigned_value, self.user_weight)
                        else:
                            power_ranger.lower_bound = Calculators.power_running(exercise.speed.assigned_value,
                                                                                 exercise.grade.min_value,
                                                                                 self.user_weight)
                            if exercise.grade.max_value is not None:
                                power_ranger.upper_bound = Calculators.power_running(exercise.speed.assigned_value,
                                                                                     exercise.grade.max_value,
                                                                                     self.user_weight)
                                average_grade = (exercise.grade.min_value + exercise.grade.max_value) / float(2)
                                power_ranger.observed_value = Calculators.power_running(exercise.speed.assigned_value,
                                                                                        average_grade, self.user_weight)
                            else:
                                # TODO don't like this assumption
                                power_ranger.observed_value = Calculators.power_running(exercise.speed.assigned_value,
                                                                                        exercise.grade.min_value,
                                                                                        self.user_weight)
                    else:
                        if exercise.grade.assigned_value is not None:
                            power_ranger.lower_bound = Calculators.power_running(exercise.speed.min_value, exercise.grade.assigned_value, self.user_weight)
                            if exercise.speed.max_value is not None:
                                average_speed = (exercise.speed.min_value + exercise.speed.max_value) / float(2)
                                power_ranger.observed_value = Calculators.power_running(average_speed, exercise.grade.assigned_value, self.user_weight)
                                power_ranger.upper_bound = Calculators.power_running(exercise.speed.max_value, exercise.grade.assigned_value, self.user_weight)
                            else:
                                power_ranger.observed_value = power_ranger.lower_bound

                        else:
                            # means both speed and grade use min/max values
                            power_ranger.lower_bound = Calculators.power_running(exercise.speed.min_value,
                                                                                 exercise.grade.min_value,
                                                                                 self.user_weight)
                            if exercise.speed.max_value is not None and exercise.grade.max_value is not None:
                                power_ranger.upper_bound = Calculators.power_running(exercise.speed.max_value,
                                                                                     exercise.grade.max_value,
                                                                                     self.user_weight)
                                average_grade = (exercise.grade.min_value + exercise.grade.max_value) / float(2)
                                average_speed = (exercise.speed.min_value + exercise.speed.max_value) / float(2)
                                power_ranger.observed_value = Calculators.power_running(average_speed,
                                                                                        average_grade,
                                                                                        self.user_weight)
                            else:
                                # exercise.speed.max_value is None and/or exercise.grade.max_value is None:
                                power_ranger.upper_bound = None
                                # TODO don't like this assumption
                                power_ranger.observed_value = Calculators.power_running(exercise.speed.min_value,
                                                                                        exercise.grade.min_value,
                                                                                        self.user_weight)
                    exercise.power = power_ranger
                elif exercise.cardio_action == CardioAction.cycle:
                    power_ranger = StandardErrorRange()
                    if exercise.speed.assigned_value is not None:
                        if exercise.grade.assigned_value is not None:
                            power_ranger.observed_value = Calculators.power_cycling(exercise.speed.assigned_value, grade=exercise.grade.assigned_value, user_weight=self.user_weight)
                        else:
                            power_ranger.lower_bound = Calculators.power_cycling(exercise.speed.assigned_value,
                                                                                 grade=exercise.grade.min_value,
                                                                                 user_weight=self.user_weight)
                            if exercise.grade.max_value is not None:
                                power_ranger.upper_bound = Calculators.power_cycling(exercise.speed.assigned_value,
                                                                                     grade=exercise.grade.max_value,
                                                                                     user_weight=self.user_weight)
                                average_grade = (exercise.grade.min_value + exercise.grade.max_value) / float(2)
                                power_ranger.observed_value = Calculators.power_cycling(exercise.speed.assigned_value,
                                                                                        grade=average_grade,
                                                                                        user_weight=self.user_weight)
                            else:
                                # TODO don't like this assumption
                                power_ranger.observed_value = Calculators.power_cycling(exercise.speed.assigned_value,
                                                                                        grade=exercise.grade.min_value,
                                                                                        user_weight=self.user_weight)
                    else:
                        if exercise.grade.assigned_value is not None:
                            power_ranger.lower_bound = Calculators.power_cycling(exercise.speed.min_value,
                                                                                 grade=exercise.grade.assigned_value,
                                                                                 user_weight=self.user_weight)
                            if exercise.speed.max_value is not None:
                                average_speed = (exercise.speed.min_value + exercise.speed.max_value) / float(2)
                                power_ranger.observed_value = Calculators.power_cycling(average_speed, exercise.grade.assigned_value, self.user_weight)
                                power_ranger.upper_bound = Calculators.power_cycling(exercise.speed.max_value, exercise.grade.assigned_value, self.user_weight)
                            else:
                                power_ranger.observed_value = power_ranger.lower_bound

                        else:
                            # means both speed and grade use min/max values
                            power_ranger.lower_bound = Calculators.power_cycling(exercise.speed.min_value,
                                                                                 grade=exercise.grade.min_value,
                                                                                 user_weight=self.user_weight)
                            if exercise.speed.max_value is not None and exercise.grade.max_value is not None:
                                power_ranger.upper_bound = Calculators.power_cycling(exercise.speed.max_value,
                                                                                     grade=exercise.grade.max_value,
                                                                                     user_weight=self.user_weight)
                                average_grade = (exercise.grade.min_value + exercise.grade.max_value) / float(2)
                                average_speed = (exercise.speed.min_value + exercise.speed.max_value) / float(2)
                                power_ranger.observed_value = Calculators.power_cycling(average_speed,
                                                                                        grade=average_grade,
                                                                                        user_weight=self.user_weight)
                            else:
                                # exercise.speed.max_value is None and/or exercise.grade.max_value is None:
                                power_ranger.upper_bound = None
                                # TODO don't like this assumption
                                power_ranger.observed_value = Calculators.power_cycling(exercise.speed.min_value,
                                                                                        grade=exercise.grade.min_value,
                                                                                        user_weight=self.user_weight)
                    exercise.power = power_ranger
                else:  # for all other cardio types
                    exercise.power = StandardErrorRange(
                        observed_value=Calculators.power_cardio(exercise.cardio_action, self.user_weight, self.gender))
            else:
                exercise.power = StandardErrorRange(
                    observed_value=Calculators.power_cardio(exercise.cardio_action, self.user_weight, self.gender))

        if exercise.power.lower_bound is None:
            exercise.power.lower_bound = exercise.power.observed_value

        if exercise.power.upper_bound is None:
            exercise.power.upper_bound = exercise.power.observed_value

        return exercise

    @staticmethod
    def get_rpe_from_rep_max(rep_max, reps):

        # assume 100 bodyweight as we just want relative percentages
        one_rep_max_weight = (96.7 * 0.033 * rep_max) + 96.7
        actual_reps_weight = (96.7 * 0.033 * reps) + 96.7

        rep_max_percentage = round(min((float(actual_reps_weight) / one_rep_max_weight) * 96.7, 100), 0)

        # even though we base it on 100, math is off by ~ 3.3%
        # TODO: check to see if this is too restrictive
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
            rpe = max(1, rpe)

        else:
            rpe = 1

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

    def get_max_reps_for_bodyweight_exercises(self, bodyweight_ratio, weight=0):
        external_weight_ratio = weight / self.user_weight
        bodyweight_ratio -= external_weight_ratio
        if bodyweight_ratio <= 1:
            return 1

        return max(int((bodyweight_ratio - 1) / .033), 1)

    @staticmethod
    def get_prime_movers_from_joint_actions(joint_action_list, prime_movers):

        functional_movement_factory = FunctionalMovementFactory()

        for prioritized_joint_action in joint_action_list:
            joint_action_type = prioritized_joint_action.joint_action
            functional_movement = functional_movement_factory.get_functional_movement(joint_action_type)
            if prioritized_joint_action.priority == 1:
                prime_movers['first_prime_movers'].update(functional_movement.prime_movers)
            elif prioritized_joint_action.priority == 2:
                prime_movers['second_prime_movers'].update(functional_movement.prime_movers)
            elif prioritized_joint_action.priority == 3:
                prime_movers['third_prime_movers'].update(functional_movement.prime_movers)
            elif prioritized_joint_action.priority == 4:
                prime_movers['fourth_prime_movers'].update(functional_movement.prime_movers)

    def get_one_rep_max_bodyweight_ratio(self, exercise):
        # get prime movers from action
        prime_movers = {
            "first_prime_movers": set(),
            "second_prime_movers": set(),
            "third_prime_movers": set(),
            "fourth_prime_movers": set()
            }
        for action in exercise.primary_actions:
            self.get_prime_movers_from_joint_actions(action.hip_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.knee_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.ankle_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.trunk_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.shoulder_scapula_joint_action, prime_movers)
            self.get_prime_movers_from_joint_actions(action.elbow_joint_action, prime_movers)

        if len(exercise.equipments) > 0:
            equipment = exercise.equipments[0]
        else:
            equipment = Equipment.bodyweight
        if equipment == Equipment.no_equipment:
            equipment = Equipment.bodyweight
        bodyweight_ratio = self.bodyweight_ratio_predictor.predict_bodyweight_ratio(self.user_weight, self.gender, prime_movers, equipment)

        return bodyweight_ratio

    def get_rpe_from_weight(self, workout_exercise):
        rpe = StandardErrorRange(observed_value=1)
        # get correct equipment
        if len(workout_exercise.equipments) > 0:
            equipment = workout_exercise.equipments[0]
        else:
            equipment = Equipment.bodyweight
        if equipment == Equipment.no_equipment:
            equipment = Equipment.bodyweight

        # get reps
        reps = StandardErrorRange(observed_value=0)
        if workout_exercise.reps_per_set is not None:
            reps.observed_value = workout_exercise.reps_per_set * workout_exercise.sets
        elif workout_exercise.duration is not None:
            reps.lower_bound = workout_exercise.duration / workout_exercise.duration_per_rep.upper_bound
            reps.upper_bound = workout_exercise.duration / workout_exercise.duration_per_rep.lower_bound
            reps.observed_value = workout_exercise.duration / workout_exercise.duration_per_rep.observed_value

        if workout_exercise.weight_measure == WeightMeasure.rep_max:
            rpe.observed_value = self.get_rpe_from_rep_max(workout_exercise.weight, reps.observed_value)
            if reps.lower_bound is not None:
                rpe1 = self.get_rpe_from_rep_max(workout_exercise.weight, reps.observed_value)
                rpe2 = self.get_rpe_from_rep_max(workout_exercise.weight, reps.observed_value)
                rpe.lower_bound = min([rpe1, rpe2])
                rpe.upper_bound = max([rpe1, rpe2])

        else:
            if workout_exercise.weight_measure == WeightMeasure.percent_bodyweight:

                weight = workout_exercise.weight * self.user_weight

            elif workout_exercise.weight_measure == WeightMeasure.actual_weight:

                weight = workout_exercise.weight
            else:
                weight = 0

            one_rep_max_bodyweight_ratio = self.get_one_rep_max_bodyweight_ratio(workout_exercise)
            if equipment == Equipment.bodyweight:
                rep_max_reps = self.get_max_reps_for_bodyweight_exercises(one_rep_max_bodyweight_ratio, weight)
            else:
                if weight == 0:
                    return rpe
                else:
                    one_rep_max_weight = one_rep_max_bodyweight_ratio * self.user_weight
                    # find the % 1RM value
                    percent_one_rep_max_weight = min(100, (weight / one_rep_max_weight) * 100)

                    # find the n of nRM that corresponds to the % 1RM value.  For example, n = 10 for 75% 1RM aka 10RM = 75% of 1RM
                    rep_max_reps = self.get_reps_for_percent_rep_max(percent_one_rep_max_weight)

            # given the amount of reps they completed and the n of nRM, find the RPE
            rpe.observed_value = self.get_rpe_from_rep_max(rep_max_reps, reps.observed_value)
            if reps.lower_bound is not None:
                rpe1 = self.get_rpe_from_rep_max(rep_max_reps, reps.lower_bound)
                rpe2 = self.get_rpe_from_rep_max(rep_max_reps, reps.upper_bound)
                rpe.lower_bound = min([rpe1, rpe2])
                rpe.upper_bound = max([rpe1, rpe2])

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
