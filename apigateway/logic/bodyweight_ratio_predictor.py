import os
from datastores.ml_model_datastore import MLModelsDatastore
from fathomapi.utils.xray import xray_recorder
from models.movement_tags import Gender



non_prime_mover_features = [
    'bodyweight',
    'equipment_barbells', 'equipment_bodyweight', 'equipment_cable', 'equipment_dumbbells', 'equipment_machine',
    'gender']
all_prime_movers = [
    21, 26, 34, 40, 41, 42, 43, 44, 45, 46,
    47, 48, 49, 50, 51, 52, 53, 54, 55, 56,
    57, 58, 60, 61, 63, 64, 65, 66, 69, 70,
    71, 72, 74, 75, 76, 78, 79, 81, 82, 83,
    84, 85, 122, 123, 124, 125, 126, 130, 131, 132
]


class BodyWeightRatioPredictor(object):
    def __init__(self):
        self.model = MLModelsDatastore.get_bodyweight_ratio_model()

    @xray_recorder.capture('logic.BodyWeightRatioPredictor.predict_bodyweight_ratio')
    def predict_bodyweight_ratio(self, user_weight, gender, prime_movers, equipment):
        """

        :param user_weight:
        :param gender:
        :param prime_movers:
        :param equipment:
        :return:
        """
        if os.environ.get('CODEBUILD_RUN', '') == 'TRUE':
            return .5
        else:
            gender = 1.0 if gender.name == 'female' else 0.0
            equipment_barbells = 0.0
            equipment_bodyweight = 0.0
            equipment_cable = 0.0
            equipment_dumbbells = 0.0
            equipment_machine = 0.0
            if equipment.name == 'barbells':
                equipment_barbells = 1.0
            if equipment.name == 'bodyweight':
                equipment_bodyweight = 1.0
            if equipment.name == 'cable':
                equipment_cable = 1.0
            if equipment.name == 'dumbbells':
                equipment_dumbbells = 1.0
            if equipment.name == 'machine':
                equipment_machine = 1.0
            features = [user_weight, equipment_barbells, equipment_bodyweight, equipment_cable, equipment_dumbbells, equipment_machine, gender]
            prime_movers_features = self.get_prime_movers_features(prime_movers)
            features.extend(prime_movers_features)
            predicted_ratio = self.model.predict([features])[0]
            if predicted_ratio < 0:
                predicted_ratio = 0
            predicted_ratio = round(predicted_ratio, 3)
            return predicted_ratio

    @classmethod
    def get_prime_movers_features(cls, prime_movers):
        prime_mover_features = {}
        for prime_mover in prime_movers['first_prime_movers']:
            prime_mover_features[f"prime_mover_{prime_mover}"] = 1
        for second_prime_mover in prime_movers['second_prime_movers']:
            prime_mover_features[f"second_prime_mover_{second_prime_mover}"] = 1
        for third_prime_mover in prime_movers['third_prime_movers']:
            prime_mover_features[f"third_prime_mover_{third_prime_mover}"] = 1
        all_prime_mover_features = []
        for pm in all_prime_movers:
            all_prime_mover_features.append(prime_mover_features.get(f"prime_mover_{pm}", 0))
            all_prime_mover_features.append(prime_mover_features.get(f"second_prime_mover_{pm}", 0))
            all_prime_mover_features.append(prime_mover_features.get(f"third_prime_mover_{pm}", 0))
        return all_prime_mover_features
