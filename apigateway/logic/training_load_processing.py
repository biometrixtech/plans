from fathomapi.utils.xray import xray_recorder
from models.training_volume import StandardErrorRange
from models.session import HighLoadSession, HighDetailedLoadSession, SessionType
from datetime import timedelta
import statistics, math
from utils import format_date, parse_date
from models.stats import SportMaxLoad
from models.movement_tags import AdaptationType


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

    def get_load_5_20(self, attribute_5_day_name, attribute_20_day_name):

        attribute_5_day = getattr(self, attribute_5_day_name)
        attribute_20_day = getattr(self, attribute_20_day_name)

        if attribute_5_day is not None and attribute_20_day is not None:
            standard_error_range = StandardErrorRange()
            combinations = []
            if attribute_5_day.lower_bound is not None and attribute_20_day.lower_bound is not None:
               combinations.append(attribute_5_day.lower_bound / attribute_20_day.lower_bound)
            if attribute_5_day.upper_bound is not None and attribute_20_day.upper_bound is not None:
                combinations.append(attribute_5_day.upper_bound / attribute_20_day.upper_bound)
            if attribute_5_day.lower_bound is not None and attribute_20_day.upper_bound is not None:
                combinations.append(attribute_5_day.lower_bound / attribute_20_day.upper_bound)
            if attribute_5_day.upper_bound is not None and attribute_20_day.lower_bound is not None:
                combinations.append(attribute_5_day.upper_bound / attribute_20_day.lower_bound)

            if attribute_5_day.observed_value is not None and attribute_20_day.observed_value is not None:
                standard_error_range.observed_value = attribute_5_day.observed_value / attribute_20_day.observed_value
            elif attribute_5_day.observed_value is not None and attribute_20_day.observed_value is None:
                standard_error_range.observed_value = attribute_5_day.observed_value
            elif attribute_5_day.observed_value is None and attribute_20_day.observed_value is not None:
                standard_error_range.observed_value = attribute_20_day.observed_value

            if standard_error_range.observed_value is not None:
                combinations.append(standard_error_range.observed_value)

            if len(combinations) > 0:
                standard_error_range.lower_bound = min(combinations)
            if len(combinations) > 0:
                standard_error_range.upper_bound = max(combinations)

            standard_error_range.insufficient_data = min(attribute_5_day.insufficient_data,
                                                         attribute_20_day.insufficient_data)

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
    def load_training_session_values(self, all_training_sessions):

        self.last_week_sport_training_loads = {}
        self.previous_week_sport_training_loads = {}

        five_days_ago = parse_date(self.end_date) - timedelta(days=4)
        eight_days_ago = parse_date(self.end_date) - timedelta(days=7)
        fourteen_days_ago = parse_date(self.end_date) - timedelta(days=13)
        twenty_days_ago = parse_date(self.end_date) - timedelta(days=19)

        eight_day_plus_sessions = list(c for c in all_training_sessions if c.event_date <= eight_days_ago)

        self.last_5_days_training_sessions = list(c for c in all_training_sessions if c.event_date >= five_days_ago)
        self.last_20_days_training_sessions = list(c for c in all_training_sessions if c.event_date >= twenty_days_ago)

        if len(eight_day_plus_sessions) > 0:
            self.training_sessions_exist_days_8_35 = True

        last_14_day_sessions = list(c for c in all_training_sessions if c.event_date > fourteen_days_ago)
        previous_7_day_training_sessions = list(c for c in all_training_sessions if eight_days_ago >= c.event_date > fourteen_days_ago)
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

        return user_stats

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


    def get_percent(self, test_value, base_value):

            if test_value is not None:
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
                standard_error_range.observed_value = sum(values)
            else:
                standard_error_range.observed_value = statistics.mean(values)

        if 1 < len(values) < expected_workouts:
            average_value = statistics.mean(values)
            stdev = statistics.stdev(values)
            standard_error = (stdev / math.sqrt(len(values))) * math.sqrt(
                (expected_workouts - len(values)) / expected_workouts)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            if return_sum:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor) * len(values)
                standard_error_range.lower_bound = (average_value - standard_error_range_factor) * len(values)
            else:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor)
                standard_error_range.lower_bound = (average_value - standard_error_range_factor)
        elif 1 == len(values) < expected_workouts:
            #let'a quick manufacture some data
            fake_values = []
            fake_values.extend(values)
            fake_values.append(values[0] * 1.5)
            average_value = statistics.mean(fake_values)
            stdev = statistics.stdev(fake_values)
            standard_error = (stdev / math.sqrt(len(fake_values))) * math.sqrt(
                (expected_workouts - len(fake_values)) / expected_workouts)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            if return_sum:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor) * len(fake_values)
                standard_error_range.lower_bound = (average_value - standard_error_range_factor) * len(fake_values)
            else:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor)
                standard_error_range.lower_bound = (average_value - standard_error_range_factor)

        elif len(values) == 0:
            standard_error_range.insufficient_data = True

        return standard_error_range
