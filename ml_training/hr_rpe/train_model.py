import os
import pandas as pd
from sklearn.ensemble import GradientBoostingRegressor
from joblib import dump
import boto3


def prepare_data():
    file_name = 'hr_rpe_data.csv'
    if not os.path.exists('data'):
        os.mkdir('data')
    data_file_location = f'data/{file_name}'
    if not os.path.exists(data_file_location):
        bucket = boto3.resource('s3').Bucket('biometrix-hr-rpe-data')
        bucket.download_file(file_name, data_file_location)
    data = pd.read_csv(data_file_location)
    print(data.shape)
    data = data[data.age > 15]
    print(data.shape)
    data.dropna(inplace=True)
    print(data.shape)
    data.max_hr /= 207
    data.rpe = data.rpe.replace({6: 0, 7: 0, 8: 1, 9: 1, 10: 2, 11: 2, 12: 3, 13: 3, 14: 4, 15: 5, 16: 6, 17: 7, 18: 8, 19: 9, 20: 10})
    data = pd.get_dummies(data, columns=['gender'])
    data = data.drop(columns=['gender_1.0'])
    data = data.round(2)
    data.rename(columns={'gender_2.0': 'gender'}, inplace=True)

    features = [
        'gender',
        'weight',
        'vo2_max',
        'max_hr',
        'percent_max_hr'
    ]
    X = data.loc[:, features]

    y = data.loc[:, 'rpe']

    return X, y


def train_gb(X, y):
    regressor = GradientBoostingRegressor(
            loss='huber',
            learning_rate=.07,
            max_depth=8,
            alpha=.98,
            n_estimators=800,
            subsample=.95,
            verbose=3
    )
    regressor.fit(X.values, y.values)

    return regressor


def get_model():
    if not os.path.exists('model'):
        os.mkdir('model')
    model_filename = 'model/hr_rpe.joblib'
    X, y= prepare_data()
    gb_regressor = train_gb(X, y)
    dump(gb_regressor, model_filename)


if __name__ == '__main__':
    get_model()
