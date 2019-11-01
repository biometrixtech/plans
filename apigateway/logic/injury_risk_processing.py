from datetime import datetime, timedelta
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.functional_movement import BodyPartInjuryRisk, SessionFunctionalMovement
from models.body_parts import BodyPart, BodyPartFactory
from copy import deepcopy
from datastores.session_datastore import SessionDatastore
from utils import format_date
from models.functional_movement_stats import InjuryCycleSummary, InjuryCycleSummaryProcessor
from fathomapi.utils.exceptions import NoSuchEntityException
from math import floor

class InjuryRiskProcessor(object):
    def __init__(self, event_date_time, symptoms_list, training_session_list, injury_risk_dict, athlete_stats, user_id):
        self.user_id = user_id
        self.event_date_time = event_date_time
        self.symptoms = symptoms_list
        self.training_sessions = training_session_list
        self.load_stats = athlete_stats.load_stats
        self.injury_risk_dict = injury_risk_dict
        self.relative_load_level = 3
        self.high_relative_load_sessions = athlete_stats.high_relative_load_sessions
        self.aggregated_injury_risk_dict = {}
        self.two_days_ago = self.event_date_time.date() - timedelta(days=1)
        self.three_days_ago = self.event_date_time.date() - timedelta(days=2)
        self.ten_days_ago = self.event_date_time.date() - timedelta(days=9)
        self.twenty_days_ago = self.event_date_time.date() - timedelta(days=19)
        self.functional_anatomy_processor = FunctionalAnatomyProcessor()
        
        self.eccentric_volume_dict = {}
        self.concentric_volume_dict = {}
        self.total_volume_dict = {}
        self.prime_mover_eccentric_volume_dict = {}
        self.prime_mover_concentric_volume_dict = {}
        self.prime_mover_total_volume_dict = {}
        self.synergist_eccentric_volume_dict = {}
        self.synergist_compensating_eccentric_volume_dict = {}
        self.synergist_concentric_volume_dict = {}
        self.synergist_compensating_concentric_volume_dict = {}
        self.synergist_total_volume_dict = {}
        
        self.eccentric_intensity_dict = {}
        self.concentric_intensity_dict = {}
        self.total_intensity_dict = {}
        self.prime_mover_eccentric_intensity_dict = {}
        self.prime_mover_concentric_intensity_dict = {}
        self.prime_mover_total_intensity_dict = {}
        self.synergist_eccentric_intensity_dict = {}
        self.synergist_compensating_eccentric_intensity_dict = {}
        self.synergist_concentric_intensity_dict = {}
        self.synergist_compensating_concentric_intensity_dict = {}
        self.synergist_total_intensity_dict = {}

    def initialize(self):

        self.relative_load_level = 3
        two_days_ago = (self.event_date_time - timedelta(days=1)).date()

        # check workload for relative load level
        if len(self.high_relative_load_sessions) > 0:

            max_percent = 49.9

            relevant_high_load_sessions = [s for s in self.high_relative_load_sessions if s.date.date()
                                           >= two_days_ago]
            if len(relevant_high_load_sessions) > 0:

                for r in relevant_high_load_sessions:
                    if r.percent_of_max is not None:
                        max_percent = max(r.percent_of_max, max_percent)

            if max_percent >= 75.0:
                self.relative_load_level = 1
            elif max_percent >= 50.0:
                self.relative_load_level = 2

         # check RPE for relative load level
        # Low
        # RPE <= 1 and self.ultra_high_intensity_session
        # RPE <= 3 and not self.ultra_high_intensity_session():
        # Mod
        # RPE >= 3 and self.ultra_high_intensity_session
        # RPE >= 5 and not self.ultra_high_intensity_session():
        # High
        # RPE >= 5 and self.ultra_high_intensity_session
        # RPE >= 7 and not self.ultra_high_intensity_session():
        relevant_training_sessions = [s for s in self.training_sessions if s.event_date.date()
                                           >= two_days_ago]

        for r in relevant_training_sessions:
            high_intensity_session = r.ultra_high_intensity_session()
            if r.session_RPE is not None:
                if (r.session_RPE >= 5 and high_intensity_session) or (r.session_RPE >= 7 and not high_intensity_session):
                    self.relative_load_level = 1
                elif (r.session_RPE >= 3 and high_intensity_session) or (r.session_RPE >= 5 and not high_intensity_session):
                    self.relative_load_level = 2

    def process(self, update_historical_data=False, aggregate_results=False):

        self.initialize()
        # deconstruct symptoms to muscle level
        detailed_symptoms = []
        for s in self.symptoms:
            muscles = BodyPartLocation.get_muscles_for_group(s.body_part.location)
            if isinstance(muscles, list) and len(muscles) > 0:  # muscle groups that have constituent muscles defined
                for m in muscles:
                    symptom = deepcopy(s)
                    symptom.body_part = BodyPart(m, None)
                    detailed_symptoms.append(symptom)
            else:  # joints, ligaments and muscle groups that do not have constituent muscles defined
                detailed_symptoms.append(s)

        self.symptoms = detailed_symptoms

        if update_historical_data:
            self.injury_risk_dict = self.update_historical_data(self.load_stats)
        else:
            self.process_todays_symptoms(self.event_date_time.date(), self.injury_risk_dict)
            self.process_todays_sessions(self.event_date_time.date(), self.injury_risk_dict, self.load_stats)

        # taking care of this elsewhere
        #self.injury_risk_dict = self.update_injury_risk_dict_rankings(self.injury_risk_dict)

        #reconstruct to group level
        if aggregate_results:

            aggregated_injury_hist_dict = {}

            for body_part_side, body_part_injury_risk in self.injury_risk_dict.items():
                if body_part_side not in aggregated_injury_hist_dict:
                    muscle_group = BodyPartLocation.get_muscle_group(body_part_side.body_part_location)
                    if isinstance(muscle_group, BodyPartLocation):
                        new_body_part_side = BodyPartSide(muscle_group, body_part_side.side)
                        if new_body_part_side not in aggregated_injury_hist_dict:
                            aggregated_injury_hist_dict[new_body_part_side] = deepcopy(body_part_injury_risk)
                        else:
                            aggregated_injury_hist_dict[new_body_part_side].merge(self.injury_risk_dict[body_part_side])
                    else:
                        aggregated_injury_hist_dict[body_part_side] = deepcopy(self.injury_risk_dict[body_part_side])
                else:
                    aggregated_injury_hist_dict[body_part_side].merge(self.injury_risk_dict[body_part_side])

            self.aggregated_injury_risk_dict = aggregated_injury_hist_dict

            #self.aggregated_injury_risk_dict = self.update_injury_risk_dict_rankings(self.aggregated_injury_risk_dict)

            return self.aggregated_injury_risk_dict
        else:
            return self.injury_risk_dict

    def reset_reported_symptoms(self, injury_risk_dict):

        for b in injury_risk_dict.keys():
            injury_risk_dict[b].last_ache_date = None
            injury_risk_dict[b].last_tight_date = None
            injury_risk_dict[b].last_knots_date = None
            injury_risk_dict[b].last_sharp_date = None
            injury_risk_dict[b].sharp_count_last_0_20_days = 0
            injury_risk_dict[b].sharp_count_last_0_10_days = 0
            injury_risk_dict[b].ache_count_last_0_20_days = 0
            injury_risk_dict[b].ache_count_last_0_10_days = 0

            injury_risk_dict[b].tight_count_last_0_20_days = 0
            injury_risk_dict[b].knots_count_last_0_20_days = 0
            injury_risk_dict[b].long_count_last_0_20_days = 0
            injury_risk_dict[b].short_count_last_0_20_days = 0

    def update_injury_risk_dict_rankings(self, injury_risk_dict):
        
        total_compensation_muscles = [c.total_compensation_percent for c in injury_risk_dict.values() if c.total_compensation_percent > 0]
        eccentric_compensation_muscles = [c.eccentric_compensation_percent for c in injury_risk_dict.values() if c.eccentric_compensation_percent > 0]
        total_volume_muscles = [c.total_volume_today() for c in injury_risk_dict.values() if
                                      c.total_volume_today() > 0]
        eccentric_volume_muscles = [c.eccentric_volume_today() for c in injury_risk_dict.values() if
                                          c.eccentric_volume_today() > 0]
        
        max_total_compensation = None
        max_eccentric_compensation = None
        max_total_volume = None
        max_eccentric_volume = None

        if len(total_compensation_muscles) > 0:
            min_total_compensation = min(total_compensation_muscles)
            max_total_compensation = max(total_compensation_muscles)
            total_compensation_tier = ((max_total_compensation - min_total_compensation) / 4)
            total_compensation_tier_1 = max_total_compensation - total_compensation_tier
            total_compensation_tier_2 = max_total_compensation - (2 * total_compensation_tier)
            total_compensation_tier_3 = max_total_compensation - (3 * total_compensation_tier)

        if len(eccentric_compensation_muscles) > 0:
            min_eccentric_compensation = min(eccentric_compensation_muscles)
            max_eccentric_compensation = max(eccentric_compensation_muscles)
            eccentric_compensation_tier = ((max_eccentric_compensation - min_eccentric_compensation) / 4)
            eccentric_compensation_tier_1 = max_eccentric_compensation - eccentric_compensation_tier
            eccentric_compensation_tier_2 = max_eccentric_compensation - (2 * eccentric_compensation_tier)
            eccentric_compensation_tier_3 = max_eccentric_compensation - (3 * eccentric_compensation_tier)

        if len(total_volume_muscles) > 0:
            min_total_volume = min(total_volume_muscles)
            max_total_volume = max(total_volume_muscles)
            total_volume_tier = ((max_total_volume - min_total_volume) / 4)
            total_volume_tier_1 = max_total_volume - total_volume_tier
            total_volume_tier_2 = max_total_volume - (2 * total_volume_tier)
            total_volume_tier_3 = max_total_volume - (3 * total_volume_tier)

        if len(eccentric_volume_muscles) > 0:
            min_eccentric_volume = min(eccentric_volume_muscles)
            max_eccentric_volume = max(eccentric_volume_muscles)
            eccentric_volume_tier = ((max_eccentric_volume - min_eccentric_volume) / 4)
            eccentric_volume_tier_1 = max_eccentric_volume - eccentric_volume_tier
            eccentric_volume_tier_2 = max_eccentric_volume - (2 * eccentric_volume_tier)
            eccentric_volume_tier_3 = max_eccentric_volume - (3 * eccentric_volume_tier)

        if max_total_compensation is not None or max_eccentric_compensation is not None or max_total_volume is not None or max_eccentric_volume is not None:

            for body_part_side, body_part_injurk_risk in injury_risk_dict.items():
                if max_total_compensation is not None:
                    if body_part_injurk_risk.total_compensation_percent >= total_compensation_tier_1:
                        body_part_injurk_risk.total_compensation_percent_tier = 1
                    elif body_part_injurk_risk.total_compensation_percent >= total_compensation_tier_2:
                        body_part_injurk_risk.total_compensation_percent_tier = 2
                    elif body_part_injurk_risk.total_compensation_percent >= total_compensation_tier_3:
                        body_part_injurk_risk.total_compensation_percent_tier = 3
                    elif body_part_injurk_risk.total_compensation_percent >= min_total_compensation:
                        body_part_injurk_risk.total_compensation_percent_tier = 4
                else:
                    body_part_injurk_risk.total_compensation_percent_tier = 0

                if max_eccentric_compensation is not None:
                    if body_part_injurk_risk.eccentric_compensation_percent >= eccentric_compensation_tier_1:
                        body_part_injurk_risk.eccentric_compensation_percent_tier = 1
                    elif body_part_injurk_risk.eccentric_compensation_percent >= eccentric_compensation_tier_2:
                        body_part_injurk_risk.eccentric_compensation_percent_tier = 2
                    elif body_part_injurk_risk.eccentric_compensation_percent >= eccentric_compensation_tier_3:
                        body_part_injurk_risk.eccentric_compensation_percent_tier = 3
                    elif body_part_injurk_risk.eccentric_compensation_percent >= min_eccentric_compensation:
                        body_part_injurk_risk.eccentric_compensation_percent_tier = 4
                else:
                    body_part_injurk_risk.eccentric_compensation_percent_tier = 0

                if max_total_volume is not None:
                    total_volume_today = body_part_injurk_risk.total_volume_today()

                    if total_volume_today >= total_volume_tier_1:
                        body_part_injurk_risk.total_volume_percent_tier = 1
                        if self.relative_load_level == 1:
                            body_part_injurk_risk.last_excessive_strain_date = self.event_date_time.date()
                            body_part_injurk_risk.last_inhibited_date = self.event_date_time.date()
                            body_part_injurk_risk.last_non_functional_overreaching_date = self.event_date_time.date()
                        elif self.relative_load_level == 2:
                            body_part_injurk_risk.last_excessive_strain_date = self.event_date_time.date()
                            body_part_injurk_risk.last_inhibited_date = self.event_date_time.date()
                            body_part_injurk_risk.last_functional_overreaching_date = self.event_date_time.date()
                    elif total_volume_today >= total_volume_tier_2:
                        body_part_injurk_risk.total_volume_percent_tier = 2
                        if self.relative_load_level == 1:
                            body_part_injurk_risk.last_excessive_strain_date = self.event_date_time.date()
                            body_part_injurk_risk.last_inhibited_date = self.event_date_time.date()
                            body_part_injurk_risk.last_functional_overreaching_date = self.event_date_time.date()
                    elif total_volume_today >= total_volume_tier_3:
                        body_part_injurk_risk.total_volume_percent_tier = 3
                    elif total_volume_today >= min_total_volume:
                        body_part_injurk_risk.total_volume_percent_tier = 4
                else:
                    body_part_injurk_risk.total_volume_percent_tier = 0

                if max_eccentric_volume is not None:
                    eccentric_volume_today = body_part_injurk_risk.eccentric_volume_today()

                    if eccentric_volume_today >= eccentric_volume_tier_1:
                        body_part_injurk_risk.eccentric_volume_percent_tier = 1
                    elif eccentric_volume_today >= eccentric_volume_tier_2:
                        body_part_injurk_risk.eccentric_volume_percent_tier = 2
                    elif eccentric_volume_today >= eccentric_volume_tier_3:
                        body_part_injurk_risk.eccentric_volume_percent_tier = 3
                    elif eccentric_volume_today >= min_eccentric_volume:
                        body_part_injurk_risk.eccentric_volume_percent_tier = 4
                else:
                    body_part_injurk_risk.eccentric_volume_percent_tier = 0

        return injury_risk_dict
    
    def update_historic_session_stats(self, base_date, injury_risk_dict):

        twenty_days_ago = base_date - timedelta(days=19)

        last_20_days_sessions= [s for s in self.training_sessions if
                                 base_date >= s.event_date.date() >= twenty_days_ago]

        last_20_days_sessions = sorted(last_20_days_sessions, key=lambda k: k.event_date)

        dates = []
        dates.extend([s.event_date.date() for s in last_20_days_sessions])

        for body_part_side, body_part_injury_risk in injury_risk_dict.items():
            injury_risk_dict[body_part_side].overactive_count_0_20_days = 0
            injury_risk_dict[body_part_side].underactive_inhibited_count_0_20_days = 0
            injury_risk_dict[body_part_side].underactive_weak_count_0_20_days = 0
            injury_risk_dict[body_part_side].compensating_count_0_20_days = 0
            injury_risk_dict[body_part_side].short_count_0_20_days = 0
            injury_risk_dict[body_part_side].long_count_0_20_days = 0

        for d in dates:
            overactive_set = set()
            underactive_inhibited_set = set()
            underactive_weak_set = set()
            compensating_set = set()
            short_set = set()
            long_set = set()

            todays_sessions = [s for s in last_20_days_sessions if s.event_date.date() == d]

            for t in todays_sessions:
                for body_part_side in t.overactive_body_parts:
                    overactive_set.add(body_part_side)
                for body_part_side in t.underactive_inhibited_body_parts:
                    underactive_inhibited_set.add(body_part_side)
                for body_part_side in t.underactive_weak_body_parts:
                    underactive_weak_set.add(body_part_side)
                for body_part_side in t.compensating_body_parts:
                    compensating_set.add(body_part_side)
                for body_part_side in t.short_body_parts:
                    short_set.add(body_part_side)
                for body_part_side in t.long_body_parts:
                    long_set.add(body_part_side)

            for b in overactive_set:
                if b not in injury_risk_dict:
                    injury_risk_dict[b] = BodyPartInjuryRisk()
                injury_risk_dict[b].overactive_count_last_0_20_days += 1

            for b in underactive_inhibited_set:
                if b not in injury_risk_dict:
                    injury_risk_dict[b] = BodyPartInjuryRisk()
                injury_risk_dict[b].underactive_inhibited_count_last_0_20_days += 1

            for b in underactive_weak_set:
                if b not in injury_risk_dict:
                    injury_risk_dict[b] = BodyPartInjuryRisk()
                injury_risk_dict[b].underactive_weak_count_last_0_20_days += 1

            for b in compensating_set:
                if b not in injury_risk_dict:
                    injury_risk_dict[b] = BodyPartInjuryRisk()
                injury_risk_dict[b].compensation_count_last_0_20_days += 1

            for b in short_set:
                if b not in injury_risk_dict:
                    injury_risk_dict[b] = BodyPartInjuryRisk()
                injury_risk_dict[b].short_count_last_0_20_days += 1

            for b in long_set:
                if b not in injury_risk_dict:
                    injury_risk_dict[b] = BodyPartInjuryRisk()
                injury_risk_dict[b].long_count_last_0_20_days += 1

        return injury_risk_dict

    def update_historical_symptoms(self, base_date, injury_risk_dict):

        twenty_days_ago = base_date - timedelta(days=19)
        ten_days_ago = base_date - timedelta(days=9)

        last_20_days_symptoms = [s for s in self.symptoms if
                                 base_date >= s.reported_date_time.date() >= twenty_days_ago]

        last_20_days_symptoms = sorted(last_20_days_symptoms, key=lambda k: k.reported_date_time)

        self.reset_reported_symptoms(injury_risk_dict)

        for s in last_20_days_symptoms:
            target_body_part_side = BodyPartSide(s.body_part.location, s.side)
            if s.sharp is not None and s.sharp > 0:
                if target_body_part_side not in injury_risk_dict:
                    injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < s.reported_date_time.date():
                    injury_risk_dict[target_body_part_side].last_sharp_date = s.reported_date_time.date()
                    # if s.reported_date_time.date() <= three_days_ago:
                    injury_risk_dict[target_body_part_side].sharp_count_last_0_20_days += 1
                    if s.reported_date_time.date() >= ten_days_ago:
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
            if s.ache is not None and s.ache > 0:
                # if s.body_part.location.value not in [55, 56, 57, 58]:
                #     j=0
                if target_body_part_side not in injury_risk_dict:
                    injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < s.reported_date_time.date():
                    injury_risk_dict[target_body_part_side].last_ache_date = s.reported_date_time.date()
                    # if s.reported_date_time.date() <= three_days_ago:
                    injury_risk_dict[target_body_part_side].ache_count_last_0_20_days += 1
                    if s.reported_date_time.date() >= ten_days_ago:
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    # if three_days_ago >= s.reported_date_time.date() >= ten_days_ago:
                    #     injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
            if s.tight is not None and s.tight > 0:
                if target_body_part_side not in injury_risk_dict:
                    injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if injury_risk_dict[target_body_part_side].last_tight_date is None or injury_risk_dict[target_body_part_side].last_tight_date < s.reported_date_time.date():
                    injury_risk_dict[target_body_part_side].last_tight_date = s.reported_date_time.date()
                    # if s.reported_date_time.date() <= three_days_ago:
                    injury_risk_dict[target_body_part_side].tight_count_last_0_20_days += 1

            if s.knots is not None and s.knots > 0:
                if target_body_part_side not in injury_risk_dict:
                    injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if injury_risk_dict[target_body_part_side].last_knots_date is None or injury_risk_dict[target_body_part_side].last_knots_date < s.reported_date_time.date():
                    injury_risk_dict[target_body_part_side].last_knots_date = s.reported_date_time.date()
                    injury_risk_dict[target_body_part_side].knots_count_last_0_20_days += 1

        return injury_risk_dict

    def update_historical_data(self, load_stats):

        combined_dates = []
        combined_dates.extend([s.event_date.date() for s in self.training_sessions])

        #last_20_days_symptoms = [s for s in self.symptoms if s.event_date_time.date() >= self.twenty_days_ago.date()]
        combined_dates.extend([s.reported_date_time.date() for s in self.symptoms])

        combined_dates = list(set(combined_dates))
        combined_dates.sort()

        injury_risk_dict = {}

        injury_cycle_summary_dict = {}

        twenty_days_ago = self.event_date_time.date() - timedelta(days=19)

        for d in combined_dates:

            if d == datetime(2019, 10, 31).date():
                j = 0
            seven_days_ago = d - timedelta(days=6)
            fourteeen_days_ago = d - timedelta(days=13)

            # first let's update our historical data
            injury_risk_dict = self.update_historical_symptoms(d, injury_risk_dict)

            # injury_risk_dict = self.update_historic_session_stats(d, injury_risk_dict)

            injury_risk_dict = self.process_todays_symptoms(d, injury_risk_dict)

            daily_sessions = [n for n in self.training_sessions if n.event_date.date() == d]
            daily_sessions = sorted(daily_sessions, key=lambda x:x.event_date)

            session_mapping_dict = {}

            for session in daily_sessions:
                session_functional_movement = SessionFunctionalMovement(session, injury_risk_dict)
                current_session = session_functional_movement.process(d, load_stats)

                injury_cycle_summary_dict = self.update_injury_cycle_summaries(current_session,
                                                                               injury_cycle_summary_dict,
                                                                               injury_risk_dict, d)

                if d >= twenty_days_ago:
                    injury_risk_dict = self.mark_anc_muscle_imbalance(injury_cycle_summary_dict, injury_risk_dict,
                                                                      current_session.event_date)

                # # save all updates from processing back to the session - TODO: make sure this is the best place/time to save this info
                # session_datastore = SessionDatastore()
                # try:
                #     session_datastore.update(current_session, self.user_id, format_date(d))
                # except NoSuchEntityException:
                #     session_datastore.update(current_session, self.user_id, format_date(d - timedelta(days=1)))
                # #TODO: continue if fails the second time

                injury_risk_dict = self.update_injury_risk_dict_rankings(injury_risk_dict)

                session_mapping_dict[current_session] = session_functional_movement.functional_movement_mappings

            daily_injury_risk_dict = self.merge_daily_sessions(d, session_mapping_dict, injury_risk_dict)

            for body_part_side, body_part_injury_risk in daily_injury_risk_dict.items():

                if body_part_side not in injury_risk_dict:
                    injury_risk_dict[body_part_side] = BodyPartInjuryRisk()

                self.populate_volume_dictionaries(body_part_injury_risk, body_part_side, d)

                eccentric_volume_dict = self.eccentric_volume_dict[body_part_side]
                concentric_volume_dict = self.concentric_volume_dict[body_part_side]
                total_volume_dict = self.total_volume_dict[body_part_side]

                # TODO: calc ramp, etc for intensity
                # self.populate_intensity_dictionaries(body_part_injury_risk, body_part_side, d)
                # eccentric_intensity_dict = self.eccentric_intensity_dict[body_part_side]
                # concentric_intensity_dict = self.concentric_intensity_dict[body_part_side]

                last_week_eccentric_volume_dict = dict(
                    filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago, eccentric_volume_dict.items()))

                current_week_eccentric_volume_dict = dict(
                    filter(lambda elem: d > elem[0] >= seven_days_ago, eccentric_volume_dict.items()))

                last_week_concentric_volume_dict = dict(
                    filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago, concentric_volume_dict.items()))

                current_week_concentric_volume_dict = dict(
                    filter(lambda elem: d > elem[0] >= seven_days_ago, concentric_volume_dict.items()))

                last_week_eccentric_volume = sum(last_week_eccentric_volume_dict.values())
                current_week_eccentric_volume = sum(current_week_eccentric_volume_dict.values())
                last_week_concentric_volume = sum(last_week_concentric_volume_dict.values())
                current_week_concentric_volume = sum(current_week_concentric_volume_dict.values())

                injury_risk_dict[body_part_side].eccentric_volume_this_week = current_week_eccentric_volume
                injury_risk_dict[body_part_side].eccentric_volume_last_week = last_week_eccentric_volume
                injury_risk_dict[body_part_side].concentric_volume_this_week = current_week_concentric_volume
                injury_risk_dict[body_part_side].concentric_volume_last_week = last_week_concentric_volume
                
                injury_risk_dict[body_part_side].total_compensation_percent = injury_risk_dict[body_part_side].percent_total_compensation()
                injury_risk_dict[body_part_side].eccentric_compensation_percent = injury_risk_dict[
                    body_part_side].percent_eccentric_compensation()

                injury_risk_dict[body_part_side].eccentric_volume_ramp_today = injury_risk_dict[body_part_side].eccentric_volume_ramp()
                injury_risk_dict[body_part_side].total_volume_ramp_today = injury_risk_dict[body_part_side].total_volume_ramp()

                # if injury_risk_dict[body_part_side].eccentric_volume_ramp_today > 1.0 or injury_risk_dict[body_part_side].total_volume_ramp_today > 1.0:
                #     injury_risk_dict[body_part_side].last_excessive_strain_date = d
                #     injury_risk_dict[body_part_side].last_inhibited_date = d
                #
                # if 1.0 < injury_risk_dict[body_part_side].eccentric_volume_ramp_today <= 1.05:
                #     injury_risk_dict[body_part_side].last_functional_overreaching_date = d
                # elif 1.05 < injury_risk_dict[body_part_side].eccentric_volume_ramp_today:
                #     injury_risk_dict[body_part_side].last_non_functional_overreaching_date = d
                #
                # elif 1.0 < injury_risk_dict[body_part_side].total_volume_ramp_today <= 1.1:
                #     injury_risk_dict[body_part_side].last_functional_overreaching_date = d
                # elif 1.1 < injury_risk_dict[body_part_side].total_volume_ramp_today:
                #     injury_risk_dict[body_part_side].last_non_functional_overreaching_date = d
        injury_risk_dict = self.update_injury_risk_dict_rankings(injury_risk_dict)

        return injury_risk_dict

    def get_movement_pattern_elasiticity_adf(self, movement_pattern, side):

        if side == 1:
            if movement_pattern.left is not None:
                elasticity_value = movement_pattern.left.elasticity
                adf_value = movement_pattern.left.y_adf
            else:
                elasticity_value = 0.0
                adf_value = 0.0
        else:
            if movement_pattern.right is not None:
                elasticity_value = movement_pattern.right.elasticity
                adf_value = movement_pattern.right.y_adf
            else:
                elasticity_value = 0.0
                adf_value = 0.0

        return elasticity_value, adf_value

    def update_injury_cycle_summaries(self, current_session, injury_cycle_summary_dict, injury_risk_dict, base_date):

        sides = [1, 2]

        summary_dict = {}

        for side in sides:

            apt_ankle_present = False
            hip_drop_present = False
            knee_valgus_present = False
            hip_drop_pva_present = False
            knee_valgus_pva_present = False

            proc = InjuryCycleSummaryProcessor(injury_cycle_summary_dict, side, current_session.event_date)

            if current_session.movement_patterns is not None and current_session.movement_patterns.apt_ankle_pitch is not None:

                apt_ankle = current_session.movement_patterns.apt_ankle_pitch
                apt_ankle_elasticity, apt_ankle_adf = self.get_movement_pattern_elasiticity_adf(apt_ankle, side)
                if apt_ankle_elasticity != 0:
                    proc.increment_overactive_short_by_list([21, 26, 70, 58, 71, 72, 59, 55, 65, 49, 50, 52, 53, 54, 62])
                    proc.increment_underactive_long_by_list([75, 74, 73, 66, 63, 64, 47, 48])
                    apt_ankle_present = True

                if apt_ankle_adf != 0 and current_session.duration_minutes >= 20:
                    proc.increment_weak_by_list([73, 66])

            if current_session.movement_patterns is not None and current_session.movement_patterns.hip_drop_apt is not None:

                hip_drop_apt = current_session.movement_patterns.hip_drop_apt
                hip_drop_apt_elasticity, hip_drop_apt_adf = self.get_movement_pattern_elasiticity_adf(hip_drop_apt,
                                                                                                      side)
                if hip_drop_apt_elasticity != 0:
                    proc.increment_overactive_short_by_list([59, 49, 50, 52, 53, 54])
                    proc.increment_underactive_long_by_list([63, 64, 47, 48])

                    hip_drop_present = True

                if hip_drop_apt_adf != 0 and current_session.movement_patterns >= 20:
                    proc.increment_weak_by_list([56, 66])

            if current_session.movement_patterns is not None and current_session.movement_patterns.knee_valgus_apt is not None:

                knee_valgus_apt = current_session.movement_patterns.knee_valgus_apt
                knee_valgus_apt_elasticity, knee_valgus_apt_adf = self.get_movement_pattern_elasiticity_adf(
                    knee_valgus_apt, side)

                if knee_valgus_apt_elasticity != 0:
                    proc.increment_overactive_short_by_list([69, 49, 50, 52, 53, 54, 21, 66])
                    proc.increment_underactive_long_by_list([21])

                    knee_valgus_present = True

                if knee_valgus_apt_adf != 0 and current_session.movement_patterns >= 20:
                    proc.increment_weak_by_list([44, 42, 40, 41])

            if hip_drop_present and knee_valgus_present:

                if hip_drop_apt_elasticity == 0 and knee_valgus_apt_elasticity == 0:
                    proc.increment_overactive_short_by_list([21, 26, 58, 71, 72])
                    proc.increment_underactive_long_by_list([75, 74, 73, 66])

            if current_session.movement_patterns is not None and current_session.movement_patterns.hip_drop_pva is not None:

                hip_drop_pva = current_session.movement_patterns.hip_drop_pva
                hip_drop_pva_elasticity, hip_drop_pva_adf = self.get_movement_pattern_elasiticity_adf(hip_drop_pva,
                                                                                                      side)
                if hip_drop_pva_elasticity != 0:
                    hip_drop_pva_present = True

            # This isn't used yet
            # if current_session.movement_patterns is not None and current_session.movement_patterns.knee_valgus_hip_drop is not None:
            #
            #     knee_valgus_hip_drop = current_session.movement_patterns.knee_valgus_hip_drop
            #     knee_valgus_hip_drop_elasticity, knee_valgus_hip_drop_adf = self.get_movement_pattern_elasiticity_adf(
            #         knee_valgus_hip_drop, side)

            if current_session.movement_patterns is not None and current_session.movement_patterns.knee_valgus_pva is not None:

                knee_valgus_pva = current_session.movement_patterns.knee_valgus_pva
                knee_valgus_pva_elasticity, knee_valgus_pva_adf = self.get_movement_pattern_elasiticity_adf(knee_valgus_pva, side)

                if knee_valgus_pva_elasticity != 0:
                    proc.increment_overactive_short_by_list(
                        [59, 55, 46, 75, 65, 59, 49, 50, 52, 53, 54])
                    proc.increment_underactive_long_by_list([68, 53, 47, 48, 44, 63, 64, 66])
                    knee_valgus_pva_present = True

            if hip_drop_pva_present or knee_valgus_pva_present:

                proc.increment_overactive_short_by_list([44, 75, 43, 41, 59, 55, 46, 65, 59, 49, 50, 52, 53, 54, 58, 62])
                proc.increment_underactive_long_by_list([40, 42, 68, 53, 47, 48, 56, 63, 64, 66])

            if apt_ankle_present and (hip_drop_pva_present or knee_valgus_pva_present):

                proc.increment_overactive_short_by_list(
                    [65, 59, 49, 50, 52, 53, 54, 58, 62, 59, 55, 46])
                proc.increment_underactive_long_by_list([63,64, 66, 68, 53, 47, 48, 56])

            if hip_drop_pva_present and knee_valgus_pva_present:

                proc.increment_overactive_short_by_list(
                    [44, 75, 43, 41, 59, 55, 46])
                proc.increment_underactive_long_by_list([40, 42, 68, 53, 47, 48, 56])


            summary_dict = proc.injury_cycle_summary_dict

        two_days_ago = base_date - timedelta(days=1)

        for body_part_side, body_part_injury_risk in injury_risk_dict.items():
            proc = InjuryCycleSummaryProcessor(injury_cycle_summary_dict, body_part_side.side, current_session.event_date)
            if body_part_injury_risk.last_muscle_spasm_date == base_date:

                proc.increment_overactive_short(body_part_side.body_part_location.value)
            if body_part_injury_risk.last_adhesions_date == base_date:
                proc.increment_short(body_part_side.body_part_location.value)
            if body_part_injury_risk.last_inflammation_date == base_date:
                proc.increment_underactive(body_part_side.body_part_location.value)
            if body_part_injury_risk.last_non_functional_overreaching_date is not None and body_part_injury_risk.last_non_functional_overreaching_date >= two_days_ago:
                proc.increment_underactive(body_part_side.body_part_location.value)

            summary_dict = proc.injury_cycle_summary_dict

        return summary_dict

    def mark_anc_muscle_imbalance(self, injury_cycle_summary_dict, injury_risk_dict, event_date_time):

        for body_part_side, injury_cycle_summary in injury_cycle_summary_dict.items():

            if body_part_side.body_part_location.value == 62:
                j=0

            if injury_cycle_summary.last_updated_date_time is None or injury_cycle_summary.last_updated_date_time == event_date_time:
                if (injury_cycle_summary.overactive_short_count > injury_cycle_summary.overactive_long_count and
                        injury_cycle_summary.overactive_short_count > injury_cycle_summary.underactive_short_count and
                        injury_cycle_summary.overactive_short_count > injury_cycle_summary.underactive_long_count):
                    if body_part_side not in injury_risk_dict:
                        injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
                    if injury_risk_dict[body_part_side].last_overactive_short_date is None or injury_risk_dict[body_part_side].last_overactive_short_date < event_date_time.date():
                        injury_risk_dict[body_part_side].last_overactive_short_date = event_date_time.date()
                        # could be an additional session of the day and in this case, we want to consider it more than once
                        injury_risk_dict[body_part_side].overactive_short_count_last_0_20_days += 1

                elif (injury_cycle_summary.overactive_long_count > injury_cycle_summary.overactive_short_count and
                      injury_cycle_summary.overactive_long_count > injury_cycle_summary.underactive_short_count and
                      injury_cycle_summary.overactive_long_count > injury_cycle_summary.underactive_long_count):
                    if body_part_side not in injury_risk_dict:
                        injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
                    if injury_risk_dict[body_part_side].last_overactive_long_date is None or injury_risk_dict[body_part_side].last_overactive_long_date < event_date_time.date():
                        injury_risk_dict[body_part_side].last_overactive_long_date = event_date_time.date()
                        injury_risk_dict[body_part_side].overactive_long_count_last_0_20_days += 1

                elif (injury_cycle_summary.underactive_short_count > injury_cycle_summary.overactive_short_count and
                      injury_cycle_summary.underactive_short_count > injury_cycle_summary.overactive_long_count and
                      injury_cycle_summary.underactive_short_count > injury_cycle_summary.underactive_long_count):
                    if body_part_side not in injury_risk_dict:
                        injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
                    if injury_risk_dict[body_part_side].last_underactive_short_date is None or injury_risk_dict[body_part_side].last_underactive_short_date < event_date_time.date():
                        injury_risk_dict[body_part_side].last_underactive_short_date = event_date_time.date()
                        injury_risk_dict[body_part_side].underactive_short_count_last_0_20_days += 1

                elif (injury_cycle_summary.underactive_long_count > injury_cycle_summary.overactive_short_count and
                      injury_cycle_summary.underactive_long_count > injury_cycle_summary.overactive_long_count and
                      injury_cycle_summary.underactive_long_count > injury_cycle_summary.underactive_short_count):
                    if body_part_side not in injury_risk_dict:
                        injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
                    if injury_risk_dict[body_part_side].last_underactive_long_date is None or injury_risk_dict[body_part_side].last_underactive_long_date < event_date_time.date():
                        injury_risk_dict[body_part_side].last_underactive_long_date = event_date_time.date()
                        injury_risk_dict[body_part_side].underactive_long_count_last_0_20_days += 1

                if injury_cycle_summary.weak_count > 0:
                    if body_part_side not in injury_risk_dict:
                        injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
                    if injury_risk_dict[body_part_side].last_weak_date is None or injury_risk_dict[body_part_side].last_weak_date < event_date_time.date():
                        injury_risk_dict[body_part_side].last_weak_date = event_date_time.date()
                        injury_risk_dict[body_part_side].weak_count_last_0_20_days += 1

            #injury_cycle_summary.last_updated_date_time = event_date_time

        return injury_risk_dict

    def populate_volume_dictionaries(self, body_part_injury_risk, body_part_side, d):
        
        # eccentric volume
        if body_part_side not in self.eccentric_volume_dict:
            self.eccentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        if d not in self.eccentric_volume_dict[body_part_side]:
            self.eccentric_volume_dict[body_part_side][d] = 0
        self.eccentric_volume_dict[body_part_side][d] = body_part_injury_risk.eccentric_volume_today()
        
        # if body_part_side not in self.prime_mover_eccentric_volume_dict:
        #     self.prime_mover_eccentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.prime_mover_eccentric_volume_dict[body_part_side]:
        #     self.prime_mover_eccentric_volume_dict[body_part_side][d] = 0
        # self.prime_mover_eccentric_volume_dict[body_part_side][
        #     d] += body_part_injury_risk.prime_mover_eccentric_volume_today
        # 
        # if body_part_side not in self.synergist_eccentric_volume_dict:
        #     self.synergist_eccentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_eccentric_volume_dict[body_part_side]:
        #     self.synergist_eccentric_volume_dict[body_part_side][d] = 0
        # self.synergist_eccentric_volume_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_eccentric_volume_today
        # 
        # if body_part_side not in self.synergist_compensating_eccentric_volume_dict:
        #     self.synergist_compensating_eccentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_compensating_eccentric_volume_dict[body_part_side]:
        #     self.synergist_compensating_eccentric_volume_dict[body_part_side][d] = 0
        # self.synergist_compensating_eccentric_volume_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_compensating_eccentric_volume_today
        
        # concentric volume
        if body_part_side not in self.concentric_volume_dict:
            self.concentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        if d not in self.concentric_volume_dict[body_part_side]:
            self.concentric_volume_dict[body_part_side][d] = 0
        self.concentric_volume_dict[body_part_side][d] = body_part_injury_risk.concentric_volume_today()
        
        # if body_part_side not in self.prime_mover_concentric_volume_dict:
        #     self.prime_mover_concentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.prime_mover_concentric_volume_dict[body_part_side]:
        #     self.prime_mover_concentric_volume_dict[body_part_side][d] = 0
        # self.prime_mover_concentric_volume_dict[body_part_side][
        #     d] += body_part_injury_risk.prime_mover_concentric_volume_today
        # 
        # if body_part_side not in self.synergist_concentric_volume_dict:
        #     self.synergist_concentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_concentric_volume_dict[body_part_side]:
        #     self.synergist_concentric_volume_dict[body_part_side][d] = 0
        # self.synergist_concentric_volume_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_concentric_volume_today
        # 
        # if body_part_side not in self.synergist_compensating_concentric_volume_dict:
        #     self.synergist_compensating_concentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_compensating_concentric_volume_dict[body_part_side]:
        #     self.synergist_compensating_concentric_volume_dict[body_part_side][d] = 0
        # self.synergist_compensating_concentric_volume_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_compensating_concentric_volume_today
        
        # total volume
        if body_part_side not in self.total_volume_dict:
            self.total_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        if d not in self.total_volume_dict[body_part_side]:
            self.total_volume_dict[body_part_side][d] = 0
        self.total_volume_dict[body_part_side][
            d] = body_part_injury_risk.total_volume_today()
        
        # if body_part_side not in self.prime_mover_total_volume_dict:
        #     self.prime_mover_total_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.prime_mover_total_volume_dict[body_part_side]:
        #     self.prime_mover_total_volume_dict[body_part_side][d] = 0
        # self.prime_mover_total_volume_dict[body_part_side][
        #     d] += body_part_injury_risk.prime_mover_total_volume_today
        # 
        # if body_part_side not in self.synergist_total_volume_dict:
        #     self.synergist_total_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_total_volume_dict[body_part_side]:
        #     self.synergist_total_volume_dict[body_part_side][d] = 0
        # self.synergist_total_volume_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_total_volume_today

    def populate_intensity_dictionaries(self, body_part_injury_risk, body_part_side, d):

        # eccentric intensity
        if body_part_side not in self.eccentric_intensity_dict:
            self.eccentric_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        if d not in self.eccentric_intensity_dict[body_part_side]:
            self.eccentric_intensity_dict[body_part_side][d] = 0
        self.eccentric_intensity_dict[body_part_side][d] += body_part_injury_risk.eccentric_intensity_today

        # if body_part_side not in self.prime_mover_eccentric_intensity_dict:
        #     self.prime_mover_eccentric_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.prime_mover_eccentric_intensity_dict[body_part_side]:
        #     self.prime_mover_eccentric_intensity_dict[body_part_side][d] = 0
        # self.prime_mover_eccentric_intensity_dict[body_part_side][
        #     d] += body_part_injury_risk.prime_mover_eccentric_intensity_today
        # 
        # if body_part_side not in self.synergist_eccentric_intensity_dict:
        #     self.synergist_eccentric_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_eccentric_intensity_dict[body_part_side]:
        #     self.synergist_eccentric_intensity_dict[body_part_side][d] = 0
        # self.synergist_eccentric_intensity_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_eccentric_intensity_today
        # 
        # if body_part_side not in self.synergist_compensating_eccentric_intensity_dict:
        #     self.synergist_compensating_eccentric_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_compensating_eccentric_intensity_dict[body_part_side]:
        #     self.synergist_compensating_eccentric_intensity_dict[body_part_side][d] = 0
        # self.synergist_compensating_eccentric_intensity_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_compensating_eccentric_intensity_today

        # concentric intensity
        if body_part_side not in self.concentric_intensity_dict:
            self.concentric_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        if d not in self.concentric_intensity_dict[body_part_side]:
            self.concentric_intensity_dict[body_part_side][d] = 0
        self.concentric_intensity_dict[body_part_side][d] += body_part_injury_risk.concentric_intensity_today

        # if body_part_side not in self.prime_mover_concentric_intensity_dict:
        #     self.prime_mover_concentric_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.prime_mover_concentric_intensity_dict[body_part_side]:
        #     self.prime_mover_concentric_intensity_dict[body_part_side][d] = 0
        # self.prime_mover_concentric_intensity_dict[body_part_side][
        #     d] += body_part_injury_risk.prime_mover_concentric_intensity_today
        # 
        # if body_part_side not in self.synergist_concentric_intensity_dict:
        #     self.synergist_concentric_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_concentric_intensity_dict[body_part_side]:
        #     self.synergist_concentric_intensity_dict[body_part_side][d] = 0
        # self.synergist_concentric_intensity_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_concentric_intensity_today
        # 
        # if body_part_side not in self.synergist_compensating_concentric_intensity_dict:
        #     self.synergist_compensating_concentric_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_compensating_concentric_intensity_dict[body_part_side]:
        #     self.synergist_compensating_concentric_intensity_dict[body_part_side][d] = 0
        # self.synergist_compensating_concentric_intensity_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_compensating_concentric_intensity_today

        # total intensity
        if body_part_side not in self.total_intensity_dict:
            self.total_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        if d not in self.total_intensity_dict[body_part_side]:
            self.total_intensity_dict[body_part_side][d] = 0
        self.total_intensity_dict[body_part_side][
            d] += body_part_injury_risk.concentric_intensity_today + body_part_injury_risk.eccentric_intensity_today

        # if body_part_side not in self.prime_mover_total_intensity_dict:
        #     self.prime_mover_total_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.prime_mover_total_intensity_dict[body_part_side]:
        #     self.prime_mover_total_intensity_dict[body_part_side][d] = 0
        # self.prime_mover_total_intensity_dict[body_part_side][
        #     d] += body_part_injury_risk.prime_mover_total_intensity_today
        # 
        # if body_part_side not in self.synergist_total_intensity_dict:
        #     self.synergist_total_intensity_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
        # if d not in self.synergist_total_intensity_dict[body_part_side]:
        #     self.synergist_total_intensity_dict[body_part_side][d] = 0
        # self.synergist_total_intensity_dict[body_part_side][
        #     d] += body_part_injury_risk.synergist_total_intensity_today
    
    def process_todays_sessions(self, base_date, injury_risk_dict, load_stats):

        daily_sessions = [n for n in self.training_sessions if n.event_date.date() == base_date]
        daily_sessions = sorted(daily_sessions, key=lambda x:x.event_date)

        #reset
        for body_part_side, body_part_injury_risk in injury_risk_dict.items():

            #injury_risk_dict[body_part_side].eccentric_volume_today = 0
            #injury_risk_dict[body_part_side].concentric_volume_today = 0
            #injury_risk_dict[body_part_side].last_compensation_date = None
            #injury_risk_dict[body_part_side].compensating_source = None

            injury_risk_dict[body_part_side].prime_mover_concentric_volume_today = 0
            injury_risk_dict[body_part_side].prime_mover_eccentric_volume_today = 0
            #injury_risk_dict[body_part_side].prime_mover_total_volume_today = 0
            injury_risk_dict[body_part_side].synergist_concentric_volume_today = 0
            injury_risk_dict[body_part_side].synergist_eccentric_volume_today = 0
            #injury_risk_dict[body_part_side].synergist_total_volume_today = 0
            injury_risk_dict[body_part_side].synergist_compensating_concentric_volume_today = 0
            injury_risk_dict[body_part_side].synergist_compensating_eccentric_volume_today = 0
            #injury_risk_dict[body_part_side].synergist_compensating_total_volume_today = 0

            #injury_risk_dict[body_part_side].concentric_intensity_today = 0
            #injury_risk_dict[body_part_side].eccentric_intensity_today = 0

            injury_risk_dict[body_part_side].prime_mover_concentric_intensity_today = 0
            injury_risk_dict[body_part_side].prime_mover_eccentric_intensity_today = 0
            #injury_risk_dict[body_part_side].prime_mover_total_intensity_today = 0

            injury_risk_dict[body_part_side].synergist_concentric_intensity_today = 0
            injury_risk_dict[body_part_side].synergist_eccentric_intensity_today = 0
            #injury_risk_dict[body_part_side].synergist_total_intensity_today = 0
            injury_risk_dict[body_part_side].synergist_compensating_concentric_intensity_today = 0
            injury_risk_dict[body_part_side].synergist_compensating_eccentric_intensity_today = 0
            #injury_risk_dict[body_part_side].synergist_compensating_total_intensity_today = 0

        session_mapping_dict = {}
        injury_cycle_summary_dict = {}

        for session in daily_sessions:
            session_functional_movement = SessionFunctionalMovement(session, injury_risk_dict)
            current_session = session_functional_movement.process(base_date, load_stats)

            # # save all updates from processing back to the session
            # session_datastore = SessionDatastore()
            # try:
            #     session_datastore.update(current_session, self.user_id, format_date(base_date))
            # except NoSuchEntityException:
            #     session_datastore.update(current_session, self.user_id, format_date(base_date - timedelta(days=1)))
            # # TODO: continue if fails the second time

            injury_cycle_summary_dict = self.update_injury_cycle_summaries(current_session,
                                                                           injury_cycle_summary_dict,
                                                                           injury_risk_dict, base_date)

            injury_risk_dict = self.mark_anc_muscle_imbalance(injury_cycle_summary_dict, injury_risk_dict,
                                                              current_session.event_date)

            injury_risk_dict = self.update_injury_risk_dict_rankings(injury_risk_dict)

            session_mapping_dict[current_session] = session_functional_movement.functional_movement_mappings

        injury_risk_dict = self.merge_daily_sessions(base_date, session_mapping_dict, injury_risk_dict)

        injury_risk_dict = self.update_injury_risk_dict_rankings(injury_risk_dict)

            # for b in session_functional_movement.body_parts:
            #
            #     if b.body_part_side not in injury_risk_dict:
            #         injury_risk_dict[b.body_part_side] = BodyPartInjuryRisk()
            #
            #     injury_risk_dict[b.body_part_side].eccentric_volume_today += b.eccentric_volume
            #     injury_risk_dict[b.body_part_side].concentric_volume_today += b.concentric_volume
            #     if b.is_compensating:
            #         injury_risk_dict[b.body_part_side].last_compensation_date = base_date
            #         injury_risk_dict[b.body_part_side].compensating_source = b.compensation_source
            #
            #     eccentric_volume_ramp = injury_risk_dict[b.body_part_side].eccentric_volume_ramp()
            #     total_volume_ramp = injury_risk_dict[b.body_part_side].total_volume_ramp()
            #
            #     if eccentric_volume_ramp > 1.0 or total_volume_ramp > 1.0:
            #         injury_risk_dict[b.body_part_side].last_excessive_strain_date = base_date
            #         injury_risk_dict[b.body_part_side].last_inhibited_date = base_date
            #
            #     if 1.0 < eccentric_volume_ramp <= 1.05:
            #         injury_risk_dict[b.body_part_side].last_functional_overreaching_date = base_date
            #     elif 1.05 < eccentric_volume_ramp:
            #         injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = base_date
            #
            #     elif 1.0 < total_volume_ramp <= 1.1:
            #         injury_risk_dict[b.body_part_side].last_functional_overreaching_date = base_date
            #     elif 1.1 < total_volume_ramp:
            #         injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = base_date

    def merge_daily_sessions(self, base_date, session_functional_movement_dict_list, injury_risk_dict):

        # this method takes a list of n functional movement lists from session processing and merges to a unified injury risk dict object for the day

        # first get a list of unique keys across all dictionaries

        body_part_side_list = []

        for session in session_functional_movement_dict_list:
            for functional_movement_mapping in session_functional_movement_dict_list[session]:

                prime_movers = [BodyPartSide(b.body_part_side.body_part_location, b.body_part_side.side) for b in functional_movement_mapping.prime_movers]
                synergists = [BodyPartSide(b.body_part_side.body_part_location, b.body_part_side.side) for b in functional_movement_mapping.synergists]
                body_part_side_list.extend(prime_movers)
                body_part_side_list.extend(synergists)

        body_part_side_set = list(set(body_part_side_list))

        for b in body_part_side_set:

            if b not in injury_risk_dict:
                injury_risk_dict[b] = BodyPartInjuryRisk()

        for body_part_side, body_part_injury_risk in injury_risk_dict.items():
            # volume
            injury_risk_dict[body_part_side].prime_mover_concentric_volume_today = 0
            injury_risk_dict[body_part_side].prime_mover_eccentric_volume_today = 0

            injury_risk_dict[body_part_side].synergist_concentric_volume_today = 0
            injury_risk_dict[body_part_side].synergist_eccentric_volume_today = 0

            injury_risk_dict[body_part_side].synergist_compensating_concentric_volume_today = 0
            injury_risk_dict[body_part_side].synergist_compensating_eccentric_volume_today = 0

            injury_risk_dict[body_part_side].compensating_causes_volume_today = []
            injury_risk_dict[body_part_side].compensating_source_volume = None

            # intensity
            injury_risk_dict[body_part_side].prime_mover_concentric_intensity_today = 0
            injury_risk_dict[body_part_side].prime_mover_eccentric_intensity_today = 0
            #injury_risk_dict[body_part_side].prime_mover_total_intensity_today = 0
            injury_risk_dict[body_part_side].synergist_concentric_intensity_today = 0
            injury_risk_dict[body_part_side].synergist_eccentric_intensity_today = 0
            injury_risk_dict[body_part_side].synergist_compensating_concentric_intensity_today = 0
            injury_risk_dict[body_part_side].synergist_compensating_eccentric_intensity_today = 0
            #injury_risk_dict[body_part_side].synergist_total_intensity_today = 0
            #injury_risk_dict[body_part_side].eccentric_intensity_today = 0
            #injury_risk_dict[body_part_side].concentric_intensity_today = 0
            injury_risk_dict[body_part_side].compensating_causes_intensity_today = []
            injury_risk_dict[body_part_side].compensating_source_intensity = None

            injury_risk_dict[body_part_side].last_compensation_date = None

        for session, functional_movement_list in session_functional_movement_dict_list.items():
            for functional_movement in functional_movement_list:
                # note: BodyPartFunctionalMovement hashes on body part side
                for prime_mover in functional_movement.prime_movers:  # list of BodyPartFunctionalMovement objects
                    body_part_side = BodyPartSide(prime_mover.body_part_side.body_part_location, prime_mover.body_part_side.side)
                    injury_risk_dict[body_part_side].prime_mover_concentric_volume_today += prime_mover.concentric_volume
                    injury_risk_dict[body_part_side].prime_mover_eccentric_volume_today += prime_mover.eccentric_volume
                    # injury_risk_dict[
                    #     body_part_side].prime_mover_total_volume_today = prime_mover.total_volume()

                    injury_risk_dict[body_part_side].prime_mover_concentric_intensity_today = max(
                        prime_mover.concentric_intensity,
                        injury_risk_dict[body_part_side].prime_mover_concentric_intensity_today)
                    injury_risk_dict[body_part_side].prime_mover_eccentric_intensity_today = max(
                        prime_mover.eccentric_intensity,
                        injury_risk_dict[body_part_side].prime_mover_eccentric_intensity_today)
                    injury_risk_dict[body_part_side].prime_mover_total_intensity_today = max(
                        prime_mover.total_intensity(),
                        injury_risk_dict[body_part_side].prime_mover_total_intensity_today)

                for synergist in functional_movement.synergists:
                    body_part_side = BodyPartSide(synergist.body_part_side.body_part_location,
                                                  synergist.body_part_side.side)
                    injury_risk_dict[body_part_side].synergist_concentric_volume_today += synergist.concentric_volume
                    injury_risk_dict[body_part_side].synergist_eccentric_volume_today += synergist.eccentric_volume
                    injury_risk_dict[body_part_side].synergist_compensating_concentric_volume_today += synergist.compensated_concentric_volume
                    injury_risk_dict[body_part_side].synergist_compensating_eccentric_volume_today += synergist.compensated_eccentric_volume
                    # injury_risk_dict[
                    #     body_part_side].synergist_total_volume_today = synergist.total_volume()

                    injury_risk_dict[body_part_side].synergist_concentric_intensity_today = max(
                        synergist.concentric_intensity,
                        injury_risk_dict[body_part_side].synergist_concentric_intensity_today)
                    injury_risk_dict[body_part_side].synergist_eccentric_intensity_today = max(
                        synergist.eccentric_intensity,
                        injury_risk_dict[body_part_side].synergist_eccentric_intensity_today)
                    injury_risk_dict[body_part_side].synergist_compensating_concentric_intensity_today = max(
                        synergist.compensated_concentric_intensity,
                        injury_risk_dict[body_part_side].synergist_compensating_concentric_intensity_today)
                    injury_risk_dict[body_part_side].synergist_compensating_eccentric_intensity_today = max(
                        synergist.compensated_eccentric_intensity,
                        injury_risk_dict[body_part_side].synergist_compensating_eccentric_intensity_today)
                    injury_risk_dict[body_part_side].synergist_total_intensity_today = max(
                        synergist.total_intensity(),
                        injury_risk_dict[body_part_side].synergist_total_intensity_today)

                    injury_risk_dict[body_part_side].compensating_causes_volume_today.extend(
                        synergist.compensating_causes_volume)
                    injury_risk_dict[body_part_side].compensating_causes_intensity_today.extend(
                        synergist.compensating_causes_intensity)

                    if len(synergist.compensating_causes_volume) > 0 or len(synergist.compensating_causes_intensity) > 0:
                        injury_risk_dict[body_part_side].last_compensation_date = base_date
                        #TODO - take merge compensation sources here
                    injury_risk_dict[body_part_side].compensating_source_volume = synergist.compensation_source_volume
                    injury_risk_dict[body_part_side].compensating_source_intensity = synergist.compensation_source_intensity

        for body_part_side, body_part_injury_risk in injury_risk_dict.items():
            # injury_risk_dict[body_part_side].concentric_volume_today += (injury_risk_dict[body_part_side].prime_mover_concentric_volume_today +
            #                                                              injury_risk_dict[body_part_side].synergist_concentric_volume_today +
            #                                                              injury_risk_dict[
            #                                                                  body_part_side].synergist_compensating_concentric_volume_today)
            # injury_risk_dict[body_part_side].eccentric_volume_today += (injury_risk_dict[body_part_side].prime_mover_eccentric_volume_today +
            #                                                              injury_risk_dict[body_part_side].synergist_eccentric_volume_today +
            #                                                              injury_risk_dict[
            #                                                                  body_part_side].synergist_compensating_eccentric_volume_today)

            injury_risk_dict[body_part_side].eccentric_volume_ramp_today = injury_risk_dict[
                body_part_side].eccentric_volume_ramp()
            injury_risk_dict[body_part_side].total_volume_ramp_today = injury_risk_dict[
                body_part_side].total_volume_ramp()

            injury_risk_dict[body_part_side].total_compensation_percent = injury_risk_dict[
                body_part_side].percent_total_compensation()
            injury_risk_dict[body_part_side].eccentric_compensation_percent = injury_risk_dict[
                body_part_side].percent_eccentric_compensation()

            # if injury_risk_dict[body_part_side].eccentric_volume_ramp_today > 1.0 or injury_risk_dict[body_part_side].total_volume_ramp_today > 1.0:
            #     injury_risk_dict[body_part_side].last_excessive_strain_date = base_date
            #     injury_risk_dict[body_part_side].last_inhibited_date = base_date
            #
            # if 1.0 < injury_risk_dict[body_part_side].eccentric_volume_ramp_today <= 1.05:
            #     injury_risk_dict[body_part_side].last_functional_overreaching_date = base_date
            # elif 1.05 < injury_risk_dict[body_part_side].eccentric_volume_ramp_today:
            #     injury_risk_dict[body_part_side].last_non_functional_overreaching_date = base_date
            #
            # elif 1.0 < injury_risk_dict[body_part_side].total_volume_ramp_today <= 1.1:
            #     injury_risk_dict[body_part_side].last_functional_overreaching_date = base_date
            # elif 1.1 < injury_risk_dict[body_part_side].total_volume_ramp_today:
            #     injury_risk_dict[body_part_side].last_non_functional_overreaching_date = base_date


        return injury_risk_dict


    def process_todays_symptoms(self, base_date, injury_risk_dict):

        todays_symptoms = [s for s in self.symptoms if s.reported_date_time.date() == base_date]

        # TODO: check for ligament or severity-based measures

        for t in todays_symptoms:

            #related_joints = self.functional_anatomy_processor.get_related_joints(t.body_part.location.value)

            # Inflammation
            injury_risk_dict = self.identify_inflammation_today(base_date, t, injury_risk_dict)

            # Muscle Spasm
            injury_risk_dict = self.identify_muscle_spasm_today(base_date, t, injury_risk_dict)

            # Adhesions
            injury_risk_dict = self.identify_adhesions_today(base_date, t, injury_risk_dict)

        return injury_risk_dict

    def identify_inflammation_today(self, base_date, target_symptom, injury_risk_dict):

        # max_related_joint_sharp_count_last_10_days = 0
        # max_related_joint_ache_count_last_10_days = 0

        # is the target symptom a muscle, or joint? (or ligament)

        body_part_factory = BodyPartFactory()

        is_muscle = body_part_factory.is_muscle(target_symptom.body_part)
        is_ligament = body_part_factory.is_ligament(target_symptom.body_part)

        target_body_part_side = BodyPartSide(target_symptom.body_part.location, target_symptom.side)

        if is_muscle:

            if target_symptom.sharp is not None and target_symptom.sharp > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < base_date:
                        injury_risk_dict[target_body_part_side].last_sharp_date = base_date
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_inflammation_date = base_date
                    injury_risk_dict[target_body_part_side].last_inhibited_date = base_date
                    injury_risk_dict[target_body_part_side].last_sharp_level = target_symptom.sharp
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_inflammation_date = base_date
                    body_part_injury_risk.last_inhibited_date = base_date
                    body_part_injury_risk.last_sharp_date = base_date
                    body_part_injury_risk.last_sharp_level = target_symptom.sharp
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_inflammation_date = base_date
                    injury_risk_dict[target_body_part_side].last_inhibited_date = base_date
                    injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_inflammation_date = base_date
                    body_part_injury_risk.last_inhibited_date = base_date
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk
        else:

            # either joint or ligament

            sharp_count = 0
            ache_count = 0
            ache_count_10_20 = 0

            # any sharp symptoms get marked inflammation

            if target_symptom.sharp is not None and target_symptom.sharp > 0:

                if target_body_part_side in injury_risk_dict:
                    sharp_count = injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days
                    if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < base_date:
                        injury_risk_dict[target_body_part_side].last_sharp_date = base_date
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
                        injury_risk_dict[target_body_part_side].last_sharp_level = target_symptom.sharp
                        sharp_count = injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days
                    injury_risk_dict[target_body_part_side].last_inflammation_date = base_date
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_sharp_date = base_date
                    body_part_injury_risk.last_sharp_level = target_symptom.sharp
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    body_part_injury_risk.last_inflammation_date = base_date
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache > 0:

                if target_body_part_side in injury_risk_dict:
                    ache_count = injury_risk_dict[target_body_part_side].ache_count_last_0_10_days
                    ache_count_10_20 = injury_risk_dict[target_body_part_side].ache_count_last_0_20_days
                    if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                        injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                        ache_count = injury_risk_dict[target_body_part_side].ache_count_last_0_10_days
                        ache_count_10_20 = injury_risk_dict[target_body_part_side].ache_count_last_0_20_days
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

                # moderate severity or 2 reports in last 10 days
                # TODO: is moderate to high ache severity > 3?
                if target_symptom.ache > 3 or (ache_count >= 2 and ache_count == ache_count_10_20):
                    injury_risk_dict[target_body_part_side].last_inflammation_date = base_date

            # second, mark it inflamed, noting that joints cannot be inhibited as well
            # update the injury risk dict accordingly
            if ache_count >= 2 and ache_count == ache_count_10_20:
                if target_body_part_side in injury_risk_dict:
                    injury_risk_dict[target_body_part_side].last_inflammation_date = base_date
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_inflammation_date = base_date
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

                # third, mark all related muscles both inhibited and inflamed
                if is_ligament:
                    related_muscles = self.functional_anatomy_processor.get_related_muscles_for_ligament(
                        target_body_part_side.body_part_location.value)
                else:
                    related_muscles = self.functional_anatomy_processor.get_related_muscles_for_joint(
                        target_body_part_side.body_part_location.value)

                if related_muscles is not None:
                    for r in related_muscles:
                        if target_body_part_side.side == 0:
                            bilateral = body_part_factory.get_bilateral(BodyPartLocation(r))
                            if bilateral:
                                sides = [1, 2]
                            else:
                                sides = [0]
                        else:
                            sides = [target_body_part_side.side]
                        for sd in sides:
                            body_part_side = BodyPartSide(BodyPartLocation(r), sd)
                            if body_part_side in injury_risk_dict:
                                injury_risk_dict[body_part_side].last_inflammation_date = base_date
                                injury_risk_dict[body_part_side].last_inhibited_date = base_date
                            else:
                                body_part_injury_risk = BodyPartInjuryRisk()
                                body_part_injury_risk.last_inflammation_date = base_date
                                body_part_injury_risk.last_inhibited_date = base_date
                                injury_risk_dict[body_part_side] = body_part_injury_risk

        return injury_risk_dict

    def identify_muscle_spasm_today(self, base_date, target_symptom, injury_risk_dict):

        body_part_factory = BodyPartFactory()

        is_muscle = body_part_factory.is_muscle(target_symptom.body_part)
        is_ligament = body_part_factory.is_ligament(target_symptom.body_part)

        target_body_part_side = BodyPartSide(target_symptom.body_part.location, target_symptom.side)

        # TODO: is moderate to high ache severity > 3?

        if is_muscle:

            if target_symptom.sharp is not None and target_symptom.sharp > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < base_date:
                        injury_risk_dict[target_body_part_side].last_sharp_date = base_date
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_muscle_spasm_date = base_date
                    injury_risk_dict[target_body_part_side].last_sharp_level = target_symptom.sharp
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_muscle_spasm_date = base_date
                    body_part_injury_risk.last_sharp_date = base_date
                    body_part_injury_risk.last_sharp_level = target_symptom.sharp
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.tight is not None and target_symptom.tight > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_tight_date is None or injury_risk_dict[target_body_part_side].last_tight_date < base_date:
                        injury_risk_dict[target_body_part_side].last_tight_date = base_date
                        #injury_risk_dict[target_body_part_side].tight_count_last_0_10_days += 1  # not tracked
                    injury_risk_dict[target_body_part_side].last_muscle_spasm_date = base_date
                    injury_risk_dict[target_body_part_side].last_tight_level = target_symptom.tight
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_muscle_spasm_date = base_date
                    body_part_injury_risk.last_tight_date = base_date
                    body_part_injury_risk.last_tight_level = target_symptom.tight
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache > 3:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_muscle_spasm_date = base_date
                    injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_muscle_spasm_date = base_date
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache <= 3:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].ache_count_last_0_10_days >= 2:
                        injury_risk_dict[target_body_part_side].last_muscle_spasm_date = base_date
                    # just for tracking
                    if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    #body_part_injury_risk.last_muscle_spasm_date = event_date_time.date()  # not muscle spasm, just tracking
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

        else:

            mark_related_muscles = False

            if target_symptom.sharp is not None and target_symptom.sharp > 0:
                mark_related_muscles = True

                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < base_date:
                        injury_risk_dict[target_body_part_side].last_sharp_date = base_date
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_sharp_level = target_symptom.sharp

                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_sharp_date = base_date
                    body_part_injury_risk.last_sharp_level = target_symptom.sharp
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.tight is not None and target_symptom.tight > 0:
                mark_related_muscles = True

                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_tight_date is None or injury_risk_dict[target_body_part_side].last_tight_date < base_date:
                        injury_risk_dict[target_body_part_side].last_tight_date = base_date
                        #injury_risk_dict[target_body_part_side].tight_count_last_0_10_days += 1  # not tracked

                    injury_risk_dict[target_body_part_side].last_tight_level = target_symptom.tight
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_tight_date = base_date
                    body_part_injury_risk.last_tight_level = target_symptom.tight
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache > 3:
                mark_related_muscles = True
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache <= 3:

                if is_ligament:
                    mark_related_muscles = True  # related muscles of ligaments reported ache at any level should be muscle spasm

                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].ache_count_last_0_10_days >= 2:
                        mark_related_muscles = True
                    # just for tracking
                    if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    #body_part_injury_risk.last_muscle_spasm_date = event_date_time.date()  # not muscle spasm, just tracking
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if mark_related_muscles:
                if is_ligament:
                    related_muscles = self.functional_anatomy_processor.get_related_muscles_for_ligament(
                        target_body_part_side.body_part_location.value)
                else:
                    related_muscles = self.functional_anatomy_processor.get_related_muscles_for_joint(
                        target_body_part_side.body_part_location.value)
                body_part_factory = BodyPartFactory()

                if related_muscles is not None:
                    for r in related_muscles:
                        if target_body_part_side.side == 0:
                            bilateral = body_part_factory.get_bilateral(BodyPartLocation(r))
                            if bilateral:
                                sides = [1, 2]
                            else:
                                sides = [0]
                        else:
                            sides = [target_body_part_side.side]
                        for sd in sides:
                            body_part_side = BodyPartSide(BodyPartLocation(r), sd)
                            if body_part_side in injury_risk_dict:
                                injury_risk_dict[body_part_side].last_muscle_spasm_date = base_date
                            else:
                                body_part_injury_risk = BodyPartInjuryRisk()
                                body_part_injury_risk.last_muscle_spasm_date = base_date
                                injury_risk_dict[body_part_side] = body_part_injury_risk

        return injury_risk_dict

    def identify_adhesions_today(self, base_date, target_symptom, injury_risk_dict):

        body_part_factory = BodyPartFactory()

        is_muscle = body_part_factory.is_muscle(target_symptom.body_part)
        is_ligament = body_part_factory.is_ligament(target_symptom.body_part)

        target_body_part_side = BodyPartSide(target_symptom.body_part.location, target_symptom.side)

        if is_muscle:

            mark_adhesions = False

            if target_symptom.knots is not None and target_symptom.knots > 0:

                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].last_knots_date is None or injury_risk_dict[target_body_part_side].last_knots_date < base_date:
                        injury_risk_dict[target_body_part_side].last_knots_date = base_date
                        # injury_risk_dict[target_body_part_side].knots_count_last_0_20_days += 1
                    injury_risk_dict[target_body_part_side].last_adhesions_date = base_date
                    injury_risk_dict[target_body_part_side].last_short_date = base_date
                    injury_risk_dict[target_body_part_side].last_knots_level = target_symptom.knots
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_adhesions_date = base_date
                    body_part_injury_risk.last_short_date = base_date
                    body_part_injury_risk.last_knots_date = base_date
                    body_part_injury_risk.last_knots_level = target_symptom.knots
                    #body_part_injury_risk.knots_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.tight is not None and target_symptom.tight > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].tight_count_last_0_20_days >= 3:
                        injury_risk_dict[target_body_part_side].last_adhesions_date = base_date
                        injury_risk_dict[target_body_part_side].last_short_date = base_date
                    # just for tracking
                    if injury_risk_dict[target_body_part_side].last_tight_date is None or injury_risk_dict[target_body_part_side].last_tight_date < base_date:
                        injury_risk_dict[target_body_part_side].last_tight_date = base_date
                        #injury_risk_dict[target_body_part_side].tight_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_tight_level = target_symptom.tight
                else:
                    # just for tracking
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_tight_date = base_date
                    body_part_injury_risk.last_tight_level = target_symptom.ache
                    #body_part_injury_risk.tight_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.sharp is not None and target_symptom.sharp > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].sharp_count_last_0_20_days >= 3:
                        injury_risk_dict[target_body_part_side].last_adhesions_date = base_date
                        injury_risk_dict[target_body_part_side].last_short_date = base_date
                    # just for tracking
                    if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < base_date:
                        injury_risk_dict[target_body_part_side].last_sharp_date = base_date
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_sharp_level = target_symptom.sharp
                else:
                    # just for tracking
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_sharp_date = base_date
                    body_part_injury_risk.last_sharp_level = target_symptom.sharp
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].ache_count_last_0_20_days >= 4: # higher for ache
                        injury_risk_dict[target_body_part_side].last_adhesions_date = base_date
                        injury_risk_dict[target_body_part_side].last_short_date = base_date
                    # just for tracking
                    if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                else:
                    # just for tracking
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

        else:

            mark_related_muscles = False

            if target_symptom.tight is not None and target_symptom.tight > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].tight_count_last_0_20_days >= 3:
                        mark_related_muscles = True
                        if is_ligament:
                            if injury_risk_dict[target_body_part_side].last_inflammation_date == base_date:
                                injury_risk_dict[target_body_part_side].last_tendinopathy_date = base_date
                            else:
                                injury_risk_dict[target_body_part_side].last_tendinosis_date = base_date
                        else:
                            injury_risk_dict[target_body_part_side].last_altered_joint_arthokinematics_date = base_date
                    # just for tracking
                    if injury_risk_dict[target_body_part_side].last_tight_date is None or injury_risk_dict[target_body_part_side].last_tight_date < base_date:
                        injury_risk_dict[target_body_part_side].last_tight_date = base_date
                        # injury_risk_dict[target_body_part_side].tight_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_tight_level = target_symptom.tight
                else:
                    # just for tracking
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_tight_date = base_date
                    body_part_injury_risk.last_tight_level = target_symptom.ache
                    # body_part_injury_risk.tight_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.sharp is not None and target_symptom.sharp > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].sharp_count_last_0_20_days >= 3:
                        mark_related_muscles = True
                        if is_ligament:
                            if injury_risk_dict[target_body_part_side].last_inflammation_date == base_date:
                                injury_risk_dict[target_body_part_side].last_tendinopathy_date = base_date
                            else:
                                injury_risk_dict[target_body_part_side].last_tendinosis_date = base_date
                        else:
                            injury_risk_dict[target_body_part_side].last_altered_joint_arthokinematics_date = base_date
                    # just for tracking
                    if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < base_date:
                        injury_risk_dict[target_body_part_side].last_sharp_date = base_date
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_sharp_level = target_symptom.sharp
                else:
                    # just for tracking
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_sharp_date = base_date
                    body_part_injury_risk.last_sharp_level = target_symptom.sharp
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache > 0:
                if target_body_part_side in injury_risk_dict:
                    if is_ligament:
                        threshold = 3
                    else:
                        threshold = 4
                    if injury_risk_dict[target_body_part_side].ache_count_last_0_20_days >= threshold:  # higher for ache - joint
                        mark_related_muscles = True
                        if is_ligament:
                            if injury_risk_dict[target_body_part_side].last_inflammation_date == base_date:
                                injury_risk_dict[target_body_part_side].last_tendinopathy_date = base_date
                            else:
                                injury_risk_dict[target_body_part_side].last_tendinosis_date = base_date
                        else:
                            injury_risk_dict[target_body_part_side].last_altered_joint_arthokinematics_date = base_date
                    # just for tracking
                    if injury_risk_dict[target_body_part_side].last_ache_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                else:
                    # just for tracking
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if mark_related_muscles:
                if is_ligament:
                    related_muscles = self.functional_anatomy_processor.get_related_muscles_for_ligament(
                        target_body_part_side.body_part_location.value)
                else:
                    related_muscles = self.functional_anatomy_processor.get_related_muscles_for_joint(
                        target_body_part_side.body_part_location.value)

                if related_muscles is not None:
                    for r in related_muscles:
                        if target_body_part_side.side == 0:
                            bilateral = body_part_factory.get_bilateral(BodyPartLocation(r))
                            if bilateral:
                                sides = [1, 2]
                            else:
                                sides = [0]
                        else:
                            sides = [target_body_part_side.side]
                        for sd in sides:
                            body_part_side = BodyPartSide(BodyPartLocation(r), sd)
                            #body_part_side = BodyPartSide(BodyPartLocation(r), target_symptom.side)
                            if body_part_side in injury_risk_dict:
                                injury_risk_dict[body_part_side].last_adhesions_date = base_date
                            else:
                                body_part_injury_risk = BodyPartInjuryRisk()
                                body_part_injury_risk.last_adhesions_date = base_date
                                injury_risk_dict[body_part_side] = body_part_injury_risk

        return injury_risk_dict
