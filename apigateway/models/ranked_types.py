from models.soreness_base import BodyPartLocation
from models.training_volume import StandardErrorRange


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