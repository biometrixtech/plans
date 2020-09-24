import pandas as pd
import os, json, string
from utils import convert_workout_text_to_id


def get_completed_workouts(lib):
    all_workouts = {}
    base_path = f'../../database/ntc/libraries/{lib}_completed/'
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    workout = json.load(f)
                    all_workouts[workout['program_module_id']] = workout
    return all_workouts

ntc_workouts = get_completed_workouts('NTC')
nrc_workouts = get_completed_workouts('NRC')


# def get_all_workouts(persona="persona2a"):
#     workouts_list = pd.read_csv(f'personas/{persona}/workout_history.csv')
#     for day, workout_info in workouts_list.iterrows():
#         todays_files = get_completed_workout(workout_info['Workout'], workout_info['Library'])
#         if len(todays_files) > 0:
#             print(todays_files[0]['program_module_id'], todays_files[0]['program_id'] )
#         else:
#             print('Off')


def get_completed_workout(workout, lib):
        if workout != 'Off':
            program_module_id = convert_workout_text_to_id(workout)
            if lib == 'NTC':
                daily_workout = ntc_workouts[program_module_id]
            elif lib == 'NRC':
                daily_workout = nrc_workouts[program_module_id]
            else:
                raise ValueError('invalid library name')
            return [daily_workout]
        return []


def get_planned_workouts(lib):
    all_workouts = {}
    if lib == 'NTC':
        base_path = f'../../database/ntc/libraries/workouts/'
    elif lib == 'NRC':
        base_path = f'../../database/ntc/libraries/{lib}_workouts/'
    else:
        raise ValueError("No library found")
    dirs = os.listdir(base_path)
    for dir in dirs:
        if '.DS_' in dir:
            continue
        files = os.listdir(f"{base_path}/{dir}")
        for file in files:
            if '.json' in file:
                with open(f'{base_path}/{dir}/{file}', 'r') as f:
                    workout = json.load(f)
                    all_workouts[workout['program_module_id']] = workout
    return all_workouts

planned_nrc_workouts = get_completed_workouts('NRC')
planned_ntc_workouts = get_completed_workouts('NTC')


def get_planned_workout(workout, lib):
        if workout != 'Off':
            program_module_id = convert_workout_text_to_id(workout)
            if lib == 'NTC':
                if program_module_id in planned_ntc_workouts:
                    daily_workout = planned_ntc_workouts[program_module_id]
                else:
                    raise ValueError(f"Workout not found in library. Possible typo: {workout}")
            elif lib == 'NRC':
                if program_module_id in planned_nrc_workouts:
                    daily_workout = planned_nrc_workouts[program_module_id]
                else:
                    raise ValueError(f"Workout not found in library. Possible typo: {workout}")
            else:
                raise ValueError('invalid library name')
            return [daily_workout]
        return []

# get_all_workouts()