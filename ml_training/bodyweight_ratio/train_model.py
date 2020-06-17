import os
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from joblib import dump
import boto3


def prepare_data():
    file_name = 'full_bodyweight_ratio_data.csv'
    if not os.path.exists('data'):
        os.mkdir('data')
    data_file_location = f'data/{file_name}'
    if not os.path.exists(data_file_location):
        bucket = boto3.resource('s3').Bucket('biometrix-bodyweight-ratio-data')
        bucket.download_file(file_name, data_file_location)
    data = pd.read_csv(data_file_location)
    features = [
        'bodyweight',
        'equipment_barbell', 'equipment_bodyweight', 'equipment_cable', 'equipment_dumbbells', 'equipment_machine',
        'gender']
    all_prime_movers = [
        21, 26, 34, 40, 41, 42, 43, 44, 45, 46,
        47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
        57, 58, 60, 61, 63, 64, 65, 66, 69, 70,
        71, 72, 74, 75, 76, 78, 79, 81, 82, 83,
        84, 85, 122, 123, 124, 125, 126, 130, 131, 132
    ]
    for pm in all_prime_movers:
        features.append(f"prime_mover_{pm}")
        features.append(f"second_prime_mover_{pm}")
        features.append(f"third_prime_mover_{pm}")
    X = data.loc[:, features]
    y = data.loc[:, 'average_ratio']

    return X, y


def train_gb(X, y):
    regressor = GradientBoostingRegressor(
            learning_rate=.05,
            max_depth=8,
            n_estimators=200,
            subsample=.75,
            min_samples_split=10,
            min_samples_leaf=5
    )
    regressor.fit(X, y)

    return regressor


def get_model():
    if not os.path.exists('model'):
        os.mkdir('model')
    model_filename = 'model/bodyweight_ratio.joblib'
    X, y = prepare_data()
    gb_regressor = train_gb(X, y)
    dump(gb_regressor, model_filename)


if __name__ == '__main__':
    get_model()
