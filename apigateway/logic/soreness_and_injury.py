from enum import Enum, IntEnum, auto


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


class InjuryDescriptor(Enum):
    contusion = 0
    sprain = 1
    strain = 2
    dislocation = 3
    fracture = 4
    pain = 5
    other = 6


class PreSessionSoreness(object):

    def __init__(self):
        self.type = None    # soreness_type
        self.severity = None    # muscle_soreness_severity or joint_soreness_severity
        self.body_part = None
        # self.descriptor = None  # soreness_descriptor


class PostSessionSoreness(object):

    def __init__(self):
        self.body_part = None
        self.discomfort_level = 0
        self.sustained_in_practice = False
        self.type = None    # soreness_type
        self.limited_performance = 0
        self.limited_how_much_i_could_do = 0


class InjuryStatus(Enum):
    healthy = 0
    healthy_chronically_injured = 1
    returning_from_injury = 2


class BodyPart(Enum):
    head = auto()
    shoulder = auto()
    chest = auto()
    abdominals = auto()
    hip_flexor = auto()
    groin = auto()
    quads = auto()
    knee = auto()
    shin = auto()
    ankle = auto()
    foot = auto()
    neck = auto()
    upper_back = auto()
    lower_back = auto()
    glutes = auto()
    hamstrings = auto()
    calves = auto()
    achilles = auto()


class InjuryType(Enum):
    muscle = auto()
    ligament = auto()
    tendon = auto()
    bone = auto()


class DaysMissedDueToInjury(IntEnum):
    less_than_7_days = 0
    one_four_weeks = 1
    one_three_months = 2


class Injury(object):

    def __init__(self):
        self.body_part = None
        self.injury_type = None
        self.date = None
        self.days_missed = DaysMissedDueToInjury.less_than_7_days
