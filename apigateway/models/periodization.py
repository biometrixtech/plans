from enum import Enum

from models.periodization_goal import PeriodizationGoalType
from models.training_volume import StandardErrorRange
from models.training_load import TrainingLoad
from models.movement_tags import DetailedAdaptationType, SubAdaptationType, AdaptationDictionary
from datetime import timedelta


# class AthleteTrainingHistory(object):
#     def __init__(self):
#         self.average_session_duration = StandardErrorRange()
#         self.average_session_rpe = StandardErrorRange()
#         self.average_sessions_per_week = StandardErrorRange()
#
#         self.average_session_load = TrainingLoad()
#         self.average_day_load = TrainingLoad()
#
#         self.last_weeks_load = TrainingLoad()
#         self.previous_1_weeks_load = TrainingLoad()
#         self.previous_2_weeks_load = TrainingLoad()
#         self.previous_3_weeks_load = TrainingLoad()
#         self.previous_4_weeks_load = TrainingLoad()
#
#         # self.last_weeks_average_session_duration = StandardErrorRange()
#         # self.current_weeks_average_session_rpe = StandardErrorRange()
#
#         self.last_weeks_detailed_load = DetailedTrainingLoad()
#         self.previous_1_weeks_detailed_load = DetailedTrainingLoad()
#         self.previous_2_weeks_detailed_load = DetailedTrainingLoad()
#         self.previous_3_weeks_detailed_load = DetailedTrainingLoad()
#         self.previous_4_weeks_detailed_load = DetailedTrainingLoad()
#
#     def get_last_four_weeks_power_load(self):
#
#         power_load_list = []
#
#         if self.last_weeks_load.power_load is not None:
#             power_load_list.append(self.last_weeks_load.power_load)
#
#         if self.previous_1_weeks_load.power_load is not None:
#             power_load_list.append(self.previous_1_weeks_load.power_load)
#
#         if self.previous_2_weeks_load.power_load is not None:
#             power_load_list.append(self.previous_2_weeks_load.power_load)
#
#         if self.previous_3_weeks_load.power_load is not None:
#             power_load_list.append(self.previous_3_weeks_load.power_load)
#
#         return power_load_list
#
#     def get_last_four_weeks_rpe_load(self):
#
#         load_list = []
#
#         if self.last_weeks_load.rpe_load is not None:
#             load_list.append(self.last_weeks_load.rpe_load)
#
#         if self.previous_1_weeks_load.rpe_load is not None:
#             load_list.append(self.previous_1_weeks_load.rpe_load)
#
#         if self.previous_2_weeks_load.rpe_load is not None:
#             load_list.append(self.previous_2_weeks_load.rpe_load)
#
#         if self.previous_3_weeks_load.rpe_load is not None:
#             load_list.append(self.previous_3_weeks_load.rpe_load)
#
#         return load_list


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


class PeriodizedExercise(object):
    def __init__(self, detailed_adaptation_type, sub_adaptation_type, times_per_week_range, duration_range, rpe_range,
                 priority=0):
        self.detailed_adaptation_type = detailed_adaptation_type
        self.sub_adaptation_type = sub_adaptation_type
        self.times_per_week = times_per_week_range
        self.found_times = 0
        self.duration = duration_range
        self.rpe = rpe_range
        self.priority = priority
        self.periodization_id = None
        #self.update_adaptation_types()

    def update_adaptation_types(self):

        adaptation_dictionary = AdaptationDictionary()
        if self.uses_detailed_adapatation_type():
            self.sub_adaptation_type = adaptation_dictionary.detailed_types[self.detailed_adaptation_type]

    def uses_detailed_adapatation_type(self):

        if self.detailed_adaptation_type is not None:
            return True
        else:
            return False

    def uses_sub_adaptation_type(self):

        if self.sub_adaptation_type is not None:
            return True
        else:
            return False


class TrainingPhase(object):
    def __init__(self, training_phase_type, lower_progression_bound, upper_progression_bound):
        self.training_phase_type = training_phase_type  # indicates max rate of progressions
        self.acwr = StandardErrorRange(lower_bound=lower_progression_bound, upper_bound=upper_progression_bound)


class TemplateWorkout(object):
    def __init__(self):
        self.acceptable_session_rpe = None
        self.acceptable_session_watts = None
        self.acceptable_session_duration = None
        self.acceptable_session_watts_duration = None
        self.acceptable_session_rpe_load = None
        self.acceptable_session_power_load = None
        self.muscle_load_ranking = {}
        self.adaptation_type_ranking = []


class PeriodizationPlan(object):
    def __init__(self, start_date, athlete_periodization_goals, training_phase, athlete_persona):
        self.start_date = start_date
        self.periodization_goals = athlete_periodization_goals
        self.training_phase = training_phase
        self.athlete_persona = athlete_persona
        self.template_workout = None
        self.next_workouts = {}

    def get_week_number(self, event_date):

        monday1 = (self.start_date - timedelta(days=self.start_date.weekday()))
        monday2 = (event_date - timedelta(days=event_date.weekday()))

        return int(round((monday2 - monday1).days / 7, 0))

    def get_week_start_date(self, event_date):

        week_number = self.get_week_number(event_date)

        return self.start_date + timedelta(weeks=week_number)


class PeriodizationPlanWeek(object):
    def __init__(self):
        self.target_weekly_load = TrainingLoad()
        self.start_date = None
        self.end_date = None
        self.target_session_duration = StandardErrorRange()
        self.target_session_watts_duration = StandardErrorRange()
        self.target_session_rpe = StandardErrorRange()
        self.target_session_watts = StandardErrorRange()
        self.target_session_load = TrainingLoad()
        self.target_day_load = StandardErrorRange()
        self.target_sessions_per_week = StandardErrorRange()


class PeriodizationOneRequiredCombination(object):
    def __init__(self):
        self.periodization_id = None
        self.combination_range = StandardErrorRange()


class PeriodizationModel(object):
    def __init__(self):
        self.progression_persona = None
        self.progressions = []
        self.required_exercises = []
        self.one_required_exercises = []
        self.one_required_combinations = []

#     def get_available_workouts(self, workout_library, completed_workouts):
#         pass
#
#
# class ImproveCardiovascularPeriodizationModel(PeriodizationModel):
#     def __init__(self):
#         super().__init__()
#
#     def get_available_workouts(self, workout_library, completed_workouts):
#         pass
#


class PeriodizationProgression(object):
    def __init__(self, week_number, training_phase, rpe_load_contribution, volume_load_contribution):
        self.week_number = week_number
        self.training_phase = training_phase
        self.rpe_load_contribution = rpe_load_contribution
        self.volume_load_contribution = volume_load_contribution


class RequiredExerciseFactory(object):

    def get_required_exercises(self, periodization_goal):

        if periodization_goal == PeriodizationGoalType.increase_cardiovascular_health or periodization_goal == PeriodizationGoalType.lose_weight:

            return [PeriodizedExercise(None, SubAdaptationType.strength,
                                       times_per_week_range=StandardErrorRange(lower_bound=2), duration_range=None,
                                       rpe_range=None, priority=1)]
        elif periodization_goal == PeriodizationGoalType.increase_cardio_endurance:

            base_training_volume = None # TBD

            correctives = PeriodizedExercise(DetailedAdaptationType.corrective, None,
                                             times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                             duration_range=None, rpe_range=None, priority=1)

            anaerobic_threshold = PeriodizedExercise(DetailedAdaptationType.anaerobic_threshold_training, None,
                                                    times_per_week_range=StandardErrorRange(lower_bound=1,
                                                                                            upper_bound=2),
                                                    duration_range=None, rpe_range=None, priority=3)

            exercises = [correctives, anaerobic_threshold]

            return exercises

        elif periodization_goal == PeriodizationGoalType.increase_cardio_endurance_with_speed:

            correctives = PeriodizedExercise(DetailedAdaptationType.corrective, None,
                                             times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                             duration_range=None, rpe_range=None, priority=2)

            base_training = PeriodizedExercise(DetailedAdaptationType.base_aerobic_training, None,
                                                    times_per_week_range=StandardErrorRange(lower_bound=1,
                                                                                            upper_bound=2),
                                                    duration_range=None, rpe_range=None, priority=4)

            exercises = [correctives, base_training]

            return exercises

        elif periodization_goal == PeriodizationGoalType.increase_strength_max_strength:

            movement_efficiency = PeriodizedExercise(None, SubAdaptationType.movement_efficiency,
                                             times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                             duration_range=None, rpe_range=None, priority=2)

            base_training = PeriodizedExercise(DetailedAdaptationType.base_aerobic_training, None,
                                                    times_per_week_range=StandardErrorRange(lower_bound=1,
                                                                                            upper_bound=2),
                                                    duration_range=None, rpe_range=None, priority=3)

            exercises = [movement_efficiency, base_training]

            return exercises

    def get_one_required_exercises(self, periodization_goal):

        if periodization_goal == PeriodizationGoalType.increase_cardiovascular_health:

            mod_intensity = PeriodizedExercise(None, SubAdaptationType.cardiorespiratory_training,
                                               times_per_week_range=StandardErrorRange(lower_bound=5),
                                               duration_range=StandardErrorRange(lower_bound=30*60, upper_bound=60*60),
                                               rpe_range=StandardErrorRange(lower_bound=3, upper_bound=5), priority=1)

            mod_intensity.periodization_id = 1

            vigorous_intensity = PeriodizedExercise(None, SubAdaptationType.cardiorespiratory_training,
                                                    times_per_week_range=StandardErrorRange(lower_bound=3),
                                                    duration_range=StandardErrorRange(lower_bound=20 * 60,
                                                                                      upper_bound=60 * 60),
                                                    rpe_range=StandardErrorRange(lower_bound=6, upper_bound=10),
                                                    priority=1)

            vigorous_intensity.periodization_id = 1

            exercises = [mod_intensity, vigorous_intensity]

            return exercises

        elif periodization_goal == PeriodizationGoalType.increase_cardio_endurance:

            stabilization_strength = PeriodizedExercise(DetailedAdaptationType.stabilization_strength, None,
                                             times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                             duration_range=None, rpe_range=None, priority=2)

            stabilization_strength.periodization_id = 2

            strength_endurance = PeriodizedExercise(DetailedAdaptationType.strength_endurance, None,
                                               times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                               duration_range=None, rpe_range=None, priority=2)

            strength_endurance.periodization_id = 2

            return [stabilization_strength, strength_endurance]

        elif periodization_goal == PeriodizationGoalType.increase_cardio_endurance_with_speed:

            anaerobic_threshold_training = PeriodizedExercise(DetailedAdaptationType.anaerobic_threshold_training, None,
                                             times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                             duration_range=None, rpe_range=None, priority=1)

            anaerobic_threshold_training.periodization_id = 3

            high_intensity_anaerobic_training = PeriodizedExercise(DetailedAdaptationType.high_intensity_anaerobic_training, None,
                                               times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                               duration_range=None, rpe_range=None, priority=1)

            high_intensity_anaerobic_training.periodization_id = 3

            stabilization_strength = PeriodizedExercise(DetailedAdaptationType.stabilization_strength, None,
                                             times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                             duration_range=None, rpe_range=None, priority=3)

            stabilization_strength.periodization_id = 4

            strength_endurance = PeriodizedExercise(DetailedAdaptationType.strength_endurance, None,
                                               times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                               duration_range=None, rpe_range=None, priority=3)

            strength_endurance.periodization_id = 4

            return [anaerobic_threshold_training, high_intensity_anaerobic_training, stabilization_strength, strength_endurance]

        elif periodization_goal == PeriodizationGoalType.increase_strength_max_strength:

            hypertrophy = PeriodizedExercise(DetailedAdaptationType.hypertrophy, None,
                                             times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                             duration_range=None, rpe_range=None, priority=1)

            hypertrophy.periodization_id = 5

            maximal_strength = PeriodizedExercise(DetailedAdaptationType.maximal_strength, None,
                                               times_per_week_range=StandardErrorRange(lower_bound=2, upper_bound=3),
                                               duration_range=None, rpe_range=None, priority=1)

            maximal_strength.periodization_id = 5

            return [hypertrophy, maximal_strength]

    def get_one_required_combination(self, periodization_goal):

        if periodization_goal == PeriodizationGoalType.increase_cardiovascular_health or periodization_goal == PeriodizationGoalType.lose_weight:

            combo = PeriodizationOneRequiredCombination()
            combo.periodization_id = 1
            combo.combination_range = StandardErrorRange(lower_bound=3, upper_bound=5)

            return [combo]

        elif periodization_goal == PeriodizationGoalType.increase_cardio_endurance:

            combo = PeriodizationOneRequiredCombination()
            combo.periodization_id = 2
            combo.combination_range = StandardErrorRange(lower_bound=2, upper_bound=3)

            return [combo]

        elif periodization_goal == PeriodizationGoalType.increase_cardio_endurance_with_speed:

            combo_1 = PeriodizationOneRequiredCombination()
            combo_1.periodization_id = 3
            combo_1.combination_range = StandardErrorRange(lower_bound=2, upper_bound=3)

            combo_2 = PeriodizationOneRequiredCombination()
            combo_2.periodization_id = 4
            combo_2.combination_range = StandardErrorRange(lower_bound=2, upper_bound=3)

            return [combo_1, combo_2]

        elif periodization_goal == PeriodizationGoalType.increase_strength_max_strength:

            combo = PeriodizationOneRequiredCombination()
            combo.periodization_id = 5
            combo.combination_range = StandardErrorRange(lower_bound=2, upper_bound=3)

            return [combo]


class PeriodizationModelFactory(object):

    def create(self, persona, training_phase_type, periodization_goals):

        if persona == PeriodizationPersona.well_trained:

            periodization_model = PeriodizationModel()
            periodization_model.progression_persona = PeriodizationPersona.well_trained

            for goal in periodization_goals:
                periodization_model.required_exercises.extend(RequiredExerciseFactory().get_required_exercises(goal))
                periodization_model.one_required_exercises.extend(RequiredExerciseFactory().get_one_required_exercises(
                    goal))
                periodization_model.one_required_combinations.extend(RequiredExerciseFactory().get_one_required_combination(
                    goal))

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
