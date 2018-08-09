from models.stats import AthleteStats
from datetime import datetime, timedelta
import statistics
from utils import format_datetime


class StatsProcessing(object):

    def __init__(self, athlete_id, event_date, daily_readiness_datastore, post_session_survey_datastore,
                 daily_plan_datastore, athlete_stats_datastore):
        self.athlete_id = athlete_id
        self.event_date = event_date
        self.daily_readiness_datastore = daily_readiness_datastore
        self.post_session_survey_datastore = post_session_survey_datastore
        self.athlete_stats_datastore = athlete_stats_datastore
        self.daily_plan_datastore = daily_plan_datastore
        # self.start_date = None
        # self.end_date = None
        self.start_date_time = None
        self.end_date_time = None
        self.acute_days = None
        self.chronic_days = None
        self.acute_start_date_time = None
        self.chronic_start_date_time = None
        self.chronic_load_start_date_time = None
        self.acute_readiness_surveys = []
        self.chronic_readiness_surveys = []
        self.acute_post_session_surveys = []
        self.chronic_post_session_surveys = []
        self.acute_daily_plans = []
        self.chronic_daily_plans = []
        self.last_7_days_plans = []
        self.days_8_14_plans = []

    def set_start_end_times(self):
        if self.event_date is None:
            readiness_surveys = self.daily_readiness_datastore.get(self.athlete_id)
            last_daily_readiness_survey = readiness_surveys[0]
            event_date_time = last_daily_readiness_survey.get_event_date()
            self.event_date = event_date_time.date().strftime('%Y-%m-%d')
        start_date = datetime.strptime(self.event_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.event_date, "%Y-%m-%d")
        self.start_date_time = start_date - timedelta(days=28)
        self.end_date_time = end_date + timedelta(days=1)

    def process_athlete_stats(self):
        self.set_start_end_times()
        self.load_historical_data()
        athlete_stats = AthleteStats(self.athlete_id)
        athlete_stats.event_date = self.event_date
        athlete_stats = self.calc_survey_stats(athlete_stats)
        athlete_stats = self.calc_training_volume_metrics(athlete_stats)
        self.athlete_stats_datastore.put(athlete_stats)

    def calc_training_volume_metrics(self, athlete_stats):

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
            x for x in self.get_session_attribute_sum("external_load", self.last_7_days_plans) if x is not None)

        last_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               self.last_7_days_plans) if x is not None)
        previous_week_external_values.extend(
            x for x in self.get_session_attribute_sum("external_load", self.days_8_14_plans) if x is not None)

        previous_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               self.days_8_14_plans) if x is not None)

        a_external_load_values.extend(
            x for x in self.get_session_attribute_sum("external_load", self.acute_daily_plans) if x is not None)


        a_internal_load_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               self.acute_daily_plans) if x is not None)

        a_external_load_values.extend(
            x for x in self.get_session_attribute_sum("external_load", self.acute_daily_plans) if x is not None)

        a_high_intensity_values.extend(
            x for x in self.get_session_attribute_sum("high_intensity_load", self.acute_daily_plans) if
            x is not None)

        a_mod_intensity_values.extend(
            x for x in self.get_session_attribute_sum("mod_intensity_load", self.acute_daily_plans) if
            x is not None)

        a_low_intensity_values.extend(
            x for x in self.get_session_attribute_sum("low_intensity_load", self.acute_daily_plans) if
            x is not None)

        weeks_list = self.get_chronic_weeks_plans()

        for w in weeks_list:

            c_internal_load_values.extend(
                x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes", w)
                if x is not None)

            c_external_load_values.extend(x for x in self.get_session_attribute_sum("external_load", w) if x is not None)

            c_high_intensity_values.extend(x for x in self.get_session_attribute_sum("high_intensity_load", w)
                                           if x is not None)

            c_mod_intensity_values.extend(x for x in self.get_session_attribute_sum("mod_intensity_load", w)
                                          if x is not None)

            c_low_intensity_values.extend(x for x in self.get_session_attribute_sum("low_intensity_load", w)
                                          if x is not None)

        if len(last_week_external_values) > 0 and len(previous_week_external_values) > 0:
            current_load = sum(last_week_external_values)
            previous_load = sum(previous_week_external_values)
            athlete_stats.external_ramp = ((current_load - previous_load) / previous_load) * 100

        if len(last_week_internal_values) > 0 and len(previous_week_internal_values) > 0:
            current_load = sum(last_week_internal_values)
            previous_load = sum(previous_week_internal_values)
            athlete_stats.internal_ramp = ((current_load - previous_load) / previous_load) * 100

        if len(last_week_external_values) > 1:
            average_load = statistics.mean(last_week_external_values)
            stdev_load = statistics.stdev(last_week_external_values)
            athlete_stats.external_monotony = average_load / stdev_load
            athlete_stats.external_strain = athlete_stats.external_monotony * sum(last_week_external_values)

        if len(last_week_internal_values) > 1:
            average_load = statistics.mean(last_week_internal_values)
            stdev_load = statistics.stdev(last_week_internal_values)
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

        return athlete_stats

    def get_chronic_weeks_plans(self):

        week4_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time - timedelta(days=28) <=
                          d.get_event_datetime() < self.acute_start_date_time - timedelta(days=21)]
        week3_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time
                          - timedelta(days=21) <= d.get_event_datetime() < self.acute_start_date_time -
                          timedelta(days=11)]
        week2_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time
                          - timedelta(days=14) <= d.get_event_datetime() < self.acute_start_date_time -
                          timedelta(days=7)]
        week1_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time
                          - timedelta(days=7) <= d.get_event_datetime() < self.acute_start_date_time]

        weeks_list = [week1_sessions, week2_sessions, week3_sessions, week4_sessions]

        return weeks_list

    def get_session_attribute_sum(self, attribute_name, daily_plan_collection):

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

        values = list(getattr(c, attribute_1_name) * getattr(c, attribute_1_name) for c in session_collection
                      if getattr(c, attribute_1_name) is not None and getattr(c, attribute_2_name) is not None)
        return values

    def calc_survey_stats(self, athlete_stats):

        if len(self.acute_readiness_surveys) > 0:

            acute_readiness_values = [x.readiness for x in self.acute_readiness_surveys if x is not None]
            acute_sleep_quality_values = [x.sleep_quality for x in self.acute_readiness_surveys if x is not None]

            chronic_readiness_values = [x.readiness for x in self.chronic_readiness_surveys if x is not None]
            chronic_sleep_quality_values = [x.sleep_quality for x in self.chronic_readiness_surveys if x is not None]

            acute_RPE_values = [x.survey.RPE for x in self.acute_post_session_surveys if x.survey.RPE is not None]
            chronic_RPE_values = [x.survey.RPE for x in self.chronic_post_session_surveys if x.survey.RPE is not None]

            dates_difference = self.end_date_time - self.start_date_time

            max_acute_soreness_values = []
            max_chronic_soreness_values = []

            acute_soreness_values = []
            chronic_soreness_values = []

            for d in range(dates_difference.days + 1):

                acute_post_surveys = [x.survey for x in self.acute_post_session_surveys if x.survey is not None and
                                      x.event_date == (self.start_date_time + timedelta(d)).strftime("%Y-%m-%d")]

                acute_post_soreness_values = []

                for s in acute_post_surveys:
                    soreness_values = [x.severity for x in s.soreness if x.severity is not None]
                    acute_post_soreness_values.extend(soreness_values)

                readiness_surveys = [x for x in self.acute_readiness_surveys if x is not None and
                                     x.event_date == (self.start_date_time + timedelta(d)).strftime("%Y-%m-%d")]

                acute_readiness_soreness_values = []

                for s in readiness_surveys:
                    soreness_values = [x.severity for x in s.soreness if x.severity is not None]
                    acute_readiness_values.extend(soreness_values)

                acute_soreness_values.extend(acute_post_soreness_values)
                acute_soreness_values.extend(acute_readiness_soreness_values)

                if len(acute_soreness_values) > 0:
                    max_acute_soreness_values.append(max(acute_soreness_values))

                chronic_post_surveys = [x.survey for x in self.chronic_post_session_surveys if x.survey is not None and
                                      x.event_date == (self.start_date_time + timedelta(d)).strftime("%Y-%m-%d")]

                chronic_post_soreness_values = []

                for s in chronic_post_surveys:
                    soreness_values = [x.severity for x in s.soreness if x.severity is not None]
                    chronic_post_soreness_values.extend(soreness_values)

                chronic_readiness_surveys = [x for x in self.chronic_readiness_surveys if x is not None and
                                     x.event_date == (self.start_date_time + timedelta(d)).strftime("%Y-%m-%d")]

                chronic_readiness_soreness_values = []

                for s in chronic_readiness_surveys:
                    soreness_values = [x.severity for x in s.soreness if x.severity is not None]
                    chronic_readiness_soreness_values.extend(soreness_values)

                chronic_soreness_values.extend(chronic_post_soreness_values)
                chronic_soreness_values.extend(chronic_readiness_soreness_values)

                if len(chronic_soreness_values) > 0:
                    max_chronic_soreness_values.append(max(chronic_soreness_values))

            if len(acute_RPE_values) > 0:
                athlete_stats.acute_avg_RPE = statistics.mean(acute_RPE_values)

            if len(acute_readiness_values) > 0:
                athlete_stats.acute_avg_readiness = statistics.mean(acute_readiness_values)

            if len(acute_sleep_quality_values) > 0:
                athlete_stats.acute_avg_sleep_quality = statistics.mean(acute_sleep_quality_values)

            if len(max_acute_soreness_values) > 0:
                athlete_stats.acute_avg_max_soreness = statistics.mean(max_acute_soreness_values)

            if len(chronic_RPE_values) > 0:
                athlete_stats.chronic_avg_RPE = statistics.mean(chronic_RPE_values)

            if len(chronic_readiness_values) > 0:
                athlete_stats.chronic_avg_readiness = statistics.mean(chronic_readiness_values)

            if len(chronic_sleep_quality_values) > 0:
                athlete_stats.chronic_avg_sleep_quality = statistics.mean(chronic_sleep_quality_values)

            if len(max_chronic_soreness_values) > 0:
                athlete_stats.chronic_avg_max_soreness = statistics.mean(max_chronic_soreness_values)

        return athlete_stats

    def load_historical_data(self):

        daily_readiness_surveys = self.daily_readiness_datastore.get(self.athlete_id, self.start_date_time,
                                                                     self.end_date_time, last_only=False)

        post_session_surveys = self.post_session_survey_datastore.get(self.athlete_id, self.start_date_time,
                                                                      self.end_date_time)

        daily_plans = self.daily_plan_datastore.get(self.athlete_id, self.start_date_time, self.end_date_time)

        if daily_readiness_surveys is not None and len(daily_readiness_surveys) > 0:
            daily_readiness_surveys.sort(key=lambda x: x.event_date, reverse=False)
            earliest_survey_date_time = daily_readiness_surveys[0].event_date
        else:
            return

        if post_session_surveys is not None and len(post_session_surveys) > 0:
            post_session_surveys.sort(key=lambda x: x.event_date_time, reverse=False)
            earliest_survey_date_time = min(earliest_survey_date_time, post_session_surveys[0].event_date_time)

        days_difference = (self.end_date_time - earliest_survey_date_time).days

        if 7 <= days_difference < 14:
            self.acute_days = 3
            self.chronic_days = int(days_difference)
        elif 14 <= days_difference <= 28:
            self.acute_days = 7
            self.chronic_days = int(days_difference)
        elif days_difference > 28:
            self.acute_days = 7
            self.chronic_days = 28

        if self.acute_days is not None and self.chronic_days is not None:
            self.acute_start_date_time = self.end_date_time - timedelta(days=self.acute_days)
            self.chronic_start_date_time = self.end_date_time - timedelta(days=self.chronic_days)
            chronic_date_time = self.acute_start_date_time - timedelta(days=self.chronic_days)
            chronic_delta = self.end_date_time - chronic_date_time
            self.chronic_load_start_date_time = self.end_date_time - chronic_delta
            last_week = self.end_date_time - timedelta(days=7)
            previous_week = last_week - timedelta(days=7)

            self.acute_post_session_surveys = [p for p in post_session_surveys
                                               if p.event_date_time >= self.acute_start_date_time]
            self.chronic_post_session_surveys = [p for p in post_session_surveys
                                                 if p.event_date_time >= self.chronic_start_date_time]
            self.acute_readiness_surveys = [p for p in daily_readiness_surveys
                                            if p.event_date >= self.acute_start_date_time]
            self.chronic_readiness_surveys = [p for p in daily_readiness_surveys
                                              if p.event_date >= self.chronic_start_date_time]

            self.acute_daily_plans = [p for p in daily_plans if p.get_event_datetime() >= self.acute_start_date_time]

            self.chronic_daily_plans = [p for p in daily_plans if self.acute_start_date_time >
                                        p.get_event_datetime() >= self.chronic_load_start_date_time]

            self.last_7_days_plans = [p for p in daily_plans if p.get_event_datetime() >= last_week]

            self.days_8_14_plans = [p for p in daily_plans if last_week > p.get_event_datetime() >= previous_week]








