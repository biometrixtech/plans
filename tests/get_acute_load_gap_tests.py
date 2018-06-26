import pytest
import training

# athlete has 28 days of data plus has data in current week


def test_acute_load_calc_within_ramp_28_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [50, 50, 50, 50]
    expected_remaining_load = [14.5, None, 10, 10]
    # 72.5 (target) - 54.5 = 18, but since we only want to ramp up 10%, target will be reduced to 0.5
    target_load = 0.5
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_fully_ramped_28_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [50, 50, 50, 50]
    expected_remaining_load = [15, None, 10, 10]
    # 72.5 (target) - 55 = 17.5, but since we only want to ramp up 10%, target will be reduced to 0.0
    target_load = 0.0
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_overreaching_28_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [50, 50, 50, 50]
    expected_remaining_load = [25, None, 25, 25]
    # 72.5 (target) - 95 = -22.5; want to return a negative number to indicate athlete is overreaching
    target_load = -22.5
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


# athlete has 28 days of data plus no data (yet) in current week


def test_acute_load_calc_within_ramp_28_none():
    calc = training.Calculator()
    acute_load = [None, None]
    chronic_load = [50, 50, 50, 50]
    expected_remaining_load = [10, 10, 14.5, 10, 10]
    # 72.5 (target) - 54.5 = 18, but since we only want to ramp up 10%, target will be reduced to 0.5
    target_load = 0.5
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_fully_ramped_28_none():
    calc = training.Calculator()
    acute_load = [None, None]
    chronic_load = [50, 50, 50, 50]
    expected_remaining_load = [10, 10, 15, 10, 10]
    # 72.5 (target) - 55 = 17.5, but since we only want to ramp up 10%, target will be reduced to 0.0
    target_load = 0.0
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_overreaching_28_none():
    calc = training.Calculator()
    acute_load = [None, None]
    chronic_load = [50, 50, 50, 50]
    expected_remaining_load = [10, 10, 25, 25, 25]
    # 72.5 (target) - 95 = -22.5; want to return a negative number to indicate athlete is overreaching
    target_load = -22.5
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load

# athlete has 21 days of data plus has data in current week


def test_acute_load_calc_within_ramp_21_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [None, 50, 50, 50]
    expected_remaining_load = [14.5, None, 10, 10]
    # 72.5 (target) - 54.5 = 18, but since we only want to ramp up 10%, target will be reduced to 0.5
    target_load = 0.5
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_fully_ramped_21_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [None, 50, 50, 50]
    expected_remaining_load = [15, None, 10, 10]
    # 72.5 (target) - 55 = 17.5, but since we only want to ramp up 10%, target will be reduced to 0.0
    target_load = 0.0
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_overreaching_21_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [None, 50, 50, 50]
    expected_remaining_load = [25, None, 25, 25]
    # 72.5 (target) - 95 = -22.5; want to return a negative number to indicate athlete is overreaching
    target_load = -22.5
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


# athlete has 14 days of data plus has data in current week


def test_acute_load_calc_within_ramp_14_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [None, None, 50, 50]
    expected_remaining_load = [14.5, None, 10, 10]
    # 72.5 (target) - 54.5 = 18, but since we only want to ramp up 10%, target will be reduced to 0.5
    target_load = 0.5
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_fully_ramped_14_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [None, None, 50, 50]
    expected_remaining_load = [15, None, 10, 10]
    # 72.5 (target) - 55 = 17.5, but since we only want to ramp up 10%, target will be reduced to 0.0
    target_load = 0.0
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_overreaching_14_plus():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [None, None, 50, 50]
    expected_remaining_load = [25, None, 25, 25]
    # 72.5 (target) - 95 = -22.5; want to return a negative number to indicate athlete is overreaching
    target_load = -22.5
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


# athlete has too few of data plus has data in current week


def test_acute_load_calc_0_plus_too_few_days():
    calc = training.Calculator()
    acute_load = [10, 10]
    chronic_load = [None, None, None, None]
    expected_remaining_load = [14.5, None, 10, 10]
    target_load = None
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_only_1_week():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [None, None, None, 50]
    expected_remaining_load = [14.5, None, 10, 10]
    target_load = None
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load


def test_acute_load_calc_0_weeks():
    calc = training.Calculator()
    acute_load = [10, None, 10]
    chronic_load = [None, None, None, None]
    expected_remaining_load = [14.5, None, 10, 10]
    target_load = None
    assert calc.get_acute_load_gap(acute_load, chronic_load, expected_remaining_load) == target_load

