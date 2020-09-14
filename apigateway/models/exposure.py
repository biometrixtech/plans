class TrainingExposure(object):
    def __init__(self, detailed_adaptation_type, volume=None, volume_measure=None, rpe=None, rpe_load=None,
                 weekly_load_percentage=None):
        self.detailed_adaptation_type = detailed_adaptation_type
        self.volume = volume
        self.volume_measure = volume_measure
        self.rpe = rpe
        self.rpe_load = rpe_load
        self.weekly_load_percentage = weekly_load_percentage

    def __eq__(self, other):

        if self.detailed_adaptation_type.value == other.detailed_adaptation_type.value:
            if self.weekly_load_percentage is not None and other.weekly_load_percentage is not None:
                if (self.weekly_load_percentage.lower_bound == other.weekly_load_percentage.lower_bound and
                        self.weekly_load_percentage.observed_value == other.weekly_load_percentage.observed_value and
                        self.weekly_load_percentage.upper_bound == other.weekly_load_percentage.upper_bound):
                    return True
            if self.weekly_load_percentage is None and other.weekly_load_percentage is None:
                return True
        else:
            return False


class TargetTrainingExposure(object):
    def __init__(self, training_exposures, exposure_count=None, priority=0):
        self.training_exposures = training_exposures
        self.exposure_count = exposure_count
        self.priority = priority


class AthleteTargetTrainingExposure(TargetTrainingExposure):
    def __init__(self, training_exposures, exposure_count=None, priority=0, progression_week=0):
        super().__init__(training_exposures, exposure_count, priority)
        self.progression_week = progression_week


