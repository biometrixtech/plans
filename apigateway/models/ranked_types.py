from models.movement_tags import AdaptationTypeMeasure, TrainingType, AdaptationType, DetailedAdaptationType, \
    SubAdaptationType
from models.soreness_base import BodyPartLocation
from models.training_volume import StandardErrorRange
from serialisable import Serialisable


class RankedBodyPart(object):
    def __init__(self, body_part_location, ranking):
        self.body_part_location = body_part_location
        self.power_load = None
        self.ranking = ranking

    def __hash__(self):
        return hash((self.body_part_location, self.ranking))

    def __eq__(self, other):
        val = (self.body_part_location == other.body_part_location and self.ranking == other.ranking)

        return val

    def json_serialise(self):

        ret = {
            'body_part_location': self.body_part_location.value,
            'power_load': self.power_load.json_serialise() if self.power_load is not None else None,
            'ranking': self.ranking
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        ranked_body_part = cls(
                BodyPartLocation(input_dict.get('body_part_location')) if input_dict.get('body_part_location') is not None else None,
                input_dict.get('ranking')
        )
        ranked_body_part.power_load = StandardErrorRange.json_deserialise(input_dict.get('power_load'))
        return ranked_body_part


class RankedAdaptationType(Serialisable):
    def __init__(self, adaptation_type_measure, adaptation_type, ranking, duration):
        self.adaptation_type_measure = adaptation_type_measure
        self.adaptation_type = adaptation_type
        self.ranking = ranking
        self.duration = duration

    def __hash__(self):
        return hash((self.adaptation_type.value, self.ranking))

    def __eq__(self, other):
        val = (self.adaptation_type.value == other.adaptation_type.value and self.ranking == other.ranking)

        return val

    def json_serialise(self):

        ret = {
            'adaptation_type_measure': self.adaptation_type_measure.value,
            'adaptation_type': self.adaptation_type.value,
            'ranking': self.ranking,
            'duration': self.duration
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):

        measure = AdaptationTypeMeasure(input_dict['adaptation_type_measure'])
        ranked_type = RankedAdaptationType(measure,
                                           RankedAdaptationType.get_adaptation_type_from_measure(measure, input_dict['adaptation_type']),
                                           input_dict['ranking'] if input_dict.get('ranking') is not None else None,
                                           input_dict.get('duration')
                                           )
        return ranked_type

    @staticmethod
    def get_adaptation_type_from_measure(adaptation_type_measure, adaptation_type_value):

        if adaptation_type_measure == AdaptationTypeMeasure.training_type:
            return TrainingType(adaptation_type_value)
        elif adaptation_type_measure == AdaptationTypeMeasure.adaptation_type:
            return AdaptationType(adaptation_type_value)
        elif adaptation_type_measure == AdaptationTypeMeasure.detailed_adaptation_type:
            return DetailedAdaptationType(adaptation_type_value)
        else:
            return SubAdaptationType(adaptation_type_value)