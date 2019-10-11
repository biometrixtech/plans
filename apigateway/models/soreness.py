from enum import Enum, IntEnum

from models.body_parts import BodyPart, BodyPartFactory
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
        self.status_changed_date_time = None
        self.daily = True
        self.tissue_overload = 0
        self.inflammation = 0
        self.muscle_spasm = 0
        self.adhesions = 0
        self.altered_neuromuscular_control = 0
        self.muscle_imbalance = 0
        self.functional_inefficiency = 0
        self.tight = None
        self.knots = None
        self.ache = None
        self.sharp = None


    @classmethod
    def json_deserialise(cls, input_dict):
        soreness = cls()
        soreness.body_part = BodyPart(BodyPartLocation(input_dict['body_part']), None)
        soreness.pain = input_dict.get('pain', False)
        soreness.severity = input_dict.get('severity', None)
        soreness.movement = input_dict.get('movement', None)
        soreness.side = input_dict.get('side', None)
        soreness.max_severity = input_dict.get('max_severity', None)
        soreness.first_reported_date_time = input_dict.get('first_reported_date_time', None)
        soreness.last_reported_date_time = input_dict.get('last_reported_date_time', None)
        soreness.cleared_date_time = input_dict.get('cleared_date_time', None)
        soreness.max_severity_date_time = input_dict.get('max_severity_date_time', None)
        soreness.causal_session = input_dict.get('causal_session', None)
        if input_dict.get('status_changed_date_time', None) is not None:
            soreness.status_changed_date_time = parse_datetime(input_dict['status_changed_date_time'])
        if input_dict.get('reported_date_time', None) is not None:
            soreness.reported_date_time = input_dict['reported_date_time']
        soreness.tight = input_dict.get('tight')
        soreness.knots = input_dict.get('knots')
        soreness.ache = input_dict.get('ache')
        soreness.sharp = input_dict.get('sharp')
        soreness.tissue_overload = input_dict.get('tissue_overload', 0)
        soreness.inflammation = input_dict.get('inflammation', 0)
        soreness.muscle_spasm = input_dict.get('muscle_spasm', 0)
        soreness.adhesions = input_dict.get('adhesions', 0)
        soreness.altered_neuromuscular_control = input_dict.get('altered_neuromuscular_control', 0)
        soreness.muscle_imbalance = input_dict.get('muscle_imbalance', 0)
        soreness.functional_inefficiency = input_dict.get('functional_inefficiency', 0)
        cls.get_symptoms_from_severity_movement(soreness)

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
        elif name in ['tight', 'knots'] and value is not None:
            self.movement = self.get_movement_from_tight_knot(value)

        elif name == 'sharp' and value is not None:
            severity_sharp = self.get_pain_from_sharp_ache(value)
            self.pain = True
            if self.severity is None:
                self.severity = severity_sharp
            else:
                self.severity = max([self.severity, severity_sharp])
        elif name == 'ache' and value is not None:
            if BodyPartFactory().is_muscle(self.body_part):
                severity_ache = self.get_soreness_from_ache(value)
            else:
                self.pain = True
                severity_ache = self.get_pain_from_sharp_ache(value)
            if self.severity is None:
                self.severity = severity_ache
            else:
                self.severity = max([self.severity, severity_ache])

        super().__setattr__(name, value)


    def get_symptoms_from_severity_movement(self):
        if self.tight is None and self.knots is None and self.ache is None and self.sharp is None:
            # only update if all are none, i.e. this is old data
            if BodyPartFactory().is_muscle(self.body_part):
                ## update for muscles
                if self.severity is not None:
                    if self.pain:  # if pain, set sharp
                        self.sharp = self.get_sharp_ache_from_pain(self.severity)
                    else:  # else set ache
                        self.ache = self.get_ache_from_soreness(self.severity)
                if self.movement is not None:
                    # set same value for tight and knots if movement is available
                    self.tight = self.get_tight_knots_from_movement(self.movement)
                    self.knots = self.get_tight_knots_from_movement(self.movement)
            else:
                self.pain = True  # joint is always pain
                if self.severity is not None:
                    # set same severity value for ache and sharp
                    self.ache = self.get_sharp_ache_from_pain(self.severity)
                    self.sharp = self.get_sharp_ache_from_pain(self.severity)
                if self.movement is not None:
                    # if movement is available, set tight
                    self.tight = self.get_tight_knots_from_movement(self.movement)

    @staticmethod
    def get_movement_from_tight_knot(value):
        if value == 0:
            return 0
        if value <= 1:
            return 1
        elif value <= 3:
            return 2
        elif value <= 4:
            return 3
        elif value <= 6:
            return 4
        else:
            return 5
        # mapping = {0:0, 1:1, 2:3, 3:2, 4:3, 5:4, 6:4, 7:5, 8:5, 9:5, 10:5}
        # return mapping[value]

    @staticmethod
    def get_tight_knots_from_movement(value):
        if value == 0:
            return 0
        elif value <= 1:
            return 1
        elif value <= 2:
            return 2
        elif value <= 3:
            return 4
        elif value <= 4:
            return 5
        else:
            return 7
        # mapping = {0:0, 1:1, 2:2, 3:4, 4:5, 5:7}
        # return mapping[value]

    @staticmethod
    def get_pain_from_sharp_ache(value):
        if value == 0:
            return 0
        elif value <= 2:
            return 1
        elif value <= 3:
            return 2
        elif value <= 4:
            return 3
        elif value <= 5:
            return 4
        else:
            return 5
        # mapping = {0:0, 1:1, 2:1, 3:2, 4:3, 5:4, 6:5, 7:5, 8:5, 9:5, 10:5}
        # return mapping[value]

    @staticmethod
    def get_sharp_ache_from_pain(value):
        if value == 0:
            return 0
        elif value <= 1:
            return 1
        elif value <= 2:
            return 3
        elif value <= 3:
            return 4
        elif value <= 4:
            return 5
        else:
            return 6
        # mapping = {0:0, 1:1, 2:3, 3:4, 4:5, 5:6}
        # return mapping[value]

    @staticmethod
    def get_soreness_from_ache(value):
        if value == 0:
            return 0
        elif value <= 3:
            return 1
        elif value <= 4:
            return 2
        elif value <= 5:
            return 3
        elif value <= 6:
            return 4
        else:
            return 5
        # mapping = {0:0, 1:1, 2:1, 3:1, 4:2, 5:3, 6:4, 7:5, 8:5, 9:5, 10:5}
        # return mapping[value]

    @staticmethod
    def get_ache_from_soreness(value):
        if value == 0:
            return 0
        elif value <= 1:
            return 1
        elif value <= 2:
            return 4
        elif value <= 3:
            return 5
        elif value <= 4:
            return 6
        else:
            return 7
        # mapping = {0:0, 1:1, 2:4, 3:5, 4:6, 5:7}
        # return mapping[value]



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
                self.body_part.location == BodyPartLocation.hip or
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
                self.body_part.location == BodyPartLocation.it_band or
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
                   'status': self.historic_soreness_status.name if self.historic_soreness_status is not None else HistoricSorenessStatus.dormant_cleared.name,
                   'status_changed_date_time': format_datetime(self.status_changed_date_time) if self.status_changed_date_time is not None else None
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
                   'side': self.side,
                   'tight': self.tight,
                   'knots': self.knots,
                   'ache': self.ache,
                   'sharp': self.sharp,
                   'tissue_overload': self.tissue_overload,
                   'inflammation': self.inflammation,
                   'muscle_spasm': self.muscle_spasm,
                   'adhesions': self.adhesions,
                   'altered_neuromuscular_control': self.altered_neuromuscular_control,
                   'muscle_imbalance': self.muscle_imbalance,
                   'functional_inefficiency': self.functional_inefficiency
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
