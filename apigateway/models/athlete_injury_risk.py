from models.soreness_base import BodyPartSide
from models.body_part_injury_risk import BodyPartInjuryRisk, BodyPartHistInjuryRisk


class AthleteInjuryRisk(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.items = {}

    def json_serialise(self):
        return {
            'user_id': self.user_id,
            'items': [{"body_part": key.json_serialise(),
                       "injury_risk": value.json_serialise()} for key, value in self.items.items()]
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        athlete_injury_risk = cls(input_dict['user_id'])
        for item in input_dict.get('items', []):
            athlete_injury_risk.items[BodyPartSide.json_deserialise(item['body_part'])] = BodyPartInjuryRisk.json_deserialise(item['injury_risk'])

        return athlete_injury_risk


class AthleteHistInjuryRisk(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.items = {}

    def json_serialise(self):
        return {
            'user_id': self.user_id,
            'items': [{"body_part": key.json_serialise(),
                       "injury_risk": value.json_serialise()} for key, value in self.items.items()]
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        athlete_hist_injury_risk = cls(input_dict['user_id'])
        for item in input_dict.get('items', []):
            athlete_hist_injury_risk.items[BodyPartSide.json_deserialise(item['body_part'])] = BodyPartHistInjuryRisk.json_deserialise(item['injury_risk'])

        return athlete_hist_injury_risk
