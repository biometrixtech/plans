from models.training_load import DetailedTrainingLoad, MuscleDetailedLoad, MuscleDetailedLoadSummary
from models.soreness import BodyPartSide, BodyPartLocation
from models.training_volume import StandardErrorRange
from models.movement_tags import DetailedAdaptationType
from logic.periodization_processor import PeriodizationPlanProcessor
from models.periodization import AthleteTrainingHistory, PeriodizationModel, PeriodizationProgression, PeriodizationModelFactory, PeriodizationPersona, PeriodizationGoal, TrainingPhaseType

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
    def __init__(self, id, rpe, duration):
        self.id = id
        self.session_rpe = rpe
        self.duration = duration
        self.session_load = rpe * duration


def get_list_of_load_workouts(rpe_list, duration_list):

    workouts = []
    id = 1

    for r in rpe_list:
        for d in duration_list:
            workout = SimpleWorkout(id, r, d)
            workouts.append(workout)
            id += 1

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

# def test_find_workout_combinations():
#
#     rpe_list = list(range(1,11,1))
#     duration_list = list(range(30, 95, 5))
#     workouts = get_list_of_load_workouts(rpe_list, duration_list)
#
#     athlete_training_history = AthleteTrainingHistory()
#     athlete_training_history.session_load = StandardErrorRange(lower_bound=120, upper_bound=225)
#     athlete_training_history.session_rpe = StandardErrorRange(lower_bound=4, upper_bound=7)
#     athlete_training_history.session_duration = StandardErrorRange(lower_bound=30, upper_bound=75)
#     athlete_training_history.sessions_per_week = StandardErrorRange(lower_bound=3, upper_bound=5)
#
#     # TODO - add training load for last 4-5 weeks
#
#     athlete_training_goal = PeriodizationGoal.improve_cardiovascular_health
#
#     proc = PeriodizationPlanProcessor(athlete_training_goal, athlete_training_history, PeriodizationPersona.well_trained,TrainingPhaseType.increase)
#     proc.set_weekly_targets()
#
#     completed_workouts = []
#
#     acceptable_workouts_1 = proc.get_acceptable_workouts(0, workouts, 350, 500, completed_workouts)
#
#     acceptable_workouts_1_copy = [a for a in acceptable_workouts_1]
#
#     completed_workout_1 = acceptable_workouts_1_copy.pop(0)
#     completed_workouts.append(completed_workout_1)
#
#     acceptable_workouts_2 = proc.get_acceptable_workouts(0, workouts, 350, 500, completed_workouts)
#
#     acceptable_workouts_2_copy = [a for a in acceptable_workouts_2]
#
#     completed_workout_2 = acceptable_workouts_2_copy.pop(0)
#     completed_workouts.append(completed_workout_2)
#
#     acceptable_workouts_3 = proc.get_acceptable_workouts(0, workouts, 350, 500, completed_workouts)
#
#     assert len(acceptable_workouts_3) > 0








