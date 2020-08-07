from models.training_load import DetailedTrainingLoad, CompletedSessionDetails
from models.training_volume import StandardErrorRange
from models.movement_tags import DetailedAdaptationType
from logic.periodization_processor import PeriodizationPlanProcessor, WorkoutScoringManager
from models.periodization import PeriodizedExercise, PeriodizationGoal, PeriodizationPersona, TrainingPhaseType
from models.movement_tags import RankedAdaptationType, AdaptationDictionary, SubAdaptationType, TrainingType, AdaptationTypeMeasure
from models.planned_exercise import PlannedWorkoutLoad
from tests.mocks.mock_workout_library_datastore import PlannedWorkoutLibraryDatastore
from tests.mocks.mock_completed_session_details_datastore import CompletedSessionDetailsDatastore
from tests.mocks.mock_workout_datastore import WorkoutDatastore
from datetime import datetime, timedelta
from tests.mocks.planned_workout_utilities import get_planned_workout

planned_workout_dictionary = PlannedWorkoutLibraryDatastore().get()


def get_workout_list():

    workout_library_list = list(planned_workout_dictionary.values())

    return workout_library_list


class SimpleWorkout(object):
    def __init__(self, id, rpe, duration, ranked_detailed_adaptation_types, ranked_sub_adaptation_types, session_rpe_load=None):
        self.id = id
        self.projected_session_rpe = rpe
        self.duration = duration
        self.projected_rpe_load = session_rpe_load
        self.ranking = 0
        self.score = 0
        self.session_detailed_load = DetailedTrainingLoad()
        self.session_detailed_load.detailed_adaptation_types = ranked_detailed_adaptation_types
        self.session_detailed_load.sub_adaptation_types = ranked_sub_adaptation_types
        self.update_adaptation_types()
        self.projected_monotony = None
        self.projected_strain_event_level = None

    def update_adaptation_types(self):

        adaptation_dictionary = AdaptationDictionary()

        if len(self.session_detailed_load.sub_adaptation_types) == 0:
            self.session_detailed_load.sub_adaptation_types = [
                RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type, adaptation_dictionary.detailed_types[d.adaptation_type], d.ranking, 0) for d in
                self.session_detailed_load.detailed_adaptation_types]
            adapt_dict = {}
            for a in self.session_detailed_load.sub_adaptation_types:
                if a.adaptation_type not in adapt_dict.keys():
                    adapt_dict[a.adaptation_type] = a.ranking
                else:
                    adapt_dict[a.adaptation_type] = min(a.ranking, adapt_dict[a.adaptation_type])
            sub_types = []
            for a, r in adapt_dict.items():
                sub_types.append(RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type, a, r, 0))
            self.session_detailed_load.sub_adaptation_types = sub_types


def get_fake_training_history(start_date_time, rpe_list, watts_list, durations_list, workout_ids):

    load_list = []

    for r in range(len(rpe_list)):
        if rpe_list[r] > 0:
            session_parameters = SessionParameters(start_date_time + timedelta(days=r), workout_ids[r])
            session_parameters.power_load = StandardErrorRange(lower_bound=watts_list[r]*durations_list[r]*.9,
                                                               observed_value=watts_list[r]*durations_list[r],
                                                               upper_bound=watts_list[r] * durations_list[r] * 1.15)
            session_parameters.rpe_load = StandardErrorRange(lower_bound=rpe_list[r]*durations_list[r]*.9,
                                                             observed_value=rpe_list[r]*durations_list[r],
                                                             upper_bound=rpe_list[r] * durations_list[r] * 1.15)
            session_parameters.session_rpe = StandardErrorRange(lower_bound=rpe_list[r]-1,
                                                                observed_value=rpe_list[r],
                                                                upper_bound=rpe_list[r]+1)
            session_parameters.duration = durations_list[r]

            completed_workout = get_completed_workout(session_parameters)

            load_list.append(completed_workout)

    return load_list


def create_workout_week(start_date_time, week_list):

    completed_workouts = []

    for d in range(0, len(week_list)):
        workout_id = week_list[d]
        if workout_id > 0:
            workout = planned_workout_dictionary[str(workout_id)]
            completed_workout = complete_a_planned_workout(start_date_time - timedelta(days=d), workout)
            completed_workouts.append(completed_workout)

    return completed_workouts


def create_workout_history(start_date_time):

    workout_history = []

    current_weeks_load = create_workout_week(start_date_time, [0, 25])
    previous_1_weeks_load = create_workout_week(start_date_time - timedelta(days=6), [0, 28, 0, 26, 35, 28, 0])
    previous_2_weeks_load = create_workout_week(start_date_time - timedelta(days=13), [0, 25, 26, 0, 28, 25, 15])
    previous_3_weeks_load = create_workout_week(start_date_time - timedelta(days=20), [0, 25, 34, 31, 0, 26, 0])
    previous_4_weeks_load = create_workout_week(start_date_time - timedelta(days=27), [0, 29, 0, 0, 45, 48, 0])

    workout_history.extend(current_weeks_load)
    workout_history.extend(previous_1_weeks_load)
    workout_history.extend(previous_2_weeks_load)
    workout_history.extend(previous_3_weeks_load)
    workout_history.extend(previous_4_weeks_load)

    return workout_history


class SessionParameters(object):
    def __init__(self, event_date_time, workout_id):
        self.event_date_time = event_date_time
        self.provider_id = 1
        self.workout_id = workout_id
        self.duration = None
        self.session_rpe=None
        self.rpe_load=None
        self.power_load=None
        self.session_detailed_load = None
        self.muscle_detailed_load = None


def get_completed_workout(session_parameters: SessionParameters):

    session = CompletedSessionDetails(session_parameters.event_date_time, session_parameters.provider_id,
                                      session_parameters.workout_id)
    session.duration = session_parameters.duration
    session.session_RPE = session_parameters.session_rpe
    session.rpe_load = session_parameters.rpe_load
    session.power_load = session_parameters.power_load
    session.session_detailed_load = session_parameters.session_detailed_load
    session.muscle_detailed_load = session_parameters.muscle_detailed_load

    return session


def complete_a_planned_workout(event_date_time, planned_workout: PlannedWorkoutLoad):

    session = CompletedSessionDetails(event_date_time, 1, planned_workout.workout_id)
    session.duration = planned_workout.duration
    session.session_RPE = planned_workout.projected_session_rpe
    session.rpe_load = planned_workout.projected_rpe_load
    session.power_load = planned_workout.projected_power_load
    session.session_detailed_load = planned_workout.session_detailed_load
    session.muscle_detailed_load = planned_workout.muscle_detailed_load

    return session


# def test_find_workout_combinations():
#
#     rpe_list = list(range(1,11,1))
#     duration_list = list(range(30, 150, 5))
#     workouts = get_list_of_load_workouts(rpe_list, duration_list)
#
#     athlete_training_history = get_fake_training_history()
#
#     athlete_training_goal = PeriodizationGoal.increase_cardiovascular_health
#
#     proc = PeriodizationPlanProcessor(athlete_training_goal, athlete_training_history, PeriodizationPersona.well_trained,TrainingPhaseType.slowly_increase)
#     proc.set_weekly_targets()
#
#     completed_workouts = []
#
#     acceptable_workouts_1 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=True)
#
#     acceptable_workouts_1_copy = [a for a in acceptable_workouts_1]
#
#     completed_workout_1 = acceptable_workouts_1_copy.pop(0)
#     completed_workouts.append(completed_workout_1)
#
#     acceptable_workouts_2 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=True)
#
#     acceptable_workouts_2_copy = [a for a in acceptable_workouts_2]
#
#     completed_workout_2 = acceptable_workouts_2_copy.pop(0)
#     completed_workouts.append(completed_workout_2)
#
#     acceptable_workouts_3 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=True)
#
#     acceptable_workouts_3_copy = [a for a in acceptable_workouts_3]
#
#     completed_workout_3 = acceptable_workouts_3_copy.pop(0)
#     completed_workouts.append(completed_workout_3)
#
#     acceptable_workouts_4 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=True)
#
#     acceptable_workouts_4_copy = [a for a in acceptable_workouts_4]
#
#     completed_workout_4 = acceptable_workouts_4_copy.pop(0)
#     completed_workouts.append(completed_workout_4)
#
#     acceptable_workouts_5 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=True)
#
#     assert len(acceptable_workouts_5) > 0


# def test_top_rec_should_be_greatest_need_day_3_cardio():
#
#     start_date_time = datetime.now()
#
#     workout_history = create_workout_history(datetime.now())
#
#     completed_session_details_datastore = CompletedSessionDetailsDatastore()
#     completed_session_details_datastore.side_load_planned_workout(workout_history)
#
#     workout_library_datastore = PlannedWorkoutLibraryDatastore()
#
#     athlete_training_goal = PeriodizationGoal.increase_cardiovascular_health
#
#     proc = PeriodizationPlanProcessor(start_date_time,athlete_training_goal,PeriodizationPersona.well_trained,
#                                       TrainingPhaseType.slowly_increase,
#                                       completed_session_details_datastore,
#                                       workout_library_datastore)
#     plan = proc.create_periodization_plan(datetime.now().date())
#
#     acceptable_workouts_1 = [a for a in plan.next_workouts[0]]
#
#     acceptable_workout_1 = next(a for a in acceptable_workouts_1 if a.session_detailed_load.sub_adaptation_types[0].adaptation_type == SubAdaptationType.strength)
#     completed_workout_1 = complete_a_planned_workout(start_date_time+timedelta(days=1), acceptable_workout_1)
#
#     proc.completed_session_details_datastore.completed_sessions.append(completed_workout_1)
#     plan = proc.update_periodization_plan(plan, (start_date_time+timedelta(days=1)).date())
#
#     acceptable_workouts_2 = [a for a in plan.next_workouts[0]]
#
#     acceptable_workout_2 = next(a for a in acceptable_workouts_2 if a.session_detailed_load.sub_adaptation_types[
#         0].adaptation_type == SubAdaptationType.strength)
#     completed_workout_2 = complete_a_planned_workout(start_date_time + timedelta(days=2), acceptable_workout_2)
#
#     proc.completed_session_details_datastore.completed_sessions.append(completed_workout_2)
#     plan = proc.update_periodization_plan(plan, (start_date_time + timedelta(days=2)).date())
#
#     acceptable_workouts_3 = [a for a in plan.next_workouts[0]]
#
#     strength_workouts = [a for a in acceptable_workouts_3 if a.session_detailed_load.sub_adaptation_types[0].adaptation_type == SubAdaptationType.strength]
#     cardio_workouts = [a for a in acceptable_workouts_3 if
#                          a.session_detailed_load.sub_adaptation_types[0].adaptation_type == SubAdaptationType.cardiorespiratory_training]
#
#     assert acceptable_workouts_3[0].session_detailed_load.sub_adaptation_types[0].adaptation_type == SubAdaptationType.cardiorespiratory_training


def test_acceptable_strength_cardio_same_score_both_required():

    proc = PeriodizationPlanProcessor(datetime.now(),None, None, None,  CompletedSessionDetailsDatastore(), None)
    strength_list = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, DetailedAdaptationType.muscular_endurance, 1, 0),
                    RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, DetailedAdaptationType.strength_endurance, 1, 0)]
    cardio_list = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, DetailedAdaptationType.anaerobic_threshold_training, 1, 0),
                   RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, DetailedAdaptationType.high_intensity_anaerobic_training, 2, 0)]
    periodized_strength_exercise = PeriodizedExercise(None, SubAdaptationType.strength,
                                                      times_per_week_range=StandardErrorRange(lower_bound=2),
                                                      duration_range=None,
                                                      rpe_range=None)
    periodized_cardio_exercise = PeriodizedExercise(None, SubAdaptationType.cardiorespiratory_training,
                                                    times_per_week_range=StandardErrorRange(lower_bound=2),
                                                    duration_range=StandardErrorRange(lower_bound=60, upper_bound=90),
                                                    rpe_range=StandardErrorRange(lower_bound=4, upper_bound=5))

    session_rpe_load = StandardErrorRange(500, 700, 600)
    # Note session rpe needs to match cardio's rpe range for this to work
    session_rpe = StandardErrorRange(lower_bound=4, observed_value=4.5, upper_bound=5)
    strength_workout = SimpleWorkout(1, session_rpe, 75, strength_list,[], session_rpe_load=session_rpe_load)
    cardio_workout = SimpleWorkout(1, session_rpe, 75, cardio_list, [], session_rpe_load=session_rpe_load)

    strength_score = proc.get_workout_score(strength_workout, periodized_strength_exercise,
                                            StandardErrorRange(lower_bound=450, upper_bound=650))
    cardio_score = proc.get_workout_score(cardio_workout, periodized_cardio_exercise,
                                          StandardErrorRange(lower_bound=450, upper_bound=650))

    assert strength_score == cardio_score


def test_completing_combo_required_reduces_score():

    proc = PeriodizationPlanProcessor(datetime.now(), None, None, None,  CompletedSessionDetailsDatastore(), None)
    cardio_list = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, DetailedAdaptationType.anaerobic_threshold_training, 1, 10),
                   RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, DetailedAdaptationType.high_intensity_anaerobic_training, 2, 10)]

    vigorous_cardio_exercise = PeriodizedExercise(None, SubAdaptationType.cardiorespiratory_training,
                                                    times_per_week_range=StandardErrorRange(lower_bound=2),
                                                    duration_range=StandardErrorRange(lower_bound=30, upper_bound=60),
                                                    rpe_range=StandardErrorRange(lower_bound=6, upper_bound=10))

    moderate_cardio_exercise = PeriodizedExercise(None, SubAdaptationType.cardiorespiratory_training,
                                                    times_per_week_range=StandardErrorRange(lower_bound=3, upper_bound=5),
                                                    duration_range=StandardErrorRange(lower_bound=60, upper_bound=90),
                                                    rpe_range=StandardErrorRange(lower_bound=3, upper_bound=5))

    paul_cardio_workout = get_planned_workout(1, [TrainingType.strength_cardiorespiratory],
                                              session_rpe=StandardErrorRange(lower_bound=3, observed_value=4, upper_bound=5),
                                              projected_rpe_load=StandardErrorRange(lower_bound=3 * 75, observed_value=4 * 75,
                                                                upper_bound=5 * 75),
                                              reps=10,
                                              rpe=StandardErrorRange(observed_value=7.5),
                                              duration=75,
                                              percent_max_hr=65
                                              )

    vigorous_cardio_workout = get_planned_workout(1, [TrainingType.strength_cardiorespiratory],
                                                  session_rpe=StandardErrorRange(lower_bound=7, observed_value=8, upper_bound=9),
                                                  projected_rpe_load=StandardErrorRange(lower_bound=7 * 75, observed_value=8 * 75,
                                                                upper_bound=9 * 75),
                                                  reps=10,
                                                  rpe=StandardErrorRange(observed_value=7.5),
                                                  duration=75,
                                                  percent_max_hr=75)

    one_required_combination = StandardErrorRange(lower_bound=3, upper_bound=5)

    paul_cardio_workout_score_vigorous = proc.get_workout_score(paul_cardio_workout, vigorous_cardio_exercise,
                                            StandardErrorRange(lower_bound=2700, upper_bound=3500),
                                                                one_required_combination)
    paul_cardio_workout_score_moderate = proc.get_workout_score(paul_cardio_workout, moderate_cardio_exercise,
                                                                StandardErrorRange(lower_bound=2700, upper_bound=3500),
                                                                one_required_combination)

    vigorous_cardio_workout_score_vigorous = proc.get_workout_score(vigorous_cardio_workout, vigorous_cardio_exercise,
                                            StandardErrorRange(lower_bound=2700, upper_bound=3500),
                                                                one_required_combination)
    vigorous_cardio_workout_score_moderate = proc.get_workout_score(vigorous_cardio_workout, moderate_cardio_exercise,
                                                                StandardErrorRange(lower_bound=2700, upper_bound=3500),
                                                                one_required_combination)

    one_required_combination_statisfied = StandardErrorRange(lower_bound=0, upper_bound=2)

    paul_cardio_workout_score_vigorous_2 = proc.get_workout_score(paul_cardio_workout, vigorous_cardio_exercise,
                                                                StandardErrorRange(lower_bound=2700, upper_bound=3500),
                                                                  one_required_combination_statisfied)
    paul_cardio_workout_score_moderate_2 = proc.get_workout_score(paul_cardio_workout, moderate_cardio_exercise,
                                                                StandardErrorRange(lower_bound=2700, upper_bound=3500),
                                                                  one_required_combination_statisfied)

    vigorous_cardio_workout_score_vigorous_2 = proc.get_workout_score(vigorous_cardio_workout, vigorous_cardio_exercise,
                                                                    StandardErrorRange(lower_bound=2700,
                                                                                       upper_bound=3500),
                                                                      one_required_combination_statisfied)
    vigorous_cardio_workout_score_moderate_2 = proc.get_workout_score(vigorous_cardio_workout, moderate_cardio_exercise,
                                                                    StandardErrorRange(lower_bound=2700,
                                                                                       upper_bound=3500),
                                                                      one_required_combination_statisfied)

    assert paul_cardio_workout_score_moderate > paul_cardio_workout_score_moderate_2
    assert paul_cardio_workout_score_vigorous > paul_cardio_workout_score_vigorous_2
    assert vigorous_cardio_workout_score_moderate > vigorous_cardio_workout_score_moderate_2
    assert vigorous_cardio_workout_score_vigorous > vigorous_cardio_workout_score_vigorous_2


# def test_too_high_session_load_lower_score():
#
#     proc = PeriodizationPlanProcessor(None, None, None, None)
#     list_a = [RankedAdaptationType(DetailedAdaptationType.muscular_endurance, 1),
#               RankedAdaptationType(DetailedAdaptationType.strength_endurance, 2)]
#     periodized_exercise = PeriodizedExercise(None, SubAdaptationType.strength,StandardErrorRange(lower_bound=2), None, None)
#
#     workout = SimpleWorkout(1, None, None, list_a,[], session_load=800)
#
#     score = proc.get_workout_score(workout, periodized_exercise, StandardErrorRange(lower_bound=450, upper_bound=650))
#
#     assert score == 68.0
#
#
def test_cosine_similarity_prioritized_adaptation_types_equal():

    list_a = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.muscular_endurance, 1, 10),
              RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.strength_endurance, 2, 10)]
    list_b = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.muscular_endurance, 1, 10),
              RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.strength_endurance, 2, 10)]

    val = WorkoutScoringManager.cosine_similarity(list_a, list_b)

    assert 1.0 == round(val, 5)


def test_cosine_similarity_prioritized_adaptation_types_half_equal():

    list_a = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.muscular_endurance, 1, 10),
              RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.strength_endurance, 2, 0)]
    list_b = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.muscular_endurance, 1, 10),
              RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.hypertrophy, 2, 0)]

    val = WorkoutScoringManager.cosine_similarity(list_a, list_b)

    assert 0.67 == round(val, 2)


def test_cosine_similarity_prioritized_adaptation_types_partial_credit():

    list_a = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type, DetailedAdaptationType.muscular_endurance, 1, 10),
              RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.strength_endurance, 2, 10)]
    list_b = [RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.muscular_endurance, 2, 10),
              RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,DetailedAdaptationType.strength_endurance, 1, 10)]

    val = WorkoutScoringManager.cosine_similarity(list_a, list_b)

    assert 0.67 == round(val, 2)




