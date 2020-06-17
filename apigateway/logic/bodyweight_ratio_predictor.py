import os
from datastores.ml_model_datastore import MLModelsDatastore
from fathomapi.utils.xray import xray_recorder

class BodyWeightRatioPredictor(object):
    def __init__(self):
        self.model = MLModelsDatastore.get_bodyweight_ratio_model()

    @xray_recorder.capture('logic.BodyWeightRatioPredictor.predict_bodyweight_ratio')
    def predict_bodyweight_ratio(self, features):
        """
        :return:
        """
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            return .5
        else:
            predicted_ratio = self.model.predict(features)[0]
            if predicted_ratio < 0:
                predicted_ratio = 0
            predicted_ratio = round(predicted_ratio, 3)
            return predicted_ratio
