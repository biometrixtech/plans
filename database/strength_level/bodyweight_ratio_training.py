import pandas as pd
import numpy as np
from joblib import dump
import copy
from sklearn.model_selection import cross_validate, train_test_split, cross_val_predict, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error

from sklearn.ensemble import GradientBoostingRegressor


def get_feature_names():
    features = [
        'bodyweight',
        'equipment_barbell', 'equipment_bodyweight', 'equipment_cable', 'equipment_dumbbells', 'equipment_machine',
        'gender', 'fitness_level_0', 'fitness_level_1', 'fitness_level_2', 'fitness_level_3', 'fitness_level_4'
    ]
    all_prime_movers = [
        21, 26, 33, 34, 40, 41, 42, 43, 44, 45, 46,
        47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
        57, 58, 60, 61, 63, 64, 65, 66, 69, 70,
        71, 72, 74, 75, 76, 78, 79, 81, 82, 83,
        84, 85, 122, 123, 124, 125, 126, 130, 131, 132
    ]
    for prime_mover in all_prime_movers:
        features.append(f"prime_mover_{prime_mover}")
        features.append(f"second_prime_mover_{prime_mover}")
        features.append(f"third_prime_mover_{prime_mover}")
    # 'prime_mover_21', 'second_prime_mover_21', 'third_prime_mover_21', 'prime_mover_26', 'second_prime_mover_26', 'third_prime_mover_26', 'prime_mover_33', 'second_prime_mover_33', 'third_prime_mover_33', 'prime_mover_34', 'second_prime_mover_34', 'third_prime_mover_34', 'prime_mover_40', 'second_prime_mover_40', 'third_prime_mover_40', 'prime_mover_41', 'second_prime_mover_41', 'third_prime_mover_41', 'prime_mover_42', 'second_prime_mover_42', 'third_prime_mover_42', 'prime_mover_43', 'second_prime_mover_43', 'third_prime_mover_43', 'prime_mover_44', 'second_prime_mover_44', 'third_prime_mover_44', 'prime_mover_45', 'second_prime_mover_45', 'third_prime_mover_45', 'prime_mover_46', 'second_prime_mover_46', 'third_prime_mover_46', 'prime_mover_47', 'second_prime_mover_47', 'third_prime_mover_47', 'prime_mover_48', 'second_prime_mover_48', 'third_prime_mover_48', 'prime_mover_49', 'second_prime_mover_49', 'third_prime_mover_49', 'prime_mover_50', 'second_prime_mover_50', 'third_prime_mover_50', 'prime_mover_51', 'second_prime_mover_51', 'third_prime_mover_51', 'prime_mover_52', 'second_prime_mover_52', 'third_prime_mover_52', 'prime_mover_53', 'second_prime_mover_53', 'third_prime_mover_53', 'prime_mover_54', 'second_prime_mover_54', 'third_prime_mover_54', 'prime_mover_55', 'second_prime_mover_55', 'third_prime_mover_55', 'prime_mover_56', 'second_prime_mover_56', 'third_prime_mover_56', 'prime_mover_57', 'second_prime_mover_57', 'third_prime_mover_57', 'prime_mover_58', 'second_prime_mover_58', 'third_prime_mover_58', 'prime_mover_60', 'second_prime_mover_60', 'third_prime_mover_60', 'prime_mover_61', 'second_prime_mover_61', 'third_prime_mover_61', 'prime_mover_63', 'second_prime_mover_63', 'third_prime_mover_63', 'prime_mover_64', 'second_prime_mover_64', 'third_prime_mover_64', 'prime_mover_65', 'second_prime_mover_65', 'third_prime_mover_65', 'prime_mover_66', 'second_prime_mover_66', 'third_prime_mover_66', 'prime_mover_69', 'second_prime_mover_69', 'third_prime_mover_69', 'prime_mover_70', 'second_prime_mover_70', 'third_prime_mover_70', 'prime_mover_71', 'second_prime_mover_71', 'third_prime_mover_71', 'prime_mover_72', 'second_prime_mover_72', 'third_prime_mover_72', 'prime_mover_74', 'second_prime_mover_74', 'third_prime_mover_74', 'prime_mover_75', 'second_prime_mover_75', 'third_prime_mover_75', 'prime_mover_76', 'second_prime_mover_76', 'third_prime_mover_76', 'prime_mover_78', 'second_prime_mover_78', 'third_prime_mover_78', 'prime_mover_79', 'second_prime_mover_79', 'third_prime_mover_79', 'prime_mover_81', 'second_prime_mover_81', 'third_prime_mover_81', 'prime_mover_82', 'second_prime_mover_82', 'third_prime_mover_82', 'prime_mover_83', 'second_prime_mover_83', 'third_prime_mover_83', 'prime_mover_84', 'second_prime_mover_84', 'third_prime_mover_84', 'prime_mover_85', 'second_prime_mover_85', 'third_prime_mover_85', 'prime_mover_122', 'second_prime_mover_122', 'third_prime_mover_122', 'prime_mover_123', 'second_prime_mover_123', 'third_prime_mover_123', 'prime_mover_124', 'second_prime_mover_124', 'third_prime_mover_124', 'prime_mover_125', 'second_prime_mover_125', 'third_prime_mover_125', 'prime_mover_126', 'second_prime_mover_126', 'third_prime_mover_126', 'prime_mover_130', 'second_prime_mover_130', 'third_prime_mover_130', 'prime_mover_131', 'second_prime_mover_131', 'third_prime_mover_131', 'prime_mover_132', 'second_prime_mover_132', 'third_prime_mover_132']
    return features

def train_model():
    data = pd.read_csv('full_bodyweight_ratio_data.csv')
    # return None
    y = data['average_ratio']
    del data['average_ratio']

    X_train, X_test, y_train, y_test = train_test_split(data, y, test_size=.2) #, random_state=20)
    print(X_test.shape, X_train.shape)
    test_exercise = X_test['exercise']
    test_equipment = X_test['equipment_bodyweight']
    features = get_feature_names()
    X_train = X_train[features]
    X_test = X_test[features]
    # test_equipment = X_test['equipment_Barbell']
    # del X_test['exercise'], X_train['exercise']
    data = data[features]
    regressor = GradientBoostingRegressor(
            # loss='huber',
            learning_rate=.05,
            max_depth=8,
            # alpha=.98,
            n_estimators=200,
            subsample=.75,
            # verbose=3,
            min_samples_split=10,
            min_samples_leaf=5
    )
    regressor.fit(X_train.values, y_train.values)
    # regressor.fit(data.values, y.values)

    print(regressor.score(X_test, y_test))
    dump(regressor, 'bodyweight_ratio.joblib')
    features = list(X_train.columns)
    print(features)
    print([(i, j) for i, j in zip(features, regressor.feature_importances_)])

    predictions_gb = regressor.predict(X_test.values)
    predictions_gb[predictions_gb < 0] = 0
    predictions_gb[predictions_gb > 10] = 10
    predictions_gb = predictions_gb.round(3)
    rmse = np.sqrt(mean_squared_error(y_test, predictions_gb))
    print("RMSE: %f" % (rmse))
    error = abs(y_test.values - predictions_gb)

    out = copy.deepcopy(X_test)

    out['real'] = y_test.values
    out['predicted'] = predictions_gb
    out['absolute_error'] = np.round(error, 3)
    out['percentage_error'] = np.round((out['absolute_error'] / out['real']) * 100, 1)
    out['exercise'] = test_exercise
    out['bodyweight_ex'] = test_equipment
    out.to_csv(f'prediction_GB_newdata.csv', columns=['exercise', 'bodyweight_ex', 'bodyweight', 'real', 'predicted', 'absolute_error', 'percentage_error'])
    result = pd.DataFrame({
        'pred': predictions_gb,
        'real': y_test.values,
        'absolute_error': error,
        'percentage_error': out['percentage_error'].values
    })
    print(result.describe(percentiles=[.25, .75, .9, .95, .99]))
    print(cross_val_score(regressor, data, y, cv=5))

if __name__ == '__main__':
    train_model()