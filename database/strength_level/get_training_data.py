"""
Before running download csvs from https://docs.google.com/spreadsheets/d/1nWFT78tuIdp6RJrx9lL2tvZSUOfX0d42tNf_jwJEHZI/edit#gid=1486386156
Save 'detailed weighted' tab as weighted_exercises.csv and
'Detailed Bodyweight' tab as bodyweight_exercises.csv

"""
import pandas as pd
import numpy as np

from sklearn.utils import shuffle


def add_prime_movers(data):
    all_prime_movers = [
        21, 26, 33, 34, 40, 41, 42, 43, 44, 45, 46,
        47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
        57, 58, 60, 61, 63, 64, 65, 66, 69, 70,
        71, 72, 74, 75, 76, 78, 79, 81, 82, 83,
        84, 85, 122, 123, 124, 125, 126, 130, 131, 132]
    for prime_mover in all_prime_movers:
        data[f'prime_mover_{prime_mover}'] = 0
        data[f'second_prime_mover_{prime_mover}'] = 0
        data[f'third_prime_mover_{prime_mover}'] = 0
    new_prime_movers = set()
    for index, row in data.iterrows():
        if row['prime_movers'] is not np.nan:
            prime_movers = row['prime_movers'].replace(', ', ',').replace(" ", "")
            prime_movers = prime_movers.split(',')
            for prime_mover in prime_movers:
                data.loc[index, f"prime_mover_{prime_mover.strip()}"] = 1
        if row['second_prime_movers'] is not np.nan:
            second_prime_movers = row['second_prime_movers'].replace(', ', ',').replace(" ", "")
            second_prime_movers = second_prime_movers.split(',')
            for second_prime_mover in second_prime_movers:
                data.loc[index, f"second_prime_mover_{second_prime_mover.strip()}"] = 1
        if row['third_prime_movers'] is not np.nan:
            third_prime_movers = row['third_prime_movers'].replace(', ', ',').replace(" ", "")
            third_prime_movers = third_prime_movers.split(',')
            for third_prime_mover in third_prime_movers:
                data.loc[index, f"third_prime_mover_{third_prime_mover.strip()}"] = 1


def combine_and_clean_data():

    weighted_exercises = pd.read_csv('weighted_exercises.csv',
                                     usecols=['gender', 'exercise', 'equipment',
                                              'bodyweight',
                                              'Beginner Ratio', 'Novice Ratio', 'Intermediate Ratio', 'Advanced Ratio', 'Elite Ratio',
                                              ]
                                     )

    weighted_exercises.rename(columns={
        'Beginner Ratio': '0',
        'Novice Ratio': '1',
        'Intermediate Ratio': '2',
        'Advanced Ratio': '3',
        'Elite Ratio': '4'
    }, inplace=True)
    weighted_exercises = weighted_exercises.melt(id_vars=['gender', 'exercise', 'equipment', 'bodyweight'])
    weighted_exercises.rename(columns={
        'variable': 'fitness_level',
        'value': 'average_ratio'
    }, inplace=True)

    bodyweight_exercises = pd.read_csv('bodyweight_exercises.csv',
                                       usecols=['gender', 'exercise', 'equipment',
                                                'bodyweight',
                                                'Beg 1RM Ratio', 'Novice 1RM Ratio', 'Inter 1RM Ratio', 'Advanced 1RM Ratio', 'Elite 1RM Ratio'
                                                ]
                                       )

    bodyweight_exercises.rename(columns={
        'Beg 1RM Ratio': '0',
        'Novice 1RM Ratio': '1',
        'Inter 1RM Ratio': '2',
        'Advanced 1RM Ratio': '3',
        'Elite 1RM Ratio': '4'
    }, inplace=True)
    bodyweight_exercises = bodyweight_exercises.melt(id_vars=['gender', 'exercise', 'equipment', 'bodyweight'])
    bodyweight_exercises.rename(columns={
        'variable': 'fitness_level',
        'value': 'average_ratio'
    }, inplace=True)

    data = weighted_exercises.append(bodyweight_exercises)
    data.exercise = data.exercise.str.lower()
    prime_movers = pd.read_csv('strengthlevel_primemovers.csv')

    data = data.merge(prime_movers, on='exercise', how='left')
    data.bodyweight /= 2.204  # convert to kg
    data.bodyweight = data.bodyweight.round(1)
    data.average_ratio = data.average_ratio.round(3)
    data.dropna(subset=['prime_movers'], inplace=True)
    data = pd.get_dummies(data, prefix=['equipment'], columns=['equipment'])
    if 'equipment_Cable' not in data.columns:
        data['equipment_Cable'] = 0
    if 'equipment_Machine' not in data.columns:
        data['equipment_Machine'] = 0
    # if 'equipment_cable' not in data.columns:
    #     data['equipment_cable'] = 0
    data = pd.get_dummies(data, prefix=['gender'], columns=['gender'])
    data = pd.get_dummies(data, prefix=['fitness_level'], columns=['fitness_level'])
    data = data.drop(columns=['gender_Male'])
    data.rename(columns={'gender_Female': 'gender'}, inplace=True)
    # data = data[['exercise', 'bodyweight', 'average_ratio', ]]
    add_prime_movers(data)
    data.fillna(0, inplace=True)
    del data['prime_movers'], data['second_prime_movers'], data['third_prime_movers'], data['fourth_prime_movers']
    data = shuffle(data)
    data.columns = data.columns.str.lower()
    data.to_csv('full_bodyweight_ratio_data.csv', index=False)
    return data


if __name__ == '__main__':
    combine_and_clean_data()
