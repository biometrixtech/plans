import abc
from enum import Enum


class SessionType(Enum):
    practice = 0
    strength_and_conditioning = 1
    game = 2
    tournament = 3
    bump_up = 4
    corrective = 5
    long_term_recovery = 6


class Session(metaclass=abc.ABCMeta):
    def __init__(self):
        self.duration_minutes = None
        self.external_load = None
        self.high_intensity_load = None
        self.mod_intensity_load = None
        self.low_intensity_load = None
        self.high_intensity_minutes = None
        self.mod_intensity_minutes = None
        self.low_intensity_minutes = None
        self.high_intensity_RPE = None
        self.mod_intensity_RPE = None
        self.low_intensity_RPE = None
        self.readiness = None
        self.pre_session_soreness = []  # pre_session_soreness object array
        self.post_session_soreness = []     # post_session_soreness object array
        self.sleep_quality = None
        self.date = None
        self.time = None
        self.estimated = False
        self.internal_load_imputed = False
        self.external_load_imputed = False

        # post-session
        self.session_RPE = None
        self.performance_level = 100  # only answered if there is discomfort
        self.completion_percentage = 100    # only answered if there is discomfort
        self.sustained_injury_or_pain = False

    @abc.abstractmethod
    def session_type(self):
        return SessionType.practice

    def internal_load(self):
        if self.session_RPE is not None and self.duration_minutes is not None:
            return self.session_RPE * self.duration_minutes
        else:
            return None


class BumpUpSession(Session):
    def __init__(self):
        Session.__init__(self)
        self.exercises = []

    def session_type(self):
        return SessionType.bump_up


class PracticeSession(Session):
    def __init__(self):
        Session.__init__(self)

    def session_type(self):
        return SessionType.practice


class StrengthConditioningSession(Session):
    def __init__(self):
        Session.__init__(self)

    def session_type(self):
        return SessionType.strength_and_conditioning


class Game(Session):
    def __init__(self):
        Session.__init__(self)

    def session_type(self):
        return SessionType.game


class Tournament(Session):
    def __init__(self):
        Session.__init__(self)
        self.games = []

    def session_type(self):
        return SessionType.tournament


class CorrectiveSession(Session):
    def __init__(self):
        Session.__init__(self)
        self.exercises = []

    def session_type(self):
        return SessionType.corrective


class GlobalLoadEstimationParameters(object):

    def __init__(self):
        self.high_intensity_percentage = 0
        self.moderate_intensity_percentage = 0
        self.low_intensity_percentage = 0
        self.total_avg_external_load_per_minute = 0
        self.high_intensity_avg_load_per_minute = 0
        self.moderate_intensity_avg_load_per_minute = 0
        self.low_intensity_avg_load_per_minute = 0


class SessionLoadEstimationParameter(GlobalLoadEstimationParameters):

    def __init__(self):
        GlobalLoadEstimationParameters.__init__()
        self.session_type = SessionType.practice


