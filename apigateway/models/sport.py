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
    football = 5
    general_fitness = 6
    golf = 7
    gymnastics = 8
    ice_hockey = 9
    lacrosse = 10
    rowing = 11
    rugby = 12
    running = 13
    soccer = 14
    swimming_diving = 15
    tennis = 16
    distance_running = 17
    sprints = 18
    jumps = 19
    throws = 20
    volleyball = 21
    wrestling = 22
    weightlifting = 23
    no_sport = None


class NoSportPosition(Enum):
    Power = 1
    Strength = 3
    Endurance = 0
    Speed = 2
    CrossTraining = 4


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




