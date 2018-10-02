import abc
from enum import Enum
import models.exercise
import models.soreness


class Athlete(metaclass=abc.ABCMeta):
    def __init__(self):
        self.goals = AthleteGoals.improved_performance
        self.full_name = ""
        self.email = ""
        self.date_of_birth = None
        self.injury_status = models.soreness.InjuryStatus.healthy
        self.height = 0
        self.weight = 0
        self.sports = []
        self.injury_history = []  # collection of Injury objects
        self.assigned_exercises = []

    @abc.abstractmethod
    def max_exercise_technical_difficulty(self):
        return models.exercise.TechnicalDifficulty.beginner


class AgeGroup(Enum):
    unclassified = 0
    youth = 1
    college = 2
    adult = 3


class AthleteGoals(Enum):
    improved_performance = 0
    improved_robustness = 1
    return_from_injury = 2


class YouthAthlete(Athlete):
    def __init(self, level=None):
        Athlete.__init__(self, level)

    def max_exercise_technical_difficulty(self):
        return models.exercise.TechnicalDifficulty.beginner


class CollegeAthlete(Athlete):
    def __init(self, level=None):
        Athlete.__init__(self, level)
    
    def max_exercise_technical_difficulty(self):
        return models.exercise.TechnicalDifficulty.beginner


class AdultAthlete(Athlete):
    def __init(self, level=None):
        Athlete.__init__(self, level)

    def max_exercise_technical_difficulty(self):
        return models.exercise.TechnicalDifficulty.beginner

