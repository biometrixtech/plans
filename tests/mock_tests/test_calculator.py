from logic.calculators import Calculators


def test_percent_max_hr_from_rpe():
    prev_perc = 0
    for i in range(0, 100):
        rpe = i / 10
        perc_max_hr = Calculators.get_percent_max_hr_from_rpe(rpe)
        assert perc_max_hr >= prev_perc
        prev_perc = perc_max_hr


def test_rowing_work_vo2_from_power():
    work_vo2 = Calculators.work_vo2_rowing_from_power(250, 70)
    assert work_vo2 > 0
