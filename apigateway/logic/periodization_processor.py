from models.periodization import PeriodizationPlanWeek, PeriodizationModelFactory, PeriodizationPlan, TemplateWorkout
from itertools import combinations, chain, repeat, islice, count
from collections import Counter
from models.training_volume import StandardErrorRange
from statistics import mean
from models.training_load import TrainingLoad, CompletedSessionDetails, LoadType, DetailedTrainingLoad
from models.movement_tags import AdaptationDictionary, AdaptationTypeMeasure, SubAdaptationType, DetailedAdaptationType
from logic.training_load_calcs import TrainingLoadCalculator
from models.planned_exercise import PlannedWorkoutLoad
from models.body_parts import BodyPartLocation
from models.ranked_types import RankedBodyPart, RankedAdaptationType
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

        candidate_durations = []
        recommended_durations = []
        if len(candidate_exercise_priorities) > 0:
            if candidate_exercise_priorities[0].adaptation_type_measure == AdaptationTypeMeasure.sub_adaptation_type:
                candidate_duration_dict = {p.adaptation_type.value: p.duration for p in candidate_exercise_priorities}
                candidate_durations = [candidate_duration_dict.get(sat.value, 0) or 0 for sat in SubAdaptationType]
                recommended_duration_dict = {p.adaptation_type.value: p.duration for p in recommended_exercise_priorities}
                recommended_durations = [recommended_duration_dict.get(sat.value, 0) or 0 for sat in SubAdaptationType]
            elif candidate_exercise_priorities[0].adaptation_type_measure == AdaptationTypeMeasure.detailed_adaptation_type:
                candidate_duration_dict = {p.adaptation_type.value: p.duration for p in candidate_exercise_priorities}
                candidate_durations = [candidate_duration_dict.get(dat.value, 0) or 0 for dat in DetailedAdaptationType]
                recommended_duration_dict = {p.adaptation_type.value: p.duration for p in recommended_exercise_priorities}
                recommended_durations = [recommended_duration_dict.get(dat.value, 0) or 0 for dat in DetailedAdaptationType]

        if len(candidate_durations) > 0 and len(recommended_durations) > 0:
            difference = [abs(cand - rec) for cand, rec in zip(candidate_durations, recommended_durations)]
            percent_covered = [max([1 - diff / rec, 0]) for diff, rec in zip(difference, recommended_durations) if rec > 0]
            if len(percent_covered) > 0:
                cosine_similarity_3 = sum(percent_covered) / len(percent_covered)
            else:
                cosine_similarity_3 = 0
        else:
            cosine_similarity_3 = 0

        average_cosine_similarity = (cosine_similarity_1 + cosine_similarity_2 + cosine_similarity_3) / 3

        return average_cosine_similarity


class TargetLoadCalculator(object):

    def get_weekly_load_target(self, average_training_load, acwr_range):

        load_calcs_load = [average_training_load.lower_bound * acwr_range.lower_bound,
                           average_training_load.lower_bound * acwr_range.upper_bound,
                           average_training_load.upper_bound * acwr_range.lower_bound,
                           average_training_load.upper_bound * acwr_range.upper_bound]

        min_load_calcs_load = min(load_calcs_load)
        max_load_calcs_load = max(load_calcs_load)
        load = StandardErrorRange(lower_bound=min_load_calcs_load, upper_bound=max_load_calcs_load,
                                  observed_value=(min_load_calcs_load + max_load_calcs_load) / float(2))
        return load

    def get_target_session_volume(self, min_workouts_week, max_workouts_week, target_session_rpe, weekly_load_target):
        target_weekly_volumes = [weekly_load_target.lower_bound / float(target_session_rpe.lower_bound),
                                 weekly_load_target.lower_bound / float(target_session_rpe.upper_bound),
                                 weekly_load_target.upper_bound / float(target_session_rpe.lower_bound),
                                 weekly_load_target.upper_bound / float(target_session_rpe.upper_bound),

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

        target_session_volume = StandardErrorRange(lower_bound=target_session_volume_lower,
                                                   upper_bound=target_session_volume_upper,
                                                   observed_value=(target_session_volume_lower + target_session_volume_upper) / 2)

        return target_session_volume

    def get_target_session_rpe(self, average_session_rpe, progression, rpe_load_rate_increase):

        sample_volume = 1000
        lowest_load = average_session_rpe.lower_bound * sample_volume
        new_lowest_load = (lowest_load * rpe_load_rate_increase.lower_bound)
        vol_increase_100_contribution = new_lowest_load / float(average_session_rpe.lower_bound)
        vol_increase_scaled_contribution = ((vol_increase_100_contribution - sample_volume) * progression.volume_load_contribution) + sample_volume

        rep_load_rate_lower_rpe_lower = ((rpe_load_rate_increase.lower_bound * average_session_rpe.lower_bound)
                                         - average_session_rpe.lower_bound)
        rep_load_rate_upper_rpe_lower = ((rpe_load_rate_increase.upper_bound * average_session_rpe.lower_bound)
                                         - average_session_rpe.lower_bound)
        rep_load_rate_lower_rpe_upper = ((rpe_load_rate_increase.lower_bound * average_session_rpe.upper_bound)
                                         - average_session_rpe.upper_bound)
        rep_load_rate_upper_rpe_upper = ((rpe_load_rate_increase.upper_bound * average_session_rpe.upper_bound)
                                         - average_session_rpe.upper_bound)

        target_rpes = [(rep_load_rate_lower_rpe_lower * progression.rpe_load_contribution) + average_session_rpe.lower_bound,
                       (rep_load_rate_upper_rpe_lower * progression.rpe_load_contribution) + average_session_rpe.lower_bound,
                       (rep_load_rate_lower_rpe_upper * progression.rpe_load_contribution) + average_session_rpe.upper_bound,
                       (rep_load_rate_upper_rpe_upper * progression.rpe_load_contribution) + average_session_rpe.upper_bound,
                       ]
        target_rpe_lower = min(target_rpes)
        target_rpe_upper = max(target_rpes)

        new_factor_lowest_load = target_rpe_lower * vol_increase_scaled_contribution
        adjustment = new_lowest_load / new_factor_lowest_load

        target_session_rpe = StandardErrorRange(lower_bound=target_rpe_lower * adjustment,
                                                upper_bound=target_rpe_upper * adjustment,
                                                observed_value=((target_rpe_lower + target_rpe_upper) / 2) * adjustment)

        return target_session_rpe

    def get_target_session_load_and_rate(self, average_session_load, last_weeks_load, weekly_load_target):
        net_weeks_load_increase_lower = weekly_load_target.lower_bound - last_weeks_load.lower_bound
        net_weeks_load_increase_upper = weekly_load_target.upper_bound - last_weeks_load.upper_bound

        load_rate_increase_lower = (last_weeks_load.lower_bound + net_weeks_load_increase_lower) / float(
            last_weeks_load.lower_bound)
        load_rate_increase_upper = (last_weeks_load.upper_bound + net_weeks_load_increase_upper) / float(
            last_weeks_load.upper_bound)

        target_session_loads = [load_rate_increase_lower * average_session_load.lower_bound,
                                load_rate_increase_lower * average_session_load.upper_bound,
                                load_rate_increase_upper * average_session_load.lower_bound,
                                load_rate_increase_upper * average_session_load.upper_bound]

        min_session_load = min(target_session_loads)
        max_session_load = max(target_session_loads)
        target_session_load = StandardErrorRange(lower_bound=min_session_load,
                                                 upper_bound=max_session_load,
                                                 observed_value=(min_session_load + max_session_load) / 2)

        target_session_rate = StandardErrorRange(lower_bound=load_rate_increase_lower,
                                                 upper_bound=load_rate_increase_upper,
                                                 observed_value=(load_rate_increase_lower + load_rate_increase_upper) / 2)

        return target_session_load, target_session_rate

    def get_updated_session_load_target(self, current_weekly_target_load, target_session_load, load_this_week):

        min_week_load = max(current_weekly_target_load.lower_bound - load_this_week.lower_bound, 0)
        max_week_load = current_weekly_target_load.upper_bound - load_this_week.upper_bound
        lowest_acceptable_session_load = min(target_session_load.lower_bound, min_week_load)
        highest_acceptable_session_load = min(target_session_load.upper_bound, max_week_load)

        acceptable_session_load = StandardErrorRange(lower_bound=lowest_acceptable_session_load,
                                                     upper_bound=highest_acceptable_session_load,
                                                     observed_value=(lowest_acceptable_session_load +
                                                                     highest_acceptable_session_load) / 2)
        return acceptable_session_load



class PeriodizationPlanProcessor(object):
    def __init__(self, event_date, athlete_periodization_goal, athlete_persona, training_phase_type, completed_session_details_datastore, workout_library_datastore, exclude_completed=True):
        self.start_date = event_date

        self.persona = athlete_persona
        self.goal = athlete_periodization_goal
        self.training_phase_type = training_phase_type
        self.model = PeriodizationModelFactory().create(persona=athlete_persona, training_phase_type=training_phase_type, periodization_goal=athlete_periodization_goal)
        self.exclude_completed = exclude_completed
        self.completed_session_details_datastore = completed_session_details_datastore
        self.workout_library_datastore = workout_library_datastore
        self.current_weekly_workouts = []
        self.weekly_targets = []
        self.current_weekly_load = TrainingLoad()
        self.last_week_workouts = []
        self.previous_week_1_workouts = []
        self.previous_week_2_workouts = []
        self.previous_week_3_workouts = []
        self.previous_week_4_workouts = []

        self.average_session_duration = StandardErrorRange()
        self.average_session_rpe = StandardErrorRange()
        self.average_sessions_per_week = StandardErrorRange()
        self.average_session_load = TrainingLoad()
        #self.average_day_load = TrainingLoad()

        self.last_week_rpe_load_values = []
        self.previous_week_1_rpe_load_values = []
        self.previous_week_2_rpe_load_values = []
        self.previous_week_3_rpe_load_values = []
        self.previous_week_4_rpe_load_values = []

        self.last_week_power_load_values = []
        self.previous_week_1_power_load_values = []
        self.previous_week_2_power_load_values = []
        self.previous_week_3_power_load_values = []
        self.previous_week_4_power_load_values = []

        self.last_week_rpe_values = []
        self.previous_week_1_rpe_values = []
        self.previous_week_2_rpe_values = []
        self.previous_week_3_rpe_values = []
        self.previous_week_4_rpe_values = []

        # self.last_week_rpe_load_sum = None
        # self.previous_week_1_rpe_load_sum = None
        # self.previous_week_2_rpe_load_sum = None
        # self.previous_week_3_rpe_load_sum = None
        # self.previous_week_4_rpe_load_sum = None
        self.chronic_rpe_load_average = None

        # self.last_week_power_load_sum = None
        # self.previous_week_1_power_load_sum = None
        # self.previous_week_2_power_load_sum = None
        # self.previous_week_3_power_load_sum = None
        # self.previous_week_4_power_load_sum = None
        self.chronic_power_load_average = None

        self.last_weeks_load = TrainingLoad()
        self.previous_1_weeks_load = TrainingLoad()
        self.previous_2_weeks_load = TrainingLoad()
        self.previous_3_weeks_load = TrainingLoad()
        self.previous_4_weeks_load = TrainingLoad()

        self.average_last_four_weeks_load = TrainingLoad()

        self.current_weeks_detailed_load = DetailedTrainingLoad()
        self.last_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_1_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_2_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_3_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_4_weeks_detailed_load = DetailedTrainingLoad()

        self.last_seven_days_workouts = []
        self.last_seven_days_detailed_load = DetailedTrainingLoad()
        self.last_seven_days_ranked_muscles = []
        self.last_seven_days_highest_muscle_load = 0
        self.muscle_load_needs = {}

    def get_last_four_weeks_power_load(self):

        power_load_list = []

        if self.last_weeks_load.power_load is not None:
            power_load_list.append(self.last_weeks_load.power_load)

        if self.previous_1_weeks_load.power_load is not None:
            power_load_list.append(self.previous_1_weeks_load.power_load)

        if self.previous_2_weeks_load.power_load is not None:
            power_load_list.append(self.previous_2_weeks_load.power_load)

        if self.previous_3_weeks_load.power_load is not None:
            power_load_list.append(self.previous_3_weeks_load.power_load)

        return power_load_list

    def get_last_four_weeks_rpe_load(self):

        load_list = []

        if self.last_weeks_load.rpe_load is not None:
            load_list.append(self.last_weeks_load.rpe_load)

        if self.previous_1_weeks_load.rpe_load is not None:
            load_list.append(self.previous_1_weeks_load.rpe_load)

        if self.previous_2_weeks_load.rpe_load is not None:
            load_list.append(self.previous_2_weeks_load.rpe_load)

        if self.previous_3_weeks_load.rpe_load is not None:
            load_list.append(self.previous_3_weeks_load.rpe_load)

        return load_list

    def create_periodization_plan(self, start_date):

        self.start_date = start_date
        self.load_completed_workouts(start_date)
        self.populate_values()
        self.sum_weeks()
        self.calculate_averages()
        self.set_weekly_targets()
        self.sum_detailed_load()

        periodization_plan = PeriodizationPlan(self.start_date, self.goal, self.training_phase_type, self.persona)
        week_number = 0
        # workouts = self.workout_library_datastore.get()
        # periodization_plan.next_workouts[0] = self.get_ranked_workouts(week_number,
        #                                                                workouts=workouts,
        #                                                                completed_session_details_list=self.current_weekly_workouts,
        #                                                                exclude_completed=self.exclude_completed)

        template_workout = self.get_template_workout(week_number, self.current_weekly_workouts)
        template_workout.muscle_load_ranking = self.muscle_load_needs
        template_workout = self.add_adaptation_type_needs_from_required_to_template(template_workout)

        periodization_plan.template_workout = template_workout

        return periodization_plan

    def update_periodization_plan(self, periodization_plan: PeriodizationPlan, event_date):

        self.start_date = periodization_plan.start_date
        week_start_date = periodization_plan.get_week_start_date(event_date)
        self.load_completed_workouts(week_start_date)
        self.populate_values()
        self.sum_weeks()
        self.calculate_averages()
        self.set_weekly_targets()
        self.sum_detailed_load()

        periodization_plan.athlete_persona = self.persona
        periodization_plan.training_phase = self.training_phase_type
        periodization_plan.periodization_goal = self.goal

        week_number = periodization_plan.get_week_number(event_date)
        # workouts = self.workout_library_datastore.get()
        # periodization_plan.next_workouts[0] = self.get_ranked_workouts(week_number,
        #                                                                workouts=workouts,
        #                                                                completed_session_details_list=self.current_weekly_workouts,
        #                                                                exclude_completed=self.exclude_completed)

        template_workout = self.get_template_workout(week_number, self.current_weekly_workouts)
        template_workout.muscle_load_ranking = self.muscle_load_needs
        template_workout = self.add_adaptation_type_needs_from_required_to_template(template_workout)

        periodization_plan.template_workout = template_workout

        return periodization_plan

    def load_completed_workouts(self, week_start_date):

        self.current_weekly_workouts = self.completed_session_details_datastore.get(
            start_date_time=week_start_date, end_date_time=week_start_date+timedelta(days=6))
        rpe_load_values = [l.rpe_load for l in self.current_weekly_workouts]
        power_load_values = [l.power_load for l in self.current_weekly_workouts]
        self.current_weekly_load.rpe_load = StandardErrorRange.get_sum_from_error_range_list(rpe_load_values)
        self.current_weekly_load.power_load = StandardErrorRange.get_sum_from_error_range_list(power_load_values)

        self.last_week_workouts = self.completed_session_details_datastore.get(
            start_date_time=week_start_date - timedelta(days=7), end_date_time=week_start_date - timedelta(days=1))
        self.previous_week_1_workouts = self.completed_session_details_datastore.get(
            start_date_time=week_start_date - timedelta(days=14), end_date_time=week_start_date - timedelta(days=8))
        self.previous_week_2_workouts = self.completed_session_details_datastore.get(
            start_date_time=week_start_date - timedelta(days=21), end_date_time=week_start_date - timedelta(days=15))
        self.previous_week_3_workouts = self.completed_session_details_datastore.get(
            start_date_time=week_start_date - timedelta(days=28), end_date_time=week_start_date - timedelta(days=22))
        self.previous_week_4_workouts = self.completed_session_details_datastore.get(
            start_date_time=week_start_date - timedelta(days=35), end_date_time=week_start_date - timedelta(days=29))

        self.last_seven_days_workouts = self.completed_session_details_datastore.get(
            start_date_time=self.start_date - timedelta(days=7), end_date_time=self.start_date)

    def add_adaptation_type_needs_from_required_to_template(self, template_workout: TemplateWorkout):

        # get an adaptation type (with duration) for each one needed by required workouts
        # rank in order of what's required
        completed_session_details_list = self.current_weekly_workouts
        # first how many of the plan's recommended workouts have not been completed?
        required_exercises = self.get_non_completed_required_exercises(self.model.required_exercises,
                                                                       completed_session_details_list)

        one_required_exercises = self.get_non_completed_required_exercises(self.model.one_required_exercises,
                                                                           completed_session_details_list)
        for combination in self.model.one_required_combinations:
            relevant_one_required_exercises = [o for o in one_required_exercises if o.periodization_id == combination.periodization_id]
            total_found_times = [r.found_times for r in relevant_one_required_exercises]
            total_found = 0
            if len(total_found_times) > 0:
                total_found = sum(total_found_times)

            relevent_combinations = [c for c in self.model.one_required_combinations if c.periodization_id == combination.periodization_id]
            for relevant_combo in relevent_combinations:
                if relevant_combo.combination_range.lower_bound is not None:
                    relevant_combo.combination_range.lower_bound = relevant_combo.combination_range.lower_bound - total_found
                if relevant_combo.combination_range.upper_bound is not None:
                    relevant_combo.combination_range.upper_bound = relevant_combo.combination_range.upper_bound - total_found

        # adjust required workout ranges to athlete's rpe and duration capacities:
        for r in required_exercises:
            if r.rpe is not None:
                r.rpe.upper_bound = min(r.rpe.upper_bound, template_workout.acceptable_session_rpe.upper_bound)
            if r.duration is not None:
                r.duration.upper_bound = min(r.duration.upper_bound, template_workout.acceptable_session_duration.upper_bound)
                if r.duration.upper_bound < r.duration.lower_bound:
                    r.duration.lower_bound = template_workout.acceptable_session_duration.lower_bound

        for r in one_required_exercises:
            if r.rpe is not None:
                r.rpe.upper_bound = min(r.rpe.upper_bound, template_workout.acceptable_session_rpe.upper_bound)
            if r.duration is not None:
                r.duration.upper_bound = min(r.duration.upper_bound, template_workout.acceptable_session_duration.upper_bound)
                if r.duration.upper_bound < r.duration.lower_bound:
                    r.duration.lower_bound = template_workout.acceptable_session_duration.lower_bound

        all_required_exercises = []
        all_required_exercises.extend(required_exercises)
        all_required_exercises.extend(one_required_exercises)

        # TODO if nothing is required but they're hellbent on working out, we give them a "needs" list like muscle load

        sorted_required_exercises = sorted(all_required_exercises, key=lambda x: (1-x.priority, x.times_per_week.lowest_value()), reverse=True)

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

        template_workout.adaptation_type_ranking = ranked_adaptation_type_list

        return template_workout

    def sum_detailed_load(self):

        seven_days_detailed_load = DetailedTrainingLoad()
        #seven_days_training_type_load = TrainingTypeLoad()
        seven_days_muscle_load = {}
        seven_days_ranked_muscle_load = []

        for completed_session_details in self.last_seven_days_workouts:
            seven_days_detailed_load.add(completed_session_details.session_detailed_load)
            #seven_days_training_type_load.add(completed_session_details.session_training_type_load)
            for ranked_body_part in completed_session_details.ranked_muscle_load:
                if ranked_body_part not in seven_days_muscle_load:
                    seven_days_muscle_load[ranked_body_part.body_part_location] = ranked_body_part.power_load
                else:
                    seven_days_muscle_load[ranked_body_part.body_part_location].add(ranked_body_part.power_load)

        for body_part_location, power_load in seven_days_muscle_load.items():
            ranked_body_part = RankedBodyPart(body_part_location, 0)
            ranked_body_part.power_load = power_load
            seven_days_ranked_muscle_load.append(ranked_body_part)

        muscle_groups = BodyPartLocation.muscle_groups()
        missing_muscle_groups = [m for m in muscle_groups if m not in seven_days_muscle_load.keys()]

        sorted_seven_days_ranked_muscle_load = sorted(seven_days_ranked_muscle_load, key=lambda x: x.power_load.highest_value(), reverse=True)

        for s in range(0, len(sorted_seven_days_ranked_muscle_load)):
            sorted_seven_days_ranked_muscle_load[s].ranking = s+1
            self.last_seven_days_highest_muscle_load = max(sorted_seven_days_ranked_muscle_load[s].power_load.highest_value(),self.last_seven_days_highest_muscle_load)

        for m in missing_muscle_groups:
            self.muscle_load_needs[m] = 100

        for s in sorted_seven_days_ranked_muscle_load:
            self.muscle_load_needs[s.body_part_location] = 100 - ((s.power_load.highest_value() / self.last_seven_days_highest_muscle_load) * 100)

        self.last_seven_days_detailed_load = seven_days_detailed_load
        self.last_seven_days_detailed_load.rank_adaptation_types()
        self.last_seven_days_ranked_muscles = sorted_seven_days_ranked_muscle_load

    def populate_values(self):

        self.last_week_rpe_load_values = [l.rpe_load for l in self.last_week_workouts if l.rpe_load is not None]
        self.previous_week_1_rpe_load_values = [l.rpe_load for l in self.previous_week_1_workouts if l.rpe_load is not None]
        self.previous_week_2_rpe_load_values = [l.rpe_load for l in self.previous_week_2_workouts if l.rpe_load is not None]
        self.previous_week_3_rpe_load_values = [l.rpe_load for l in self.previous_week_3_workouts if l.rpe_load is not None]
        self.previous_week_4_rpe_load_values = [l.rpe_load for l in self.previous_week_4_workouts if l.rpe_load is not None]

        self.last_week_power_load_values = [l.power_load for l in self.last_week_workouts if l.power_load is not None]
        self.previous_week_1_power_load_values = [l.power_load for l in self.previous_week_1_workouts if l.power_load is not None]
        self.previous_week_2_power_load_values = [l.power_load for l in self.previous_week_2_workouts if l.power_load is not None]
        self.previous_week_3_power_load_values = [l.power_load for l in self.previous_week_3_workouts if l.power_load is not None]
        self.previous_week_4_power_load_values = [l.power_load for l in self.previous_week_4_workouts if l.power_load is not None]

        self.last_week_rpe_values = [l.session_RPE for l in self.last_week_workouts if l.session_RPE is not None]
        self.previous_week_1_rpe_values = [l.session_RPE for l in self.previous_week_1_workouts if l.session_RPE is not None]
        self.previous_week_2_rpe_values = [l.session_RPE for l in self.previous_week_2_workouts if l.session_RPE is not None]
        self.previous_week_3_rpe_values = [l.session_RPE for l in self.previous_week_3_workouts if l.session_RPE is not None]
        self.previous_week_4_rpe_values = [l.session_RPE for l in self.previous_week_4_workouts if l.session_RPE is not None]

    def sum_weeks(self):

        self.last_weeks_load.rpe_load = StandardErrorRange.get_sum_from_error_range_list(self.last_week_rpe_load_values)
        self.previous_1_weeks_load.rpe_load = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_1_rpe_load_values)
        self.previous_2_weeks_load.rpe_load = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_2_rpe_load_values)
        self.previous_3_weeks_load.rpe_load = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_3_rpe_load_values)
        self.previous_4_weeks_load.rpe_load = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_4_rpe_load_values)

        self.last_weeks_load.power_load = StandardErrorRange.get_sum_from_error_range_list(
            self.last_week_power_load_values)
        self.previous_1_weeks_load.power_load = StandardErrorRange.get_sum_from_error_range_list(
            self.previous_week_1_power_load_values)
        self.previous_2_weeks_load.power_load = StandardErrorRange.get_sum_from_error_range_list(
            self.previous_week_2_power_load_values)
        self.previous_3_weeks_load.power_load = StandardErrorRange.get_sum_from_error_range_list(
            self.previous_week_3_power_load_values)
        self.previous_4_weeks_load.power_load = StandardErrorRange.get_sum_from_error_range_list(
            self.previous_week_4_power_load_values)

    def calculate_averages(self):

        rpe_chronic_weeks = [self.previous_1_weeks_load.rpe_load,
                             self.previous_2_weeks_load.rpe_load,
                             self.previous_3_weeks_load.rpe_load,
                             self.previous_4_weeks_load.rpe_load]

        power_chronic_weeks = [self.previous_1_weeks_load.power_load,
                               self.previous_2_weeks_load.power_load,
                               self.previous_3_weeks_load.power_load,
                               self.previous_4_weeks_load.power_load]

        self.chronic_rpe_load_average = StandardErrorRange.get_average_from_error_range_list(rpe_chronic_weeks)
        self.chronic_power_load_average = StandardErrorRange.get_average_from_error_range_list(power_chronic_weeks)

        last_four_weeks_rpe_load = self.get_last_four_weeks_rpe_load()
        last_four_weeks_power_load = self.get_last_four_weeks_power_load()
        lower_bounds_rpe_load = [w.lower_bound for w in last_four_weeks_rpe_load if w.lower_bound is not None]
        upper_bounds_rpe_load = [w.upper_bound for w in last_four_weeks_rpe_load if w.upper_bound is not None]
        lower_bounds_power_load = [w.lower_bound for w in last_four_weeks_power_load if w.lower_bound is not None]
        upper_bounds_power_load = [w.upper_bound for w in last_four_weeks_power_load if w.upper_bound is not None]

        average_last_four_weeks_rpe_load = StandardErrorRange(lower_bound=mean(lower_bounds_rpe_load),
                                                              upper_bound=mean(upper_bounds_rpe_load))

        average_last_four_weeks_power_load = StandardErrorRange(lower_bound=mean(lower_bounds_power_load),
                                                                upper_bound=mean(upper_bounds_power_load))

        self.average_last_four_weeks_load.rpe_load = average_last_four_weeks_rpe_load
        self.average_last_four_weeks_load.power_load = average_last_four_weeks_power_load

        last_two_weeks_sessions = self.last_week_power_load_values
        last_two_weeks_sessions.extend(self.previous_week_1_power_load_values)
        if len(self.last_week_power_load_values) <= 1:
            last_two_weeks_sessions.extend(self.previous_week_2_power_load_values)

        self.average_session_load.power_load = StandardErrorRange.get_average_from_error_range_list(last_two_weeks_sessions)

        last_two_weeks_sessions_rpe = self.last_week_rpe_load_values
        last_two_weeks_sessions_rpe.extend(self.previous_week_1_rpe_load_values)
        if len(self.previous_week_1_rpe_load_values) <= 1:
            last_two_weeks_sessions.extend(self.previous_week_2_rpe_load_values)

        self.average_session_load.rpe_load = StandardErrorRange.get_average_from_error_range_list(last_two_weeks_sessions_rpe)

        last_two_weeks_rpes = self.last_week_rpe_values
        last_two_weeks_rpes.extend(self.previous_week_1_rpe_values)
        if len(self.last_week_rpe_values) <= 1:
            last_two_weeks_rpes.extend(self.previous_week_2_rpe_values)

        self.average_session_rpe = StandardErrorRange.get_average_from_error_range_list(last_two_weeks_rpes)

        sessions_per_week = []
        started = False
        if len(self.previous_week_4_workouts) > 0:
            sessions_per_week.append(len(self.previous_week_4_workouts))
            started = True
        if len(self.previous_week_3_workouts) > 0 or started:
            sessions_per_week.append(len(self.previous_week_3_workouts))
            started = True
        if len(self.previous_week_2_workouts) > 0 or started:
            sessions_per_week.append(len(self.previous_week_2_workouts))
        if len(self.previous_week_1_workouts) > 0 or started:
            sessions_per_week.append(len(self.previous_week_1_workouts))
        sessions_per_week.append(len(self.last_week_workouts))

        self.average_sessions_per_week = StandardErrorRange(lower_bound=min(sessions_per_week), observed_value=mean(sessions_per_week), upper_bound=max(sessions_per_week))

    # def set_athlete_training_history(self):
    #
    #     self.athlete_training_history = AthleteTrainingHistory()
    #
    #     self.athlete_training_history.last_weeks_load.rpe_load = self.training_load_calculator.current_week_rpe_load_sum
    #     self.athlete_training_history.last_weeks_load.power_load = self.training_load_calculator.current_week_power_load_sum
    #
    #     self.athlete_training_history.previous_1_weeks_load.rpe_load = self.training_load_calculator.previous_week_1_rpe_load_sum
    #     self.athlete_training_history.previous_1_weeks_load.power_load = self.training_load_calculator.previous_week_1_power_load_sum
    #
    #     self.athlete_training_history.previous_2_weeks_load.rpe_load = self.training_load_calculator.previous_week_2_rpe_load_sum
    #     self.athlete_training_history.previous_2_weeks_load.power_load = self.training_load_calculator.previous_week_2_power_load_sum
    #
    #     self.athlete_training_history.previous_3_weeks_load.rpe_load = self.training_load_calculator.previous_week_3_rpe_load_sum
    #     self.athlete_training_history.previous_3_weeks_load.power_load = self.training_load_calculator.previous_week_3_power_load_sum
    #
    #     self.athlete_training_history.previous_4_weeks_load.rpe_load = self.training_load_calculator.previous_week_4_rpe_load_sum
    #     self.athlete_training_history.previous_4_weeks_load.power_load = self.training_load_calculator.previous_week_4_power_load_sum
    #
    #     self.athlete_training_history.average_session_load.rpe_load = self.training_load_calculator.average_session_load
    #     self.athlete_training_history.average_session_load.power_load = self.training_load_calculator.average_session_load
    #
    #     self.athlete_training_history.average_session_rpe = self.training_load_calculator.average_session_rpe
    #     self.athlete_training_history.average_sessions_per_week = self.training_load_calculator.average_sessions_per_week
    #
    #     self.athlete_training_history.last_weeks_detailed_load = self.training_load_calculator.last_weeks_detailed_load
    #     self.athlete_training_history.previous_1_weeks_detailed_load = self.training_load_calculator.previous_1_weeks_detailed_load
    #     self.athlete_training_history.previous_2_weeks_detailed_load = self.training_load_calculator.previous_2_weeks_detailed_load
    #     self.athlete_training_history.previous_3_weeks_detailed_load = self.training_load_calculator.previous_3_weeks_detailed_load
    #     self.athlete_training_history.previous_4_weeks_detailed_load = self.training_load_calculator.previous_4_weeks_detailed_load

    def set_weekly_targets(self):
        # sets procession from high volume-low intensity to low volume-high intensity over the course of the
        # mesocyle (length defined as number_of_weeks)

        for t in range(0, len(self.model.progressions)):
            weekly_targets = self.get_weekly_targets(self.model.progressions[t])
            self.weekly_targets.append(weekly_targets)

    def get_weekly_load_target(self, progression, average_training_load):

        calc = TargetLoadCalculator()

        rpe_load = calc.get_weekly_load_target(average_training_load.rpe_load, progression.training_phase.acwr)
        power_load = calc.get_weekly_load_target(average_training_load.power_load, progression.training_phase.acwr)

        load_target = TrainingLoad()
        load_target.rpe_load = rpe_load
        load_target.power_load = power_load

        return load_target

    def get_weekly_targets(self, progression):

        # determine the weekly load increase and determine the RPE/volume contributions according the the progression

        weekly_load_target = self.get_weekly_load_target(progression, self.average_last_four_weeks_load)

        calc = TargetLoadCalculator()

        target_session_rpe_load, rpe_load_rate_increase = calc.get_target_session_load_and_rate(self.average_session_load.rpe_load,
                                                                        self.last_weeks_load.rpe_load,
                                                                        weekly_load_target.rpe_load)

        target_session_power_load, power_load_rate_increase = calc.get_target_session_load_and_rate(self.average_session_load.power_load,
                                                                          self.last_weeks_load.power_load,
                                                                          weekly_load_target.power_load)

        # given load rate of increase, determine the RPE's share of that increase
        # apply adjusted RPE rate of increase

        target_session_rpe = calc.get_target_session_rpe(self.average_session_rpe, progression, rpe_load_rate_increase)

        # target_watts_rates = [1 + (power_load_rate_increase.lower_bound * progression.rpe_load_contribution),
        #                      1 + (power_load_rate_increase.upper_bound * progression.rpe_load_contribution)]
        #
        # target_watts_increase_lower = min(target_watts_rates)
        # target_watts_increase_upper = max(target_watts_rates)

        # now reverse engineer the volume's contribution of increase given load and RPE

        target_session_volume = calc.get_target_session_volume(self.average_sessions_per_week.lower_bound,
                                                               self.average_sessions_per_week.upper_bound,
                                                               target_session_rpe,
                                                               weekly_load_target.rpe_load)

        target_session_load = TrainingLoad()
        target_session_load.rpe_load = target_session_rpe_load
        target_session_load.power_load = target_session_power_load

        periodization_plan_week = PeriodizationPlanWeek()
        periodization_plan_week.target_weekly_load = weekly_load_target
        periodization_plan_week.target_session_load = target_session_load
        periodization_plan_week.target_session_duration = target_session_volume
        periodization_plan_week.target_session_rpe = target_session_rpe

        return periodization_plan_week

    def get_template_workout(self, week_number, completed_session_details_list: [CompletedSessionDetails]):

        template_workout = TemplateWorkout()
        calc = TargetLoadCalculator()

        current_week_target = self.weekly_targets[week_number]

        # TODO - how do we adjust weekly workouts (based on goals) when they appear to exceed athlete's number of expected workouts?

        rpe_load_this_week = StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)
        power_load_this_week = StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)

        for c in completed_session_details_list:
            rpe_load_this_week.add(c.rpe_load)
            power_load_this_week.add(c.power_load)

        # even though we subtracted out existing load this week in the weekly target step,
        # the weekly load value here is the overall target and doesn't consider load this week
        acceptable_session_rpe_load = calc.get_updated_session_load_target(current_week_target.target_weekly_load.rpe_load,
                                                                           current_week_target.target_session_load.rpe_load,
                                                                           rpe_load_this_week)

        acceptable_session_power_load = calc.get_updated_session_load_target(current_week_target.target_weekly_load.power_load,
                                                                             current_week_target.target_session_load.power_load,
                                                                             power_load_this_week)

        template_workout.acceptable_session_rpe_load = acceptable_session_rpe_load
        template_workout.acceptable_session_power_load = acceptable_session_power_load

        template_workout.adaptation_type_ranking = self.last_seven_days_detailed_load.detailed_adaptation_types

        template_workout.acceptable_session_rpe = current_week_target.target_session_rpe
        template_workout.acceptable_session_duration = current_week_target.target_session_duration

        return template_workout

    def get_non_completed_required_exercises(self, required_exercises,
                                             completed_session_details_list: [CompletedSessionDetails]):

        for r in required_exercises:
            for c in completed_session_details_list:
                if r.sub_adaptation_type is not None and r.sub_adaptation_type in [d.adaptation_type for d in c.session_detailed_load.sub_adaptation_types]:
                    if r.rpe is not None:
                        if r.rpe.lower_bound <= c.session_RPE.lower_bound and c.session_RPE.upper_bound <= r.rpe.upper_bound:
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
                            r.found_times += 1
                        if r.times_per_week.upper_bound is not None:
                            r.times_per_week.upper_bound = max(0, r.times_per_week.upper_bound - 1)
                elif r.sub_adaptation_type is None and r.detailed_adaptation_type is not None and r.detailed_adaptation_type in [d.adaptation_type for d in c.session_detailed_load.detailed_adaptation_types]:
                    if r.rpe is not None:
                        if r.rpe.lower_bound <= c.session_RPE.lower_bound and c.session_RPE.upper_bound <= r.rpe.upper_bound:
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
                            r.found_times += 1
                        if r.times_per_week.upper_bound is not None:
                            r.times_per_week.upper_bound = max(0, r.times_per_week.upper_bound - 1)

        return required_exercises

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

    def complete_a_planned_workout(self, event_date_time, planned_workout: PlannedWorkoutLoad):

        session = CompletedSessionDetails(event_date_time, 1, planned_workout.workout_id)
        session.duration = planned_workout.duration
        session.session_RPE = planned_workout.projected_session_rpe
        session.rpe_load = planned_workout.projected_rpe_load
        session.power_load = planned_workout.projected_power_load
        session.session_detailed_load = planned_workout.session_detailed_load
        session.muscle_detailed_load = planned_workout.muscle_detailed_load

        return session

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

        cosine_similarity = WorkoutScoringManager.cosine_similarity(test_workout.session_detailed_load.sub_adaptation_types, [RankedAdaptationType(AdaptationTypeMeasure.sub_adaptation_type, recommended_exercise.sub_adaptation_type, 1, 0)])

        if cosine_similarity > 0:
            if one_required_combination is None:
                times_per_week_score = recommended_exercise.times_per_week.lower_bound / float(5)
            else:
                times_per_week_score = one_required_combination.lower_bound / float(5)
        else:
            times_per_week_score = 0

        if test_workout.projected_monotony is None or test_workout.projected_monotony.observed_value is None:
            monotony_score = 1.0
        elif test_workout.projected_monotony.observed_value < 1.5:
            monotony_score = 1.0
        elif 1.5 <= test_workout.projected_monotony.observed_value < 2:
            monotony_score = 0.5
        else:
            monotony_score = 0.0

        if test_workout.projected_strain_event_level is None or test_workout.projected_strain_event_level.observed_value is None:
            strain_event_score = 1.0
        elif test_workout.projected_strain_event_level.observed_value == 0:
            strain_event_score = 1.0
        elif 1.5 <= test_workout.projected_strain_event_level.observed_value < 2:
            strain_event_score = 0.5
        else:
            strain_event_score = 0.0

        composite_score = ((monotony_score * .1) + (strain_event_score * .1) + (times_per_week_score * .2) + (rpe_score * .2) + (duration_score * .1) + (load_score * .1) + (cosine_similarity * .2)) * 100

        return composite_score




