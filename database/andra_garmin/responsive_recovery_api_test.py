import os, json
import database.andra_garmin.api_utils as utils
import datetime

if utils.HEADERS['Authorization'] is None:
    utils.login_user(utils.USER['email'])


# UPDATE this for correct series to look at
data_series = 'july-sept2020'
workouts_folder = f'workouts/{data_series}'


def read_json(file_name):
    file_name = f"{workouts_folder}/{file_name}"
    with open(file_name, 'r') as f:
        workout = json.load(f)
    return workout

def create_session(file_name):

    workout = read_json(file_name)
    data = {
        "user_age": 35,
        "event_date_time": workout['event_date_time'],
        "symptoms": [
        ],
        "session": {
            "event_date": workout['event_date_time'],
            "session_type": 7,
            "duration": workout['duration_seconds']  / 60,
            "description": workout['name'],
            # "calories": 100,
            "distance": workout['distance'],
            # "session_RPE": 7.3,
            "end_date": workout['workout_sections'][0]['end_date_time'],
            # "hr_data": {{hr_data}},
            "workout_program_module": workout
        }
    }
    response = utils.submit_session_to_get_responsive_recovery(data)
    if response.status_code != 201:
        print(file_name)



all_files = os.listdir(workouts_folder)

for file_name in all_files:
    if ".json" in file_name:
        create_session(file_name)