from enum import Enum
from models.training_volume import StandardErrorRange
from models.training_load import DetailedTrainingLoad, TrainingLoad


class AthleteTrainingHistory(object):
    def __init__(self):
        self.average_session_duration = StandardErrorRange()
        self.average_session_rpe = StandardErrorRange()
        self.average_sessions_per_week = StandardErrorRange()

        self.average_session_load = TrainingLoad()
        self.average_day_load = TrainingLoad()

        self.current_weeks_load = TrainingLoad()
        self.previous_1_weeks_load = TrainingLoad()
        self.previous_2_weeks_load = TrainingLoad()
        self.previous_3_weeks_load = TrainingLoad()
        self.previous_4_weeks_load = TrainingLoad()

        self.current_weeks_average_session_duration = StandardErrorRange()
        self.current_weeks_average_session_rpe = StandardErrorRange()

        self.current_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_1_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_2_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_3_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_4_weeks_detailed_load = DetailedTrainingLoad()

    def get_last_four_weeks_power_load(self):

        power_load_list = []

        if self.current_weeks_load.power_load is not None:
            power_load_list.append(self.current_weeks_load.power_load)

        if self.previous_1_weeks_load.power_load is not None:
            power_load_list.append(self.previous_1_weeks_load.power_load)

        if self.previous_2_weeks_load.power_load is not None:
            power_load_list.append(self.previous_2_weeks_load.power_load)

        if self.previous_3_weeks_load.power_load is not None:
            power_load_list.append(self.previous_3_weeks_load.power_load)

        return power_load_list

    def get_last_four_weeks_rpe_load(self):

        load_list = []

        if self.current_weeks_load.rpe_load is not None:
            load_list.append(self.current_weeks_load.rpe_load)

        if self.previous_1_weeks_load.rpe_load is not None:
            load_list.append(self.previous_1_weeks_load.rpe_load)

        if self.previous_2_weeks_load.rpe_load is not None:
            load_list.append(self.previous_2_weeks_load.rpe_load)

        if self.previous_3_weeks_load.rpe_load is not None:
            load_list.append(self.previous_3_weeks_load.rpe_load)

        return load_list


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


class PeriodizationGoal(Enum):
    improve_cardiovascular_health = 10


class TrainingPhase(object):
    def __init__(self, training_phase_type, lower_progression_bound, upper_progression_bound):
        self.training_phase_type = training_phase_type  # indicates max rate of progressions
        self.acwr = StandardErrorRange(lower_bound=lower_progression_bound, upper_bound=upper_progression_bound)


# should proceed from high volume-low intensity to low volume-high intensity training over the course of the mesocycle
class PeriodizationPlan(object):
    def __init__(self, athlete_periodization_goal):
        self.periodization_goal = athlete_periodization_goal
        self.training_phase = None
        self.weeks = []


class PeriodizationPlanWeek(object):
    def __init__(self):
        self.target_weekly_load = StandardErrorRange()
        self.start_date = None
        self.end_date = None
        self.target_session_duration = StandardErrorRange()
        self.target_session_rpe = StandardErrorRange()
        self.target_session_load = StandardErrorRange()
        self.target_day_load = StandardErrorRange()
        self.target_sessions_per_week = StandardErrorRange()


class PeriodizationModel(object):
    def __init__(self):
        self.progression_persona = None
        self.progressions = []


class PeriodizationProgression(object):
    def __init__(self, week_number, training_phase, rpe_load_contribution, volume_load_contribution):
        self.week_number = week_number
        self.training_phase = training_phase
        self.rpe_load_contribution = rpe_load_contribution
        self.volume_load_contribution = volume_load_contribution


class PeriodizationModelFactory(object):

    def create(self, persona, training_phase_type):

        if persona == PeriodizationPersona.well_trained:

            periodization_model = PeriodizationModel()
            periodization_model.progression_persona = PeriodizationPersona.well_trained

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

            periodization_model.progressions = progressions

            return periodization_model


class TrainingPhaseFactory(object):

    def create(self, training_phase_type):

        if training_phase_type == TrainingPhaseType.recovery:
            return TrainingPhase(training_phase_type=training_phase_type, lower_progression_bound=None,
                                 upper_progression_bound=None)
        elif training_phase_type == TrainingPhaseType.taper:
            return TrainingPhase(training_phase_type=training_phase_type, lower_progression_bound=.8,
                                 upper_progression_bound=.1)
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
