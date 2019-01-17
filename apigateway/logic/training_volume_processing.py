from models.training_volume import IndicatorLevel, TrainingLevel, TrainingVolumeGap, TrainingVolumeGapType, TrainingReport
from datetime import datetime, timedelta
import statistics
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

        if len(last_week_internal_values) > 1:
            average_load = statistics.mean(last_week_internal_values)
            stdev_load = statistics.stdev(last_week_internal_values)
            if stdev_load > 0:
                athlete_stats.internal_monotony = average_load / stdev_load
                athlete_stats.internal_strain = athlete_stats.internal_monotony * sum(last_week_internal_values)

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

        if athlete_stats.acute_external_total_load is not None and athlete_stats.chronic_external_total_load is not None:
            if athlete_stats.chronic_external_total_load > 0:
                athlete_stats.external_acwr = athlete_stats.acute_external_total_load / athlete_stats.chronic_external_total_load

        athlete_stats.historical_internal_strain = self.get_historical_internal_strain(self.start_date,
                                                                                       self.end_date,
                                                                                       acute_daily_plans,
                                                                                       chronic_daily_plans)

        return athlete_stats

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

        values = list(getattr(c, attribute_name) for c in session_collection if getattr(c, attribute_name) is not None)
        return values

    def get_product_of_session_attributes(self, attribute_1_name, attribute_2_name, session_collection):

        values = list(getattr(c, attribute_1_name) * getattr(c, attribute_2_name) for c in session_collection
                      if getattr(c, attribute_1_name) is not None and getattr(c, attribute_2_name) is not None)
        return values

    def get_historical_internal_strain(self, start_date, end_date, acute_daily_plans, chronic_daily_plans):

        target_dates = []

        all_plans = []
        all_plans.extend(chronic_daily_plans)
        all_plans.extend(acute_daily_plans)

        all_plans.sort(key=lambda x: x.event_date)

        date_diff = parse_date(end_date) - parse_date(start_date)

        for i in range(1, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        strain_values = []

        index = 0
        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_plans = [p for p in all_plans if (parse_date(start_date) + timedelta(index)) < p.get_event_datetime() <= target_dates[t]]
                load_values.extend(
                    x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                            daily_plans) if x is not None)
                if len(load_values) > 1:
                    current_load = sum(load_values)
                    average_load = statistics.mean(load_values)
                    stdev_load = statistics.stdev(load_values)
                    if stdev_load > 0:
                        internal_monotony = average_load / stdev_load
                        internal_strain = internal_monotony * current_load
                        strain_values.append(internal_strain)
                index += 1

        return strain_values

    def get_ramp_gap(self, current_load, previous_load):
        if previous_load > 0:
            #ramp = ((current_load - previous_load) / float(previous_load))
            ramp = current_load / float(previous_load)
        else:
            ramp = 0

        if ramp > 1.1:
            low_load = 0.0
            high_load = 0.0
        else:
            #1.0 = current_load / previous_load
            #1.1* previous_load = current_load + gap
            #low_load = (1.0 * previous_load) + previous_load - current_load
            low_load = previous_load - current_load
            high_load = (1.1 * previous_load) - current_load

        training_volume_gap = TrainingVolumeGap(low_load, high_load, TrainingVolumeGapType.ramp)

        if ramp < 1:
            training_volume_gap.training_level = TrainingLevel.undertraining
        elif 1 <= ramp < 1.1:
            training_volume_gap.training_level = TrainingLevel.optimal
        elif 1.1 <= ramp < 1.15:
            training_volume_gap.training_level = TrainingLevel.overreaching
        elif ramp >= 1.15:
            training_volume_gap.training_level = TrainingLevel.excessive

        return training_volume_gap

    def get_acwr_gap(self, acute_start_date_time, chronic_start_date_time, acute_daily_plans, chronic_daily_plans):

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

        new_acute_start_date_time = acute_start_date_time + timedelta(days=1)
        new_chronic_start_date_time = chronic_start_date_time + timedelta(days=1)
        new_acute_daily_plans = sorted([p for p in daily_plans if p.get_event_datetime() >=
                                        new_acute_start_date_time], key=lambda x: x.event_date)

        new_chronic_daily_plans = sorted([p for p in daily_plans if new_acute_start_date_time >
                                          p.get_event_datetime() >= new_chronic_start_date_time],
                                         key=lambda x: x.event_date)
        acute_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                    new_acute_daily_plans) if x is not None)

        chronic_values = []

        if acute_days == 7 and chronic_days == 28:

            week4_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=28) <=
                              d.get_event_datetime() < new_acute_start_date_time - timedelta(days=21)]

            chronic_4_values.extend(
                x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                        week4_sessions) if x is not None)
            chronic_values.append(sum(chronic_4_values))

        if acute_days == 7 and 21 <= chronic_days <= 28:

            week3_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time
                              - timedelta(days=21) <= d.get_event_datetime() < new_acute_start_date_time -
                              timedelta(days=14)]

            chronic_3_values.extend(
                x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                        week3_sessions) if x is not None)
            chronic_values.append(sum(chronic_3_values))

        if acute_days == 7 and 14 <= chronic_days <= 28:

            week2_sessions = [d for d in chronic_daily_plans if new_acute_start_date_time
                              - timedelta(days=14) <= d.get_event_datetime() < new_acute_start_date_time -
                              timedelta(days=7)]

            chronic_2_values.extend(
                x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                        week2_sessions) if x is not None)
            chronic_values.append(sum(chronic_2_values))

        if acute_days <= 7 and 7 <= chronic_days <= 28:

            week1_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time
                              - timedelta(days=7) <= d.get_event_datetime() < new_acute_start_date_time]

            chronic_1_values.extend(
                x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                        week1_sessions) if x is not None)

            chronic_values.append(sum(chronic_1_values))

        chronic_value = 0
        if len(chronic_values) > 0:
            chronic_value = statistics.mean(chronic_values)
        acute_value = 0
        if len(acute_values) > 0:
            acute_value = sum(acute_values)

        # ideal is 0.8 to 1.3 with 1.3 being ideal
        # low_difference = 0.8 = (acute_value + x) / chronic_value
        # 0.8 * chronic_value = acute_value + x
        # (0.8 * chronic_value) - acute_value = x

        low_target = (0.8 * chronic_value) - acute_value
        high_target = (1.3 * chronic_value) - acute_value

        training_volume_gap = TrainingVolumeGap(low_target, high_target, TrainingVolumeGapType.acwr)
        if chronic_value > 0:
            training_volume_gap.internal_acwr = acute_value / chronic_value
        else:
            training_volume_gap.internal_acwr = 0

        training_volume_gap.internal_freshness_index = chronic_value - acute_value
        training_volume_gap.competition_focused = (training_volume_gap.internal_freshness_index > 0)
        training_volume_gap.performance_focused = (training_volume_gap.internal_freshness_index <= 0)

        if chronic_value > 0:
            if acute_value / chronic_value < 0.8:
                training_volume_gap.training_level = TrainingLevel.undertraining
            elif 0.8 <= acute_value / chronic_value <= 1.3:
                training_volume_gap.training_level = TrainingLevel.optimal
            elif 1.3 < acute_value / chronic_value <= 1.5:
                training_volume_gap.training_level = TrainingLevel.overreaching
            elif acute_value / chronic_value > 1.5:
                training_volume_gap.training_level = TrainingLevel.excessive

        return training_volume_gap

    def get_training_report(self, athlete_stats, last_7_days_plans, days_8_14_plans, acute_start_date_time, chronic_start_date_time, acute_plans, chronic_plans, end_date_time):

        last_6_internal_load_values = []
        last_7_internal_load_values = []
        last_7_13_internal_load_values = []

        last_six_days = end_date_time - timedelta(days=6 + 1)
        thirteen_days_ago = last_six_days - timedelta(days=7)

        last_6_day_plans = [p for p in last_7_days_plans if p.get_event_datetime() >= last_six_days]
        last_7_day_plans = last_7_days_plans
        last_7_day_plans.sort(key=lambda x: x.event_date, reverse=False)
        last_7_13_day_plans = [p for p in last_7_days_plans if p.get_event_datetime() < last_six_days]
        last_7_13_day_plans.extend([p for p in days_8_14_plans if p.get_event_datetime() >= thirteen_days_ago])

        last_6_internal_load_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                    last_6_day_plans) if x is not None)

        last_7_internal_load_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                    last_7_day_plans) if x is not None)

        last_7_13_internal_load_values.extend(
            x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                    last_7_13_day_plans) if x is not None)

        current_load = sum(last_6_internal_load_values)
        previous_load = sum(last_7_13_internal_load_values)

        ramp_gap = self.get_ramp_gap(current_load, previous_load)

        low_monotony_gap, high_monotony_gap,  = self.get_monotony_gap(last_6_internal_load_values)

        strain_gap = self.get_strain_gap(athlete_stats, low_monotony_gap.internal_monotony_index, last_7_internal_load_values)

        acwr_gap = self.get_acwr_gap(acute_start_date_time, chronic_start_date_time, acute_plans, chronic_plans)

        gap_list = [ramp_gap, strain_gap, acwr_gap]

        report = self.compile_training_report(athlete_stats.athlete_id, gap_list, low_monotony_gap, high_monotony_gap)

        report.internal_monotony_index = high_monotony_gap.internal_monotony_index
        report.internal_freshness_index = acwr_gap.internal_freshness_index
        report.internal_acwr = acwr_gap.internal_acwr
        report.performance_focused = acwr_gap.performance_focused
        report.competition_focused = acwr_gap.competition_focused
        report.internal_strain = athlete_stats.internal_strain
        report.internal_ramp = athlete_stats.internal_ramp
        report.need_for_variability = high_monotony_gap.need_for_variability
        return report

    def get_monotony_gap(self, last_6_internal_load_values):

        # what is the monotony if we have a workout with this load?
        average_load = 0
        if len(last_6_internal_load_values) > 0:
            average_load = statistics.mean(last_6_internal_load_values)

        stdev_load = 0
        if len(last_6_internal_load_values) > 1:
            stdev_load = statistics.stdev(last_6_internal_load_values)

        if stdev_load > 0:
            internal_monotony = average_load / stdev_load
        else:
            internal_monotony = 0
        # monotony = weekly mean total load/weekly standard deviation of load
        # In order to increase the standard deviation of a set of numbers, you must add a value that is more than
        # one standard deviation away from the mean
        low_monotony_fix = 0
        high_monotony_fix = 0
        if internal_monotony >= 1.7: # bumped it down from 2 just for safe measure
            low_monotony_fix = average_load - (1.05 * stdev_load)
            high_monotony_fix = average_load + (1.05 * stdev_load)
        low_monotony_gap = TrainingVolumeGap(0, low_monotony_fix, TrainingVolumeGapType.monotony)
        high_monotony_gap = TrainingVolumeGap(high_monotony_fix, None, TrainingVolumeGapType.monotony)
        if internal_monotony > 2:
            low_monotony_gap.need_for_variability = IndicatorLevel.high
            high_monotony_gap.need_for_variability = IndicatorLevel.high
            low_monotony_gap.training_level = TrainingLevel.overreaching
            high_monotony_gap.training_level = TrainingLevel.overreaching
        elif 1.3 < internal_monotony <= 2:
            low_monotony_gap.need_for_variability = IndicatorLevel.moderate
            high_monotony_gap.need_for_variability = IndicatorLevel.moderate
        elif internal_monotony <= 1.3:
            low_monotony_gap.need_for_variability = IndicatorLevel.low
            high_monotony_gap.need_for_variability = IndicatorLevel.low

        low_monotony_gap.internal_monotony_index = internal_monotony
        high_monotony_gap.internal_monotony_index = internal_monotony

        return low_monotony_gap, high_monotony_gap

    def compile_training_report(self, user_id, gap_list, low_monotony_gap, high_monotony_gap):

        min_values = []
        max_values = []

        # we want the lowest high threshold
        max_values.extend(list(g for g in gap_list if g.high_threshold is not None))
        max_values.sort(key=lambda x: x.high_threshold, reverse=False)

        # this number needs to be consistent with monotony.  Should we use the low or high?
        if max_values[0].high_threshold < high_monotony_gap.low_threshold:
            max_values.append(low_monotony_gap)  # go with low monotony option since best option could create monotony
            min_values.append(low_monotony_gap)
        else:
            #max_values.append(high_monotony_gap)  this will usuall be None
            min_values.append(high_monotony_gap)

        # re-sort
        max_values.sort(key=lambda x: x.high_threshold, reverse=False)

        high_threshold_gap = max_values[0]

        min_values.extend(list(g for g in gap_list if g.low_threshold is not None and g.low_threshold < high_threshold_gap.high_threshold))

        min_values.sort(key=lambda x: x.low_threshold,
                        reverse=True)  # I think we want the highest min value for the tightest band that is lower than the high_threshold

        if len(min_values) > 0:
            # we want the highest low threshold
            low_threshold_gap = min_values[0]
        else:
            low_threshold_gap = max_values[0]

        report = TrainingReport(user_id, low_threshold_gap.low_threshold, max(0, high_threshold_gap.high_threshold))

        report.most_limiting_gap_type_low = low_threshold_gap.training_volume_gap_type
        report.most_limiting_gap_type_high = high_threshold_gap.training_volume_gap_type
        report.training_volume_gaps = max_values
        report.training_level = TrainingLevel(max(low_threshold_gap.training_level if low_threshold_gap.training_level is not None else 0,
                                                               high_threshold_gap.training_level if high_threshold_gap.training_level is not None else 0))

        return report

    def get_strain_gap(self, athlete_stats, internal_monotony, last_7_internal_load_values):

        strain_count = min(7, len(athlete_stats.historical_internal_strain))
        training_volume_gap = TrainingVolumeGap()

        if strain_count > 1:
            internal_strain_sd = statistics.stdev(athlete_stats.historical_internal_strain[-strain_count:])
            internal_strain_avg = statistics.mean(athlete_stats.historical_internal_strain[-strain_count:])

            # not guaranteed internal_strain has a value today
            if athlete_stats.internal_strain is not None and internal_monotony is not None and internal_monotony > 0:

                strain_surplus = athlete_stats.internal_strain - (1.2 * internal_strain_sd) - internal_strain_avg
                load_change = strain_surplus / internal_monotony

                # 1.2 * internal_strain_sd = athlete_stats.internal_strain - x
                # 1.2 * internal_strain_sd - athlete_stats.internal_strain =  - x
                # (-1) * (1.2 * internal_strain_sd - athlete_stats.internal_strain =  - x)

                # add/reduce this load from day 7 so the forecast load will reduce the strain; not perfect but close
                strain_gap = max(0, last_7_internal_load_values[0] - load_change)
            else:
                strain_gap = None
            training_volume_gap.low_threshold = 0
            training_volume_gap.high_threshold = strain_gap
            training_volume_gap.training_volume_gap_type = TrainingVolumeGapType.strain

        # review the last week of strain and determine and count how many strain spikes occurred

        strain_events = 0

        for s in range(8, 15):
            hist_strain_count = min(s, len(athlete_stats.historical_internal_strain))

            if hist_strain_count >= (s + 1):
                start_index = -len(athlete_stats.historical_internal_strain) - (s + 1)
                end_index = start_index + 7
                internal_strain_sd = statistics.stdev(athlete_stats.historical_internal_strain[start_index:end_index])
                internal_strain_avg = statistics.mean(athlete_stats.historical_internal_strain[start_index:end_index])

                current_strain = athlete_stats.historical_internal_strain[end_index]

                if (current_strain - internal_strain_avg) / internal_strain_sd > 1.2:
                    strain_events += 1

        if strain_events == 0:
            training_volume_gap.training_level = TrainingLevel.optimal
        elif strain_events == 1:
            training_volume_gap.training_level = TrainingLevel.overreaching
        elif strain_events > 1:
            training_volume_gap.training_level = TrainingLevel.excessive

        return training_volume_gap
