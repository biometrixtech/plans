from serialisable import Serialisable
from models.training_volume import StandardErrorRange
from models.movement_tags import DetailedAdaptationType


class TrainingExposure(Serialisable):
    def __init__(self, detailed_adaptation_type, volume=None, volume_measure=None, rpe=None, rpe_load=None,
                 weekly_load_percentage=None):
        self.detailed_adaptation_type = detailed_adaptation_type
        self.volume = volume
        self.volume_measure = volume_measure  #ignoring this for now
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

    def json_serialise(self):
        ret = {
            'detailed_adaptation_type': self.detailed_adaptation_type.value if self.detailed_adaptation_type is not None else None,
            'volume': self.volume.json_serialise() if self.volume is not None else None,
            #'volume': self.volume if self.volume is not None else None,
            'volume_measure': self.volume_measure.value if self.volume_measure is not None else None,
            'rpe': self.rpe.json_serialise() if self.rpe is not None else None,
            'rpe_load': self.rpe_load.json_serialise() if self.rpe_load is not None else None,
            'weekly_load_percentage': self.weekly_load_percentage.json_serialise() if self.weekly_load_percentage is not None else None
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):

        training_exposure = TrainingExposure(DetailedAdaptationType(input_dict['detailed_adaptation_type']))
        training_exposure.volume = StandardErrorRange.json_deserialise(input_dict['volume'])
        training_exposure.rpe = StandardErrorRange.json_deserialise(input_dict['rpe'])
        training_exposure.rpe_load = StandardErrorRange.json_deserialise(input_dict['rpe_load'])
        training_exposure.weekly_load_percentage = StandardErrorRange.json_deserialise(input_dict['weekly_load_percentage'])

        return training_exposure


class TargetTrainingExposure(object):
    def __init__(self, training_exposures, exposure_count=None, priority=0):
        self.training_exposures = training_exposures
        self.exposure_count = exposure_count
        self.priority = priority


class AthleteTargetTrainingExposure(TargetTrainingExposure):
    def __init__(self, training_exposures, exposure_count=None, priority=0, progression_week=0):
        super().__init__(training_exposures, exposure_count, priority)
        self.progression_week = progression_week


