import datetime
from models.body_parts import BodyPart, BodyPartFactory
from models.soreness_base import BodyPartLocation
from utils import format_datetime, parse_datetime


class Symptom(object):
    def __init__(self, user_id, reported_date_time):
        self.user_id = user_id
        self.reported_date_time = reported_date_time
        self.body_part = None
        self.pain = False
        self.side = None
        self.tight = None
        self.knots = None
        self.ache = None
        self.sharp = None

    def json_serialise(self):
        return {
            "user_id": self.user_id,
            'body_part': self.body_part.location.value,
            'side': self.side,
            'pain': self.pain,
            'tight': self.tight,
            'knots': self.knots,
            'ache': self.ache,
            'sharp': self.sharp,
            'reported_date_time': format_datetime(self.reported_date_time) if self.reported_date_time is not None else None
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        symptom = cls(input_dict['user_id'], input_dict['reported_date_time'])
        symptom.body_part = BodyPart(BodyPartLocation(input_dict['body_part']), None)
        symptom.side = input_dict.get('side')
        symptom.tight = input_dict.get('tight')
        symptom.knots = input_dict.get('knots')
        symptom.ache = input_dict.get('ache')
        symptom.sharp = input_dict.get('sharp')

        return symptom

    def __setattr__(self, name, value):
        if name in ['reported_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        elif name == 'sharp' and value is not None:
            self.pain = True
        elif name == 'ache' and value is not None:
            if not BodyPartFactory().is_muscle(self.body_part):
                self.pain = True

        super().__setattr__(name, value)
