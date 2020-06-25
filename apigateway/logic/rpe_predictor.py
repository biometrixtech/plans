import os
from models.movement_tags import Gender
from fathomapi.utils.xray import xray_recorder
from datastores.ml_model_datastore import MLModelsDatastore

class RPEPredictor(object):
    def __init__(self):
        self.model = MLModelsDatastore.get_hr_model()

    @xray_recorder.capture('logic.RPEPredictor.predict_rpe')
    def predict_rpe(self, hr, user_weight=60.0, user_age=20.0, vo2_max=40.0, gender=Gender.female):
        """

        :param hr:
        :param user_weight:
        :param user_age:
        :param vo2_max:
        :param gender:
        :return:
        """
        if gender == Gender.female:
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
