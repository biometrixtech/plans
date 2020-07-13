from models.periodization import AthleteTrainingHistory, PeriodizationPlan, PeriodizationPlanWeek, PeriodizationModelFactory
from itertools import combinations, chain, repeat, islice, count
from collections import Counter
from models.training_volume import StandardErrorRange
from statistics import mean
from models.training_load import TrainingLoad, CompletedSessionDetails, LoadType
from models.movement_tags import AdaptationDictionary, RankedAdaptationType, AdaptationTypeMeasure
from logic.training_load_calcs import TrainingLoadCalculator
from math import sqrt
from datetime import timedelta


class WorkoutScoringManager(object):

    @staticmethod
    def cosine_similarity(candidate_exercise_priorities, recommended_exercise_priorities):

        # get the adaptation types separately so we can look for matches of type (but not necessarily ranking)
        candidate_adaptation_types = [c.adaptation_type for c in candidate_exercise_priorities]
        recommended_adaptation_types = [r.adaptation_type for r in recommended_exercise_priorities]
        all_adaptation_types = set(candidate_adaptation_types).union(recommended_adaptation_types)

        all_exercise_priorities = set(candidate_exercise_priorities).union(recommended_exercise_priorities)
        dotprod_1 = sum((1 if k in candidate_exercise_priorities else 0) * (1 if k in recommended_exercise_priorities else 0) for k in all_exercise_priorities)
        magA_1 = sqrt(sum((1 if k in candidate_exercise_priorities else 0) ** 2 for k in all_exercise_priorities))
        magB_1 = sqrt(sum((1 if k in recommended_exercise_priorities else 0) ** 2 for k in all_exercise_priorities))
        if (magA_1 * magB_1) == 0 :
            cosine_similarity_1 = 0
        else:
            cosine_similarity_1 = dotprod_1 / (magA_1 * magB_1)

        dotprod_2 = sum(
            (1 if k in candidate_adaptation_types else 0) * (1 if k in recommended_adaptation_types else 0) for k
            in all_adaptation_types)
        magA_2 = sqrt(sum((1 if k in candidate_adaptation_types else 0) ** 2 for k in all_adaptation_types))
        magB_2 = sqrt(sum((1 if k in recommended_adaptation_types else 0) ** 2 for k in all_adaptation_types))
        if (magA_2 * magB_2) == 0:
            cosine_similarity_2 = 0
        else:
            cosine_similarity_2 = dotprod_2 / (magA_2 * magB_2)

        average_cosine_similarity = (cosine_similarity_1 + cosine_similarity_2) / 2

        return average_cosine_similarity


class PeriodizationPlanProcessor(object):
    def __init__(self, event_date, completed_session_details_datastore, athlete_periodization_goal, athlete_persona, training_phase_type, athlete_training_history=None, training_calculator=None):
        self.event_date = event_date
        self.completed_session_details_datastore = completed_session_details_datastore
        self.persona = athlete_persona
        self.goal = athlete_periodization_goal
        self.athlete_training_history = athlete_training_history
        self.model = PeriodizationModelFactory().create(persona=athlete_persona, training_phase_type=training_phase_type, periodization_goal=athlete_periodization_goal)
        self.weekly_targets = []
        self.training_load_calculator = training_calculator
        self.set_training_load_calculator()
        self.set_athlete_training_history()

    def set_training_load_calculator(self):

        if self.training_load_calculator is None:

            current_week_load_list = self.completed_session_details_datastore.get(
                start_date_time=self.event_date - timedelta(days=6), end_date_time=self.event_date)
            previous_week_1_load_list = self.completed_session_details_datastore.get(
                start_date_time=self.event_date - timedelta(days=13), end_date_time=self.event_date - timedelta(days=7))
            previous_week_2_load_list = self.completed_session_details_datastore.get(
                start_date_time=self.event_date - timedelta(days=20), end_date_time=self.event_date - timedelta(days=14))
            previous_week_3_load_list = self.completed_session_details_datastore.get(
                start_date_time=self.event_date - timedelta(days=27), end_date_time=self.event_date - timedelta(days=21))
            previous_week_4_load_list = self.completed_session_details_datastore.get(
                start_date_time=self.event_date - timedelta(days=34), end_date_time=self.event_date - timedelta(days=28))

            self.training_load_calculator = TrainingLoadCalculator(current_week_load_list,
                                                                   previous_week_1_load_list,
                                                                   previous_week_2_load_list,
                                                                   previous_week_3_load_list,
                                                                   previous_week_4_load_list)

    def set_athlete_training_history(self):

        if self.athlete_training_history is None:

            self.athlete_training_history = AthleteTrainingHistory()

            self.athlete_training_history.current_weeks_load.rpe_load = self.training_load_calculator.current_week_rpe_load_sum
            self.athlete_training_history.current_weeks_load.power_load = self.training_load_calculator.current_week_power_load_sum

            self.athlete_training_history.previous_1_weeks_load.rpe_load = self.training_load_calculator.previous_week_1_rpe_load_sum
            self.athlete_training_history.previous_1_weeks_load.power_load = self.training_load_calculator.previous_week_1_power_load_sum

            self.athlete_training_history.previous_2_weeks_load.rpe_load = self.training_load_calculator.previous_week_2_rpe_load_sum
            self.athlete_training_history.previous_2_weeks_load.power_load = self.training_load_calculator.previous_week_2_power_load_sum

            self.athlete_training_history.previous_3_weeks_load.rpe_load = self.training_load_calculator.previous_week_3_rpe_load_sum
            self.athlete_training_history.previous_3_weeks_load.power_load = self.training_load_calculator.previous_week_3_power_load_sum

            self.athlete_training_history.previous_4_weeks_load.rpe_load = self.training_load_calculator.previous_week_4_rpe_load_sum
            self.athlete_training_history.previous_4_weeks_load.power_load = self.training_load_calculator.previous_week_4_power_load_sum

            self.athlete_training_history.average_session_load.rpe_load = self.training_load_calculator.average_session_load
            self.athlete_training_history.average_session_load.power_load = self.training_load_calculator.average_session_load

            self.athlete_training_history.average_session_rpe = self.training_load_calculator.average_session_rpe
            self.athlete_training_history.average_sessions_per_week = self.training_load_calculator.average_sessions_per_week

            self.athlete_training_history.current_weeks_detailed_load = self.training_load_calculator.current_weeks_detailed_load
            self.athlete_training_history.previous_1_weeks_detailed_load = self.training_load_calculator.previous_1_weeks_detailed_load
            self.athlete_training_history.previous_2_weeks_detailed_load = self.training_load_calculator.previous_2_weeks_detailed_load
            self.athlete_training_history.previous_3_weeks_detailed_load = self.training_load_calculator.previous_3_weeks_detailed_load
            self.athlete_training_history.previous_4_weeks_detailed_load = self.training_load_calculator.previous_4_weeks_detailed_load

    def set_weekly_targets(self):
        # sets procession from high volume-low intensity to low volume-high intensity over the course of the
        # mesocyle (length defined as number_of_weeks)

        for t in range(0, len(self.model.progressions)):
            weekly_targets = self.get_weekly_targets(self.model.progressions[t])
            self.weekly_targets.append(weekly_targets)

    def get_weekly_load_target(self, progression):

        # acwr
        last_four_weeks_rpe_load = self.athlete_training_history.get_last_four_weeks_rpe_load()
        lower_bounds = [w.lower_bound for w in last_four_weeks_rpe_load if w.lower_bound is not None]
        upper_bounds = [w.upper_bound for w in last_four_weeks_rpe_load if w.upper_bound is not None]

        lower_bound_average = mean(lower_bounds)
        upper_bound_average = mean(upper_bounds)

        lower_acwr = progression.training_phase.acwr.lower_bound
        upper_acwr = progression.training_phase.acwr.upper_bound

        load_calcs = [lower_bound_average * lower_acwr,
                      lower_bound_average * upper_acwr,
                      upper_bound_average * lower_acwr,
                      upper_bound_average * upper_acwr]

        load_target = TrainingLoad()
        load_target.rpe_load.lower_bound = min(load_calcs)
        load_target.rpe_load.upper_bound = max(load_calcs)
        load_target.rpe_load.observed_value = (load_target.rpe_load.upper_bound + load_target.rpe_load.lower_bound) / float(2)

        return load_target

    def get_weekly_targets(self, progression):

        current_weeks_rpe_load_lower = self.athlete_training_history.current_weeks_load.rpe_load.lower_bound
        current_weeks_rpe_load_upper = self.athlete_training_history.current_weeks_load.rpe_load.upper_bound

        current_average_session_rpe_load_lower = self.athlete_training_history.average_session_load.rpe_load.lower_bound
        current_average_session_rpe_load_upper = self.athlete_training_history.average_session_load.rpe_load.upper_bound

        current_average_session_rpe_lower = self.athlete_training_history.average_session_rpe.lower_bound
        current_average_session_rpe_upper = self.athlete_training_history.average_session_rpe.upper_bound

        min_workouts_week = self.athlete_training_history.average_sessions_per_week.lower_bound
        max_workouts_week = self.athlete_training_history.average_sessions_per_week.upper_bound

        # determine the weekly load increase and determine the RPE/volume contributions according the the progression

        weekly_rpe_load_target = self.get_weekly_load_target(progression)

        net_weeks_rpe_load_increase_lower = weekly_rpe_load_target.rpe_load.lower_bound - current_weeks_rpe_load_lower
        net_weeks_rpe_load_increase_upper = weekly_rpe_load_target.rpe_load.upper_bound - current_weeks_rpe_load_upper

        rpe_load_rate_increase_lower = (current_weeks_rpe_load_lower - net_weeks_rpe_load_increase_lower) / float(
            current_weeks_rpe_load_lower)
        rpe_load_rate_increase_upper = (current_weeks_rpe_load_upper - net_weeks_rpe_load_increase_upper) / float(
            current_weeks_rpe_load_upper)

        target_session_loads = [(1 + rpe_load_rate_increase_lower) * current_average_session_rpe_load_lower,
                                (1 + rpe_load_rate_increase_lower) * current_average_session_rpe_load_upper,
                                (1 + rpe_load_rate_increase_upper) * current_average_session_rpe_load_lower,
                                (1 + rpe_load_rate_increase_upper) * current_average_session_rpe_load_upper]

        target_session_load_lower = min(target_session_loads)
        target_session_load_upper = max(target_session_loads)

        # given load rate of increase, determine the RPE's share of that increase

        target_rpe_rates = [1 + (rpe_load_rate_increase_lower * progression.rpe_load_contribution),
                       1 + (rpe_load_rate_increase_upper * progression.rpe_load_contribution)]

        target_rpe_increase_lower = min(target_rpe_rates)
        target_rpe_increase_upper = max(target_rpe_rates)

        # apply adjusted RPE rate of increase

        target_rpes = [target_rpe_increase_lower * current_average_session_rpe_lower,
                       target_rpe_increase_lower * current_average_session_rpe_upper,
                       target_rpe_increase_upper * current_average_session_rpe_lower,
                       target_rpe_increase_upper * current_average_session_rpe_upper,

        ]

        target_rpe_lower = min(target_rpes)
        target_rpe_upper = max(target_rpes)

        # now reverse engineer the volume's contribution of increase given load and RPE

        target_weekly_volumes = [weekly_rpe_load_target.rpe_load.lower_bound / float(target_rpe_lower),
                          weekly_rpe_load_target.rpe_load.lower_bound / float(target_rpe_upper),
                          weekly_rpe_load_target.rpe_load.upper_bound / float(target_rpe_lower),
                          weekly_rpe_load_target.rpe_load.upper_bound / float(target_rpe_upper),

        ]

        target_weekly_volume_lower = min(target_weekly_volumes)
        target_weekly_volume_upper = max(target_weekly_volumes)

        target_session_volumes = [target_weekly_volume_lower / float(min_workouts_week),
                          target_weekly_volume_lower / float(max_workouts_week),
                          target_weekly_volume_upper / float(min_workouts_week),
                          target_weekly_volume_upper / float(max_workouts_week),

        ]

        target_session_volume_lower = min(target_session_volumes)
        target_session_volume_upper = max(target_session_volumes)

        periodization_plan_week = PeriodizationPlanWeek()
        periodization_plan_week.target_weekly_load = weekly_rpe_load_target

        target_session_load = TrainingLoad()
        target_session_load.rpe_load.lower_bound = target_session_load_lower
        target_session_load.rpe_load.upper_bound = target_session_load_upper

        periodization_plan_week.target_session_load = target_session_load

        periodization_plan_week.target_session_duration = StandardErrorRange(lower_bound=target_session_volume_lower,
                                                                             upper_bound=target_session_volume_upper)
        periodization_plan_week.target_session_rpe = StandardErrorRange(lower_bound=target_rpe_lower,
                                                                        upper_bound=target_rpe_upper)

        return periodization_plan_week

    def get_acceptable_workouts(self, week_number, workouts, completed_session_details_list: [CompletedSessionDetails], exclude_completed=True):

        current_week_target = self.weekly_targets[week_number]

        lowest_acceptable_load = current_week_target.target_session_load.rpe_load.lower_bound
        highest_acceptable_load = current_week_target.target_session_load.rpe_load.upper_bound

        lowest_acceptable_rpe = current_week_target.target_session_rpe.lower_bound
        highest_acceptable_rpe = current_week_target.target_session_rpe.upper_bound
        shortest_acceptable_duration = current_week_target.target_session_duration.lower_bound
        longest_acceptable_duration = current_week_target.target_session_duration.upper_bound

        # TODO - how do we adjust weekly workouts (based on goals) when they appear to exceed athlete's number of expected workouts?
        min_workouts_week = max(self.athlete_training_history.average_sessions_per_week.lower_bound - len(completed_session_details_list), 0)
        max_workouts_week = self.athlete_training_history.average_sessions_per_week.upper_bound - len(completed_session_details_list)

        if exclude_completed:
            workouts = [w for w in workouts if w.workout_id not in [c.workout_id for c in completed_session_details_list]]

        # first how many of the plan's recommended workouts have not been completed?
        required_exercises, required_found_times = self.get_non_completed_required_exercises(self.model.required_exercises,
                                                                                             completed_session_details_list)

        one_required_exercises, one_required_found_times = self.get_non_completed_required_exercises(self.model.one_required_exercises,
                                                                                                     completed_session_details_list)
        if self.model.one_required_combination is not None:
            if self.model.one_required_combination.lower_bound is not None:
                self.model.one_required_combination.lower_bound = self.model.one_required_combination.lower_bound - one_required_found_times
            if self.model.one_required_combination.upper_bound is not None:
                self.model.one_required_combination.upper_bound = self.model.one_required_combination.upper_bound - one_required_found_times

        # adjust required workout ranges to athlete's rpe and duration capacities:
        for r in required_exercises:
            if r.rpe is not None:
                r.rpe.upper_bound = min(r.rpe.upper_bound, highest_acceptable_rpe)
            if r.duration is not None:
                r.duration.upper_bound = min(r.duration.upper_bound, longest_acceptable_duration)
                if r.duration.upper_bound < r.duration.lower_bound:
                    r.duration.lower_bound = shortest_acceptable_duration

        for r in one_required_exercises:
            if r.rpe is not None:
                r.rpe.upper_bound = min(r.rpe.upper_bound, highest_acceptable_rpe)
            if r.duration is not None:
                r.duration.upper_bound = min(r.duration.upper_bound, longest_acceptable_duration)
                if r.duration.upper_bound < r.duration.lower_bound:
                    r.duration.lower_bound = shortest_acceptable_duration

        load_this_week = StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)

        for c in completed_session_details_list:
            load_this_week.add(c.power_load)

        min_week_load = max(current_week_target.target_weekly_load.rpe_load.lower_bound - load_this_week.lower_bound, 0)
        max_week_load = current_week_target.target_weekly_load.rpe_load.upper_bound - load_this_week.upper_bound

        lowest_acceptable_load = min(lowest_acceptable_load, min_week_load)
        highest_acceptable_load = min(highest_acceptable_load, max_week_load)

        # TODO calculate training load metrics for each potential workout given the athlete's training history
        # right stinking here

        for r in required_exercises:
            for w in workouts:
                workout_score = self.get_workout_score(w, r, StandardErrorRange(lower_bound=lowest_acceptable_load,
                                                                                upper_bound=highest_acceptable_load))
                w.score = max(workout_score, w.score)

        for r in one_required_exercises:
            for w in workouts:
                workout_score = self.get_workout_score(w, r, StandardErrorRange(lower_bound=lowest_acceptable_load,
                                                                                upper_bound=highest_acceptable_load),
                                                       self.model.one_required_combination)
                w.score = max(workout_score, w.score)

        workouts.sort(key=lambda x: x.score, reverse=True)

        # give tied scores same ranking
        last_score = None
        ranking = 0
        for k in range(0, len(workouts)):
            if last_score is None or last_score > workouts[k].score:
                ranking += 1
            workouts[k].ranking = ranking
            last_score = workouts[k].score

        # TODO: compare acceptable workouts vs top 10-25 rankings

        # acceptable_workouts = [w for w in workouts if
        #                        lowest_acceptable_load <= w.session_rpe * w.duration <= highest_acceptable_load and
        #                        #lowest_acceptable_rpe <= w.session_rpe <= highest_acceptable_rpe) and
        #                        w.session_rpe <= highest_acceptable_rpe and
        #                        shortest_acceptable_duration <= w.duration <= longest_acceptable_duration]
        #
        # combinations = self.get_acceptable_workouts_from_combinations(acceptable_workouts, min_week_load, max_week_load,
        #                                                               min_workouts_week, max_workouts_week)
        #
        # return combinations

        return workouts

    def get_non_completed_required_exercises(self, required_exercises,
                                             completed_session_details_list: [CompletedSessionDetails]):

        found_times = 0

        for r in required_exercises:
            for c in completed_session_details_list:
                if r.sub_adaptation_type in [d.adaptation_type for d in c.session_detailed_load.sub_adaptation_types]:
                    if r.rpe is not None:
                        if r.rpe.lower_bound <= c.session_rpe.lower_bound and c.session_rpe.upper_bound <= r.rpe.upper_bound:
                            found = True
                        else:
                            found = False
                    else:
                        found = True
                    if r.duration is not None:
                        if found and r.duration.lower_bound <= c.duration <= r.duration.upper_bound:
                            found = True
                        else:
                            found = False
                    if found:
                        if r.times_per_week.lower_bound is not None:
                            r.times_per_week.lower_bound = max(0, r.times_per_week.lower_bound - 1)
                            found_times += 1
                        if r.times_per_week.upper_bound is not None:
                            r.times_per_week.upper_bound = max(0, r.times_per_week.upper_bound - 1)

        return required_exercises, found_times

    def combinations_without_repetition(self, r, iterable=None, values=None, counts=None):
        if iterable:
            values, counts = zip(*Counter(iterable).items())

        f = lambda i, c: chain.from_iterable(map(repeat, i, c))
        if counts is None:
            return
        n = len(counts)
        indices = list(islice(f(count(), counts), r))
        if len(indices) < r:
            return
        while True:
            yield tuple(values[i] for i in indices)
            for i, j in zip(reversed(range(r)), f(reversed(range(n)), reversed(counts))):
                if indices[i] != j:
                    break
            else:
                return
            j = indices[i] + 1
            for i, j in zip(range(i, r), f(count(j), islice(counts, j, None))):
                indices[i] = j

    def get_acceptable_workouts_from_combinations(self, workouts, lowest_weekly_load_target, highest_weekly_load_target,
                                                  lowest_workouts_week, highest_workouts_week):

        # returns the combinations for each number of workouts that week that targets the desired range of load

        workouts_per_week = list(range(lowest_workouts_week, highest_workouts_week + 1))
        workout_combinations = []

        for w in workouts_per_week:
            for k in self.combinations_without_repetition(w, iterable=workouts):
                k = list(k)
                weekly_load = sum(t.session_load for t in k)
                if lowest_weekly_load_target <= weekly_load <= highest_weekly_load_target:
                    workout_combinations.append(k)

        unique_workouts = set(x for l in workout_combinations for x in l)

        return unique_workouts

    def get_workout_score(self, test_workout, recommended_exercise, target_load_range, one_required_combination=None):

        if recommended_exercise.rpe is not None:
            if recommended_exercise.rpe.upper_bound is not None and (recommended_exercise.rpe.lower_bound <= test_workout.projected_session_rpe.lower_bound and test_workout.projected_rpe_load.upper_bound <= recommended_exercise.rpe.upper_bound):
                rpe_score = 1.0
            elif recommended_exercise.rpe.upper_bound is not None and (
                    test_workout.projected_session_rpe.upper_bound > recommended_exercise.rpe.upper_bound):
                rpe_score = 0.0
            elif recommended_exercise.rpe.lower_bound <= test_workout.projected_session_rpe.lower_bound:
                rpe_score = 1.0
            elif test_workout.projected_session_rpe.upper_bound > recommended_exercise.rpe.upper_bound:
                rpe_score = 0.0
            else:
                rpe_score = test_workout.projected_session_rpe.lower_bound / recommended_exercise.rpe.lower_bound
        else:
            rpe_score = 1.0

        if recommended_exercise.duration is not None:
            if recommended_exercise.duration.lower_bound <= test_workout.duration <= recommended_exercise.duration.upper_bound:
                duration_score = 1.0
            elif test_workout.duration > recommended_exercise.duration.upper_bound:
                duration_score = recommended_exercise.duration.upper_bound / test_workout.duration

            else:
                duration_score = test_workout.duration / recommended_exercise.duration.lower_bound
        else:
            duration_score = 1.0

        if target_load_range.upper_bound is not None and (
                target_load_range.lower_bound <= test_workout.projected_rpe_load.lower_bound and test_workout.projected_rpe_load.upper_bound <= target_load_range.upper_bound):
            load_score = 1.0
        elif target_load_range.upper_bound is not None and (test_workout.projected_rpe_load.upper_bound > target_load_range.upper_bound):
            load_score = 0.0
        elif target_load_range.lower_bound <= test_workout.projected_rpe_load.lower_bound:
            load_score = 1.0
        elif test_workout.projected_rpe_load.upper_bound > target_load_range.upper_bound:
            load_score = 0.0
        else:
            load_score = test_workout.projected_rpe_load.lower_bound / target_load_range.lower_bound

        cosine_similarity = WorkoutScoringManager.cosine_similarity(test_workout.session_detailed_load.sub_adaptation_types, [RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type, recommended_exercise.sub_adaptation_type, 1)])

        if cosine_similarity > 0:
            if one_required_combination is None:
                times_per_week_score = recommended_exercise.times_per_week.lower_bound / float(5)
            else:
                times_per_week_score = one_required_combination.lower_bound / float(5)
        else:
            times_per_week_score = 0

        composite_score = ((times_per_week_score * .2) + (rpe_score * .2) + (duration_score * .2) + (load_score * .2) + (cosine_similarity * .2)) * 100

        return composite_score




