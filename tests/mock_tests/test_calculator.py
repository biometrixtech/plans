from logic.calculators import Calculators
from models.movement_tags import Gender, CardioAction
from models.training_volume import StandardErrorRange


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


def test_watts_to_mets_and_watts_to_mets():
    assert Calculators.watts_to_mets(Calculators.mets_to_watts(mets=10, weight=70), weight=70) == 10
    assert Calculators.watts_to_mets(Calculators.mets_to_watts(mets=10, weight=70, efficiency=.2), weight=70, efficiency=.2) == 10
    assert Calculators.watts_to_mets(Calculators.mets_to_watts(mets=1.5, weight=70, efficiency=.2), weight=70, efficiency=.2) == 1.5
    assert Calculators.watts_to_mets(Calculators.mets_to_watts(mets=1000, weight=70, efficiency=.2), weight=70, efficiency=.2) == 1000


def test_mets_to_watts():
    watts1 = Calculators.mets_to_watts(mets=10, weight=70, efficiency=.2)
    watts2 = Calculators.mets_to_watts(mets=10.0, weight=70, efficiency=.2)
    watts3 = Calculators.mets_to_watts(mets=2, weight=70, efficiency=1.0)
    assert watts1 == watts2 == watts3


def test_mets_to_watts_fractions():
    watts1 = Calculators.mets_to_watts(mets=.5, weight=70, efficiency=.2)
    watts2 = Calculators.mets_to_watts(mets=1/2, weight=70, efficiency=.2)
    assert watts1 == watts2


def test_watts_to_mets():
    watts1 = Calculators.watts_to_mets(watts=10, weight=70, efficiency=.2)
    watts2 = Calculators.watts_to_mets(watts=10.0, weight=70, efficiency=.2)
    watts3 = Calculators.watts_to_mets(watts=10.0001, weight=70, efficiency=.2)
    watts4 = Calculators.watts_to_mets(watts=50, weight=70, efficiency=1.0)
    assert watts1 == watts2 == watts3 == watts4


def test_watts_to_mets_fractions():
    watts1 = Calculators.watts_to_mets(watts=.5, weight=70, efficiency=.2)
    watts2 = Calculators.watts_to_mets(watts=1/2, weight=70, efficiency=.2)
    watts3 = Calculators.watts_to_mets(watts=5/10, weight=70, efficiency=.2)
    assert watts1 == watts2 == watts3


def test_mets_cardio_male_female_difference():
    male_mets = Calculators.mets_cardio(cardio_type='row', gender=Gender.male)
    female_mets = Calculators.mets_cardio(cardio_type='row', gender=Gender.female)

    assert male_mets == female_mets + 1


def test_mets_cardio():
    sprint_mets = Calculators.mets_cardio(cardio_type='sprint')
    run_mets = Calculators.mets_cardio(cardio_type='run')
    ruck_mets = Calculators.mets_cardio(cardio_type='ruck')

    assert sprint_mets > run_mets > ruck_mets


def test_work_vo2_cycling_alternate():
    work_vo2 = Calculators.work_vo2_cycling_alternate(power=500, weight=60)
    work_vo2_2 = Calculators.work_vo2_cycling_alternate(power=50, weight=60)

    assert round(work_vo2 - 3.5, 1) == round((work_vo2_2 - 3.5) * 10, 1)


def test_work_vo2_running_alternate_different_speed_and_grade():
    work_vo2_1 = Calculators.work_vo2_running_alternate(speed=1.7, grade=.01)
    work_vo2_2 = Calculators.work_vo2_running_alternate(speed=1.8, grade=.01)
    work_vo2_3 = Calculators.work_vo2_running_alternate(speed=1.7, grade=0)

    assert work_vo2_2 > work_vo2_1 > work_vo2_3


def test_work_vo2_running_alternate_fractions():
    work_vo2_1 = Calculators.work_vo2_running_alternate(speed=.5, grade=.3)
    work_vo2_2 = Calculators.work_vo2_running_alternate(speed=1/2, grade=3/10)
    work_vo2_3 = Calculators.work_vo2_running_alternate(speed=2/4, grade=.3)

    assert work_vo2_1 == work_vo2_2 == work_vo2_3


def test_work_vo2_rowing_from_power():
    work_vo2_1 = Calculators.work_vo2_rowing_from_power(power=100, weight=50)
    work_vo2_2 = Calculators.work_vo2_rowing_from_power(power=10, weight=50)
    assert round(work_vo2_1, 0) == round(work_vo2_2 * 10, 0)


def test_power_cardio_run():
    power_sprint = Calculators.power_cardio(cardio_type=CardioAction.sprint, user_weight=70)
    power_run = Calculators.power_cardio(cardio_type=CardioAction.run, user_weight=70)
    power_ruck = Calculators.power_cardio(cardio_type=CardioAction.ruck, user_weight=70)
    assert power_sprint > power_run > power_ruck


def test_power_cardio_no_type():
    user_weight = 70
    eff = .21
    power_male = Calculators.power_cardio(cardio_type=None, user_weight=user_weight, gender=Gender.male)
    assert power_male == Calculators.mets_to_watts(mets=5, weight=user_weight, efficiency=eff)
    power_female = Calculators.power_cardio(cardio_type=None, user_weight=user_weight)
    assert power_female == Calculators.mets_to_watts(mets=4, weight=user_weight, efficiency=eff)


def test_power_running_all_present():
    power = Calculators.power_running(speed=1, grade=.1, user_weight=70)
    assert power is not None
    assert power > 0


def test_power_running_no_weight():
    power = Calculators.power_running(speed=1, grade=.1)
    assert power is not None
    assert power > 0


def test_power_running_no_grade():
    power = Calculators.power_running(speed=1, user_weight=70)
    assert power is not None
    assert power > 0


def test_power_running_speed_only():
    power = Calculators.power_running(speed=1,)
    assert power is not None
    assert power > 0


def test_power_cycling():
    power1 = Calculators.power_cycling(speed=1, user_weight=70, grade=.1, wind_speed=.1, cycle_weight=10, altitude=100, handlebar_position='hoods')
    power2 = Calculators.power_cycling(speed=1, user_weight=70, grade=.1, wind_speed=.1, cycle_weight=10, altitude=100)
    power3 = Calculators.power_cycling(speed=1, user_weight=70, grade=.1, wind_speed=.1, cycle_weight=10)
    power4 = Calculators.power_cycling(speed=1, user_weight=70, grade=.1, wind_speed=.1)
    power5 = Calculators.power_cycling(speed=1, user_weight=70)
    power6 = Calculators.power_cycling(speed=1)

    assert power1 is not None and power1 > 0
    assert power2 is not None and power2 > 0
    assert power3 is not None and power3 > 0
    assert power4 is not None and power4 > 0
    assert power5 is not None and power5 > 0
    assert power6 is not None and power6 > 0


def test_power_rowing():
    power1 = Calculators.power_rowing(speed=10)
    power2 = Calculators.power_rowing(speed=11)
    assert power2 > power1


def test_vo2_max_estimation_demographics():
    vo2_max_1 = Calculators.vo2_max_estimation_demographics(age=25, user_weight=50, user_height=1.7, gender=Gender.female, activity_level=3)
    vo2_max_2 = Calculators.vo2_max_estimation_demographics(age=25, user_weight=50, user_height=1.7, gender=Gender.female)
    vo2_max_3 = Calculators.vo2_max_estimation_demographics(age=25, user_weight=50, user_height=1.7)
    vo2_max_4 = Calculators.vo2_max_estimation_demographics(age=25, user_weight=50)
    assert vo2_max_1 is not None
    assert 0 < vo2_max_1.lower_bound < vo2_max_1.observed_value < vo2_max_1.upper_bound
    assert vo2_max_2 is not None
    assert 0 < vo2_max_2.lower_bound < vo2_max_2.observed_value < vo2_max_2.upper_bound
    assert vo2_max_3 is not None
    assert 0 < vo2_max_3.lower_bound < vo2_max_3.observed_value < vo2_max_3.upper_bound
    assert vo2_max_4 is not None
    assert 0 < vo2_max_4.lower_bound < vo2_max_4.observed_value < vo2_max_4.upper_bound


def test_vo2max_schembre():
    vo2_max_1 = Calculators.vo2max_schembre(age=20, weight=70, height=1.78, gender=Gender.female, activity_level=1)
    vo2_max_2 = Calculators.vo2max_schembre(age=20, weight=70, height=1.78, gender=Gender.female)
    vo2_max_3 = Calculators.vo2max_schembre(age=20, weight=70, height=1.78)
    assert vo2_max_1 is not None and vo2_max_1 > 0
    assert vo2_max_2 is not None and vo2_max_2 > 0
    assert vo2_max_3 is not None and vo2_max_3 > 0


def test_vo2max_schembre_activity_level():
    vo2_max_1 = Calculators.vo2max_schembre(age=20, weight=70, height=1.78, gender=Gender.female, activity_level=1)
    vo2_max_2 = Calculators.vo2max_schembre(age=20, weight=70, height=1.78, gender=Gender.female, activity_level=2)
    assert vo2_max_1 < vo2_max_2


def test_vo2max_schembre_gender():
    vo2_max_female = Calculators.vo2max_schembre(age=20, weight=70, height=1.78, gender=Gender.female, activity_level=1)
    vo2_max_male = Calculators.vo2max_schembre(age=20, weight=70, height=1.78, gender=Gender.male, activity_level=1)
    assert vo2_max_female < vo2_max_male


def test_vo2max_matthews():
    age = 35
    weight = 70
    height = 1.75
    vo2_max_1 = Calculators.vo2max_matthews(age, weight, height, gender=Gender.female, activity_level=5.0)
    vo2_max_2 = Calculators.vo2max_matthews(age, weight, height, gender=Gender.female)
    vo2_max_3 = Calculators.vo2max_matthews(age, weight, height)
    assert vo2_max_1 is not None and vo2_max_1 > 0
    assert vo2_max_2 is not None and vo2_max_2 > 0
    assert vo2_max_3 is not None and vo2_max_3 > 0


def test_vo2max_matthews_gender():
    age = 35
    weight = 70
    height = 1.75
    vo2_max_female = Calculators.vo2max_matthews(age, weight, height, gender=Gender.female, activity_level=5.0)
    vo2_max_male = Calculators.vo2max_matthews(age, weight, height, gender=Gender.male, activity_level=5.0)
    assert vo2_max_female < vo2_max_male


def test_vo2max_matthews_activity_level():
    age = 35
    weight = 70
    height = 1.75
    vo2_max_1 = Calculators.vo2max_matthews(age, weight, height, gender=Gender.female, activity_level=5.0)
    vo2_max_2 = Calculators.vo2max_matthews(age, weight, height, gender=Gender.female, activity_level=4.0)
    assert vo2_max_1 > vo2_max_2


def test_vo2max_matthews_weight():
    """everything else remaining same decreases with weight"""
    age = 35
    height = 1.75
    vo2_max_1 = Calculators.vo2max_matthews(age, 70, height, gender=Gender.female, activity_level=5.0)
    vo2_max_2 = Calculators.vo2max_matthews(age, 71, height, gender=Gender.female, activity_level=5.0)
    assert vo2_max_1 > vo2_max_2


def test_vo2max_matthews_age():
    """everything else remaining the same, decreases with age"""
    weight = 35
    height = 1.75
    vo2_max_1 = Calculators.vo2max_matthews(20, weight, height, gender=Gender.female, activity_level=5.0)
    vo2_max_2 = Calculators.vo2max_matthews(21, weight, height, gender=Gender.female, activity_level=5.0)
    assert vo2_max_1 > vo2_max_2


def test_vo2max_nhanes():
    age = 25
    vo2_max_1 = Calculators.vo2max_nhanes(age, bmi=22.0, gender=Gender.female, activity_level=5.0)
    vo2_max_2 = Calculators.vo2max_nhanes(age, bmi=22.0, gender=Gender.female)
    vo2_max_3 = Calculators.vo2max_nhanes(age, bmi=22.0)
    vo2_max_4 = Calculators.vo2max_nhanes(age)
    assert vo2_max_1 is not None and vo2_max_1 > 0
    assert vo2_max_2 is not None and vo2_max_2 > 0
    assert vo2_max_3 is not None and vo2_max_3 > 0
    assert vo2_max_4 is not None and vo2_max_4 > 0


def test_vo2max_population():
    age = 25
    vo2_max_1 = Calculators.vo2max_population(age, female=True, activity_level=5.0)
    vo2_max_2 = Calculators.vo2max_population(age, female=True)
    vo2_max_3 = Calculators.vo2max_population(age, female=False)
    vo2_max_4 = Calculators.vo2max_population(age, female=True, activity_level=6.0)
    assert vo2_max_1 is not None and vo2_max_1 > 0
    assert vo2_max_2 is not None and vo2_max_2 > 0
    assert vo2_max_3 is not None and vo2_max_3 > 0
    assert vo2_max_4 is not None and vo2_max_4 > 0
    assert vo2_max_3 > vo2_max_2
    assert vo2_max_4 > vo2_max_1


def test_get_mets_from_rpe_acsm():
    last = 0
    for rpe in range(1, 11):
        mets = Calculators.get_mets_from_rpe_acsm(rpe, age=20)
        assert mets > last
        last = mets


def test_get_power_from_rpe():
    last = StandardErrorRange(observed_value=0)
    for rpe in range(1, 11):
        rpe_range = StandardErrorRange(observed_value=rpe)
        power = Calculators.get_power_from_rpe(rpe_range, weight=70, vo2_max=StandardErrorRange(lower_bound=45, upper_bound=55))
        assert power.lowest_value() >= last.lowest_value() and power.highest_value() > last.highest_value()
        last = power


def test_get_power_from_rpe_diff_weight():
    for rpe in range(1, 11):
        rpe_range = StandardErrorRange(observed_value=rpe)
        power1 = Calculators.get_power_from_rpe(rpe_range, weight=50, vo2_max=StandardErrorRange(lower_bound=45, upper_bound=55))
        power2 = Calculators.get_power_from_rpe(rpe_range, weight=60, vo2_max=StandardErrorRange(lower_bound=45, upper_bound=55))
        power3 = Calculators.get_power_from_rpe(rpe_range, weight=70, vo2_max=StandardErrorRange(lower_bound=45, upper_bound=55))
        power4 = Calculators.get_power_from_rpe(rpe_range, weight=80, vo2_max=StandardErrorRange(lower_bound=45, upper_bound=55))
        assert power1.highest_value() < power2.highest_value() < power3.highest_value() < power4.highest_value()


# def test_get_power_from_rpe_diff_weight2():
#     for rpe in range(1, 11):
#         power1 = Calculators.get_power_from_rpe(rpe, age=20, weight=50)
#         power2 = Calculators.get_power_from_rpe(rpe, age=20, weight=60)
#         power3 = Calculators.get_power_from_rpe(rpe, age=20, weight=70)
#         power4 = Calculators.get_power_from_rpe(rpe, age=20, weight=80)
#         assert power1 < power2 < power3 < power4


def test_power_resistance_exercise():
    for weight in range(10, 100):
        print(weight, Calculators.power_resistance_exercise(weight, .05 * 70).observed_value)
    speed = 6 * 1610 / 3600
    print(Calculators.power_running(speed, user_weight=70))
    # power = Calculators.power_resistance_exercise(100, 70).observed_value
    # print(power, Calculators.watts_to_mets(power, weight=70, efficiency=1))


def test_power_cycling_100():
    speed = 25 * 1610 / 3600
    print(Calculators.power_cycling(speed, user_weight=70))
    print(Calculators.power_cardio(CardioAction.cycle, user_weight=70))
    # power = Calculators.power_resistance_exercise(100, 70).observed_value
    # print(power, Calculators.watts_to_mets(power, weight=70, efficiency=1))


def test_vo2_max_from_rpe_5():
    rpe = StandardErrorRange(observed_value=5)
    vo2_max = Calculators.percent_vo2_max_from_rpe_range(rpe)
    assert 65 == vo2_max.lower_bound
    assert 72.5 == vo2_max.upper_bound


def test_vo2_max_from_rpe_10():
    rpe = StandardErrorRange(observed_value=10)
    vo2_max = Calculators.percent_vo2_max_from_rpe_range(rpe)
    assert 100 == vo2_max.lower_bound
    assert 100 == vo2_max.upper_bound


def test_vo2_max_from_rpe_0():
    rpe = StandardErrorRange(observed_value=0)
    vo2_max = Calculators.percent_vo2_max_from_rpe_range(rpe)
    assert None is vo2_max.lower_bound
    assert None is vo2_max.upper_bound

