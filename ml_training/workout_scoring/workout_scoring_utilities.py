from models.session_functional_movement import SessionFunctionalMovement
from models.workout_program import WorkoutProgramModule
from models.session import MixedActivitySession, SportTrainingSession
from logic.workout_processing import WorkoutProcessor
from datetime import datetime, timedelta
from tests.mocks.mock_completed_session_details_datastore import CompletedSessionDetailsDatastore
from logic.periodization_processor import PeriodizationPlanProcessor
from models.periodization import PeriodizationPersona, PeriodizationGoal, TrainingPhaseType
from models.training_volume import StandardErrorRange
from models.soreness_base import BodyPartLocation
from models.ranked_types import RankedAdaptationType, RankedBodyPart
from models.movement_tags import AdaptationTypeMeasure
from models.periodization import TemplateWorkout
import numpy as np

from models.periodization import RequiredExerciseFactory

muscle_groups = list(BodyPartLocation.muscle_groups().keys())


def get_exercise_json(name, movement_id, reps, reps_unit=1, weight_measure=None, weight=None, rpe=5, duration=None):
    return {
            "id": "1",
            "name": name,
            "weight_measure": weight_measure,
            "weight": weight,
            "sets": 1,
            "reps_per_set": reps,
            "unit_of_measure": reps_unit,
            "movement_id": movement_id,
            "bilateral": True,
            "side": 0,
            "rpe": rpe,
            "pace": 120,
            "stroke_rate": 22,
            "duration": duration
        }


def define_all_exercises():
    return {
        "rowing": get_exercise_json("2k Row", reps=90, reps_unit=0, movement_id="58459d9ddc2ce90011f93d84", rpe=6, duration=30*60),
        "indoor_cycle": get_exercise_json("Indoor Cycle", reps=180, reps_unit=4, movement_id="57e2fd3a4c6a031dc777e90c", duration=20*60),
        "med_ball_chest_pass": get_exercise_json("Med Ball Chest Pass", reps=15, reps_unit=1, movement_id="586540fd4d0fec0011c031a4", weight_measure=2, weight=15),
        "explosive_burpee": get_exercise_json("Explosive Burpee", reps=15, reps_unit=1, movement_id="57e2fd3a4c6a031dc777e913"),
        "dumbbell_bench_press": get_exercise_json("Dumbbell Bench Press", reps=8, reps_unit=1, movement_id="57e2fd3a4c6a031dc777e847", weight_measure=2, weight=50),
        "bent_over_row": get_exercise_json("Bent Over Row", reps=8, reps_unit=1, movement_id="57e2fd3a4c6a031dc777e936", weight_measure=2, weight=150)
    }


def get_section_json(name, exercises):
    return {
                "name": name,
                "duration_seconds": 360,
                "start_date_time": None,
                "end_date_time": None,
                "exercises": exercises
            }


def get_workout_program(session, sections):
    all_exercises = define_all_exercises()
    workout_program = {
        "workout_sections": []
    }

    for section_name, exercises in sections.items():
        workout_program['workout_sections'].append(get_section_json(section_name, exercises=[all_exercises[ex] for ex in exercises]))

    workout = WorkoutProgramModule.json_deserialise(workout_program)
    processor = WorkoutProcessor()
    session.workout_program_module = workout
    processor.process_workout(session)
    return workout

def get_section(reference_number):

    if reference_number==0:
        sections = {
            "Cardio": ['rowing'],
            'Stamina': ['med_ball_chest_pass', 'explosive_burpee'],
            'Strength': ['dumbbell_bench_press', 'bent_over_row'],
            'Cardio2': ['indoor_cycle']
        }
    elif reference_number==1:
        sections = {
            "Cardio": ['rowing'],
            'Stamina': ['med_ball_chest_pass'],
            'Strength': ['dumbbell_bench_press'],
            'Cardio2': ['indoor_cycle']
        }
    elif reference_number==2:
        sections = {
            "Cardio": ['rowing'],
            'Stamina': ['explosive_burpee'],
            'Strength': ['bent_over_row'],
            'Cardio2': ['indoor_cycle']
        }
    elif reference_number==3:
        sections = {
            "cardio": ['indoor_cycle'],
            'Strength': ['bent_over_row','indoor_cycle'],
            'cardio2': ['indoor_cycle']
        }
    elif reference_number==4:
        sections = {
            "Warmup / Movement Prep": ['rowing'],
            'Stamina': ['med_ball_chest_pass', 'explosive_burpee','med_ball_chest_pass'],
            'Strength': ['dumbbell_bench_press', 'bent_over_row'],
            'Recovery Protocol': ['indoor_cycle']
        }
    else:
        sections = {
            "cardio": ['indoor_cycle']
        }

    return sections


def get_sessions(session_types, dates, rpes, durations, sport_names, sections_list):

    if len(session_types) != len(dates) != len(rpes) != len(durations) != len(sport_names):
        raise Exception("length must match for all arguments")

    sessions = []

    for d in range(0, len(dates)):
        if session_types[d] == 7:
            session = MixedActivitySession()
            sections = get_section(sections_list[d])
            session.workout_program_module = get_workout_program(session, sections=sections)
        else:
            session = SportTrainingSession()
            session.sport_name = sport_names[d]
        session.event_date = dates[d]
        session.session_RPE = rpes[d]
        session.duration_minutes = durations[d]

        sessions.append(session)

    return sessions

def get_seven_day_completed_data_store():

    session_types = [7, 7, 7, 7, 7, 7, 7]
    sections = [1, 2, 3, 4, 5, 2, 1]

    dates = []
    for d in range(0, 7):
        dates.append(datetime.now() - timedelta(days=d))
    rpes = [StandardErrorRange(observed_value=5),
            StandardErrorRange(observed_value=6),
            StandardErrorRange(observed_value=4),
            StandardErrorRange(observed_value=5),
            StandardErrorRange(observed_value=6),
            StandardErrorRange(observed_value=3),
            StandardErrorRange(observed_value=4)]

    durations = [100, 90, 80, 90, 95, 85, 105]
    sport_names = [None, None, None, None, None, None, None]

    # workout_programs = [get_workout_program(sections=sections)]

    sessions = get_sessions(session_types, dates, rpes, durations, sport_names, sections)

    completed_session_details_list = []

    for session in sessions:
        session_functional_movement = SessionFunctionalMovement(session, {})
        session_functional_movement.process(session.event_date, None)
        completed_session_details_list.append(session_functional_movement.completed_session_details)

    completed_session_details_list = [c for c in completed_session_details_list if c is not None]

    data_store = CompletedSessionDetailsDatastore()
    data_store.side_load_planned_workout(completed_session_details_list)

    return data_store


def get_template_workout():

    data_store = get_seven_day_completed_data_store()
    proc = PeriodizationPlanProcessor(datetime.now(), PeriodizationGoal.increase_cardio_endurance_with_speed,
                                      PeriodizationPersona.well_trained, TrainingPhaseType.increase, data_store, None)
    plan = proc.create_periodization_plan(datetime.now().date())
    return plan.template_workout


def get_required_exercises(goal):
    required_exercises = RequiredExerciseFactory().get_required_exercises(goal)
    one_required_exercises = RequiredExerciseFactory().get_one_required_exercises(goal)
    return required_exercises, one_required_exercises


def get_muscle_needs():
    muscle_load_needs = {}

    no_load_needed_muscles = np.random.choice(muscle_groups, np.random.randint(0, 5))  # TODO need a better way to randomize which muscles have been fully loaded alredy
    for muscle in no_load_needed_muscles:
        muscle_load_needs[muscle] = 0
    muscles_to_be_loaded = set(muscle_groups) - set(no_load_needed_muscles)

    # get some muscles that have not been loaded at all
    missing_muscle_groups = np.random.choice(list(muscles_to_be_loaded), np.random.randint(1, 5))  # TODO need a better way to randomize which muscles haven't been loaded
    for muscle in missing_muscle_groups:
        muscle_load_needs[muscle] = 100
    remaining_muscles = muscles_to_be_loaded - set(missing_muscle_groups)

    for muscle in remaining_muscles:
        muscle_load_needs[muscle] = np.random.random() * 100  # TODO need a better way to randomize how much a muscle has been loaded so far
    return muscle_load_needs

def randomize_template_workout(template_workout):
    rpe_lower = np.random.uniform(1, 8)
    rpe_upper = np.random.uniform(rpe_lower, max([rpe_lower + 3, 9]))
    template_workout.acceptable_session_rpe = StandardErrorRange(lower_bound=rpe_lower, upper_bound=rpe_upper)
    duration_lower = np.random.uniform(20 * 60, 90 * 60) # lower is in range 20 min to 90 min
    duration_upper = np.random.uniform(duration_lower, max([duration_lower + 20 * 60, 90 * 60]))  #upper limit is max of lower + 20 mins or 100 mins
    template_workout.acceptable_session_duration = StandardErrorRange(lower_bound=duration_lower, upper_bound=duration_upper)
    rpe_load = template_workout.acceptable_session_rpe.plagiarize()
    rpe_load.multiply_range(template_workout.acceptable_session_duration)
    template_workout.acceptable_session_rpe_load = rpe_load
    template_workout.muscle_load_ranking = get_muscle_needs()
    template_workout.acceptable_session_power_load = StandardErrorRange()
    template_workout.adaptation_type_ranking = adjust_adaptation_type_ranking(template_workout.adaptation_type_ranking)


def adjust_adaptation_type_ranking(adaptation_type_ranking):
    if len(adaptation_type_ranking) <= 2:
        selected_adaptation_type_ranking = adaptation_type_ranking
    else:
        min_ranked_types = 2
        max_ranked_types = len(adaptation_type_ranking) + 1
        selected_adaptation_type_ranking = list(np.random.choice(adaptation_type_ranking, size=np.random.randint(min_ranked_types, max_ranked_types), replace=False))
    if len(adaptation_type_ranking) != len(selected_adaptation_type_ranking):
        last_used_ranking = 0
        last_found_ranking = 0
        for rat in selected_adaptation_type_ranking:
            if rat.ranking == last_used_ranking:
                pass
            elif rat.ranking == last_found_ranking:
                rat.ranking = last_used_ranking
            else:
                last_found_ranking = rat.ranking
                rat.ranking = last_used_ranking + 1
            last_used_ranking = rat.ranking
    all_rankings = list(set(rat.ranking for rat in selected_adaptation_type_ranking))
    shuffled_rankings = list(set(rat.ranking for rat in selected_adaptation_type_ranking))
    np.random.shuffle(shuffled_rankings)
    ranking_shuffle_dict = {old: new for old, new in zip(all_rankings, shuffled_rankings)}
    for rat in selected_adaptation_type_ranking:
        rat.ranking = ranking_shuffle_dict.get(rat.ranking)
    return selected_adaptation_type_ranking


def get_template_workouts():
    goals = [
        PeriodizationGoal.increase_cardiovascular_health,
        PeriodizationGoal.increase_cardio_endurance,
        PeriodizationGoal.increase_cardio_endurance_with_speed,
        PeriodizationGoal.increase_strength_max_strength
    ]
    all_template_workouts = []
    for goal in goals:
        template_workout = TemplateWorkout()
        required_exercises, one_required_exercises = get_required_exercises(goal)
        all_required_exercises = []
        all_required_exercises.extend(required_exercises)
        all_required_exercises.extend(one_required_exercises)
        all_required_exercises.sort(key=lambda x: (1-x.priority, x.times_per_week.lowest_value()), reverse=True)
        template_workout.adaptation_type_ranking = rank_adaptation_types(all_required_exercises)
        all_template_workouts.append(template_workout)

    return all_template_workouts

def rank_adaptation_types(sorted_required_exercises):
    required_exercise_dict = {}

    ranking = 1
    last_times_per_week = None
    last_priority = None
    last_ranking_used = 0

    for periodized_exercise in sorted_required_exercises:
        adjusted_ranking = False
        if periodized_exercise.times_per_week.lowest_value() > 0:
            if last_times_per_week is None:
                last_times_per_week = periodized_exercise.times_per_week.lowest_value()
            elif last_times_per_week > periodized_exercise.times_per_week.lowest_value():
                if ranking == last_ranking_used:
                    ranking += 1
                    adjusted_ranking = True

            if last_priority is None:
                last_priority = periodized_exercise.priority
            elif last_priority < periodized_exercise.priority:
                last_priority = periodized_exercise.priority
                if not adjusted_ranking:
                    if ranking == last_ranking_used:
                        ranking += 1

            if periodized_exercise.detailed_adaptation_type is not None:
                detailed_ranked_type = RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,
                                                            periodized_exercise.detailed_adaptation_type,
                                                            ranking,
                                                            periodized_exercise.duration.highest_value() if periodized_exercise.duration is not None else None)

                if periodized_exercise.detailed_adaptation_type not in required_exercise_dict:
                    required_exercise_dict[periodized_exercise.detailed_adaptation_type] = detailed_ranked_type
                    last_ranking_used = ranking
                else:
                    # if same ranking, go with the larger duration, otherwise ignore the duration of the lower ranking
                    if required_exercise_dict[periodized_exercise.detailed_adaptation_type].ranking == ranking:
                        if required_exercise_dict[periodized_exercise.detailed_adaptation_type].duration is None:
                            required_exercise_dict[periodized_exercise.detailed_adaptation_type].duration = periodized_exercise.duration.highest_value()
                        else:
                            if periodized_exercise.duration is not None:
                                required_exercise_dict[periodized_exercise.detailed_adaptation_type].duration = max(required_exercise_dict[periodized_exercise.detailed_adaptation_type].duration,
                                                                                                                    periodized_exercise.duration.highest_value())

            if periodized_exercise.sub_adaptation_type is not None:
                sub_adaptation_type = RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type,
                                                           periodized_exercise.sub_adaptation_type,
                                                           ranking,
                                                           periodized_exercise.duration.highest_value() if periodized_exercise.duration is not None else None)

                if periodized_exercise.sub_adaptation_type not in required_exercise_dict:
                    required_exercise_dict[periodized_exercise.sub_adaptation_type] = sub_adaptation_type
                    last_ranking_used = ranking
                else:
                    # if same ranking, go with the larger duration, otherwise ignore the duration of the lower ranking
                    if required_exercise_dict[periodized_exercise.sub_adaptation_type].ranking == ranking:
                        if required_exercise_dict[periodized_exercise.sub_adaptation_type].duration is None:
                            required_exercise_dict[
                                periodized_exercise.sub_adaptation_type].duration = periodized_exercise.duration.highest_value()
                        else:
                            if periodized_exercise.duration is not None:
                                required_exercise_dict[periodized_exercise.sub_adaptation_type].duration = max(
                                        required_exercise_dict[periodized_exercise.sub_adaptation_type].duration,
                                        periodized_exercise.duration.highest_value())

    ranked_adaptation_type_list = list(required_exercise_dict.values())
    return ranked_adaptation_type_list

