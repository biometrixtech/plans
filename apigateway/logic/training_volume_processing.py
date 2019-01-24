from models.training_volume import IndicatorLevel, SuggestedTrainingDay, TrainingLevel, TrainingVolumeGap, TrainingVolumeGapType, TrainingReport
from models.soreness import HistoricSorenessStatus
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
                athlete_stats.internal_freshness_index = athlete_stats.chronic_internal_total_load - athlete_stats.acute_internal_total_load

        if athlete_stats.acute_external_total_load is not None and athlete_stats.chronic_external_total_load is not None:
            if athlete_stats.chronic_external_total_load > 0:
                athlete_stats.external_acwr = athlete_stats.acute_external_total_load / athlete_stats.chronic_external_total_load
                athlete_stats.external_freshness_index = athlete_stats.chronic_external_total_load - athlete_stats.acute_external_total_load

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

    def get_historical_internal_strain(self, start_date, end_date, acute_daily_plans, chronic_daily_plans):

        target_dates = []

        all_plans = []
        all_plans.extend(chronic_daily_plans)
        all_plans.extend(acute_daily_plans)

        all_plans.sort(key=lambda x: x.event_date)

        date_diff = parse_date(end_date) - parse_date(start_date)

        for i in range(1, date_diff.days):
            target_dates.append(parse_date(start_date) + timedelta(days=i))

        index = 0
        strain_values = []

        if len(target_dates) > 7:
            for t in range(6, len(target_dates)):
                load_values = []
                daily_plans = [p for p in all_plans if (parse_date(start_date) + timedelta(index)) < p.get_event_datetime() <= target_dates[t]]
                load_values.extend(
                    x for x in self.get_session_attributes_product_sum_list("session_RPE", "duration_minutes",
                                                                            daily_plans) if x is not None)
                strain = self.calculate_daily_strain(load_values)
                if strain is not None:
                    strain_values.append(strain)
                index += 1

        return strain_values

    def calculate_daily_strain(self, load_values):

        internal_strain = None

        if len(load_values) > 1:

            current_load = sum(load_values)
            average_load = statistics.mean(load_values)
            stdev_load = statistics.stdev(load_values)

            if stdev_load > 0:
                internal_monotony = average_load / stdev_load
                internal_strain = internal_monotony * current_load


        return internal_strain

    def get_ramp_gap(self, current_load, previous_load):
        if previous_load > 0:
            #ramp = ((current_load - previous_load) / float(previous_load))
            ramp = current_load / float(previous_load)
        else:
            ramp = 0

        '''deprecated
        if ramp > 1.1:
            low_load = 0.0
            high_load = 0.0
        else:
        '''
        #1.0 = current_load / previous_load
        #1.1* previous_load = current_load + gap
        #low_load = (1.0 * previous_load) + previous_load - current_load
        low_load = previous_load - current_load
        high_load = (1.1 * previous_load) - current_load
        overreaching_load = (1.11 * previous_load) - current_load
        excessive_load = (1.16 * previous_load) - current_load

        training_volume_gap = TrainingVolumeGap(low_load, overreaching_load, excessive_load, TrainingVolumeGapType.ramp)

        if ramp < 1:
            training_volume_gap.training_level = TrainingLevel.undertraining
        elif 1 <= ramp < 1.1:
            training_volume_gap.training_level = TrainingLevel.optimal
        elif 1.1 <= ramp < 1.15:
            training_volume_gap.training_level = TrainingLevel.overreaching
        elif ramp >= 1.15:
            training_volume_gap.training_level = TrainingLevel.excessive

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

    def get_acwr_gap(self, acute_values, chronic_values):

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

        training_volume_gap = TrainingVolumeGap((0.8 * chronic_value) - acute_value,
                                                (1.31 * chronic_value) - acute_value,
                                                (1.51 * chronic_value) - acute_value, TrainingVolumeGapType.acwr)

        return training_volume_gap

    def get_training_report(self, athlete_stats, acute_start_date_time, chronic_start_date_time, acute_plans, chronic_plans, end_date_time):

        report = TrainingReport(user_id=athlete_stats.athlete_id)
        report = self.calc_report_stats(acute_plans, acute_start_date_time, athlete_stats, chronic_plans, report)
        #if report.chronic_avg_duration_minutes is not None and report.chronic_avg_rpe is not None:
        #    target_load = report.chronic_avg_duration_minutes * report.chronic_avg_rpe
        #else:
        #    target_load = 0
        target_load = 0

        report.internal_monotony_index = athlete_stats.internal_monotony
        report = self.calc_need_for_variability(athlete_stats.internal_monotony, report)

        suggested_training_days = []
        historical_internal_strain = athlete_stats.historical_internal_strain
        internal_monotony = athlete_stats.internal_monotony

        acute_days = len(acute_plans)
        chronic_days = len(chronic_plans)

        daily_plans = []
        daily_plans.extend(list(x for x in
                                self.get_session_attributes_product_sum_tuple_list("session_RPE", "duration_minutes",
                                                                                   acute_plans) if x is not None))
        daily_plans.extend(list(x for x in
                                self.get_session_attributes_product_sum_tuple_list("session_RPE", "duration_minutes",
                                                                                   chronic_plans) if x is not None))

        for index in range(0, 7):

            chronic_values = []
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

            if acute_days == 7 and 21 <=chronic_days <= 28:
                week4_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=28)
                                  <= d[0] < new_acute_start_date_time - timedelta(days=21)]

                chronic_4_values.extend(x[1] for x in week4_sessions if x[1] is not None)
                chronic_values.append(sum(chronic_4_values))

            if acute_days == 7 and 14 <= chronic_days <= 28:
                week3_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=21)
                                  <= d[0] < new_acute_start_date_time - timedelta(days=14)]

                chronic_3_values.extend(x[1] for x in week3_sessions if x[1] is not None)
                chronic_values.append(sum(chronic_3_values))

            if acute_days == 7 and 7 <= chronic_days <= 28:
                week2_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=14)
                                  <= d[0] < new_acute_start_date_time - timedelta(days=7)]

                chronic_2_values.extend(x[1] for x in week2_sessions if x[1] is not None)
                chronic_values.append(sum(chronic_2_values))

            if acute_days <= 7 and 7 <= chronic_days <= 28:
                week1_sessions = [d for d in new_chronic_daily_plans if new_acute_start_date_time - timedelta(days=7)
                                  <= d[0] < new_acute_start_date_time]

                chronic_1_values.extend(x[1] for x in week1_sessions if x[1] is not None)

                chronic_values.append(sum(chronic_1_values))

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

            current_load = sum(last_6_internal_load_values)
            previous_load = sum(last_7_13_internal_load_values)
            ramp_load = previous_load
            if len(chronic_values) > 0:
                average_chronic_load = statistics.mean(chronic_values)
                ramp_load = max(average_chronic_load, ramp_load)
            ramp_gap = self.get_ramp_gap(current_load, ramp_load)

            low_monotony_gap, high_monotony_gap,  = self.get_monotony_gap(last_6_internal_load_values)

            strain_gap = self.get_strain_gap(historical_internal_strain, internal_monotony, last_7_internal_load_values)

            acwr_gap = self.get_acwr_gap(acute_values, chronic_values)

            gap_list = [ramp_gap, strain_gap, acwr_gap]

            suggested_training_day = self.compile_training_report(athlete_stats.athlete_id, end_date_time + timedelta(days=index), gap_list, low_monotony_gap, high_monotony_gap)
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
            if chronic_days < 28:
                chronic_days += 1
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
        low_monotony_gap = TrainingVolumeGap(None, low_overreaching_fix, low_excessive_fix, TrainingVolumeGapType.monotony)
        high_monotony_gap = TrainingVolumeGap(None, high_overreaching_fix, high_excessive_fix, TrainingVolumeGapType.monotony)
        #low_monotony_gap.training_level = None
        #high_monotony_gap.training_level = None

        return low_monotony_gap, high_monotony_gap

    def compile_training_report(self, user_id, date_time, gap_list, low_monotony_gap, high_monotony_gap):

        #min_values = []
        #max_values = []
        opt_values = []
        ovr_values = []
        exc_values = []

        # we want the lowest high threshold
        #max_values.extend(list(g for g in gap_list if g.high_threshold is not None))
        #max_values.sort(key=lambda x: x.high_threshold, reverse=False)

        opt_values.extend(list(g for g in gap_list if g.low_optimal_threshold is not None))
        opt_values.sort(key=lambda x: x.low_optimal_threshold, reverse=False)

        ovr_values.extend(list(g for g in gap_list if g.low_overreaching_threshold is not None))
        ovr_values.sort(key=lambda x: x.low_overreaching_threshold, reverse=False)

        exc_values.extend(list(g for g in gap_list if g.low_excessive_threshold is not None))
        exc_values.sort(key=lambda x: x.low_excessive_threshold, reverse=False)

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

        training_day.low_optimal_gap_type = opt_values[0].training_volume_gap_type
        training_day.low_overreaching_gap_type = ovr_values[0].training_volume_gap_type
        training_day.low_excessive_gap_type = exc_values[0].training_volume_gap_type
        training_day.training_volume_gaps = opt_values

        #report.training_level = TrainingLevel(max(low_threshold_gap.training_level if low_threshold_gap.training_level is not None else 0,
        #                                                       high_threshold_gap.training_level if high_threshold_gap.training_level is not None else 0))

        return training_day

    def get_strain_gap(self, historical_internal_strain, internal_monotony, last_7_internal_load_values):

        strain_count = min(7, len(historical_internal_strain))
        training_volume_gap = TrainingVolumeGap()
        max_load = None

        if strain_count > 1:
            internal_strain_sd = statistics.stdev(historical_internal_strain[-strain_count:])
            internal_strain_avg = statistics.mean(historical_internal_strain[-strain_count:])

            # not guaranteed internal_strain has a value today
            if historical_internal_strain[len(historical_internal_strain)-1] is not None and internal_monotony is not None and internal_monotony > 0:

                strain_surplus = historical_internal_strain[len(historical_internal_strain)-1] - (1.2 * internal_strain_sd) - internal_strain_avg
                load_change = strain_surplus / internal_monotony

                internal_strain_sd_load = internal_strain_sd / internal_monotony
                internal_strain_avg_load = internal_strain_avg / internal_monotony
                max_load = internal_strain_avg_load + internal_strain_sd_load

                # 1.2 * internal_strain_sd = athlete_stats.internal_strain - x
                # 1.2 * internal_strain_sd - athlete_stats.internal_strain =  - x
                # (-1) * (1.2 * internal_strain_sd - athlete_stats.internal_strain =  - x)

                # add/reduce this load from day 7 so the forecast load will reduce the strain; not perfect but close
                strain_gap = max(0, last_7_internal_load_values[0] - load_change)

            #else:
            #    strain_gap = None
            #training_volume_gap.low_threshold = 0
            #training_volume_gap.high_threshold = strain_gap
            training_volume_gap.training_volume_gap_type = TrainingVolumeGapType.strain

        # review the last week of strain and determine and count how many strain spikes occurred

        strain_events = 0

        for s in range(8, 15):
            hist_strain_count = min(s, len(historical_internal_strain))

            if hist_strain_count >= (s + 1):
                start_index = -len(historical_internal_strain) - (s + 1)
                end_index = start_index + 7
                internal_strain_sd = statistics.stdev(historical_internal_strain[start_index:end_index])
                internal_strain_avg = statistics.mean(historical_internal_strain[start_index:end_index])

                current_strain = historical_internal_strain[end_index]

                if (current_strain - internal_strain_avg) / internal_strain_sd > 1.2:
                    strain_events += 1

        #if strain_events == 0:
        #    training_volume_gap.training_level = TrainingLevel.optimal
        #elif strain_events == 1:
        #    training_volume_gap.training_level = TrainingLevel.overreaching
        #elif strain_events > 1:
        #    training_volume_gap.training_level = TrainingLevel.excessive

        if strain_events >= 1:
            training_volume_gap.low_excessive_threshold = max_load
            training_volume_gap.low_overreaching_threshold = None
        else:
            training_volume_gap.low_overreaching_threshold = max_load
            training_volume_gap.low_excessive_threshold = None
        training_volume_gap.low_optimal_threshold = None

        return training_volume_gap
