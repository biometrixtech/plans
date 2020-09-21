from fathomapi.utils.xray import xray_recorder
from models.training_volume import StandardErrorRange
from models.session import HighLoadSession, HighDetailedLoadSession, SessionType
from datetime import timedelta
import statistics, math
from utils import format_date, parse_date
from models.stats import SportMaxLoad
from models.movement_tags import AdaptationType
from logic.athlete_capacity_processing import AthleteCapacityProcessor
from models.athlete_capacity import AthleteBaselineCapacities


class TrainingLoadProcessing(object):
    def __init__(self, start_date, end_date, load_stats, expected_weekly_workouts):
        self.start_date = start_date
        self.end_date = end_date

        #self.load_monitoring_measures = {}

        self.no_soreness_load_tuples = []
        self.soreness_load_tuples = []
        self.load_tuples_last_2_weeks = []
        self.load_tuples_last_2_4_weeks = []
        self.no_soreness_load_tuples_last_2_weeks = []
        self.no_soreness_load_tuples_last_2_4_weeks = []
        #self.recovery_loads = {}
        #self.maintenance_loads = {}
        #self.functional_overreaching_loads = {}
        #self.functional_overreaching_NFO_loads = {}
        #self.high_relative_load_session = False
        self.high_relative_load_sessions = []
        self.high_relative_load_score = 50
        self.last_week_sport_training_loads = {}
        self.previous_week_sport_training_loads = {}
        self.last_14_days_training_sessions = []
        self.last_5_days_training_sessions = []
        self.last_20_days_training_sessions = []
        self.load_stats = load_stats
        self.sport_max_load = {}
        self.adaptation_type_load = {}

        self.average_tissue_load_5_day = None
        self.average_tissue_load_20_day = None
        self.average_force_load_5_day = None
        self.average_force_load_20_day = None
        self.average_power_load_5_day = None
        self.average_power_load_20_day = None

        self.training_sessions_exist_days_8_35 = False

        self.expected_weekly_workouts = expected_weekly_workouts

        # added to support load calcs
        self.last_week_internal_values = []
        self.previous_week_internal_values = []
        self.previous_week_2_internal_values = []
        self.previous_week_3_internal_values = []
        self.previous_week_4_internal_values = []
        self.internal_load_tuples = []
        self.cardio_internal_load_tuples = []
        self.a_internal_load_values = []
        self.c_internal_load_values = []

        self.last_week_power_load_values = []
        self.previous_week_power_load_values = []
        self.previous_week_2_power_load_values = []
        self.previous_week_3_power_load_values = []
        self.previous_week_4_power_load_values = []
        self.power_load_tuples = []
        self.cardio_power_load_tuples = []
        self.a_power_load_values = []
        self.c_power_load_values = []

        self.athlete_capacities = AthleteBaselineCapacities
        self.total_historical_sessions = 0
        # self.acute_days = acute_days
        # self.chronic_days = chronic_days
        # self.acute_start_date_time = acute_start_date_time
        # self.chronic_start_date_time = chronic_start_date_time
        # self.acute_training_sessions = []
        # self.chronic_training_sessions = []

    def get_load_5_20(self, attribute_5_day_name, attribute_20_day_name):

        attribute_5_day = getattr(self, attribute_5_day_name)
        attribute_20_day = getattr(self, attribute_20_day_name)

        if attribute_5_day is not None and attribute_20_day is not None:
            standard_error_range = attribute_5_day.plagiarize()
            standard_error_range.divide_range(attribute_20_day)

            return standard_error_range

        else:

            return None

    def force_load_5_20(self):

        return self.get_load_5_20("average_force_load_5_day", "average_force_load_20_day")

    def rpe_load_5_20(self):

        return self.get_load_5_20("average_rpe_load_5_day", "average_rpe_load_20_day")

    def tissue_load_5_20(self):

        return self.get_load_5_20("average_tissue_load_5_day", "average_tissue_load_20_day")

    def trimp_5_20(self):

        return self.get_load_5_20("average_trimp_load_5_day", "average_trimp_load_20_day")

    def power_load_5_20(self):

        return self.get_load_5_20("average_power_load_5_day", "average_power_load_20_day")

    def work_vo2_load_5_20(self):

        return self.get_load_5_20("average_work_vo2_load_5_day", "average_work_vo2_load_20_day")

    @xray_recorder.capture('logic.TrainingLoadProcessing.load_plan_values')
    def load_training_session_values(self, acute_training_sessions, chronic_weeks_training_sessions,
                                     chronic_training_sessions, pre_acute_chronic_sessions=[]):

        all_training_sessions = []
        all_training_sessions.extend(acute_training_sessions)
        all_training_sessions.extend(chronic_training_sessions)

        if len(all_training_sessions)==0:
            all_training_sessions.extend(pre_acute_chronic_sessions)

        self.last_week_sport_training_loads = {}
        self.previous_week_sport_training_loads = {}

        self.last_week_internal_values = []
        self.internal_load_tuples = []
        self.previous_week_internal_values = []
        self.a_internal_load_values = []
        self.c_internal_load_values = []

        self.last_week_power_load_values = []
        self.power_load_tuples = []
        self.previous_week_power_load_values = []
        self.a_power_load_values = []
        self.c_power_load_values = []

        five_days_ago = parse_date(self.end_date) - timedelta(days=4)
        eight_days_ago = parse_date(self.end_date) - timedelta(days=7)
        fourteen_days_ago = parse_date(self.end_date) - timedelta(days=13)
        twenty_days_ago = parse_date(self.end_date) - timedelta(days=19)
        twenty_one_days_ago = parse_date(self.end_date) - timedelta(days=20)
        twenty_eight_days_ago = parse_date(self.end_date) - timedelta(days=27)
        thirty_five_days_ago = parse_date(self.end_date) - timedelta(days=34)

        eight_day_plus_sessions = list(c for c in all_training_sessions if c.event_date <= eight_days_ago)

        self.last_5_days_training_sessions = list(c for c in all_training_sessions if c.event_date >= five_days_ago)
        self.last_20_days_training_sessions = list(c for c in all_training_sessions if c.event_date >= twenty_days_ago)

        if len(eight_day_plus_sessions) > 0:
            self.training_sessions_exist_days_8_35 = True

        last_14_day_sessions = list(c for c in all_training_sessions if c.event_date > fourteen_days_ago)
        previous_7_day_training_sessions = list(c for c in all_training_sessions if eight_days_ago >= c.event_date > fourteen_days_ago)
        previous_14_day_training_sessions = list(
            c for c in all_training_sessions if fourteen_days_ago >= c.event_date > twenty_one_days_ago)
        previous_21_day_training_sessions = list(
            c for c in all_training_sessions if twenty_one_days_ago >= c.event_date > twenty_eight_days_ago)
        previous_28_day_training_sessions = list(
            c for c in all_training_sessions if twenty_eight_days_ago >= c.event_date > thirty_five_days_ago)

        last_7_day_training_sessions = list(c for c in all_training_sessions if c.event_date > eight_days_ago)

        self.last_14_days_training_sessions = last_14_day_sessions

        self.load_stats.set_min_max_values(previous_7_day_training_sessions)
        self.load_stats.set_min_max_values(last_7_day_training_sessions)

        self.adaptation_type_load[AdaptationType.not_tracked.value] = self.load_stats.max_not_tracked if self.load_stats.max_not_tracked is not None else 0
        self.adaptation_type_load[AdaptationType.strength_endurance_cardiorespiratory.value] = self.load_stats.max_strength_endurance_cardiorespiratory if self.load_stats.max_strength_endurance_cardiorespiratory is not None else 0
        self.adaptation_type_load[AdaptationType.strength_endurance_strength.value] = self.load_stats.max_strength_endurance_strength if self.load_stats.max_strength_endurance_strength is not None else 0
        self.adaptation_type_load[AdaptationType.power_drill.value] = self.load_stats.max_power_drill if self.load_stats.max_power_drill is not None else 0
        self.adaptation_type_load[AdaptationType.maximal_strength_hypertrophic.value] = self.load_stats.max_maximal_strength_hypertrophic if self.load_stats.max_maximal_strength_hypertrophic is not None else 0
        self.adaptation_type_load[AdaptationType.power_explosive_action.value] = self.load_stats.max_power_explosive_action if self.load_stats.max_power_explosive_action is not None else 0

        for p in previous_7_day_training_sessions:

            if p.session_type() == SessionType.sport_training:
                if p.sport_name not in self.previous_week_sport_training_loads:
                    self.last_week_sport_training_loads[p.sport_name] = []
                    self.previous_week_sport_training_loads[p.sport_name] = []
                training_load = p.training_load(self.load_stats)
                if training_load is not None and training_load.observed_value is not None and training_load.observed_value > 0:
                    self.previous_week_sport_training_loads[p.sport_name].append(training_load.observed_value)
                    if p.sport_name.value in self.sport_max_load:
                        if training_load.observed_value > self.sport_max_load[p.sport_name.value].load:
                            self.sport_max_load[p.sport_name.value].load = training_load.observed_value
                            self.sport_max_load[p.sport_name.value].event_date_time = p.event_date
                            self.sport_max_load[p.sport_name.value].first_time_logged = False
                    else:
                        self.sport_max_load[p.sport_name.value] = SportMaxLoad(p.event_date, training_load.observed_value)
                        self.sport_max_load[p.sport_name.value].first_time_logged = True

        for l in last_7_day_training_sessions:

            if l.session_type() == SessionType.sport_training:
                if l.sport_name not in self.last_week_sport_training_loads:
                    self.last_week_sport_training_loads[l.sport_name] = []
                    self.previous_week_sport_training_loads[l.sport_name] = []
                training_load = l.training_load(self.load_stats)
                if training_load is not None and training_load.observed_value is not None and training_load.observed_value > 0:
                    self.last_week_sport_training_loads[l.sport_name].append(training_load.observed_value)
                    if l.sport_name.value in self.sport_max_load:
                        if training_load.observed_value > self.sport_max_load[l.sport_name.value].load:
                            self.sport_max_load[l.sport_name.value].load = training_load.observed_value
                            self.sport_max_load[l.sport_name.value].event_date_time = l.event_date
                            self.sport_max_load[l.sport_name.value].first_time_logged = False
                    else:
                        self.sport_max_load[l.sport_name.value] = SportMaxLoad(l.event_date, training_load.observed_value)
                        self.sport_max_load[l.sport_name.value].first_time_logged = True

        self.last_week_internal_values.extend(
            x.rpe_load for x in last_7_day_training_sessions if x.rpe_load is not None)
        self.last_week_power_load_values.extend(
            x.power_load for x in last_7_day_training_sessions if x.power_load is not None)

        self.previous_week_internal_values.extend(
            x.rpe_load for x in previous_7_day_training_sessions if x.rpe_load is not None)
        self.previous_week_power_load_values.extend(
            x.power_load for x in previous_7_day_training_sessions if x.power_load is not None)

        self.previous_week_2_internal_values.extend(
            x.rpe_load for x in previous_14_day_training_sessions if x.rpe_load is not None)
        self.previous_week_2_power_load_values.extend(
            x.power_load for x in previous_14_day_training_sessions if x.power_load is not None)

        self.previous_week_3_internal_values.extend(
            x.rpe_load for x in previous_21_day_training_sessions if x.rpe_load is not None)
        self.previous_week_3_power_load_values.extend(
            x.power_load for x in previous_21_day_training_sessions if x.power_load is not None)

        self.previous_week_4_internal_values.extend(
            x.rpe_load for x in previous_28_day_training_sessions if x.rpe_load is not None)
        self.previous_week_4_power_load_values.extend(
            x.power_load for x in previous_28_day_training_sessions if x.power_load is not None)

        self.a_internal_load_values.extend(x.rpe_load for x in acute_training_sessions if x.rpe_load is not None)
        self.a_power_load_values.extend(x.power_load for x in acute_training_sessions if x.power_load is not None)

        for w in chronic_weeks_training_sessions:
            internal_weeks_values = [x.rpe_load for x in w if x.rpe_load is not None]
            power_load_weeks_values = [x.power_load for x in w if x.power_load is not None]
            internal_week_sum = self.get_standard_error_range(expected_workouts_week=self.expected_weekly_workouts,
                                                            values=internal_weeks_values,
                                                            return_sum=True)
            power_load_week_sum = self.get_standard_error_range(expected_workouts_week=self.expected_weekly_workouts,
                                                              values=power_load_weeks_values,
                                                              return_sum=True)
            self.c_internal_load_values.append(internal_week_sum)
            self.c_power_load_values.append(power_load_week_sum)

        self.internal_load_tuples.extend(list(x for x in self.get_session_attributes_tuple_list("event_date",
                                                                                                 "rpe_load",
                                                                                                all_training_sessions)))
        self.power_load_tuples.extend(list(x for x in self.get_session_attributes_tuple_list("event_date",
                                                                                                "power_load",
                                                                                                all_training_sessions)))

        proc = AthleteCapacityProcessor()

        self.athlete_capacities = proc.get_capacity_from_workout_history(all_training_sessions)
        self.total_historical_sessions = len(all_training_sessions)

        # if len(self.internal_load_tuples) > 0:
        #     internal_load_values = list(x[1] for x in self.internal_load_tuples if x[1] is not None)
        #     high_internal = max(internal_load_values)
        #     low_internal = min(internal_load_values)
        #     range = (high_internal - low_internal) / 3
        #     self.low_internal_load_day_lower_bound = low_internal
        #     self.low_internal_load_day_upper_bound = low_internal + range
        #     self.mod_internal_load_day_upper_bound = high_internal - range
        #     self.high_internal_load_day_upper_bound = high_internal

    @xray_recorder.capture('logic.TrainingLoadProcessing.calc_training_load_metrics')
    def calc_training_load_metrics(self, user_stats):

        user_stats.training_load_ramp = {}

        for sport_name, load in self.previous_week_sport_training_loads.items():
            user_stats.training_load_ramp[sport_name] = self.get_ramp(user_stats.expected_weekly_workouts,
                                                                      self.last_week_sport_training_loads[
                                                                             sport_name],
                                                                      self.previous_week_sport_training_loads[
                                                                             sport_name]
                                                                      )

        if user_stats.eligible_for_high_load_trigger:
            self.set_high_relative_load_sessions(user_stats, self.last_14_days_training_sessions)
        else:
            if self.training_sessions_exist_days_8_35:
                eligible_for_high_load_trigger = False

                if user_stats.expected_weekly_workouts is None or user_stats.expected_weekly_workouts <= 1:
                    if len(self.last_14_days_training_sessions) > 1:
                        eligible_for_high_load_trigger = True
                elif 1 < user_stats.expected_weekly_workouts <= 4:
                    if len(self.last_14_days_training_sessions) > 2:
                        eligible_for_high_load_trigger = True
                elif user_stats.expected_weekly_workouts > 4:
                    if len(self.last_14_days_training_sessions) > 4:
                        eligible_for_high_load_trigger = True

                if eligible_for_high_load_trigger:
                    user_stats.eligible_for_high_load_trigger = True
                    self.set_high_relative_load_sessions(user_stats, self.last_14_days_training_sessions)
                else:
                    user_stats.eligible_for_high_load_trigger = False

        user_stats.internal_ramp = self.get_ramp(user_stats.expected_weekly_workouts,
                                                 self.last_week_internal_values, self.previous_week_internal_values)
        user_stats.power_load_ramp = self.get_ramp(user_stats.expected_weekly_workouts,
                                                   self.last_week_power_load_values, self.previous_week_power_load_values)

        user_stats.internal_monotony = self.get_monotony(user_stats.expected_weekly_workouts,
                                                         self.last_week_internal_values)

        user_stats.power_load_monotony = self.get_monotony(user_stats.expected_weekly_workouts,
                                                           self.last_week_power_load_values)

        historical_internal_monotony = self.get_historical_monotony(self.start_date, self.end_date,
                                                                    user_stats.expected_weekly_workouts,
                                                                    self.internal_load_tuples)

        historical_power_load_monotony = self.get_historical_monotony(self.start_date, self.end_date,
                                                                      user_stats.expected_weekly_workouts,
                                                                      self.power_load_tuples)

        user_stats.historical_internal_monotony = historical_internal_monotony
        user_stats.historical_power_load_monotony = historical_power_load_monotony

        historical_internal_strain, strain_events = self.get_historical_strain(self.start_date, self.end_date,
                                                                               user_stats.expected_weekly_workouts,
                                                                               self.internal_load_tuples)
        historical_power_load_strain, power_strain_events = self.get_historical_strain(self.start_date, self.end_date,
                                                                                       user_stats.expected_weekly_workouts,
                                                                                       self.power_load_tuples)

        user_stats.internal_strain_events = strain_events
        user_stats.power_load_strain_events = power_strain_events

        user_stats.internal_strain = self.get_strain(user_stats.expected_weekly_workouts,
                                                     user_stats.internal_monotony, self.last_week_internal_values,
                                                     historical_internal_strain)
        user_stats.power_load_strain = self.get_strain(user_stats.expected_weekly_workouts,
                                                       user_stats.power_load_monotony, self.last_week_power_load_values,
                                                       historical_power_load_strain)

        user_stats.acute_internal_total_load = self.get_standard_error_range(user_stats.expected_weekly_workouts,
                                                                             self.a_internal_load_values)
        user_stats.acute_power_total_load = self.get_standard_error_range(user_stats.expected_weekly_workouts,
                                                                          self.a_power_load_values)

        # user_stats.chronic_internal_total_load = self.get_standard_error_range(
        #     user_stats.expected_weekly_workouts, self.c_internal_load_values, return_sum=False)

        # already factored in expected weekly workouts
        user_stats.chronic_internal_total_load = StandardErrorRange.get_average_from_error_range_list(
            self.c_internal_load_values)
        user_stats.chronic_power_total_load = StandardErrorRange.get_average_from_error_range_list(
            self.c_power_load_values)

        acute_internal_load = user_stats.acute_internal_total_load.plagiarize()
        acute_internal_load.divide_range(user_stats.chronic_internal_total_load)

        user_stats.internal_acwr = acute_internal_load.plagiarize()

        acute_power_load = user_stats.acute_power_total_load.plagiarize()
        acute_power_load.divide_range(user_stats.chronic_power_total_load)

        user_stats.power_load_acwr = acute_power_load.plagiarize()

        user_stats.internal_freshness_index = self.get_freshness_index(
            user_stats.acute_internal_total_load,
            user_stats.chronic_internal_total_load)
        user_stats.power_load_freshness_index = self.get_freshness_index(
            user_stats.acute_power_total_load,
            user_stats.chronic_power_total_load)

        user_stats.historical_internal_strain = historical_internal_strain
        user_stats.historical_power_load_strain = historical_power_load_strain

        user_stats.average_weekly_internal_load = self.get_average_weekly_internal_load()

        user_stats.athlete_capacities = self.athlete_capacities  # calculated when loading values

        return user_stats

    def get_average_weekly_internal_load(self):

        internal_load_values = []
        if len(self.last_week_internal_values) > 0:
            #internal_load_values.append(StandardErrorRange.get_sum_from_error_range_list(self.last_week_internal_values))
            internal_load_values.append(
                self.get_standard_error_range(self.expected_weekly_workouts, self.last_week_internal_values, return_sum=True))
        if len(self.previous_week_internal_values) > 0:
            #internal_load_values.append(StandardErrorRange.get_sum_from_error_range_list(self.previous_week_internal_values))
            internal_load_values.append(
                self.get_standard_error_range(self.expected_weekly_workouts, self.previous_week_internal_values,
                                              return_sum=True))
        if len(self.previous_week_2_internal_values) > 0:
            #internal_load_values.append(StandardErrorRange.get_sum_from_error_range_list(self.previous_week_2_internal_values))
            internal_load_values.append(
                self.get_standard_error_range(self.expected_weekly_workouts, self.previous_week_2_internal_values,
                                              return_sum=True))
        if len(self.previous_week_3_internal_values) > 0:
            #internal_load_values.append(StandardErrorRange.get_sum_from_error_range_list(self.previous_week_3_internal_values))
            internal_load_values.append(
                self.get_standard_error_range(self.expected_weekly_workouts, self.previous_week_3_internal_values,
                                              return_sum=True))
        if len(self.previous_week_4_internal_values) > 0:
            #internal_load_values.append(StandardErrorRange.get_sum_from_error_range_list(self.previous_week_4_internal_values))
            internal_load_values.append(
                self.get_standard_error_range(self.expected_weekly_workouts, self.previous_week_4_internal_values,
                                              return_sum=True))

        if len(internal_load_values) == 1:
            return StandardErrorRange.get_sum_from_error_range_list(internal_load_values)
        elif len(internal_load_values) > 1:
            return StandardErrorRange.get_average_from_error_range_list(internal_load_values)
        else:
            return StandardErrorRange(lower_bound=0, observed_value=0, upper_bound=0)

    def set_high_relative_load_sessions(self, user_stats, training_sessions):

        for t in training_sessions:
            if t.session_type() == SessionType.sport_training:
                if t.sport_name in user_stats.training_load_ramp:
                    if (user_stats.training_load_ramp[t.sport_name].observed_value is None or
                            user_stats.training_load_ramp[t.sport_name].observed_value > 1.1):
                        if t.session_RPE is not None and t.session_RPE > 4:
                            high_load_session = HighLoadSession(t.event_date, t.sport_name)
                            high_load_session.percent_of_max = self.get_max_training_percent(t)
                            self.high_relative_load_sessions.append(high_load_session)
                else:
                    if t.session_RPE is not None and t.session_RPE > 4:
                        high_load_session = HighLoadSession(t.event_date, t.sport_name)
                        high_load_session.percent_of_max = self.get_max_training_percent(t)
                        self.high_relative_load_sessions.append(high_load_session)
            elif t.session_type() == SessionType.mixed_activity:

                max_percent = 0
                greater_than_50 = []

                percent = self.get_percent(t.not_tracked_load, self.adaptation_type_load[AdaptationType.not_tracked.value])
                if percent > 80:
                    max_percent = percent
                if percent > 50:
                    greater_than_50.append(percent)

                percent = self.get_percent(t.strength_endurance_cardiorespiratory_load,
                                             self.adaptation_type_load[AdaptationType.strength_endurance_cardiorespiratory.value])
                if percent > 80 and percent > max_percent:
                    max_percent = percent

                if percent > 50:
                    greater_than_50.append(percent)

                percent = self.get_percent(t.strength_endurance_strength_load,
                                               self.adaptation_type_load[
                                                   AdaptationType.strength_endurance_strength.value])
                if percent > 50:
                    greater_than_50.append(percent)

                if percent > 80 and percent > max_percent:
                    max_percent = percent

                percent = self.get_percent(t.power_drill_load, self.adaptation_type_load[AdaptationType.power_drill.value])
                if percent > 80 and percent > max_percent:
                    max_percent = percent

                if percent > 50:
                    greater_than_50.append(percent)

                percent = self.get_percent(t.maximal_strength_hypertrophic_load,
                                                 self.adaptation_type_load[AdaptationType.maximal_strength_hypertrophic.value])
                if percent > 80 and percent > max_percent:
                    max_percent = percent

                if percent > 50:
                    greater_than_50.append(percent)

                percent = self.get_percent(t.power_explosive_action_load,self.adaptation_type_load[AdaptationType.power_explosive_action.value])

                if percent > 80 and percent > max_percent:
                    max_percent = percent

                if percent > 50:
                    greater_than_50.append(percent)

                if max_percent > 80:
                    high_load_session = HighDetailedLoadSession(t.event_date)
                    high_load_session.percent_of_max = max_percent
                    self.high_relative_load_sessions.append(high_load_session)

                else:
                    if len(greater_than_50) >= 2:
                        high_load_session = HighDetailedLoadSession(t.event_date)
                        high_load_session.percent_of_max = max(greater_than_50)
                        self.high_relative_load_sessions.append(high_load_session)

        average_5_day_tissue_load_list = [f.tissue_load for f in self.last_5_days_training_sessions if
                                          f.tissue_load is not None]
        if len(average_5_day_tissue_load_list) > 0:
            self.average_tissue_load_5_day = self.get_average_for_error_ranges(average_5_day_tissue_load_list,
                                                                               0.714 * self.expected_weekly_workouts)  # adjusted expected weekly workouts by 5/7 of value

        average_20_day_tissue_load_list = [f.tissue_load for f in self.last_20_days_training_sessions if
                                           f.tissue_load is not None]
        if len(average_20_day_tissue_load_list) > 0:
            self.average_tissue_load_20_day = self.get_average_for_error_ranges(average_20_day_tissue_load_list,
                                                                                0.95 * (
                                                                                            self.expected_weekly_workouts * 3))  # adjusted expected weekly workouts by 20/21 of value

        average_5_day_power_load_list = [f.power_load for f in self.last_5_days_training_sessions if
                                         f.power_load is not None]
        if len(average_5_day_power_load_list) > 0:
            self.average_power_load_5_day = self.get_average_for_error_ranges(average_5_day_power_load_list,
                                                                              0.714 * self.expected_weekly_workouts)  # adjusted expected weekly workouts by 5/7 of value

        average_20_day_power_load_list = [f.power_load for f in self.last_20_days_training_sessions if
                                          f.power_load is not None]
        if len(average_20_day_power_load_list) > 0:
            self.average_power_load_20_day = self.get_average_for_error_ranges(average_20_day_power_load_list,
                                                                               0.95 * (
                                                                                           self.expected_weekly_workouts * 3))  # adjusted expected weekly workouts by 20/21 of value
        tissue_load_5_20_lowest_value = 0.0
        power_load_5_20_lowest_value = 0.0

        tissue_load_5_20 = self.tissue_load_5_20()
        if tissue_load_5_20 is not None:
            tissue_load_5_20_lowest_value = tissue_load_5_20.lowest_value()
        power_load_5_20 = self.power_load_5_20()
        if power_load_5_20 is not None:
            power_load_5_20_lowest_value = power_load_5_20.lowest_value()

        tissue_load_percent = 50
        power_load_percent = 50

        if tissue_load_5_20_lowest_value is not None and tissue_load_5_20_lowest_value > 1.1:
            tissue_load_percent = min(100, ((tissue_load_5_20_lowest_value - 1.1) * 100) + 50)

        if power_load_5_20_lowest_value is not None and power_load_5_20_lowest_value > 1.1:
            power_load_percent = min(100, ((power_load_5_20_lowest_value - 1.1) * 100) + 50)

        self.high_relative_load_score = max(tissue_load_percent, power_load_percent)

    # def get_average_error_range(self, atrribute_name, session_list):
    #
    #     error_range_values = [getattr(s, atrribute_name) for s in session_list]
    def get_session_attributes_tuple_list(self, attribute_1_name, attribute_2_name, training_sessions):

        values = []

        for training_session in training_sessions:

            values.append((getattr(training_session, attribute_1_name), getattr(training_session, attribute_2_name)))

        return values

    def get_percent(self, test_value, base_value):

            if test_value is not None:
                # TODO: using only observed_value
                if isinstance(test_value, StandardErrorRange):
                    test_value = test_value.observed_value
                    if test_value is None:
                        return 0
                if base_value is None:
                    return 100
                if test_value > base_value:
                    return 100

                if base_value > 0:
                    ratio = test_value / base_value
                    return ratio * 100

            return 0

    def get_ramp(self, expected_weekly_workouts, last_week_values, previous_week_values, factor=1.1):

        current_load = self.get_standard_error_range(expected_weekly_workouts, last_week_values)
        previous_load = self.get_standard_error_range(expected_weekly_workouts, previous_week_values)

        #ramp_error_range = StandardErrorRangeMetric() this is for later
        ramp_error_range = StandardErrorRange()

        if current_load.insufficient_data or previous_load.insufficient_data:
            ramp_error_range.insufficient_data = True

        ramp_values = []
        # ignore all cases of lower_bound since we know the load could not be lower than observed
        # the following commenting out was for clarity and should be preserved

        ramp_values = self.get_ramp_value(ramp_values, current_load.observed_value, previous_load.upper_bound)
        ramp_values = self.get_ramp_value(ramp_values, current_load.upper_bound, previous_load.observed_value)
        ramp_values = self.get_ramp_value(ramp_values, current_load.upper_bound, previous_load.upper_bound)

        if (current_load.observed_value is not None and previous_load.observed_value is not None
                and previous_load.observed_value > 0):
            ramp_error_range.observed_value = current_load.observed_value / float(previous_load.observed_value)

        if len(ramp_values) > 0:
            min_value = min(ramp_values)
            max_value = max(ramp_values)
            if (ramp_error_range.observed_value is None or (ramp_error_range.observed_value is not None and
                                                            min_value < ramp_error_range.observed_value)):
                ramp_error_range.lower_bound = min_value

            if (ramp_error_range.observed_value is None or (ramp_error_range.observed_value is not None and
                                                            max_value > ramp_error_range.observed_value)):
                ramp_error_range.upper_bound = max_value

        return ramp_error_range

    def get_ramp_value(self, values, current_load_value, previous_load_value):

        if (current_load_value is not None and previous_load_value is not None
                and previous_load_value > 0):
            values.append(current_load_value/float(previous_load_value))

        return values

    def get_acwr(self, acute_load_error, chronic_load_error, factor=1.3):

        standard_error_range = StandardErrorRange()

        if acute_load_error.insufficient_data or chronic_load_error.insufficient_data:
            standard_error_range.insufficient_data = True

        if acute_load_error.observed_value is not None and chronic_load_error.observed_value is not None:
            if chronic_load_error.observed_value > 0:
                standard_error_range.observed_value = (acute_load_error.observed_value /
                                                       chronic_load_error.observed_value)
                #not doing this now
                #standard_error_range.observed_value_gap = (factor * chronic_load_error.observed_value) - acute_load_error.observed_value

        acwr_values = []
        acwr_values = self.get_acwr_value(acwr_values, acute_load_error.observed_value, chronic_load_error.upper_bound)
        acwr_values = self.get_acwr_value(acwr_values, acute_load_error.upper_bound, chronic_load_error.observed_value)
        acwr_values = self.get_acwr_value(acwr_values, acute_load_error.upper_bound, chronic_load_error.upper_bound)

        if len(acwr_values) > 0:
            min_value = min(acwr_values)
            max_value = max(acwr_values)
            if (standard_error_range.observed_value is not None
                    and (min_value < standard_error_range.observed_value)):
                standard_error_range.lower_bound = min_value
            if (standard_error_range.observed_value is not None
                    and (max_value > standard_error_range.observed_value)):
                standard_error_range.upper_bound = max_value
            if standard_error_range.observed_value is None:
                standard_error_range.lower_bound = min_value
                standard_error_range.upper_bound = max_value

        '''not doing this now
        gap_values = []
        # ignore all cases of lower_bound since we know the load could not be lower than observed
        # the following commenting out was for clarity and should be preserved
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.lower_bound, chronic_load_error.lower_bound, factor)
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.lower_bound, chronic_load_error.observed_value, factor)
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.lower_bound, chronic_load_error.upper_bound, factor)
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.observed_value, chronic_load_error.lower_bound, factor)
        gap_values = self.get_acwr_gap(gap_values, acute_load_error.observed_value, chronic_load_error.upper_bound, factor)
        #gap_values = self.get_acwr_gap(gap_values, acute_load_error.upper_bound, chronic_load_error.lower_bound, factor)
        gap_values = self.get_acwr_gap(gap_values, acute_load_error.upper_bound, chronic_load_error.observed_value, factor)
        gap_values = self.get_acwr_gap(gap_values, acute_load_error.upper_bound, chronic_load_error.upper_bound, factor)

        if len(gap_values) > 0:
            min_acwr = min(gap_values)
            max_acwr = max(gap_values)
            if (standard_error_range.observed_value_gap is not None
                    and (min_acwr < standard_error_range.observed_value_gap)):
                standard_error_range.lower_bound_gap = min_acwr
            if (standard_error_range.observed_value_gap is not None
                    and (max_acwr > standard_error_range.observed_value_gap)):
                standard_error_range.upper_bound_gap = max_acwr
            if standard_error_range.observed_value_gap is None:
                standard_error_range.lower_bound_gap = min_acwr
                standard_error_range.upper_bound_gap = max_acwr

        '''
        return standard_error_range

    def get_acwr_value(self, acwr_values, acute_load_value, chronic_load_value):

        if acute_load_value is not None and chronic_load_value is not None:
            if chronic_load_value > 0:
                acwr_values.append(acute_load_value/float(chronic_load_value))

        return acwr_values

    def get_freshness_index(self, acute_load_error, chronic_load_error):

        standard_error_range = StandardErrorRange()

        if acute_load_error.insufficient_data or chronic_load_error.insufficient_data:
            standard_error_range.insufficient_data = True

        if acute_load_error.observed_value is not None and chronic_load_error.observed_value is not None:
            if chronic_load_error.observed_value > 0:
                standard_error_range.observed_value = (chronic_load_error.observed_value -
                                                       acute_load_error.observed_value)

        fresh_values = []

        if acute_load_error.observed_value is not None and chronic_load_error.upper_bound is not None:
            if chronic_load_error.upper_bound > 0:
                fresh_values.append(chronic_load_error.upper_bound - acute_load_error.observed_value)
        if acute_load_error.upper_bound is not None and chronic_load_error.upper_bound is not None:
            if chronic_load_error.upper_bound > 0:
                fresh_values.append(chronic_load_error.upper_bound - acute_load_error.upper_bound)
        if acute_load_error.upper_bound is not None and chronic_load_error.observed_value is not None:
            if chronic_load_error.observed_value > 0:
                fresh_values.append(chronic_load_error.observed_value - acute_load_error.upper_bound)

        if len(fresh_values) > 0:
            min_fresh = min(fresh_values)
            max_fresh = max(fresh_values)
            if (standard_error_range.observed_value is not None
                    and (min_fresh < standard_error_range.observed_value)):
                standard_error_range.lower_bound = min_fresh
            if (standard_error_range.observed_value is not None
                    and (max_fresh > standard_error_range.observed_value)):
                standard_error_range.upper_bound = max_fresh
            if standard_error_range.observed_value is None:
                standard_error_range.lower_bound = min_fresh
                standard_error_range.upper_bound = max_fresh

        return standard_error_range


    def get_max_training_percent(self, training_session):

        percent = None

        if self.load_stats is not None and self.sport_max_load is not None:
            training_volume = training_session.training_load(self.load_stats)
            if training_volume is not None and training_volume.observed_value > 0:
                training_volume_value = round(training_volume.observed_value, 2)

                if training_session.sport_name.value in self.sport_max_load:

                    percent = int(round((training_volume_value / self.sport_max_load[training_session.sport_name.value].load) * 100, 0))

        return percent

    def get_average_for_error_ranges(self, error_range_list, expected_weekly_workouts):

        lower_adjustments = 0
        upper_adjustments = 0
        for e in error_range_list:
            if e.lower_bound is None and e.observed_value is not None:
                e.lower_bound = e.observed_value
                lower_adjustments += 1
            if e.upper_bound is None and e.observed_value is not None:
                e.upper_bound = e.observed_value
                upper_adjustments += 1

        if lower_adjustments == upper_adjustments and lower_adjustments == len(error_range_list): # just use observed values
            observed_value_list = [e.observed_value for e in error_range_list if e.observed_value is not None]
            upper_bound_list = []
            lower_bound_list = []
        else:
            observed_value_list = [e.observed_value for e in error_range_list if e.observed_value is not None]
            upper_bound_list = [e.upper_bound for e in error_range_list if e.upper_bound is not None]
            lower_bound_list = [e.lower_bound for e in error_range_list if e.lower_bound is not None]

        average_range = StandardErrorRange()

        if len(observed_value_list) > 0:
            average_range = self.get_standard_error_range(expected_weekly_workouts, observed_value_list, return_sum=False)

        if len(upper_bound_list) > 0:
            upper_bound_value_range = self.get_standard_error_range(expected_weekly_workouts, upper_bound_list, return_sum=False)
            if average_range.upper_bound is not None and upper_bound_value_range.upper_bound is not None:
                average_range.upper_bound = max(average_range.upper_bound, upper_bound_value_range.upper_bound)
            elif average_range.upper_bound is None and upper_bound_value_range.upper_bound is not None:
                average_range.upper_bound = upper_bound_value_range.upper_bound

        if len(lower_bound_list) > 0:
            lower_bound_value_range = self.get_standard_error_range(expected_weekly_workouts, lower_bound_list, return_sum=False)
            if average_range.lower_bound is not None and lower_bound_value_range.lower_bound is not None:
                average_range.lower_bound = min(average_range.upper_bound, lower_bound_value_range.lower_bound)
            elif average_range.lower_bound is None and lower_bound_value_range.lower_bound is not None:
                average_range.lower_bound = lower_bound_value_range.lower_bound

        return average_range

    def get_standard_error_range(self, expected_workouts_week, values, return_sum=True):

        standard_error_range = StandardErrorRange()

        expected_workouts = 5

        if expected_workouts_week is not None:
            expected_workouts = expected_workouts_week

        if len(values) > 0:
            if return_sum:
                if isinstance(values[0], StandardErrorRange):
                    standard_error_range.observed_value = StandardErrorRange.get_sum_from_error_range_list(
                        values).highest_value()
                else:
                    standard_error_range.observed_value = sum(values)

            else:
                if isinstance(values[0], StandardErrorRange):
                    standard_error_range.observed_value = StandardErrorRange.get_average_from_error_range_list(
                        values).highest_value()
                else:
                    standard_error_range.observed_value = statistics.mean(values)

        if 1 < len(values) < expected_workouts:
            if isinstance(values[0], StandardErrorRange):
                average_value = StandardErrorRange.get_average_from_error_range_list(values)
                average_observed_value = average_value.highest_value()
                observed_values = [l.highest_value() for l in values]
            else:
                average_observed_value = statistics.mean(values)
                observed_values = [l for l in values]

            stdev = statistics.stdev(observed_values)
            standard_error = (stdev / math.sqrt(len(values))) * math.sqrt(
                (expected_workouts - len(values)) / expected_workouts)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            if return_sum:
                standard_error_range.upper_bound = (average_observed_value + standard_error_range_factor) * len(values)
                standard_error_range.lower_bound = (average_observed_value - standard_error_range_factor) * len(values)
            else:
                standard_error_range.upper_bound = (average_observed_value + standard_error_range_factor)
                standard_error_range.lower_bound = (average_observed_value - standard_error_range_factor)
        elif 1 == len(values) < expected_workouts:
            #let'a quick manufacture some data
            fake_values = []
            fake_values.extend(values)
            if isinstance(values[0], StandardErrorRange):
                fake_range = values[0].plagiarize()
                fake_range.multiply(1.5)
                fake_values.append(fake_range)
                average_value = StandardErrorRange.get_average_from_error_range_list(fake_values)
                average_observed_value = average_value.highest_value()

                observed_values = [l.highest_value() for l in fake_values]
            else:
                fake_values.append(values[0]*1.5)
                average_observed_value = statistics.mean(fake_values)
                observed_values = [l for l in fake_values]

            stdev = statistics.stdev(observed_values)
            standard_error = (stdev / math.sqrt(len(observed_values))) * math.sqrt(
                (expected_workouts - len(observed_values)) / expected_workouts)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            if return_sum:
                standard_error_range.upper_bound = (average_observed_value + standard_error_range_factor) * len(observed_values)
                standard_error_range.lower_bound = (average_observed_value - standard_error_range_factor) * len(observed_values)
            else:
                standard_error_range.upper_bound = (average_observed_value + standard_error_range_factor)
                standard_error_range.lower_bound = (average_observed_value - standard_error_range_factor)

        elif len(values) == 0:
            standard_error_range.insufficient_data = True

        return standard_error_range

    # TODO this won't work as it expects singular values and the parm is standard error ranges
    def get_monotony(self, expected_weekly_workouts, values):

        standard_error_range = StandardErrorRange()

        if len(values) > 1:

            average_load = self.get_standard_error_range(expected_weekly_workouts, values, return_sum=False)

            numeric_values = [n.highest_value() for n in values]

            stdev_load = statistics.stdev(numeric_values)

            if stdev_load > 0:

                if average_load.observed_value is not None:
                    standard_error_range.observed_value = average_load.observed_value / stdev_load

                if average_load.upper_bound is not None:
                    standard_error_range.upper_bound = average_load.upper_bound / stdev_load

                # ignore all cases of lower_bound since we know the load could not be lower than observed
                # the following commenting out was for clarity and should be preserved
                #if average_load.lower_bound is not None:
                #    standard_error_range.lower_bound = average_load.lower_bound / stdev_load

            '''ignoring monotony gaps as they structured differntly
            low_gaps = []
            high_gaps = []
            m3, m4 = self.get_monotony_gaps(average_load.observed_value, stdev_load)
            low_gaps.append(m3)
            high_gaps.append(m4)
            m5, m6 = self.get_monotony_gaps(average_load.upper_bound, stdev_load)
            low_gaps.append(m5)
            high_gaps.append(m6)

            low_gap = self.get_lower_training_volume_gap(TrainingVolumeGapType.monotony,
                                                         list(x for x in low_gaps if x is not None))
            high_gap = self.get_lower_training_volume_gap(TrainingVolumeGapType.monotony,
                                                          list(x for x in high_gaps if x is not None))

            if low_gap is not None:
                standard_error_range.training_volume_gaps.append(low_gap)

            if high_gap is not None:
                standard_error_range.training_volume_gaps.append(high_gap)
            '''
        else:
            standard_error_range.insufficient_data = True

        return standard_error_range

    def get_historical_monotony(self, start_date, end_date, expected_weekly_workouts, load_tuples):

        target_dates = []

        weekly_expected_workouts = 5

        if expected_weekly_workouts is not None:
            weekly_expected_workouts = expected_weekly_workouts

        load_tuples.sort(key=lambda x: x[0])

        date_diff = parse_date(end_date) - parse_date(start_date)

        for i in range(1, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        index = 0
        monotony_values = []

        # evaluates a rolling week's worth of values for each day
        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_values = [p for p in load_tuples if (parse_date(start_date) + timedelta(index)) < p[0] <= target_dates[t]]
                load_values.extend(x[1] for x in daily_values if x is not None and x[1] is not None)
                monotony = self.get_monotony(weekly_expected_workouts, load_values)

                if monotony.observed_value is not None or monotony.upper_bound is not None:
                    monotony_values.append(monotony)
                index += 1

        return monotony_values

    def get_historical_strain(self, start_date, end_date, expected_weekly_workouts, load_tuples):

        target_dates = []

        weekly_expected_workouts = 5

        if expected_weekly_workouts is not None:
            weekly_expected_workouts = expected_weekly_workouts

        load_tuples.sort(key=lambda x: x[0])

        date_diff = parse_date(end_date) - parse_date(start_date) + timedelta(days=1)  # include all days within start/end

        for i in range(0, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        index = 0
        strain_values = []
        strain_events = StandardErrorRange()

        # evaluates a rolling week's worth of values for each day to calculate "daily" strain
        avg_observed = None
        stdev_observed = None
        avg_upper = None
        stdev_upper = None
        obs_events = 0
        up_events = 0

        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_values = [p for p in load_tuples if (parse_date(start_date) + timedelta(index)) <= p[0] <= target_dates[t]]
                load_values.extend(x[1] for x in daily_values if x is not None and x[1] is not None)
                strain = self.calculate_daily_strain(load_values, weekly_expected_workouts)

                if strain.observed_value is not None or strain.upper_bound is not None:
                    strain_values.append(strain)

                    if len(strain_values) > 1:
                        observed_values = list(o.observed_value for o in strain_values if o.observed_value is not None)
                        upper_values = list(o.upper_bound for o in strain_values if o.upper_bound is not None)

                        if 1 < len(observed_values):
                            if stdev_observed is not None and avg_observed is not None and strain.observed_value is not None:
                                if strain.observed_value >= ((1.2 * stdev_observed) + avg_observed):
                                    obs_events += 1
                            avg_observed = statistics.mean(observed_values)
                            stdev_observed = statistics.stdev(observed_values)

                            strain_events.observed_value = obs_events

                        if 1 < len(upper_values):
                            if stdev_upper is not None and avg_upper is not None and strain.upper_bound is not None:
                                if strain.upper_bound >= ((1.2 * stdev_upper) + avg_upper):
                                    up_events += 1
                            avg_upper = statistics.mean(upper_values)
                            stdev_upper = statistics.stdev(upper_values)

                            strain_events.upper_bound = up_events
                index += 1

        return strain_values, strain_events

    def calculate_daily_strain(self, load_values, expected_weekly_workouts):

        daily_strain = StandardErrorRange()

        weekly_expected_workouts = 5

        if expected_weekly_workouts is not None:
            weekly_expected_workouts = expected_weekly_workouts

        if len(load_values) > 1:

            current_load = StandardErrorRange.get_sum_from_error_range_list(load_values)

            numeric_load_values = [n.highest_value() for n in load_values]

            average_load = statistics.mean(numeric_load_values)
            stdev_load = statistics.stdev(numeric_load_values)
            stdev_load = max(stdev_load, 0.1)

            monotony = average_load / stdev_load
            daily_strain.observed_value = monotony * current_load.highest_value()

            if len(numeric_load_values) < weekly_expected_workouts:
                standard_error = (stdev_load / math.sqrt(len(numeric_load_values))) * math.sqrt(
                    (weekly_expected_workouts - len(numeric_load_values)) / weekly_expected_workouts)  # adjusts for finite population correction
                standard_error_range_factor = 1.96 * standard_error

                standard_error_high = average_load + standard_error_range_factor

                monotony_high = standard_error_high / stdev_load
                daily_strain.upper_bound = monotony_high * current_load.highest_value()

                # unlikely actual load is lower than observed value; ignoring for now
                #standard_error_low = average_load - standard_error_range_factor
                #monotony_low = standard_error_low / stdev_load
                #daily_strain.lower_bound = monotony_low * current_load

        return daily_strain

    def get_strain_value(self, strain_values, load_value, monotony_value):

        if load_value is not None and monotony_value is not None:
            strain_values.append(load_value * monotony_value)

        return strain_values

    def get_strain(self, expected_weekly_workouts, monotony_error_range, last_week_values, historical_strain):

        load = self.get_standard_error_range(expected_weekly_workouts, last_week_values)

        # standard_error_range = StandardErrorRangeMetric() not doing this now
        standard_error_range = StandardErrorRange()

        if monotony_error_range.insufficient_data or load.insufficient_data:
            standard_error_range.insufficient_data = True

        if load.observed_value is not None and monotony_error_range.observed_value is not None:
            standard_error_range.observed_value = load.observed_value * monotony_error_range.observed_value

        '''not doing this now
        if len(historical_strain) > 0:

            strain_count = min(7, len(list(x.observed_value for x in historical_strain if x.observed_value is not None)))

            if strain_count > 1:
                strain_sd = statistics.stdev(
                    list(x.observed_value for x in historical_strain[-strain_count:] if x.observed_value is not None))
                strain_avg = statistics.mean(
                    list(x.observed_value for x in historical_strain[-strain_count:] if x.observed_value is not None))

                if historical_strain[len(
                        historical_strain) - 1] is not None and monotony_error_range.observed_value is not None and monotony_error_range.observed_value > 0:

                    # if the athlete strained, this wil be a negative number
                    # if positive, it reports the amount of load they have left without straining for the last practice
                    strain_surplus = (1.2 * strain_sd) + strain_avg - historical_strain[len(historical_strain)-1].observed_value
                    load_change = strain_surplus / monotony_error_range.observed_value

                    standard_error_range.observed_value_gap = load_change
        '''

        strain_values = []
        # ignoring lower bounds since we know the load can't be lower than observed
        # strain_values = self.get_strain_value(strain_values, load.lower_bound, monotony_error_range.lower_bound)
        # strain_values = self.get_strain_value(strain_values, load.lower_bound, monotony_error_range.observed_value)
        # strain_values = self.get_strain_value(strain_values, load.lower_bound, monotony_error_range.upper_bound)
        # strain_values = self.get_strain_value(strain_values, load.observed_value, monotony_error_range.lower_bound)
        strain_values = self.get_strain_value(strain_values, load.observed_value, monotony_error_range.upper_bound)
        # strain_values = self.get_strain_value(strain_values, load.upper_bound, monotony_error_range.lower_bound)
        strain_values = self.get_strain_value(strain_values, load.upper_bound, monotony_error_range.observed_value)
        strain_values = self.get_strain_value(strain_values, load.upper_bound, monotony_error_range.upper_bound)

        if len(strain_values) > 0:
            min_strain_value = min(strain_values)
            max_strain_value = max(strain_values)

            if standard_error_range.observed_value is not None and min_strain_value < standard_error_range.observed_value:
                standard_error_range.lower_bound = min_strain_value
            if standard_error_range.observed_value is not None and max_strain_value > standard_error_range.observed_value:
                standard_error_range.upper_bound = max_strain_value
            if standard_error_range.observed_value is None:
                standard_error_range.lower_bound = min_strain_value
                standard_error_range.upper_bound = max_strain_value

        '''not doing gap analysis now
        gap_values = []
        # ignoring lower bounds since we know the load can't be lower than observed
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "lower_bound", monotony_error_range.lower_bound)
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "lower_bound", monotony_error_range.observed_value)
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "lower_bound", monotony_error_range.upper_bound)
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "observed_value", monotony_error_range.lower_bound)
        gap_values = self.get_strain_gap(gap_values, historical_strain, "observed_value", monotony_error_range.upper_bound)
        #gap_values = self.get_strain_gap(gap_values, historical_strain, "upper_bound", monotony_error_range.lower_bound)
        gap_values = self.get_strain_gap(gap_values, historical_strain, "upper_bound", monotony_error_range.observed_value)
        gap_values = self.get_strain_gap(gap_values, historical_strain, "upper_bound", monotony_error_range.upper_bound)

        if len(gap_values) > 0:
            min_strain = min(gap_values)
            max_strain = max(gap_values)

            if standard_error_range.observed_value_gap is not None and min_strain < standard_error_range.observed_value_gap:
                standard_error_range.lower_bound_gap = min_strain
            if standard_error_range.observed_value_gap is not None and max_strain > standard_error_range.observed_value_gap:
                standard_error_range.upper_bound_gap = max_strain
            if standard_error_range.observed_value_gap is None:
                standard_error_range.lower_bound_gap = min_strain
                standard_error_range.upper_bound_gap = max_strain

        '''
        return standard_error_range


