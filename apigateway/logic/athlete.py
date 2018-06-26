import abc
from enum import Enum, IntEnum
import soreness_and_injury
import exercise


class Athlete(metaclass=abc.ABCMeta):
    def __init__(self):
        self.level = AthleteLevel.recreational
        self.goals = AthleteGoals.improved_performance
        self.full_name = ""
        self.email = ""
        self.date_of_birth = None
        self.injury_status = soreness_and_injury.InjuryStatus.healthy
        self.height = 0
        self.weight = 0
        self.sports = []
        self.injuries = []  # collection of Injury objects

    @abc.abstractmethod
    def max_exercise_technical_difficulty(self):
        return exercise.TechnicalDifficulty.beginner


class AgeGroup(Enum):
    Unclassified = 0
    Youth = 1
    College = 2
    Adult = 3


class AthleteLevel(IntEnum):
    recreational = 0
    high_school = 1
    club_travel = 2
    developmental_league = 3
    ncaa_division_iii = 4
    ncaa_division_ii = 5
    ncaa_division_i = 6
    professional = 7


class AthleteGoals(Enum):
    improved_performance = 0
    improved_robustness = 1
    return_from_injury = 2


class Sport(Enum):
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


class YouthAthlete(athlete):
    def __init(self, level=None):
        athlete.__init__(self, level)

    def max_exercise_technical_difficulty(self):
        return exercise.TechnicalDifficulty.beginner


class CollegeAthlete(athlete):
    def __init(self, level=None):
        athlete.__init__(self, level)
    
    def max_exercise_technical_difficulty(self):
        return exercise.TechnicalDifficulty.beginner


class AdultAthlete(athlete):
    def __init(self, level=None):
        athlete.__init__(self, level)

    def max_exercise_technical_difficulty(self):
        return exercise.TechnicalDifficulty.beginner

