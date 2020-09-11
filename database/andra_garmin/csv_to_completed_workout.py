import pandas as pd
import numpy as np
import datetime, os, json
from utils import format_datetime


# data_series = 'april-june2020'
data_series = 'july-sept2020'
csv_files_folder = f'csv_data/{data_series}'
workouts_folder = f'workouts/{data_series}'
if not os.path.exists(workouts_folder):
    os.mkdir(workouts_folder)


all_workouts = pd.read_csv('garmin_data/Activities.csv')
# def get_movement_id(distance, speed=2, duration=0):
#     if 800 < distance <= 5000:
#         movement_id = 'cruising'
#     elif distance < 800:
#         movement_id = 'sprint'
#     else:
#         movement_id = 'run'
#     return movement_id


def write_json(workout, workout_name, directory):
    json_string = json.dumps(workout, indent=4)
    file_name = os.path.join(f"{directory}/{workout_name}.json")
    if not os.path.exists(f"{directory}"):
        os.makedirs(f"{directory}")
    # print(f"writing: {file_name}")
    f1 = open(file_name, 'w')
    f1.write(json_string)
    f1.close()

def create_workout(file_name=''):


    detail_data = pd.read_csv(f'{csv_files_folder}/{file_name}')
    start_time = datetime.datetime.strptime(detail_data.timestamp.values[0], "%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=4)
    start_time = start_time.strftime("%Y-%m-%d %H:%M:%S")
    summary = all_workouts[all_workouts.Date == start_time]

    exercise = {}
    if len(summary) > 0:
        exercise['name'] = summary.Title.values[0]
        exercise['distance'] = float(summary.Distance) * 1609 # detail_data.distance.values[-1]
        start_time = datetime.datetime.strptime(detail_data.timestamp.values[0], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(detail_data.timestamp.values[-1], "%Y-%m-%d %H:%M:%S")
        duration = summary['Time'].values[0]
        duration = duration.split(":")
        duration = float(duration[0]) * 60 * 60 + float(duration[1]) * 60 + float(duration[2])
        exercise['duration'] = duration  # (end_time - start_time).seconds
        activity_type = summary['Activity Type'].values[0]
        if activity_type == 'Running':
            pace = summary['Avg Pace'].values[0]
            pace = pace.split(":")
            pace = float(pace[0]) * 60 + float(pace[1])
            exercise['speed'] = 1609 / pace
            if pace > 540:
                exercise['movement_id'] = "run"
            else:
                print('fast_run', file_name)
                print(pace)
                exercise['movement_id'] = "tempo"
        elif activity_type == 'Cycling':
            exercise['speed'] = float( summary['Avg Pace']) * 1609 / 3600  #np.mean(detail_data.enhanced_speed)
            exercise['movement_id'] = 'cycle'
        else:
            print(exercise['name'])
            return None
    else:
        exercise['name'] = "Unnamed run"
        exercise['distance'] = detail_data.distance.values[-1]
        start_time = datetime.datetime.strptime(detail_data.timestamp.values[0], "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(detail_data.timestamp.values[-1], "%Y-%m-%d %H:%M:%S")
        exercise['duration'] = (end_time - start_time).seconds
        exercise['speed'] =  np.mean(detail_data.enhanced_speed)
        exercise['movement_id'] = 'run'


    # exercise['movement_id'] = get_movement_id(exercise['distance'])
    exercise['hr'] = list(detail_data.heart_rate.values)

    section = {}
    section['name'] = "workout"
    section['duration_seconds'] = exercise['duration']
    section['workout_exercises'] = [exercise]
    section['start_date_time'] = format_datetime(start_time)
    section['end_date_time'] = format_datetime(end_time)

    workout = {}
    workout['name'] = exercise['name']
    workout['duration_seconds'] = exercise['duration']
    workout['workout_sections'] = [section]
    workout['distance'] = exercise['distance']
    workout['event_date_time'] = format_datetime(start_time)
    workout['program_module_id'] = exercise['name']
    workout['program_id'] = "garmin_data"
    write_json(workout, file_name.split('.')[0], workouts_folder)

count = 0
all_files = os.listdir(csv_files_folder)
for file_name in all_files:
    # if count > 0:
    #     break
    if '.csv' in file_name:
        create_workout(file_name)
        count += 1