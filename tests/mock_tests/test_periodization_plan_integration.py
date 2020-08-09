from models.session_functional_movement import SessionFunctionalMovement
from models.workout_program import WorkoutProgramModule
from models.session import MixedActivitySession, SportTrainingSession
from logic.workout_processing import WorkoutProcessor
from datetime import datetime, timedelta
from tests.mocks.mock_completed_session_details_datastore import CompletedSessionDetailsDatastore
from logic.periodization_processor import PeriodizationPlanProcessor
from models.periodization import PeriodizationPersona, PeriodizationGoal, TrainingPhaseType
from models.training_volume import StandardErrorRange


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
        # "rowing": get_exercise_json("2k Row", reps=90, reps_unit=0, movement_id="58459d9ddc2ce90011f93d84", rpe=6,
        #                             duration=30 * 60),
        "rowing": get_exercise_json("2k Row", reps=90, reps_unit=0, movement_id="58459d9ddc2ce90011f93d84", rpe=6),
        "cardio_rowing": get_exercise_json("Long Row", reps=1800, reps_unit=0, movement_id="58459d9ddc2ce90011f93d84",
                                           rpe=6),
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
            "Warmup / Movement Prep": ['rowing'],
            'Stamina': ['med_ball_chest_pass', 'explosive_burpee'],
            'Strength': ['dumbbell_bench_press', 'bent_over_row'],
            'Recovery Protocol': ['indoor_cycle']
        }
    elif reference_number==1:
        sections = {
            "Warmup / Movement Prep": ['rowing'],
            'Stamina': ['med_ball_chest_pass'],
            'Strength': ['dumbbell_bench_press'],
            'Recovery Protocol': ['indoor_cycle']
        }
    elif reference_number==2:
        sections = {
            "Warmup / Movement Prep": ['rowing'],
            'Stamina': ['explosive_burpee'],
            'Strength': ['bent_over_row'],
            'Recovery Protocol': ['indoor_cycle']
        }
    elif reference_number==3:
        sections = {
            "Warmup / Movement Prep": ['indoor_cycle'],
            'Strength': ['bent_over_row','indoor_cycle'],
            'Recovery Protocol': ['indoor_cycle']
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
            "Warmup / Movement Prep": ['indoor_cycle']
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

# def test_check_active_rest_phases_no_soreness_with_mixed_session():
#
#     session = MixedActivitySession()
#     session.event_date = datetime.now()
#
#     exercise_action_1 = ExerciseAction("1", "flail")
#     exercise_action_1.primary_muscle_action = MuscleAction.concentric
#     exercise_action_1.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
#     exercise_action_1.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
#     exercise_action_1.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
#     #exercise_action_1.tissue_load_left = StandardErrorRange(observed_value=100)
#     #exercise_action_1.tissue_load_right = StandardErrorRange(observed_value=200)
#     exercise_action_1.power_load_left = StandardErrorRange(observed_value=100)
#     exercise_action_1.power_load_right = StandardErrorRange(observed_value=200)
#     exercise_action_1.lower_body_stability_rating = 1.1
#     exercise_action_1.upper_body_stability_rating = 0.6
#     exercise_action_1.adaptation_type = AdaptationType.strength_endurance_strength
#     exercise_action_1.training_type = TrainingType.strength_cardiorespiratory
#
#     exercise_action_2 = ExerciseAction("1", "flail")
#     exercise_action_2.primary_muscle_action = MuscleAction.concentric
#     exercise_action_2.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
#     exercise_action_2.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
#     exercise_action_2.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
#     #exercise_action_2.tissue_load_left = StandardErrorRange(observed_value=200)
#     #exercise_action_2.tissue_load_right = StandardErrorRange(observed_value=100)
#     exercise_action_2.power_load_left = StandardErrorRange(observed_value=200)
#     exercise_action_2.power_load_right = StandardErrorRange(observed_value=100)
#     exercise_action_2.lower_body_stability_rating = 1.1
#     exercise_action_2.upper_body_stability_rating = 0.6
#     exercise_action_2.adaptation_type = AdaptationType.power_explosive_action
#     exercise_action_2.training_type = TrainingType.strength_cardiorespiratory
#
#     exercise_1 = WorkoutExercise()
#     exercise_1.rpe = StandardErrorRange(observed_value=5)
#     exercise_1.duration = 90
#     exercise_1.power_load = StandardErrorRange(observed_value=300)
#     exercise_1.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
#     exercise_1.primary_actions.append(exercise_action_1)
#
#     exercise_2 = WorkoutExercise()
#     exercise_2.rpe = StandardErrorRange(observed_value=5)
#     exercise_2.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
#     exercise_2.duration = 90
#     exercise_2.power_load = StandardErrorRange(observed_value=300)
#     exercise_2.primary_actions.append(exercise_action_2)
#
#     section_1 = WorkoutSection()
#     section_1.exercises.append(exercise_1)
#
#     section_2 = WorkoutSection()
#     section_2.exercises.append(exercise_2)
#
#     program_module = WorkoutProgramModule()
#     program_module.workout_sections.append(section_1)
#     program_module.workout_sections.append(section_2)
#
#     session.workout_program_module = program_module
#


def get_seven_day_completed_data_store():

    session_types = [7, 7, 7, 7, 7, 7, 7]
    sections = [0, 1, 2, 3, 4, 5, 2]

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

    durations = [100 * 60, 90 * 60, 80 * 60, 90 * 60, 95 * 60, 85 * 60, 105 * 60]
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


def test_7_days_completed_sessions_cardio_health():

    data_store = get_seven_day_completed_data_store()
    proc = PeriodizationPlanProcessor(datetime.now(), PeriodizationGoal.increase_cardiovascular_health,
                                      PeriodizationPersona.well_trained, TrainingPhaseType.increase, data_store, None)
    plan = proc.create_periodization_plan(datetime.now().date())

    assert plan.template_workout is not None


def test_7_days_completed_sessions_cardio_endurance():
    data_store = get_seven_day_completed_data_store()
    proc = PeriodizationPlanProcessor(datetime.now(), PeriodizationGoal.increase_cardio_endurance,
                                      PeriodizationPersona.well_trained, TrainingPhaseType.increase, data_store, None)
    plan = proc.create_periodization_plan(datetime.now().date())

    assert plan.template_workout is not None


def test_7_days_completed_sessions_cardio_endurance_with_speed():
    data_store = get_seven_day_completed_data_store()
    proc = PeriodizationPlanProcessor(datetime.now(), PeriodizationGoal.increase_cardio_endurance_with_speed,
                                      PeriodizationPersona.well_trained, TrainingPhaseType.increase, data_store, None)
    plan = proc.create_periodization_plan(datetime.now().date())

    assert plan.template_workout is not None

def test_7_days_completed_sessions_strength_max_strength():
    data_store = get_seven_day_completed_data_store()
    proc = PeriodizationPlanProcessor(datetime.now(), PeriodizationGoal.increase_strength_max_strength,
                                      PeriodizationPersona.well_trained, TrainingPhaseType.increase, data_store, None)
    plan = proc.create_periodization_plan(datetime.now().date())

    assert plan.template_workout is not None

#
# def test_aggregate_load_concentric():
#
#     exercise_action_1 = ExerciseAction("1", "flail")
#     exercise_action_1.primary_muscle_action = MuscleAction.concentric
#     exercise_action_1.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
#     exercise_action_1.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
#     exercise_action_1.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
#     #exercise_action_1.tissue_load_left = StandardErrorRange(observed_value=100)
#     #exercise_action_1.tissue_load_right = StandardErrorRange(observed_value=200)
#     exercise_action_1.power_load_left = StandardErrorRange(observed_value=100)
#     exercise_action_1.power_load_right = StandardErrorRange(observed_value=200)
#     exercise_action_1.lower_body_stability_rating = 1.1
#     exercise_action_1.upper_body_stability_rating = 0.6
#     exercise_action_1.adaptation_type = AdaptationType.strength_endurance_strength
#
#     exercise_action_2 = ExerciseAction("1", "flail")
#     exercise_action_2.primary_muscle_action = MuscleAction.concentric
#     exercise_action_2.hip_joint_action = [PrioritizedJointAction(1, FunctionalMovementType.hip_extension)]
#     exercise_action_2.knee_joint_action = [PrioritizedJointAction(2, FunctionalMovementType.knee_extension)]
#     exercise_action_2.ankle_joint_action = [PrioritizedJointAction(3, FunctionalMovementType.ankle_plantar_flexion)]
#     #exercise_action_2.tissue_load_left = StandardErrorRange(observed_value=200)
#     #exercise_action_2.tissue_load_right = StandardErrorRange(observed_value=100)
#     exercise_action_2.power_load_left = StandardErrorRange(observed_value=200)
#     exercise_action_2.power_load_right = StandardErrorRange(observed_value=100)
#     exercise_action_2.lower_body_stability_rating = 1.1
#     exercise_action_2.upper_body_stability_rating = 0.6
#     exercise_action_2.adaptation_type = AdaptationType.power_explosive_action
#
#     exercise_1 = WorkoutExercise()
#     exercise_1.weight_measure = WeightMeasure.actual_weight
#     exercise_1.weight = 100
#     exercise_1.reps_per_set = 5
#     exercise_1.power_load = StandardErrorRange(observed_value=300)
#     exercise_1.equipment = Equipment.dumbbells
#     exercise_1.primary_actions.append(exercise_action_1)
#     exercise_1.training_type = TrainingType.strength_integrated_resistance
#
#     exercise_2 = WorkoutExercise()
#     exercise_2.power_load = StandardErrorRange(observed_value=300)
#     exercise_2.primary_actions.append(exercise_action_2)
#     exercise_2.training_type = TrainingType.power_action_plyometrics
#
#     section_1 = WorkoutSection()
#     section_1.exercises.append(exercise_1)
#
#     section_2 = WorkoutSection()
#     section_2.exercises.append(exercise_2)
#
#     program_module = WorkoutProgramModule()
#     program_module.workout_sections.append(section_1)
#     program_module.workout_sections.append(section_2)
#
#     factory = FunctionalMovementFactory()
#     dict = factory.get_functional_movement_dictionary()
#
#     session_functional_movement = SessionFunctionalMovement(None, {})
#     session_functional_movement.completed_session_details = CompletedSessionDetails(datetime.now(), None, None)
#     load_dict = session_functional_movement.process_workout_load(program_module, datetime.now(), dict)