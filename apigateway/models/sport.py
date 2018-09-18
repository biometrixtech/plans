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
    baseball_softball = 1
    cross_country = 2
    cycling = 3
    field_hockey = 4
    general_fitness = 5
    golf = 6
    gymnastics = 7
    ice_hockey = 8
    lacrosse = 9
    rowing = 10
    rugby = 11
    running = 12
    soccer = 13
    swimming_diving = 14
    tennis = 15
    track_and_field = 16
    volleyball = 17
    wrestling = 18
    weightlifting = 19
    football = 20
    no_sport = None


class BaseballPosition(Enum):
    Catcher = 0
    Infielder = 1
    Pitcher = 2
    Outfielder = 3


class BasketballPosition(Enum):
    Center = 0
    Forward = 1
    Guard = 2


class FootballPosition(Enum):
    DefensiveBack = 0
    Kicker = 1
    Linebacker = 2
    Lineman = 3
    Quarterback = 4
    Receiver = 5
    RunningBack = 6


class LacrossePosition(Enum):
    Attacker = 0
    Defender = 1
    Goalie = 2
    Midfielder = 3


class SoccerPosition(Enum):
    Defender = 0
    Forward = 1
    Goalkeeper = 2
    Midfielder = 3
    Striker = 4




