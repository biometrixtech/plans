import os
import boto3
import joblib

from fathomapi.api.config import Config
from fathomapi.utils.xray import xray_recorder

model_bucket_name = Config.get('PROVIDER_INFO')['model_bucket']
hr_rpe_model_filename = Config.get('PROVIDER_INFO')['hr_rpe_model_filename']
bodyweight_ratio_model_filename = Config.get('PROVIDER_INFO')['bodyweight_ratio_model_filename']

_hr_rpe_model = None
_bodyweight_model = None


class MLModelsDatastore(object):
    @xray_recorder.capture('logic.MLModelsDatastore.get_hr_model')
    @classmethod
    def get_hr_model(cls):
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            return None
        else:
            global _hr_rpe_model
            if _hr_rpe_model is None:
                _hr_rpe_model = cls.download_and_load_model(hr_rpe_model_filename)
            return _hr_rpe_model

    @xray_recorder.capture('logic.MLModelsDatastore.get_bodyweight_ratio_model')
    @classmethod
    def get_bodyweight_ratio_model(cls):
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            return None
        else:
            global _bodyweight_model
            if _bodyweight_model is None:
                _bodyweight_model = cls.download_and_load_model(bodyweight_ratio_model_filename)
            return _bodyweight_model

    @xray_recorder.capture('logic.MLModelsDatastore.load_models')
    @classmethod
    def load_models(cls):
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            pass
        else:
            global _hr_rpe_model
            global _bodyweight_model
            if _hr_rpe_model is None:
                _hr_rpe_model = cls.download_and_load_model(hr_rpe_model_filename)
                print('downloaded_hr_model')
            if _bodyweight_model is None:
                _bodyweight_model = cls.download_and_load_model(bodyweight_ratio_model_filename)
                print('downloaded_bodyweight_model')

    @classmethod
    def download_and_load_model(cls, model_filename):
        cls.download_file(model_filename)
        model = joblib.load(cls.file_location(model_filename))
        return model

    @staticmethod
    def file_location(model_filename):
        if os.environ.get('UNIT_TESTS', '') == 'TRUE':
            file_location = os.path.join('..', 'data', model_filename)
        else:
            file_location = f'/tmp/{model_filename}'
        return file_location

    @classmethod
    @xray_recorder.capture('logic.MLModelsDatastore.download_file')
    def download_file(cls, model_filename):
        bucket = boto3.resource('s3').Bucket(model_bucket_name)
        file_location = cls.file_location(model_filename)
        if not os.path.exists(file_location):
            bucket.download_file(f"plans/{model_filename}", file_location)
