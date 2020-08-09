from logic.periodization_processor import TargetLoadCalculator
from models.periodization import PeriodizationProgression, TrainingPhaseType
from models.training_load import TrainingLoad
from models.training_volume import StandardErrorRange


# TODO - VALIDATE!
def test_get_updated_session_load_target():

    calc = TargetLoadCalculator()
    weekly_load_target = StandardErrorRange(lower_bound=1200, upper_bound=1700)
    target_session_load = StandardErrorRange(lower_bound=300, upper_bound=400)
    load_this_week = StandardErrorRange(lower_bound=500, upper_bound=700)
    new_target = calc.get_updated_session_load_target(weekly_load_target, target_session_load, load_this_week)
    assert 300 == new_target.lower_bound
    assert 350 == new_target.observed_value
    assert 400 == new_target.upper_bound


# TODO - VALIDATE!
def test_get_target_session_load_and_rate():

    calc = TargetLoadCalculator()
    average_session_load = StandardErrorRange(lower_bound=300, upper_bound=400)
    last_weeks_load = StandardErrorRange(lower_bound=1100, upper_bound=1600)
    weekly_load_target = StandardErrorRange(lower_bound=1200, upper_bound=1700)
    target_session_load, target_rate = calc.get_target_session_load_and_rate(average_session_load, last_weeks_load, weekly_load_target)
    assert 575 == target_session_load.lower_bound
    assert 675.74 == round(target_session_load.observed_value, 2)
    assert 776.47 == round(target_session_load.upper_bound, 2)
    assert 0.92 == round(target_rate.lower_bound, 2)
    assert 0.93 == round(target_rate.observed_value, 2)
    assert 0.94 == round(target_rate.upper_bound, 2)


# TODO - VALIDATE!
def test_get_target_session_rpe():

    calc = TargetLoadCalculator()
    average_session_rpe = StandardErrorRange(lower_bound=4, upper_bound=6, observed_value=5)
    progression = PeriodizationProgression(1, TrainingPhaseType.increase, rpe_load_contribution=0.20,
                                           volume_load_contribution=0.80)
    rpe_load_rate_increase = StandardErrorRange(lower_bound=0.25, upper_bound=0.33)
    session_rpe = calc.get_target_session_rpe(average_session_rpe, progression, rpe_load_rate_increase)
    assert 4.2 == session_rpe.lower_bound
    assert 2.633 == session_rpe.observed_value
    assert 6.40 == round(session_rpe.upper_bound, 2)


# TODO - VALIDATE!
def test_get_target_session_volume():

    calc = TargetLoadCalculator()
    target_session_rpe = StandardErrorRange(lower_bound=4, upper_bound=6, observed_value=5)
    weekly_load_target = StandardErrorRange(lower_bound=800, upper_bound=1200, observed_value=1000)
    session_volume = calc.get_target_session_volume(min_workouts_week=3, max_workouts_week=5,
                                                    target_session_rpe=target_session_rpe,
                                                    weekly_load_target=weekly_load_target)
    assert 26.67 == round(session_volume.lower_bound, 2)
    assert 63.33 == round(session_volume.observed_value, 2)
    assert 100 == round(session_volume.upper_bound, 2)


# TODO - VALIDATE!
def test_get_weekly_load_target():

    calc = TargetLoadCalculator()
    average_rpe_load = StandardErrorRange(lower_bound=100, upper_bound=200, observed_value=150)
    acwr_range = StandardErrorRange(lower_bound=.8, upper_bound=1.2)
    rpe_load = calc.get_weekly_load_target(average_training_load=average_rpe_load, acwr_range=acwr_range)

    assert 80 == rpe_load.lower_bound
    assert 160 == rpe_load.observed_value
    assert 240 == rpe_load.upper_bound
