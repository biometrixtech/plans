from logic.periodization_processor import TargetLoadCalculator
from models.periodization import PeriodizationProgression, TrainingPhaseType
from models.training_volume import StandardErrorRange


def test_get_updated_session_load_target_normal():

    calc = TargetLoadCalculator()
    weekly_load_target = StandardErrorRange(lower_bound=1200, upper_bound=1700)
    load_this_week = StandardErrorRange(lower_bound=500, upper_bound=700)

    target_session_load = StandardErrorRange(lower_bound=300, upper_bound=400)

    new_target = calc.get_updated_session_load_target(weekly_load_target, target_session_load, load_this_week)
    assert 300 == new_target.lower_bound
    assert 350 == new_target.observed_value
    assert 400 == new_target.upper_bound


def test_get_updated_session_load_target_almost_met():

    calc = TargetLoadCalculator()
    weekly_load_target = StandardErrorRange(lower_bound=1200, upper_bound=1700)
    load_this_week = StandardErrorRange(lower_bound=1000, upper_bound=1400)

    target_session_load = StandardErrorRange(lower_bound=300, upper_bound=400)

    new_target = calc.get_updated_session_load_target(weekly_load_target, target_session_load, load_this_week)
    assert 200 == new_target.lower_bound
    assert 250 == new_target.observed_value
    assert 300 == new_target.upper_bound


def test_get_target_session_load_and_rate():

    calc = TargetLoadCalculator()
    average_session_load = StandardErrorRange(lower_bound=300, upper_bound=400)
    last_weeks_load = StandardErrorRange(lower_bound=1100, upper_bound=1600)
    weekly_load_target = StandardErrorRange(lower_bound=1200, upper_bound=1700)
    target_session_load, target_rate = calc.get_target_session_load_and_rate(average_session_load, last_weeks_load, weekly_load_target)

    # first need to understand how much the weekly load is increasing over last week.
    # in this case, smallest increase is from 1600 -> 1700 resulting in a net increase of 100 (rate of 1.0625)
    # lower bound of average session = 300 * 1.0625=318.75

    assert 318.75 == target_session_load.lower_bound
    assert 377.56 == round(target_session_load.observed_value, 2)
    assert 436.36 == round(target_session_load.upper_bound, 2)
    assert 1.09 == round(target_rate.lower_bound, 2)
    assert 1.08 == round(target_rate.observed_value, 2)
    assert 1.06 == round(target_rate.upper_bound, 2)


def test_get_target_session_rpe():

    calc = TargetLoadCalculator()
    average_session_rpe = StandardErrorRange(lower_bound=4, upper_bound=6, observed_value=5)
    progression = PeriodizationProgression(1, TrainingPhaseType.increase, rpe_load_contribution=0.20,
                                           volume_load_contribution=0.80)
    load_rate_increase = StandardErrorRange(lower_bound=1.25, upper_bound=1.33)
    session_rpe = calc.get_target_session_rpe(average_session_rpe, progression, load_rate_increase)

    # this is embarrassingly bad algebra, but it seems to get to the right answer
    # let's assume rpe=4, volume=100. session_rpe_load = 400
    # load_rate_increase = 1.25.  new_session_rpe_load = 500.  (net increase of session load is 100 or 25%)
    # new_session_rpe_load => volume represents 80% of the 25% increase or 20%; rpe increases 5%
    # if volume is 100% of the increase, volume = 125 (aka 4*125=500); diff is 125-100 = 25 * .8 = 120
    # if rpe is 100$ of the increase, rpe = 5; .2 of 5-4= 1 * .2 = 4.2
    # new rpe = 4*1.05 = 4.2; volume = 100 * 1.2 = 120; 4.2 * 120 = 504
    # final cleanup => 500/504 = .992
    # rpe=4.2*.992 = 4.167 => 4.17; volume = 120*.992 = 119.04

    assert 4.17 == round(session_rpe.lower_bound, 2)
    assert 5.26 == round(session_rpe.observed_value, 2)
    assert 6.35 == round(session_rpe.upper_bound, 2)


def test_get_target_session_volume():

    calc = TargetLoadCalculator()
    target_session_rpe = StandardErrorRange(lower_bound=4, upper_bound=6, observed_value=5)
    weekly_load_target = StandardErrorRange(lower_bound=800, upper_bound=1200, observed_value=1000)
    session_volume = calc.get_target_session_volume(min_workouts_week=3, max_workouts_week=5,
                                                    target_session_rpe=target_session_rpe,
                                                    weekly_load_target=weekly_load_target)
    # so let's say we have max 5 workouts a week.  weekly_load_target lower=800
    # that means lowest average session is 160 load units
    # if the highest value of the average rpe is 6, that means the lowest volume should be 26.67

    assert 26.67 == round(session_volume.lower_bound, 2)
    assert 63.33 == round(session_volume.observed_value, 2)
    assert 100 == round(session_volume.upper_bound, 2)


def test_get_weekly_load_target():

    calc = TargetLoadCalculator()
    average_rpe_load = StandardErrorRange(lower_bound=1000, upper_bound=2000, observed_value=1500)
    acwr_range = StandardErrorRange(lower_bound=.8, upper_bound=1.2)
    rpe_load = calc.get_weekly_load_target(average_training_load=average_rpe_load, acwr_range=acwr_range)

    assert 800 == rpe_load.lower_bound
    assert 1600 == rpe_load.observed_value
    assert 2400 == rpe_load.upper_bound
