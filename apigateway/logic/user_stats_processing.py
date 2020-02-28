import math
import statistics
from collections import namedtuple
from datetime import datetime, timedelta
from models.chart_data import BodyPartChartCollection, MuscularStrainChart, HighRelativeLoadChart, DOMSChart, BodyResponseChart
from fathomapi.utils.xray import xray_recorder
from logic.training_volume_processing import TrainingVolumeProcessing
from logic.soreness_processing import SorenessCalculator
from models.stats import AthleteStats
from models.soreness import Soreness
from models.soreness_base import HistoricSorenessStatus
from models.body_parts import BodyPart, BodyPartFactory, BodyPartLocation, BodyPartSide
from models.historic_soreness import HistoricSoreness, HistoricSeverity, CoOccurrence, SorenessCause
from models.post_session_survey import PostSessionSurvey
from models.data_series import DataSeries
from models.asymmetry import HistoricAsymmetry, AsymmetryType
from utils import parse_date, format_date
from logic.injury_risk_processing import InjuryRiskProcessor
from models.athlete_injury_risk import AthleteInjuryRisk
from copy import deepcopy


class UserStatsProcessing(object):

    def __init__(self, athlete_id, event_date, datastore_collection):
        self.athlete_id = athlete_id
        self.event_date = event_date
        self.athlete_stats_datastore = datastore_collection.athlete_stats_datastore
        self.daily_plan_datastore = datastore_collection.daily_plan_datastore
        self.cleared_soreness_datastore = datastore_collection.cleared_soreness_datastore
        self.injury_risk_datastore = datastore_collection.injury_risk_datastore
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

        self.acute_readiness_surveys = []
        self.chronic_readiness_surveys = []
        self.acute_post_session_surveys = []
        self.chronic_post_session_surveys = []
        self.acute_daily_plans = []
        self.chronic_daily_plans = []
        self.last_6_days_plans = []
        self.last_7_days_plans = []
        self.last_7_13_days_plans = []
        self.days_8_14_plans = []
        self.last_7_days_ps_surveys = []
        self.last_25_days_ps_surveys = []
        self.latest_plan_date = None
        self.last_7_days_readiness_surveys = []
        self.last_25_days_readiness_surveys = []
        self.days_8_14_ps_surveys = []
        self.days_8_14_readiness_surveys = []
        self.daily_internal_plans = []
        self.all_plans = []
        self.all_daily_readiness_surveys = []
        self.historic_data_loaded = False
        self.acute_symptoms = []
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

    @xray_recorder.capture('logic.StatsProcessing.process_athlete_stats')
    def process_athlete_stats(self, current_athlete_stats=None, force_historical_process=False):
        if self.start_date is None:
            self.set_start_end_times()
        self.load_historical_data()
        if current_athlete_stats is None:  # if no athlete_stats was passed, read from mongo
            current_athlete_stats = self.athlete_stats_datastore.get(athlete_id=self.athlete_id)

            if current_athlete_stats is None:  # if not found in mongo (first time use), create a new one
                current_athlete_stats = AthleteStats(self.athlete_id)
                current_athlete_stats.event_date = self.event_date
            if current_athlete_stats.event_date is None:
                current_athlete_stats.event_date = self.event_date

        soreness_list_25 = self.merge_soreness_from_surveys(
            self.get_readiness_soreness_list(self.last_25_days_readiness_surveys),
            self.get_ps_survey_soreness_list(self.last_25_days_ps_surveys),
            self.last_25_days_symptoms
        )

        training_volume_processing = TrainingVolumeProcessing(self.start_date,
                                                              format_date( self.event_date),
                                                              current_athlete_stats.load_stats)  # want event date since end date = event_date + 1

        # this gets updated in load plan values
        training_volume_processing.sport_max_load = current_athlete_stats.sport_max_load

        training_volume_processing.load_plan_values(self.last_7_days_plans,
                                                    self.days_8_14_plans,
                                                    self.acute_daily_plans,
                                                    self.get_chronic_weeks_plans(),
                                                    self.chronic_daily_plans
                                                    )

        sessions = training_volume_processing.get_training_sessions(self.all_plans)

        current_athlete_stats.sport_max_load = training_volume_processing.sport_max_load

        current_athlete_stats.load_stats = training_volume_processing.load_stats
        current_athlete_stats = training_volume_processing.calc_training_volume_metrics(current_athlete_stats)
        current_athlete_stats.high_relative_load_sessions = training_volume_processing.high_relative_load_sessions

        if current_athlete_stats.event_date.date() == self.event_date.date():
            # persist all of soreness/pain and session_RPE
            current_athlete_stats.session_RPE = current_athlete_stats.session_RPE
            current_athlete_stats.session_RPE_event_date = current_athlete_stats.session_RPE_event_date
            if force_historical_process:
                # New
                historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)
                injury_risk_processor = InjuryRiskProcessor(self.event_date, soreness_list_25, sessions,
                                                            historical_injury_risk_dict, current_athlete_stats, self.athlete_id)
                injury_risk_processor.process(update_historical_data=True)

                athlete_injury_risk = AthleteInjuryRisk(self.athlete_id)
                athlete_injury_risk.items = injury_risk_processor.injury_risk_dict

                self.injury_risk_datastore.put(athlete_injury_risk)

        else:  # nightly process (first update for the day)
            # clear these if it's a new day
            current_athlete_stats.session_RPE = None
            current_athlete_stats.session_RPE_event_date = None

            training_sessions = []
            training_sessions.extend(training_volume_processing.get_training_sessions(self.last_7_days_plans))
            training_sessions.extend(training_volume_processing.get_training_sessions(self.days_8_14_plans))

            historical_injury_risk_dict = self.injury_risk_datastore.get(self.athlete_id)
            injury_risk_processor = InjuryRiskProcessor(self.event_date, soreness_list_25, sessions,
                                                        historical_injury_risk_dict, current_athlete_stats, self.athlete_id)
            injury_risk_processor.process(update_historical_data=True)

            athlete_injury_risk = AthleteInjuryRisk(self.athlete_id)
            athlete_injury_risk.items = injury_risk_processor.injury_risk_dict

            self.injury_risk_datastore.put(athlete_injury_risk)

        current_athlete_stats.event_date = self.event_date
        return current_athlete_stats


    def load_historical_symptoms(self, symptoms):

        self.acute_symptoms = sorted([s for s in symptoms if self.acute_start_date_time is not None and
                                      s.reported_date_time >= self.acute_start_date_time],
                                     key=lambda x: x.reported_date_time)
        self.chronic_symptoms = sorted([s for s in symptoms if self.acute_start_date_time is not None and
                                        self.chronic_start_date_time is not None and
                                        self.acute_start_date_time > s.reported_date_time >= self.chronic_start_date_time],
                                       key=lambda x: x.reported_date_time)

        self.last_7_days_symptoms = [s for s in symptoms if self.last_week is not None and
                                     s.reported_date_time >= self.last_week]

        self.last_25_days_symptoms = [s for s in symptoms if self.last_25_days is not None and
                                      s.reported_date_time >= self.last_25_days]

        self.days_8_14_symptoms = [s for s in symptoms if self.last_week is not None
                                   and self.previous_week is not None and
                                   self.last_week > s.reported_date_time >= self.previous_week]