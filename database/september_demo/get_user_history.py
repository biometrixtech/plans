import pandas as pd
from datetime import datetime, timedelta
from models.soreness_base import BodyPartLocation
from database.september_demo.get_workouts_for_persona import get_completed_workout


def get_soreness(persona):
    soreness_pd = pd.read_csv(f"personas/{persona}/symptom_reporting.csv")
    columns = soreness_pd.columns.values
    columns = [col.strip().lower() for col in columns]
    soreness_pd.columns = columns
    soreness_pd.fillna('', inplace=True)

    all_soreness = {}
    for i, row in soreness_pd.iterrows():
        if row['body_part'] is not None and row['body_part'] != "":
            if row['body_part'] == 'deltoids':
                row['body_part'] = 'deltoid'
            body_part = BodyPartLocation[row['body_part']].value
            side = 1 if row['body_part_side'].lower() == "left" else 2 if row['body_part_side'].lower() == 'right' else 0
            severity = int(row['severity'])
            tight = severity if row['tight'] == "x" else None
            knots = severity if row['knots'] == "x" else None
            ache = severity if row['ache'] == "x" else None
            sharp = severity if row['sharp'] == "x" else None
            soreness = {
                "body_part": body_part,
                "side": side,
                "tight": tight,
                "knots": knots,
                "sharp": sharp,
                "ache": ache
            }
            before_session = True if row['before/after workout'] == 'before' else False
            day = f"{int(row['week'])}_{row['day']}"
            if day not in all_soreness:
                all_soreness[day] = {
                    'before_session': [],
                    'after_session': []
                }
            if before_session:
                all_soreness[day]['before_session'].append(soreness)
            else:
                all_soreness[day]['after_session'].append(soreness)
    return all_soreness

def get_dates(days):
    dates = []
    today =  datetime.today()
    end_date = datetime(year=today.year, month=today.month, day=today.day)
    start_date = end_date - timedelta(days=days)


    delta = end_date - start_date

    for i in range(delta.days + 1):
        dates.append(start_date + timedelta(i))

    return dates

def get_user_data(persona='persona2a'):
    user_history = {}
    workout_history = pd.read_csv(f'personas/{persona}/workout_history.csv')
    soreness_history = get_soreness(persona)
    workout_history_length = len(workout_history)
    dates = get_dates(workout_history_length)
    for i, row in workout_history.iterrows():
        day = f"{row['Week']}_{row['Day']}"
        workout = get_completed_workout(row['Workout'], row['Library'])
        if day not in user_history:
            user_history[day] = {
                'workout': [],
                'soreness': None,
                'session_RPE': None,
                'date': None
            }
        user_history[day]['date'] = dates[i]
        user_history[day]['workout'] = workout
        user_history[day]['soreness'] = soreness_history.get(day)
        if len(workout) > 0:
            user_history[day]['session_RPE'] = float(row['sRPE'])
    return user_history

# user_history = get_user_data()
# print('here')