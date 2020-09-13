from datetime import timedelta
from enum import Enum
from models.athlete_capacity import AthleteBaselineCapacities
from models.training_volume import StandardErrorRange


class PeriodizationPlan(object):
    def __init__(self, start_date, athlete_periodization_goals, training_phase_type, athlete_persona):
        self.start_date = start_date
        self.periodization_goals = athlete_periodization_goals
        self.training_phase_type = training_phase_type
        self.athlete_persona = athlete_persona
        self.target_training_exposures = []
        self.target_weekly_rpe_load = None
        self.expected_weekly_workouts = None
        self.athlete_capacities = AthleteBaselineCapacities()

    def get_week_number(self, event_date):

        monday1 = (self.start_date - timedelta(days=self.start_date.weekday()))
        monday2 = (event_date - timedelta(days=event_date.weekday()))

        return int(round((monday2 - monday1).days / 7, 0))

    def get_week_start_date(self, event_date):

        week_number = self.get_week_number(event_date)

        return self.start_date + timedelta(weeks=week_number)




class PeriodizationProgressionFactory(object):

    def create(self, persona, training_phase_type):

        if persona == PeriodizationPersona.well_trained:

            training_phase = TrainingPhaseFactory().create(training_phase_type)

            periodization_progression_1 = PeriodizationProgression(week_number=0, training_phase=training_phase,
                                                                   rpe_load_contribution=0.20, volume_load_contribution=0.80)
            periodization_progression_2 = PeriodizationProgression(week_number=1, training_phase=training_phase,
                                                                   rpe_load_contribution=0.40, volume_load_contribution=0.60)
            periodization_progression_3 = PeriodizationProgression(week_number=2, training_phase=training_phase,
                                                                   rpe_load_contribution=0.60, volume_load_contribution=0.40)
            periodization_progression_4 = PeriodizationProgression(week_number=3, training_phase=training_phase,
                                                                   rpe_load_contribution=0.80, volume_load_contribution=0.20)

            progressions = [periodization_progression_1, periodization_progression_2, periodization_progression_3,
                            periodization_progression_4]

            return progressions


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


class TrainingPhaseFactory(object):

    def create(self, training_phase_type):

        if training_phase_type == TrainingPhaseType.recovery:
            return TrainingPhase(training_phase_type=training_phase_type, lower_progression_bound=None,
                                 upper_progression_bound=None)
        elif training_phase_type == TrainingPhaseType.taper:
            return TrainingPhase(training_phase_type=training_phase_type, lower_progression_bound=.8,
                                 upper_progression_bound=1.1)
        elif training_phase_type == TrainingPhaseType.maintain:
            return TrainingPhase(training_phase_type=training_phase_type, lower_progression_bound=.9,
                                 upper_progression_bound=1.1)
        elif training_phase_type == TrainingPhaseType.slowly_increase:
            return TrainingPhase(training_phase_type=training_phase_type, lower_progression_bound=1.2,
                                 upper_progression_bound=1.3)
        elif training_phase_type == TrainingPhaseType.increase:
            return TrainingPhase(training_phase_type=training_phase_type,lower_progression_bound=1.3,
                                 upper_progression_bound=1.5)
        elif training_phase_type == TrainingPhaseType.aggressively_increase:
            return TrainingPhase(training_phase_type=training_phase_type,lower_progression_bound=1.5,
                                 upper_progression_bound=2.0)
        else:
            return TrainingPhase(training_phase_type=TrainingPhaseType.recovery, lower_progression_bound=None,
                                 upper_progression_bound=None)


class PeriodizationProgression(object):
    def __init__(self, week_number, training_phase, rpe_load_contribution, volume_load_contribution):
        self.week_number = week_number
        self.training_phase = training_phase
        self.rpe_load_contribution = rpe_load_contribution
        self.volume_load_contribution = volume_load_contribution


class TrainingPhase(object):
    def __init__(self, training_phase_type, lower_progression_bound, upper_progression_bound):
        self.training_phase_type = training_phase_type  # indicates max rate of progressions
        self.acwr = StandardErrorRange(lower_bound=lower_progression_bound, upper_bound=upper_progression_bound)