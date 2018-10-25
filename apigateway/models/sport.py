from enum import Enum, IntEnum


class SportLevel(IntEnum):
    recreational = 0
    high_school = 1
    club_travel = 2
    developmental_league = 3
    ncaa_division_iii = 4
    ncaa_division_ii = 5
    ncaa_division_i = 6
    professional = 7


class Sport(object):

    def __init__(self):
        self.name = None
        self.level = SportLevel.recreational
        self.season_start_date = None
        self.season_end_date = None
        # self.typical_schedule = session.Schedule()


class SportName(Enum):
    basketball = 0
    baseball = 1
    softball = 2
    cycling = 3
    field_hockey = 4
    football = 5
    general_fitness = 6
    golf = 7
    gymnastics = 8
    skate_sports = 9
    lacrosse = 10
    rowing = 11
    rugby = 12
    diving = 13
    soccer = 14
    pool_sports = 15
    tennis = 16
    distance_running = 17
    sprints = 18
    jumps = 19
    throws = 20
    volleyball = 21
    wrestling = 22
    weightlifting = 23
    track_field =24
    no_sport = None


class NoSportPosition(Enum):
    power = 1
    strength = 3
    endurance = 0
    speed_agility = 2
    cross_training = 4


class BaseballPosition(Enum):
    catcher = 0
    infielder = 1
    pitcher = 2
    outfielder = 3


class BasketballPosition(Enum):
    center = 0
    forward = 1
    guard = 2


class FootballPosition(Enum):
    defensive_back = 0
    kicker = 1
    linebacker = 2
    lineman = 3
    quarterback = 4
    receiver = 5
    running_back = 6


class LacrossePosition(Enum):
    attacker = 0
    defender = 1
    goalie = 2
    midfielder = 3


class SoccerPosition(Enum):
    defender = 0
    forward = 1
    goalkeeper = 2
    midfielder = 3
    striker = 4

class SoftballPosition(Enum):
    catcher = 0
    infielder = 1
    pitcher = 2
    outfielder = 3

class FieldHockeyPosition(Enum):
    goalie = 0
    fullback = 1
    midfielder = 2
    forward = 3

class TrackAndFieldPosition(Enum):
    sprinter = 0
    jumper = 1
    thrower = 2
    distance = 3

