from models.stats import AthleteStats
import datetime
from utils import format_datetime

class StatsProcessing(object):

    def __init__(self, athlete_id, daily_readiness_datastore, post_session_survey_datastore):
        self.athlete_id = athlete_id
        self.daily_readiness_datastore = daily_readiness_datastore
        self.post_session_survey_datastore = post_session_survey_datastore
        self.acute_readiness_surveys = []
        self.chronic_readiness_surveys = []
        self.acute_post_session_surveys = []
        self.chronic_post_session_surveys = []

    def load_acute_chronic_data(self, event_date):
        start_date_time = datetime.datetime.strptime(event_date, "%Y-%m-%d")
        end_date_time = datetime.datetime.strptime(event_date, "%Y-%m-%d")
        start_time = format_datetime(
            datetime.datetime(start_date_time.year, start_date_time.month, start_date_time.day - 28, 0, 0, 0))
        end_time = format_datetime(
            datetime.datetime(end_date_time.year, end_date_time.month, end_date_time.day + 1, 0, 0, 0))

        daily_readiness_surveys = self.daily_readiness_datastore.get(self.athlete_id, start_time, end_time,
                                                                     last_only=False)

        post_session_surveys = self.post_session_survey_datastore.get(self.athlete_id, start_time, end_time)

        earliest_survey_date_time = None

        if daily_readiness_surveys is not None and len(daily_readiness_surveys) > 0:
            daily_readiness_surveys.sort(key=lambda x: x.event_date, reverse=True)
            earliest_survey_date_time = daily_readiness_surveys[0].event_date

        if post_session_surveys is not None and len(daily_readiness_surveys) > 0:
            post_session_surveys.sort(key=lambda x: x.event_date_time, reverse=True)
            earliest_survey_date_time = min(earliest_survey_date_time, post_session_surveys[0].event_date_time)

        acute_start_date_time = None
        chronic_start_date_time = None







