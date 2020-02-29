from fathomapi.utils.xray import xray_recorder
from models.training_volume import StandardErrorRange
from models.session import HighLoadSession
from datetime import timedelta
import statistics, math
from utils import format_date, parse_date
from models.stats import SportMaxLoad


class TrainingLoadProcessing(object):
    def __init__(self, start_date, end_date, load_stats):
        self.start_date = start_date
        self.end_date = end_date

        self.load_monitoring_measures = {}

        self.no_soreness_load_tuples = []
        self.soreness_load_tuples = []
        self.load_tuples_last_2_weeks = []
        self.load_tuples_last_2_4_weeks = []
        self.no_soreness_load_tuples_last_2_weeks = []
        self.no_soreness_load_tuples_last_2_4_weeks = []
        self.recovery_loads = {}
        self.maintenance_loads = {}
        self.functional_overreaching_loads = {}
        self.functional_overreaching_NFO_loads = {}
        self.high_relative_load_session = False
        self.high_relative_load_sessions = []
        self.doms = []
        self.last_week_sport_training_loads = {}
        self.previous_week_sport_training_loads = {}
        self.last_14_days_training_sessions = []
        self.load_stats = load_stats
        self.sport_max_load = {}

        self.training_sessions_exist_days_8_35 = False

    @xray_recorder.capture('logic.TrainingLoadProcessing.load_plan_values')
    def load_training_session_values(self, last_7_day_training_sessions, previous_7_day_training_sessions,
                                     chronic_training_sessions):

        self.last_week_sport_training_loads = {}
        self.previous_week_sport_training_loads = {}

        eight_days_ago = parse_date(self.end_date) - timedelta(days=8)
        eight_day_plus_sessions = list(c for c in chronic_training_sessions if c.event_date <= eight_days_ago)
        if len(eight_day_plus_sessions) > 0:
            self.training_sessions_exist_days_8_35 = True

        last_14_day_sessions = []
        last_14_day_sessions.extend(previous_7_day_training_sessions)
        last_14_day_sessions.extend(last_7_day_training_sessions)

        self.last_14_days_training_sessions = last_14_day_sessions

        self.load_stats.set_min_max_values(previous_7_day_training_sessions)
        self.load_stats.set_min_max_values(last_7_day_training_sessions)

        for p in previous_7_day_training_sessions:

            if p.sport_name not in self.previous_week_sport_training_loads:
                self.last_week_sport_training_loads[p.sport_name] = []
                self.previous_week_sport_training_loads[p.sport_name] = []
            training_load = p.training_load(self.load_stats)
            if training_load is not None:
                self.previous_week_sport_training_loads[p.sport_name].append(training_load)
                if p.sport_name.value in self.sport_max_load:
                    if training_load > self.sport_max_load[p.sport_name.value].load:
                        self.sport_max_load[p.sport_name.value].load = training_load
                        self.sport_max_load[p.sport_name.value].event_date_time = p.event_date
                        self.sport_max_load[p.sport_name.value].first_time_logged = False
                else:
                    self.sport_max_load[p.sport_name.value] = SportMaxLoad(p.event_date, training_load)
                    self.sport_max_load[p.sport_name.value].first_time_logged = True

        for l in last_7_day_training_sessions:

            if l.sport_name not in self.last_week_sport_training_loads:
                self.last_week_sport_training_loads[l.sport_name] = []
                self.previous_week_sport_training_loads[l.sport_name] = []
            training_load = l.training_load(self.load_stats)
            if training_load is not None:
                self.last_week_sport_training_loads[l.sport_name].append(training_load)
                if l.sport_name.value in self.sport_max_load:
                    if training_load > self.sport_max_load[l.sport_name.value].load:
                        self.sport_max_load[l.sport_name.value].load = training_load
                        self.sport_max_load[l.sport_name.value].event_date_time = l.event_date
                        self.sport_max_load[l.sport_name.value].first_time_logged = False
                else:
                    self.sport_max_load[l.sport_name.value] = SportMaxLoad(l.event_date, training_load)
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

    def set_high_relative_load_sessions(self, athlete_stats, training_sessions):

        for t in training_sessions:
            if t.sport_name in athlete_stats.training_load_ramp:
                if (athlete_stats.training_load_ramp[t.sport_name].observed_value is None or
                        athlete_stats.training_load_ramp[t.sport_name].observed_value > 1.1):
                    if t.session_RPE is not None and t.session_RPE > 4:
                        high_load_session = HighLoadSession(t.event_date, t.sport_name)
                        high_load_session.percent_of_max = self.get_max_training_percent(t)
                        self.high_relative_load_sessions.append(high_load_session)
            else:
                if t.session_RPE is not None and t.session_RPE > 4:
                    high_load_session = HighLoadSession(t.event_date, t.sport_name)
                    high_load_session.percent_of_max = self.get_max_training_percent(t)
                    self.high_relative_load_sessions.append(high_load_session)

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
            if training_volume is not None and training_volume > 0:
                training_volume = round(training_volume, 2)

                if training_session.sport_name.value in self.sport_max_load:

                    percent = int(round((training_volume / self.sport_max_load[training_session.sport_name.value].load) * 100, 0))

        return percent

    def get_standard_error_range(self, expected_workouts_week, values, return_sum=True):

        standard_error_range = StandardErrorRange()

        expected_workouts = 5

        if expected_workouts_week is not None:
            expected_workouts = expected_workouts_week

        if len(values) > 0:
            standard_error_range.observed_value = sum(values)

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
