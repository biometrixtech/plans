import sklearn
import numpy as np
import joblib
print(sklearn.__version__)
import boto3

def predict():
    bucket = boto3.resource('s3').Bucket('biometrix-globalmodels')
    bucket.download_file('hr_rpe.joblib','/tmp/hr_rpe.joblib')
    model = joblib.load('/tmp/hr_rpe.joblib')
    print(model.n_features_)
    print(model.predict(np.array([[1, 2, 3, 4, 5]])))
    return model

predict()
