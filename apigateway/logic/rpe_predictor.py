import os
# import numpy as np
import joblib
import boto3

class RPEPredictor(object):
    def __init__(self, test=False):
        self.model = self.load_model(test)

    def load_model(self, test):
        bucket = boto3.resource('s3').Bucket('biometrix-globalmodels')
        if test:
            download_loc = os.path.join('..', 'data', 'hr_rpe.joblib')
        else:
            download_loc = '/tmp/hr_rpe.joblib'
        if not os.path.exists(download_loc):
            bucket.download_file('hr_rpe.joblib', download_loc)
        model = joblib.load(download_loc)

        return model

    def predict_rpe(self):
        print(self.model.n_features_)
        return self.model.predict([[1, 2, 3, 4, 5]])