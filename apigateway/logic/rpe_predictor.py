import os
import joblib
import boto3
from fathomapi.api.config import Config
from fathomapi.utils.xray import xray_recorder

model_filename = Config.get('PROVIDER_INFO')['hr_rpe_model_filename']
model_bucket_name = Config.get('PROVIDER_INFO')['hr_rpe_model_bucket']


class RPEPredictor(object):
    def __init__(self):
        self.model = self.load_model()

    @xray_recorder.capture('logic.RPEPredictor.load_model')
    @classmethod
    def load_model(cls):
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            return None
        else:
            cls.download_file()
            model = joblib.load(cls.file_location())
            return model

    @staticmethod
    def file_location():
        if os.environ.get('UNIT_TESTS', '') == 'TRUE':
            file_location = os.path.join('..', 'data', model_filename)
        else:
            file_location = f'/tmp/{model_filename}'
        return file_location

    @classmethod
    @xray_recorder.capture('logic.RPEPredictor.download_file')
    def download_file(cls):
        bucket = boto3.resource('s3').Bucket(model_bucket_name)
        file_location = cls.file_location()
        if not os.path.exists(file_location):
            bucket.download_file(model_filename, file_location)

    @xray_recorder.capture('logic.RPEPredictor.predict_rpe')
    def predict_rpe(self, hr, user_weight=60.0, user_age=20.0, vo2_max=40.0, female=True):
        """

        :param hr:
        :param user_weight:
        :param user_age:
        :param vo2_max:
        :param female:
        :return:
        """
        if female:
            gender = 1.0
        else:
            gender = 0.0
        max_hr = 207 - .7 * user_age
        percent_max_hr = hr / max_hr
        features = [[gender, user_weight, vo2_max, max_hr, percent_max_hr]]
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            return 4
        else:
            predicted_rpe = self.model.predict(features)[0]
            if predicted_rpe < 0:
                predicted_rpe = 0
            predicted_rpe = round(predicted_rpe, 1)
            return predicted_rpe