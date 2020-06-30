from models.training_load import DetailedTrainingLoad, MuscleDetailedLoad, MuscleDetailedLoadSummary
from models.soreness import BodyPartSide, BodyPartLocation
from models.training_volume import StandardErrorRange
from models.movement_tags import DetailedAdaptationType
from logic.periodization_processor import PeriodizationPlanProcessor
from scipy.optimize import optimize

def get_load_dictionary(load_type_list, load_list):

    load = {}
    for t in range(0, len(load_type_list)):
        load[load_type_list[t]] = StandardErrorRange(None, None, load_list[t])

    return load


def get_program_a():

    muscle_load = MuscleDetailedLoad("test_provider", "test_program_a")

    load_type_list = [DetailedAdaptationType.mobility, DetailedAdaptationType.speed,
                      DetailedAdaptationType.muscular_endurance, DetailedAdaptationType.anaerobic_interval_training]

    quad_loads = [50, 40, 30, 20]
    bicep_loads = [45, 35, 25, 15]

    r_quad_load = get_load_dictionary(load_type_list, quad_loads)

    l_quad_load = get_load_dictionary(load_type_list, quad_loads)

    r_bicep_load = get_load_dictionary(load_type_list, bicep_loads)

    l_bicep_load = get_load_dictionary(load_type_list, bicep_loads)

    muscle_load.items[BodyPartSide(BodyPartLocation.quads, 1)] = l_quad_load
    muscle_load.items[BodyPartSide(BodyPartLocation.quads, 2)] = r_quad_load
    muscle_load.items[BodyPartSide(BodyPartLocation.biceps, 1)] = l_bicep_load
    muscle_load.items[BodyPartSide(BodyPartLocation.biceps, 2)] = r_bicep_load

    return muscle_load


def get_program_b():

    muscle_load = MuscleDetailedLoad("test_provider", "test_program_b")

    load_type_list = [DetailedAdaptationType.stabilization_endurance, DetailedAdaptationType.base_aerobic_training,
                      DetailedAdaptationType.muscular_endurance, DetailedAdaptationType.anaerobic_interval_training]

    quad_loads = [50, 40, 30, 20]
    bicep_loads = [45, 35, 25, 15]

    r_quad_load = get_load_dictionary(load_type_list, quad_loads)

    l_quad_load = get_load_dictionary(load_type_list, quad_loads)

    r_bicep_load = get_load_dictionary(load_type_list, bicep_loads)

    l_bicep_load = get_load_dictionary(load_type_list, bicep_loads)

    muscle_load.items[BodyPartSide(BodyPartLocation.quads, 1)] = l_quad_load
    muscle_load.items[BodyPartSide(BodyPartLocation.quads, 2)] = r_quad_load
    muscle_load.items[BodyPartSide(BodyPartLocation.biceps, 1)] = l_bicep_load
    muscle_load.items[BodyPartSide(BodyPartLocation.biceps, 2)] = r_bicep_load

    return muscle_load

def get_program_c():

    muscle_load = MuscleDetailedLoad("test_provider", "test_program_c")

    load_type_list = [DetailedAdaptationType.stabilization_endurance, DetailedAdaptationType.base_aerobic_training,
                      DetailedAdaptationType.sustained_power, DetailedAdaptationType.stabilization_power]

    quad_loads = [50, 40, 30, 20]
    bicep_loads = [45, 35, 25, 15]

    r_quad_load = get_load_dictionary(load_type_list, quad_loads)

    l_quad_load = get_load_dictionary(load_type_list, quad_loads)

    r_bicep_load = get_load_dictionary(load_type_list, bicep_loads)

    l_bicep_load = get_load_dictionary(load_type_list, bicep_loads)

    muscle_load.items[BodyPartSide(BodyPartLocation.quads, 1)] = l_quad_load
    muscle_load.items[BodyPartSide(BodyPartLocation.quads, 2)] = r_quad_load
    muscle_load.items[BodyPartSide(BodyPartLocation.biceps, 1)] = l_bicep_load
    muscle_load.items[BodyPartSide(BodyPartLocation.biceps, 2)] = r_bicep_load

    return muscle_load


def sum_load(program_load_dict):

    summed_load = {}

    for body_part_side, load_dict in program_load_dict.items.items():
        for load_type, load in load_dict.items():
            if load_type not in summed_load.keys():
                summed_load[load_type] = StandardErrorRange()
                summed_load[load_type].add(load)

    return summed_load


class SimpleWorkout(object):
    def __init__(self, session_load):
        self.session_load = session_load


def get_list_of_load_workouts(number_workouts):

    load = 10
    workouts = []

    for n in range(0, number_workouts):
        workout = SimpleWorkout(load)
        workouts.append(workout)
        load += 10

    return workouts


def test_sum_parts():

    program_a = get_program_a()
    summed_load_a = sum_load(program_a)

    program_b = get_program_b()
    summed_load_b = sum_load(program_b)

    program_c = get_program_c()
    summed_load_c = sum_load(program_c)

    assert 4 == len(summed_load_a)
    assert 4 == len(summed_load_b)
    assert 4 == len(summed_load_c)

    # get the load by muscle
    # aggregate to the session by type of load
    # should also look at the session load (non aggregated from muscle)

    # create three sessions that should be reasonably different (or perhaps somewhat similar?) and given a client's background, we should get a different ranking.
    # 3 diff clients should yield different rankings

def test_find_workout_combinations():

    twenty_workouts = get_list_of_load_workouts(20)

    min_workouts_week = 3
    max_workouts_week = 5

    proc = PeriodizationPlanProcessor(None)

    combinations = proc.get_acceptable_combinations(twenty_workouts, 250, 350, min_workouts_week, max_workouts_week)
    total_combinations = 0
    for workout_count, load_list in combinations.items():
        for loads in load_list:
            load_vals = [l.session_load for l in loads]
            print(load_vals)
            total_combinations += 1

    print("total=" + str(total_combinations))

    assert len(combinations) > 0








