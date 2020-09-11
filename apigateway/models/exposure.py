from models.training_load import DetailedAdaptationType
from models.movement_tags import AdaptationType
from models.exercise import UnitOfMeasure
from models.movement_actions import MovementSpeed, MovementResistance


class TrainingExposure(object):
    def __init__(self, detailed_adaptation_type, volume=None, volume_measure=None, rpe=None, rpe_load=None):
        self.detailed_adaptation_type = detailed_adaptation_type
        self.volume = volume
        self.volume_measure = volume_measure
        self.rpe = rpe
        self.rpe_load = rpe_load


class TargetTrainingExposure(object):
    def __init__(self, training_exposures, exposure_count=None, priority=0):
        self.training_exposures = training_exposures
        self.exposure_count = exposure_count
        self.priority = priority


class TrainingExposureProcessor(object):

    def get_exposures(self, exercise):

        exposures = []

        if exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory:
            if exercise.predicted_rpe is not None and exercise.duration is not None:
                # muscular endurance
                # TODO make this less than VO2Max
                if exercise.predicted_rpe.highest_value() <= 7 and exercise.duration >= 240:
                    exposure = TrainingExposure(DetailedAdaptationType.muscular_endurance)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # sustained power
                # TODO make this more than VO2Max
                elif exercise.predicted_rpe.highest_value() > 7 and exercise.duration >= 15:
                    exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.strength_endurance_strength:
            if exercise.predicted_rpe is not None and exercise.reps_per_set is not None:
                # strength endurance
                if 8 <= exercise.reps_per_set <= 12 and 7 <= exercise.predicted_rpe.highest_value() <= 8 and exercise.movement_speed == MovementSpeed.mod:
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
                    (exercise.resistance == MovementResistance.none or exercise.resistance == MovementResistance.low)):
                exposure = TrainingExposure(DetailedAdaptationType.speed)
                exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

            # sustained power
            if (exercise.duration is not None and exercise.duration >= 45 * 60 and
                    (exercise.movement_speed == MovementSpeed.fast or exercise.movement_speed == MovementSpeed.explosive)):
                exposure = TrainingExposure(DetailedAdaptationType.sustained_power)
                exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

            # power
            if ((exercise.movement_speed == MovementSpeed.fast or exercise.movement_speed == MovementSpeed.explosive) and
                    exercise.resistance == MovementResistance.mod):
                exposure = TrainingExposure(DetailedAdaptationType.power)
                exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                exposures.append(exposure)

        if exercise.adaptation_type == AdaptationType.power_explosive_action and exercise.predicted_rpe is not None:

            # maximal power
            if (3 <= exercise.predicted_rpe.highest_value() <= 4.5 and (
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
                if exercise.predicted_rpe.lowest_value() >= 2 and exercise.predicted_rpe.highest_value() < 4:
                    exposure = TrainingExposure(DetailedAdaptationType.base_aerobic_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # anaerobic threshold
                #80 <= percent_max_hr < 86:
                if exercise.predicted_rpe.lowest_value() >= 4 and exercise.predicted_rpe.highest_value() <= 5:
                    exposure = TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

                # anaerobic interval
                #86 <= percent_max_hr
                if exercise.predicted_rpe.highest_value() > 5:
                    exposure = TrainingExposure(DetailedAdaptationType.high_intensity_anaerobic_training)
                    exposure = self.copy_duration_exercise_details_to_exposure(exercise, exposure)
                    exposures.append(exposure)

        return exposures

    def copy_duration_exercise_details_to_exposure(self, exercise, exposure):

        exposure.volume = exercise.duration
        exercise.volume_measure = UnitOfMeasure.seconds
        exposure.rpe = exercise.predicted_rpe
        exposure.rpe_load = exercise.rpe_load

        return exposure

    def copy_reps_exercise_details_to_exposure(self, exercise, exposure):

        exposure.volume = exercise.reps_per_set * exercise.sets
        exercise.volume_measure = UnitOfMeasure.count
        exposure.rpe = exercise.predicted_rpe
        exposure.rpe_load = exercise.rpe_load

        return exposure
