import database.september_demo.set_up_config
import pickle
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
from models.periodization_plan import PeriodizationPlan, PeriodizationPersona, TrainingPhaseType, TrainingPhaseFactory
from models.periodization_goal import PeriodizationGoalFactory, PeriodizationGoalType, PeriodizationGoal
from models.athlete_capacity import TrainingPersona, SubAdaptionTypePersonas
from logic.periodization_processing import PeriodizationPlanProcessor
from logic.workout_scoring import WorkoutScoringProcessor
from logic.soreness_processing import SorenessCalculator
from database.september_demo.write_injury_risk_dict import InjuryRiskDictOutputProcessor
from logic.athlete_capacity_processing import AthleteCapacityProcessor
from database.september_demo.user_profiles import profiles
from database.september_demo.demo_utilities import DemoOutput
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
# from database.september_demo.get_workouts_for_persona import get_completed_workout
from database.september_demo.get_user_history import get_user_data
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


def create_session_only(workout, session_RPE):
    # workout = read_json(file_name, user_name)
    data = {
        "event_date": workout['event_date_time'],
        "session_type": 7,
        "duration": workout['duration_seconds'] / 60,
        "description": workout['program_module_id'],
        # "calories": 100,
        "distance": workout['distance'],
        "session_RPE": session_RPE,
        "end_date": workout['workout_sections'][0]['end_date_time'],
        # "hr_data": {{hr_data}},
        "workout_program_module": workout
    }
    return data


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

    demo_utilities = DemoOutput()

    # users = get_users()
    users = ['persona2a']

    symptoms = None

    for user_name in users:
        user_history = get_user_data(user_name)
        date_0 = user_history['1_Monday']['date']
        # user_history = pd.read_csv(f'personas/{user_name}/workout_history.csv')
        user_profile = profiles[user_name]

        periodization_goals = periodization_goal_factory.create(PeriodizationGoalType[user_profile['periodization_goal_type']])
        # periodization_goals = periodization_goal_factory.create(PeriodizationGoalType.increase_cardio_endurance)
        training_phase_type = TrainingPhaseType[user_profile['training_phase_type']]
        periodization_persona = PeriodizationPersona[user_profile['periodization_persona']]
        sub_adaptation_type_persona = SubAdaptionTypePersonas(cardio_persona=TrainingPersona[user_profile['cardio_proficiency']],
                                                              strength_persona=TrainingPersona[user_profile['strength_proficiency']],
                                                              power_persona=TrainingPersona[user_profile['power_proficiency']])

        # user_history_length = len(user_history)
        # dates = get_dates(user_history_length)

        days_lived = 0

        user_stats_output = open('output/user_stats_' + user_name + ".csv", 'w')
        user_stats_output.write(demo_utilities.user_stats_header_line + '\n')

        workout_output = open('output/workouts_' + user_name + ".csv", 'w')
        workout_output.write(demo_utilities.workout_header_line + '\n')

        periodization_plan_output = open('output/periodization_plan_' + user_name + ".csv", "w")
        periodization_plan_output.write(demo_utilities.periodization_plan_header_line + '\n')

        scoring_output = open('output/workout_scoring_' + user_name + ".csv", "w")
        scoring_output_header_line = ("event_date,score,program_module_id, training_exposures")

        scoring_output.write(scoring_output_header_line + '\n')

        recovery_output = open('output/recovery_plan_' + user_name + ".csv", "w")
        recovery_header_line = ("event_date, symptoms, activity_type, comprehensive_exercises, complete_exercises, efficient_exercises, Ice/CWI")
        recovery_output.write(recovery_header_line + '\n')

        ird_output = open('output/ird_' + user_name + ".csv", "w")
        ird_header_line = ("event_date, body_part_data")
        ird_output.write(ird_header_line + '\n')

        email = user_name + "@300.com"

        user_id, jwt = login_user(email)

        demo_persona = DemoPersona(user_id)

        demo_persona.clear_user()
        beginning_event_date_time = date_0 + timedelta(hours=3, minutes=2, seconds=3)
        beginning_event_date_time = utc.localize(beginning_event_date_time)
        demo_persona.create_stats(user_profile, beginning_event_date_time)

        user_age = user_profile['user_age']  # TODO how do we get this set!?!?!

        # for i, daily_info in user_history.iterrows():
        for daily_info in user_history.values():
            date = daily_info['date']
            event_date = date + timedelta(hours=3, minutes=2, seconds=3)
            event_date = utc.localize(event_date)
            event_date_string = format_datetime(event_date)
            print(event_date_string)

            target_date = datetime(2020, 8, 10) + timedelta(hours=3, minutes=2, seconds=3)
            target_date = utc.localize(target_date)

            if event_date == target_date:
                stop_here=0

            todays_files = daily_info['workout']
            todays_soreness = daily_info['soreness']

            if todays_soreness is not None:
                soreness_before_session = todays_soreness['before_session']
                soreness_after_session = todays_soreness['after_session']
            else:
                soreness_before_session = []
                soreness_after_session = []

            if days_lived > 0:
                # update nightly process
                demo_persona.update_stats(event_date, force_historical=True)
                user_stats_string = demo_utilities.get_user_stats_string(demo_persona.user_stats)
                user_stats_output.write(user_stats_string + '\n')

                ird_datastore = InjuryRiskDatastore()
                injury_risk_dict = ird_datastore.get(user_id)

                ird_processor = InjuryRiskDictOutputProcessor('output/irds/', user_id, user_name)
                ird_processor.write_headers(date.strftime("%Y-%m-%d"))
                ird_processor.write_day(event_date.date())
                ird_processor.close()

                if plan is not None:
                    plan = periodization_plan_processor.set_acute_chronic_muscle_needs(plan, event_date, injury_risk_dict)
                    plan = periodization_plan_processor.update_periodization_plan_for_week(plan,
                                                                                           event_date,
                                                                                           demo_persona.user_stats)
                    athlete_capacitiy_processor = AthleteCapacityProcessor()
                    training_phase_factory = TrainingPhaseFactory()
                    training_phase = training_phase_factory.create(plan.training_phase_type)
                    athlete_readiness = athlete_capacitiy_processor.get_daily_readiness_scores(event_date,
                                                                                               injury_risk_dict,
                                                                                               demo_persona.user_stats,
                                                                                               plan, training_phase)

                    plan_string = demo_utilities.get_periodization_plan_string(plan, event_date, athlete_readiness)
                    periodization_plan_output.write(plan_string + '\n')

            zero_date = date + timedelta(hours=0, minutes=0, seconds=0)

            ird_datastore = InjuryRiskDatastore()
            injury_risk_dict = ird_datastore.get(user_id)

            check_now = 0

            if len(todays_files) == 0:  # no workout available for this day
                all_soreness = []
                all_soreness.extend(soreness_before_session)
                all_soreness.extend(soreness_after_session)
                response = submit_mobility_wod_request([], user_id, event_date, symptoms=all_soreness, user_age=user_age)

                mobility_wod_string = demo_utilities.get_mobility_wod_string(event_date, all_soreness, response)
                recovery_output.write(mobility_wod_string + '\n')

                user_stats_datastore = UserStatsDatastore()
                demo_persona.user_stats = user_stats_datastore.get(athlete_id=user_id)

                if plan is not None:
                    planned_load_datastore = PlannedWorkoutLoadDatastore()
                    planned_workouts = planned_load_datastore.get(user_profile_id=user_name)
                    scoring_proc = WorkoutScoringProcessor()
                    for planned_workout in planned_workouts:
                        planned_workout.score = scoring_proc.score_workout(plan.athlete_capacities, plan.target_training_exposures, planned_workout.training_exposures)

                    planned_workouts.sort(key=lambda x: x.score, reverse=True)

                    for planned_workout in planned_workouts:
                        scoring_string = demo_utilities.get_scoring_string(event_date, planned_workout)
                        scoring_output.write(scoring_string + '\n')

            # for file_name in all_files:
            for workout in todays_files:
                # workout = read_json(file_name, user_name)
                pre_workout_event_date_time = date + timedelta(hours=8, minutes=30)
                pre_workout_event_date_time = utc.localize(pre_workout_event_date_time)
                event_date_time = date + timedelta(hours=17, minutes=30)
                event_date_time = utc.localize(event_date_time)

                if start_date is None:
                    start_date = event_date

                days = (event_date - start_date).days
                workout['event_date_time'] = format_datetime(event_date_time)
                session_RPE = daily_info['session_RPE']
                session_data = create_session_only(workout, session_RPE)
                movement_prep = submit_movement_prep_request(session_data, user_id, pre_workout_event_date_time, program_module_id=None, symptoms=soreness_before_session)
                movement_prep_string = demo_utilities.get_movement_prep_string(event_date, soreness_before_session, movement_prep)
                recovery_output.write(movement_prep_string + '\n')

                user_stats_datastore = UserStatsDatastore()
                demo_persona.user_stats = user_stats_datastore.get(athlete_id=user_id)

                # soreness_after_session_copy = pickle.loads(pickle.dumps(soreness_after_session, -1))
                response = submit_session_to_get_responsive_recovery(session_data, user_id, jwt, event_date_time, symptoms=soreness_after_session)
                responsive_recovery_string = demo_utilities.get_responsive_recovery_string(event_date, soreness_after_session, response)
                recovery_output.write(responsive_recovery_string + '\n')

                user_stats_datastore = UserStatsDatastore()
                demo_persona.user_stats = user_stats_datastore.get(athlete_id=user_id)
                user_stats_string = demo_utilities.get_user_stats_string(demo_persona.user_stats)
                user_stats_output.write(user_stats_string + '\n')

                training_session_datastore = TrainingSessionDatastore()
                training_sessions = training_session_datastore.get(user_id=user_id, event_date_time=event_date_time, read_session_load_dict=False)

                ird_datastore = InjuryRiskDatastore()
                injury_risk_dict = ird_datastore.get(user_id)

                ird_processor_2 = InjuryRiskDictOutputProcessor('output/irds/', user_id, user_name+"_2")
                ird_processor_2.write_headers(date.strftime("%Y-%m-%d"))
                ird_processor_2.write_day(event_date.date())
                ird_processor_2.close()

                for training_session in training_sessions:
                    session_string = demo_utilities.get_session_string(training_session)
                    workout_output.write(session_string + '\n')
                    if plan is not None:
                        plan = periodization_plan_processor.set_acute_chronic_muscle_needs(plan, event_date,
                                                                                           injury_risk_dict)
                        periodization_plan_processor.update_exposure_needs(plan.target_training_exposures, training_session.training_exposures)

                        athlete_capacitiy_processor = AthleteCapacityProcessor()
                        training_phase_factory = TrainingPhaseFactory()
                        training_phase = training_phase_factory.create(plan.training_phase_type)
                        athlete_readiness = athlete_capacitiy_processor.get_daily_readiness_scores(
                            event_date, injury_risk_dict, demo_persona.user_stats, plan, training_phase)

                        plan_string = demo_utilities.get_periodization_plan_string(plan, event_date, athlete_readiness)
                        periodization_plan_output.write(plan_string + '\n')

                    total_workouts += 1

                if plan is not None:
                    planned_load_datastore = PlannedWorkoutLoadDatastore()
                    planned_workouts = planned_load_datastore.get(user_profile_id=user_name)
                    scoring_proc = WorkoutScoringProcessor()
                    for planned_workout in planned_workouts:
                        planned_workout.score = scoring_proc.score_workout(plan.athlete_capacities, plan.target_training_exposures, planned_workout.training_exposures)

                    planned_workouts.sort(key=lambda x: x.score, reverse=True)

                    for planned_workout in planned_workouts:
                        scoring_string = demo_utilities.get_scoring_string(event_date, planned_workout)
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

                        athlete_capacitiy_processor = AthleteCapacityProcessor()
                        training_phase_factory = TrainingPhaseFactory()
                        training_phase = training_phase_factory.create(plan.training_phase_type)
                        athlete_readiness = athlete_capacitiy_processor.get_daily_readiness_scores(
                            event_date, injury_risk_dict, demo_persona.user_stats, plan, training_phase)

                        plan_string = demo_utilities.get_periodization_plan_string(plan, event_date, athlete_readiness)
                        periodization_plan_output.write(plan_string + '\n')

            # last_date = event_date
            days_lived += 1

        user_stats_output.close()
        workout_output.close()
        periodization_plan_output.close()
        scoring_output.close()
        recovery_output.close()
        ird_output.close()
