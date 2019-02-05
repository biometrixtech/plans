from models.training_volume import IndicatorLevel, StandardErrorRange, StandardErrorRangeMetric, SuggestedTrainingDay, TrainingLevel, TrainingVolumeGap, TrainingVolumeGapType, TrainingReport
from models.soreness import HistoricSorenessStatus
from datetime import datetime, timedelta
import statistics, math
from utils import parse_date, parse_datetime, format_date


class TrainingVolumeProcessing(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date
        self.a_internal_load_values = []
        self.a_external_load_values = []
        self.a_high_intensity_values = []
        self.a_mod_intensity_values = []
        self.a_low_intensity_values = []

        self.c_internal_load_values = []
        self.c_external_load_values = []
        self.c_high_intensity_values = []
        self.c_mod_intensity_values = []
        self.c_low_intensity_values = []

        self.last_week_external_values = []
        self.previous_week_external_values = []
        self.last_week_internal_values = []
        self.previous_week_internal_values = []

        self.internal_load_tuples = []
        self.external_load_tuples = []

    def load_plan_values(self, last_7_days_plans, days_8_14_plans, acute_daily_plans, chronic_weeks_plans, chronic_daily_plans):

        self.last_week_external_values.extend(
            x for x in self.get_plan_session_attribute_sum_list("external_load", last_7_days_plans) if x is not None)

        self.last_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                    last_7_days_plans) if x is not None)
        self.previous_week_external_values.extend(
            x for x in self.get_plan_session_attribute_sum_list("external_load", days_8_14_plans) if x is not None)

        self.previous_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                    days_8_14_plans) if x is not None)

        self.a_external_load_values.extend(
            x for x in self.get_plan_session_attribute_sum("external_load", acute_daily_plans) if x is not None)

        self.a_internal_load_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               acute_daily_plans) if x is not None)

        self.a_external_load_values.extend(
            x for x in self.get_plan_session_attribute_sum("external_load", acute_daily_plans) if x is not None)

        self.a_high_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("high_intensity_load", acute_daily_plans) if
            x is not None)

        self.a_mod_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("mod_intensity_load", acute_daily_plans) if
            x is not None)

        self.a_low_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("low_intensity_load", acute_daily_plans) if
            x is not None)

        for w in chronic_weeks_plans:
            self.c_internal_load_values.extend(
                x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes", w)
                if x is not None)

            self.c_external_load_values.extend(
                x for x in self.get_plan_session_attribute_sum("external_load", w) if x is not None)

            self.c_high_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("high_intensity_load", w)
                                           if x is not None)

            self.c_mod_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("mod_intensity_load", w)
                                          if x is not None)

            self.c_low_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("low_intensity_load", w)
                                          if x is not None)

        self.internal_load_tuples.extend(list(x for x in self.get_session_attributes_product_sum_tuple_list("session_RPE",
                                                                                                 "duration_minutes",
                                                                                                acute_daily_plans)
                                if x is not None))
        self.internal_load_tuples.extend(list(x for x in self.get_session_attributes_product_sum_tuple_list("session_RPE",
                                                                                                 "duration_minutes",
                                                                                                 chronic_daily_plans)
                                if x is not None))


    def calc_training_volume_metrics(self, athlete_stats):

        athlete_stats.external_ramp = self.get_ramp(athlete_stats.expected_weekly_workouts,
                                                    self.last_week_external_values, self.previous_week_external_values)

        athlete_stats.internal_ramp = self.get_ramp(athlete_stats.expected_weekly_workouts,
                                                    self.last_week_internal_values, self.previous_week_internal_values)

        athlete_stats.external_monotony = self.get_monotony(athlete_stats.expected_weekly_workouts,
                                                            self.last_week_external_values)

        athlete_stats.external_strain = self.get_strain(athlete_stats.expected_weekly_workouts,
                                                        athlete_stats.external_monotony, self.last_week_external_values, athlete_stats.historical_external_strain)

        athlete_stats.internal_monotony = self.get_monotony(athlete_stats.expected_weekly_workouts,
                                                            self.last_week_internal_values)

        historical_internal_strain = self.get_historical_internal_strain(self.start_date, self.end_date)

        athlete_stats.internal_strain = self.get_strain(athlete_stats.expected_weekly_workouts,
                                                        athlete_stats.internal_monotony, self.last_week_internal_values,
                                                        historical_internal_strain)

        athlete_stats.acute_internal_total_load = self.get_standard_error_range(athlete_stats.expected_weekly_workouts,
                                                                                self.a_internal_load_values)
        athlete_stats.acute_external_total_load = self.get_standard_error_range(athlete_stats.expected_weekly_workouts,
                                                                                self.a_external_load_values)
        athlete_stats.acute_external_high_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.a_high_intensity_values)
        athlete_stats.acute_external_mod_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.a_mod_intensity_values)
        athlete_stats.acute_external_low_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.a_low_intensity_values)

        athlete_stats.chronic_internal_total_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_internal_load_values)
        athlete_stats.chronic_external_total_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_external_load_values)
        athlete_stats.chronic_external_high_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_high_intensity_values)
        athlete_stats.chronic_external_mod_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_mod_intensity_values)
        athlete_stats.chronic_external_low_intensity_load = self.get_standard_error_range(
            athlete_stats.expected_weekly_workouts, self.c_low_intensity_values)

        athlete_stats.external_acwr = self.get_acwr(athlete_stats.acute_external_total_load,
                                                    athlete_stats.chronic_external_total_load)

        athlete_stats.internal_acwr = self.get_acwr(athlete_stats.acute_internal_total_load,
                                                    athlete_stats.chronic_internal_total_load)

        athlete_stats.internal_freshness_index = self.get_freshness_index(
            athlete_stats.acute_internal_total_load,
            athlete_stats.chronic_internal_total_load)

        athlete_stats.external_freshness_index = self.get_freshness_index(
            athlete_stats.acute_external_total_load,
            athlete_stats.chronic_external_total_load)

        athlete_stats.historical_internal_strain = historical_internal_strain

        return athlete_stats

    def get_acwr(self, acute_load_error, chronic_load_error):

        standard_error_range = StandardErrorRangeMetric()

        if acute_load_error.insufficient_data or chronic_load_error.insufficient_data:
            standard_error_range.insufficient_data = True

        if acute_load_error.observed_value is not None and chronic_load_error.observed_value is not None:
            if chronic_load_error.observed_value > 0:
                standard_error_range.observed_value = (acute_load_error.observed_value /
                                                       chronic_load_error.observed_value)

        acwr_values = []

        if acute_load_error.observed_value is not None and chronic_load_error.upper_bound is not None:
            if chronic_load_error.upper_bound > 0:
                acwr_values.append(acute_load_error.observed_value / chronic_load_error.upper_bound)
        if acute_load_error.upper_bound is not None and chronic_load_error.upper_bound is not None:
            if chronic_load_error.upper_bound > 0:
                acwr_values.append(acute_load_error.upper_bound / chronic_load_error.upper_bound)
        if acute_load_error.upper_bound is not None and chronic_load_error.observed_value is not None:
            if chronic_load_error.observed_value > 0:
                acwr_values.append(acute_load_error.upper_bound / chronic_load_error.observed_value)

        if len(acwr_values) > 0:
            min_acwr = min(acwr_values)
            max_acwr = max(acwr_values)
            if (standard_error_range.observed_value is not None
                    and (min_acwr < standard_error_range.observed_value)):
                standard_error_range.lower_bound = min_acwr
            if (standard_error_range.observed_value is not None
                    and (max_acwr > standard_error_range.observed_value)):
                standard_error_range.upper_bound = max_acwr
            if standard_error_range.observed_value is None:
                standard_error_range.lower_bound = min_acwr
                standard_error_range.upper_bound = max_acwr

        acwr_gaps = []
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.lower_bound, chronic_load_error.lower_bound))
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.lower_bound, chronic_load_error.observed_value))
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.lower_bound, chronic_load_error.upper_bound))
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.observed_value, chronic_load_error.lower_bound))
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.observed_value, chronic_load_error.observed_value))
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.observed_value, chronic_load_error.upper_bound))
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.upper_bound, chronic_load_error.lower_bound))
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.upper_bound, chronic_load_error.observed_value))
        acwr_gaps.append(self.get_acwr_gap(acute_load_error.upper_bound, chronic_load_error.upper_bound))

        gap = self.get_lower_training_volume_gap(TrainingVolumeGapType.acwr, list(a for a in acwr_gaps if a is not None))

        if gap is not None:
            standard_error_range.training_volume_gaps.append(gap)

        return standard_error_range

    def get_lower_training_volume_gap(self, gap_type, gaps):

        if len(gaps) == 0:
            return  None

        lower_training_volume_gap = TrainingVolumeGap(gap_type=gap_type)

        low_optimal_list = list(a.low_optimal_threshold for a in gaps if a.low_optimal_threshold is not None)
        high_optimal_list = list(a.high_optimal_threshold for a in gaps if a.high_optimal_threshold is not None)
        low_overreaching_list = list(
            a.low_overreaching_threshold for a in gaps if a.low_overreaching_threshold is not None)
        high_overreaching_list = list(
            a.high_overreaching_threshold for a in gaps if a.high_overreaching_threshold is not None)
        low_excessive_list = list(
            a.low_excessive_threshold for a in gaps if a.low_excessive_threshold is not None)
        high_excessive_list = list(
            a.high_excessive_threshold for a in gaps if a.high_excessive_threshold is not None)

        if len(low_optimal_list) > 0:
            lower_training_volume_gap.low_optimal_threshold = min(low_optimal_list)
        if len(high_optimal_list) > 0:
            lower_training_volume_gap.high_optimal_threshold = min(high_optimal_list)
        if len(low_overreaching_list) > 0:
            lower_training_volume_gap.low_overreaching_threshold = min(low_overreaching_list)
        if len(high_overreaching_list) > 0:
            lower_training_volume_gap.high_overreaching_threshold = min(high_overreaching_list)
        if len(low_excessive_list) > 0:
            lower_training_volume_gap.low_excessive_threshold = min(low_excessive_list)
        if len(high_excessive_list) > 0:
            lower_training_volume_gap.high_excessive_threshold = min(high_excessive_list)
        return lower_training_volume_gap

    def get_upper_training_volume_gap(self, gap_type, gaps):
        upper_training_volume_gap = TrainingVolumeGap(gap_type=gap_type)

        low_optimal_list = list(a.low_optimal_threshold for a in gaps if a.low_optimal_threshold is not None)
        high_optimal_list = list(a.high_optimal_threshold for a in gaps if a.high_optimal_threshold is not None)
        low_overreaching_list = list(
            a.low_overreaching_threshold for a in gaps if a.low_overreaching_threshold is not None)
        high_overreaching_list = list(
            a.high_overreaching_threshold for a in gaps if a.high_overreaching_threshold is not None)
        low_excessive_list = list(
            a.low_excessive_threshold for a in gaps if a.low_excessive_threshold is not None)
        high_excessive_list = list(
            a.high_excessive_threshold for a in gaps if a.high_excessive_threshold is not None)

        if len(low_optimal_list) > 0:
            upper_training_volume_gap.low_optimal_threshold = max(low_optimal_list)
        if len(high_optimal_list) > 0:
            upper_training_volume_gap.high_optimal_threshold = max(high_optimal_list)
        if len(low_overreaching_list) > 0:
            upper_training_volume_gap.low_overreaching_threshold = max(low_overreaching_list)
        if len(high_overreaching_list) > 0:
            upper_training_volume_gap.high_overreaching_threshold = max(high_overreaching_list)
        if len(low_excessive_list) > 0:
            upper_training_volume_gap.low_excessive_threshold = max(low_excessive_list)
        if len(high_excessive_list) > 0:
            upper_training_volume_gap.high_excessive_threshold = max(high_excessive_list)
        return upper_training_volume_gap

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

    def get_strain(self, expected_weekly_workouts, monotony_error_range, last_week_values, historical_strain):

        load = self.get_standard_error_range(expected_weekly_workouts, last_week_values)

        standard_error_range = StandardErrorRangeMetric()

        if monotony_error_range.insufficient_data or load.insufficient_data:
            standard_error_range.insufficient_data = True

        if load.observed_value is not None and monotony_error_range.observed_value is not None:
            standard_error_range.observed_value = load.observed_value * monotony_error_range.observed_value

        strain_values = []

        if load.upper_bound is not None and monotony_error_range.observed_value is not None:
            strain_values.append(load.upper_bound * monotony_error_range.observed_value)
        if load.upper_bound is not None and monotony_error_range.upper_bound is not None:
            strain_values.append(load.upper_bound * monotony_error_range.upper_bound)
        if load.observed_value is not None and monotony_error_range.upper_bound is not None:
            strain_values.append(load.observed_value * monotony_error_range.upper_bound)
        if len(strain_values) > 0:
            min_strain = min(strain_values)
            max_strain = max(strain_values)

            if standard_error_range.observed_value is not None and min_strain < standard_error_range.observed_value:
                standard_error_range.lower_bound = min_strain
            if standard_error_range.observed_value is not None and max_strain > standard_error_range.observed_value:
                standard_error_range.upper_bound = max_strain
            if standard_error_range.observed_value is None:
                standard_error_range.lower_bound = min_strain
                standard_error_range.upper_bound = max_strain

        gaps = []
        gaps.append(self.get_strain_gap(list(x.observed_value for x in historical_strain if x is not None), monotony_error_range.observed_value))
        gaps.append(self.get_strain_gap(list(x.observed_value for x in historical_strain if x is not None),
                                        monotony_error_range.lower_bound))
        gaps.append(self.get_strain_gap(list(x.observed_value for x in historical_strain if x is not None),
                                        monotony_error_range.upper_bound))
        gaps.append(self.get_strain_gap(list(x.lower_bound for x in historical_strain if x is not None),
                                        monotony_error_range.observed_value))
        gaps.append(self.get_strain_gap(list(x.lower_bound for x in historical_strain if x is not None),
                                        monotony_error_range.lower_bound))
        gaps.append(self.get_strain_gap(list(x.lower_bound for x in historical_strain if x is not None),
                                        monotony_error_range.upper_bound))
        gaps.append(self.get_strain_gap(list(x.upper_bound for x in historical_strain if x is not None),
                                        monotony_error_range.observed_value))
        gaps.append(self.get_strain_gap(list(x.upper_bound for x in historical_strain if x is not None),
                                        monotony_error_range.lower_bound))
        gaps.append(self.get_strain_gap(list(x.upper_bound for x in historical_strain if x is not None),
                                        monotony_error_range.upper_bound))

        gap = self.get_lower_training_volume_gap(TrainingVolumeGapType.strain,
                                                                 list(x for x in gaps if x is not None))

        if gap is not None:
            standard_error_range.training_volume_gaps.append(gap)

        return standard_error_range

    def get_monotony(self, expected_weekly_workouts, values):

        standard_error_range = StandardErrorRangeMetric()

        if len(values) > 1:

            average_load = self.get_standard_error_range(expected_weekly_workouts, values, return_sum=False)

            stdev_load = statistics.stdev(values)

            if stdev_load > 0:

                if average_load.observed_value is not None:
                    standard_error_range.observed_value = average_load.observed_value / stdev_load

                if average_load.upper_bound is not None:
                    if standard_error_range.observed_value is not None:
                        if average_load.upper_bound / stdev_load < standard_error_range.observed_value:
                            standard_error_range.lower_bound = average_load.upper_bound / stdev_load
                        elif average_load.upper_bound / stdev_load > standard_error_range.observed_value:
                            standard_error_range.upper_bound = average_load.upper_bound / stdev_load
                    else:
                        standard_error_range.upper_bound = average_load.upper_bound / stdev_load

            low_gaps = []
            high_gaps = []
            m1, m2 = self.get_monotony_gaps(average_load.lower_bound, stdev_load)
            low_gaps.append(m1)
            high_gaps.append(m2)
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

        else:
            standard_error_range.insufficient_data = True

        return standard_error_range

    def get_ramp(self, expected_weekly_workouts, last_week_values, previous_week_values):

        current_load = self.get_standard_error_range(expected_weekly_workouts, last_week_values)
        previous_load = self.get_standard_error_range(expected_weekly_workouts, previous_week_values)

        ramp_error_range = StandardErrorRangeMetric()

        if current_load.insufficient_data or previous_load.insufficient_data:
            ramp_error_range.insufficient_data = True

        if (current_load.observed_value is not None and previous_load.observed_value is not None
                and previous_load.observed_value > 0):
            ramp_error_range.observed_value = current_load.observed_value / float(previous_load.observed_value)

        bound_values = []

        if (current_load.upper_bound is not None and previous_load.upper_bound is not None
                and previous_load.upper_bound > 0):
            bound_values.append(current_load.upper_bound / float(previous_load.upper_bound))
        if (current_load.observed_value is not None and previous_load.upper_bound is not None
                and previous_load.upper_bound > 0):
            bound_values.append(current_load.observed_value / float(previous_load.upper_bound))
        if (current_load.upper_bound is not None and previous_load.observed_value is not None
                and previous_load.observed_value > 0):
            bound_values.append(current_load.upper_bound / float(previous_load.observed_value))
        if len(bound_values) > 0:
            min_bound = min(bound_values)
            max_bound = max(bound_values)
            if (ramp_error_range.observed_value is None or (ramp_error_range.observed_value is not None and
                                                                min_bound < ramp_error_range.observed_value)):
                ramp_error_range.lower_bound = min_bound
            if (ramp_error_range.observed_value is None or (ramp_error_range.observed_value is not None and
                                                                max_bound > ramp_error_range.observed_value)):
                ramp_error_range.upper_bound = max_bound

        ramp_gaps = []
        ramp_gaps.append(self.get_ramp_gap(current_load.lower_bound, previous_load.lower_bound))
        ramp_gaps.append(self.get_ramp_gap(current_load.lower_bound, previous_load.observed_value))
        ramp_gaps.append(self.get_ramp_gap(current_load.lower_bound, previous_load.upper_bound))
        ramp_gaps.append(self.get_ramp_gap(current_load.observed_value, previous_load.lower_bound))
        ramp_gaps.append(self.get_ramp_gap(current_load.observed_value, previous_load.observed_value))
        ramp_gaps.append(self.get_ramp_gap(current_load.observed_value, previous_load.upper_bound))
        ramp_gaps.append(self.get_ramp_gap(current_load.upper_bound, previous_load.lower_bound))
        ramp_gaps.append(self.get_ramp_gap(current_load.upper_bound, previous_load.observed_value))
        ramp_gaps.append(self.get_ramp_gap(current_load.upper_bound, previous_load.upper_bound))

        gap = self.get_lower_training_volume_gap(TrainingVolumeGapType.ramp, list(r for r in ramp_gaps if r is not None))

        if gap is not None:
            ramp_error_range.training_volume_gaps.append(gap)

        return ramp_error_range

    def calc_monotony_strain(self, load_values):

        monotony = None
        strain = None

        if len(load_values) > 1:
            average_load = statistics.mean(load_values)
            stdev_load = statistics.stdev(load_values)
            if stdev_load > 0:
                monotony = average_load / stdev_load
                strain = monotony * sum(load_values)

        return monotony, strain

    def calc_monotony_strain_se(self, load_values, avg_workouts_week):

        monotony = None
        strain = None

        if len(load_values) > 1:
            fpc = max(avg_workouts_week, len(load_values))

            average_load = statistics.mean(load_values)
            stdev_load = statistics.stdev(load_values)
            standard_error = (stdev_load / math.sqrt(len(load_values))) * math.sqrt(
                (fpc - len(load_values)) / fpc)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            high_avg_load = (average_load + standard_error_range_factor)
            high_total_load = high_avg_load * len(load_values)

            if stdev_load > 0:
                monotony = high_avg_load / stdev_load
                strain = monotony * high_total_load

        return monotony, strain

    def get_plan_session_attribute_sum(self, attribute_name, daily_plan_collection):

        sum_value = None

        values = []

        for c in daily_plan_collection:

            values.extend(self.get_values_for_session_attribute(attribute_name, c.training_sessions))
            values.extend(self.get_values_for_session_attribute(attribute_name, c.practice_sessions))
            values.extend(self.get_values_for_session_attribute(attribute_name, c.strength_conditioning_sessions))
            values.extend(self.get_values_for_session_attribute(attribute_name, c.games))
            values.extend(self.get_values_for_session_attribute(attribute_name, c.bump_up_sessions))

        if len(values) > 0:
            sum_value = sum(values)

        return [sum_value]

    def get_plan_session_attribute_sum_list(self, attribute_name, daily_plan_collection):

        #sum_value = None

        values = []

        for c in daily_plan_collection:

            sub_values = []

            sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.training_sessions))
            sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.practice_sessions))
            sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.strength_conditioning_sessions))
            sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.games))
            sub_values.extend(self.get_values_for_session_attribute(attribute_name, c.bump_up_sessions))

            if len(sub_values) > 0:
                sum_value = sum(sub_values)
                values.append(sum_value)

        return values

    def get_session_attributes_product_sum_list(self, attribute_1_name, attribute_2_name, daily_plan_collection):

        # sum_value = None

        values = []

        for c in daily_plan_collection:

            sub_values = []

            sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                     c.training_sessions))
            sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                     c.practice_sessions))
            sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                     c.strength_conditioning_sessions))
            sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                     c.games))
            sub_values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                     c.bump_up_sessions))
            if len(sub_values) > 0:
                sum_value = sum(sub_values)
                values.append(sum_value)

        return values

    def get_session_attributes_product_sum_tuple_list(self, attribute_1_name, attribute_2_name, daily_plan_collection):

        # sum_value = None

        values = []

        for c in daily_plan_collection:

            #sub_values = []

            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.training_sessions))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.practice_sessions))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.strength_conditioning_sessions))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.games))
            values.extend(self.get_tuple_product_of_session_attributes(c.get_event_datetime(), attribute_1_name, attribute_2_name,
                                                                     c.bump_up_sessions))
            #if len(sub_values) > 0:
            #    sum_value = sum(sub_values)
            #    values.append(sum_value)

        return values

    def get_session_attributes_product_sum(self, attribute_1_name, attribute_2_name, daily_plan_collection):

        sum_value = None

        values = []

        for c in daily_plan_collection:
            values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                 c.training_sessions))
            values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                 c.practice_sessions))
            values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                 c.strength_conditioning_sessions))
            values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                 c.games))
            values.extend(self.get_product_of_session_attributes(attribute_1_name, attribute_2_name,
                                                                 c.bump_up_sessions))
        if len(values) > 0:
            sum_value = sum(values)

        return [sum_value]

    def get_values_for_session_attribute(self, attribute_name, session_collection):

        try:
            values = list(getattr(c, attribute_name) for c in session_collection if getattr(c, attribute_name) is not None)
            return values
        except:
            return []

    def get_product_of_session_attributes(self, attribute_1_name, attribute_2_name, session_collection):

        values = list(getattr(c, attribute_1_name) * getattr(c, attribute_2_name) for c in session_collection
                      if getattr(c, attribute_1_name) is not None and getattr(c, attribute_2_name) is not None)
        return values

    def get_tuple_product_of_session_attributes(self, event_date_time, attribute_1_name, attribute_2_name, session_collection):

        values = []
        values_list = list(getattr(c, attribute_1_name) * getattr(c, attribute_2_name) for c in session_collection
                      if getattr(c, attribute_1_name) is not None and getattr(c, attribute_2_name) is not None)
        for v in values_list:
            values.append((event_date_time, v))

        return values

    def get_historical_internal_strain(self, start_date, end_date, weekly_expected_workouts=5):

        target_dates = []

        #all_plans.sort(key=lambda x: x.event_date)
        self.internal_load_tuples.sort(key=lambda x: x[0])

        date_diff = parse_date(end_date) - parse_date(start_date)

        for i in range(1, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        index = 0
        strain_values = []

        # evaluates a rolling week's worth of values for each day to calculate "daily" strain
        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_plans = [p for p in self.internal_load_tuples if (parse_date(start_date) + timedelta(index)) < p[0] <= target_dates[t]]
                load_values.extend(x[1] for x in daily_plans if x is not None)
                strain = self.calculate_daily_strain(load_values, weekly_expected_workouts)
                if strain.observed_value is not None or strain.upper_bound is not None:
                    strain_values.append(strain)
                index += 1

        return strain_values

    def calculate_daily_strain(self, load_values, weekly_expected_workouts=5):

        daily_strain = StandardErrorRange()

        if len(load_values) > 1:

            current_load = sum(load_values)
            average_load = statistics.mean(load_values)
            stdev_load = statistics.stdev(load_values)
            if stdev_load > 0:
                monotony = average_load / stdev_load
                daily_strain.observed_value = monotony * current_load

                if len(load_values) < weekly_expected_workouts:
                    standard_error = (stdev_load / math.sqrt(len(load_values))) * math.sqrt(
                        (weekly_expected_workouts - len(load_values)) / weekly_expected_workouts)  # adjusts for finite population correction
                    standard_error_range_factor = 1.96 * standard_error
                    # we may underestimate load from observed values, not overestimate so we only need upper bound
                    standard_error_high = average_load + standard_error_range_factor

                    internal_monotony_high = standard_error_high / stdev_load
                    daily_strain.upper_bound = internal_monotony_high * current_load

        return daily_strain

    def get_ramp_gap(self, current_load, previous_load):

        if current_load is None or previous_load is None:
            return None

        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.ramp)

        training_volume_gap.low_optimal_threshold = previous_load - current_load
        training_volume_gap.high_optimal_threshold = (1.10 * previous_load) - current_load
        training_volume_gap.low_overreaching_threshold = (1.11 * previous_load) - current_load
        training_volume_gap.high_overreaching_threshold = (1.15 * previous_load) - current_load
        training_volume_gap.low_excessive_threshold = (1.16 * previous_load) - current_load
        training_volume_gap.high_excessive_threshold = (1.16 * previous_load) - current_load

        return training_volume_gap

    def get_ramp_gap_old(self, current_load_values, previous_load_values, avg_workouts_week=5):

        current_load = 0
        current_load_high = 0
        previous_load = 0
        previous_load_high = 0

        if len(current_load_values) > 1:
            if len(current_load_values) < avg_workouts_week:
                average_load = statistics.mean(current_load_values)
                stdev_load = statistics.stdev(current_load_values)
                standard_error = (stdev_load / math.sqrt(len(current_load_values))) * math.sqrt(
                    (avg_workouts_week - len(current_load_values)) / avg_workouts_week)  # adjusts for finite population correction
                standard_error_range_factor = 1.96 * standard_error
                current_load_high = (average_load + standard_error_range_factor) * len(current_load_values)
            current_load = sum(current_load_values)

        if len(previous_load_values) > 1:
            if len(previous_load_values) < avg_workouts_week:
                average_load = statistics.mean(previous_load_values)
                stdev_load = statistics.stdev(previous_load_values)
                standard_error = (stdev_load / math.sqrt(len(previous_load_values))) * math.sqrt(
                    (avg_workouts_week - len(previous_load_values)) / avg_workouts_week)  # adjusts for finite population correction
                standard_error_range_factor = 1.96 * standard_error
                previous_load_high = (average_load + standard_error_range_factor) * len(previous_load_values)
            previous_load = sum(previous_load_values)

        '''deprecated
        if previous_load > 0:
            ramp_1 = current_load / float(previous_load)
            ramp_2 = current_load_high / float(previous_load)
        else:
            ramp_1 = 0
            ramp_2 = 0
            
        if previous_load_high > 0:
            ramp_3 = current_load / float(previous_load_high)
            ramp_4 = current_load_high / float(previous_load_high)
        else:
            ramp_3 = 0
            ramp_4 = 0
        
        
        if ramp > 1.1:
            low_load = 0.0
            high_load = 0.0
        else:
        '''
        #1.0 = current_load / previous_load
        #1.1* previous_load = current_load + gap
        #low_load = (1.0 * previous_load) + previous_load - current_load

        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.ramp)

        training_volume_gap.low_optimal_threshold = previous_load - current_load
        training_volume_gap.high_optimal_threshold = (1.10 * previous_load) - current_load
        training_volume_gap.low_overreaching_threshold = (1.11 * previous_load) - current_load
        training_volume_gap.high_overreaching_threshold = (1.15 * previous_load) - current_load
        training_volume_gap.low_excessive_threshold = (1.16 * previous_load) - current_load
        training_volume_gap.high_excessive_threshold = (1.16 * previous_load) - current_load
        if previous_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load_high - current_load)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                             (1.10 * previous_load_high) - current_load)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load_high) - current_load)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.15 * previous_load_high) - current_load)
            training_volume_gap.low_excessive_threshold = min(training_volume_gap.low_excessive_threshold,
                                                                 (1.16 * previous_load_high) - current_load)
            training_volume_gap.high_excessive_threshold = max(training_volume_gap.high_excessive_threshold,
                                                                  (1.16 * previous_load_high) - current_load)
        if current_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load - current_load_high)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                             (1.10 * previous_load) - current_load_high)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load) - current_load_high)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.15 * previous_load) - current_load_high)
            training_volume_gap.low_excessive_threshold = min(training_volume_gap.low_excessive_threshold,
                                                                 (1.16 * previous_load) - current_load_high)
            training_volume_gap.high_excessive_threshold = max(training_volume_gap.high_excessive_threshold,
                                                                  (1.16 * previous_load) - current_load_high)
        if previous_load_high > 0 and current_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load_high - current_load_high)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                             (1.10 * previous_load_high) - current_load_high)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load_high) - current_load_high)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.15 * previous_load_high) - current_load_high)
            training_volume_gap.low_excessive_threshold = min(training_volume_gap.low_excessive_threshold,
                                                                 (1.16 * previous_load_high) - current_load_high)
            training_volume_gap.high_excessive_threshold = max(training_volume_gap.high_excessive_threshold,
                                                                  (1.16 * previous_load_high) - current_load_high)

        '''deprecated
        low_load = previous_load - current_load
        high_load = (1.1 * previous_load) - current_load
        overreaching_load = (1.11 * previous_load) - current_load
        excessive_load = (1.16 * previous_load) - current_load
        
        #training_volume_gap = TrainingVolumeGap(low_load, overreaching_load, excessive_load, TrainingVolumeGapType.ramp)
        
        
        if ramp < 1:
            training_volume_gap.training_level = TrainingLevel.undertraining
        elif 1 <= ramp < 1.1:
            training_volume_gap.training_level = TrainingLevel.optimal
        elif 1.1 <= ramp < 1.15:
            training_volume_gap.training_level = TrainingLevel.overreaching
        elif ramp >= 1.15:
            training_volume_gap.training_level = TrainingLevel.excessive
        '''

        return training_volume_gap

    def get_acute_chronic_durations(self, training_report, acute_start_date_time, acute_daily_plans, chronic_daily_plans):

        acute_values = []
        chronic_1_values = []
        chronic_2_values = []
        chronic_3_values = []
        chronic_4_values = []

        acute_days = len(acute_daily_plans)
        chronic_days = len(chronic_daily_plans)

        daily_plans = []
        daily_plans.extend(acute_daily_plans)
        daily_plans.extend(chronic_daily_plans)

        all_chronic_values = []
        all_chronic_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes", chronic_daily_plans) if x is not None)

        acute_values.extend(
            x for x in self.get_plan_session_attribute_sum_list("duration_minutes", acute_daily_plans) if x is not None)

        chronic_values = []

        if acute_days == 7 and chronic_days == 28:

            week4_sessions = [d for d in chronic_daily_plans if acute_start_date_time - timedelta(days=28) <=
                              d.get_event_datetime() < acute_start_date_time - timedelta(days=21)]

            chronic_4_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes", week4_sessions) if x is not None)
            chronic_values.append(sum(chronic_4_values))

        if acute_days == 7 and 21 <= chronic_days <= 28:

            week3_sessions = [d for d in chronic_daily_plans if acute_start_date_time
                              - timedelta(days=21) <= d.get_event_datetime() < acute_start_date_time -
                              timedelta(days=14)]

            chronic_3_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes", week3_sessions) if x is not None)
            chronic_values.append(sum(chronic_3_values))

        if acute_days == 7 and 14 <= chronic_days <= 28:

            week2_sessions = [d for d in chronic_daily_plans if acute_start_date_time
                              - timedelta(days=14) <= d.get_event_datetime() < acute_start_date_time -
                              timedelta(days=7)]

            chronic_2_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes", week2_sessions) if x is not None)
            chronic_values.append(sum(chronic_2_values))

        if acute_days <= 7 and 7 <= chronic_days <= 28:

            week1_sessions = [d for d in chronic_daily_plans if acute_start_date_time
                              - timedelta(days=7) <= d.get_event_datetime() < acute_start_date_time]

            chronic_1_values.extend(
                x for x in self.get_plan_session_attribute_sum_list("duration_minutes",
                                                                        week1_sessions) if x is not None)

            chronic_values.append(sum(chronic_1_values))

        chronic_value = 0
        if len(chronic_values) > 0:
            chronic_value = statistics.mean(chronic_values)
            training_report.chronic_min_duration_minutes = min(all_chronic_values)
            training_report.chronic_max_duration_minutes = max(all_chronic_values)
            training_report.chronic_avg_duration_minutes = statistics.mean(all_chronic_values)
        training_report.chronic_duration_minutes = chronic_value

        acute_value = 0
        if len(acute_values) > 0:
            acute_value = sum(acute_values)
            training_report.acute_min_duration_minutes = min(acute_values)
            training_report.acute_max_duration_minutss = max(acute_values)
            training_report.acute_avg_duration_minutes = statistics.mean(acute_values)

        training_report.acute_duration_minutes = acute_value
        if training_report.chronic_duration_minutes > 0:
            training_report.acute_chronic_duration_minutes = training_report.acute_duration_minutes / training_report.chronic_duration_minutes

        return training_report

    def get_acwr_gap(self, acute_value, chronic_value):

        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.acwr)

        if acute_value is not None and chronic_value is not None and chronic_value > 0:

            training_volume_gap.low_optimal_threshold =(0.8 * chronic_value) - acute_value
            training_volume_gap.high_optimal_threshold = (1.3 * chronic_value) - acute_value
            training_volume_gap.low_overreaching_threshold = (1.31 * chronic_value) - acute_value
            training_volume_gap.high_overreaching_threshold = (1.50 * chronic_value) - acute_value
            training_volume_gap.low_excessive_threshold = (1.51 * chronic_value) - acute_value
            training_volume_gap.high_excessive_threshold = (1.51 * chronic_value) - acute_value

        return training_volume_gap

    def get_acwr_gap_old(self, acute_values, chronic_values, chronic_values_high, avg_workouts_week=5):

        chronic_value = 0
        chronic_high_value = 0
        acute_high = 0

        if len(chronic_values) > 0:
            chronic_value = statistics.mean(chronic_values)

        if len(chronic_values_high) > 0:
            chronic_high_value = statistics.mean(chronic_values_high)

        acute_value = 0
        if len(acute_values) > 0 or len(acute_values) >= avg_workouts_week:
            acute_value = sum(acute_values)
        if 1 < len(acute_values) < avg_workouts_week:
            average_load = statistics.mean(acute_values)
            stdev_load = statistics.stdev(acute_values)
            standard_error = (stdev_load / math.sqrt(len(acute_values))) * math.sqrt((avg_workouts_week-len(acute_values))/avg_workouts_week) #adjusts for finite population correction
            standard_error_range_factor = 1.96 * standard_error
            acute_high = (average_load + standard_error_range_factor) * len(acute_values)

        # ideal is 0.8 to 1.3 with 1.3 being ideal
        # low_difference = 0.8 = (acute_value + x) / chronic_value
        # 0.8 * chronic_value = acute_value + x
        # (0.8 * chronic_value) - acute_value = x

        training_volume_gaps = []
        training_volume_gaps.append(TrainingVolumeGap((0.8 * chronic_value) - acute_value,
                                                (1.31 * chronic_value) - acute_value,
                                                (1.51 * chronic_value) - acute_value, TrainingVolumeGapType.acwr))
        training_volume_gaps.append(TrainingVolumeGap((0.8 * chronic_high_value) - acute_value,
                                                  (1.31 * chronic_high_value) - acute_value,
                                                  (1.51 * chronic_high_value) - acute_value, TrainingVolumeGapType.acwr))

        training_volume_gaps.append(TrainingVolumeGap((0.8 * chronic_value) - acute_high,
                                                  (1.31 * chronic_value) - acute_high,
                                                  (1.51 * chronic_value) - acute_high, TrainingVolumeGapType.acwr))

        training_volume_gaps.append(TrainingVolumeGap((0.8 * chronic_high_value) - acute_high,
                                                  (1.31 * chronic_high_value) - acute_high,
                                                  (1.51 * chronic_high_value) - acute_high, TrainingVolumeGapType.acwr))

        optimal_list = list(t.low_optimal_threshold for t in training_volume_gaps if t is not None)
        overreaching_list = list(t.low_overreaching_threshold for t in training_volume_gaps if t is not None)
        excessive_list = list(t.low_excessive_threshold for t in training_volume_gaps if t is not None)
        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.acwr)
        if len(optimal_list) > 0:
            training_volume_gap.low_optimal_threshold = min(optimal_list)
            training_volume_gap.high_optimal_threshold = max(optimal_list)
        if len(overreaching_list) > 0:
            training_volume_gap.low_overreaching_threshold = min(overreaching_list)
            training_volume_gap.high_overreaching_threshold = max(overreaching_list)
        if len(excessive_list) > 0:
            training_volume_gap.low_excessive_threshold = min(excessive_list)
            training_volume_gap.high_excessive_threshold = max(excessive_list)

        return training_volume_gap

    def get_ewacwr_gap(self, acute_plans, chronic_plans):

        acute_value = 0
        chronic_value = 0
        #acute_n = len(acute_plans)
        #chronic_n = len(chronic_plans)
        acute_n = 7
        chronic_n = 28
        acute_value_sd = 0
        chronic_value_sd = 0
        n = 1
        for a in acute_plans:
            acute_value = (2/(acute_n + 1)) * a[1] + ((1 - (2/(acute_n + 1))) * acute_value)
            w = float(2/float((acute_n + 1)))
            acute_value_sd = math.sqrt(w * ((float(a[1]) - float(acute_value))**2) + ((1-w)*(acute_value_sd**2)))
            standard_error = acute_value_sd / math.sqrt(n)
            standard_error_range_factor = 1.96 * standard_error
            acute_low = acute_value - standard_error_range_factor
            acute_high = acute_value + standard_error_range_factor
            n += 1

        n = 1
        for c in chronic_plans:
            chronic_value = (2 / (chronic_n + 1)) * c[1] + ((1 - (2 / (chronic_n + 1))) * chronic_value)
            w = float(2/float((chronic_n + 1)))
            chronic_value_sd = math.sqrt(w * ((float(c[1]) - float(chronic_value))**2) + ((1-w)*(chronic_value**2)))
            standard_error = chronic_value_sd / math.sqrt(n)
            standard_error_range_factor = 1.96 * standard_error
            chronic_low = chronic_value - standard_error_range_factor
            chronic_high = chronic_value + standard_error_range_factor
            n += 1
        # ideal is 0.8 to 1.3 with 1.3 being ideal
        # low_difference = 0.8 = (acute_value + x) / chronic_value
        # 0.8 * chronic_value = acute_value + x
        # (0.8 * chronic_value) - acute_value = x

        ac_1 = acute_low / chronic_high
        ac_2 = acute_high / chronic_low
        ac_3 = acute_low / chronic_low
        ac_4 = acute_high / chronic_high

        training_volume_gap = TrainingVolumeGap((0.8 * chronic_value) - acute_value,
                                                (1.31 * chronic_value) - acute_value,
                                                (1.51 * chronic_value) - acute_value, TrainingVolumeGapType.acwr)

        return training_volume_gap

    def get_training_report(self, athlete_stats, new_stats_processing, avg_workouts_week=5):

        user_id = athlete_stats.athlete_id
        historical_internal_strain = athlete_stats.historical_internal_strain
        acute_days = new_stats_processing.acute_days
        chronic_days = new_stats_processing.chronic_days
        acute_start_date_time = new_stats_processing.acute_start_date_time
        chronic_start_date_time = new_stats_processing.chronic_start_date_time
        end_date_time = new_stats_processing.end_date_time
        daily_plans = new_stats_processing.daily_internal_plans

        report = TrainingReport(user_id=user_id)

        #report.internal_monotony_index = athlete_stats.internal_monotony
        #report = self.calc_need_for_variability(athlete_stats.internal_monotony, report)

        suggested_training_days = []

        target_load = 0

        #for index in range(0, 7):
        for index in range(0, 1): # just doing one day now

            chronic_values = []
            chronic_values_high = []
            #chronic_1_values = []
            #chronic_2_values = []
            #chronic_3_values = []
            #chronic_4_values = []

            #new_acute_start_date_time = acute_start_date_time + timedelta(days=1) + timedelta(days=index)
            #new_chronic_start_date_time = chronic_start_date_time + timedelta(days=1) + timedelta(days=index)

            acute_values = new_stats_processing.get_acute_internal_values()
            chronic_values_by_week = new_stats_processing.get_chronic_daily_values_by_week()

            #new_chronic_daily_plans = sorted([p for p in daily_plans if new_acute_start_date_time > p[0] >=
            #                                  new_chronic_start_date_time], key=lambda x: x[0])

            #week4_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=28)
            #                  <= d[0] < new_acute_start_date_time - timedelta(days=21)]

            #chronic_4_values.extend(x[1] for x in week4_sessions if x[1] is not None)

            se_range_chronic_4 = self.get_standard_error_range(avg_workouts_week, chronic_values_by_week[3])
            if not se_range_chronic_4.insufficient_data and se_range_chronic_4.upper_bound is not None:
                chronic_values_high.append(se_range_chronic_4.upper_bound*len(chronic_values_by_week[3]))
            if se_range_chronic_4.observed_value is not None:
                chronic_values.append(se_range_chronic_4.observed_value)

            #week3_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=21)
            #                  <= d[0] < new_acute_start_date_time - timedelta(days=14)]

            #chronic_3_values.extend(x[1] for x in week3_sessions if x[1] is not None)
            se_range_chronic_3 = self.get_standard_error_range(avg_workouts_week, chronic_values_by_week[2])
            if se_range_chronic_3.observed_value is not None:
                chronic_values.append(se_range_chronic_3.observed_value)
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if not se_range_chronic_3.insufficient_data and se_range_chronic_3.upper_bound is not None:
                chronic_values_high.append(se_range_chronic_3.upper_bound*len(chronic_values_by_week[2]))
            else:
                if len(chronic_values_high) > 0:
                    chronic_values_high.append(0)

            #week2_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=14)
            #                  <= d[0] < new_acute_start_date_time - timedelta(days=7)]

            #chronic_2_values.extend(x[1] for x in week2_sessions if x[1] is not None)
            se_range_chronic_2 = self.get_standard_error_range(avg_workouts_week, chronic_values_by_week[1])
            if se_range_chronic_2.observed_value is not None:
                chronic_values.append(se_range_chronic_2.observed_value)
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if not se_range_chronic_2.insufficient_data and se_range_chronic_2.upper_bound is not None:
                chronic_values_high.append(se_range_chronic_2.upper_bound*len(chronic_values_by_week[1]))
            else:
                if len(chronic_values_high) > 0:
                    chronic_values_high.append(0)

            #week1_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=7)
            #                  <= d[0] < new_acute_start_date_time]

            #chronic_1_values.extend(x[1] for x in week1_sessions if x[1] is not None)

            se_range_chronic_1 = self.get_standard_error_range(avg_workouts_week, chronic_values_by_week[0])
            if se_range_chronic_1.observed_value is not None:
                chronic_values.append(se_range_chronic_1.observed_value)
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if not se_range_chronic_1.insufficient_data and se_range_chronic_1.upper_bound is not None:
                chronic_values_high.append(se_range_chronic_1.upper_bound*len(chronic_values_by_week[0]))
            else:
                if len(chronic_values_high) > 0:
                    chronic_values_high.append(0)

            last_6_internal_load_values = []
            last_7_internal_load_values = []
            last_7_13_internal_load_values = []

            last_six_days = end_date_time - timedelta(days=6 + 1) + timedelta(days=index)
            last_seven_days = end_date_time - timedelta(days=7 + 1) + timedelta(days=index)
            thirteen_days_ago = last_six_days - timedelta(days=7)

            last_6_day_plans = [p for p in daily_plans if p[0] >= last_six_days]
            last_7_day_plans = [p for p in daily_plans if p[0] >= last_seven_days]
            last_7_day_plans.sort(key=lambda x: x[0], reverse=False)

            last_7_13_day_plans = [p for p in daily_plans if thirteen_days_ago <= p[0] < last_six_days]

            last_6_internal_load_values.extend(x[1] for x in last_6_day_plans if x[1] is not None)
            #last_6_internal_load_values.extend(list(x.target_load for x in suggested_training_days))

            last_7_internal_load_values.extend(x[1] for x in last_7_day_plans if x[1] is not None)

            last_7_13_internal_load_values.extend(x[1] for x in last_7_13_day_plans if x[1] is not None)

            #current_load = sum(last_6_internal_load_values)
            #previous_load = sum(last_7_13_internal_load_values)
            #ramp_load = previous_load
            if len(chronic_values) > 0:
                average_chronic_load = statistics.mean(chronic_values)
                #ramp_load = max(average_chronic_load, ramp_load)
            ramp_gap = self.get_ramp_gap(last_6_internal_load_values, last_7_13_internal_load_values, avg_workouts_week)

            low_monotony_gap, high_monotony_gap,  = self.get_monotony_gap(last_6_internal_load_values, avg_workouts_week)

            strain_gap = self.get_strain_gap(historical_internal_strain, last_7_internal_load_values, avg_workouts_week)

            acwr_gap = self.get_acwr_gap(acute_values, chronic_values, chronic_values_high, avg_workouts_week)
            #acwr_gap = self.get_ewacwr_gap(new_acute_daily_plans, new_chronic_daily_plans)

            gap_list = [ramp_gap, strain_gap, acwr_gap]

            suggested_training_day = self.compile_training_report(user_id, end_date_time + timedelta(days=index), gap_list, low_monotony_gap, high_monotony_gap)
            #if min(suggested_training_day.high_threshold - suggested_training_day.low_threshold, target_load) < 30:
            #    suggested_training_day.target_load = 0
            #else:
            #    if target_load > 0:
            #        suggested_training_day.target_load = min(suggested_training_day.high_threshold - suggested_training_day.low_threshold, target_load)
            #    else:
            #        suggested_training_day.target_load = suggested_training_day.high_threshold - suggested_training_day.low_threshold
            suggested_training_day.target_load = 0
            suggested_training_days.append(suggested_training_day)
            matching_workouts = list(d for d in daily_plans if d[1]<suggested_training_day.low_overreaching_threshold)
            matching_workouts.sort(key=lambda x: x[1], reverse=True)
            suggested_training_day.matching_workouts = matching_workouts
            daily_plans.append((suggested_training_day.date_time, suggested_training_day.target_load))
            internal_monotony = 0
            #if chronic_days < 28:
            #    chronic_days += 1
            if len(last_7_internal_load_values) > 0:
                new_strain = self.calculate_daily_strain(last_7_internal_load_values)
                if len(historical_internal_strain) > 0:
                    del historical_internal_strain[0]
                if new_strain is not None:
                    historical_internal_strain.append(new_strain)
                new_average_load = statistics.mean(last_7_internal_load_values)
                if len(last_7_internal_load_values) > 1:
                    new_stdev_load = statistics.stdev(last_7_internal_load_values)

                    if new_stdev_load > 0:
                        internal_monotony = new_average_load / new_stdev_load

        report.suggested_training_days = suggested_training_days


        return report

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
            else:
                standard_error_range.upper_bound = (average_value + standard_error_range_factor)
        elif 1 == len(values) < expected_workouts or len(values) == 0:
            standard_error_range.insufficient_data = True

        return standard_error_range

    def calc_need_for_variability(self, internal_monotony, report):

        if internal_monotony is not None:
            if internal_monotony > 2:
                report.need_for_variability = IndicatorLevel.high
                # report.training_level = TrainingLevel.overreaching - how should we summarize?

            elif 1.3 < internal_monotony <= 2:
                report.need_for_variability = IndicatorLevel.moderate

            elif internal_monotony <= 1.3:
                report.need_for_variability = IndicatorLevel.low

        else:
            report.need_for_variability = IndicatorLevel.low

        return report

    def calc_report_stats(self, acute_plans, acute_start_date_time, athlete_stats, chronic_plans, report):
        report.internal_acwr = athlete_stats.internal_acwr
        report.internal_freshness_index = athlete_stats.internal_freshness_index
        report.competition_focused = (report.internal_freshness_index > 0)
        report.performance_focused = (report.internal_freshness_index <= 0)
        if athlete_stats.internal_acwr is not None:
            if athlete_stats.internal_acwr < 0.8:
                report.training_level = TrainingLevel.undertraining
            elif 0.8 <= athlete_stats.internal_acwr <= 1.3:
                report.training_level = TrainingLevel.optimal
            elif 1.3 < athlete_stats.internal_acwr <= 1.5:
                report.training_level = TrainingLevel.overreaching
            elif athlete_stats.internal_acwr > 1.5:
                report.training_level = TrainingLevel.excessive
        report.internal_strain = athlete_stats.internal_strain
        report.internal_ramp = athlete_stats.internal_ramp
        report = self.get_acute_chronic_workout_characteristics(report, acute_plans, chronic_plans)
        report = self.get_acute_chronic_durations(report, acute_start_date_time, acute_plans, chronic_plans)
        report.historic_soreness = list(h for h in athlete_stats.historic_soreness if
                                        h.historic_soreness_status is not HistoricSorenessStatus.dormant_cleared)
        severity_list = list(h.average_severity for h in report.historic_soreness)
        if len(severity_list) > 0:
            report.low_hs_severity = min(severity_list)
            report.high_hs_severity = max(severity_list)
            report.average_hs_severity = statistics.mean(severity_list)
        return report

    def get_acute_chronic_workout_characteristics(self, training_report, acute_plans, chronic_plans):

        acute_rpes = []
        chronic_rpes = []

        acute_rpes.extend(
            x for x in self.get_plan_session_attribute_sum_list("session_RPE", acute_plans) if x is not None)
        chronic_rpes.extend(
            x for x in self.get_plan_session_attribute_sum_list("session_RPE", chronic_plans) if x is not None)

        if len(acute_rpes) > 0:
            training_report.acute_min_rpe = min(acute_rpes)
            training_report.acute_max_rpe = max(acute_rpes)
            training_report.acute_avg_rpe = statistics.mean(acute_rpes)
        if len(chronic_rpes) > 0:
            training_report.chronic_min_rpe = min(chronic_rpes)
            training_report.chronic_max_rpe = max(chronic_rpes)
            training_report.chronic_avg_rpe = statistics.mean(chronic_rpes)

        if training_report.acute_avg_rpe is not None and training_report.chronic_avg_rpe is not None and training_report.chronic_avg_rpe > 0:
            training_report.rpe_acwr = training_report.acute_avg_rpe / training_report.chronic_avg_rpe

        return training_report


    def get_monotony_gaps(self, average_load, stdev_load):

        if average_load is None or stdev_load is None or stdev_load == 0:
            return None, None

        low_monotony_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.monotony)
        low_monotony_gap.low_optimal_threshold = average_load - (1.10 * stdev_load)
        low_monotony_gap.high_optimal_threshold = average_load - (1.01 * stdev_load)

        high_montony_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.monotony)
        high_montony_gap.low_optimal_threshold = average_load + (1.01 * stdev_load)
        high_montony_gap.high_optimal_threshold = average_load + (1.10 * stdev_load)

        return low_monotony_gap, high_montony_gap

    def get_monotony_gap(self, last_6_internal_load_values, avg_workouts_week=5):

        # what is the monotony if we have a workout with this load?
        average_load = 0
        high_average_load = 0

        if len(last_6_internal_load_values) > 0:
            average_load = statistics.mean(last_6_internal_load_values)
        if len(last_6_internal_load_values) > 1:
            fpc = max(avg_workouts_week, len(last_6_internal_load_values))
            stdev_load = statistics.stdev(last_6_internal_load_values)
            standard_error = (stdev_load / math.sqrt(len(last_6_internal_load_values))) * math.sqrt(
                (fpc - len(last_6_internal_load_values)) / fpc)  # includes finite population correction
            standard_error_range_factor = 1.96 * standard_error
            high_average_load = average_load + standard_error_range_factor

        stdev_load = 0
        if len(last_6_internal_load_values) > 1:
            stdev_load = statistics.stdev(last_6_internal_load_values)

        if stdev_load > 0:
            internal_monotony = average_load / stdev_load
            internal_monotony_high = high_average_load / stdev_load
        else:
            internal_monotony = 0
            internal_monotony_high = 0
        # monotony = weekly mean total load/weekly standard deviation of load
        # In order to increase the standard deviation of a set of numbers, you must add a value that is more than
        # one standard deviation away from the mean
        low_overreaching_fix = None
        high_overreaching_fix = None
        low_excessive_fix = None
        high_excessive_fix = None
        if 1.7 < internal_monotony < 2.0:
            low_overreaching_fix = average_load - (1.05 * stdev_load)
            high_overreaching_fix = average_load + (1.05 * stdev_load)
        elif internal_monotony >= 2.0:
            low_excessive_fix = average_load - (1.05 * stdev_load)
            high_excessive_fix = average_load + (1.05 * stdev_load)
        low_monotony_gap_low = TrainingVolumeGap(None, low_overreaching_fix, low_excessive_fix, TrainingVolumeGapType.monotony)
        high_monotony_gap_low = TrainingVolumeGap(None, high_overreaching_fix, high_excessive_fix, TrainingVolumeGapType.monotony)

        low_overreaching_fix = None
        high_overreaching_fix = None
        low_excessive_fix = None
        high_excessive_fix = None
        if 1.7 < internal_monotony_high < 2.0:
            low_overreaching_fix = high_average_load - (1.05 * stdev_load)
            high_overreaching_fix = high_average_load + (1.05 * stdev_load)
        elif internal_monotony_high >= 2.0:
            low_excessive_fix = high_average_load - (1.05 * stdev_load)
            high_excessive_fix = high_average_load + (1.05 * stdev_load)
        low_monotony_gap_high = TrainingVolumeGap(None, low_overreaching_fix, low_excessive_fix,
                                             TrainingVolumeGapType.monotony)
        high_monotony_gap_high = TrainingVolumeGap(None, high_overreaching_fix, high_excessive_fix,
                                              TrainingVolumeGapType.monotony)

        low_monotony_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.monotony)
        low_monotony_gap.low_overreaching_threshold = low_monotony_gap_low.low_overreaching_threshold
        low_monotony_gap.high_overreaching_threshold = low_monotony_gap_high.low_overreaching_threshold
        low_monotony_gap.low_excessive_threshold = low_monotony_gap_low.low_excessive_threshold
        low_monotony_gap.high_excessive_threshold = low_monotony_gap_high.low_excessive_threshold

        high_monotony_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.monotony)
        high_monotony_gap.low_overreaching_threshold = high_monotony_gap_low.low_overreaching_threshold
        high_monotony_gap.high_overreaching_threshold = high_monotony_gap_high.low_overreaching_threshold
        high_monotony_gap.low_excessive_threshold = high_monotony_gap_low.low_excessive_threshold
        high_monotony_gap.high_excessive_threshold = high_monotony_gap_high.low_excessive_threshold

        #low_monotony_gap.training_level = None
        #high_monotony_gap.training_level = None

        return low_monotony_gap, high_monotony_gap

    def rank_standard_error_range_metrics(self, metrics_list):

        gaps = []
        monotony_gaps = []

        for m in metrics_list:
            for t in m.training_volume_gaps:
                if t.training_volume_gap_type is not TrainingVolumeGapType.monotony:
                    gaps.append(t)
                else:
                    monotony_gaps.append(t)

        opt_low_values = []
        opt_high_values = []
        ovr_low_values = []
        ovr_high_values = []
        exc_low_values = []
        exc_high_values = []

        opt_low_values.extend(list(g for g in gaps if g.low_optimal_threshold is not None))
        opt_low_values.sort(key=lambda x: x.low_optimal_threshold, reverse=False)

        opt_high_values.extend(list(g for g in gaps if g.high_optimal_threshold is not None))
        opt_high_values.sort(key=lambda x: x.high_optimal_threshold, reverse=False)

        ovr_low_values.extend(list(g for g in gaps if g.low_overreaching_threshold is not None))
        ovr_low_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)

        ovr_high_values.extend(list(g for g in gaps if g.high_overreaching_threshold is not None))
        ovr_high_values.sort(key=lambda x: x.high_overreaching_threshold, reverse=False)

        exc_low_values.extend(list(g for g in gaps if g.low_excessive_threshold is not None))
        exc_low_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)

        exc_high_values.extend(list(g for g in gaps if g.high_excessive_threshold is not None))
        exc_high_values.sort(key=lambda x: x.high_excessive_threshold, reverse=False)

        '''reconcile this and make it work
        # this number needs to be consistent with monotony.  Should we use the low or high?
        if high_monotony_gap.low_overreaching_threshold is not None and ovr_values[0].low_overreaching_threshold < high_monotony_gap.low_overreaching_threshold:
            ovr_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony

        else:
            if high_monotony_gap.low_overreaching_threshold is not None:
                ovr_values.append(high_monotony_gap)

        # this number needs to be consistent with monotony.  Should we use the low or high?
        if high_monotony_gap.low_excessive_threshold is not None and exc_values[0].low_excessive_threshold < high_monotony_gap.low_excessive_threshold:
            exc_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony
        else:
            if high_monotony_gap.low_excessive_threshold is not None:
                exc_values.append(high_monotony_gap)

        # re-sort
        ovr_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)
        exc_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)
        '''

        low_optimal = None
        high_optimal = None
        low_overreaching = None
        high_overreaching = None
        low_excessive = None
        high_excessive = None

        if len(opt_low_values) > 0:
            low_optimal = opt_low_values[0].low_optimal_threshold

        if len(opt_high_values) > 0:
            high_optimal = opt_high_values[0].high_optimal_threshold

        if len(ovr_low_values) > 0:
            low_overreaching = ovr_low_values[0].low_overreaching_threshold

        if len(ovr_high_values) > 0:
            high_overreaching = ovr_high_values[0].high_overreaching_threshold

        if len(exc_low_values) > 0:
            low_excessive = exc_low_values[0].low_excessive_threshold

        if len(exc_high_values) > 0:
            high_excessive = exc_high_values[0].high_excessive_threshold

        j=0

    def compile_training_report(self, user_id, date_time, gap_list, low_monotony_gap, high_monotony_gap):

        #min_values = []
        #max_values = []
        opt_values = []
        opt_high_values = []
        ovr_values = []
        ovr_high_values = []
        exc_values = []
        exc_high_values = []

        # we want the lowest high threshold
        #max_values.extend(list(g for g in gap_list if g.high_threshold is not None))
        #max_values.sort(key=lambda x: x.high_threshold, reverse=False)

        opt_values.extend(list(g for g in gap_list if g.low_optimal_threshold is not None))
        opt_values.sort(key=lambda x: x.low_optimal_threshold, reverse=False)

        opt_high_values.extend(list(g for g in gap_list if g.high_optimal_threshold is not None))
        opt_high_values.sort(key=lambda x: x.high_optimal_threshold, reverse=False)

        ovr_values.extend(list(g for g in gap_list if g.low_overreaching_threshold is not None))
        ovr_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)

        ovr_high_values.extend(list(g for g in gap_list if g.high_overreaching_threshold is not None))
        ovr_high_values.sort(key=lambda x: x.high_overreaching_threshold, reverse=False)

        exc_values.extend(list(g for g in gap_list if g.low_excessive_threshold is not None))
        exc_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)

        exc_high_values.extend(list(g for g in gap_list if g.high_excessive_threshold is not None))
        exc_high_values.sort(key=lambda x: x.high_excessive_threshold, reverse=False)

        # this number needs to be consistent with monotony.  Should we use the low or high?
        if high_monotony_gap.low_overreaching_threshold is not None and ovr_values[0].low_overreaching_threshold < high_monotony_gap.low_overreaching_threshold:
            ovr_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony

        else:
            if high_monotony_gap.low_overreaching_threshold is not None:
                ovr_values.append(high_monotony_gap)

        # this number needs to be consistent with monotony.  Should we use the low or high?
        if high_monotony_gap.low_excessive_threshold is not None and exc_values[0].low_excessive_threshold < high_monotony_gap.low_excessive_threshold:
            exc_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony
        else:
            if high_monotony_gap.low_excessive_threshold is not None:
                exc_values.append(high_monotony_gap)

        # re-sort
        ovr_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)
        exc_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)

        #high_threshold_gap = max_values[0]

        #min_values.extend(list(g for g in gap_list if g.low_threshold is not None and g.low_threshold < high_threshold_gap.high_threshold))

        #min_values.sort(key=lambda x: x.low_threshold,
        #                reverse=True)  # I think we want the highest min value for the tightest band that is lower than the high_threshold

        #if len(min_values) > 0:
            # we want the highest low threshold
        #    low_threshold_gap = min_values[0]
        #else:
        #    low_threshold_gap = max_values[0]

        #report = TrainingReport(user_id, low_threshold_gap.low_threshold, max(0, high_threshold_gap.high_threshold))
        training_day = SuggestedTrainingDay(user_id, date_time, opt_values[0].low_optimal_threshold,
                                            ovr_values[0].low_overreaching_threshold,
                                            exc_values[0].low_excessive_threshold)
        training_day.high_optimal_threshold = opt_high_values[0].high_optimal_threshold
        training_day.high_overreaching_threshold = ovr_high_values[0].high_overreaching_threshold
        training_day.high_excessive_threshold = exc_high_values[0].high_excessive_threshold
        training_day.low_optimal_gap_type = opt_values[0].training_volume_gap_type
        training_day.low_overreaching_gap_type = ovr_values[0].training_volume_gap_type
        training_day.low_excessive_gap_type = exc_values[0].training_volume_gap_type
        training_day.high_optimal_gap_type = opt_high_values[0].training_volume_gap_type
        training_day.high_overreaching_gap_type = ovr_high_values[0].training_volume_gap_type
        training_day.high_excessive_gap_type = exc_high_values[0].training_volume_gap_type
        training_day.training_volume_gaps_opt = opt_values
        training_day.training_volume_gaps_ovr = ovr_values
        training_day.training_volume_gaps_exc = exc_values
        training_day.training_volume_gaps_opt_high = opt_high_values
        training_day.training_volume_gaps_ovr_high = ovr_high_values
        training_day.training_volume_gaps_exc_high = exc_high_values

        #report.training_level = TrainingLevel(max(low_threshold_gap.training_level if low_threshold_gap.training_level is not None else 0,
        #                                                       high_threshold_gap.training_level if high_threshold_gap.training_level is not None else 0))

        return training_day


    def get_strain_gap(self, historical_strain_values, monotony):

        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.strain)

        if len(historical_strain_values) > 0:

            strain_count = min(7, len(list(x for x in historical_strain_values if x is not None)))

            if strain_count > 1:
                strain_sd = statistics.stdev(
                    list(x for x in historical_strain_values[-strain_count:] if x is not None))
                strain_avg = statistics.mean(
                    list(x for x in historical_strain_values[-strain_count:] if x is not None))

                if historical_strain_values[len(
                        historical_strain_values) - 1] is not None and monotony is not None and monotony > 0:

                    strain_sd_load = strain_sd / monotony
                    strain_avg_load = strain_avg / monotony
                    training_volume_gap.high_optimal_threshold = strain_avg_load + strain_sd_load

        return training_volume_gap

    def get_strain_gap_old(self, historical_internal_strain, last_7_internal_load_values, weekly_expected_workouts=5):

        strain_count = min(7, len(historical_internal_strain))
        training_volume_gap = TrainingVolumeGap(gap_type=TrainingVolumeGapType.strain)
        max_load = None
        max_load_upper = None

        internal_strain_sd = 0
        internal_strain_avg = 0

        internal_strain_sd_upper = 0
        internal_strain_avg_upper = 0

        internal_monotony, internal_strain = self.calc_monotony_strain(last_7_internal_load_values)
        internal_monotony_upper, internal_strain_upper = self.calc_monotony_strain_se(last_7_internal_load_values, weekly_expected_workouts)

        if strain_count > 1:
            internal_strain_sd = statistics.stdev(list(x.observed_value for x in historical_internal_strain[-strain_count:]))
            internal_strain_avg = statistics.mean(list(x.observed_value for x in historical_internal_strain[-strain_count:]))
            if len(list(x.upper_bound for x in historical_internal_strain[-strain_count:] if x.upper_bound is not None)) > 0:
                internal_strain_sd_upper = statistics.stdev(list(x.upper_bound for x in historical_internal_strain[-strain_count:] if x.upper_bound is not None))
                internal_strain_avg_upper = statistics.mean(list(x.upper_bound for x in historical_internal_strain[-strain_count:] if x.upper_bound is not None))

            # not guaranteed internal_strain has a value today
            if historical_internal_strain[len(historical_internal_strain)-1] is not None and internal_monotony is not None and internal_monotony > 0:

                #strain_surplus = historical_internal_strain[len(historical_internal_strain)-1] - (1.2 * internal_strain_sd) - internal_strain_avg
                #load_change = strain_surplus / internal_monotony

                internal_strain_sd_load = internal_strain_sd / internal_monotony
                internal_strain_avg_load = internal_strain_avg / internal_monotony
                max_load = internal_strain_avg_load + internal_strain_sd_load

                # 1.2 * internal_strain_sd = athlete_stats.internal_strain - x
                # 1.2 * internal_strain_sd - athlete_stats.internal_strain =  - x
                # (-1) * (1.2 * internal_strain_sd - athlete_stats.internal_strain =  - x)

                # add/reduce this load from day 7 so the forecast load will reduce the strain; not perfect but close
                #strain_gap = max(0, last_7_internal_load_values[0] - load_change)

            if historical_internal_strain[len(historical_internal_strain)-1] is not None and internal_monotony_upper is not None and internal_monotony_upper > 0:

                internal_strain_sd_load_upper = internal_strain_sd_upper / internal_monotony_upper
                internal_strain_avg_load_upper = internal_strain_avg_upper / internal_monotony_upper
                max_load_upper = internal_strain_avg_load_upper + internal_strain_sd_load_upper

            training_volume_gap.training_volume_gap_type = TrainingVolumeGapType.strain

        # review the last week of strain and determine and count how many strain spikes occurred

        strain_events = 0
        strain_events_upper = 0

        for s in range(8, 15):
            hist_strain_count = min(s, len(historical_internal_strain))

            if hist_strain_count >= (s + 1):
                start_index = -len(historical_internal_strain) - (s + 1)
                end_index = start_index + 7
                if len(list(x.observed_value for x in historical_internal_strain[-strain_count:])) > 0:
                    internal_strain_sd = statistics.stdev(list(x.observed_value for x in historical_internal_strain[-strain_count:]))
                    internal_strain_avg = statistics.mean(list(x.observed_value for x in historical_internal_strain[-strain_count:]))

                    current_strain = historical_internal_strain[end_index].observed_value

                    if (current_strain - internal_strain_avg) / internal_strain_sd > 1.2:
                        strain_events += 1

                if len(list(x.upper_bound for x in historical_internal_strain[-strain_count:])) > 0:
                    internal_strain_sd_upper = statistics.stdev(
                        list(x.upper_bound for x in historical_internal_strain[-strain_count:]))
                    internal_strain_avg_upper = statistics.mean(
                        list(x.upper_bound for x in historical_internal_strain[-strain_count:]))

                    current_strain_upper = historical_internal_strain[end_index].upper_bound

                    if (current_strain_upper - internal_strain_avg_upper) / internal_strain_sd_upper > 1.2:
                        strain_events_upper += 1

        if strain_events >= 1:
            training_volume_gap.low_excessive_threshold = max_load
            training_volume_gap.low_overreaching_threshold = None
        else:
            training_volume_gap.low_overreaching_threshold = max_load
            training_volume_gap.low_excessive_threshold = None

        if strain_events_upper >= 1:
            training_volume_gap.high_excessive_threshold = max_load_upper
            training_volume_gap.high_overreaching_threshold = None
        else:
            training_volume_gap.high_overreaching_threshold = max_load_upper
            training_volume_gap.high_excessive_threshold = None

        training_volume_gap.low_optimal_threshold = None

        return training_volume_gap
