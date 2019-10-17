from datetime import datetime, timedelta
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.functional_movement import BodyPartInjuryRisk, SessionFunctionalMovement
from models.body_parts import BodyPart, BodyPartFactory
from copy import deepcopy
import statistics
import math


class InjuryRiskProcessor(object):
    def __init__(self, event_date_time, symptoms_list, training_session_list, injury_risk_dict, load_stats):
        self.event_date_time = event_date_time
        self.symptoms = symptoms_list
        self.training_sessions = training_session_list
        self.load_stats = load_stats
        self.injury_risk_dict = injury_risk_dict
        self.aggregated_injury_risk_dict = {}
        self.two_days_ago = self.event_date_time.date() - timedelta(days=1)
        self.three_days_ago = self.event_date_time.date() - timedelta(days=2)
        self.ten_days_ago = self.event_date_time.date() - timedelta(days=9)
        self.twenty_days_ago = self.event_date_time.date() - timedelta(days=19)
        self.functional_anatomy_processor = FunctionalAnatomyProcessor()
        self.eccentric_volume_dict = {}
        self.concentric_volume_dict = {}
        self.total_volume_dict = {}

    def process(self, update_historical_data=False, aggregate_results=False):

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

            return self.aggregated_injury_risk_dict
        else:
            return self.injury_risk_dict

    def reset_reported_symptoms(self, injury_risk_dict):

        for b in self.injury_risk_dict.keys():
            injury_risk_dict[b].last_sharp_date = None
            injury_risk_dict[b].last_ache_date = None
            injury_risk_dict[b].last_tight_date = None
            injury_risk_dict[b].sharp_count_last_0_20_days = 0
            injury_risk_dict[b].sharp_count_last_0_10_days = 0
            injury_risk_dict[b].ache_count_last_0_20_days = 0
            injury_risk_dict[b].ache_count_last_0_10_days = 0
            injury_risk_dict[b].ache_count_last_0_10_days = 0
            injury_risk_dict[b].tight_count_last_0_20_days = 0
            injury_risk_dict[b].knots_count_last_0_20_days = 0

    def update_historical_symptoms(self, base_date, injury_risk_dict):

        twenty_days_ago = base_date - timedelta(days=19)
        ten_days_ago = base_date - timedelta(days=9)
        three_days_ago = base_date - timedelta(days=2)

        last_20_days_symptoms = [s for s in self.symptoms if
                                 base_date >= s.reported_date_time.date() >= twenty_days_ago]

        last_20_days_symptoms = sorted(last_20_days_symptoms, key=lambda k: k.reported_date_time)
        #self.reset_reported_symptoms(injury_risk_dict)

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

        #days_1_15 = [d for d in combined_dates if d < self.twenty_days_ago.date()]



        # for d in days_1_15:
        #     initial_sessions = [t for t in self.training_sessions if t.event_date_time.date() == d]
        #     for s in initial_sessions:
        #         session_functional_movement = SessionFunctionalMovement(s, injury_risk_dict)
        #         session_functional_movement.process()
        #
        #         # update injury_risk_dict from session, calculate ramp, etc.

        #self.reset_reported_symptoms() # --> maybe start with brand new injury risk dict?

        #combined_dates = [d for d in combined_dates if d >= self.twenty_days_ago.date()]
        injury_risk_dict = {}

        for d in combined_dates:

            seven_days_ago = d - timedelta(days=6)
            fourteeen_days_ago = d - timedelta(days=13)

            injury_risk_dict = {}
            # first let's update our historical data
            injury_risk_dict = self.update_historical_symptoms(d, injury_risk_dict)
            # TODO - assign status to symptoms not today
            injury_risk_dict = self.process_todays_symptoms(d, injury_risk_dict)
            # now process todays sessions
            daily_sessions = [n for n in self.training_sessions if n.event_date.date() == d]

            for session in daily_sessions:
                session_functional_movement = SessionFunctionalMovement(session, injury_risk_dict)
                session_functional_movement.process(d, load_stats)

                for b in session_functional_movement.body_parts:

                    if b.body_part_side not in injury_risk_dict:
                        injury_risk_dict[b.body_part_side] = BodyPartInjuryRisk()

                    if b.body_part_side not in self.eccentric_volume_dict:
                        self.eccentric_volume_dict[b.body_part_side] = {}  # now we have a dictionary of dictionaries
                    if d not in self.eccentric_volume_dict[b.body_part_side]:
                        self.eccentric_volume_dict[b.body_part_side][d] = 0
                    self.eccentric_volume_dict[b.body_part_side][d] += b.eccentric_volume

                    if b.body_part_side not in self.concentric_volume_dict:
                        self.concentric_volume_dict[b.body_part_side] = {}  # now we have a dictionary of dictionaries
                    if d not in self.concentric_volume_dict[b.body_part_side]:
                        self.concentric_volume_dict[b.body_part_side][d] = 0
                    self.concentric_volume_dict[b.body_part_side][d] += b.concentric_volume

                    if b.body_part_side not in self.total_volume_dict:
                        self.total_volume_dict[b.body_part_side] = {}  # now we have a dictionary of dictionaries
                    if d not in self.total_volume_dict[b.body_part_side]:
                        self.total_volume_dict[b.body_part_side][d] = 0
                    self.total_volume_dict[b.body_part_side][d] += b.concentric_volume + b.eccentric_volume

                    eccentric_volume_dict = self.eccentric_volume_dict[b.body_part_side]
                    concentric_volume_dict = self.concentric_volume_dict[b.body_part_side]
                    total_volume_dict = self.total_volume_dict[b.body_part_side]

                    last_week_eccentric_volume_dict = dict(
                        filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago, eccentric_volume_dict.items()))

                    last_week_concentric_volume_dict = dict(
                        filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago, concentric_volume_dict.items()))

                    last_week_total_volume_dict = dict(
                        filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago,
                               total_volume_dict.items()))

                    current_week_eccentric_volume_dict = dict(
                        filter(lambda elem: d > elem[0] >= seven_days_ago, eccentric_volume_dict.items()))

                    current_week_concentric_volume_dict = dict(
                        filter(lambda elem: d > elem[0] >= seven_days_ago, concentric_volume_dict.items()))

                    current_week_total_volume_dict = dict(
                        filter(lambda elem: d > elem[0] >= seven_days_ago, total_volume_dict.items()))

                    today_eccentric_volume_dict = dict(
                        filter(lambda elem: elem[0] == d, eccentric_volume_dict.items())
                        )

                    today_concentric_volume_dict = dict(
                        filter(lambda elem: elem[0] == d, concentric_volume_dict.items()))

                    today_total_volume_dict = dict(
                        filter(lambda elem: elem[0] == d, total_volume_dict.items()))

                    last_week_eccentric_volume = sum(last_week_eccentric_volume_dict.values())
                    last_week_concentric_volume = sum(last_week_concentric_volume_dict.values())
                    ast_week_total_volume = sum(last_week_total_volume_dict.values())

                    todays_eccentric_volume = sum(today_eccentric_volume_dict.values())
                    todays_concentric_volume = sum(today_concentric_volume_dict.values())
                    todays_total_volume = sum(today_total_volume_dict.values())

                    current_week_concentric_volume = sum(current_week_concentric_volume_dict.values())
                    current_week_eccentric_volume = sum(current_week_eccentric_volume_dict.values())
                    current_week_total_volume = sum(current_week_total_volume_dict.values())
                    ecc_t_score = 0
                    total_t_score = 0

                    all_ecc_values = []
                    all_ecc_values.extend(last_week_eccentric_volume_dict.values())
                    all_ecc_values.extend(current_week_eccentric_volume_dict.values())
                    all_ecc_values.append(todays_eccentric_volume)
                    all_ecc_values = [a for a in all_ecc_values if a > 0]
                    if len(all_ecc_values) >= 3:
                        current_ecc_std = statistics.stdev(all_ecc_values)
                        current_ecc_avg = statistics.mean(all_ecc_values)
                        if current_ecc_std != 0:
                            ecc_t_score = (todays_eccentric_volume - current_ecc_avg) / (current_ecc_std/math.sqrt(len(all_ecc_values)))
                            injury_risk_dict[b.body_part_side].ecc_volume_obs = len(all_ecc_values)
                            injury_risk_dict[b.body_part_side].ecc_stddev = current_ecc_std
                            injury_risk_dict[b.body_part_side].ecc_mean = current_ecc_avg
                            if self.is_1_significant(ecc_t_score, len(all_ecc_values)):
                                injury_risk_dict[b.body_part_side].last_excessive_strain_date = d
                                injury_risk_dict[b.body_part_side].last_inhibited_date = d
                                injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = d
                            elif self.is_2_significant(ecc_t_score, len(all_ecc_values)):
                                injury_risk_dict[b.body_part_side].last_excessive_strain_date = d
                                injury_risk_dict[b.body_part_side].last_inhibited_date = d
                                injury_risk_dict[b.body_part_side].last_functional_overreaching_date = d

                    # all_total_values = []
                    # all_total_values.extend(last_week_total_volume_dict.values())
                    # all_total_values.extend(current_week_total_volume_dict.values())
                    # all_total_values.append(todays_total_volume)
                    # all_total_values = [a for a in all_total_values if a > 0]
                    # if len(all_total_values) >= 3:
                    #     current_total_std = statistics.stdev(all_total_values)
                    #     current_total_avg = statistics.mean(all_total_values)
                    #     if current_total_std != 0:
                    #         total_t_score = (todays_total_volume - current_total_avg) / (current_total_std/math.sqrt(len(all_total_values)))
                    #         injury_risk_dict[b.body_part_side].total_volume_obs = len(all_total_values)
                    #         injury_risk_dict[b.body_part_side].total_stddev = current_total_std
                    #         injury_risk_dict[b.body_part_side].total_mean = current_total_avg
                    #         if self.is_1_significant(total_t_score, len(all_total_values)):
                    #             injury_risk_dict[b.body_part_side].last_excessive_strain_date = d
                    #             injury_risk_dict[b.body_part_side].last_inhibited_date = d
                    #             injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = d
                    #         elif self.is_2_significant(total_t_score, len(all_total_values)):
                    #             injury_risk_dict[b.body_part_side].last_excessive_strain_date = d
                    #             injury_risk_dict[b.body_part_side].last_inhibited_date = d
                    #             injury_risk_dict[b.body_part_side].last_functional_overreaching_date = d

                    # if len(last_week_eccentric_volume_dict.values()) > 1:
                    #     last_ecc_std = statistics.stdev(last_week_eccentric_volume_dict.values())
                    # if len(last_week_concentric_volume_dict.values()) > 1:
                    #     last_con_std = statistics.stdev(last_week_concentric_volume_dict.values())


                    injury_risk_dict[b.body_part_side].eccentric_volume_this_week = current_week_eccentric_volume
                    injury_risk_dict[b.body_part_side].eccentric_volume_last_week = last_week_eccentric_volume
                    injury_risk_dict[b.body_part_side].eccentric_volume_today = todays_eccentric_volume

                    injury_risk_dict[b.body_part_side].concentric_volume_this_week = current_week_concentric_volume
                    injury_risk_dict[b.body_part_side].concentric_volume_last_week = last_week_concentric_volume
                    injury_risk_dict[b.body_part_side].concentric_volume_today = todays_concentric_volume

                    # eccentric_volume_ramp = injury_risk_dict[b.body_part_side].eccentric_volume_ramp()
                    # total_volume_ramp = injury_risk_dict[b.body_part_side].total_volume_ramp()

                    # if eccentric_volume_ramp > 1.0 or total_volume_ramp > 1.0:
                    #     injury_risk_dict[b.body_part_side].last_excessive_strain_date = d
                    #     #injury_risk_dict[b.body_part_side].last_inflammation_date = d
                    #     injury_risk_dict[b.body_part_side].last_inhibited_date = d
                    #
                    # if 1.0 < eccentric_volume_ramp <= 1.05:
                    #     injury_risk_dict[b.body_part_side].last_functional_overreaching_date = d
                    # elif 1.05 < eccentric_volume_ramp:
                    #     injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = d
                    #
                    # if 1.0 < total_volume_ramp <= 1.1:
                    #     injury_risk_dict[b.body_part_side].last_functional_overreaching_date = d
                    # elif 1.1 < total_volume_ramp:
                    #     injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = d
        return injury_risk_dict

    def is_10_significant(self, t_stat, obs):

        df = obs - 1

        if df < 1:
            return False

        crit_vals = {}
        crit_vals[1] = 6.314
        crit_vals[2] = 2.920
        crit_vals[3] = 2.353
        crit_vals[4] = 2.132
        crit_vals[5] = 2.015
        crit_vals[6] = 1.943
        crit_vals[7] = 1.895
        crit_vals[8] = 1.860
        crit_vals[9] = 1.833
        crit_vals[10] = 1.812
        crit_vals[11] = 1.796
        crit_vals[12] = 1.782
        crit_vals[13] = 1.771

        if df in crit_vals:
            if abs(t_stat) > abs(crit_vals[obs]):
                return True
            else:
                return False

        else:
            if abs(t_stat) > 1.7:
                return True
            else:
                return False

    def is_5_significant(self, t_stat, obs):

        df = obs - 1

        if df < 1:
            return False

        crit_vals = {}
        crit_vals[1] = 12.706
        crit_vals[2] = 4.303
        crit_vals[3] = 3.182
        crit_vals[4] = 2.776
        crit_vals[5] = 2.571
        crit_vals[6] = 2.447
        crit_vals[7] = 2.365
        crit_vals[8] = 2.306
        crit_vals[9] = 2.262
        crit_vals[10] = 2.228
        crit_vals[11] = 2.201
        crit_vals[12] = 2.179
        crit_vals[13] = 2.160

        if df in crit_vals:
            if abs(t_stat) > abs(crit_vals[obs]):
                return True
            else:
                return False

        else:
            if abs(t_stat) > 2.0:
                return True
            else:
                return False

    def is_1_significant(self, t_stat, obs):

        df = obs - 1

        if df < 1:
            return False

        crit_vals = {}
        crit_vals[1] = 63.657
        crit_vals[2] = 9.925
        crit_vals[3] = 5.841
        crit_vals[4] = 4.604
        crit_vals[5] = 4.032
        crit_vals[6] = 3.707
        crit_vals[7] = 3.499
        crit_vals[8] = 3.355
        crit_vals[9] = 3.250
        crit_vals[10] = 3.169
        crit_vals[11] = 3.106
        crit_vals[12] = 3.055
        crit_vals[13] = 2.977

        if df in crit_vals:
            if abs(t_stat) > abs(crit_vals[obs]):
                return True
            else:
                return False

        else:
            if abs(t_stat) > 2.8:
                return True
            else:
                return False

    def is_2_significant(self, t_stat, obs):

        df = obs - 1

        if df < 1:
            return False

        # crit_vals = {}
        # crit_vals[1] = 63.657
        # crit_vals[2] = 9.925
        # crit_vals[3] = 5.841
        # crit_vals[4] = 4.604
        # crit_vals[5] = 4.032
        # crit_vals[6] = 3.707
        # crit_vals[7] = 3.499
        # crit_vals[8] = 3.355
        # crit_vals[9] = 3.250
        # crit_vals[10] = 3.169
        # crit_vals[11] = 3.106
        # crit_vals[12] = 3.055
        # crit_vals[13] = 2.977
        #0.03
        crit_vals = {}
        crit_vals[1] = 31.821
        crit_vals[2] = 6.965
        crit_vals[3] = 4.541
        crit_vals[4] = 3.747
        crit_vals[5] = 3.365
        crit_vals[6] = 3.143
        crit_vals[7] = 2.998
        crit_vals[8] = 2.896
        crit_vals[9] = 2.821
        crit_vals[10] = 2.764
        crit_vals[11] = 2.718
        crit_vals[12] = 2.681
        crit_vals[13] = 2.650

        if df in crit_vals:
            if abs(t_stat) > abs(crit_vals[obs]):
                return True
            else:
                return False

        else:
            if abs(t_stat) > 2.6:
                return True
            else:
                return False


    def process_todays_sessions(self, base_date, injury_risk_dict, load_stats):

        daily_sessions = [n for n in self.training_sessions if n.event_date.date() == base_date]

        for session in daily_sessions:
            session_functional_movement = SessionFunctionalMovement(session, injury_risk_dict)
            session_functional_movement.process(base_date, load_stats)
            for b in session_functional_movement.body_parts:

                if b.body_part_side not in injury_risk_dict:
                    injury_risk_dict[b.body_part_side] = BodyPartInjuryRisk()

                injury_risk_dict[b.body_part_side].eccentric_volume_today += b.eccentric_volume
                injury_risk_dict[b.body_part_side].concentric_volume_today += b.concentric_volume
                injury_risk_dict[b.body_part_side].is_compensating = b.is_compensating
                injury_risk_dict[b.body_part_side].compensating_source = b.compensation_source

                if injury_risk_dict[b.body_part_side].ecc_volume_obs >= 2:
                    if injury_risk_dict[b.body_part_side].ecc_stddev != 0:
                        ecc_t_score = (injury_risk_dict[b.body_part_side].eccentric_volume_today - injury_risk_dict[b.body_part_side].ecc_mean) / (
                                injury_risk_dict[b.body_part_side].ecc_stddev / math.sqrt(injury_risk_dict[b.body_part_side].ecc_volume_obs))

                        if self.is_1_significant(ecc_t_score, injury_risk_dict[b.body_part_side].ecc_volume_obs+1):
                            injury_risk_dict[b.body_part_side].last_excessive_strain_date = base_date
                            injury_risk_dict[b.body_part_side].last_inhibited_date = base_date
                            injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = base_date
                        elif self.is_2_significant(ecc_t_score, injury_risk_dict[b.body_part_side].ecc_volume_obs+1):
                            injury_risk_dict[b.body_part_side].last_excessive_strain_date = base_date
                            injury_risk_dict[b.body_part_side].last_inhibited_date = base_date
                            injury_risk_dict[b.body_part_side].last_functional_overreaching_date = base_date

                # if injury_risk_dict[b.body_part_side].total_stddev != 0:
                #     total_volume_today = injury_risk_dict[b.body_part_side].eccentric_volume_today + injury_risk_dict[b.body_part_side].concentric_volume_today
                #     total_t_score = (total_volume_today - injury_risk_dict[b.body_part_side].total_mean) / (
                #             injury_risk_dict[b.body_part_side].total_stddev / math.sqrt(injury_risk_dict[b.body_part_side].total_volume_obs))
                #
                #     if self.is_1_significant(total_t_score, injury_risk_dict[b.body_part_side].total_volume_obs+1):
                #         injury_risk_dict[b.body_part_side].last_excessive_strain_date = base_date
                #         injury_risk_dict[b.body_part_side].last_inhibited_date = base_date
                #         injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = base_date
                #     elif self.is_2_significant(total_t_score, injury_risk_dict[b.body_part_side].total_volume_obs+1):
                #         injury_risk_dict[b.body_part_side].last_excessive_strain_date = base_date
                #         injury_risk_dict[b.body_part_side].last_inhibited_date = base_date
                #         injury_risk_dict[b.body_part_side].last_functional_overreaching_date = base_date

                #eccentric_volume_ramp = injury_risk_dict[b.body_part_side].eccentric_volume_ramp()
                #total_volume_ramp = injury_risk_dict[b.body_part_side].total_volume_ramp()

                # if eccentric_volume_ramp > 1.0 or total_volume_ramp > 1.0:
                #     injury_risk_dict[b.body_part_side].last_excessive_strain_date = base_date
                #     #injury_risk_dict[b.body_part_side].last_inflammation_date = base_date
                #     injury_risk_dict[b.body_part_side].last_inhibited_date = base_date
                #
                # if 1.0 < eccentric_volume_ramp <= 1.05:
                #     injury_risk_dict[b.body_part_side].last_functional_overreaching_date = base_date
                # elif 1.05 < eccentric_volume_ramp:
                #     injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = base_date
                #
                # if 1.0 < total_volume_ramp <= 1.1:
                #     injury_risk_dict[b.body_part_side].last_functional_overreaching_date = base_date
                # elif 1.1 < total_volume_ramp:
                #     injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = base_date

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

        # TODO: handle ligament differently
        if is_muscle or is_ligament:

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

            # assuming all non-muscles are joints (including ligaments)
            # TODO: accommodate ligaments

            sharp_count = 0
            ache_count = 0

            if target_symptom.sharp is not None and target_symptom.sharp > 0:

                # first, let's check to see how often this has happened

                if target_body_part_side in injury_risk_dict:
                    sharp_count = injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days
                    if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < base_date:
                        injury_risk_dict[target_body_part_side].last_sharp_date = base_date
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
                        injury_risk_dict[target_body_part_side].last_sharp_level = target_symptom.sharp
                        sharp_count = injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_sharp_date = base_date
                    body_part_injury_risk.last_sharp_level = target_symptom.sharp
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            if target_symptom.ache is not None and target_symptom.ache > 0:

                if target_body_part_side in injury_risk_dict:
                    ache_count = injury_risk_dict[target_body_part_side].ache_count_last_0_10_days
                    if injury_risk_dict[target_body_part_side].last_ache_date < base_date is None or injury_risk_dict[target_body_part_side].last_ache_date < base_date:
                        injury_risk_dict[target_body_part_side].last_ache_date = base_date
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                        injury_risk_dict[target_body_part_side].last_ache_level = target_symptom.ache
                        ache_count = injury_risk_dict[target_body_part_side].ache_count_last_0_10_days
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_ache_date = base_date
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    body_part_injury_risk.last_ache_level = target_symptom.ache
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

            # second, mark it inflamed, noting that joints cannot be inhibited as well
            # update the injury risk dict accordingly
            if sharp_count >= 2 or ache_count >= 2:
                if target_body_part_side in injury_risk_dict:
                    injury_risk_dict[target_body_part_side].last_inflammation_date = base_date
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_inflammation_date = base_date
                    injury_risk_dict[target_body_part_side] = body_part_injury_risk

                # third, mark all related muscles both inhibited and inflamed
                related_muscles = self.functional_anatomy_processor.get_related_muscles_from_joints(target_body_part_side.body_part_location.value)

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
                            injury_risk_dict[body_part_side].last_inflammation_date = base_date
                            injury_risk_dict[body_part_side].last_inhibited_date = base_date
                        else:
                            body_part_injury_risk = BodyPartInjuryRisk()
                            body_part_injury_risk.last_inflammation_date = base_date
                            body_part_injury_risk.last_inhibited_date = base_date
                            injury_risk_dict[body_part_side] = body_part_injury_risk

        # now treat everything with excessive strain in last 2 days as inflammation
        # #TODO right here GABBY
        # two_days_ago = base_date - timedelta(days=1)
        # excessive_strain_body_parts = dict(filter(lambda elem: elem[1].last_excessive_strain_date is not None and
        #                                                        elem[1].last_excessive_strain_date >= two_days_ago,
        #                                           injury_risk_dict.items()))
        #
        # for b, e in excessive_strain_body_parts.items():
        #     injury_risk_dict[b].last_inflammation_date = base_date
        #     injury_risk_dict[b].last_inhibited_date = base_date

        return injury_risk_dict

    def identify_muscle_spasm_today(self, base_date, target_symptom, injury_risk_dict):

        body_part_factory = BodyPartFactory()

        is_muscle = body_part_factory.is_muscle(target_symptom.body_part)
        is_ligament = body_part_factory.is_ligament(target_symptom.body_part)


        target_body_part_side = BodyPartSide(target_symptom.body_part.location, target_symptom.side)

        # TODO: is moderate to high ache severity > 3?

        # TODO: handle ligament differently
        if is_muscle or is_ligament:

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

            # assuming all non-muscles are joints (including ligaments)
            # TODO: accommodate ligaments
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
                related_muscles = self.functional_anatomy_processor.get_related_muscles_from_joints(
                    target_body_part_side.body_part_location.value)
                body_part_factory = BodyPartFactory()

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

        # TODO: handle ligament differently
        if is_muscle or is_ligament:

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
            # assuming all non-muscles are joints (including ligaments)
            # TODO: accommodate ligaments
            mark_related_muscles = False

            if target_symptom.tight is not None and target_symptom.tight > 0:
                if target_body_part_side in injury_risk_dict:
                    if injury_risk_dict[target_body_part_side].tight_count_last_0_20_days >= 3:
                        mark_related_muscles = True
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
                    if injury_risk_dict[target_body_part_side].ache_count_last_0_20_days >= 4:  # higher for ache
                        mark_related_muscles = True
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
                related_muscles = self.functional_anatomy_processor.get_related_muscles_from_joints(
                    target_body_part_side.body_part_location.value)

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
