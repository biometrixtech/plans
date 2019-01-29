from models.training_volume import IndicatorLevel, StandardErrorRange, SuggestedTrainingDay, TrainingLevel, TrainingVolumeGap, TrainingVolumeGapType, TrainingReport
from models.soreness import HistoricSorenessStatus
from datetime import datetime, timedelta
import statistics, math
from utils import parse_date, parse_datetime, format_date


class TrainingVolumeProcessing(object):
    def __init__(self, start_date, end_date):
        self.start_date = start_date
        self.end_date = end_date

    def calc_training_volume_metrics(self, athlete_stats, last_7_days_plans, days_8_14_plans, acute_daily_plans, chronic_weeks_plans, chronic_daily_plans):

        a_internal_load_values = []
        a_external_load_values = []
        a_high_intensity_values = []
        a_mod_intensity_values = []
        a_low_intensity_values = []

        c_internal_load_values = []
        c_external_load_values = []
        c_high_intensity_values = []
        c_mod_intensity_values = []
        c_low_intensity_values = []

        last_week_external_values = []
        previous_week_external_values = []
        last_week_internal_values = []
        previous_week_internal_values = []

        last_week_external_values.extend(
            x for x in self.get_plan_session_attribute_sum_list("external_load", last_7_days_plans) if x is not None)

        last_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                               last_7_days_plans) if x is not None)
        previous_week_external_values.extend(
            x for x in self.get_plan_session_attribute_sum_list("external_load", days_8_14_plans) if x is not None)

        previous_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                               days_8_14_plans) if x is not None)

        a_external_load_values.extend(
            x for x in self.get_plan_session_attribute_sum("external_load", acute_daily_plans) if x is not None)


        a_internal_load_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               acute_daily_plans) if x is not None)

        a_external_load_values.extend(
            x for x in self.get_plan_session_attribute_sum("external_load", acute_daily_plans) if x is not None)

        a_high_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("high_intensity_load", acute_daily_plans) if
            x is not None)

        a_mod_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("mod_intensity_load", acute_daily_plans) if
            x is not None)

        a_low_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("low_intensity_load", acute_daily_plans) if
            x is not None)

        for w in chronic_weeks_plans:

            c_internal_load_values.extend(
                x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes", w)
                if x is not None)

            c_external_load_values.extend(x for x in self.get_plan_session_attribute_sum("external_load", w) if x is not None)

            c_high_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("high_intensity_load", w)
                                           if x is not None)

            c_mod_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("mod_intensity_load", w)
                                          if x is not None)

            c_low_intensity_values.extend(x for x in self.get_plan_session_attribute_sum("low_intensity_load", w)
                                          if x is not None)

        if len(last_week_external_values) > 0 and len(previous_week_external_values) > 0:
            current_load = sum(last_week_external_values)
            previous_load = sum(previous_week_external_values)
            if previous_load > 0:
                #athlete_stats.external_ramp = ((current_load - previous_load) / previous_load) * 100
                athlete_stats.external_ramp = current_load / previous_load

        if len(last_week_internal_values) > 0 and len(previous_week_internal_values) > 0:
            current_load = sum(last_week_internal_values)
            previous_load = sum(previous_week_internal_values)
            if previous_load > 0:
                #athlete_stats.internal_ramp = ((current_load - previous_load) / previous_load) * 100
                athlete_stats.internal_ramp = current_load / previous_load

        if len(last_week_external_values) > 1:
            average_load = statistics.mean(last_week_external_values)
            stdev_load = statistics.stdev(last_week_external_values)
            if stdev_load > 0:
                athlete_stats.external_monotony = average_load / stdev_load
                athlete_stats.external_strain = athlete_stats.external_monotony * sum(last_week_external_values)

        monotony, strain = self.calc_monotony_strain(last_week_internal_values)
        athlete_stats.internal_monotony = monotony
        athlete_stats.internal_strain = strain

        if len(a_internal_load_values) > 0:
            athlete_stats.acute_internal_total_load = sum(a_internal_load_values)

        if len(a_external_load_values) > 0:
            athlete_stats.acute_external_total_load = sum(a_external_load_values)
        if len(a_high_intensity_values) > 0:
            athlete_stats.acute_external_high_intensity_load = sum(a_high_intensity_values)
        if len(a_mod_intensity_values) > 0:
            athlete_stats.acute_external_mod_intensity_load = sum(a_mod_intensity_values)
        if len(a_low_intensity_values) > 0:
            athlete_stats.acute_external_low_intensity_load = sum(a_low_intensity_values)

        if len(c_internal_load_values) > 0:
            athlete_stats.chronic_internal_total_load = statistics.mean(c_internal_load_values)

        if len(c_external_load_values) > 0:
            athlete_stats.chronic_external_total_load = statistics.mean(c_external_load_values)
        if len(c_high_intensity_values) > 0:
            athlete_stats.chronic_external_high_intensity_load = statistics.mean(c_high_intensity_values)
        if len(c_mod_intensity_values) > 0:
            athlete_stats.chronic_external_mod_intensity_load = statistics.mean(c_mod_intensity_values)
        if len(c_low_intensity_values) > 0:
            athlete_stats.chronic_external_low_intensity_load = statistics.mean(c_low_intensity_values)

        if athlete_stats.acute_internal_total_load is not None and athlete_stats.chronic_internal_total_load is not None:
            if athlete_stats.chronic_internal_total_load > 0:
                athlete_stats.internal_acwr = athlete_stats.acute_internal_total_load / athlete_stats.chronic_internal_total_load
                athlete_stats.internal_freshness_index = athlete_stats.chronic_internal_total_load - athlete_stats.acute_internal_total_load

        if athlete_stats.acute_external_total_load is not None and athlete_stats.chronic_external_total_load is not None:
            if athlete_stats.chronic_external_total_load > 0:
                athlete_stats.external_acwr = athlete_stats.acute_external_total_load / athlete_stats.chronic_external_total_load
                athlete_stats.external_freshness_index = athlete_stats.chronic_external_total_load - athlete_stats.acute_external_total_load

        all_plans = []
        all_plans.extend(chronic_daily_plans)
        all_plans.extend(acute_daily_plans)

        athlete_stats.historical_internal_strain = self.get_historical_internal_strain(self.start_date,
                                                                                       self.end_date,
                                                                                       all_plans)

        return athlete_stats

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

    def get_historical_internal_strain(self, start_date, end_date, all_plans, weekly_expected_workouts=5):

        target_dates = []

        all_plans.sort(key=lambda x: x.event_date)

        date_diff = parse_date(end_date) - parse_date(start_date)

        for i in range(1, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        index = 0
        strain_values = []

        # evaluates a rolling week's worth of values for each day to calculate "daily" strain
        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_plans = [p for p in all_plans if (parse_date(start_date) + timedelta(index)) < p.get_event_datetime() <= target_dates[t]]
                load_values.extend(
                    x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                            daily_plans) if x is not None)
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

    def get_ramp_gap(self, current_load_values, previous_load_values, avg_workouts_week=5):

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
        training_volume_gap.high_optimal_threshold = previous_load - current_load
        training_volume_gap.low_overreaching_threshold = (1.11 * previous_load) - current_load
        training_volume_gap.high_overreaching_threshold = (1.11 * previous_load) - current_load
        training_volume_gap.low_excessive_threshold = (1.16 * previous_load) - current_load
        training_volume_gap.high_excessive_threshold = (1.16 * previous_load) - current_load
        if previous_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load_high - current_load)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                            previous_load_high - current_load)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load_high) - current_load)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.11 * previous_load_high) - current_load)
            training_volume_gap.low_excessive_threshold = min(training_volume_gap.low_excessive_threshold,
                                                                 (1.16 * previous_load_high) - current_load)
            training_volume_gap.high_excessive_threshold = max(training_volume_gap.high_excessive_threshold,
                                                                  (1.16 * previous_load_high) - current_load)
        if current_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load - current_load_high)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                            previous_load - current_load_high)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load) - current_load_high)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.11 * previous_load) - current_load_high)
            training_volume_gap.low_excessive_threshold = min(training_volume_gap.low_excessive_threshold,
                                                                 (1.16 * previous_load) - current_load_high)
            training_volume_gap.high_excessive_threshold = max(training_volume_gap.high_excessive_threshold,
                                                                  (1.16 * previous_load) - current_load_high)
        if previous_load_high > 0 and current_load_high > 0:
            training_volume_gap.low_optimal_threshold = min(training_volume_gap.low_optimal_threshold,
                                                            previous_load_high - current_load_high)
            training_volume_gap.high_optimal_threshold = max(training_volume_gap.high_optimal_threshold,
                                                            previous_load_high - current_load_high)
            training_volume_gap.low_overreaching_threshold = min(training_volume_gap.low_overreaching_threshold,
                                                                 (1.11 * previous_load_high) - current_load_high)
            training_volume_gap.high_overreaching_threshold = max(training_volume_gap.high_overreaching_threshold,
                                                                  (1.11 * previous_load_high) - current_load_high)
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

    def get_acwr_gap(self, acute_values, chronic_values, chronic_values_high, avg_workouts_week=5):

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

    def get_training_report(self, user_id, acute_start_date_time, chronic_start_date_time, daily_plans, historical_internal_strain,end_date_time, avg_workouts_week=5):

        report = TrainingReport(user_id=user_id)

        #report.internal_monotony_index = athlete_stats.internal_monotony
        #report = self.calc_need_for_variability(athlete_stats.internal_monotony, report)

        suggested_training_days = []

        target_load = 0

        #for index in range(0, 7):
        for index in range(0, 1): # just doing one day now

            chronic_values = []
            chronic_values_high = []
            chronic_1_values = []
            chronic_2_values = []
            chronic_3_values = []
            chronic_4_values = []

            new_acute_start_date_time = acute_start_date_time + timedelta(days=1) + timedelta(days=index)
            new_chronic_start_date_time = chronic_start_date_time + timedelta(days=1) + timedelta(days=index)

            new_acute_daily_plans = sorted([p for p in daily_plans if p[0] >= new_acute_start_date_time],
                                           key=lambda x: x[0])

            acute_values = list(x[1] for x in new_acute_daily_plans if x[1] is not None)

            new_chronic_daily_plans = sorted([p for p in daily_plans if new_acute_start_date_time > p[0] >=
                                              new_chronic_start_date_time], key=lambda x: x[0])

            #if 21 <=chronic_days <= 28:
            week4_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=28)
                              <= d[0] < new_acute_start_date_time - timedelta(days=21)]

            chronic_4_values.extend(x[1] for x in week4_sessions if x[1] is not None)
            if len(chronic_4_values) > 0  or len(chronic_4_values) >= avg_workouts_week:
                chronic_values.append(sum(chronic_4_values))
            if len(chronic_4_values) > 1 and len(chronic_4_values) < avg_workouts_week:
                average_load = statistics.mean(chronic_4_values)
                stdev_load = statistics.stdev(chronic_4_values)
                standard_error = (stdev_load / math.sqrt(len(chronic_4_values))) * math.sqrt(
                    (avg_workouts_week - len(chronic_4_values)) / avg_workouts_week) # includes finite population correction
                standard_error_range_factor = 1.96 * standard_error
                chronic_values_high.append((average_load + standard_error_range_factor)*len(chronic_4_values))

            #if 14 <= chronic_days <= 28:
            week3_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=21)
                              <= d[0] < new_acute_start_date_time - timedelta(days=14)]

            chronic_3_values.extend(x[1] for x in week3_sessions if x[1] is not None)
            if len(chronic_3_values) > 0 or len(chronic_3_values) >= avg_workouts_week:
                chronic_values.append(sum(chronic_3_values))
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if len(chronic_3_values) > 1 and len(chronic_3_values) < avg_workouts_week:
                average_load = statistics.mean(chronic_3_values)
                stdev_load = statistics.stdev(chronic_3_values)
                standard_error = (stdev_load / math.sqrt(len(chronic_3_values))) * math.sqrt(
                    (avg_workouts_week - len(chronic_3_values)) / avg_workouts_week) # includes finite population correction
                standard_error_range_factor = 1.96 * standard_error
                chronic_values_high.append((average_load + standard_error_range_factor)*len(chronic_3_values))
            else:
                if len(chronic_values) > 0:
                    chronic_values_high.append(0)
                    # not sure what to do with low/high here

            #if 7 <= chronic_days <= 28:
            week2_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=14)
                              <= d[0] < new_acute_start_date_time - timedelta(days=7)]

            chronic_2_values.extend(x[1] for x in week2_sessions if x[1] is not None)
            if len(chronic_2_values) > 0  or len(chronic_2_values) >= avg_workouts_week:
                chronic_values.append(sum(chronic_2_values))
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if len(chronic_2_values) > 1 and len(chronic_2_values) < avg_workouts_week:
                average_load = statistics.mean(chronic_2_values)
                stdev_load = statistics.stdev(chronic_2_values)
                standard_error = (stdev_load / math.sqrt(len(chronic_2_values))) * math.sqrt(
                    (avg_workouts_week - len(chronic_2_values)) / avg_workouts_week) # includes finite population correction
                standard_error_range_factor = 1.96 * standard_error
                chronic_values_high.append((average_load + standard_error_range_factor)*len(chronic_2_values))
            else:
                if len(chronic_values) > 0:
                    chronic_values_high.append(0)

            #if 7 <= chronic_days <= 28:
            week1_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=7)
                              <= d[0] < new_acute_start_date_time]

            chronic_1_values.extend(x[1] for x in week1_sessions if x[1] is not None)

            if len(chronic_1_values) > 0 or len(chronic_1_values) >= avg_workouts_week:
                chronic_values.append(sum(chronic_1_values))
            else:
                if len(chronic_values) > 0:
                    chronic_values.append(0)
            if len(chronic_1_values) > 1 and len(chronic_1_values) < avg_workouts_week:
                average_load = statistics.mean(chronic_1_values)
                stdev_load = statistics.stdev(chronic_1_values)
                standard_error = (stdev_load / math.sqrt(len(chronic_1_values))) * math.sqrt(
                    (avg_workouts_week - len(chronic_1_values)) / avg_workouts_week) # includes finite population correction
                standard_error_range_factor = 1.96 * standard_error
                chronic_values_high.append((average_load + standard_error_range_factor)*len(chronic_1_values))
            else:
                if len(chronic_values) > 0:
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

    def get_strain_gap(self, historical_internal_strain, last_7_internal_load_values, weekly_expected_workouts=5):

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
            if len(list(x.upper_bound for x in historical_internal_strain[-strain_count:])) > 0:
                internal_strain_sd_upper = statistics.stdev(list(x.upper_bound for x in historical_internal_strain[-strain_count:]))
                internal_strain_avg_upper = statistics.mean(list(x.upper_bound for x in historical_internal_strain[-strain_count:]))

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
