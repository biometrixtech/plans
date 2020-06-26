import os, json, pytest
import datetime
from logic.workout_processing import WorkoutProcessor
from logic.injury_risk_processing import InjuryRiskProcessor
from logic.exercise_assignment import ExerciseAssignment
from models.workout_program import WorkoutProgramModule
from models.planned_exercise import PlannedWorkout, PlannedWorkoutSection, PlannedExercise
from models.session import MixedActivitySession, PlannedSession
from models.training_volume import Assignment
from models.sport import SportName
from models.user_stats import UserStats
from logic.api_processing import APIProcessing
from tests.mocks.mock_exercise_datastore import ExerciseLibraryDatastore
from tests.mocks.mock_completed_exercise_datastore import CompletedExerciseDatastore
from tests.mocks.mock_workout_datastore import WorkoutDatastore
from tests.mocks.mock_datastore_collection import DatastoreCollection
from database.OTF_calculator import OTFCalculator

exercise_library_datastore = ExerciseLibraryDatastore()
completed_exercise_datastore = CompletedExerciseDatastore()


# TODO: have this work with the planned_exercise models
# TODO: update plans logic and related to handle "planned load" vs actual

@pytest.fixture(scope="session", autouse=True)
def load_exercises():
    exercise_library_datastore.side_load_exericse_list_from_csv()


def read_json(file_name):
    if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
        file_name = f"tests/data/otf/{file_name}.json"
    else:
        file_name = os.path.join(os.path.realpath(".."), f"data/otf/{file_name}.json")
    with open(file_name, 'r') as f:
        workout = json.load(f)
    return workout


# def get_workout_program(file_name):
#     workout_json = read_json(file_name)
#     workout_program_module = WorkoutProgramModule.json_deserialise(workout_json)
#     WorkoutProcessor().process_workout(workout_program_module)
#     return workout_program_module


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


def get_workout(date, file_name):
    planned_session = PlannedSession()
    planned_session.event_date = date
    workout_json = read_json(file_name)
    # workout_program_module = WorkoutProgramModule.json_deserialise(workout_json)
    planned_workout = PlannedWorkout.json_deserialise(workout_json)
    planned_session.workout = planned_workout

    return planned_session

def get_session(date, rpe=5, duration=60, file_name=None, assignment_type='default'):
    # session = MixedActivitySession()
    # session.event_date = date
    # session.session_RPE = rpe
    # session.duration_minutes = duration
    # session.sport_name = SportName.high_intensity_interval_training

    planned_session = PlannedSession()
    planned_session.event_date = date
    workout_json = read_json(file_name)
    #workout_program_module = WorkoutProgramModule.json_deserialise(workout_json)
    planned_workout = PlannedWorkout.json_deserialise(workout_json)
    planned_session.workout = planned_workout
    WorkoutProcessor(user_weight=60).process_planned_workout(planned_session, assignment_type)

    return planned_session


def get_session_2(date, rpe=5, duration=60, file_name=None, assignment_type='default'):
    session = MixedActivitySession()
    session.event_date = date
    session.session_RPE = rpe
    session.duration_minutes = duration
    session.sport_name = SportName.high_intensity_interval_training

    workout_json = read_json(file_name)
    workout_program_module = WorkoutProgramModule.json_deserialise(workout_json)
    session.workout_program_module = workout_program_module
    WorkoutProcessor(user_weight=60).process_workout(session)

    return session

def get_activity(event_date_time, symptoms, sessions):
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
    calc.sport_cardio_plyometrics = check_cardio_sport(sessions)
    calc.sport_body_parts = get_sport_body_parts(sessions)
    movement_prep = calc.get_movement_integration_prep(force_on_demand=True)
    return movement_prep


def test_may1():
    session_power_walker = get_session(datetime.datetime.now(), file_name='may1_alt', assignment_type='power_walker')
    session_runner = get_session(datetime.datetime.now(), file_name='may1_alt', assignment_type='runner')
    session_jogger = get_session(datetime.datetime.now(), file_name='may1_alt', assignment_type='jogger')
    #session = get_session(datetime.datetime.now(), file_name='may1_alt')

    movement_prep_power_walker = get_activity(datetime.datetime.now(), [], [session_power_walker])
    movement_prep_runner = get_activity(datetime.datetime.now(), [], [session_runner])
    movement_prep_jogger = get_activity(datetime.datetime.now(), [], [session_jogger])
    assigned_exercises = {}
    for ex_phase in movement_prep_power_walker[0].exercise_phases:
        assigned_exercises[ex_phase.name] = list(ex_phase.exercises.keys())
    print('here')


def get_treadmill_exercise(exercise_id, exercise_name, duration_assignment, grade_assignment):

    planned_exercise = PlannedExercise()
    planned_exercise.name = exercise_name
    planned_exercise.id = exercise_id

    planned_exercise.duration = duration_assignment

    planned_exercise.grade = grade_assignment

    return  planned_exercise


def get_rowing_exercise(exercise_id, exercise_name, duration_assignment, stroke_rate):

    planned_exercise = PlannedExercise()
    planned_exercise.name = exercise_name
    planned_exercise.id = exercise_id

    planned_exercise.duration = duration_assignment

    planned_exercise.stroke_rate = stroke_rate

    return  planned_exercise

def test_walking():

    otf_calc = OTFCalculator()

    jogging = get_treadmill_exercise("walk", "walk", Assignment(assigned_value=60.00, min_value='', max_value=''),
                                     Assignment(assigned_value=.01))
    jogging.movement_id = "5823768d473c06100052ed9a"
    jogging.speed = Assignment(assigned_value=1.65)

    running = get_treadmill_exercise("walk", "walk", Assignment(assigned_value=60.00, min_value='', max_value=''),
                                     Assignment(assigned_value=.01))
    running.movement_id = "5823768d473c06100052ed9a"
    running.speed = Assignment(assigned_value=1.65)

    power_walking = get_treadmill_exercise("walk", "walk", Assignment(assignment_type=None, assigned_value=60.00, min_value='', max_value=''),
                                              otf_calc.get_grade("power_walker", "base", 0))
    power_walking.movement_id = "5823768d473c06100052ed9a"
    power_walking.speed = Assignment(assigned_value=1.65)

    workout_processor = WorkoutProcessor()

    workout_processor.add_movement_detail_to_planned_exercise(jogging, "jogger")
    workout_processor.add_movement_detail_to_planned_exercise(power_walking, "power_walker")
    workout_processor.add_movement_detail_to_planned_exercise(running, "runner")

    assert jogging.power.observed_value == running.power.observed_value < power_walking.power.observed_value
    assert power_walking.power.lower_bound < power_walking.power.observed_value < power_walking.power.upper_bound


def test_running():

    otf_calc = OTFCalculator()

    movement_id = "5823768d473c06100052ed9a"

    duration_assignment = Assignment(assigned_value=60.00, min_value='', max_value='')
    grade_assignment = Assignment(assigned_value=0.0)

    jogging = get_treadmill_exercise("run", "run", duration_assignment, grade_assignment)
    jogging.movement_id = movement_id
    jogging.pace = otf_calc.get_pace("jogger", "base")

    running = get_treadmill_exercise("run", "run", duration_assignment, grade_assignment)
    running.movement_id = movement_id
    running.pace = otf_calc.get_pace("runner", "base")

    power_walking = get_treadmill_exercise("run", "run",
                                           duration_assignment, grade_assignment)
    power_walking.movement_id = movement_id
    power_walking.pace = otf_calc.get_pace("power_walker", "base")

    workout_processor = WorkoutProcessor()

    workout_processor.add_movement_detail_to_planned_exercise(jogging, "jogger")
    workout_processor.add_movement_detail_to_planned_exercise(power_walking, "power_walker")
    workout_processor.add_movement_detail_to_planned_exercise(running, "runner")

    assert power_walking.power.lower_bound < jogging.power.lower_bound < running.power.lower_bound
    assert power_walking.power.observed_value < jogging.power.observed_value < running.power.observed_value
    assert power_walking.power.upper_bound < jogging.power.upper_bound < running.power.upper_bound


def test_running_diff_inclines():

    otf_calc = OTFCalculator()

    movement_id = "5823768d473c06100052ed9a"

    duration_assignment = Assignment(assigned_value=90.00, min_value='', max_value='')
    base_grade_assignment = Assignment(assigned_value=.06)
    power_walker_grade_assignment = Assignment(min_value=.08, max_value=.15)

    jogging = get_treadmill_exercise("run", "run", duration_assignment, base_grade_assignment)
    jogging.movement_id = movement_id
    jogging.pace = otf_calc.get_pace("jogger", "base")

    running = get_treadmill_exercise("run", "run", duration_assignment, base_grade_assignment)
    running.movement_id = movement_id
    running.pace = otf_calc.get_pace("runner", "base")

    power_walking = get_treadmill_exercise("run", "run",
                                           duration_assignment, power_walker_grade_assignment)
    power_walking.movement_id = movement_id
    power_walking.pace = otf_calc.get_pace("power_walker", "base")

    workout_processor = WorkoutProcessor()

    workout_processor.add_movement_detail_to_planned_exercise(jogging, "jogger")
    workout_processor.add_movement_detail_to_planned_exercise(power_walking, "power_walker")
    workout_processor.add_movement_detail_to_planned_exercise(running, "runner")

    assert power_walking.power.lower_bound < jogging.power.lower_bound < running.power.lower_bound
    assert power_walking.power.observed_value < jogging.power.observed_value < running.power.observed_value
    assert power_walking.power.upper_bound > jogging.power.upper_bound < running.power.upper_bound


def test_rowing():

    activity_name = "row"
    movement_id = "58459d9ddc2ce90011f93d84"
    duration = 180.0
    duration_assignment = Assignment(assigned_value=duration, min_value='', max_value='')
    jogging = get_rowing_exercise(activity_name, activity_name, duration_assignment, 24)
    jogging.movement_id = movement_id

    running = get_rowing_exercise(activity_name, activity_name, duration_assignment, 24)
    running.movement_id = movement_id

    power_walking = get_rowing_exercise(activity_name, activity_name, duration_assignment, 24)
    power_walking.movement_id = movement_id

    workout_processor = WorkoutProcessor()

    workout_processor.add_movement_detail_to_planned_exercise(jogging, "jogger")
    workout_processor.add_movement_detail_to_planned_exercise(power_walking, "power_walker")
    workout_processor.add_movement_detail_to_planned_exercise(running, "runner")

    assert power_walking.power.lower_bound == jogging.power.lower_bound == running.power.lower_bound
    assert power_walking.power.observed_value == jogging.power.observed_value == running.power.observed_value
    assert power_walking.power.upper_bound == jogging.power.upper_bound == running.power.upper_bound


def test_api_movement_prep_compare_exercise_counts():
    mock_datastore_collection = DatastoreCollection()
    workout_datastore = WorkoutDatastore()

    workout = get_workout(datetime.datetime.now(), file_name='may1_alt')
    workout_datastore.side_load_planned_workout(workout)
    mock_datastore_collection.workout_datastore = workout_datastore
    mock_datastore_collection.exercise_datastore = exercise_library_datastore

    user_stats = UserStats("tester")
    user_stats.fitness_provider_cardio_profile = "power_walker"
    user_stats.athlete_weight = 70
    user_stats.event_date = datetime.datetime.now()

    api_processing = APIProcessing("tester", datetime.datetime.now(), user_stats=user_stats,
                                   datastore_collection=mock_datastore_collection)
    api_processing.create_planned_workout_from_id("1")

    movement_prep = api_processing.create_activity(activity_type='movement_prep', planned_session=workout)

    mock_datastore_collection_2 = DatastoreCollection()
    workout_datastore_2 = WorkoutDatastore()
    workout_2 = get_workout(datetime.datetime.now(), file_name='may1_alt')
    workout_datastore_2.side_load_planned_workout(workout_2)
    mock_datastore_collection_2.workout_datastore = workout_datastore_2
    mock_datastore_collection_2.exercise_datastore = exercise_library_datastore

    user_stats_2 = UserStats("tester")
    user_stats_2.fitness_provider_cardio_profile = "jogger"
    user_stats_2.athlete_weight = 70
    user_stats_2.event_date = datetime.datetime.now()

    api_processing_2 = APIProcessing("tester", datetime.datetime.now(), user_stats=user_stats_2,
                                     datastore_collection=mock_datastore_collection_2)
    api_processing_2.create_planned_workout_from_id("1")

    movement_prep_2 = api_processing_2.create_activity(activity_type='movement_prep', planned_session=workout_2)

    mock_datastore_collection_3 = DatastoreCollection()
    workout_datastore_3 = WorkoutDatastore()
    workout_3 = get_workout(datetime.datetime.now(), file_name='may1_alt')
    workout_datastore_3.side_load_planned_workout(workout_3)
    mock_datastore_collection_3.workout_datastore = workout_datastore_3
    mock_datastore_collection_3.exercise_datastore = exercise_library_datastore

    user_stats_3 = UserStats("tester")
    user_stats_3.fitness_provider_cardio_profile = "runner"
    user_stats_3.athlete_weight = 70
    user_stats_3.event_date = datetime.datetime.now()

    api_processing_3 = APIProcessing("tester", datetime.datetime.now(), user_stats=user_stats_3,
                                     datastore_collection=mock_datastore_collection_3)
    api_processing_3.create_planned_workout_from_id("1")

    movement_prep_3 = api_processing_3.create_activity(activity_type='movement_prep', planned_session=workout_3)

    inhibit_1_exercise_count = len(movement_prep.movement_integration_prep.exercise_phases[0].exercises)
    inhibit_2_exercise_count = len(movement_prep_2.movement_integration_prep.exercise_phases[0].exercises)
    inhibit_3_exercise_count = len(movement_prep_3.movement_integration_prep.exercise_phases[0].exercises)

    static_stretch_1_exercise_count = len(movement_prep.movement_integration_prep.exercise_phases[1].exercises)
    static_stretch_2_exercise_count = len(movement_prep_2.movement_integration_prep.exercise_phases[1].exercises)
    static_stretch_3_exercise_count = len(movement_prep_3.movement_integration_prep.exercise_phases[1].exercises)

    active_stretch_1_exercise_count = len(movement_prep.movement_integration_prep.exercise_phases[2].exercises)
    active_stretch_2_exercise_count = len(movement_prep_2.movement_integration_prep.exercise_phases[2].exercises)
    active_stretch_3_exercise_count = len(movement_prep_3.movement_integration_prep.exercise_phases[2].exercises)

    dynamic_stretch_1_exercise_count = len(movement_prep.movement_integration_prep.exercise_phases[3].exercises)
    dynamic_stretch_2_exercise_count = len(movement_prep_2.movement_integration_prep.exercise_phases[3].exercises)
    dynamic_stretch_3_exercise_count = len(movement_prep_3.movement_integration_prep.exercise_phases[3].exercises)

    isolated_activate_1_exercise_count = len(movement_prep.movement_integration_prep.exercise_phases[4].exercises)
    isolated_activate_2_exercise_count = len(movement_prep_2.movement_integration_prep.exercise_phases[4].exercises)
    isolated_activate_3_exercise_count = len(movement_prep_3.movement_integration_prep.exercise_phases[4].exercises)

    static_integrate_1_exercise_count = len(movement_prep.movement_integration_prep.exercise_phases[5].exercises)
    static_integrate_2_exercise_count = len(movement_prep_2.movement_integration_prep.exercise_phases[5].exercises)
    static_integrate_3_exercise_count = len(movement_prep_3.movement_integration_prep.exercise_phases[5].exercises)

    dynamic_integrate_1_exercise_count = len(movement_prep.movement_integration_prep.exercise_phases[6].exercises)
    dynamic_integrate_2_exercise_count = len(movement_prep_2.movement_integration_prep.exercise_phases[6].exercises)
    dynamic_integrate_3_exercise_count = len(movement_prep_3.movement_integration_prep.exercise_phases[6].exercises)

    assert 0 < inhibit_1_exercise_count
    assert 0 < inhibit_2_exercise_count
    assert 0 < inhibit_3_exercise_count
    assert 0 == static_stretch_1_exercise_count
    assert 0 == static_stretch_2_exercise_count
    assert 0 == static_stretch_3_exercise_count
    assert 0 < active_stretch_1_exercise_count
    assert 0 < active_stretch_2_exercise_count
    assert 0 < active_stretch_3_exercise_count
    assert 0 == dynamic_stretch_1_exercise_count
    assert 0 == dynamic_stretch_2_exercise_count
    assert 0 == dynamic_stretch_3_exercise_count
    assert 0 < isolated_activate_1_exercise_count
    assert 0 < isolated_activate_2_exercise_count
    assert 0 < isolated_activate_3_exercise_count
    assert 0 == static_integrate_1_exercise_count
    assert 0 == static_integrate_2_exercise_count
    assert 0 == static_integrate_3_exercise_count
    assert 0 == dynamic_integrate_1_exercise_count
    assert 0 == dynamic_integrate_2_exercise_count
    assert 0 == dynamic_integrate_3_exercise_count


def test_api_movement_prep_compare_volume_may1_alt():

    mock_datastore_collection = DatastoreCollection()
    workout_datastore = WorkoutDatastore()

    workout = get_workout(datetime.datetime.now(), file_name='may1_alt')
    workout_datastore.side_load_planned_workout(workout)
    mock_datastore_collection.workout_datastore = workout_datastore
    mock_datastore_collection.exercise_datastore = exercise_library_datastore

    user_stats = UserStats("tester")
    user_stats.fitness_provider_cardio_profile = "power_walker"
    user_stats.athlete_weight = 70
    user_stats.event_date = datetime.datetime.now()

    api_processing = APIProcessing("tester", datetime.datetime.now(),user_stats=user_stats,
                                   datastore_collection=mock_datastore_collection)
    api_processing.create_planned_workout_from_id("1")

    movement_prep = api_processing.create_activity(activity_type='movement_prep', planned_session=workout)
    injury_risk_dict_1 = api_processing.activity_manager.exercise_assignment_calculator.injury_risk_dict

    total_concentric_volume_1_lower_bound = 0
    total_concentric_volume_1_observed = 0
    total_concentric_volume_1_upper_bound = 0

    for body_part_side, body_part_injury_risk in injury_risk_dict_1.items():
        total_concentric_volume_1_lower_bound += body_part_injury_risk.concentric_volume_today.lower_bound
        total_concentric_volume_1_observed += body_part_injury_risk.concentric_volume_today.observed_value
        total_concentric_volume_1_upper_bound += body_part_injury_risk.concentric_volume_today.upper_bound

    mock_datastore_collection_2 = DatastoreCollection()
    workout_datastore_2 = WorkoutDatastore()
    workout_2 = get_workout(datetime.datetime.now(), file_name='may1_alt')
    workout_datastore_2.side_load_planned_workout(workout_2)
    mock_datastore_collection_2.workout_datastore = workout_datastore_2
    mock_datastore_collection_2.exercise_datastore = exercise_library_datastore

    user_stats_2 = UserStats("tester")
    user_stats_2.fitness_provider_cardio_profile = "jogger"
    user_stats_2.athlete_weight = 70
    user_stats_2.event_date = datetime.datetime.now()

    api_processing_2 = APIProcessing("tester", datetime.datetime.now(),user_stats=user_stats_2,
                                   datastore_collection=mock_datastore_collection_2)
    api_processing_2.create_planned_workout_from_id("1")

    movement_prep_2 = api_processing_2.create_activity(activity_type='movement_prep', planned_session=workout_2)
    injury_risk_dict_2 = api_processing_2.activity_manager.exercise_assignment_calculator.injury_risk_dict

    total_concentric_volume_2_lower_bound = 0
    total_concentric_volume_2_observed = 0
    total_concentric_volume_2_upper_bound = 0

    for body_part_side, body_part_injury_risk in injury_risk_dict_2.items():
        total_concentric_volume_2_lower_bound += body_part_injury_risk.concentric_volume_today.lower_bound
        total_concentric_volume_2_observed += body_part_injury_risk.concentric_volume_today.observed_value
        total_concentric_volume_2_upper_bound += body_part_injury_risk.concentric_volume_today.upper_bound

    mock_datastore_collection_3 = DatastoreCollection()
    workout_datastore_3 = WorkoutDatastore()
    workout_3 = get_workout(datetime.datetime.now(), file_name='may1_alt')
    workout_datastore_3.side_load_planned_workout(workout_3)
    mock_datastore_collection_3.workout_datastore = workout_datastore_3
    mock_datastore_collection_3.exercise_datastore = exercise_library_datastore

    user_stats_3 = UserStats("tester")
    user_stats_3.fitness_provider_cardio_profile = "runner"
    user_stats_3.athlete_weight = 70
    user_stats_3.event_date = datetime.datetime.now()

    api_processing_3 = APIProcessing("tester", datetime.datetime.now(),user_stats=user_stats_3,
                                   datastore_collection=mock_datastore_collection_3)
    api_processing_3.create_planned_workout_from_id("1")

    movement_prep_3 = api_processing_3.create_activity(activity_type='movement_prep', planned_session=workout_3)
    injury_risk_dict_3 = api_processing_3.activity_manager.exercise_assignment_calculator.injury_risk_dict

    total_concentric_volume_3_lower_bound = 0
    total_concentric_volume_3_observed = 0
    total_concentric_volume_3_upper_bound = 0

    for body_part_side, body_part_injury_risk in injury_risk_dict_3.items():
        total_concentric_volume_3_lower_bound += body_part_injury_risk.concentric_volume_today.lower_bound
        total_concentric_volume_3_observed += body_part_injury_risk.concentric_volume_today.observed_value
        total_concentric_volume_3_upper_bound += body_part_injury_risk.concentric_volume_today.upper_bound

    assert total_concentric_volume_1_lower_bound < total_concentric_volume_1_observed < total_concentric_volume_1_upper_bound
    assert total_concentric_volume_2_lower_bound < total_concentric_volume_2_observed < total_concentric_volume_2_upper_bound
    assert total_concentric_volume_3_lower_bound < total_concentric_volume_3_observed < total_concentric_volume_3_upper_bound
    assert total_concentric_volume_1_lower_bound < total_concentric_volume_2_lower_bound
    assert total_concentric_volume_2_lower_bound < total_concentric_volume_3_lower_bound
    assert total_concentric_volume_1_observed < total_concentric_volume_2_observed
    assert total_concentric_volume_2_observed < total_concentric_volume_3_observed
    assert total_concentric_volume_1_upper_bound < total_concentric_volume_2_upper_bound
    assert total_concentric_volume_2_upper_bound < total_concentric_volume_3_upper_bound

#
def test_may2():
    session = get_session_2(datetime.datetime.now(), file_name='may2')
    movement_prep = get_activity(datetime.datetime.now(), [], [session])
    assigned_exercises = {}
    for ex_phase in movement_prep[0].exercise_phases:
        assigned_exercises[ex_phase.name] = list(ex_phase.exercises.keys())
    print('here')


def test_may18():
    session = get_session_2(datetime.datetime.now(), file_name='may18')
    movement_prep = get_activity(datetime.datetime.now(), [], [session])
    assigned_exercises = {}
    for ex_phase in movement_prep[0].exercise_phases:
        assigned_exercises[ex_phase.name] = list(ex_phase.exercises.keys())
    print('here')
#
#
# def test_at_home1():
#     session = get_session(datetime.datetime.now(), file_name='at_home1')
#     movement_prep = get_activity(datetime.datetime.now(), [], [session])
#     assigned_exercises = {}
#     for ex_phase in movement_prep[0].exercise_phases:
#         assigned_exercises[ex_phase.name] = list(ex_phase.exercises.keys())
#     print('here')