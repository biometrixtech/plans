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
        self.acute_start_date_time = None
        self.chronic_start_date_time = None
        self.chronic_load_start_date_time = None
        self.acute_readiness_surveys = []
        self.chronic_readiness_surveys = []
        self.acute_post_session_surveys = []
        self.chronic_post_session_surveys = []
        self.acute_daily_plans = []
        self.chronic_daily_plans = []

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
        self.load_acute_chronic_data()
        athlete_stats = AthleteStats(self.athlete_id)
        athlete_stats.event_date = self.event_date
        athlete_stats = self.calc_survey_stats(athlete_stats)
        self.athlete_stats_datastore.put(athlete_stats)

    def calc_training_volume_metrics(self, athlete_stats):

        a_external_load_values = []
        a_high_intensity_values = []
        a_mod_intensity_values = []
        a_low_intensity_values = []

        c_external_load_values = []
        c_high_intensity_values = []
        c_mod_intensity_values = []
        c_low_intensity_values = []

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

            c_external_load_values.extend(x for x in self.get_session_attribute_sum("external_load", w) if x is not None)

            c_high_intensity_values.extend(x for x in self.get_session_attribute_sum("high_intensity_load", w)
                                           if x is not None)

            c_mod_intensity_values.extend(x for x in self.get_session_attribute_sum("mod_intensity_load", w)
                                          if x is not None)

            c_low_intensity_values.extend(x for x in self.get_session_attribute_sum("low_intensity_load", w)
                                          if x is not None)

        if len(a_external_load_values) > 0:
            athlete_stats.acute_external_total_load = sum(a_external_load_values)
        if len(a_high_intensity_values) > 0:
            athlete_stats.acute_external_high_intensity_load = sum(a_high_intensity_values)
        if len(a_mod_intensity_values) > 0:
            athlete_stats.acute_external_mod_intensity_load = sum(a_mod_intensity_values)
        if len(a_low_intensity_values) > 0:
            athlete_stats.acute_external_low_intensity_load = sum(a_low_intensity_values)

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

        week1_sessions = [d for d in self.chronic_daily_plans if self.chronic_load_start_date_time <=
                          d.get_event_datetime() < self.chronic_load_start_date_time + timedelta(days=7)]
        week2_sessions = [d for d in self.chronic_daily_plans if self.chronic_load_start_date_time
                          + timedelta(days=7) <= d.get_event_datetime() < self.chronic_load_start_date_time +
                          timedelta(days=14)]
        week3_sessions = [d for d in self.chronic_daily_plans if self.chronic_load_start_date_time
                          + timedelta(days=14) <= d.get_event_datetime() < self.chronic_load_start_date_time +
                          timedelta(days=21)]
        week4_sessions = [d for d in self.chronic_daily_plans if self.chronic_load_start_date_time
                          + timedelta(days=21) <= d.get_event_datetime() < self.acute_start_date_time]

        weeks_list = [week1_sessions, week2_sessions, week3_sessions, week4_sessions]

        return weeks_list

    def get_session_attribute_sum(self, attribute_name, daily_plan_collection):

        sum_value = None

        values = []

        for c in daily_plan_collection:

            values.extend(self.get_values_for_session_attribute(attribute_name, c.practice_sessions))
            values.extend(self.get_values_for_session_attribute(attribute_name, c.strength_conditioning_sessions))
            values.extend(self.get_values_for_session_attribute(attribute_name, c.games))
            values.extend(self.get_values_for_session_attribute(attribute_name, c.bump_up_sessions))

        if len(values) > 0:
            sum_value = sum(values)

        return [sum_value]

    def get_values_for_session_attribute(self, attribute_name, session_collection):

        values = list(getattr(c, attribute_name) for c in session_collection if getattr(c, attribute_name) is not None)
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

    def load_acute_chronic_data(self):

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

        acute_days = None
        chronic_days = None

        if 7 <= days_difference < 14:
            acute_days = 3
            chronic_days = int(days_difference)
        elif 14 <= days_difference <= 28:
            acute_days = 7
            chronic_days = int(days_difference)
        elif days_difference > 28:
            acute_days = 7
            chronic_days = 28

        if acute_days is not None and chronic_days is not None:
            self.acute_start_date_time = self.end_date_time - timedelta(days=acute_days)
            self.chronic_start_date_time = self.end_date_time - timedelta(days=chronic_days)
            chronic_date_time = self.acute_start_date_time - timedelta(days=chronic_days)
            chronic_delta = self.end_date_time - chronic_date_time
            self.chronic_load_start_date_time = self.end_date_time - chronic_delta

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








