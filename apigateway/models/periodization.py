from enum import Enum
from models.training_volume import StandardErrorRange


class AthleteTrainingHistory(object):
    def __init__(self):
        self.longest_session_duration = None
        self.average_session_duration = None
        self.shortest_session_duration = None
        self.highest_session_rpe = None
        self.average_session_rpe = None
        self.highest_load_session = None
        self.highest_load_day = None
        self.average_load_session = None
        self.average_load_day = None

        self.min_number_sessions_per_week = None
        self.average_number_sessions_per_week = None
        self.max_number_sessions_per_week = None

        self.lowest_session_rpe = None
        self.lowest_load_session = None


class PeriodizationPlanWeek(object):
    def __init__(self):
        self.total_weeks_load = 0
        self.start_date = None
        self.end_date = None
        self.target_longest_session_duration = None
        self.target_week_average_session_duration = None
        self.target_shortest_session_duration = None
        self.target_highest_session_rpe = None
        self.target_average_session_rpe = None
        self.target_highest_load_session = None
        self.target_highest_load_day = None
        self.target_average_load_session = None
        self.target_average_load_day = None
        self.target_average_number_sessions_per_microcycle = None

        self.target_lowest_session_rpe = None
        self.target_lowest_load_session = None


class TrainingPhaseType(Enum):
    recovery = 0
    taper = 1
    maintain = 2
    slowly_increase = 3
    increase = 4
    aggressively_increase = 5


class PeriodizationPersona(Enum):
    high_injury_risk = 0
    sedentary = 1
    recreational_gaining = 2
    recreational_maintaining = 3
    well_trained = 4
    elite_athlete_gaining = 5
    elite_athlete_maintaining = 6


class TrainingPhase(object):
    def __init__(self, training_phase_type, lower_progression_bound, upper_progression_bound):
        self.training_phase_type = training_phase_type  # indicates max rate of progressions
        self.acwr = StandardErrorRange(lower_bound=lower_progression_bound, upper_bound=upper_progression_bound)


# should proceed from high volume-low intensity to low volume-high intensity training over the course of the mesocycle
class PeriodizationPlan(object):
    def __init__(self):
        self.training_phase = None
        self.weeks = []


