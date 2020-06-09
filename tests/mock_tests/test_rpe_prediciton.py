from logic.rpe_predictor import RPEPredictor


def test_load():
    predictor = RPEPredictor(test=True)
    rpe = predictor.predict_rpe()
    assert rpe
    print('here')