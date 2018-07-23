from models.stats import AthleteStats
from datetime import datetime, timedelta
import statistics
from utils import format_datetime

class StatsProcessing(object):

    def __init__(self, athlete_id, event_date, daily_readiness_datastore, post_session_survey_datastore):
        self.athlete_id = athlete_id
        self.daily_readiness_datastore = daily_readiness_datastore
        self.post_session_survey_datastore = post_session_survey_datastore
        self.start_date = datetime.strptime(event_date, "%Y-%m-%d")
        self.end_date = datetime.strptime(event_date, "%Y-%m-%d")
        self.start_date_time = datetime(self.start_date.year, self.start_date.month, self.start_date.day - 28, 0, 0, 0)
        self.end_date_time = datetime(self.end_date.year, self.end_date.month, self.end_date.day + 1, 0, 0, 0)
        self.acute_readiness_surveys = []
        self.chronic_readiness_surveys = []
        self.acute_post_session_surveys = []
        self.chronic_post_session_surveys = []

    def calc_athlete_stats(self):

        self.load_acute_chronic_data()

        athlete_stats = AthleteStats(self.athlete_id)
        acute_RPE_values = [x.RPE for x in self.acute_post_session_surveys if x is not None]
        acute_readiness_values = [x.readiness for x in self.acute_readiness_surveys if x is not None]
        acute_sleep_quality_values = [x.sleep_quality for x in self.acute_readiness_surveys if x is not None]

        chronic_RPE_values = [x.RPE for x in self.chronic_post_session_surveys if x is not None]
        chronic_readiness_values = [x.readiness for x in self.chronic_readiness_surveys if x is not None]
        chronic_sleep_quality_values = [x.sleep_quality for x in self.chronic_readiness_surveys if x is not None]

        dates_difference = self.end_date_time - self.start_date_time

        max_acute_soreness_values = []
        max_chronic_soreness_values = []

        for d in range(dates_difference.days + 1):

            acute_post_soreness_values = [x.survey.soreness.severity for x in self.acute_post_session_surveys
                                          if x.survey.soreness is not None and len(x.survey.soreness) > 0
                                          and x.event_date == d]
            acute_readiness_soreness_values = [x.soreness.severity for x in self.acute_readiness_surveys
                                               if x.soreness is not None and len(x.soreness) > 0
                                               and x.event_date == d]

            acute_soreness_values = []

            acute_soreness_values.extend(acute_post_soreness_values)
            acute_soreness_values.extend(acute_readiness_soreness_values)

            if len(acute_soreness_values) > 0:
                max_acute_soreness_values.append(max(acute_soreness_values))

            chronic_post_soreness_values = [x.survey.soreness.severity for x in self.chronic_post_session_surveys
                                            if x.survey.soreness is not None and len(x.survey.soreness) > 0
                                            and x.event_date == d]
            chronic_readiness_soreness_values = [x.soreness.severity for x in self.chronic_readiness_surveys
                                                 if x.soreness is not None and len(x.soreness) > 0
                                                 and x.event_date == d]

            chronic_soreness_values = []

            chronic_soreness_values.extend(chronic_post_soreness_values)
            chronic_soreness_values.extend(chronic_readiness_soreness_values)

            if len(chronic_soreness_values) > 0:
                max_chronic_soreness_values.append(max(chronic_soreness_values))

        athlete_stats.acute_avg_RPE = statistics.mean(acute_RPE_values)
        athlete_stats.acute_avg_readiness = statistics.mean(acute_readiness_values)
        athlete_stats.acute_avg_sleep_quality = statistics.mean(acute_sleep_quality_values)
        athlete_stats.acute_avg_max_soreness = statistics.mean(max_acute_soreness_values)

        athlete_stats.chronic_avg_RPE = statistics.mean(chronic_RPE_values)
        athlete_stats.chronic_avg_readiness = statistics.mean(chronic_readiness_values)
        athlete_stats.chronic_avg_sleep_quality = statistics.mean(chronic_sleep_quality_values)
        athlete_stats.chronic_avg_max_soreness = statistics.mean(max_chronic_soreness_values)

        return athlete_stats

    def load_acute_chronic_data(self):

        daily_readiness_surveys = self.daily_readiness_datastore.get(self.athlete_id, self.start_date_time,
                                                                     self.end_date_time, last_only=False)

        post_session_surveys = self.post_session_survey_datastore.get(self.athlete_id, self.start_date_time,
                                                                      self.end_date_time)

        if daily_readiness_surveys is not None and len(daily_readiness_surveys) > 0:
            daily_readiness_surveys.sort(key=lambda x: x.event_date, reverse=True)
            earliest_survey_date_time = daily_readiness_surveys[0].event_date
        else:
            return

        if post_session_surveys is not None and len(daily_readiness_surveys) > 0:
            post_session_surveys.sort(key=lambda x: x.event_date_time, reverse=True)
            earliest_survey_date_time = min(earliest_survey_date_time, post_session_surveys[0].event_date_time)

        days_difference = (self.end_date_time - earliest_survey_date_time).days

        acute_days = None
        chronic_days = None

        if 7 <= days_difference < 14:
            acute_days = 3
            chronic_days = days_difference
        elif 14 <= days_difference <= 28:
            acute_days = 7
            chronic_days = days_difference
        elif days_difference > 28:
            acute_days = 7
            chronic_days = 28

        if acute_days is not None and chronic_days is not None:
            acute_start_date_time = self.end_date_time - timedelta(days=acute_days)
            chronic_start_date_time = self.end_date_time - timedelta(days=chronic_days)

            self.acute_post_session_surveys = [p for p in post_session_surveys
                                               if p.event_date >= acute_start_date_time]
            self.chronic_post_session_surveys = [p for p in post_session_surveys
                                                 if p.event_date >= chronic_start_date_time]
            self.acute_readiness_surveys = [p for p in daily_readiness_surveys
                                            if p.event_date >= acute_start_date_time]
            self.chronic_readiness_surveys = [p for p in daily_readiness_surveys
                                              if p.event_date >= chronic_start_date_time]





