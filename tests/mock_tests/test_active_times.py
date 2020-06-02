import pytest
from models.exercise_phase import ExercisePhaseType
from models.session import SportTrainingSession, MixedActivitySession
from models.functional_movement_modalities import ModalityType
from datetime import datetime
from models.sport import SportName
from models.symptom import Symptom
from models.user_stats import UserStats
from logic.injury_risk_processing import InjuryRiskProcessor
from logic.exercise_assignment import ExerciseAssignment
from logic.workout_processing import WorkoutProcessor
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from models.workout_program import WorkoutProgramModule

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def get_symptoms(body_parts):
    """

    :param body_parts: list of body_part_tuple (body_part_location, side, tight, knots, ache, sharp)
    :return:
    """
    symptoms = []
    for body_part in body_parts:
        symptom = {
            "body_part": body_part[0],
            "side": body_part[1],
            "tight": body_part[2],
            "knots": body_part[3],
            "ache": body_part[4],
            "sharp": body_part[5]
        }
        symptom['reported_date_time'] = datetime.now()
        symptom['user_id'] = 'tester'
        symptom = Symptom.json_deserialise(symptom)
        symptoms.append(symptom)
    return symptoms


def get_exercise_json(name, movement_id, reps, reps_unit=1, weight_measure=None, weight=None, rpe=5):
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
            "stroke_rate": 22
        }


def define_all_exercises():
    return {
        "rowing": get_exercise_json("2k Row", reps=90, reps_unit=0, movement_id="58459d9ddc2ce90011f93d84", rpe=6),
        "indoor_cycle": get_exercise_json("Indoor Cycle", reps=180, reps_unit=4, movement_id="57e2fd3a4c6a031dc777e90c"),
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


def get_workout_program(sections):
    all_exercises = define_all_exercises()
    # rowing = all_exercises['rowing']
    # indoor_cycle = all_exercises['indoor_cycle']
    # med_ball_chest_pass = all_exercises['med_ball_chest_pass']
    # explosive_burpee = all_exercises['explosive_burpee']
    # dumbbell_bench_press = all_exercises['dumbbell_bench_press']
    # bent_over_row = all_exercises['bent_over_row']
    workout_program = {
        "workout_sections": []
    }

    for section_name, exercises in sections.items():
        workout_program['workout_sections'].append(get_section_json(section_name, exercises=[all_exercises[ex] for ex in exercises]))

    workout = WorkoutProgramModule.json_deserialise(workout_program)
    processor = WorkoutProcessor()
    processor.process_workout(workout)
    return workout


def get_sport_body_parts(training_sessions):
    sport_body_parts = {}
    for session in training_sessions:
        sport_body_parts.update(session.get_load_body_parts())
    return sport_body_parts


def check_cardio_sport(training_sessions):
    sport_cardio_plyometrics = False
    for session in training_sessions:
        if session.is_cardio_plyometrics():
            sport_cardio_plyometrics = True
    return sport_cardio_plyometrics


def is_high_intensity_session(training_sessions):
    for session in training_sessions:
        if session.ultra_high_intensity_session() and session.high_intensity_RPE():
            return True
    return False


def get_sessions(session_types, dates, rpes, durations, sport_names, workout_programs):

    if len(session_types) != len(dates) != len(rpes) != len(durations) != len(sport_names) != len(workout_programs):
        raise Exception("length must match for all arguments")

    sessions = []

    for d in range(0, len(dates)):
        if session_types[d] == 7:
            session = MixedActivitySession()
        else:
            session = SportTrainingSession()
        session.event_date = dates[d]
        session.session_RPE = rpes[d]
        session.duration_minutes = durations[d]
        session.sport_name = sport_names[d]
        session.workout_program_module = workout_programs[d]
        sessions.append(session)

    return sessions


def get_total_durations(activity):
    total_duration_efficient = 0
    total_duration_complete = 0
    total_duration_comprehensive = 0
    total_exercises = 0
    for ex_phase in activity.exercise_phases:
        phase_name = ex_phase.name
        duration_efficient_phase = 0
        duration_complete_phase = 0
        duration_comprehensive_phase = 0
        ex_count_phase = 0
        for ex in ex_phase.exercises.values():
            ex_count_phase += 1
            duration_efficient_phase += ex.duration_efficient()
            duration_complete_phase += ex.duration_complete()
            duration_comprehensive_phase += ex.duration_comprehensive()
        if ex_count_phase > 0:
            print(f"{phase_name}: exercises assigned: {ex_count_phase}, durations: efficient: {round(duration_efficient_phase / 60, 2)}, "
                  f"complete: {round(duration_complete_phase / 60, 2)}, comprehensive: {round(duration_comprehensive_phase / 60, 2)}")
            total_duration_efficient += duration_efficient_phase
            total_duration_complete += duration_complete_phase
            total_duration_comprehensive += duration_comprehensive_phase
            total_exercises += ex_count_phase

    print(f"{activity.title}, exercises assigned: {total_exercises}, durations: efficient: {round(total_duration_efficient / 60, 2)},"
          f"complete: {round(total_duration_complete / 60, 2)}, comprehensive: {round(total_duration_comprehensive / 60, 2)}")
    return total_duration_efficient, total_duration_complete, total_duration_comprehensive


def get_activity(event_date_time, symptoms, sessions, activity_type='movement_prep'):
    proc = InjuryRiskProcessor(event_date_time, symptoms, sessions, {}, UserStats("tester"), "tester")
    proc.process(aggregate_results=True)
    consolidated_injury_risk_dict = proc.get_consolidated_dict()
    calc = ExerciseAssignment(
            injury_risk_dict=consolidated_injury_risk_dict,
            exercise_library_datastore=exercise_library_datastore,
            completed_exercise_datastore=completed_exercise_datastore,
            event_date_time=event_date_time,
            relative_load_level=proc.relative_load_level,
            aggregated_injury_risk_dict=proc.aggregated_injury_risk_dict
    )
    if activity_type == 'movement_prep':
        calc.sport_cardio_plyometrics = check_cardio_sport(sessions)
        calc.sport_body_parts = get_sport_body_parts(sessions)
        movement_prep = calc.get_movement_integration_prep(force_on_demand=True)
        return movement_prep
    elif activity_type == 'mobility_wod':
        mobility_wod = calc.get_active_rest('tester', force_on_demand=True)
        return mobility_wod
    elif activity_type == 'responsive_recovery':
        calc.high_intensity_session = is_high_intensity_session(sessions)
        modality, ice, cwi = calc.get_responsive_recovery_modality(sessions[0].id, force_on_demand=True)
        return modality, ice, cwi


def test_get_responsive_recovery_with_simple_session_one_symptom_high_rpe():
    session_types = [6]
    dates = [datetime.now()]
    rpes = [7]
    durations = [100]
    sport_names = [SportName.weightlifting]
    workout_programs = [None]

    sessions = get_sessions(session_types, dates, rpes, durations, sport_names, workout_programs)
    symptoms = get_symptoms(body_parts=[
        (7, 1, None, None, None, 2)  # left knee sharp=2
    ])

    activity, ice, cwi = get_activity(dates[0], symptoms, sessions, 'responsive_recovery')
    print("\nactive_recovery, 100 mins weightlifting, high rpe (ice vs cwi), knee sharp=2")
    assert len(activity) == 1
    activity = activity[0]
    assert activity.type == ModalityType.active_recovery
    assert activity.display_image == "dynamic_stretch"
    assert activity.when == "after training"
    assert activity.locked_text == "You missed the optimal window for Active Recovery."
    assert activity.title == "Active Recovery".upper()

    exercise_phases = activity.exercise_phases
    assert len(exercise_phases) == 1
    assert exercise_phases[0].type == ExercisePhaseType.dynamic_integrate

    duration_efficient, duration_complete, duration_comprehensive = get_total_durations(activity)
    assert duration_efficient > 0
    assert duration_complete > 0
    assert duration_comprehensive > 0

    assert ice is None
    assert cwi is not None
    cwi_json = cwi.json_serialise()
    assert cwi_json['minutes'] == 10


def test_get_responsive_recovery_with_simple_session_one_symptom_low_rpe():
    session_types = [6]
    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [SportName.distance_running]
    workout_programs = [None]

    sessions = get_sessions(session_types, dates, rpes, durations, sport_names, workout_programs)
    symptoms = get_symptoms(body_parts=[
        (7, 1, None, None, None, 2)  # left knee sharp=2
    ])

    activity, ice, cwi = get_activity(dates[0], symptoms, sessions, 'responsive_recovery')
    print("\nactive_rest, 100 mins run, low rpe (ice vs cwi), knee sharp=2")
    assert len(activity) == 1
    activity = activity[0]
    assert activity.type == ModalityType.post_active_rest
    assert activity.display_image == "static_stretch"
    assert activity.when == "anytime, up to 3 per day"
    assert activity.locked_text == "Mobility Workout missed. Tap + to create another."
    assert activity.title == "Mobility".upper()

    exercise_phases = activity.exercise_phases
    assert len(exercise_phases) == 4
    assert exercise_phases[0].type == ExercisePhaseType.inhibit
    assert exercise_phases[1].type == ExercisePhaseType.static_stretch
    assert exercise_phases[2].type == ExercisePhaseType.isolated_activate
    assert exercise_phases[3].type == ExercisePhaseType.static_integrate

    duration_efficient, duration_complete, duration_comprehensive = get_total_durations(activity)
    assert duration_efficient > 0
    assert duration_complete > 0
    assert duration_comprehensive > 0

    assert ice is not None
    assert cwi is None

    ice_json = ice.json_serialise()
    assert len(ice_json['body_parts']) == 1


def test_get_movement_prep_with_simple_session_no_symptoms():
    session_types = [6]
    dates = [datetime.now()]
    rpes = [7]
    durations = [100]
    sport_names = [SportName.distance_running]
    workout_programs = [None]

    sessions = get_sessions(session_types, dates, rpes, durations, sport_names, workout_programs)
    symptoms = []

    print("\nmovement prep, 100 mins weightlifting, no symptoms")
    movement_prep = get_activity(dates[0], symptoms, sessions, 'movement_prep')[0]
    assert movement_prep.type == ModalityType.movement_integration_prep
    assert len(movement_prep.exercise_phases[0].exercises) > 0  # make sure there's something in inhibit

    duration_efficient, duration_complete, duration_comprehensive = get_total_durations(movement_prep)
    assert duration_efficient > 0
    assert duration_complete > 0
    assert duration_comprehensive > 0


def test_get_movement_prep_with_mixed_activity_session_one_symptom():
    session_types = [7]
    dates = [datetime.now()]
    rpes = [5]
    durations = [100]
    sport_names = [None]
    sections = {
                   "Warmup / Movement Prep": ['rowing'],
                   'Stamina': ['med_ball_chest_pass', 'explosive_burpee'],
                   'Strength': ['dumbbell_bench_press', 'bent_over_row'],
                   'Recovery Protocol': ['indoor_cycle']
    }
    workout_programs = [get_workout_program(sections=sections)]

    sessions = get_sessions(session_types, dates, rpes, durations, sport_names, workout_programs)
    symptoms = get_symptoms(body_parts=[(7, 1, None, None, None, 2)])  # left knee sharp=2

    print("\nmovement prep, mixed activity session, knee sharp")
    movement_prep = get_activity(dates[0], symptoms, sessions, 'movement_prep')[0]
    assert movement_prep.display_image == "dynamic_flexibility"
    assert movement_prep.when == "before training"
    assert movement_prep.locked_text == "You skipped this Movement Prep before your Workout."
    assert movement_prep.title == "Movement Prep".upper()

    # assert len(movement_prep.exercise_phases[0].exercises) > 0  # make sure there's something in inhibit

    duration_efficient, duration_complete, duration_comprehensive = get_total_durations(movement_prep)
    assert duration_efficient > 0
    assert duration_complete > 0
    assert duration_comprehensive > 0