from models.movement_tags import Equipment, Gender
from logic.bodyweight_ratio_predictor import BodyWeightRatioPredictor


def test_prime_movers_features():

    prime_movers = {
        "first_prime_movers": {21},
        "second_prime_movers": set(),
        "third_prime_movers": {21},
        "fourth_prime_movers": set()
    }
    prime_mover_features = BodyWeightRatioPredictor.get_prime_movers_features(prime_movers)
    assert prime_mover_features[0] == 1
    assert prime_mover_features[1] == 0
    assert prime_mover_features[2] == 1


def test_prediction():
    prime_movers = {
        "first_prime_movers": {21},
        "second_prime_movers": set(),
        "third_prime_movers": {21},
        "fourth_prime_movers": set()
    }
    bodyweight = 70
    equipment = Equipment.barbells
    rm_ratio = BodyWeightRatioPredictor().predict_bodyweight_ratio(bodyweight, Gender.female, prime_movers, equipment)
    assert rm_ratio > 0
