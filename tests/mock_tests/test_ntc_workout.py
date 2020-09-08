
from fathomapi.api.config import Config
provider_info = Config.get('PROVIDER_INFO')
provider_info['movement_library_filename'] = 'movement_library_nike.json'
Config.set('PROVIDER_INFO', provider_info)

from models.planned_exercise import PlannedWorkout
from models.session import PlannedSession
from models.sport import SportName
from logic.workout_processing import WorkoutProcessor
import os, json
import datetime


def get_ntc_workout():
    all_workouts = []
    base_path = '../../database/ntc/libraries/workouts/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    json_data = json.load(f)
                    workout = PlannedWorkout.json_deserialise(json_data)
                    # for section in workout.sections:
                    #     for exercise in section.exercises:
                    #         exercise.movement_id = '58459de6dc2ce90011f93d86'
                    all_workouts.append(workout)
    return all_workouts


def get_nrc_workout():
    all_workouts = []
    base_path = '../../database/ntc/libraries/NRC_workouts/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    json_data = json.load(f)
                    workout = PlannedWorkout.json_deserialise(json_data)
                    # for section in workout.sections:
                    #     for exercise in section.exercises:
                    #         exercise.movement_id = '58459de6dc2ce90011f93d86'
                    all_workouts.append(workout)
    return all_workouts


def get_session(date, workout, assignment_type='default', movement_option=None):
    session = PlannedSession()
    session.event_date = date
    session.session_RPE = workout.rpe or 5
    # session.duration_minutes = workout.duration / 60
    session.sport_name = SportName.high_intensity_interval_training

    session.workout = workout
    WorkoutProcessor(user_weight=70, user_age=30).process_planned_workout(session, assignment_type=assignment_type, movement_option=movement_option)

    return session

# def test_ntc():
#     all_workouts = get_ntc_workout()
#     failed_count = 0
#     success_count = 0
#     for planned_workout in all_workouts:
#         try:
#             session = get_session(date=datetime.datetime.now(), workout=planned_workout)
#             if session.power_load is None or session.power_load.observed_value is None:
#                 print(f"workout has no load: {planned_workout.name}")
#             if session.rpe_load is None or session.rpe_load.observed_value is None:
#                 print(f"workout has no rpe load: {planned_workout.name}")
#             success_count += 1
#         except Exception as e:
#             failed_count += 1
#             print(f"processing failed: {planned_workout.name}")
#             print(e)
#     print(failed_count, success_count)
#
#
# def test_nrc():
#     all_workouts = get_nrc_workout()
#     failed_count = 0
#     success_count = 0
#     for planned_workout in all_workouts:
#         try:
#             session = get_session(date=datetime.datetime.now(), workout=planned_workout)
#             if session.power_load is None or session.power_load.observed_value is None:
#                 print(f"workout has no power load: {planned_workout.name}")
#             if session.rpe_load is None or session.rpe_load.observed_value is None:
#                 print(f"workout has no rpe load: {planned_workout.name}")
#             success_count += 1
#         except Exception as e:
#             failed_count += 1
#             print(f"processing failed: {planned_workout.name}")
#             print(e)
#     print(failed_count, success_count)
