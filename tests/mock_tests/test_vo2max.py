from logic.calculators import Calculators
from models.movement_tags import CardioAction, Gender


def test_vo2max():
    age = 27
    user_weight = 60
    gender = Gender.female
    activity_level = 4
    user_height = 1.65
    vo2_max = Calculators.vo2_max_estimation_demographics(age, user_weight, user_height, gender, activity_level)
    assert vo2_max.lower_bound <= vo2_max.observed_value <= vo2_max.upper_bound

def test_work_vo2():
    power = 50
    weight = 70
    work_vo2_0 = Calculators.work_vo2_cycling(power, weight)
    work_vo2_1 = Calculators.work_vo2_cycling_alternate(power, weight)
    work_vo2_running_1 = Calculators.work_vo2_running_from_power(Calculators.power_running(3.12, user_weight=77), user_weight=77)
    work_vo2_rowing_1 = Calculators.work_vo2_rowing_from_power(Calculators.power_rowing(2.7), weight=70)
    work_vo2_swimming = Calculators.work_vo2_cardio(CardioAction.swim, Gender.female)
    print('here')
