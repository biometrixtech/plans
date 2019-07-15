from enum import Enum, IntEnum

from models.body_parts import BodyPart
#from models.trigger import Trigger
from models.goal import AthleteGoal
from models.soreness_base import HistoricSorenessStatus, BaseSoreness, BodyPartLocation, BodyPartSide
from serialisable import Serialisable
import datetime
from fathomapi.utils.exceptions import InvalidSchemaException

from utils import format_datetime, parse_datetime, parse_date
from models.sport import SportName


class SorenessType(Enum):
    muscle_related = 0
    joint_related = 1


class MuscleSorenessSeverity(IntEnum):
    a_little_tight_sore = 1
    sore_can_move_ok = 2
    limits_movement = 3
    struggling_to_move = 4
    painful_to_move = 5


class JointSorenessSeverity(IntEnum):
    discomfort = 1
    dull_ache = 2
    more_severe_dull_ache = 3
    sharp_pain = 4
    inability_to_move = 5


class Soreness(BaseSoreness, Serialisable):
    def __init__(self):
        super().__init__()
        self.body_part = None
        self.historic_soreness_status = None
        self.pain = False
        self.reported_date_time = None
        self.severity = None  # muscle_soreness_severity or joint_soreness_severity
        self.movement = None
        self.side = None
        self.type = None  # soreness_type
        self.count = 1
        self.streak = 0
        self.max_severity = None  # muscle_soreness_severity
        self.max_severity_date_time = None
        self.causal_session = None
        self.first_reported_date_time = None
        self.last_reported_date_time = None
        self.cleared_date_time = None
        self.daily = True

    @classmethod
    def json_deserialise(cls, input_dict):
        soreness = cls()
        soreness.body_part = BodyPart(BodyPartLocation(input_dict['body_part']), None)
        soreness.pain = input_dict.get('pain', False)
        soreness.severity = input_dict['severity']
        soreness.movement = input_dict.get('movement', None)
        soreness.side = input_dict.get('side', None)
        soreness.max_severity = input_dict.get('max_severity', None)
        soreness.first_reported_date_time = input_dict.get('first_reported_date_time', None)
        soreness.last_reported_date_time = input_dict.get('last_reported_date_time', None)
        soreness.cleared_date_time = input_dict.get('cleared_date_time', None)
        soreness.max_severity_date_time = input_dict.get('max_severity_date_time', None)
        soreness.causal_session = input_dict.get('causal_session', None)
        # if input_dict.get('first_reported_date_time', None) is not None:
        #     soreness.first_reported_date_time = parse_date(input_dict['first_reported_date_time'])
        if input_dict.get('reported_date_time', None) is not None:
            soreness.reported_date_time = parse_datetime(input_dict['reported_date_time'])
        return soreness

    def __hash__(self):
        return hash((self.body_part.location, self.side))

    def __eq__(self, other):
        return ((self.body_part.location == other.body_part.location,
                 self.side == other.side))

    def __setattr__(self, name, value):
        if name in ['first_reported_date_time', 'last_reported_date_time', 'reported_date_time', 'cleared_date_time', 'max_severity_date_time']:
            if value is not None and not isinstance(value, datetime.datetime):
                try:
                    value = parse_datetime(value)
                except InvalidSchemaException:
                    value = parse_date(value)
        super().__setattr__(name, value)

    '''deprecated
    def is_dormant_cleared(self):
        try:
            if (self.historic_soreness_status is None or
               self.historic_soreness_status == HistoricSorenessStatus.dormant_cleared or
                self.historic_soreness_status == HistoricSorenessStatus.almost_acute_pain or 
                self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_pain or
                self.historic_soreness_status == HistoricSorenessStatus.almost_persistent_soreness):
                return True
            else:
                return False
        except AttributeError:
            return False
    
    def is_joint(self):
        if (self.body_part.location == BodyPartLocation.shoulder or
                self.body_part.location == BodyPartLocation.hip_flexor or
                self.body_part.location == BodyPartLocation.knee or
                self.body_part.location == BodyPartLocation.ankle or
                self.body_part.location == BodyPartLocation.foot or
                self.body_part.location == BodyPartLocation.lower_back or
                self.body_part.location == BodyPartLocation.elbow or
                self.body_part.location == BodyPartLocation.wrist):
            return True
        else:
            return False

    def is_muscle(self):
        if (
                self.body_part.location == BodyPartLocation.chest or
                self.body_part.location == BodyPartLocation.abdominals or
                self.body_part.location == BodyPartLocation.groin or
                self.body_part.location == BodyPartLocation.quads or
                self.body_part.location == BodyPartLocation.shin or
                self.body_part.location == BodyPartLocation.outer_thigh or
                self.body_part.location == BodyPartLocation.glutes or
                self.body_part.location == BodyPartLocation.hamstrings or
                self.body_part.location == BodyPartLocation.calves or
                self.body_part.location == BodyPartLocation.achilles or
                self.body_part.location == BodyPartLocation.upper_back_neck or
                self.body_part.location == BodyPartLocation.lats or
                self.body_part.location == BodyPartLocation.biceps or
                self.body_part.location == BodyPartLocation.triceps):
            return True
        else:
            return False
    '''

    def json_serialise(self, api=False, daily=False, trigger=False):
        if api:
            ret = {
                   'body_part': self.body_part.location.value,
                   'side': self.side,
                   'pain': self.pain,
                   'status': self.historic_soreness_status.name if self.historic_soreness_status is not None else HistoricSorenessStatus.dormant_cleared.name
                   }
        elif daily:
            ret = {
                   'body_part': self.body_part.location.value,
                   'pain': self.pain,
                   'severity': self.severity,
                   'movement': self.movement,
                   'side': self.side,
                   'reported_date_time': format_datetime(self.reported_date_time)
                   }
        elif trigger:
            ret = {
                   'body_part': self.body_part.location.value,
                   'pain': self.pain,
                   'severity': self.severity,
                   'movement': self.movement,
                   'side': self.side,
                   'first_reported_date_time': format_datetime(self.first_reported_date_time) if self.first_reported_date_time is not None else None,
                  }

        else:
            ret = {
                   'body_part': self.body_part.location.value,
                   'pain': self.pain,
                   'severity': self.severity,
                   'movement': self.movement,
                   'side': self.side
                  }
        return ret

    def __getitem__(self, item):
        return getattr(self, item)


class InjuryStatus(Enum):
    healthy = 0
    healthy_chronically_injured = 1
    returning_from_injury = 2
    returning_from_chronic_injury = 3


class CompletedExercise(Serialisable):

    def __init__(self, athlete_id, exercise_id, event_date):
        self.athlete_id = athlete_id
        self.exercise_id = exercise_id
        self.event_date = event_date

    def json_serialise(self):
        ret = {'athlete_id': self.athlete_id,
               'exercise_id': self.exercise_id,
               'event_date': format_datetime(self.event_date),
               }
        return ret


class CompletedExerciseSummary(Serialisable):

    def __init__(self, athlete_id, exercise_id, exposures):
        self.athlete_id = athlete_id
        self.exercise_id = exercise_id
        self.exposures = exposures

    def json_serialise(self):
        ret = {'athlete_id': self.athlete_id,
               'exercise_id': self.exercise_id,
               'exposures': self.exposures,
               }
        return ret


class Alert(object):
    def __init__(self, goal):
        self.goal = goal
        self.body_part = None
        self.sport_name = None
        self.severity = None

    def json_serialise(self):
        return {
            "goal": self.goal.json_serialise(),
            "body_part": self.body_part.json_serialise() if self.body_part is not None else None,
            "sport_name": self.sport_name.value if self.sport_name is not None else None,
            "severity": self.severity
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        alert = cls(AthleteGoal.json_deserialise(input_dict['goal']))
        alert.body_part = BodyPartSide.json_deserialise(input_dict['body_part']) if input_dict['body_part'] is not None else None
        alert.sport_name = input_dict['sport_name']
        alert.severity = input_dict['severity']
        return alert

    def __setattr__(self, name, value):
        if name == "sport_name" and not isinstance(value, SportName) and value is not None:
            value = SportName(value)
        super().__setattr__(name, value)


