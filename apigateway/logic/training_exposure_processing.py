from models.exercise import UnitOfMeasure
from models.exposure import TrainingExposure
from models.movement_actions import MovementSpeed, MovementResistance
from models.movement_tags import AdaptationType, DetailedAdaptationType
from models.training_volume import Assignment, StandardErrorRange


class TrainingExposureProcessor(object):

    def get_exposures(self, exercise):

        exposures = []

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            if exercise.predicted_rpe is not None and exercise.duration is not None:
                # muscular endurance
                # TODO make this less than VO2Max
                if 4 < exercise.predicted_rpe.highest_value() <= 7 and isinstance(exercise.duration, Assignment) and exercise.duration.highest_value() >= 240:
                    exposure = TrainingExposure(DetailedAdaptationType.muscular_endurance)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                elif 4 < exercise.predicted_rpe.highest_value() <= 7 and isinstance(exercise.duration, int) and exercise.duration >= 240:
                    exposure = TrainingExposure(DetailedAdaptationType.muscular_endurance)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # sustained power
                # TODO make this more than VO2Max
                elif exercise.predicted_rpe.highest_value() > 7 and isinstance(exercise.duration, Assignment) and exercise.duration.highest_value() >= 15:
                    exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                elif exercise.predicted_rpe.highest_value() > 7 and isinstance(exercise.duration, int) and exercise.duration >= 15:
                    exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.strength_endurance_strength:
            if exercise.predicted_rpe is not None and exercise.reps_per_set is not None:
                # strength endurance
                if 8 <= exercise.reps_per_set <= 12 and 5 <= exercise.predicted_rpe.highest_value() <= 7 and exercise.movement_speed == MovementSpeed.mod:
                    exposure = TrainingExposure(DetailedAdaptationType.strength_endurance)
                    exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # muscular endurance
                if 5 <= exercise.predicted_rpe.highest_value() <= 7 and 12 <= exercise.reps_per_set <= 20 and exercise.movement_speed in [MovementSpeed.slow,
                                                                                    MovementSpeed.none]:
                    exposure = TrainingExposure(DetailedAdaptationType.muscular_endurance)
                    exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        # hypertrophy
        if exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic:
            if exercise.predicted_rpe is not None and exercise.reps_per_set is not None:
                if 6 <= exercise.reps_per_set <= 12 and 7.5 <= exercise.predicted_rpe.highest_value() <= 8.5 and exercise.movement_speed == MovementSpeed.mod:
                    exposure = TrainingExposure(DetailedAdaptationType.hypertrophy)
                    exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        # maximal strength
        if exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic:
            if exercise.predicted_rpe is not None and exercise.reps_per_set is not None:
                if 1 <= exercise.reps_per_set <= 5 and 8.5 <= exercise.predicted_rpe.highest_value() <= 10.0 and exercise.movement_speed == MovementSpeed.fast:
                    exposure = TrainingExposure(DetailedAdaptationType.maximal_strength)
                    exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.power_drill or exercise.adaptation_type == AdaptationType.power_explosive_action:
            # speed
            if ((exercise.movement_speed == MovementSpeed.fast or exercise.movement_speed == MovementSpeed.explosive) and
                    #(exercise.resistance == MovementResistance.none or exercise.resistance == MovementResistance.low)):
                    (exercise.resistance == MovementResistance.none)):
                exposure = TrainingExposure(DetailedAdaptationType.speed)
                exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

            # sustained power
            if exercise.duration is not None:
                duration = exercise.duration.highest_value() if isinstance(exercise.duration, Assignment) else exercise.duration
                if (duration >= 45 and
                        (exercise.movement_speed == MovementSpeed.fast or exercise.movement_speed == MovementSpeed.explosive)):
                    exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

            if exercise.duration is not None:
                duration = exercise.duration.highest_value() if isinstance(exercise.duration, Assignment) else exercise.duration
                # sustained power
                if (duration > 45 and
                        (exercise.movement_speed == MovementSpeed.fast or exercise.movement_speed == MovementSpeed.explosive)):
                    exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

            # power
            if ((exercise.movement_speed == MovementSpeed.fast or exercise.movement_speed == MovementSpeed.explosive) and
                    exercise.resistance == MovementResistance.low):
                exposure = TrainingExposure(DetailedAdaptationType.power)
                exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.power_explosive_action and exercise.predicted_rpe is not None:

            # maximal power
            if (9 <= exercise.predicted_rpe.highest_value() <= 10 and (
                    exercise.movement_speed == MovementSpeed.fast or exercise.movement_speed == MovementSpeed.explosive)
                    and (exercise.resistance == MovementResistance.high or exercise.resistance == MovementResistance.max)):
                exposure = TrainingExposure(DetailedAdaptationType.maximal_power)
                exposure = self.copy_reps_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            # Note: the conversion to RPE (from HR) is based on McMillan & ACSM
            if exercise.predicted_rpe is not None:
                # base aerobic
                # 65 <= percent_max_hr < 80:
                if exercise.predicted_rpe.lowest_value() >= 2 and exercise.predicted_rpe.highest_value() < 4.1:
                    exposure = TrainingExposure(DetailedAdaptationType.base_aerobic_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # anaerobic threshold
                #80 <= percent_max_hr < 86:
                if exercise.predicted_rpe.lowest_value() >= 4.1 and exercise.predicted_rpe.highest_value() <= 7:
                    exposure = TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # anaerobic interval
                #86 <= percent_max_hr
                if exercise.predicted_rpe.highest_value() > 7:
                    exposure = TrainingExposure(DetailedAdaptationType.high_intensity_anaerobic_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        if len(exposures) == 0:
            stop_here = 0
        return exposures

    def copy_duration_exercise_details_to_exposure(self, exercise, exposure):

        if isinstance(exercise.duration, Assignment):
            exposure.volume = StandardErrorRange(lower_bound=exercise.duration.min_value,
                                                 observed_value=exercise.duration.assigned_value,
                                                 upper_bound=exercise.duration.max_value)
        else:
            exposure.volume = StandardErrorRange(observed_value=exercise.duration)
        exercise.volume_measure = UnitOfMeasure.seconds
        exposure.rpe = exercise.predicted_rpe
        exposure.rpe_load = exercise.rpe_load

        return exposure

    def copy_reps_exercise_details_to_exposure(self, exercise, exposure):

        if isinstance(exercise.reps_per_set, Assignment):
            reps_range = StandardErrorRange(lower_bound=exercise.reps_per_set.min_value,
                                                 observed_value=exercise.reps_per_set.assigned_value,
                                                 upper_bound=exercise.reps_per_set.max_value)
            exposure.volume = reps_range.multiply(exercise.sets)
        else:
            exposure.volume = StandardErrorRange(observed_value=exercise.reps_per_set * exercise.sets)
        exercise.volume_measure = UnitOfMeasure.count
        exposure.rpe = exercise.predicted_rpe
        exposure.rpe_load = exercise.rpe_load

        return exposure

    def aggregate_training_exposures(self, training_exposures):

        aggregated_exposures = {}

        for training_exposure in training_exposures:
            if training_exposure.detailed_adaptation_type not in aggregated_exposures:
                aggregated_exposures[training_exposure.detailed_adaptation_type] = training_exposure
            else:
                rpes = [aggregated_exposures[training_exposure.detailed_adaptation_type].rpe,
                        training_exposure.rpe]
                volumes = [aggregated_exposures[training_exposure.detailed_adaptation_type].volume,
                           training_exposure.volume]

                combined_exposure = TrainingExposure(training_exposure.detailed_adaptation_type)
                combined_exposure.rpe = StandardErrorRange()
                combined_exposure.rpe.lower_bound = StandardErrorRange.get_min_from_error_range_list(rpes)
                combined_exposure.rpe.upper_bound = StandardErrorRange.get_max_from_error_range_list(rpes)
                combined_exposure.rpe.observed_value = (combined_exposure.rpe.lower_bound + combined_exposure.rpe.upper_bound) / float(2)

                combined_exposure.volume = StandardErrorRange()
                combined_exposure.volume.lower_bound = StandardErrorRange.get_min_from_error_range_list(volumes)
                combined_exposure.volume.upper_bound = StandardErrorRange.get_max_from_error_range_list(volumes)
                combined_exposure.volume.observed_value = (combined_exposure.volume.lower_bound + combined_exposure.volume.upper_bound) / float(2)

                rpe_loads = [combined_exposure.rpe.lowest_value() * combined_exposure.volume.lowest_value(),
                             combined_exposure.rpe.lowest_value() * combined_exposure.volume.highest_value(),
                             combined_exposure.rpe.highest_value() * combined_exposure.volume.lowest_value(),
                             combined_exposure.rpe.highest_value() * combined_exposure.volume.highest_value()]

                combined_exposure.rpe_load = StandardErrorRange()
                combined_exposure.rpe_load.lower_bound = min(rpe_loads)
                combined_exposure.rpe_load.upper_bound = max(rpe_loads)
                combined_exposure.rpe_load.observed_value = (combined_exposure.rpe_load.lower_bound + combined_exposure.rpe_load.upper_bound) / float(2)

                aggregated_exposures[training_exposure.detailed_adaptation_type] = combined_exposure

        training_exposure_list = []

        for detailed_adaptation_type, training_exposure in aggregated_exposures.items():
            training_exposure_list.append(training_exposure)

        return training_exposure_list


