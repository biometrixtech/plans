from models.periodization import AthleteTrainingHistory, PeriodizationPlan, PeriodizationPlanWeek, PeriodizationModelFactory
from itertools import combinations, chain, repeat, islice, count
from collections import Counter
from models.training_volume import StandardErrorRange
from statistics import mean


class PeriodizationPlanProcessor(object):
    def __init__(self, athlete_periodization_goal, athlete_training_history, athlete_persona, training_phase_type):
        self.persona = athlete_persona
        self.goal = athlete_periodization_goal
        self.athlete_training_history = athlete_training_history
        self.model = PeriodizationModelFactory().create(persona=athlete_persona, training_phase_type=training_phase_type)
        self.weekly_targets = []

    def set_weekly_targets(self):
        # sets procession from high volume-low intensity to low volume-high intensity over the course of the
        # mesocyle (length defined as number_of_weeks)

        for t in range(0, len(self.model.progressions)):
            weekly_targets = self.get_weekly_targets(self.model.progressions[t])
            self.weekly_targets.append(weekly_targets)

    def get_load_target(self, progression):

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

        load_target = StandardErrorRange()
        load_target.lower_bound = min(load_calcs)
        load_target.upper_bound = max(load_calcs)
        load_target.observed_value = (load_target.upper_bound + load_target.lower_bound) / float(2)

        return load_target

    def get_weekly_targets(self, progression):

        current_rpe_load_lower = self.athlete_training_history.current_weeks_load.rpe_load.lower_bound
        current_rpe_load_upper = self.athlete_training_history.current_weeks_load.rpe_load.upper_bound

        current_rpe_average_load_lower = self.athlete_training_history.average_session_load.rpe_load.lower_bound
        current_rpe_average_load_upper = self.athlete_training_history.average_session_load.rpe_load.upper_bound

        rpe_load_target = self.get_load_target(progression)

        rpe_load_increase_lower = rpe_load_target.lower_bound - current_rpe_load_lower.lower_bound
        rpe_load_increase_upper = rpe_load_target.upper_bound - current_rpe_load_lower.upper_bound

        rpe_load_rate_increase_lower = (current_rpe_load_lower - rpe_load_increase_lower) / float(current_rpe_load_lower)
        rpe_load_rate_increase_upper = (current_rpe_load_upper - rpe_load_increase_upper) / float(
            current_rpe_load_upper)

        target_session_loads = [(1 + rpe_load_rate_increase_lower) * current_rpe_average_load_lower,
                                (1 + rpe_load_rate_increase_lower) * current_rpe_average_load_upper,
                                (1 + rpe_load_rate_increase_upper) * current_rpe_average_load_lower,
                                (1 + rpe_load_rate_increase_upper) * current_rpe_average_load_upper]

        target_session_load_lower = min(target_session_loads)
        target_session_load_upper = max(target_session_loads)

        target_rpe_rates = [1 + (rpe_load_rate_increase_lower * progression.rpe_load_contribution.lower_bound),
                       1 + (rpe_load_rate_increase_lower * progression.rpe_load_contribution.upper_bound),
                       1 + (rpe_load_rate_increase_upper * progression.rpe_load_contribution.lower_bound),
                       1 + (rpe_load_rate_increase_upper * progression.rpe_load_contribution.upper_bound)]

        target_rpe_increase_lower = min(target_rpe_rates)
        target_rpe_increase_upper = max(target_rpe_rates)

        target_rpes = [target_rpe_increase_lower * self.athlete_training_history.current_weeks_average_session_rpe.lower_bound,
                       target_rpe_increase_lower * self.athlete_training_history.current_weeks_average_session_rpe.upper_bound,
                       target_rpe_increase_upper * self.athlete_training_history.current_weeks_average_session_rpe.lower_bound,
                       target_rpe_increase_upper * self.athlete_training_history.current_weeks_average_session_rpe.upper_bound,

        ]

        target_rpe_lower = min(target_rpes)
        target_rpe_upper = max(target_rpes)

        target_volumes = [rpe_load_target.lower_bound / float(target_rpe_lower),
                          rpe_load_target.lower_bound / float(target_rpe_upper),
                          rpe_load_target.upper_bound / float(target_rpe_lower),
                          rpe_load_target.upper_bound / float(target_rpe_upper),

        ]

        target_volume_lower = min(target_volumes)
        target_volume_upper = max(target_volumes)

        periodization_plan_week = PeriodizationPlanWeek()
        periodization_plan_week.target_weekly_load = rpe_load_target
        periodization_plan_week.target_session_load = StandardErrorRange(lower_bound=target_session_load_lower,
                                                                         upper_bound=target_session_load_upper)

        periodization_plan_week.target_session_duration = StandardErrorRange(lower_bound=target_volume_lower,
                                                                             upper_bound=target_volume_upper)
        periodization_plan_week.target_session_rpe = StandardErrorRange(lower_bound=target_rpe_lower,
                                                                        upper_bound=target_rpe_upper)

        return periodization_plan_week

    def get_acceptable_workouts(self, week_number, workouts, min_week_load, max_week_load, completed_sessions):

        current_week_target = self.weekly_targets[week_number]

        lowest_acceptable_load = current_week_target.target_session_load.lower_bound
        highest_acceptable_load = current_week_target.target_session_load.upper_bound

        lowest_acceptable_rpe = current_week_target.target_session_rpe.lower_bound
        highest_acceptable_rpe = current_week_target.target_session_rpe.upper_bound
        shortest_acceptable_duration = current_week_target.target_session_duration.lower_bound
        longest_acceptable_duration = current_week_target.target_session_duration.upper_bound

        min_workouts_week = self.athlete_training_history.average_sessions_per_week.lower_bound - len(completed_sessions)
        max_workouts_week = self.athlete_training_history.average_sessions_per_week.upper_bound - len(completed_sessions)

        workouts = [w for w in workouts if w.id not in [c.id for c in completed_sessions]]

        acceptable_workouts = [w for w in workouts if
                               lowest_acceptable_load <= w.session_rpe * w.duration <= highest_acceptable_load and
                               lowest_acceptable_rpe <= w.session_rpe <= highest_acceptable_rpe and
                               shortest_acceptable_duration <= w.duration <= longest_acceptable_duration]

        load_this_week = sum([c.session_load for c in completed_sessions])
        min_week_load = min_week_load - load_this_week
        max_week_load = max_week_load - load_this_week

        combinations = self.get_acceptable_workouts_from_combinations(acceptable_workouts, min_week_load, max_week_load,
                                                                      min_workouts_week, max_workouts_week)

        return combinations

    def combinations_without_repetition(self, r, iterable=None, values=None, counts=None):
        if iterable:
            values, counts = zip(*Counter(iterable).items())

        f = lambda i, c: chain.from_iterable(map(repeat, i, c))
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





