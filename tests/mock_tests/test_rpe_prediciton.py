from logic.rpe_predictor import RPEPredictor


def test_load():
    predictor = RPEPredictor()
    rpe = predictor.predict_rpe(140)
    assert rpe