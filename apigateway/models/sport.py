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
    track_field = 24
    archery = 25
    australian_football = 26
    badminton = 27
    bowling = 28
    boxing = 29
    cricket = 30
    curling = 31
    dance = 32
    equestrian_sports = 33
    fencing = 34
    fishing = 35
    handball = 36
    hockey = 37
    martial_arts = 38
    paddle_sports = 39
    racquetball = 40
    sailing = 41
    snow_sports = 42
    squash = 43
    surfing_sports = 44
    swimming = 45
    table_tennis = 46
    water_polo = 47
    cross_country_skiing = 48
    downhill_skiing = 49
    kick_boxing = 50
    snowboarding = 51
    endurance = 52
    power = 53
    speed_agility = 54
    strength = 55
    cross_training = 56
    elliptical = 57
    functional_strength_training = 58
    hiking = 59
    hunting = 60
    mind_and_body = 61
    play = 62
    preparation_and_recovery = 63
    stair_climbing = 64
    traditional_strength_training = 65
    walking = 66
    water_fitness = 67
    yoga = 68
    barre = 69
    core_training = 70
    flexibility = 71
    high_intensity_interval_training = 72
    jump_rope = 73
    pilates = 74
    stairs = 75
    step_training = 76
    wheelchair_walk_pace = 77
    wheelchair_run_pace = 78
    taichi = 79
    mixed_cardio = 80
    hand_cycling = 81
    climbing = 82
    other = 83
    no_sport = None

    @classmethod
    def has_value(cls, value):
        return any(value == item.value for item in cls)


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


class VolleyballPosition(Enum):
    hitter = 0
    setter = 1
    middle_blocker = 2
    libero = 3
