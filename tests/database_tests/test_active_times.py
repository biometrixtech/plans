import pytest
from models.session import SportTrainingSession, MixedActivitySession
from datetime import datetime, date, time
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


class TestParameters(object):
    def __init__(self, file_name, high_load, no_symptom=False, simple_session=True, symptoms=1):
        self.file_name = file_name
        self.high_load = high_load
        self.no_symptom = no_symptom
        self.symptoms = symptoms
        self.simple_session = simple_session


def get_test_parameters_list():

    parm_list = []

    parm_list.append(TestParameters("active_rest",  no_symptom=False, high_load=True))
    parm_list.append(TestParameters("active_rest",  no_symptom=False, high_load=True, symptoms=2))
    parm_list.append(TestParameters("active_rest",  no_symptom=False, high_load=True, simple_session=False))
    parm_list.append(TestParameters("active_rest",  no_symptom=False, high_load=True, simple_session=False, symptoms=2))
    parm_list.append(TestParameters("movement_integration_prep",  no_symptom=False, high_load=True))
    parm_list.append(TestParameters("movement_integration_prep",  no_symptom=False, high_load=True, symptoms=2))
    parm_list.append(TestParameters("movement_integration_prep",  no_symptom=False, high_load=True, simple_session=False))
    parm_list.append(TestParameters("movement_integration_prep",  no_symptom=False, high_load=True, simple_session=False, symptoms=2))
    return parm_list


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
            "rpe": rpe
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


def get_session(session_type, current_date_time, rpe=7, duration=100, sport_name=SportName.weightlifting):

    if session_type == 7:
        session = MixedActivitySession()
        sections = {
                       "Warmup / Movement Prep": ['rowing'],
                       'Stamina': ['med_ball_chest_pass', 'explosive_burpee'],
                       'Strength': ['dumbbell_bench_press', 'bent_over_row'],
                       'Recovery Protocol': ['indoor_cycle']
        }
        session.workout_program_module = get_workout_program(sections)
    else:
        session = SportTrainingSession()
        session.sport_name = sport_name
    session.event_date = current_date_time
    session.session_RPE = rpe
    session.duration_minutes = duration

    return session


def get_ex_assigned_details(activity):
    total_duration_efficient = 0
    total_duration_complete = 0
    total_duration_comprehensive = 0
    total_exercises = 0
    phase_lines = {
        'inhibit': ",,,",
        'static_stretch': ",,,",
        'active_stretch': ",,,",
        'dynamic_stretch': ",,,",
        'isolated_activate': ",,,",
        'static_integrate': ",,,",
        'dynamic_integrate': ",,,"
    }
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
            phase_exercises = ";".join(list(ex_phase.exercises.keys()))
            # print(f"{phase_name}: exercises assigned: {ex_count_phase}, durations: efficient: {round(duration_efficient_phase / 60, 2)}, "
            #       f"complete: {round(duration_complete_phase / 60, 2)}, comprehensive: {round(duration_comprehensive_phase / 60, 2)}")
            phase_lines[phase_name] = f"{phase_exercises},{round(duration_efficient_phase / 60, 2)},{round(duration_complete_phase / 60, 2)},{round(duration_comprehensive_phase / 60, 2)}"
            total_duration_efficient += duration_efficient_phase
            total_duration_complete += duration_complete_phase
            total_duration_comprehensive += duration_comprehensive_phase
            total_exercises += ex_count_phase
        else:
            phase_lines[phase_name] = "None,0,0,0"

    total_duration_efficient = round(total_duration_efficient / 60, 2)
    total_duration_complete = round(total_duration_complete / 60, 2)
    total_duration_comprehensive = round(total_duration_comprehensive / 60, 2)
    total_line = f"{total_exercises}, {total_duration_efficient}, {total_duration_complete}, {total_duration_comprehensive}"
    ex_assignment_line = ",".join([total_line,
                                   phase_lines['inhibit'],
                                   phase_lines['static_stretch'],
                                   phase_lines['active_stretch'],
                                   phase_lines['dynamic_stretch'],
                                   phase_lines['isolated_activate'],
                                   phase_lines['static_integrate'],
                                   phase_lines['dynamic_integrate']
                                   ]
                                  )
    return ex_assignment_line


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
        modality, ice, cwi = calc.get_responsive_recovery(sessions[0].id, force_on_demand=True)
        return modality, ice, cwi


def get_body_part_string(symptoms):
    ret = ""
    for symptom in symptoms:
        ret += f"({symptom.body_part.location.name};{symptom.tight};{symptom.knots};{symptom.ache};{symptom.sharp})"
    return ret


def get_session_line(session):
    if session.session_type().value == 6:
        session_type = 'simple'
    else:
        session_type = 'mixed'
    return f"{session_type},{session.sport_name.name},{session.is_cardio_plyometrics()},{session.ultra_high_intensity_session() and session.high_intensity_RPE()}"

def test_generate_spreadsheets():

    current_date = date.today()
    current_date_time = datetime.combine(current_date, time(9, 0, 0))

    parm_list = get_test_parameters_list()

    line = ('(BodyPart;tight;knots;ache;sharp),session_type,sport_name,cardio_plyometric,ultra_high_intensity,'+
            'total_exercises,duration_efficient,duration_complete,duration_comprehensive,' +
            'inhibit_exercises,inhibit_minutes_efficient,inhibit_minutes_complete,inhibit_minutes_comprehensive,'+
            'static_stretch_exercises,static_stretch_minutes_efficient,static_stretch_minutes_complete,static_stretch_minutes_comprehensive,'+
            'active_stretch_exercises,active_stretch_minutes_efficient,active_stretch_minutes_complete,active_stretch_minutes_comprehensive,'+
            'dynamic_stretch_exercises,dynamic_stretch_minutes_efficient,dynamic_stretch_minutes_complete,dynamic_stretch_minutes_comprehensive,'+
            'isolated_activate_exercises,isolated_activate_minutes_efficient,isolated_activate_minutes_complete,isolated_activate_minutes_comprehensive,'+
            'static_integrate_exercises,static_integrate_minutes_efficient,static_integrate_minutes_complete,static_integrate_minutes_comprehensive,'+
            'dynamic_integrate_exercises,dynamic_integrate_minutes_efficient,dynamic_integrate_minutes_complete,dynamic_integrate_minutes_comprehensive'
            )

    active_rest_file = open("../../output/active_rest.csv", 'w')
    active_rest_file.write(line + '\n')

    movement_integration_prep_file = open("../../output/movement_integration_prep.csv", 'w')
    movement_integration_prep_file.write(line + '\n')

    possible_symptoms = [('sharp',), ('knots', 'sharp'), ('tight', 'ache')]
    body_parts = [2, 4, 5, 6, 7, 8, 11, 14, 15, 16]
    for test_param in parm_list:
        if test_param.high_load:
            if test_param.simple_session:
                session_type = 6
                training_sessions = [get_session(session_type, current_date_time), get_session(session_type, current_date_time, sport_name=SportName.distance_running)]
            else:
                session_type = 7
                training_sessions = [get_session(session_type, current_date_time)]
        else:
            session_line = ",,"
            training_sessions = []
        if test_param.no_symptom:
            pass
            # symptoms = []
            # active_rest = get_activity(current_date_time, symptoms, training_sessions, 'mobility_wod')[0]
            # ar_line = get_total_durations(active_rest)
            # line = f",{session_line},{ar_line}\n"
            # if test_param.file_name == 'active_rest':
            #     active_rest_file.write(line)
            # elif test_param.file_name == 'movement_integration_prep':
            #     movement_integration_prep_file.write(line)
        else:
            for session in training_sessions:
                sessions = [session]
                session_line = get_session_line(session)
                if test_param.symptoms == 1:
                    for body_part in body_parts:
                        for severity in [1, 3, 5, 7]:
                            for possible_symptom in possible_symptoms:
                                symptoms = get_symptoms(body_parts=[(body_part, 1, None, None, None, None)])
                                for symptom in symptoms:
                                    for symptom_name in possible_symptom:
                                        symptom.__setattr__(symptom_name, severity)
                                if test_param.file_name == 'active_rest':
                                    active_rest = get_activity(current_date_time, symptoms, sessions, 'mobility_wod')[0]
                                    ar_line = get_ex_assigned_details(active_rest)
                                    line = f"{get_body_part_string(symptoms)},{session_line},{ar_line}\n"
                                    active_rest_file.write(line)
                                elif test_param.file_name == 'movement_integration_prep':
                                    movement_integration_prep = get_activity(current_date_time, symptoms, sessions, 'movement_prep')[0]
                                    mi_prep_line = get_ex_assigned_details(movement_integration_prep)
                                    line = f"{get_body_part_string(symptoms)},{session_line},{mi_prep_line}\n"
                                    movement_integration_prep_file.write(line)
                elif test_param.symptoms == 2:
                    body_parts_pairs = [(7, 6), (5, 12), (4, 14), (11, 15), (16, 8)]
                    for body_part_pair in body_parts_pairs:
                        for severity in [1, 3, 5, 7]:
                            for possible_symptom in possible_symptoms:
                                symptoms = get_symptoms(body_parts=[(body_part_pair[0], 1, None, None, None, None),
                                                                    (body_part_pair[1], 1, None, None, None, None)])
                                for symptom in symptoms:
                                    for symptom_name in possible_symptom:
                                        symptom.__setattr__(symptom_name, severity)
                                if test_param.file_name == 'active_rest':
                                    active_rest = get_activity(current_date_time, symptoms, sessions, 'mobility_wod')[0]
                                    ar_line = get_ex_assigned_details(active_rest)
                                    line = f"{get_body_part_string(symptoms)},{session_line},{ar_line}\n"
                                    active_rest_file.write(line)
                                elif test_param.file_name == 'movement_integration_prep':
                                    movement_integration_prep = get_activity(current_date_time, symptoms, sessions, 'movement_prep')[0]
                                    mi_prep_line = get_ex_assigned_details(movement_integration_prep)
                                    line = f"{get_body_part_string(symptoms)},{session_line},{mi_prep_line}\n"
                                    movement_integration_prep_file.write(line)
    active_rest_file.close()
    movement_integration_prep_file.close()
