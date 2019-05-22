import datetime
from enum import Enum

from fathomapi.utils.exceptions import InvalidSchemaException
from models.soreness import BodyPartLocation, BaseSoreness, HistoricSorenessStatus
from models.session import Session
from serialisable import Serialisable
from utils import parse_datetime, format_datetime, parse_date


class SorenessCause(Enum):
    unknown = 0
    overloading = 1
    weakness = 1
    dysfunction = 2


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


'''
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
        soreness.user_id = input_dict.get('user_id', None)
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
'''


class CoOccurrence(object):
    def __init__(self, body_part_location, side, historic_soreness_status, first_reported_date_time):
        self.body_part_location = body_part_location
        self.historic_soreness_status = historic_soreness_status
        self.side = side
        self.first_reported_date_time = first_reported_date_time
        self.symmetric_pair = False
        self.count = 0
        self.percentage = 0.0
        self.correlation = 0.0
        self.confidence = 0.0

    def __eq__(self, other):
        return self.body_part_location == other.body_part_location and self.side == other.side

    def increment(self, value):
        self.count += value


class HistoricSorenessMatrix(object):
    def __init__(self):
        self.left_right_body_parts = []
        self.element_diff_moment_order_1 = 0.0
        self.element_diff_moment_order_2 = 0.0
        self.entropy = 0.0
        self.uniformity = 0.0
        self.homogeneity = 0.0


class HistoricSoreness(BaseSoreness, Serialisable):

    def __init__(self, body_part_location, side, is_pain):
        super().__init__()
        self.body_part_location = body_part_location
        # self.historic_soreness_status = HistoricSorenessStatus.dormant_cleared
        self.is_pain = is_pain
        self.side = side
        self.user_id = None
        self.streak = 0
        self.streak_start_date = None
        self.average_severity = 0.0
        self.max_severity = None  # muscle_soreness_severity
        self.max_severity_date_time = None
        self.causal_session = None
        self.first_reported_date_time = None
        self.last_reported_date_time = None
        self.cleared_date_time = None
        # self.last_reported = ""
        self.ask_acute_pain_question = False
        self.ask_persistent_2_question = False
        self.co_occurrences = []
        self.historic_severity = []
        self.cause = SorenessCause.unknown

    def __setattr__(self, name, value):
        if name in ['first_reported_date_time', 'last_reported_date_time', 'streak_start_date', 'cleared_date_time',
                    'max_severity_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    def json_serialise(self, api=False, cleared=False):
        if api:
            ret = {"body_part": self.body_part_location.value,
                   "side": self.side,
                   "pain": self.is_pain,
                   "status": self.historic_soreness_status.name}
        else:
            ret = {
                   'body_part_location': self.body_part_location.value,
                   'historic_soreness_status': self.historic_soreness_status.value,
                   'is_pain': self.is_pain,
                   'side': self.side,
                   'streak': self.streak,
                   'streak_start_date': format_datetime(self.streak_start_date) if self.streak_start_date is not None else None,
                   'average_severity': self.average_severity,
                   'max_severity': self.max_severity,
                   'max_severity_date_time': format_datetime(self.max_severity_date_time) if self.max_severity_date_time is not None else None,
                   'causal_session': self.causal_session.json_serialise() if self.causal_session is not None else None,
                   'first_reported_date_time': format_datetime(self.first_reported_date_time) if self.first_reported_date_time is not None else None,
                   'last_reported_date_time': format_datetime(self.last_reported_date_time) if self.last_reported_date_time is not None else None,
                   'cleared_date_time': format_datetime(self.cleared_date_time) if self.cleared_date_time is not None else None,
                   'historic_severity': [hist.json_serialise() for hist in self.historic_severity],
                   # 'last_reported': self.last_reported,
                   'ask_acute_pain_question': self.ask_acute_pain_question,
                   'ask_persistent_2_question': self.ask_persistent_2_question,
                   'cause': self.cause.value
                  }
            if cleared:
                ret['user_id'] = self.user_id
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        soreness = cls(BodyPartLocation(input_dict['body_part_location']), input_dict.get('side', None), input_dict.get('is_pain', False))
        soreness.user_id = input_dict.get('user_id', None)
        hist_sore_status = input_dict.get('historic_soreness_status', None)
        soreness.historic_soreness_status = HistoricSorenessStatus(hist_sore_status) if hist_sore_status is not None else HistoricSorenessStatus.dormant_cleared
        soreness.streak = input_dict.get('streak', 0)
        soreness.streak_start_date = input_dict.get("streak_start_date", None) if input_dict.get("streak_start_date", None) != "" else None
        soreness.average_severity = input_dict.get('average_severity', 0.0)
        soreness.max_severity = input_dict.get('max_severity', None)
        soreness.max_severity_date_time = input_dict.get('max_severity_date_time', None)
        soreness.first_reported_date_time = input_dict.get("first_reported_date_time", None) if input_dict.get("first_reported_date_time", None) != "" else None
        # soreness.last_reported = input_dict.get("last_reported", "")
        soreness.causal_session = Session.json_deserialise(input_dict['causal_session']) if input_dict.get(
            'causal_session', None) is not None else None
        soreness.first_reported_date_time = input_dict.get('first_reported_date_time', None)

        last_reported_date_time = input_dict.get('last_reported_date_time', None)
        if last_reported_date_time is None:
            last_reported = input_dict.get("last_reported", "")
            if last_reported != "":
                last_reported_date_time = parse_date(last_reported)

        soreness.last_reported_date_time = last_reported_date_time
        soreness.cleared_date_time = input_dict.get('cleared_date_time', None)
        soreness.historic_severity = [HistoricSeverity.json_deserialise(hist) for hist in input_dict.get('historic_severity', [])]
        soreness.ask_acute_pain_question = input_dict.get("ask_acute_pain_question", False)
        soreness.ask_persistent_2_question = input_dict.get("ask_persistent_2_question", False)

        return soreness

    def is_joint(self):
        if (self.body_part_location == BodyPartLocation.hip_flexor or
                self.body_part_location == BodyPartLocation.knee or
                self.body_part_location == BodyPartLocation.ankle or
                self.body_part_location == BodyPartLocation.foot or
                self.body_part_location == BodyPartLocation.achilles or
                self.body_part_location == BodyPartLocation.elbow or
                self.body_part_location == BodyPartLocation.wrist):
            return True
        else:
            return False

    def is_muscle(self):
        if (self.body_part_location == BodyPartLocation.shoulder or
                self.body_part_location == BodyPartLocation.chest or
                self.body_part_location == BodyPartLocation.abdominals or
                self.body_part_location == BodyPartLocation.groin or
                self.body_part_location == BodyPartLocation.quads or
                self.body_part_location == BodyPartLocation.shin or
                self.body_part_location == BodyPartLocation.outer_thigh or
                self.body_part_location == BodyPartLocation.lower_back or
                self.body_part_location == BodyPartLocation.glutes or
                self.body_part_location == BodyPartLocation.hamstrings or
                self.body_part_location == BodyPartLocation.calves or
                self.body_part_location == BodyPartLocation.upper_back_neck or
                self.body_part_location == BodyPartLocation.lats):
            return True
        else:
            return False
