import database.september_demo.set_up_config
import os
import time
import json
import requests
from database.september_demo.demo_users import get_users
from database.september_demo.demo_persona import DemoPersona
from datastores.training_session_datastore import TrainingSessionDatastore
from datastores.user_stats_datastore import UserStatsDatastore
from datastores.planed_workout_load_datastore import PlannedWorkoutLoadDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.injury_risk_datastore import InjuryRiskDatastore
from models.periodization_plan import PeriodizationPlan, PeriodizationPersona, TrainingPhaseType
from models.periodization_goal import PeriodizationGoalFactory, PeriodizationGoalType, PeriodizationGoal
from models.athlete_capacity import TrainingPersona, SubAdaptionTypePersonas
from logic.periodization_processing import PeriodizationPlanProcessor
from logic.workout_scoring import WorkoutScoringProcessor
from logic.soreness_processing import SorenessCalculator
from database.september_demo.write_injury_risk_dict import InjuryRiskDictOutputProcessor
from database.september_demo.user_profiles import profiles
import pytz
import pandas as pd

from routes.responsive_recovery import get_responsive_recovery
from routes.mobility_wod import get_mobility_wod
from routes.movement_prep import get_movement_prep

utc = pytz.UTC

from aws_xray_sdk.core import xray_recorder

os.environ['ENVIRONMENT'] = 'dev'
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from database.september_demo.demo_persona import DemoPersona
from database.september_demo.get_workouts_for_persona import get_completed_workout
from utils import format_datetime, parse_datetime, parse_date, format_date
from datetime import datetime, timedelta

BASE_URL = f"https://apis.{os.getenv('ENVIRONMENT', 'dev')}.fathomai.com"
USERS_API_VERSION = os.getenv('USERS_API_VERSION', '2_4')
PLANS_API_VERSION = os.getenv('PLANS_API_VERSION', 'latest')

# USERS_URL = f"{BASE_URL}/users/{USERS_API_VERSION}"
PLANS_URL = f"{BASE_URL}/plans/{PLANS_API_VERSION}"


# user:
# USER = {'email': "dipesh+mvp@fathomai.com",
#         'id': None}
# Headers:
# HEADERS = {
#     "Authorization": None,
#     "Content-Type": "application/json"
#   }

# UPDATE this for correct series to look at
# data_series = 'aug-nov_2019'
# workouts_folder = f'workouts/{data_series}'

#
# def login_user(email):
#     body = {"password": "Fathom123!", "personal_data": {"email": email}}
#     url = f"{USERS_URL}/user/login"
#     response = requests.post(url, data=json.dumps(body), headers=HEADERS).json()
#     USER['id'] = response['user']['id']
#     print(USER['id'])
#     HEADERS['Authorization'] = response['authorization']['jwt']


def get_dates(days):
    dates = []
    today =  datetime.today()
    end_date = datetime(year=today.year, month=today.month, day=today.day)
    start_date = end_date - timedelta(days=days)


    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates


def login_user(email, password="Fathom123!"):
    body = {"password": password, "personal_data": {"email": email}}
    headers = {"Content-Type": "application/json"}
    url = "http://apis.{env}.fathomai.com/users/2_4/user/login".format(env=os.environ['ENVIRONMENT'])
    response = requests.post(url, data=json.dumps(body), headers=headers)
    return response.json()['user']['id'], response.json()['authorization']['jwt']


def submit_session_to_get_responsive_recovery(data, user_id, jwt, event_date_time, symptoms=None):
    # body = data
    # headers = {"Content-Type": "application/json", "Authorization": jwt}
    # response = requests.post(f"{PLANS_URL}/responsive_recovery/{user_id}",
    #                          headers=headers,
    #                          data=json.dumps(data))
    response = get_responsive_recovery(user_id, event_date_time, session=data, symptoms=symptoms)

    return response


def submit_mobility_wod_request(session_list, user_id, event_date_time, symptoms=None, user_age=20):
    response = get_mobility_wod(event_date_time, user_id, sessions=session_list, symptoms=symptoms, user_age=user_age)

    return response


def submit_movement_prep_request(session, user_id, event_date_time, program_module_id, symptoms=None):
    response = get_movement_prep(event_date_time, user_id, program_module_id, session=session, symptoms=symptoms)

    return response


def read_json(file_name, user_folder):
    file_name = f"workouts/{user_folder}/{file_name}"
    with open(file_name, 'r') as f:
        workout = json.load(f)
    return workout


def create_session(file_name, user_id, jwt, workout):
    # workout = read_json(file_name, user_name)
    data = {
        "user_age": 35,
        "event_date_time": workout['event_date_time'],
        "symptoms": [
        ],
        "session": {
            "event_date": workout['event_date_time'],
            "session_type": 7,
            "duration": workout['duration_seconds'] / 60,
            "description": workout['name'],
            # "calories": 100,
            "distance": workout['distance'],
            # "session_RPE": 7.3,
            "end_date": workout['workout_sections'][0]['end_date_time'],
            # "hr_data": {{hr_data}},
            "workout_program_module": workout
        }
    }
    return data


def create_session_only(workout, session_RPE):
    # workout = read_json(file_name, user_name)
    data = {
        "event_date": workout['event_date_time'],
        "session_type": 7,
        "duration": workout['duration_seconds'] / 60,
        "description": workout['name'],
        # "calories": 100,
        "distance": workout['distance'],
        "session_RPE": session_RPE,
        "end_date": workout['workout_sections'][0]['end_date_time'],
        # "hr_data": {{hr_data}},
        "workout_program_module": workout
    }
    return data


def get_if_present_string(obj, attribute):
    string_val = ""

    if getattr(obj, attribute) is not None:
        string_val += str(getattr(obj, attribute)) + ","
    else:
        string_val += ","

    return string_val


def get_std_error_if_present_string(obj, attribute, is_last=False):
    string_val = ""

    if getattr(obj, attribute) is not None:
        std_obj = getattr(obj, attribute)
        std_obj_val = std_obj.highest_value()
        string_val += str(std_obj_val)

    if not is_last:
        string_val += ","

    return string_val


def get_training_unit_if_present_string(obj, attribute, is_last=False):
    string_val = ""

    if getattr(obj, attribute) is not None:
        string_val += "RPE=" + str(getattr(obj, attribute).rpe.highest_value()) + ";Volume=" + str(getattr(obj, attribute).volume.highest_value())

    if not is_last:
        string_val += ","

    return string_val


def get_user_stats_string(user_stats):
    # user_stats_header_line = ("high_relative_load_sessions, high_relative_load_score, eligible_for_high_load_trigger," +
    #                           "expected_weekly_workouts, vo2_max, vo2_max_date_time, best_running_time, best_running_distance, best_running_date," +
    #                           "internal_ramp, internal_monotony, internal_strain, internal_strain_events, " +
    #                           "acute_internal_total_load, chronic_internal_total_load, internal_acwr, internal_freshness_index," +
    #                           "acute_days, chronic_days, total_historical_sessions, average_weekly_internal_load," +
    #                           "base_aerobic_training, anaerobic_threshold_training, high_intensity_anaerobic_training," +
    #                           "muscular_endurance, strength_endurance, hypertrophy, maximal_strength," +
    #                           "speed, sustained_power, power, maximal_power")

    user_stats_string = str(user_stats.event_date) + "," + str(len(user_stats.high_relative_load_sessions)) + "," + str(user_stats.high_relative_load_score) + "," + str(
        user_stats.eligible_for_high_load_trigger) + ","
    user_stats_string += str(user_stats.expected_weekly_workouts) + ","

    user_stats_string += get_std_error_if_present_string(user_stats, "vo2_max")
    user_stats_string += get_if_present_string(user_stats, "vo2_max_date_time")
    user_stats_string += get_if_present_string(user_stats, "best_running_time")
    user_stats_string += get_if_present_string(user_stats, "best_running_distance")
    user_stats_string += get_if_present_string(user_stats, "best_running_date")
    user_stats_string += get_std_error_if_present_string(user_stats, "internal_ramp")
    user_stats_string += get_std_error_if_present_string(user_stats, "internal_monotony")
    user_stats_string += get_std_error_if_present_string(user_stats, "internal_strain")
    user_stats_string += get_std_error_if_present_string(user_stats, "internal_strain_events")
    user_stats_string += get_std_error_if_present_string(user_stats, "acute_internal_total_load")
    user_stats_string += get_std_error_if_present_string(user_stats, "chronic_internal_total_load")
    user_stats_string += get_std_error_if_present_string(user_stats, "internal_acwr")
    user_stats_string += get_std_error_if_present_string(user_stats, "internal_freshness_index")
    user_stats_string += get_if_present_string(user_stats, "acute_days")
    user_stats_string += get_if_present_string(user_stats, "chronic_days")
    user_stats_string += get_if_present_string(user_stats, "total_historical_sessions")
    user_stats_string += get_std_error_if_present_string(user_stats, "average_weekly_internal_load")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "base_aerobic_training")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "anaerobic_threshold_training")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "high_intensity_anaerobic_training")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "muscular_endurance")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "strength_endurance")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "hypertrophy")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "maximal_strength")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "speed")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "sustained_power")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "power")
    user_stats_string += get_training_unit_if_present_string(user_stats.athlete_capacities, "maximal_power", is_last=True)

    return user_stats_string


def get_plan_capacities_string(plan):
    plan_string = ""
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "base_aerobic_training")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "anaerobic_threshold_training")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "high_intensity_anaerobic_training")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "muscular_endurance")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "strength_endurance")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "hypertrophy")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "maximal_strength")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "speed")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "sustained_power")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "power")
    plan_string += get_training_unit_if_present_string(plan.athlete_capacities, "maximal_power", is_last=True)

    return plan_string


def get_training_exposure_string(session):
    training_string = ""
    exposure_count = 0
    for training_exposure in session.training_exposures:
        training_string += training_exposure.detailed_adaptation_type.name + "; " + str(training_exposure.rpe.highest_value()) + ";" + str(training_exposure.volume.highest_value()) + ";"
        exposure_count += 1
        if exposure_count < len(session.training_exposures):
            training_string += "||"

    return training_string


def get_target_training_exposure_string(obj, is_athlete_target_training_exposure=False):
    training_string = ""

    target_training_exposure_count = 0
    for target_training_exposure in obj.target_training_exposures:
        if is_athlete_target_training_exposure:
            training_string += ("{progression_week:" + str(target_training_exposure.progression_week) +
                                ";exposure_count:" + get_std_error_if_present_string(target_training_exposure, "exposure_count", is_last=True) + ";" + "priority:" + str(
                        target_training_exposure.priority) + ";")
        else:
            training_string += "{exposure_count:" + get_std_error_if_present_string(target_training_exposure, "exposure_count", is_last=True) + ";" + "priority:" + str(
                target_training_exposure.priority) + ";"

        exposure_count = 0
        target_training_exposure_count += 1
        for training_exposure in target_training_exposure.training_exposures:
            training_string += training_exposure.detailed_adaptation_type.name + "; "
            if training_exposure.rpe is not None:
                training_string += "RPE:" + str(training_exposure.rpe.highest_value()) + ";"
            else:
                training_string += "RPE:None;"

            if training_exposure.volume is not None:
                training_string += "VOL:" + str(training_exposure.volume.highest_value()) + ";"
            else:
                training_string += "VOL:None;"
            exposure_count += 1
            if exposure_count < len(target_training_exposure.training_exposures):
                training_string += "||"
        # if target_training_exposure_count < len(obj.target_training_exposures):
        training_string += "}"

    return training_string


def get_session_string(session):
    # workout_header_line = (
    #     "event_date_time, id,description, distance, duration_minutes, power_load_highest, rpe_load_highest, training_volume, target_training_exposures")
    session_string = str(session.event_date) + "," + session.id + "," + session.description + "," + str(session.distance) + "," + str(session.duration_minutes) + ","
    session_string += str(session.session_RPE) + "," + str(session.power_load.highest_value()) + "," + str(session.rpe_load.highest_value()) + "," + str(session.training_volume) + ","
    session_string += get_training_exposure_string(session)

    return session_string


def get_periodization_goals_string(plan):
    goal_string = ""
    goal_count = 0
    for periodization_goal in plan.periodization_goals:
        goal_string += periodization_goal.periodization_goal_type.name + ";Training Exposures= " + get_target_training_exposure_string(periodization_goal) + ";"
        goal_count += 1
        if goal_count < len(plan.periodization_goals):
            goal_string += "||"

    return goal_string


def get_body_part_side_string(body_parts):
    body_part_string = ""

    for b in body_parts:
        if len(body_part_string) > 0:
            body_part_string += ";"
        body_part_string += b.body_part_location.name + ": side=" + str(b.side)

    return body_part_string


def get_periodization_plan_string(plan, event_date):
    plan_string = str(plan.start_date) + "," + str(event_date) + ","
    plan_string += get_periodization_goals_string(plan) + ","
    plan_string += plan.training_phase_type.name + "," + plan.athlete_persona.name + ","
    plan_string += ("cardio_persona=" + plan.sub_adaptation_type_personas.cardio_persona.name + ";" +
                    "power_persona=" + plan.sub_adaptation_type_personas.power_persona.name + ";" +
                    "strength_persona=" + plan.sub_adaptation_type_personas.strength_persona.name) + ","
    plan_string += get_target_training_exposure_string(plan, is_athlete_target_training_exposure=True) + "," + get_std_error_if_present_string(plan, "target_weekly_rpe_load", is_last=True) + ","
    plan_string += get_std_error_if_present_string(plan, "expected_weekly_workouts", is_last=True) + ","
    plan_string += get_plan_capacities_string(plan) + ","
    plan_string += get_body_part_side_string(plan.acute_muscle_issues) + ","
    plan_string += get_body_part_side_string(plan.chronic_muscle_issues) + ","
    plan_string += get_body_part_side_string(plan.excessive_strain_muscles) + ","
    plan_string += get_body_part_side_string(plan.compensating_muscles) + ","
    plan_string += get_body_part_side_string(plan.functional_overreaching_muscles) + ","
    plan_string += get_body_part_side_string(plan.non_functional_overreaching_muscles) + ","
    plan_string += get_body_part_side_string(plan.tendon_issues)

    return plan_string


def get_scoring_string(event_date, workout):
    scoring_string = str(event_date) + "," + str(workout.score) + "," + workout.program_module_id.replace(',', '_') + ","

    scoring_string += get_training_exposure_string(workout)
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "base_aerobic_training")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "anaerobic_threshold_training")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "high_intensity_anaerobic_training")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "muscular_endurance")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "strength_endurance")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "hypertrophy")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "maximal_strength")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "speed")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "sustained_power")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "power")
    # scoring_string += get_training_unit_if_present_string(workout.athlete_capacities, "maximal_power", is_last=True)

    return scoring_string


def get_ird_string(event_date, body_part_side, body_part_injury_rik):
    ird_string = str(event_date) + ","
    ird_string += (body_part_side.body_part_location.name + "; side:" + str(body_part_side.side) + '; con_load: ' +
                   str(body_part_injury_rik.concentric_volume_today.highest_value()) + "; vol_tier: " +
                   str(body_part_injury_rik.total_volume_percent_tier) + ";" +
                   "last_ache_level:" + str(body_part_injury_rik.last_ache_level) + ";"
                                                                                    "last_knots_level:" + str(body_part_injury_rik.last_knots_level) + ";"
                                                                                                                                                       "last_muscle_spasm_level:" + str(
                body_part_injury_rik.last_muscle_spasm_level) + ";"
                                                                "last_sharp_level:" + str(body_part_injury_rik.last_sharp_level) + ";"
                                                                                                                                   "last_tight_level:" + str(
                body_part_injury_rik.last_tight_level) + ";"
                   # "last_ache_level:" + str(body_part_injury_rik.last_ache_level) + ";"
                   )

    return ird_string


def get_responsive_recovery_string(event_date, symptoms, responsive_recovery):
    active_rest = responsive_recovery.active_rest
    active_recovery = responsive_recovery.active_recovery
    ice = responsive_recovery.ice
    cwi = responsive_recovery.cold_water_immersion

    phase_string = str(event_date) + ","

    if len(symptoms) > 0:
        all_soreness_string = ""
        for soreness_dict in symptoms:
            if len(all_soreness_string) > 0:
                all_soreness_string += "|||"
            soreness_string = ""
            for key, value in soreness_dict.items():
                if len(soreness_string) > 0:
                    soreness_string += "; "
                if key not in ['reported_date_time', 'user_id']:
                    soreness_string += key + ":"
                    if value is None:
                        soreness_string += "None"
                else:
                    soreness_string += str(value)
            all_soreness_string += soreness_string
        phase_string += all_soreness_string + ","
    else:
        phase_string += ","

    if active_rest is not None:
        phase_string += "Active Rest,"
        phase_exercise_string = ""
        for exercise_phase in active_rest.exercise_phases:
            if len(phase_exercise_string) > 0:
                phase_exercise_string += "; "
            phase_exercise_string += str(exercise_phase.name).upper() + ":"
            exercise_string = ""
            if len(exercise_phase.exercises) > 0:
                for exercise_id, assigned_exercise in exercise_phase.exercises.items():
                    if len(exercise_string) > 0:
                        exercise_string += ";"
                    exercise_string += exercise_id
            else:
                exercise_string = " None"
            phase_exercise_string += exercise_string
        phase_string += phase_exercise_string
        worked = 0

    if active_rest is None:
        oops = 0

    if active_recovery is not None:
        here = 0
    if ice is not None:
        phase_string += "; Ice:"
        for body_part in ice.body_parts:
            phase_string += body_part.body_part_location.name + "; side=" + str(body_part.side) + ";"
    if cwi is not None:
        phase_string += "; **COLD WATER IMMERSION**"

    return phase_string


def get_movement_prep_string(event_date, symptoms, movement_prep):
    phase_string = str(event_date) + ","

    if len(symptoms) > 0:
        all_soreness_string = ""
        for soreness_dict in symptoms:
            if len(all_soreness_string) > 0:
                all_soreness_string += "|||"
            soreness_string = ""
            for key, value in soreness_dict.items():
                if len(soreness_string) > 0:
                    soreness_string += "; "
                if key not in ['reported_date_time', 'user_id']:
                    soreness_string += key + ":"
                    if value is None:
                        soreness_string += "None"
                    else:
                        soreness_string += str(value)
            all_soreness_string += soreness_string
        phase_string += all_soreness_string + ","
    else:
        phase_string += ","

    if movement_prep is not None:
        phase_string += "Movement Prep,"
        phase_exercise_string = ""
        for exercise_phase in movement_prep.movement_integration_prep.exercise_phases:
            if len(phase_exercise_string) > 0:
                phase_exercise_string += "; "
            phase_exercise_string += str(exercise_phase.name).upper() + ":"
            exercise_string = ""
            if len(exercise_phase.exercises) > 0:
                for exercise_id, assigned_exercise in exercise_phase.exercises.items():
                    if len(exercise_string) > 0:
                        exercise_string += ";"
                    exercise_string += exercise_id
            else:
                exercise_string = " None"
            phase_exercise_string += exercise_string
        phase_string += phase_exercise_string
        worked = 0
    else:
        oops = 0

    return phase_string


def get_mobility_wod_string(event_date, symptoms, responsive_recovery):
    active_rest = responsive_recovery.active_rest

    phase_string = str(event_date) + ","

    if len(symptoms) > 0:
        all_soreness_string = ""
        for soreness_dict in symptoms:
            if len(all_soreness_string) > 0:
                all_soreness_string += "|||"
            soreness_string = ""
            for key, value in soreness_dict.items():
                if len(soreness_string) > 0:
                    soreness_string += "; "
                if key not in ['reported_date_time', 'user_id']:
                    soreness_string += key + ":"
                    if value is None:
                        soreness_string += "None"
                    else:
                        soreness_string += str(value)
            all_soreness_string += soreness_string
        phase_string += all_soreness_string + ","
    else:
        phase_string += ","

    if active_rest is not None:
        phase_string += "Mobility WOD: Active Rest,"
        phase_exercise_string = ""
        for exercise_phase in active_rest.exercise_phases:
            if len(phase_exercise_string) > 0:
                phase_exercise_string += "; "
            phase_exercise_string += str(exercise_phase.name).upper() + ":"
            exercise_string = ""
            if len(exercise_phase.exercises) > 0:
                for exercise_id, assigned_exercise in exercise_phase.exercises.items():
                    if len(exercise_string) > 0:
                        exercise_string += ";"
                    exercise_string += exercise_id
            else:
                exercise_string = " None"
            phase_exercise_string += exercise_string
        phase_string += phase_exercise_string
        worked = 0
    else:
        oops = 0

    return phase_string



if __name__ == '__main__':
    start = time.time()

    days = 0
    days_since_last = 0
    total_workouts = 0

    start_date = None
    last_date = None

    # all_soreness = load_data('c59a9411-fc75-4fff-a39c-2c3f4cca0e86', '2017-10-01', '2020-10-01')
    all_soreness = {}  # change to loading from persona

    plan = None  # Periodization Plan
    periodization_plan_processor = PeriodizationPlanProcessor()
    periodization_goal_factory = PeriodizationGoalFactory()


    # users = get_users()
    users = ['persona2a']

    symptoms = None

    for user_name in users:
        user_history = pd.read_csv(f'personas/{user_name}/workout_history.csv')
        user_profile = profiles[user_name]

        periodization_goals = periodization_goal_factory.create(PeriodizationGoalType.increase_cardio_endurance)
        training_phase_type = TrainingPhaseType[user_profile['training_phase_type']]
        periodization_persona = PeriodizationPersona.well_trained
        sub_adaptation_type_persona = SubAdaptionTypePersonas(cardio_persona=TrainingPersona.intermediate,
                                                              strength_persona=TrainingPersona[user_profile['strength_proficiency']],
                                                              power_persona=TrainingPersona[user_profile['power_proficiency']])

        user_history_length = len(user_history)
        dates = get_dates(user_history_length)

        days_lived = 0

        user_stats_output = open('output/user_stats_' + user_name + ".csv", 'w')
        user_stats_header_line = ("date, high_relative_load_sessions, high_relative_load_score, eligible_for_high_load_trigger," +
                                  "expected_weekly_workouts, vo2_max, vo2_max_date_time, best_running_time, best_running_distance, best_running_date," +
                                  "internal_ramp, internal_monotony, internal_strain, internal_strain_events, " +
                                  "acute_internal_total_load, chronic_internal_total_load, internal_acwr, internal_freshness_index," +
                                  "acute_days, chronic_days, total_historical_sessions, average_weekly_internal_load," +
                                  "base_aerobic_training, anaerobic_threshold_training, high_intensity_anaerobic_training," +
                                  "muscular_endurance, strength_endurance, hypertrophy, maximal_strength," +
                                  "speed, sustained_power, power, maximal_power")
        user_stats_output.write(user_stats_header_line + '\n')

        workout_output = open('output/workouts_' + user_name + ".csv", 'w')
        workout_header_line = ("event_date_time, id,description, distance, duration_minutes, session_rpe, "
                               "power_load_highest, rpe_load_highest,  training_volume, target_training_exposures")
        workout_output.write(workout_header_line + '\n')

        periodization_plan_output = open('output/periodization_plan_' + user_name + ".csv", "w")
        periodization_plan_header_line = ("start_date, current_date, goals, training_phase_type, athlete_persona, sub_adaptation_type_personas," +
                                          "target_training_exposures, target_weekly_rpe_load,expected_weekly_workouts," +
                                          "base_aerobic_training, anaerobic_threshold_training, high_intensity_anaerobic_training," +
                                          "muscular_endurance, strength_endurance, hypertrophy, maximal_strength," +
                                          "speed, sustained_power, power, maximal_power," +
                                          "acute_muscle_issues, chronic_muscle_issues, excessive_strain_muscles, compensating_muscles," +
                                          "functional_overreaching_muscles, non_functional_overreaching_muscles, tendon_issues"
                                          )

        periodization_plan_output.write(periodization_plan_header_line + '\n')

        scoring_output = open('output/workout_scoring_' + user_name + ".csv", "w")
        scoring_output_header_line = ("event_date,score,program_module_id, training_exposures")

        scoring_output.write(scoring_output_header_line + '\n')

        recovery_output = open('output/recovery_plan_' + user_name + ".csv", "w")
        recovery_header_line = ("event_date, symptoms, activity_type, exercises")
        recovery_output.write(recovery_header_line + '\n')

        ird_output = open('output/ird_' + user_name + ".csv", "w")
        ird_header_line = ("event_date, body_part_data")
        ird_output.write(ird_header_line + '\n')

        email = user_name + "@300.com"

        user_id, jwt = login_user(email)

        demo_persona = DemoPersona(user_id)

        demo_persona.clear_user()
        beginning_event_date_time = dates[0] + timedelta(hours=1, minutes=2, seconds=3)
        beginning_event_date_time = utc.localize(beginning_event_date_time)
        demo_persona.create_stats(user_profile, beginning_event_date_time)

        user_age = user_profile['user_age']  # TODO how do we get this set!?!?!

        for i, daily_info in user_history.iterrows():
            date = dates[i]
            event_date = date + timedelta(hours=1, minutes=2, seconds=3)
            event_date = utc.localize(event_date)
            event_date_string = format_datetime(event_date)
            print(event_date_string)

            # target_date = datetime(2019, 9, 2) + timedelta(hours=1, minutes=2, seconds=3)
            # target_date = utc.localize(target_date)
            #
            # if event_date == target_date:
            #     stop_here = 0

            if date.strftime("%Y-%m-%d") in all_soreness:
                todays_soreness = all_soreness[date.strftime("%Y-%m-%d")]
            else:
                todays_soreness = []

            if len(todays_soreness) > 0:
                serialised_soreness = []
                for soreness in todays_soreness:
                    serialised_soreness.append(soreness.json_serialise())
            else:
                serialised_soreness = []

            if days_lived > 0:
                # update nightly process
                demo_persona.update_stats(event_date)
                user_stats_string = get_user_stats_string(demo_persona.user_stats)
                user_stats_output.write(user_stats_string + '\n')

                ird_datastore = InjuryRiskDatastore()
                injury_risk_dict = ird_datastore.get(user_id)

                if plan is not None:
                    plan = periodization_plan_processor.set_acute_chronic_muscle_needs(plan, event_date, injury_risk_dict)
                    plan = periodization_plan_processor.update_periodization_plan_for_week(plan,
                                                                                           event_date,
                                                                                           demo_persona.user_stats)
                    plan_string = get_periodization_plan_string(plan, event_date)
                    periodization_plan_output.write(plan_string + '\n')

            # all_files = os.listdir(f'workouts/{user_name}')

            # all_files.sort(key=lambda f: int(''.join(filter(str.isdigit, f))))

            zero_date = date + timedelta(hours=0, minutes=0, seconds=0)

            todays_files = get_completed_workout(daily_info['Workout'], daily_info['Library'])

            ird_datastore = InjuryRiskDatastore()
            injury_risk_dict = ird_datastore.get(user_id)

            ird_processor = InjuryRiskDictOutputProcessor('output/irds/', user_id, user_name)
            ird_processor.write_headers(date.strftime("%Y-%m-%d"))
            ird_processor.write_day(event_date.date())
            ird_processor.close()

            check_now = 0

            if len(todays_files) == 0:  # no workout available for this day
                response = submit_mobility_wod_request([], user_id, event_date, symptoms=serialised_soreness, user_age=user_age)

                mobility_wod_string = get_mobility_wod_string(event_date, serialised_soreness, response)
                recovery_output.write(mobility_wod_string + '\n')

                user_stats_datastore = UserStatsDatastore()
                demo_persona.user_stats = user_stats_datastore.get(athlete_id=user_id)

                if plan is not None:
                    planned_load_datastore = PlannedWorkoutLoadDatastore()
                    planned_workouts = planned_load_datastore.get(user_profile_id="andra_profile")
                    scoring_proc = WorkoutScoringProcessor()
                    for planned_workout in planned_workouts:
                        planned_workout.score = scoring_proc.score_workout(plan.athlete_capacities, plan.target_training_exposures, planned_workout.training_exposures)

                    planned_workouts.sort(key=lambda x: x.score, reverse=True)

                    for planned_workout in planned_workouts:
                        scoring_string = get_scoring_string(event_date, planned_workout)
                        scoring_output.write(scoring_string + '\n')

            # for file_name in all_files:
            for workout in todays_files:
                # workout = read_json(file_name, user_name)
                event_date_time = date + timedelta(hours=17, minutes=30)
                event_date_time = utc.localize(event_date_time)

                if start_date is None:
                    start_date = event_date

                # if last_date is None:
                #     last_date = event_date

                days = (event_date - start_date).days
                workout['event_date_time'] = format_datetime(event_date_time)
                session_RPE = daily_info['sRPE']
                session_data = create_session_only(workout, session_RPE)

                movement_prep = submit_movement_prep_request(session_data, user_id, event_date_time, program_module_id=None, symptoms=serialised_soreness)
                movement_prep_string = get_movement_prep_string(event_date, serialised_soreness, movement_prep)
                recovery_output.write(movement_prep_string + '\n')

                user_stats_datastore = UserStatsDatastore()
                demo_persona.user_stats = user_stats_datastore.get(athlete_id=user_id)

                response = submit_session_to_get_responsive_recovery(session_data, user_id, jwt, event_date_time, symptoms=serialised_soreness)
                responsive_recovery_string = get_responsive_recovery_string(event_date, serialised_soreness, response)
                recovery_output.write(responsive_recovery_string + '\n')

                user_stats_datastore = UserStatsDatastore()
                demo_persona.user_stats = user_stats_datastore.get(athlete_id=user_id)

                training_session_datastore = TrainingSessionDatastore()
                training_sessions = training_session_datastore.get(user_id=user_id, event_date_time=event_date_time, read_session_load_dict=False)

                for training_session in training_sessions:
                    session_string = get_session_string(training_session)
                    workout_output.write(session_string + '\n')
                    if plan is not None:
                        plan = periodization_plan_processor.set_acute_chronic_muscle_needs(plan, event_date,
                                                                                           injury_risk_dict)
                        periodization_plan_processor.update_exposure_needs(plan.target_training_exposures, training_session.training_exposures)
                        plan_string = get_periodization_plan_string(plan, event_date)
                        periodization_plan_output.write(plan_string + '\n')

                    total_workouts += 1

                if plan is not None:
                    planned_load_datastore = PlannedWorkoutLoadDatastore()
                    planned_workouts = planned_load_datastore.get(user_profile_id="andra_profile")
                    scoring_proc = WorkoutScoringProcessor()
                    for planned_workout in planned_workouts:
                        planned_workout.score = scoring_proc.score_workout(plan.athlete_capacities, plan.target_training_exposures, planned_workout.training_exposures)

                    planned_workouts.sort(key=lambda x: x.score, reverse=True)

                    for planned_workout in planned_workouts:
                        scoring_string = get_scoring_string(event_date, planned_workout)
                        scoring_output.write(scoring_string + '\n')

                if total_workouts >= 5:
                    if plan is None:
                        plan = periodization_plan_processor.create_periodization_plan(event_date,
                                                                                      [periodization_goals],
                                                                                      training_phase_type,
                                                                                      periodization_persona,
                                                                                      sub_adaptation_type_persona,
                                                                                      demo_persona.user_stats)
                        plan = periodization_plan_processor.set_acute_chronic_muscle_needs(plan, event_date,
                                                                                           injury_risk_dict)
                        plan_string = get_periodization_plan_string(plan, event_date)
                        periodization_plan_output.write(plan_string + '\n')

            # last_date = event_date
            days_lived += 1

        user_stats_output.close()
        workout_output.close()
        periodization_plan_output.close()
        scoring_output.close()
        recovery_output.close()
        ird_output.close()
