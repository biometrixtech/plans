import datetime
from models.soreness import BodyPartLocation, BodyPart
from models.session import Session
from utils import parse_datetime, format_datetime


class HistoricSeverity(object):
    def __init__(self, reported_date_time, severity, movement):
        self.reported_date_time = reported_date_time
        self.severity = severity
        self.movement = movement

    def json_serialise(self):
        return {
            'reported_date_time': format_datetime(self.reported_date_time) if self.reported_date_time is not None else None,
            'severity': self.severity,
            'movement': self.movement
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        return cls(input_dict['reported_date_time'], input_dict['severity'], input_dict['movement'])

    def __setattr__(self, name, value):
        if name in ['reported_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)


class DelayedOnsetMuscleSoreness(object):
    def __init__(self):
        self.user_id = None
        self.body_part = None
        self.max_severity = None  # muscle_soreness_severity
        self.max_severity_date_time = None
        self.side = None
        self.causal_session = None
        self.first_reported_date_time = None
        self.last_reported_date_time = None
        self.cleared_date_time = None
        self.historic_severity = []

    def json_serialise(self, cleared=False):
        ret = {
            'body_part': self.body_part.location.value,
            'max_severity': self.max_severity,
            'max_severity_date_time': format_datetime(self.max_severity_date_time) if self.max_severity_date_time is not None else None,
            'side': self.side,
            'causal_session': self.causal_session.json_serialise() if self.causal_session is not None else None,
            'first_reported_date_time': format_datetime(self.first_reported_date_time) if self.first_reported_date_time is not None else None,
            'last_reported_date_time': format_datetime(self.last_reported_date_time) if self.last_reported_date_time is not None else None,
            'cleared_date_time': format_datetime(self.cleared_date_time) if self.cleared_date_time is not None else None,
            'historic_severity': [hist.json_serialise() for hist in self.historic_severity]
        }
        if cleared:
            ret['user_id'] = self.user_id
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        soreness = cls()
        soreness.user_id = user_id
        soreness.body_part = BodyPart(BodyPartLocation(input_dict['body_part']), None)
        soreness.max_severity = input_dict.get('max_severity', None)
        soreness.max_severity_date_time = input_dict.get('max_severity_date_time', None)
        soreness.side = input_dict.get('side', None)
        soreness.causal_session = Session.json_deserialise(input_dict['causal_session']) if input_dict.get('causal_session', None) is not None else None
        soreness.first_reported_date_time = input_dict.get('first_reported_date_time', None)
        soreness.last_reported_date_time = input_dict.get('last_reported_date_time', None)
        soreness.cleared_date_time = input_dict.get('cleared_date_time', None)
        soreness.historic_severity = [HistoricSeverity.json_deserialise(hist) for hist in input_dict['historic_severity']]

        return soreness

    def __setattr__(self, name, value):
        if name in ['first_reported_date_time', 'max_severity_date_time', 'last_reported_date_time', 'cleared_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                value = parse_datetime(value)
        super().__setattr__(name, value)
