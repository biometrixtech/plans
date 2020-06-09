import os
# import numpy as np
import joblib
import boto3
from fathomapi.utils.xray import xray_recorder

class RPEPredictor(object):
    def __init__(self):
        self.model = self.load_model()

    @xray_recorder.capture('logic.RPEPredictor.load_model')
    def load_model(self):
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            return None
        else:
            bucket = boto3.resource('s3').Bucket('biometrix-globalmodels')
            if os.environ.get('UNIT_TESTS', '') == 'TRUE':
                download_loc = os.path.join('..', 'data', 'hr_rpe.joblib')
            else:
                download_loc = '/tmp/hr_rpe.joblib'
            if not os.path.exists(download_loc):
                bucket.download_file('hr_rpe.joblib', download_loc)
            model = joblib.load(download_loc)

            return model

    @xray_recorder.capture('logic.RPEPredictor.predict_rpe')
    def predict_rpe(self, hr, user_weight=60.0, user_age=20.0, vo2_max=40.0, female=True):
        if female:
            gender = 1.0
        else:
            gender = 0.0
        max_hr = 207 - .7 * user_age
        percent_max_hr = hr / max_hr
        prediction_features = [[user_age, user_weight, gender, percent_max_hr, vo2_max]]
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            print('here')
            return 5
        else:
            predicted_rpe = self.model.predict(prediction_features)
            print(prediction_features, predicted_rpe)
            return predicted_rpe