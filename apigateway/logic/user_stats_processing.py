from datetime import datetime, timedelta
from fathomapi.utils.xray import xray_recorder
from logic.training_load_processing import TrainingLoadProcessing
from logic.soreness_processing import SorenessCalculator
from models.user_stats import UserStats
# from models.asymmetry import HistoricAsymmetry, AsymmetryType
from utils import parse_date, format_date
from logic.injury_risk_processing import InjuryRiskProcessor
from models.athlete_injury_risk import AthleteInjuryRisk


class UserStatsProcessing(object):

    def __init__(self, athlete_id, event_date, datastore_collection):
        self.athlete_id = athlete_id
        self.event_date = event_date
        self.user_stats_datastore = datastore_collection.user_stats_datastore
        self.symptom_datastore = datastore_collection.symptom_datastore
        self.injury_risk_datastore = datastore_collection.injury_risk_datastore
        self.training_session_datastore = datastore_collection.training_session_datastore
        self.start_date = None
        self.end_date = None
        self.start_date_time = None
        self.end_date_time = None
        self.acute_days = None
        self.chronic_days = None
        self.acute_start_date_time = None
        self.chronic_start_date_time = None
        self.chronic_load_start_date_time = None

        self.last_week = None
        self.last_6_days = None
        self.last_25_days = None
        self.previous_week = None
        self.days_7_13 = None

        self.historic_data_loaded = False

        self.training_sessions = []
        self.acute_training_sessions = []
        self.chronic_training_sessions = []
        self.last_6_days_training_sessions = []
        self.last_7_days_training_sessions = []
        self.last_7_13_training_sessions = []
        self.days_8_14_training_sessions = []
        self.last_25_days_training_sessions = []
        self.latest_training_session_date = None

        self.symptoms = []
        self.acute_symptoms = []
        self.chronic_symptoms = []
        self.chronic_symptoms = []
        self.last_7_days_symptoms = []
        self.days_8_14_symptoms = []
        self.last_25_days_symptoms = []

    def set_start_end_times(self):
        # start_date = datetime.strptime(self.event_date, "%Y-%m-%d")
        # end_date = datetime.strptime(self.event_date, "%Y-%m-%d")
        start_date = self.event_date
        end_date = self.event_date
        self.start_date_time = start_date - timedelta(days=35)  # used to be 28, this allows for non-overlapping 7/28
        self.end_date_time = end_date + timedelta(days=1)
        self.start_date = self.start_date_time.strftime('%Y-%m-%d')
        self.end_date = self.end_date_time.strftime('%Y-%m-%d')
        return True

    def increment_start_end_times(self, number_of_days):
        start_date = datetime.strptime(self.event_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.event_date, "%Y-%m-%d") + timedelta(days=number_of_days)
        self.start_date_time = start_date - timedelta(days=35)  # used to be 28, this allows for non-overlapping 7/28
        self.end_date_time = end_date + timedelta(days=1)
        self.start_date = self.start_date_time.strftime('%Y-%m-%d')
        self.end_date = self.end_date_time.strftime('%Y-%m-%d')
        return True

    @xray_recorder.capture('logic.UserStatsProcessing.process_user_stats')
    def process_user_stats(self, current_user_stats=None, force_historical_process=False):
        if self.start_date is None:
            self.set_start_end_times()

        self.load_historical_data()

        if current_user_stats is None:  # if no athlete_stats was passed, read from mongo
            current_user_stats = self.user_stats_datastore.get(athlete_id=self.athlete_id)

            if current_user_stats is None:  # if not found in mongo (first time use), create a new one
                current_user_stats = UserStats(self.athlete_id)
                current_user_stats.event_date = self.event_date
            if current_user_stats.event_date is None:
                current_user_stats.event_date = self.event_date

        # for symptom in self.last_25_days_symptoms:
        #     symptom.severity = SorenessCalculator.get_severity(symptom.severity, symptom.movement)

        training_load_processing = TrainingLoadProcessing(self.start_date,
                                                          format_date(self.event_date),
                                                          current_user_stats.load_stats)  # want event date since end date = event_date + 1

        # this gets updated in load plan values
        training_load_processing.sport_max_load = current_user_stats.sport_max_load

        training_load_processing.load_training_session_values(self.last_7_days_training_sessions,
                                                              self.days_8_14_training_sessions,
                                                              self.chronic_training_sessions
                                                              )

        # three_sensor_sessions = [s for s in self.training_sessions if s.source.value == 3 and (s.asymmetry is not None or s.movement_patterns is not None)]
        # if len(three_sensor_sessions) > 0:
        #     current_user_stats.has_three_sensor_data = True
        #     current_user_stats.historic_asymmetry = self.get_historic_asymmetry(self.training_sessions)

        current_user_stats.sport_max_load = training_load_processing.sport_max_load

        current_user_stats.load_stats = training_load_processing.load_stats
        current_user_stats = training_load_processing.calc_training_load_metrics(current_user_stats)
        current_user_stats.high_relative_load_sessions = training_load_processing.high_relative_load_sessions

        if current_user_stats.event_date.date() == self.event_date.date():
            # persist all of soreness/pain and session_RPE
            # current_user_stats.session_RPE = current_user_stats.session_RPE
            # current_user_stats.session_RPE_event_date = current_user_stats.session_RPE_event_date
            if force_historical_process:
                # New
                historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)
                injury_risk_processor = InjuryRiskProcessor(self.event_date, self.last_25_days_symptoms,
                                                            self.training_sessions, historical_injury_risk_dict,
                                                            current_user_stats, self.athlete_id)
                injury_risk_processor.process(update_historical_data=True)

                athlete_injury_risk = AthleteInjuryRisk(self.athlete_id)
                athlete_injury_risk.items = injury_risk_processor.injury_risk_dict

                self.injury_risk_datastore.put(athlete_injury_risk)

        else:  # nightly process (first update for the day)
            # clear these if it's a new day
            # current_user_stats.session_RPE = None
            # current_user_stats.session_RPE_event_date = None

            historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)
            injury_risk_processor = InjuryRiskProcessor(self.event_date, self.last_25_days_symptoms,
                                                        self.training_sessions, historical_injury_risk_dict,
                                                        current_user_stats, self.athlete_id)
            injury_risk_processor.process(update_historical_data=True)

            athlete_injury_risk = AthleteInjuryRisk(self.athlete_id)
            athlete_injury_risk.items = injury_risk_processor.injury_risk_dict

            self.injury_risk_datastore.put(athlete_injury_risk)

        current_user_stats.event_date = self.event_date
        return current_user_stats

    @xray_recorder.capture('logic.StatsProcessing.load_historical_data')
    def load_historical_data(self):
        if not self.historic_data_loaded:
            self.symptoms = self.symptom_datastore.get(user_id=self.athlete_id,
                                                       start_date_time=self.start_date_time,
                                                       end_date_time=self.end_date_time)
            self.training_sessions = self.training_session_datastore.get(user_id=self.athlete_id,
                                                                         start_date_time=self.start_date_time,
                                                                         end_date_time=self.event_date)
        self.update_start_times()
        self.set_acute_chronic_periods()
        self.load_historical_symptoms()
        self.load_historical_sessions()
        self.historic_data_loaded = True

    def load_historical_symptoms(self):

        self.acute_symptoms = sorted([s for s in self.symptoms if self.acute_start_date_time is not None and
                                      s.reported_date_time >= self.acute_start_date_time],
                                     key=lambda x: x.reported_date_time)
        self.chronic_symptoms = sorted([s for s in self.symptoms if self.acute_start_date_time is not None and
                                        self.chronic_start_date_time is not None and
                                        self.acute_start_date_time > s.reported_date_time >=
                                        self.chronic_start_date_time],
                                       key=lambda x: x.reported_date_time)

        self.last_7_days_symptoms = [s for s in self.symptoms if self.last_week is not None and
                                     s.reported_date_time >= self.last_week]

        self.last_25_days_symptoms = [s for s in self.symptoms if self.last_25_days is not None and
                                      s.reported_date_time >= self.last_25_days]

        self.days_8_14_symptoms = [s for s in self.symptoms if self.last_week is not None
                                   and self.previous_week is not None and
                                   self.last_week > s.reported_date_time >= self.previous_week]

    def load_historical_sessions(self):

        self.acute_training_sessions = sorted([p for p in self.training_sessions if self.acute_start_date_time is not None and p.get_event_datetime() >=
                                               self.acute_start_date_time], key=lambda x: x.event_date)

        self.chronic_training_sessions = sorted([p for p in self.training_sessions if self.acute_start_date_time is not None and
                                                 self.chronic_load_start_date_time is not None and self.acute_start_date_time >
                                                 p.get_event_datetime() >= self.chronic_load_start_date_time],
                                                key=lambda x: x.event_date)

        self.last_6_days_training_sessions = [p for p in self.training_sessions if p.get_event_datetime() >= self.last_6_days]

        self.last_7_days_training_sessions = [p for p in self.training_sessions if p.get_event_datetime() >= self.last_week]

        self.last_7_13_training_sessions = [p for p in self.training_sessions if self.last_6_days > p.get_event_datetime() >= self.days_7_13]

        self.days_8_14_training_sessions = [p for p in self.training_sessions if self.last_week > p.get_event_datetime() >= self.previous_week]

    def update_start_times(self):

        if self.symptoms is not None and len(self.symptoms) > 0:
            self.symptoms.sort(key=lambda x: x.reported_date_time, reverse=False)
            self.start_date_time = max(self.start_date_time, self.symptoms[0].reported_date_time)

        self.latest_training_session_date = self.end_date_time

        if self.training_sessions is not None and len(self.training_sessions) > 0:
            self.training_sessions.sort(key=lambda x: x.event_date, reverse=False)
            self.latest_training_session_date = parse_date(self.training_sessions[len(self.training_sessions) - 1].event_date)

    def set_acute_chronic_periods(self):

        # add one since survey is first thing done in the day
        days_difference = (self.end_date_time.date() - self.start_date_time.date()).days + 1

        acute_days_adjustment = 0

        if days_difference == 7:
            self.acute_days = 3
            self.chronic_days = 7
        elif 7 < days_difference < 10:
            self.acute_days = 3
            self.chronic_days = int(days_difference)
        elif 10 <= days_difference < 21:
            self.acute_days = 3
            self.chronic_days = int(days_difference) - 3
            acute_days_adjustment = 3
        elif 21 <= days_difference <= 35:
            self.acute_days = 7
            self.chronic_days = int(days_difference) - 7
            acute_days_adjustment = 7
        elif days_difference > 35:
            self.acute_days = 7
            self.chronic_days = 28
            acute_days_adjustment = 7

        adjustment_factor = 0
        if self.latest_training_session_date is not None and self.event_date > self.latest_training_session_date:
            adjustment_factor = (self.event_date.date() - self.latest_training_session_date.date()).days

        if self.acute_days is not None and self.chronic_days is not None:
            self.acute_start_date_time = self.end_date_time - timedelta(days=self.acute_days + adjustment_factor)
            self.chronic_start_date_time = self.end_date_time - timedelta(
                days=self.chronic_days + acute_days_adjustment + adjustment_factor)
            chronic_date_time = self.acute_start_date_time - timedelta(days=self.chronic_days)
            chronic_delta = self.end_date_time - chronic_date_time
            self.chronic_load_start_date_time = self.end_date_time - chronic_delta

        self.last_week = self.end_date_time - timedelta(days=7 + adjustment_factor)
        self.last_6_days = self.end_date_time - timedelta(days=5 + adjustment_factor)
        self.last_25_days = self.end_date_time - timedelta(days=25 + adjustment_factor)
        self.previous_week = self.last_week - timedelta(days=7)
        self.days_7_13 = self.previous_week + timedelta(days=1)

    # def get_historic_asymmetry(self, sessions):
    #
    #     historic_asymmetry = {}
    #
    #     last_15_day_sessions = [s for s in sessions if self.event_date >= s.event_date >= self.event_date - timedelta(days=15) and s.asymmetry is not None]
    #     last_30_day_sessions = [s for s in sessions if
    #                             self.event_date - timedelta(days=15) > s.event_date >= self.event_date - timedelta(days=30) and s.asymmetry is not None]
    #
    #     apt_historic_asymmetry = HistoricAsymmetry(AsymmetryType.anterior_pelvic_tilt)
    #
    #     if len(last_15_day_sessions) >= 4:
    #         apt_asymmetric_events = 0
    #         apt_symmetric_events = 0
    #         for s in last_15_day_sessions:
    #             if s.asymmetry is not None and s.asymmetry.anterior_pelvic_tilt is not None:
    #                 apt_asymmetric_events += s.asymmetry.anterior_pelvic_tilt.asymmetric_events
    #             if s.asymmetry is not None and s.asymmetry.anterior_pelvic_tilt is not None:
    #                 apt_symmetric_events += s.asymmetry.anterior_pelvic_tilt.symmetric_events
    #
    #         apt_historic_asymmetry.asymmetric_events_15_days = apt_asymmetric_events
    #         apt_historic_asymmetry.symmetric_events_15_days = apt_symmetric_events
    #
    #     if len(last_30_day_sessions) >= 4:
    #         apt_asymmetric_events = 0
    #         apt_symmetric_events = 0
    #         for s in last_30_day_sessions:
    #             if s.asymmetry is not None and s.asymmetry.anterior_pelvic_tilt is not None:
    #                 apt_asymmetric_events += s.asymmetry.anterior_pelvic_tilt.asymmetric_events
    #             if s.asymmetry is not None and s.asymmetry.anterior_pelvic_tilt is not None:
    #                 apt_symmetric_events += s.asymmetry.anterior_pelvic_tilt.symmetric_events
    #
    #         apt_historic_asymmetry.asymmetric_events_30_days = apt_asymmetric_events
    #         apt_historic_asymmetry.symmetric_events_30_days = apt_symmetric_events
    #
    #     historic_asymmetry[AsymmetryType.anterior_pelvic_tilt.value] = apt_historic_asymmetry
    #
    #     return historic_asymmetry
