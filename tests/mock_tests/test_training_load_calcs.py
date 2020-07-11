from models.training_volume import StandardErrorRange
from logic.training_load_calcs import TrainingLoadCalculator


def create_week_workouts(load_values):

    week = []

    for load in load_values:
        week.append(StandardErrorRange(lower_bound=load*.87, observed_value=load, upper_bound=load*1.14))

    return week


def test_ramp():

    week_1 = create_week_workouts([50, 80, 60, 50])
    week_2 = create_week_workouts([60, 80, 65, 60])

    calc = TrainingLoadCalculator(week_1, week_2, [], [], [])

    ramp = calc.get_ramp()

    assert 0 < ramp.lower_bound
    assert 0 < ramp.observed_value
    assert 0 < ramp.upper_bound


def test_acwr():

    week_1 = create_week_workouts([50, 80, 60, 50])
    week_2 = create_week_workouts([60, 80, 65, 60])
    week_3 = create_week_workouts([40, 70, 55, 30])
    week_4 = create_week_workouts([50, 60, 55, 50])
    week_5 = create_week_workouts([50, 50, 55, 60])

    calc = TrainingLoadCalculator(week_1, week_2, week_3, week_4, week_5)

    acwr = calc.get_acwr()

    assert 0 < acwr.lower_bound
    assert 0 < acwr.observed_value
    assert 0 < acwr.upper_bound


def test_freshness():

    week_1 = create_week_workouts([50, 80, 60, 50])
    week_2 = create_week_workouts([60, 80, 65, 60])
    week_3 = create_week_workouts([40, 70, 55, 30])
    week_4 = create_week_workouts([50, 60, 55, 50])
    week_5 = create_week_workouts([50, 50, 55, 60])

    calc = TrainingLoadCalculator(week_1, week_2, week_3, week_4, week_5)

    freshness = calc.get_freshness()

    assert 0 > freshness.lower_bound
    assert 0 > freshness.observed_value
    assert 0 > freshness.upper_bound

def test_monotony():

    week_1 = create_week_workouts([50, 80, 60, 50])
    week_2 = create_week_workouts([60, 80, 65, 60])
    week_3 = create_week_workouts([40, 70, 55, 30])
    week_4 = create_week_workouts([50, 60, 55, 50])
    week_5 = create_week_workouts([50, 50, 55, 60])

    calc = TrainingLoadCalculator(week_1, week_2, week_3, week_4, week_5)

    monotony = calc.get_monotony(week_1)

    assert 0 < monotony.lower_bound
    assert 0 < monotony.observed_value
    assert 0 < monotony.upper_bound

def test_strain():

    week_1 = create_week_workouts([50, 80, 60, 50])
    week_2 = create_week_workouts([60, 80, 65, 60])
    week_3 = create_week_workouts([40, 70, 55, 30])
    week_4 = create_week_workouts([50, 60, 55, 50])
    week_5 = create_week_workouts([50, 50, 55, 60])

    calc = TrainingLoadCalculator(week_1, week_2, week_3, week_4, week_5)

    strain = calc.get_strain(week_1)

    assert 0 < strain.lower_bound
    assert 0 < strain.observed_value
    assert 0 < strain.upper_bound

def test_strain_spike():

    week_1 = create_week_workouts([90, 80, 100, 90])
    week_2 = create_week_workouts([60, 80, 65, 60])
    week_3 = create_week_workouts([40, 70, 55, 30])
    week_4 = create_week_workouts([50, 60, 55, 50])
    week_5 = create_week_workouts([50, 50, 55, 60])

    calc = TrainingLoadCalculator(week_1, week_2, week_3, week_4, week_5)

    spike = calc.get_strain_spike()

    assert 0 < spike.lower_bound
    assert 0 < spike.observed_value
    assert 0 < spike.upper_bound
