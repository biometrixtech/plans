import pandas as pd
from datetime import datetime
from database.september_demo.get_workouts_for_persona import get_planned_workout
from utils import format_date


def get_planned_user_workouts(persona='demo1'):
    user_history = {}
    workout_history = pd.read_csv(f'personas/{persona}/workout_history.csv')
    workout_history.fillna('', inplace=True)


    for i, row in workout_history.iterrows():
        if row['event_date_time'] != "":
            date = row['event_date_time']
            date = date.split('/')
            date = datetime(year=2020, month=int(date[0]), day=int(date[1]))
            day = format_date(date)
            if row['NRC Workout'] != '':

                workout = get_planned_workout(row['NRC Workout'], 'NRC')
                if day not in user_history:
                    user_history[day] = {
                        'planned_workouts': []
                    }
                user_history[day]['planned_workouts'].append(workout)
    return user_history

# user_history = get_user_data()
# print('here')