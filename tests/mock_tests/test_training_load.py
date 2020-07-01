from models.training_load import DetailedTrainingLoad, MuscleDetailedLoad, MuscleDetailedLoadSummary
from models.soreness import BodyPartSide, BodyPartLocation
from models.training_volume import StandardErrorRange
from models.movement_tags import DetailedAdaptationType
from logic.periodization_processor import PeriodizationPlanProcessor
from models.periodization import AthleteTrainingHistory, PeriodizationModel, PeriodizationProgression, PeriodizationModelFactory, PeriodizationPersona, PeriodizationGoal, TrainingPhaseType
from models.training_load import TrainingLoad
from statistics import mean


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

def get_fake_training_history():

    rpes = [3, 4, 5, 6, 7, 6, 5, 4, 3]
    durations = [90, 45, 60, 75, 30, 75, 60, 45, 90]

    load_list = []

    for r in range(len(rpes)):
        load_list.append(rpes[r] * durations[r])

    average_load = mean(load_list)
    weekly_load = sum(load_list) / float(2)
    average_rpes = mean(rpes)
    average_durations = mean(durations)

    average_training_load = TrainingLoad()
    average_training_load.rpe_load = StandardErrorRange(lower_bound=average_load-10, upper_bound=average_load+10)

    athlete_training_history = AthleteTrainingHistory()
    athlete_training_history.average_session_load = average_training_load

    athlete_training_history.average_session_rpe = StandardErrorRange(lower_bound=average_rpes-1, upper_bound=average_rpes+1)
    athlete_training_history.average_session_duration = StandardErrorRange(lower_bound=average_durations-10, upper_bound=average_durations+10)
    athlete_training_history.average_sessions_per_week = StandardErrorRange(lower_bound=3, upper_bound=5)

    weekly_training_load = TrainingLoad()
    weekly_training_load.rpe_load = StandardErrorRange(lower_bound=weekly_load-100, upper_bound=weekly_load+100)

    athlete_training_history.current_weeks_load = weekly_training_load
    athlete_training_history.previous_1_weeks_load = weekly_training_load
    athlete_training_history.previous_2_weeks_load = weekly_training_load
    athlete_training_history.previous_3_weeks_load = weekly_training_load
    athlete_training_history.previous_4_weeks_load = weekly_training_load

    athlete_training_history.current_weeks_average_session_rpe = StandardErrorRange(lower_bound=average_rpes-1, upper_bound=average_rpes+1)

    return athlete_training_history


def test_find_workout_combinations():

    rpe_list = list(range(1,11,1))
    duration_list = list(range(30, 150, 5))
    workouts = get_list_of_load_workouts(rpe_list, duration_list)

    athlete_training_history = get_fake_training_history()

    athlete_training_goal = PeriodizationGoal.improve_cardiovascular_health

    proc = PeriodizationPlanProcessor(athlete_training_goal, athlete_training_history, PeriodizationPersona.well_trained,TrainingPhaseType.slowly_increase)
    proc.set_weekly_targets()

    completed_workouts = []

    acceptable_workouts_1 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=False)

    acceptable_workouts_1_copy = [a for a in acceptable_workouts_1]

    completed_workout_1 = acceptable_workouts_1_copy.pop(0)
    completed_workouts.append(completed_workout_1)

    acceptable_workouts_2 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=False)

    acceptable_workouts_2_copy = [a for a in acceptable_workouts_2]

    completed_workout_2 = acceptable_workouts_2_copy.pop(0)
    completed_workouts.append(completed_workout_2)

    acceptable_workouts_3 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=False)

    acceptable_workouts_3_copy = [a for a in acceptable_workouts_3]

    completed_workout_3 = acceptable_workouts_3_copy.pop(0)
    completed_workouts.append(completed_workout_3)

    acceptable_workouts_4 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=False)

    acceptable_workouts_4_copy = [a for a in acceptable_workouts_4]

    completed_workout_4 = acceptable_workouts_4_copy.pop(0)
    completed_workouts.append(completed_workout_4)

    acceptable_workouts_5 = proc.get_acceptable_workouts(0, workouts, completed_workouts, exclude_completed=False)

    assert len(acceptable_workouts_5) > 0






