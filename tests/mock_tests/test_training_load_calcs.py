from models.training_volume import StandardErrorRange
from logic.training_load_calcs import TrainingLoadCalculator
from models.training_load import CompletedSessionDetails, LoadType
from datetime import datetime

def create_week_workouts(load_values):

    week = []

    for load in load_values:
        completed_session_details = CompletedSessionDetails(datetime.now(),1,1)
        completed_session_details.rpe_load = StandardErrorRange(lower_bound=load*.87, observed_value=load, upper_bound=load*1.14)
        completed_session_details.power_load = StandardErrorRange(lower_bound=load * .87, observed_value=load,
                                                                upper_bound=load * 1.14)
        completed_session_details.session_rpe = 5
        week.append(completed_session_details)

    return week


def test_ramp():

    week_1 = create_week_workouts([50, 80, 60, 50])
    week_2 = create_week_workouts([60, 80, 65, 60])

    ramp = TrainingLoadCalculator().get_ramp(LoadType.rpe, week_1, week_2)

    assert 0 < ramp.lower_bound
    assert 0 < ramp.observed_value
    assert 0 < ramp.upper_bound


def test_acwr():

    week_1 = create_week_workouts([50, 80, 60, 50])
    week_2_list = [create_week_workouts([60, 80, 65, 60]),
            create_week_workouts([40, 70, 55, 30]),
            create_week_workouts([50, 60, 55, 50]),
            create_week_workouts([50, 50, 55, 60])]

    acwr = TrainingLoadCalculator().get_acwr(LoadType.rpe, week_1, week_2_list)

    assert 0 < acwr.lower_bound
    assert 0 < acwr.observed_value
    assert 0 < acwr.upper_bound


def test_freshness():

    week_1 = create_week_workouts([50, 80, 60, 50])
    week_2_list = [create_week_workouts([60, 80, 65, 60]),
                   create_week_workouts([40, 70, 55, 30]),
                   create_week_workouts([50, 60, 55, 50]),
                   create_week_workouts([50, 50, 55, 60])]

    freshness = TrainingLoadCalculator().get_freshness(LoadType.rpe, week_1, week_2_list)

    assert 0 > freshness.lower_bound
    assert 0 > freshness.observed_value
    assert 0 > freshness.upper_bound


def test_monotony():

    week_1 = create_week_workouts([50, 80, 60, 50])
    # week_2 = create_week_workouts([60, 80, 65, 60])
    # week_3 = create_week_workouts([40, 70, 55, 30])
    # week_4 = create_week_workouts([50, 60, 55, 50])
    # week_5 = create_week_workouts([50, 50, 55, 60])

    #calc = TrainingLoadCalculator(week_1, week_2, week_3, week_4, week_5,calculate_averages=False)

    #values_list = [w.rpe_load for w in week_1]

    monotony = TrainingLoadCalculator().get_monotony(LoadType.rpe, week_1)

    assert 0 < monotony.lower_bound
    assert 0 < monotony.observed_value
    assert 0 < monotony.upper_bound


def test_strain():

    week_1 = create_week_workouts([50, 80, 60, 50])
    # week_2 = create_week_workouts([60, 80, 65, 60])
    # week_3 = create_week_workouts([40, 70, 55, 30])
    # week_4 = create_week_workouts([50, 60, 55, 50])
    # week_5 = create_week_workouts([50, 50, 55, 60])
    #
    # calc = TrainingLoadCalculator(week_1, week_2, week_3, week_4, week_5,calculate_averages=False)

    #values_list = [w.rpe_load for w in week_1]
    strain = TrainingLoadCalculator().get_strain(LoadType.rpe, week_1)

    assert 0 < strain.lower_bound
    assert 0 < strain.observed_value
    assert 0 < strain.upper_bound

def test_strain_spike():

    week_1 = create_week_workouts([90, 80, 100, 90])
    week_2 = create_week_workouts([60, 80, 65, 60])
    week_3 = create_week_workouts([40, 70, 55, 30])
    week_4 = create_week_workouts([50, 60, 55, 50])
    week_5 = create_week_workouts([50, 50, 55, 60])

    weeks = [week_1, week_2, week_3, week_4, week_5]

    #calc = TrainingLoadCalculator(week_1, week_2, week_3, week_4, week_5,calculate_averages=False)

    spike = TrainingLoadCalculator().get_strain_spike(LoadType.rpe, weeks)

    assert 0 < spike.lower_bound
    assert 0 < spike.observed_value
    assert 0 < spike.upper_bound
