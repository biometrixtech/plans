from models.periodization import AthleteTrainingHistory, PeriodizationPlan, PeriodizationPlanWeek
from itertools import combinations, chain, repeat, islice, count
from collections import Counter


class PeriodizationPlanProcessor(object):
    def __init__(self, athlete_training_history):
        self.athlete_training_history = athlete_training_history
        self.week_characteristics = []

    def set_mesocycle_volume_intensity(self, number_of_weeks):
        # sets procession from high volume-low intensity to low volume-high intensity over the course of the
        # mesocyle (length defined as number_of_weeks)

        first_week = self.get_first_week_load_characteristics()
        self.week_characteristics = [first_week]


        for t in range(1, number_of_weeks):
            pass
        pass

    def get_first_week_load_characteristics(self):
        # TODO - should we do more than just copy over athlete's history here?
        periodization_plan_week = PeriodizationPlanWeek()
        periodization_plan_week.target_longest_session_duration = self.athlete_training_history.longest_session_duration
        periodization_plan_week.target_week_average_session_duration = self.athlete_training_history.average_session_duration
        periodization_plan_week.target_shortest_session_duration = self.athlete_training_history.shortest_session_duration
        periodization_plan_week.target_highest_session_rpe = self.athlete_training_history.highest_session_rpe
        periodization_plan_week.target_average_session_rpe = self.athlete_training_history.average_session_rpe
        periodization_plan_week.target_highest_load_session = self.athlete_training_history.highest_load_session
        periodization_plan_week.target_highest_load_day = self.athlete_training_history.highest_load_day
        periodization_plan_week.target_average_load_session = self.athlete_training_history.average_load_session
        periodization_plan_week.target_average_load_day = self.athlete_training_history.average_load_day
        periodization_plan_week.target_lowest_session_rpe = self.athlete_training_history.lowest_session_rpe # TODO: how to determine this? do we need to?
        periodization_plan_week.target_lowest_load_session = self.athlete_training_history.lowest_load_session  # TODO: how to determine this? do we need to?
        periodization_plan_week.target_average_number_sessions_per_microcycle = self.athlete_training_history.average_number_sessions_per_week

        return periodization_plan_week

    def get_acceptable_workouts(self, week_number, workouts, min_week_load, max_week_load, completed_sessions):

        current_week_characterstics = self.week_characteristics[week_number]

        lowest_acceptable_load = current_week_characterstics.target_lowest_load_session
        highest_acceptable_load = current_week_characterstics.target_highest_load_session
        lowest_acceptable_rpe = current_week_characterstics.target_lowest_session_rpe
        highest_acceptable_rpe = current_week_characterstics.target_highest_session_rpe
        shortest_acceptable_duration = current_week_characterstics.target_shortest_session_duration
        longest_acceptable_duration = current_week_characterstics.target_longest_session_duration

        min_workouts_week = self.athlete_training_history.min_number_sessions_per_week - len(completed_sessions)
        max_workouts_week = self.athlete_training_history.max_number_sessions_per_week - len(completed_sessions)

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





