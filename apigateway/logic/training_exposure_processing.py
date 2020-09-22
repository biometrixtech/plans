from models.exercise import UnitOfMeasure
from models.exposure import TrainingExposure
from models.movement_actions import MovementSpeed, MovementResistance, Explosiveness
from models.movement_tags import AdaptationType, DetailedAdaptationType
from models.training_volume import Assignment, StandardErrorRange
from logic.calculators import Calculators


class TrainingExposureProcessor(object):

    def get_exposures(self, exercise):

        exposures = []

        if exercise.movement_speed is not None and exercise.resistance is not None and exercise.displacement is not None:
            explosiveness = Calculators.get_force_level(exercise.movement_speed, exercise.resistance, exercise.displacement)
            explosiveness_value = Explosiveness[explosiveness]
        else:
            explosiveness_value = None

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory and explosiveness_value is not None:
            if exercise.duration is not None and explosiveness_value in [Explosiveness.mod_force, Explosiveness.high_force, Explosiveness.max_force]:
                duration = exercise.duration.highest_value() if isinstance(exercise.duration,
                                                                           Assignment) else exercise.duration
                # # muscular endurance
                # if explosiveness_value == Explosiveness.mod_force and duration >= 20:
                #     exposure = TrainingExposure(DetailedAdaptationType.muscular_endurance)
                #     exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                #     exposures.append(exposure)

                # sustained power
                if explosiveness_value in [Explosiveness.high_force, Explosiveness.max_force] and duration >= 20:
                    exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.strength_endurance_strength:

            reps_per_set = exercise.get_exercise_reps_per_set()

            if explosiveness_value is not None and reps_per_set is not None:
                # strength endurance
                if explosiveness_value in [Explosiveness.mod_force, Explosiveness.low_force] and 8 <= reps_per_set.highest_value():
                    exposure = TrainingExposure(DetailedAdaptationType.strength_endurance)
                    exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # muscular endurance
                if explosiveness_value in [Explosiveness.mod_force, Explosiveness.low_force] and (12 <= reps_per_set.highest_value() or
                                                                         exercise.movement_speed in [MovementSpeed.slow, MovementSpeed.none]):
                    exposure = TrainingExposure(DetailedAdaptationType.muscular_endurance)
                    exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        # hypertrophy
        if exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic:

            reps_per_set = exercise.get_exercise_reps_per_set()

            if explosiveness_value is not None and reps_per_set is not None:
                if 6 <= reps_per_set.highest_value() and explosiveness_value == Explosiveness.high_force:
                    exposure = TrainingExposure(DetailedAdaptationType.hypertrophy)
                    exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        # maximal strength
        if exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic:
            if explosiveness_value is not None and explosiveness_value == Explosiveness.max_force:
                    exposure = TrainingExposure(DetailedAdaptationType.maximal_strength)
                    exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        if ((exercise.adaptation_type == AdaptationType.power_drill or exercise.adaptation_type == AdaptationType.power_explosive_action)
                and explosiveness_value is not None):
            # speed
            if explosiveness_value in [Explosiveness.bit_of_force]:
                exposure = TrainingExposure(DetailedAdaptationType.speed)
                exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

            # power
            if explosiveness_value == Explosiveness.low_force:
                exposure = TrainingExposure(DetailedAdaptationType.power)
                exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

            # sustained power
            if exercise.duration is not None:
                duration = exercise.duration.highest_value() if isinstance(exercise.duration, Assignment) else exercise.duration
                if duration >= 20 and explosiveness_value in [Explosiveness.low_force, Explosiveness.mod_force, Explosiveness.high_force, Explosiveness.max_force]:
                    exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

            # if exercise.duration is not None:
            #     duration = exercise.duration if isinstance(exercise.duration, int) else exercise.duration
            #     # sustained power
            #     if duration >= 20 and explosiveness_value in [Explosiveness.high_force, Explosiveness.max_force]:
            #         exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
            #         exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
            #         exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.power_explosive_action and explosiveness_value is not None:

            # maximal power
            if explosiveness_value in [Explosiveness.max_force, Explosiveness.high_force, Explosiveness.mod_force]:
                exposure = TrainingExposure(DetailedAdaptationType.maximal_power)
                exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            # Note: the conversion to RPE (from HR) is based on McMillan & ACSM
            if exercise.predicted_rpe is not None and exercise.duration is not None:
                # base aerobic
                # 65 <= percent_max_hr < 80:
                duration = exercise.duration.highest_value() if isinstance(exercise.duration,
                                                                           Assignment) else exercise.duration
                if exercise.percent_max_hr is not None and .65 <= exercise.percent_max_hr < .8:
                    exposure = TrainingExposure(DetailedAdaptationType.base_aerobic_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                elif exercise.predicted_rpe.lowest_value() >= 2.0 and exercise.predicted_rpe.highest_value() <= 4.0:  # and duration >= 300:
                    exposure = TrainingExposure(DetailedAdaptationType.base_aerobic_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # anaerobic threshold
                #80 <= percent_max_hr < 86:
                if exercise.percent_max_hr is not None and .8 <= exercise.percent_max_hr < .86 and duration >= 20:
                    exposure = TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)
                elif exercise.predicted_rpe.lowest_value() > 4.0 and exercise.predicted_rpe.highest_value() <= 7 and duration >= 20:
                    exposure = TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # anaerobic interval
                #86 <= percent_max_hr
                if exercise.percent_max_hr is not None and .86 <= exercise.percent_max_hr:
                    exposure = TrainingExposure(DetailedAdaptationType.high_intensity_anaerobic_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)
                elif exercise.predicted_rpe.highest_value() > 7 and duration >= 5:
                    exposure = TrainingExposure(DetailedAdaptationType.high_intensity_anaerobic_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        if len(exposures) == 0:
            stop_here = 0
        return exposures

    def copy_duration_exercise_details_to_exposure(self, exercise, exposure):
        if exercise.duration is not None:
            if isinstance(exercise.duration, Assignment):
                exposure.volume = StandardErrorRange(lower_bound=exercise.duration.min_value,
                                                     observed_value=exercise.duration.assigned_value,
                                                     upper_bound=exercise.duration.max_value)
            else:
                exposure.volume = StandardErrorRange(observed_value=exercise.duration)
        else:
            if isinstance(exercise.total_volume, Assignment):
                exposure.volume = StandardErrorRange(lower_bound=exercise.total_volume.min_value,
                                                     observed_value=exercise.total_volume.assigned_value,
                                                     upper_bound=exercise.total_volume.max_value)
            else:
                exposure.volume = StandardErrorRange(observed_value=exercise.total_volume)
        exposure.volume_measure = UnitOfMeasure.seconds
        exposure.rpe = exercise.predicted_rpe
        exposure.rpe_load = exercise.rpe_load

        return exposure

    def copy_reps_exercise_details_to_exposure(self, exercise, exposure):
        reps_range = exercise.get_exercise_reps_per_set()
        reps_range.multiply(exercise.sets)
        # if isinstance(exercise.reps_per_set, Assignment):
        #     reps_range = StandardErrorRange(lower_bound=exercise.reps_per_set.min_value,
        #                                          observed_value=exercise.reps_per_set.assigned_value,
        #                                          upper_bound=exercise.reps_per_set.max_value)
        #     exposure.volume = reps_range.multiply(exercise.sets)
        # else:
        #     exposure.volume = StandardErrorRange(observed_value=exercise.reps_per_set * exercise.sets)
        exposure.volume = reps_range
        exposure.volume_measure = UnitOfMeasure.count
        exposure.rpe = exercise.predicted_rpe
        exposure.rpe_load = exercise.rpe_load

        return exposure

    def aggregate_training_exposures(self, training_exposures):

        training_exposure_list = []

        detailed_adaptation_types = set([d.detailed_adaptation_type for d in training_exposures])

        for detailed_adaptation_type in detailed_adaptation_types:

            relevant_exposures = [t for t in training_exposures if t.detailed_adaptation_type.value == detailed_adaptation_type.value]

            volumes = [t.volume for t in training_exposures if
                       t.detailed_adaptation_type.value == detailed_adaptation_type.value]

            aggregated_volume = StandardErrorRange.get_sum_from_error_range_list(volumes)

            rpe_loads = [t.rpe_load for t in training_exposures if
                         t.detailed_adaptation_type.value == detailed_adaptation_type.value]

            aggregated_rpe_load = StandardErrorRange.get_sum_from_error_range_list(rpe_loads)

            rpe_list = []

            for relevant_exposure in relevant_exposures:

                rpe = relevant_exposure.rpe.plagiarize()

                weight = StandardErrorRange()

                weight.add(relevant_exposure.volume)

                weight.divide_range(aggregated_volume)

                rpe.multiply_range(weight)

                rpe_list.append(rpe)

            aggregated_rpe = StandardErrorRange.get_sum_from_error_range_list(rpe_list)

            combined_exposure = TrainingExposure(detailed_adaptation_type)
            combined_exposure.volume = aggregated_volume.plagiarize()
            combined_exposure.rpe_load = aggregated_rpe_load.plagiarize()
            combined_exposure.rpe = aggregated_rpe.plagiarize()
            combined_exposure.volume_measure = relevant_exposures[0].volume_measure #TODO - DANGEROUS ASSUMPTION!!

            training_exposure_list.append(combined_exposure)

        # for training_exposure in training_exposures:
        #     if training_exposure.detailed_adaptation_type not in aggregated_exposures:
        #         aggregated_exposures[training_exposure.detailed_adaptation_type] = training_exposure
        #     else:
        #         rpes = [aggregated_exposures[training_exposure.detailed_adaptation_type].rpe,
        #                 training_exposure.rpe]
        #         volumes = [aggregated_exposures[training_exposure.detailed_adaptation_type].volume,
        #                    training_exposure.volume]
        #
        #         combined_exposure = TrainingExposure(training_exposure.detailed_adaptation_type)
        #         combined_exposure.rpe = StandardErrorRange()
        #         combined_exposure.rpe.lower_bound = StandardErrorRange.get_min_from_error_range_list(rpes)
        #         combined_exposure.rpe.upper_bound = StandardErrorRange.get_max_from_error_range_list(rpes)
        #         combined_exposure.rpe.observed_value = (combined_exposure.rpe.lower_bound + combined_exposure.rpe.upper_bound) / float(2)
        #
        #         combined_exposure.volume = StandardErrorRange()
        #
        #         combined_exposure.volume.lower_bound = StandardErrorRange.get_min_from_error_range_list(volumes)
        #         combined_exposure.volume.upper_bound = StandardErrorRange.get_max_from_error_range_list(volumes)
        #         combined_exposure.volume.observed_value = (combined_exposure.volume.lower_bound + combined_exposure.volume.upper_bound) / float(2)
        #
        #         rpe_loads = [combined_exposure.rpe.lowest_value() * combined_exposure.volume.lowest_value(),
        #                      combined_exposure.rpe.lowest_value() * combined_exposure.volume.highest_value(),
        #                      combined_exposure.rpe.highest_value() * combined_exposure.volume.lowest_value(),
        #                      combined_exposure.rpe.highest_value() * combined_exposure.volume.highest_value()]
        #
        #         combined_exposure.rpe_load = StandardErrorRange()
        #         combined_exposure.rpe_load.lower_bound = min(rpe_loads)
        #         combined_exposure.rpe_load.upper_bound = max(rpe_loads)
        #         combined_exposure.rpe_load.observed_value = (combined_exposure.rpe_load.lower_bound + combined_exposure.rpe_load.upper_bound) / float(2)
        #
        #         aggregated_exposures[training_exposure.detailed_adaptation_type] = combined_exposure
        #
        # for detailed_adaptation_type, training_exposure in aggregated_exposures.items():
        #     training_exposure_list.append(training_exposure)

        return training_exposure_list


