import math
import statistics
from collections import namedtuple
from datetime import datetime, timedelta

from fathomapi.utils.xray import xray_recorder
from logic.training_volume_processing import TrainingVolumeProcessing
from models.stats import AthleteStats
from models.soreness import Soreness, BodyPart, HistoricSorenessStatus
from models.historic_soreness import HistoricSoreness
from models.post_session_survey import PostSessionSurvey
from utils import parse_date, format_date


class StatsProcessing(object):

    def __init__(self, athlete_id, event_date, datastore_collection):
        self.athlete_id = athlete_id
        self.event_date = event_date
        self.athlete_stats_datastore = datastore_collection.athlete_stats_datastore
        self.daily_plan_datastore = datastore_collection.daily_plan_datastore
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

    def set_start_end_times(self):
        #start_date = datetime.strptime(self.event_date, "%Y-%m-%d")
        #end_date = datetime.strptime(self.event_date, "%Y-%m-%d")
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
    def process_athlete_stats(self, current_athlete_stats=None):
        if self.start_date is None:
            self.set_start_end_times()
        self.load_historical_data()
        athlete_stats = AthleteStats(self.athlete_id)
        athlete_stats.event_date = self.event_date
        athlete_stats = self.calc_survey_stats(athlete_stats)
        training_volume_processing = TrainingVolumeProcessing(self.start_date, self.end_date)
        training_volume_processing.load_plan_values(self.last_7_days_plans,
                                                    self.days_8_14_plans,
                                                    self.acute_daily_plans,
                                                    self.get_chronic_weeks_plans(),
                                                    self.chronic_daily_plans)
        athlete_stats = training_volume_processing.calc_training_volume_metrics(athlete_stats)
        if current_athlete_stats is None:
            current_athlete_stats = self.athlete_stats_datastore.get(athlete_id=self.athlete_id)
        athlete_stats.historic_soreness = self.get_historic_soreness(current_athlete_stats.historic_soreness if current_athlete_stats is not None else None)
        if current_athlete_stats is not None:
            athlete_stats.current_sport_name = current_athlete_stats.current_sport_name
            athlete_stats.current_position = current_athlete_stats.current_position
            athlete_stats.expected_weekly_workouts = current_athlete_stats.expected_weekly_workouts
            athlete_stats.exposed_triggers = current_athlete_stats.exposed_triggers
            athlete_stats.longitudinal_insights = current_athlete_stats.longitudinal_insights
            # Only persist readiness and ps soreness from today and yesterday
            athlete_stats.readiness_soreness = [s for s in current_athlete_stats.readiness_soreness if self.persist_soreness(s)]
            athlete_stats.post_session_soreness = [s for s in current_athlete_stats.post_session_soreness if self.persist_soreness(s)]
            athlete_stats.update_daily_soreness()
            athlete_stats.readiness_pain = [s for s in current_athlete_stats.readiness_pain if self.persist_soreness(s)]
            athlete_stats.post_session_pain = [s for s in current_athlete_stats.post_session_pain if self.persist_soreness(s)]
            athlete_stats.update_daily_pain()
            athlete_stats.daily_severe_soreness_event_date = self.event_date
            athlete_stats.daily_severe_pain_event_date = self.event_date
            athlete_stats.typical_weekly_sessions = current_athlete_stats.typical_weekly_sessions
            athlete_stats.wearable_devices = current_athlete_stats.wearable_devices
            if current_athlete_stats.event_date.date() == self.event_date.date():
                # persist all of soreness/pain and session_RPE
                athlete_stats.session_RPE = current_athlete_stats.session_RPE
                athlete_stats.session_RPE_event_date = current_athlete_stats.session_RPE_event_date
            # else:
                # training_volume_processing.fill_load_monitoring_measures(self.all_daily_readiness_surveys, self.all_plans, parse_date(self.event_date))
                # athlete_stats.muscular_strain_increasing = training_volume_processing.muscular_strain_increasing()
                # athlete_stats.high_relative_load_benchmarks = training_volume_processing.calc_high_relative_load_benchmarks()
                # athlete_stats.high_relative_load_session = training_volume_processing.high_relative_load_session
        #athlete_stats.completed_functional_strength_sessions = self.get_completed_functional_strength_sessions()
        #athlete_stats.functional_strength_eligible = self.is_athlete_functional_strength_eligible(athlete_stats)

        return athlete_stats

    @xray_recorder.capture('logic.StatsProcessing.load_historical_data')
    def load_historical_data(self):
        if not self.historic_data_loaded:
            self.all_plans = self.daily_plan_datastore.get(self.athlete_id, self.start_date, self.end_date, stats_processing=True)
            self.all_daily_readiness_surveys = [plan.daily_readiness_survey for plan in self.all_plans if plan.daily_readiness_survey is not None]
        post_session_surveys = []
        for plan in self.all_plans:
            post_surveys = \
                [PostSessionSurvey.post_session_survey_from_training_session(session.post_session_survey, self.athlete_id, session.id, session.session_type().value, plan.event_date)
                 for session in plan.training_sessions if session is not None]
            post_session_surveys.extend([s for s in post_surveys if s is not None])
        self.update_start_times(self.all_daily_readiness_surveys, post_session_surveys, self.all_plans)
        self.set_acute_chronic_periods()
        self.load_historical_readiness_surveys(self.all_daily_readiness_surveys)
        self.load_historical_post_session_surveys(post_session_surveys)
        self.load_historical_plans()
        self.historic_data_loaded = True

    def persist_soreness(self, soreness):
        if soreness.reported_date_time is not None:
            if (self.event_date.date() - soreness.reported_date_time.date()).days <= 1:
                return True
            else:
                return False
        else:
            return False

    def get_acute_training_sessions(self):

        training_sessions = []

        for a in self.acute_daily_plans:
            training_sessions.extend(a.training_sessions)

        return training_sessions

    @xray_recorder.capture('logic.StatsProcessing.get_historic_soreness')
    def get_historic_soreness(self, existing_historic_soreness=None):
        soreness_list_25 = self.merge_soreness_from_surveys(
            self.get_readiness_soreness_list(self.last_25_days_readiness_surveys),
            self.get_ps_survey_soreness_list(self.last_25_days_ps_surveys)
        )
        historic_soreness = self.get_historic_soreness_list(soreness_list_25, existing_historic_soreness)

        return historic_soreness

    def get_historic_soreness_list(self, soreness_list_25, existing_historic_soreness=None):

        grouped_soreness = {}

        acute_pain_list = []

        ns = namedtuple("ns", ["location", "side", "is_pain"])

        first_reported_date_time = None
        #last_reported_date = None
        last_reported_date_time = None
        days_since_last_report = None

        for s in soreness_list_25:

            ns_new = ns(s.body_part.location, s.side, s.pain)
            if ns_new in grouped_soreness:
                grouped_soreness[ns_new] = grouped_soreness[ns_new] + 1
            else:
                grouped_soreness[ns_new] = 1
            # if last_reported_date_time is None:
            #     first_reported_date_time = s.reported_date_time
            if last_reported_date_time is None or s.reported_date_time > last_reported_date_time:
                last_reported_date_time = s.reported_date_time
                #last_reported_date = s.reported_date_time
                days_since_last_report = (self.event_date - last_reported_date_time).days

        for g in grouped_soreness:

            # find any possible matching historic soreness
            historic_soreness = HistoricSoreness(g.location, g.side, g.is_pain)

            if existing_historic_soreness is not None:
                for h in existing_historic_soreness:
                    if h.is_pain == g.is_pain and h.side == g.side and h.body_part_location == g.location:
                        historic_soreness = h

            ask_acute_pain_question = False
            streak = 0
            streak_start_date = None
            body_part_history = list(s for s in soreness_list_25 if s.body_part.location ==
                                     g.location and s.side == g.side and s.pain == g.is_pain)
            body_part_history.sort(key=lambda x: x.reported_date_time, reverse=True)

            days_skipped = 0
            last_ten_day_count = 0
            last_fourteen_day_count = 0
            last_eight_seventeen_day_count = 0
            days_diff = 0

            if len(body_part_history) > 0:
                first_reported_date_time = min([s.reported_date_time for s in body_part_history])
                if historic_soreness.last_reported_date_time is not None:
                    last_reported_date_time = max(historic_soreness.last_reported_date_time, body_part_history[0].reported_date_time)
                else:
                    last_reported_date_time = body_part_history[0].reported_date_time
                if historic_soreness.first_reported_date_time is None:
                    historic_soreness.first_reported_date_time = first_reported_date_time
                if historic_soreness.last_reported_date_time == last_reported_date_time and \
                   historic_soreness.last_reported_date_time != body_part_history[0].reported_date_time and \
                   historic_soreness.historic_soreness_status == HistoricSorenessStatus.dormant_cleared:
                    body_part_history = []

            for b in range(0, len(body_part_history)):

                days_diff = (self.event_date - body_part_history[b].reported_date_time).days

                if days_diff < 14:
                    last_fourteen_day_count += 1
                if days_diff < 10:
                    last_ten_day_count += 1
                if 8 < days_diff < 17:
                    last_eight_seventeen_day_count += 1

            if historic_soreness.is_acute_pain():

                historic_soreness = self.process_acute_pain_status(body_part_history, historic_soreness,
                                                                   last_reported_date_time)

                acute_pain_list.append(historic_soreness)

            elif (historic_soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain or
                  historic_soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness):

                historic_soreness = self.process_persistent_2_status(body_part_history, days_diff, g.is_pain,
                                                                     historic_soreness,
                                                                     last_eight_seventeen_day_count,
                                                                     last_fourteen_day_count,
                                                                     last_reported_date_time, last_ten_day_count)
                acute_pain_list.append(historic_soreness)

            elif historic_soreness.is_persistent_pain() or historic_soreness.is_persistent_soreness():

                historic_soreness = self.process_persistent_status(g.is_pain, historic_soreness, last_reported_date_time, last_ten_day_count,
                                                                   body_part_history)
                acute_pain_list.append(historic_soreness)

            else:
                # looking for acute OR persistent pain

                if len(body_part_history) >= 2:

                    for b in range(0, len(body_part_history)):
                        if days_skipped <= 3:
                            if (streak_start_date is None or body_part_history[b].reported_date_time
                                    < streak_start_date):
                                streak_start_date = body_part_history[b].reported_date_time
                            if b < (len(body_part_history) - 1):
                                days_skipped = (body_part_history[b].reported_date_time -
                                                body_part_history[b + 1].reported_date_time).days

                            streak += 1

                if streak >= 3 and g.is_pain:  # check for acute pain FIRST
                    if days_since_last_report is not None and days_since_last_report > 3:
                        ask_acute_pain_question = True

                    avg_severity = self.calc_avg_severity_acute_pain(body_part_history, streak)

                    soreness = HistoricSoreness(g.location, g.side, True)
                    soreness.historic_soreness_status = HistoricSorenessStatus.acute_pain
                    soreness.ask_acute_pain_question = ask_acute_pain_question
                    soreness.ask_persistent_2_question = False
                    soreness.average_severity = avg_severity
                    soreness.first_reported_date_time = first_reported_date_time
                    soreness.last_reported_date_time = last_reported_date_time
                    soreness.streak_start_date = streak_start_date
                    soreness.streak = streak
                    acute_pain_list.append(soreness)

                elif streak == 2 and g.is_pain and days_since_last_report <= 3:  # check for acute pain FIRST

                    avg_severity = self.calc_avg_severity_acute_pain(body_part_history, streak)

                    soreness = HistoricSoreness(g.location, g.side, True)

                    if last_ten_day_count <= 3 and len(body_part_history) >= 5:  # persistent
                        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
                    soreness.ask_acute_pain_question = False
                    soreness.ask_persistent_2_question = False
                    soreness.average_severity = avg_severity
                    soreness.first_reported_date_time = first_reported_date_time
                    soreness.last_reported_date_time = last_reported_date_time
                    soreness.streak_start_date = streak_start_date

                    acute_pain_list.append(soreness)

                elif last_ten_day_count == 3 and len(body_part_history) >= 4:  # is it persistent?

                    avg_severity = self.calc_avg_severity_persistent_2(body_part_history, self.event_date)

                    if not g.is_pain and historic_soreness.historic_soreness_status == HistoricSorenessStatus.doms:
                        soreness = historic_soreness
                    else:
                        soreness = HistoricSoreness(g.location, g.side, g.is_pain)

                    if g.is_pain:
                        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
                    else:
                        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
                    soreness.ask_acute_pain_question = False
                    soreness.ask_persistent_2_question = False
                    soreness.average_severity = avg_severity
                    soreness.first_reported_date_time = first_reported_date_time
                    soreness.last_reported_date_time = last_reported_date_time
                    soreness.streak_start_date = None

                    acute_pain_list.append(soreness)

                elif last_ten_day_count < 3 and len(body_part_history) >= 5:  # is it persistent?

                    avg_severity = self.calc_avg_severity_persistent_2(body_part_history, self.event_date)

                    if not g.is_pain and historic_soreness.historic_soreness_status == HistoricSorenessStatus.doms:
                        soreness = historic_soreness
                    else:
                        soreness = HistoricSoreness(g.location, g.side, g.is_pain)

                    if g.is_pain:
                        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
                    else:
                        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
                    soreness.ask_acute_pain_question = False
                    soreness.ask_persistent_2_question = False
                    soreness.average_severity = avg_severity
                    soreness.first_reported_date_time = first_reported_date_time
                    soreness.last_reported_date_time = last_reported_date_time
                    soreness.streak_start_date = None

                    acute_pain_list.append(soreness)

                elif last_ten_day_count == 2 and len(body_part_history) >= 4:  # is it persistent?

                    avg_severity = self.calc_avg_severity_persistent_2(body_part_history, self.event_date)

                    soreness = HistoricSoreness(g.location, g.side, g.is_pain)
                    soreness.ask_acute_pain_question = False
                    soreness.ask_persistent_2_question = False
                    soreness.average_severity = avg_severity
                    soreness.first_reported_date_time = first_reported_date_time
                    soreness.last_reported_date_time = last_reported_date_time
                    soreness.streak_start_date = None

                    acute_pain_list.append(soreness)

                elif last_ten_day_count > 3 and len(body_part_history) >= 5:  # will we ever even get here?

                    avg_severity = self.calc_avg_severity_persistent_2(body_part_history, self.event_date)

                    soreness = HistoricSoreness(g.location, g.side, g.is_pain)
                    if g.is_pain:
                        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
                    else:
                        soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
                    soreness.ask_acute_pain_question = False
                    soreness.ask_persistent_2_question = False
                    soreness.average_severity = avg_severity
                    soreness.first_reported_date_time = first_reported_date_time
                    soreness.last_reported_date_time = last_reported_date_time
                    soreness.streak_start_date = None

                    acute_pain_list.append(soreness)

                else:

                    soreness = HistoricSoreness(g.location, g.side, g.is_pain)

                    soreness.historic_soreness_status = HistoricSorenessStatus.dormant_cleared
                    soreness.ask_acute_pain_question = False
                    soreness.ask_persistent_2_question = False
                    soreness.average_severity = 0.0
                    soreness.first_reported_date_time = first_reported_date_time
                    soreness.last_reported_date_time = last_reported_date_time
                    soreness.streak_start_date = None

                    acute_pain_list.append(soreness)

        return acute_pain_list

    def process_acute_pain_status(self, body_part_history, historic_soreness, last_reported_date_time):

        if len(body_part_history) > 0:
            if historic_soreness.last_reported_date_time is not None:
                last_reported_date_time = max(historic_soreness.last_reported_date_time, body_part_history[0].reported_date_time)
            else:
                last_reported_date_time = body_part_history[0].reported_date_time
        if (self.event_date - last_reported_date_time).days > 3:
            historic_soreness.ask_acute_pain_question = True
        if len(body_part_history) > 0:
            historic_soreness.last_reported = body_part_history[0].reported_date_time
            streak = 0
            for b in body_part_history:
                if b.reported_date_time >= historic_soreness.streak_start_date:
                    streak += 1
            historic_soreness.streak = streak
            historic_soreness.average_severity = self.calc_avg_severity_acute_pain(body_part_history, streak)
        if ((last_reported_date_time - historic_soreness.streak_start_date).days >= 7
                and not historic_soreness.ask_acute_pain_question):
            historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
            historic_soreness.average_severity = self.calc_avg_severity_persistent_2(body_part_history,
                                                                                     self.event_date)
        elif ((self.event_date - historic_soreness.streak_start_date).days >= 7
              and not historic_soreness.ask_acute_pain_question):
            historic_soreness.historic_soreness_status = HistoricSorenessStatus.acute_pain
            historic_soreness.average_severity = self.calc_avg_severity_persistent_2(body_part_history,
                                                                                     self.event_date)

        return historic_soreness

    def process_persistent_2_status(self, body_part_history, days_diff, is_pain, historic_soreness,
                                    last_eight_seventeen_day_count, last_fourteen_day_count, last_reported_date_time,
                                    last_ten_day_count):
        if last_fourteen_day_count == 0:
            if is_pain:
                historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
            else:
                historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
            historic_soreness.ask_acute_pain_question = False
            historic_soreness.ask_persistent_2_question = True
            historic_soreness.streak_start_date = None

        elif last_ten_day_count <= 3 and len(body_part_history) >= 5:  # is it persistent pain?

            if (last_eight_seventeen_day_count <= 3 and days_diff >= 14 and
                    body_part_history[0].reported_date_time == self.event_date):
                if is_pain:
                    historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_pain
                else:
                    historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_soreness
                historic_soreness.ask_acute_pain_question = False
                historic_soreness.ask_persistent_2_question = False
                historic_soreness.streak_start_date = None
        historic_soreness.average_severity = self.calc_avg_severity_persistent_2(body_part_history, self.event_date)
        historic_soreness.last_reported_date_time = last_reported_date_time
        return historic_soreness

    def process_persistent_status(self, is_pain, historic_soreness, last_reported_date, last_ten_day_count,
                                  body_part_history):
        if (self.event_date - last_reported_date).days > 14:
            historic_soreness.ask_persistent_2_question = True  # same question even though different status
        if len(body_part_history) > 0:
            historic_soreness.last_reported_date_time = body_part_history[0].reported_date_time
        if last_ten_day_count > 3:
            if is_pain:
                historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
            else:
                historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_2_soreness
            historic_soreness.ask_acute_pain_question = False
            historic_soreness.ask_persistent_2_question = False
        historic_soreness.average_severity = self.calc_avg_severity_persistent_2(body_part_history, self.event_date)

        return historic_soreness

    @staticmethod
    def calc_avg_severity_acute_pain(body_part_history, streak):
        denom_sum = 0
        severity = 0.0

        last_day_in_streak = body_part_history[0].reported_date_time
        for b in range(0, streak):
            days_difference = (last_day_in_streak - body_part_history[b].reported_date_time).days
            severity += body_part_history[b].severity * (math.exp(-1.0 * days_difference))
            denom_sum += math.exp(-1.0 * days_difference)
        avg_severity = severity / float(denom_sum)

        return avg_severity

    @staticmethod
    def calc_avg_severity_persistent_2(body_part_history, current_date):

        denom_sum = 0
        severity = 0.0

        for b in range(0, 10):
            days_ago = current_date - timedelta(days=b)

            for h in body_part_history:
                if h.reported_date_time == days_ago:
                    severity += h.severity * (math.exp(-0.7 * b))
                    denom_sum += math.exp(-0.7 * b)
        if denom_sum > 0:
            avg_severity = severity / float(denom_sum)
        else:
            avg_severity = severity

        return avg_severity

    def answer_acute_pain_question(self, existing_historic_soreness, soreness_list_25, body_part_location, side, is_pain, question_response_date, severity_value):

        body_part_history = list(s for s in soreness_list_25 if s.body_part.location ==
                                 body_part_location and s.side == side and s.pain)
        body_part_history.sort(key=lambda x: x.reported_date_time, reverse=True)

        last_ten_day_count = 0
        last_fourteen_day_count = 0
        last_eight_seventeen_day_count = 0

        for b in range(0, len(body_part_history)):

            days_diff = (self.event_date - body_part_history[b].reported_date_time).days

            if days_diff < 14:
                last_fourteen_day_count += 1
            if days_diff < 10:
                last_ten_day_count += 1
            if 8 < days_diff < 17:
                last_eight_seventeen_day_count += 1

        for e in existing_historic_soreness:
            if e.body_part_location == body_part_location and e.side == side and e.is_pain:
                if e.is_acute_pain():
                    if severity_value is not None and severity_value > 0 and is_pain:
                        new_soreness = Soreness()
                        new_soreness.body_part = BodyPart(body_part_location, None)
                        new_soreness.side = side
                        new_soreness.pain = True
                        new_soreness.severity = severity_value
                        new_soreness.reported_date_time = question_response_date
                        body_part_history.append(new_soreness)
                        body_part_history.sort(key=lambda x: x.reported_date_time, reverse=True)

                        last_ten_day_count += 1
                        last_fourteen_day_count += 1
                        e.ask_acute_pain_question = False
                        # should we migrate to persistent-2?
                        if (question_response_date - e.streak_start_date).days >= 7:
                            e.historic_soreness_status = HistoricSorenessStatus.persistent_2_pain
                        if (question_response_date - e.streak_start_date).days == 6:
                            e.historic_soreness_status = HistoricSorenessStatus.acute_pain
                            e.streak += 1
                            e.average_severity = self.calc_avg_severity_acute_pain(body_part_history, e.streak)
                        else:
                            e.streak += 1
                    else:
                        e.last_reported_date_time = question_response_date
                        e.ask_acute_pain_question = False
                        e.historic_soreness_status = HistoricSorenessStatus.dormant_cleared

        return existing_historic_soreness

    def answer_persistent_2_question(self, existing_historic_soreness,  soreness_list_25, body_part_location, side, is_pain, question_response_date, severity_value, current_status):

        body_part_history = list(s for s in soreness_list_25 if s.body_part.location ==
                                 body_part_location and s.side == side and s.pain)
        body_part_history.sort(key=lambda x: x.reported_date_time, reverse=True)

        last_ten_day_count = 0
        last_fourteen_day_count = 0
        last_eight_seventeen_day_count = 0
        days_diff = 0

        for b in range(0, len(body_part_history)):

            days_diff = (parse_date(self.event_date) - parse_date(body_part_history[b].reported_date_time)).days

            if days_diff < 14:
                last_fourteen_day_count += 1
            if days_diff < 10:
                last_ten_day_count += 1
            if 8 < days_diff < 17:
                last_eight_seventeen_day_count += 1

        for e in existing_historic_soreness:
            if e.body_part_location == body_part_location and e.side == side and e.historic_soreness_status == current_status:
                if (e.is_persistent_soreness() or e.is_persistent_pain() or
                        e.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain or
                        e.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness):
                    if severity_value is not None and severity_value > 0 and e.is_pain == is_pain:
                        new_soreness = Soreness()
                        new_soreness.body_part = BodyPart(body_part_location, None)
                        new_soreness.side = side
                        new_soreness.pain = is_pain
                        new_soreness.severity = severity_value
                        new_soreness.reported_date_time = question_response_date
                        body_part_history.append(new_soreness)
                        body_part_history.sort(key=lambda x: x.reported_date_time, reverse=True)

                        last_ten_day_count += 1
                        last_fourteen_day_count += 1

                        if e.is_persistent_soreness() or e.is_persistent_pain():
                            e = self.process_persistent_status(is_pain, e, question_response_date, last_ten_day_count,
                                                               body_part_history)
                        else:
                            e = self.process_persistent_2_status(body_part_history, days_diff, is_pain, e,
                                                                 last_eight_seventeen_day_count, last_fourteen_day_count,
                                                                 question_response_date, last_ten_day_count)
                        e.ask_persistent_2_question = False

                    else:
                        e.last_reported_date_time = question_response_date
                        e.ask_persistent_2_question = False
                        e.historic_soreness_status = HistoricSorenessStatus.dormant_cleared

        return existing_historic_soreness

    def get_soreness_streaks(self, soreness_list):

        grouped_soreness = {}
        streak_soreness = {}
        streak_start_soreness = {}

        ns = namedtuple("ns", ["location", "is_pain", "side"])
        ns_2 = namedtuple("ns", ["location", "is_pain", "side", "avg_severity"])

        for s in soreness_list:
            ns_new = ns(s.body_part.location, s.pain, s.side)
            if ns_new in grouped_soreness:
                grouped_soreness[ns_new] = grouped_soreness[ns_new] + 1
            else:
                grouped_soreness[ns_new] = 1

        for g in grouped_soreness:
            streak = 1
            streak_start_date = None
            body_part_history = list(s for s in soreness_list if s.body_part.location ==
                                     g.location and s.side == g.side and s.pain == g.is_pain)
            body_part_history.sort(key=lambda x: x.reported_date_time, reverse=True)
            severity = 0.0
            if len(body_part_history) >= 2:
                for b in range(0, len(body_part_history)-1):
                    if (streak_start_date is None or body_part_history[b].reported_date_time
                            < parse_date(streak_start_date)):
                        streak_start_date = body_part_history[b].reported_date_time
                    days_skipped = (body_part_history[b].reported_date_time -
                                    body_part_history[b + 1].reported_date_time).days

                    if days_skipped <= 3:
                        streak += 1
                    else:
                        break

            for b in range(0, streak):
                severity += body_part_history[b].severity

            nsd_new = ns_2(g.location, g.is_pain, g.side, severity/float(streak))
            ns_ss = ns_2(g.location, g.is_pain, g.side, severity/float(streak))
            streak_soreness[nsd_new] = streak
            streak_start_soreness[ns_ss] = streak_start_date

        return streak_soreness, streak_start_soreness

    def merge_soreness_from_surveys(self, readiness_survey_soreness_list, ps_survey_soreness_list):

        soreness_list = []
        merged_soreness_list = []

        soreness_list.extend(readiness_survey_soreness_list)
        soreness_list.extend(ps_survey_soreness_list)

        grouped_soreness = {}

        ns = namedtuple("ns", ["location", "is_pain", "side", "reported_date_time"])

        for s in soreness_list:
            ns_new = ns(s.body_part.location, s.pain, s.side, s.reported_date_time)
            if ns_new in grouped_soreness:
                grouped_soreness[ns_new] = max(grouped_soreness[ns_new], s.severity)
            else:
                grouped_soreness[ns_new] = s.severity

        for r in grouped_soreness:

            s = Soreness()
            s.body_part = BodyPart(r.location, None)
            s.side = r.side
            s.reported_date_time = r.reported_date_time
            s.severity = grouped_soreness[r]
            s.pain = r.is_pain
            merged_soreness_list.append(s)

        return merged_soreness_list

    def get_hs_dictionary(self, soreness_list):

        historic_soreness = {}
        historic_soreness_reported = {}

        soreness_list.sort(key=lambda x: x.reported_date_time if x.reported_date_time is not None else '', reverse=False)

        hs = namedtuple("hs", ["location", "is_pain", "side"])

        for s in soreness_list:
            hs_new = hs(s.body_part.location, s.pain, s.side)
            if hs_new in historic_soreness:
                historic_soreness[hs_new] = historic_soreness[hs_new] + 1
            else:
                historic_soreness[hs_new] = 1
            historic_soreness_reported[hs_new] = s.reported_date_time

        return historic_soreness, historic_soreness_reported

    def get_chronic_weeks_plans(self):

        weeks_list = []

        if self.chronic_days is not None:

            week4_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time is not None and
                              self.acute_start_date_time - timedelta(days=min(28, self.chronic_days)) <=
                              d.get_event_datetime() < self.acute_start_date_time - timedelta(days=min(21, self.chronic_days))]
            week3_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time is not None and self.acute_start_date_time
                              - timedelta(days=min(21, self.chronic_days)) <= d.get_event_datetime() < self.acute_start_date_time -
                              timedelta(days=min(14, self.chronic_days))]
            week2_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time is not None and self.acute_start_date_time
                              - timedelta(days=min(14, self.chronic_days)) <= d.get_event_datetime() < self.acute_start_date_time -
                              timedelta(days=min(7, self.chronic_days))]
            week1_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time is not None and self.acute_start_date_time
                              - timedelta(days=min(7, self.chronic_days)) <= d.get_event_datetime() < self.acute_start_date_time]

            weeks_list = [week1_sessions, week2_sessions, week3_sessions, week4_sessions]

        return weeks_list

    def get_ps_survey_soreness_list(self, survey_list):

        soreness_list = []

        for c in survey_list:

            for s in c.survey.soreness:
                s.reported_date_time = format_date(c.event_date)
                soreness_list.append(s)

        return soreness_list

    def get_readiness_soreness_list(self, survey_list):

        soreness_list = []

        for c in survey_list:

            for s in c.soreness:
                #s.reported_date_time = format_date(c.event_date)
                s.reported_date_time = c.event_date
                soreness_list.append(s)

        return soreness_list

    '''deprecated
    def is_athlete_functional_strength_eligible(self, athlete_stats):

        # completed yesterday?
        # completed_yesterday = self.functional_strength_yesterday()

        # onboarded > 2 weeks?
        two_plus_weeks_since_onboarding = self.is_athlete_two_weeks_from_onboarding()

        # active prep / active recovery checks
        two_apar_sessions_completed = self.athlete_has_enough_active_prep_recovery_sessions()

        # logged sessions
        four_plus_training_sessions_logged = self.athlete_logged_enough_sessions()

        # no pain >=3 and soreness >=4 in the last two days
        severe_pain_soreness = athlete_stats.severe_pain_soreness_today()

        # wrapping it all up
        if (two_plus_weeks_since_onboarding and
            two_apar_sessions_completed and
            four_plus_training_sessions_logged and
            not severe_pain_soreness and
            athlete_stats.completed_functional_strength_sessions < 3):
            return True
        else:
            return False

    def functional_strength_yesterday(self):

        yesterday = format_date(parse_date(self.event_date) - timedelta(1))

        completed_sessions = [a for a in self.last_7_days_plans if a.functional_strength_completed if a is not None
                              and a.event_date == yesterday]

        if len(completed_sessions) > 0:
            return True

        return False
    
    def athlete_logged_enough_sessions(self):

        four_plus_training_sessions_logged = False
        logged_session_plans = []

        logged_session_plans.extend(self.last_7_days_ps_surveys)

        logged_session_plans.extend(self.days_8_14_ps_surveys)

        if len(logged_session_plans) > 4:
            four_plus_training_sessions_logged = True

        return four_plus_training_sessions_logged

    def athlete_has_enough_active_prep_recovery_sessions(self):

        two_apar_sessions_completed = False
        apar_sessions_completed_count_7 = 0
        apar_sessions_completed_count_14 = 0

        active_prep_completed_plans_7 = [a for a in self.last_7_days_plans if a.pre_recovery_completed if a is not None]
        active_rec_completed_plans_7 = [a for a in self.last_7_days_plans if a.post_recovery_completed if a is not None]
        active_prep_completed_plans_14 = [a for a in self.days_8_14_plans if a.pre_recovery_completed if a is not None]
        active_rec_completed_plans_14 = [a for a in self.days_8_14_plans if a.post_recovery_completed if a is not None]

        if active_prep_completed_plans_7 is not None and active_rec_completed_plans_7 is not None:
            apar_sessions_completed_count_7 = (apar_sessions_completed_count_7 + len(active_prep_completed_plans_7) +
                                               len(active_rec_completed_plans_7))

        if active_prep_completed_plans_14 is not None and active_rec_completed_plans_14 is not None:
            apar_sessions_completed_count_14 = (apar_sessions_completed_count_14 + len(active_prep_completed_plans_14) +
                                                len(active_rec_completed_plans_14))

        if apar_sessions_completed_count_7 >= 2 and apar_sessions_completed_count_14 >= 2:
            two_apar_sessions_completed = True

        return two_apar_sessions_completed

    def is_athlete_two_weeks_from_onboarding(self):

        two_plus_weeks_since_onboarding = False

        if self.chronic_readiness_surveys is not None and len(self.chronic_readiness_surveys) > 0:
            days_diff = (
                        parse_date(self.event_date) - self.chronic_readiness_surveys[0].event_date).days

            if days_diff >= 13:  # for difference, we need one less than fourteen
                two_plus_weeks_since_onboarding = True

        return two_plus_weeks_since_onboarding

    def get_completed_functional_strength_sessions(self):

        completed_sesions = [a for a in self.last_7_days_plans if a.functional_strength_completed if a is not None]

        return len(completed_sesions)
    '''
    def calc_survey_stats(self, athlete_stats):

        if len(self.acute_readiness_surveys) > 0:

            acute_readiness_values = [x.readiness for x in self.acute_readiness_surveys if x is not None and x.readiness is not None]
            acute_sleep_quality_values = [x.sleep_quality for x in self.acute_readiness_surveys if x is not None and x.sleep_quality is not None]

            chronic_readiness_values = [x.readiness for x in self.chronic_readiness_surveys if x is not None and x.readiness is not None]
            chronic_sleep_quality_values = [x.sleep_quality for x in self.chronic_readiness_surveys if x is not None and x.sleep_quality is not None]

            acute_RPE_values = [x.survey.RPE for x in self.acute_post_session_surveys if x.survey.RPE is not None]
            chronic_RPE_values = [x.survey.RPE for x in self.chronic_post_session_surveys if x.survey.RPE is not None]

            dates_difference = self.end_date_time - self.start_date_time

            max_acute_soreness_values = []
            max_persistent_2_soreness_values = []

            acute_soreness_values = []
            persistent_2_soreness_values = []

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

                persistent_2_soreness_values.extend(chronic_post_soreness_values)
                persistent_2_soreness_values.extend(chronic_readiness_soreness_values)

                if len(persistent_2_soreness_values) > 0:
                    max_persistent_2_soreness_values.append(max(persistent_2_soreness_values))

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

            if len(max_persistent_2_soreness_values) > 0:
                athlete_stats.chronic_avg_max_soreness = statistics.mean(max_persistent_2_soreness_values)

        return athlete_stats

    def get_acute_internal_values(self):

        acute_values = list(x[1] for x in self.acute_daily_plans if x[1] is not None)

        return acute_values

    def get_chronic_daily_values_by_week(self):

        weeks_values = {}

        weeks_plans = self.get_chronic_weeks_plans()

        index = 0
        for w in weeks_plans:
            weekly_values = list(x[1] for x in w if x[1] is not None)
            weeks_values[index] = weekly_values
            index += 1

        return weeks_values

    def load_historical_readiness_surveys(self, daily_readiness_surveys):

        self.acute_readiness_surveys = sorted([p for p in daily_readiness_surveys
                                               if self.acute_start_date_time is not None and p.event_date >= self.acute_start_date_time],
                                              key=lambda x: x.event_date)

        self.chronic_readiness_surveys = sorted([p for p in daily_readiness_surveys if self.acute_start_date_time is not None
                                                 and self.chronic_start_date_time is not None and self.acute_start_date_time >
                                                 p.event_date >= self.chronic_start_date_time],
                                                key=lambda x: x.event_date)

        self.last_7_days_readiness_surveys = [p for p in daily_readiness_surveys if self.last_week is not None and p.event_date >= self.last_week]

        self.last_25_days_readiness_surveys = [p for p in daily_readiness_surveys if self.last_25_days is not None and p.event_date >= self.last_25_days]

        self.days_8_14_readiness_surveys = [p for p in daily_readiness_surveys if self.last_week is not None and self.previous_week is not None and
                                            self.last_week > p.event_date >= self.previous_week]

    def load_historical_post_session_surveys(self, post_session_surveys):

        self.acute_post_session_surveys = sorted([p for p in post_session_surveys
                                                  if self.acute_start_date_time is not None and p.event_date_time >= self.acute_start_date_time],
                                                 key=lambda x: x.event_date)
        self.chronic_post_session_surveys = sorted([p for p in post_session_surveys
                                                    if self.acute_start_date_time is not None and self.chronic_start_date_time is not None and
                                                    self.acute_start_date_time > p.event_date_time >= self.chronic_start_date_time],
                                                   key=lambda x: x.event_date)

        self.last_7_days_ps_surveys = [p for p in post_session_surveys if self.last_week is not None and p.event_date_time >= self.last_week]

        self.last_25_days_ps_surveys = [p for p in post_session_surveys if self.last_25_days is not None and p.event_date_time >= self.last_25_days]

        self.days_8_14_ps_surveys = [p for p in post_session_surveys if self.last_week is not None
                                     and self.previous_week is not None and self.last_week > p.event_date_time >= self.previous_week]

    def update_start_times(self, daily_readiness_surveys, post_session_surveys, daily_plans):

        if daily_readiness_surveys is not None and len(daily_readiness_surveys) > 0:
            daily_readiness_surveys.sort(key=lambda x: x.event_date, reverse=False)
            # self.earliest_survey_date_time = daily_readiness_surveys[0].event_date
            self.start_date_time = max(self.start_date_time, daily_readiness_surveys[0].event_date)
        else:
            return

        if post_session_surveys is not None and len(post_session_surveys) > 0:
            post_session_surveys.sort(key=lambda x: x.event_date_time, reverse=False)
            # self.earliest_survey_date_time = min(self.earliest_survey_date_time,
            #                                     post_session_surveys[0].event_date_time)
            self.start_date_time = min(self.start_date_time, post_session_surveys[0].event_date_time)

        self.latest_plan_date = self.end_date_time

        if daily_plans is not None and len(daily_plans) > 0:
            daily_plans.sort(key=lambda x: x.event_date, reverse=False)
            self.latest_plan_date = parse_date(daily_plans[len(daily_plans) - 1].event_date)

    def set_acute_chronic_periods(self):

        # add one since survey is first thing done in the day
        days_difference = (self.end_date_time - self.start_date_time).days + 1

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
        if self.latest_plan_date is not None and self.event_date > self.latest_plan_date:
            adjustment_factor = (self.event_date - self.latest_plan_date).days

        if self.acute_days is not None and self.chronic_days is not None:
            self.acute_start_date_time = self.end_date_time - timedelta(days=self.acute_days + adjustment_factor)
            self.chronic_start_date_time = self.end_date_time - timedelta(
                days=self.chronic_days + acute_days_adjustment + adjustment_factor)
            chronic_date_time = self.acute_start_date_time - timedelta(days=self.chronic_days)
            chronic_delta = self.end_date_time - chronic_date_time
            self.chronic_load_start_date_time = self.end_date_time - chronic_delta

        self.last_week = self.end_date_time - timedelta(days=7 + adjustment_factor)
        self.last_6_days = self.end_date_time - timedelta(days=6 + adjustment_factor)
        self.last_25_days = self.end_date_time - timedelta(days=25 + adjustment_factor)
        self.previous_week = self.last_week - timedelta(days=7)
        self.days_7_13 = self.previous_week + timedelta(days=1)

    def load_historical_plans(self):

        self.acute_daily_plans = sorted([p for p in self.all_plans if self.acute_start_date_time is not None and p.get_event_datetime() >=
                                         self.acute_start_date_time], key=lambda x: x.event_date)

        self.chronic_daily_plans = sorted([p for p in self.all_plans if self.acute_start_date_time is not None and
                                           self.chronic_load_start_date_time is not None and self.acute_start_date_time >
                                           p.get_event_datetime() >= self.chronic_load_start_date_time],
                                          key=lambda x: x.event_date)

        self.last_6_days_plans = [p for p in self.all_plans if p.get_event_datetime() >= self.last_6_days]

        self.last_7_days_plans = [p for p in self.all_plans if p.get_event_datetime() >= self.last_week]

        self.last_7_13_days_plans = [p for p in self.all_plans if self.last_6_days > p.get_event_datetime() >= self.days_7_13]

        self.days_8_14_plans = [p for p in self.all_plans if self.last_week > p.get_event_datetime() >= self.previous_week]
