from models.stats import AthleteStats
from models.metrics import AthleteRecommendation
from models.soreness import Soreness, BodyPart, BodyPartLocation
from datetime import datetime, timedelta
import statistics
from utils import parse_date, parse_datetime, format_date
from fathomapi.utils.exceptions import NoSuchEntityException
from models.soreness import HistoricSoreness, HistoricSorenessStatus
from collections import namedtuple
from itertools import groupby
from operator import itemgetter

class StatsProcessing(object):

    def __init__(self, athlete_id, event_date, datastore_collection):
        self.athlete_id = athlete_id
        self.event_date = event_date
        self.daily_readiness_datastore = datastore_collection.daily_readiness_datastore
        self.post_session_survey_datastore = datastore_collection.post_session_survey_datastore
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
        self.acute_readiness_surveys = []
        self.chronic_readiness_surveys = []
        self.acute_post_session_surveys = []
        self.chronic_post_session_surveys = []
        self.acute_daily_plans = []
        self.chronic_daily_plans = []
        self.last_7_days_plans = []
        self.days_8_14_plans = []
        self.last_7_days_ps_surveys = []
        self.last_7_days_readiness_surveys = []
        self.days_8_14_ps_surveys = []
        self.days_8_14_readiness_surveys = []
        self.days_15_21_ps_surveys = []
        self.days_15_21_readiness_surveys = []
        self.days_22_28_ps_surveys = []
        self.days_22_28_readiness_surveys = []

    def set_start_end_times(self):
        if self.event_date is None:
            try:
                readiness_surveys = self.daily_readiness_datastore.get(self.athlete_id)
            except NoSuchEntityException:
                return False
            last_daily_readiness_survey = readiness_surveys[0]
            event_date_time = last_daily_readiness_survey.get_event_date()
            self.event_date = event_date_time.date().strftime('%Y-%m-%d')
        start_date = datetime.strptime(self.event_date, "%Y-%m-%d")
        end_date = datetime.strptime(self.event_date, "%Y-%m-%d")
        self.start_date_time = start_date - timedelta(days=28)
        self.end_date_time = end_date + timedelta(days=1)
        self.start_date = self.start_date_time.strftime('%Y-%m-%d')
        self.end_date = self.end_date_time.strftime('%Y-%m-%d')
        return True

    def process_athlete_stats(self):
        success = self.set_start_end_times()
        if success:
            self.load_historical_data()
            athlete_stats = AthleteStats(self.athlete_id)
            athlete_stats.event_date = self.event_date
            athlete_stats = self.calc_survey_stats(athlete_stats)
            athlete_stats = self.calc_training_volume_metrics(athlete_stats)
            athlete_stats.functional_strength_eligible = self.is_athlete_functional_strength_eligible()
            athlete_stats.completed_functional_strength_sessions = self.get_completed_functional_strength_sessions()
            athlete_stats.historic_soreness = self.get_historic_soreness()
            athlete_stats.three_day_consecutive_pain = self.get_three_days_consecutive_pain_list()
            current_athlete_stats = self.athlete_stats_datastore.get(athlete_id=self.athlete_id)
            if current_athlete_stats is not None:
                athlete_stats.current_sport_name = current_athlete_stats.current_sport_name
                athlete_stats.current_position = current_athlete_stats.current_position
            self.athlete_stats_datastore.put(athlete_stats)


    def get_athlete_metrics(self, athlete_id, event_date):

        athlete_metric = AthleteRecommendation()
        athlete_metric.three_day_consecutive_pain = 0.0

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
            x for x in self.get_plan_session_attribute_sum("external_load", self.last_7_days_plans) if x is not None)

        last_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               self.last_7_days_plans) if x is not None)
        previous_week_external_values.extend(
            x for x in self.get_plan_session_attribute_sum("external_load", self.days_8_14_plans) if x is not None)

        previous_week_internal_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               self.days_8_14_plans) if x is not None)

        a_external_load_values.extend(
            x for x in self.get_plan_session_attribute_sum("external_load", self.acute_daily_plans) if x is not None)


        a_internal_load_values.extend(
            x for x in self.get_session_attributes_product_sum("session_RPE", "duration_minutes",
                                                               self.acute_daily_plans) if x is not None)

        a_external_load_values.extend(
            x for x in self.get_plan_session_attribute_sum("external_load", self.acute_daily_plans) if x is not None)

        a_high_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("high_intensity_load", self.acute_daily_plans) if
            x is not None)

        a_mod_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("mod_intensity_load", self.acute_daily_plans) if
            x is not None)

        a_low_intensity_values.extend(
            x for x in self.get_plan_session_attribute_sum("low_intensity_load", self.acute_daily_plans) if
            x is not None)

        weeks_list = self.get_chronic_weeks_plans()

        for w in weeks_list:

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

    def get_historic_soreness(self):

        soreness_list = []

        soreness_list_last_7_days = self.merge_soreness_from_surveys(
            self.get_readiness_soreness_list(self.last_7_days_readiness_surveys),
            self.get_ps_survey_soreness_list(self.last_7_days_ps_surveys)
        )

        soreness_list_8_14_days = self.merge_soreness_from_surveys(
            self.get_readiness_soreness_list(self.days_8_14_readiness_surveys),
            self.get_ps_survey_soreness_list(self.days_8_14_ps_surveys)
        )

        soreness_list_15_21_days = self.merge_soreness_from_surveys(
            self.get_readiness_soreness_list(self.days_15_21_readiness_surveys),
            self.get_ps_survey_soreness_list(self.days_15_21_ps_surveys)
        )

        soreness_list_22_28_days = self.merge_soreness_from_surveys(
            self.get_readiness_soreness_list(self.days_22_28_readiness_surveys),
            self.get_ps_survey_soreness_list(self.days_22_28_ps_surveys)
        )

        soreness_list.extend(soreness_list_last_7_days)
        soreness_list.extend(soreness_list_8_14_days)
        soreness_list.extend(soreness_list_15_21_days)
        soreness_list.extend(soreness_list_22_28_days)

        streak_soreness = self.get_soreness_streaks(soreness_list)

        historic_soreness = self.get_historic_soreness_list(soreness_list_last_7_days,
                                                            soreness_list_8_14_days,
                                                            soreness_list_15_21_days,
                                                            soreness_list_22_28_days)

        for h in range(0,len(historic_soreness)):
            for s in streak_soreness:
                if (s.side == historic_soreness[h].side and s.is_pain == historic_soreness[h].is_pain
                        and s.location == historic_soreness[h].body_part_location):
                    historic_soreness[h].streak = streak_soreness[s]
                    historic_soreness[h].average_severity = s.avg_severity

        return historic_soreness

    def get_soreness_streaks(self, soreness_list):

        grouped_soreness = {}
        streak_soreness = {}

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
            body_part_history = list(s for s in soreness_list if s.body_part.location ==
                                     g.location and s.side == g.side and s.pain == g.is_pain)
            body_part_history.sort(key=lambda x: x.reported_date_time, reverse=True)
            severity = 0.0
            if len(body_part_history) >= 2:
                for b in range(0,len(body_part_history)-1):
                    days_skipped = (parse_date(body_part_history[b].reported_date_time) -
                                    parse_date(body_part_history[b + 1].reported_date_time)).days

                    if days_skipped <= 3:
                        streak += 1
                    else:
                        break

            for b in range(0, streak):
                severity += body_part_history[b].severity

            nsd_new = ns_2(g.location, g.is_pain, g.side, severity/float(streak))
            streak_soreness[nsd_new] = streak

        return streak_soreness

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
            if r.is_pain:
                s = Soreness()
                s.body_part = BodyPart(r.location, None)
                s.side = r.side
                s.reported_date_time = r.reported_date_time
                s.severity = grouped_soreness[r]
                merged_soreness_list.append(s)

        return merged_soreness_list

    def get_historic_soreness_list(self, soreness_last_7, soreness_8_14, soreness_15_21, soreness_22_28):

        historic_soreness_list = []

        historic_soreness_last_7 = self.get_hs_dictionary(soreness_last_7)
        historic_soreness_8_14 = self.get_hs_dictionary(soreness_8_14)
        historic_soreness_15_21 = self.get_hs_dictionary(soreness_15_21)
        historic_soreness_22_28 = self.get_hs_dictionary(soreness_22_28)

        for h in historic_soreness_8_14:
            historic_soreness = HistoricSoreness(h.location, h.side, h.is_pain)
            if h not in historic_soreness_last_7 and h in historic_soreness_15_21 and h in historic_soreness_22_28:
                historic_soreness.historic_soreness_status = HistoricSorenessStatus.almost_persistent
                historic_soreness_list.append(historic_soreness)

        for h in historic_soreness_last_7:
            historic_soreness = HistoricSoreness(h.location, h.side, h.is_pain)

            if historic_soreness_last_7[h] > 2:

                if h in historic_soreness_8_14 and h in historic_soreness_15_21 and h in historic_soreness_22_28:
                    if (historic_soreness_8_14[h] >= 3 and historic_soreness_15_21[h] >= 3
                            and historic_soreness_22_28[h] >= 3):
                        historic_soreness.historic_soreness_status = HistoricSorenessStatus.chronic
                    else:
                        historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent

            elif historic_soreness_last_7[h] == 2:
                if h in historic_soreness_8_14 and h in historic_soreness_15_21 and h in historic_soreness_22_28:
                    if (historic_soreness_8_14[h] >= 3 and historic_soreness_15_21[h] >= 3
                            and historic_soreness_22_28[h] >= 3):
                        historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent_almost_chronic
                    else:
                        historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent

            elif historic_soreness_last_7[h] == 1:
                if h in historic_soreness_8_14 and h in historic_soreness_15_21 and h in historic_soreness_22_28:
                    if (historic_soreness_8_14[h] >= 1 and historic_soreness_15_21[h] >= 1
                            and historic_soreness_22_28[h] >= 1):
                        historic_soreness.historic_soreness_status = HistoricSorenessStatus.persistent

            if historic_soreness.historic_soreness_status is not None:
                historic_soreness_list.append(historic_soreness)

        return historic_soreness_list

    def get_hs_dictionary(self, soreness_list):

        historic_soreness = {}

        hs = namedtuple("hs", ["location", "is_pain", "side"])

        for s in soreness_list:
            hs_new = hs(s.body_part.location, s.pain, s.side)
            if hs_new in historic_soreness:
                historic_soreness[hs_new] = historic_soreness[hs_new] + 1
            else:
                historic_soreness[hs_new] = 1

        return historic_soreness

    def get_chronic_weeks_plans(self):

        week4_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time - timedelta(days=28) <=
                          d.get_event_datetime() < self.acute_start_date_time - timedelta(days=21)]
        week3_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time
                          - timedelta(days=21) <= d.get_event_datetime() < self.acute_start_date_time -
                          timedelta(days=14)]
        week2_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time
                          - timedelta(days=14) <= d.get_event_datetime() < self.acute_start_date_time -
                          timedelta(days=7)]
        week1_sessions = [d for d in self.chronic_daily_plans if self.acute_start_date_time
                          - timedelta(days=7) <= d.get_event_datetime() < self.acute_start_date_time]

        weeks_list = [week1_sessions, week2_sessions, week3_sessions, week4_sessions]

        return weeks_list

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
                s.reported_date_time = format_date(c.event_date)
                soreness_list.append(s)

        return soreness_list

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

    def is_athlete_functional_strength_eligible(self):

        # completed yesterday?
        #completed_yesterday = self.functional_strength_yesterday()

        # onboarded > 2 weeks?
        two_plus_weeks_since_onboarding = self.is_athlete_two_weeks_from_onboarding()

        # active prep / active recovery checks
        two_apar_sessions_completed = self.athlete_has_enough_active_prep_recovery_sessions()

        # logged sessions
        four_plus_training_sessions_logged = self.athlete_logged_enough_sessions()

        # wrapping it all up
        if (two_plus_weeks_since_onboarding and two_apar_sessions_completed and four_plus_training_sessions_logged):
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

            if days_diff >= 13: # for difference, we need one less than fourteen
                two_plus_weeks_since_onboarding = True

        return two_plus_weeks_since_onboarding

    def get_completed_functional_strength_sessions(self):

        completed_sesions = [a for a in self.last_7_days_plans if a.functional_strength_completed if a is not None]

        return len(completed_sesions)

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

        daily_plans = self.daily_plan_datastore.get(self.athlete_id, self.start_date, self.end_date)

        if daily_readiness_surveys is not None and len(daily_readiness_surveys) > 0:
            daily_readiness_surveys.sort(key=lambda x: x.event_date, reverse=False)
            earliest_survey_date_time = daily_readiness_surveys[0].event_date
        else:
            return

        if post_session_surveys is not None and len(post_session_surveys) > 0:
            post_session_surveys.sort(key=lambda x: x.event_date_time, reverse=False)
            earliest_survey_date_time = min(earliest_survey_date_time, post_session_surveys[0].event_date_time)

        # add one since survey is first thing done in the day
        days_difference = (self.end_date_time - earliest_survey_date_time).days + 1

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
            self.acute_start_date_time = self.end_date_time - timedelta(days=self.acute_days + 1)
            self.chronic_start_date_time = self.end_date_time - timedelta(days=self.chronic_days)
            chronic_date_time = self.acute_start_date_time - timedelta(days=self.chronic_days)
            chronic_delta = self.end_date_time - chronic_date_time
            self.chronic_load_start_date_time = self.end_date_time - chronic_delta

            self.acute_post_session_surveys = sorted([p for p in post_session_surveys
                                                      if p.event_date_time >= self.acute_start_date_time],
                                                     key=lambda x: x.event_date)
            self.chronic_post_session_surveys = sorted([p for p in post_session_surveys
                                                        if p.event_date_time >= self.chronic_start_date_time],
                                                       key=lambda x: x.event_date)
            self.acute_readiness_surveys = sorted([p for p in daily_readiness_surveys
                                                   if p.event_date >= self.acute_start_date_time],
                                                  key=lambda x: x.event_date)

            self.chronic_readiness_surveys = sorted([p for p in daily_readiness_surveys
                                                     if p.event_date >= self.chronic_start_date_time],
                                                    key=lambda x: x.event_date)

            self.acute_daily_plans = sorted([p for p in daily_plans if p.get_event_datetime() >=
                                             self.acute_start_date_time], key=lambda x: x.event_date)

            self.chronic_daily_plans = sorted([p for p in daily_plans if self.acute_start_date_time >
                                               p.get_event_datetime() >= self.chronic_load_start_date_time],
                                              key=lambda x: x.event_date)

        last_week = self.end_date_time - timedelta(days=7 + 1)
        previous_week = last_week - timedelta(days=7)
        previous_week_2 = previous_week - timedelta(days=7)
        previous_week_3 = previous_week_2 - timedelta(days=7)

        self.last_7_days_plans = [p for p in daily_plans if p.get_event_datetime() >= last_week]

        self.days_8_14_plans = [p for p in daily_plans if last_week > p.get_event_datetime() >= previous_week]

        self.last_7_days_ps_surveys = [p for p in post_session_surveys if p.event_date_time >= last_week]

        self.days_8_14_ps_surveys = [p for p in post_session_surveys if last_week > p.event_date_time >= previous_week]

        self.last_7_days_readiness_surveys = [p for p in daily_readiness_surveys if p.event_date >= last_week]

        self.days_8_14_readiness_surveys = [p for p in daily_readiness_surveys if last_week > p.event_date >= previous_week]

        self.days_15_21_ps_surveys = [p for p in post_session_surveys if previous_week > p.event_date_time >= previous_week_2]

        self.days_15_21_readiness_surveys = [p for p in daily_readiness_surveys if previous_week > p.event_date >= previous_week_2]

        self.days_22_28_ps_surveys = [p for p in post_session_surveys if previous_week_2 > p.event_date_time >= previous_week_3]

        self.days_22_28_readiness_surveys = [p for p in daily_readiness_surveys if previous_week_2 > p.event_date >= previous_week_3]





