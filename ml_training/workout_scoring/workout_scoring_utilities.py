from models.periodization_goal import PeriodizationGoalType
from models.training_volume import StandardErrorRange
from models.soreness_base import BodyPartLocation
from models.ranked_types import RankedAdaptationType
from models.movement_tags import AdaptationTypeMeasure
from models.periodization import TemplateWorkout
import numpy as np

from models.periodization import RequiredExerciseFactory

muscle_groups = list(BodyPartLocation.muscle_groups().keys())


def get_required_exercises(goal):
    required_exercises = RequiredExerciseFactory().get_required_exercises(goal)
    one_required_exercises = RequiredExerciseFactory().get_one_required_exercises(goal)
    return required_exercises, one_required_exercises


def get_muscle_needs():
    muscle_load_needs = {}

    no_load_needed_muscles = np.random.choice(muscle_groups, np.random.randint(0, 5))  # TODO need a better way to randomize which muscles have been fully loaded alredy
    for muscle in no_load_needed_muscles:
        muscle_load_needs[muscle] = 0
    muscles_to_be_loaded = set(muscle_groups) - set(no_load_needed_muscles)

    # get some muscles that have not been loaded at all
    missing_muscle_groups = np.random.choice(list(muscles_to_be_loaded), np.random.randint(1, 5))  # TODO need a better way to randomize which muscles haven't been loaded
    for muscle in missing_muscle_groups:
        muscle_load_needs[muscle] = 100
    remaining_muscles = muscles_to_be_loaded - set(missing_muscle_groups)

    for muscle in remaining_muscles:
        muscle_load_needs[muscle] = np.random.random() * 100  # TODO need a better way to randomize how much a muscle has been loaded so far
    return muscle_load_needs


def randomize_template_workout(template_workout):
    rpe_lower = np.random.uniform(1, 8)
    rpe_upper = np.random.uniform(rpe_lower, max([rpe_lower + 3, 9]))
    template_workout.acceptable_session_rpe = StandardErrorRange(lower_bound=rpe_lower, upper_bound=rpe_upper)
    duration_lower = np.random.uniform(20 * 60, 90 * 60)  # lower is in range 20 min to 90 min
    duration_upper = np.random.uniform(duration_lower, max([duration_lower + 20 * 60, 90 * 60]))  # upper limit is max of lower + 20 mins or 100 mins
    template_workout.acceptable_session_duration = StandardErrorRange(lower_bound=duration_lower, upper_bound=duration_upper)
    rpe_load = template_workout.acceptable_session_rpe.plagiarize()
    rpe_load.multiply_range(template_workout.acceptable_session_duration)
    template_workout.acceptable_session_rpe_load = rpe_load
    template_workout.muscle_load_ranking = get_muscle_needs()
    template_workout.acceptable_session_power_load = StandardErrorRange()
    template_workout.adaptation_type_ranking = adjust_adaptation_type_ranking(template_workout.adaptation_type_ranking)


def adjust_adaptation_type_ranking(adaptation_type_ranking):
    if len(adaptation_type_ranking) <= 2:
        selected_adaptation_type_ranking = adaptation_type_ranking
    else:
        min_ranked_types = 2
        max_ranked_types = len(adaptation_type_ranking) + 1
        selected_adaptation_type_ranking = list(np.random.choice(adaptation_type_ranking, size=np.random.randint(min_ranked_types, max_ranked_types), replace=False))
    if len(adaptation_type_ranking) != len(selected_adaptation_type_ranking):
        last_used_ranking = 0
        last_found_ranking = 0
        for rat in selected_adaptation_type_ranking:
            if rat.ranking == last_used_ranking:
                pass
            elif rat.ranking == last_found_ranking:
                rat.ranking = last_used_ranking
            else:
                last_found_ranking = rat.ranking
                rat.ranking = last_used_ranking + 1
            last_used_ranking = rat.ranking
    all_rankings = list(set(rat.ranking for rat in selected_adaptation_type_ranking))
    shuffled_rankings = list(set(rat.ranking for rat in selected_adaptation_type_ranking))
    np.random.shuffle(shuffled_rankings)
    ranking_shuffle_dict = {old: new for old, new in zip(all_rankings, shuffled_rankings)}
    for rat in selected_adaptation_type_ranking:
        rat.ranking = ranking_shuffle_dict.get(rat.ranking)
    return selected_adaptation_type_ranking


def get_template_workouts():
    goals = [
        PeriodizationGoalType.increase_cardiovascular_health,
        PeriodizationGoalType.increase_cardio_endurance,
        PeriodizationGoalType.increase_cardio_endurance_with_speed,
        PeriodizationGoalType.increase_strength_max_strength
    ]
    all_template_workouts = []
    for goal in goals:
        template_workout = TemplateWorkout()
        required_exercises, one_required_exercises = get_required_exercises(goal)
        all_required_exercises = []
        all_required_exercises.extend(required_exercises)
        all_required_exercises.extend(one_required_exercises)
        all_required_exercises.sort(key=lambda x: (1-x.priority, x.times_per_week.lowest_value()), reverse=True)
        template_workout.adaptation_type_ranking = rank_adaptation_types(all_required_exercises)
        all_template_workouts.append(template_workout)

    return all_template_workouts


def rank_adaptation_types(sorted_required_exercises):
    required_exercise_dict = {}

    ranking = 1
    last_times_per_week = None
    last_priority = None
    last_ranking_used = 0

    for periodized_exercise in sorted_required_exercises:
        adjusted_ranking = False
        if periodized_exercise.times_per_week.lowest_value() > 0:
            if last_times_per_week is None:
                last_times_per_week = periodized_exercise.times_per_week.lowest_value()
            elif last_times_per_week > periodized_exercise.times_per_week.lowest_value():
                if ranking == last_ranking_used:
                    ranking += 1
                    adjusted_ranking = True

            if last_priority is None:
                last_priority = periodized_exercise.priority
            elif last_priority < periodized_exercise.priority:
                last_priority = periodized_exercise.priority
                if not adjusted_ranking:
                    if ranking == last_ranking_used:
                        ranking += 1

            if periodized_exercise.detailed_adaptation_type is not None:
                detailed_ranked_type = RankedAdaptationType(AdaptationTypeMeasure.detailed_adaptation_type,
                                                            periodized_exercise.detailed_adaptation_type,
                                                            ranking,
                                                            periodized_exercise.duration.highest_value() if periodized_exercise.duration is not None else None)

                if periodized_exercise.detailed_adaptation_type not in required_exercise_dict:
                    required_exercise_dict[periodized_exercise.detailed_adaptation_type] = detailed_ranked_type
                    last_ranking_used = ranking
                else:
                    # if same ranking, go with the larger duration, otherwise ignore the duration of the lower ranking
                    if required_exercise_dict[periodized_exercise.detailed_adaptation_type].ranking == ranking:
                        if required_exercise_dict[periodized_exercise.detailed_adaptation_type].duration is None:
                            required_exercise_dict[periodized_exercise.detailed_adaptation_type].duration = periodized_exercise.duration.highest_value()
                        else:
                            if periodized_exercise.duration is not None:
                                required_exercise_dict[periodized_exercise.detailed_adaptation_type].duration = max(required_exercise_dict[periodized_exercise.detailed_adaptation_type].duration,
                                                                                                                    periodized_exercise.duration.highest_value())

            if periodized_exercise.sub_adaptation_type is not None:
                sub_adaptation_type = RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type,
                                                           periodized_exercise.sub_adaptation_type,
                                                           ranking,
                                                           periodized_exercise.duration.highest_value() if periodized_exercise.duration is not None else None)

                if periodized_exercise.sub_adaptation_type not in required_exercise_dict:
                    required_exercise_dict[periodized_exercise.sub_adaptation_type] = sub_adaptation_type
                    last_ranking_used = ranking
                else:
                    # if same ranking, go with the larger duration, otherwise ignore the duration of the lower ranking
                    if required_exercise_dict[periodized_exercise.sub_adaptation_type].ranking == ranking:
                        if required_exercise_dict[periodized_exercise.sub_adaptation_type].duration is None:
                            required_exercise_dict[
                                periodized_exercise.sub_adaptation_type].duration = periodized_exercise.duration.highest_value()
                        else:
                            if periodized_exercise.duration is not None:
                                required_exercise_dict[periodized_exercise.sub_adaptation_type].duration = max(
                                        required_exercise_dict[periodized_exercise.sub_adaptation_type].duration,
                                        periodized_exercise.duration.highest_value())

    ranked_adaptation_type_list = list(required_exercise_dict.values())
    return ranked_adaptation_type_list
