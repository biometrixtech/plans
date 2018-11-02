from enum import Enum, IntEnum
from serialisable import Serialisable


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


class Soreness(Serialisable):
    def __init__(self):
        self.body_part = None
        self.pain = False
        self.severity = None  # muscle_soreness_severity or joint_soreness_severity
        self.side = None
        self.type = None  # soreness_type
        self.reported_date_time = None

    def json_serialise(self):
        ret = {
            'body_part': self.body_part.location.value,
            'pain': self.pain,
            'severity': self.severity,
            'side': self.side
        }
        return ret


class InjuryStatus(Enum):
    healthy = 0
    healthy_chronically_injured = 1
    returning_from_injury = 2
    returning_from_chronic_injury = 3


class BodyPartLocation(Enum):
    head = 0
    shoulder = 1
    chest = 2
    abdominals = 3
    hip_flexor = 4
    groin = 5
    quads = 6
    knee = 7
    shin = 8
    ankle = 9
    foot = 10
    outer_thigh = 11
    lower_back = 12
    general = 13
    glutes = 14
    hamstrings = 15
    calves = 16
    achilles = 17
    upper_back_neck = 18


class BodyPart(object):

    def __init__(self, body_part_location, treatment_priority):
        self.location = body_part_location
        self.treatment_priority = treatment_priority
        self.inhibit_exercises = []
        self.lengthen_exercises = []
        self.activate_exercises = []
        self.integrate_exercises = []


class HistoricSorenessStatus(IntEnum):
    dormant_cleared = 0
    persistent = 1
    chronic = 2


class HistoricSoreness(Serialisable):

    def __init__(self, body_part_location, historic_soreness_status, is_pain):
        self.body_part_location = body_part_location
        self.historic_soreness_status = historic_soreness_status
        self.is_pain = is_pain
        self.persistent_soreness_count = 0
        self.chronic_soreness_count = 0
        self.persistent_pain_count = 0
        self.chronic_pain_count = 0

    def json_serialise(self):
        ret = {
            'body_part_location': self.body_part_location.value,
            'historic_soreness_status': self.historic_soreness_status,
            'is_pain': self.is_pain,
            'persistent_soreness_count': self.persistent_soreness_count,
            'chronic_soreness_count': self.chronic_soreness_count,
            'persistent_pain_count': self.persistent_pain_count,
            'chronic_pain_count': self.chronic_pain_count,
        }
        return ret





