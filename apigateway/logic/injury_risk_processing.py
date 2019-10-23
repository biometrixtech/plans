from datetime import datetime, timedelta
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.functional_movement import BodyPartInjuryRisk, SessionFunctionalMovement
from models.body_parts import BodyPart, BodyPartFactory
from copy import deepcopy
from datastores.session_datastore import SessionDatastore
from utils import format_date

class InjuryRiskProcessor(object):
    def __init__(self, event_date_time, symptoms_list, training_session_list, injury_risk_dict, load_stats, user_id):
        self.user_id = user_id
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
        self.prime_mover_eccentric_volume_dict = {}
        self.prime_mover_concentric_volume_dict = {}
        self.prime_mover_total_volume_dict = {}
        self.synergist_eccentric_volume_dict = {}
        self.synergist_concentric_volume_dict = {}
        self.synergist_total_volume_dict = {}

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
                injury_risk_dict[b].overactive_count_0_20_days += 1

            for b in underactive_inhibited_set:
                injury_risk_dict[b].underactive_inhibited_count_0_20_days += 1

            for b in underactive_weak_set:
                injury_risk_dict[b].underactive_weak_count_0_20_days += 1

            for b in compensating_set:
                injury_risk_dict[b].compensating_count_0_20_days += 1

            for b in short_set:
                injury_risk_dict[b].short_count_0_20_days += 1

            for b in long_set:
                injury_risk_dict[b].long_count_last_0_20_days += 1

        return injury_risk_dict

    def update_historical_symptoms(self, base_date, injury_risk_dict):

        twenty_days_ago = base_date - timedelta(days=19)
        ten_days_ago = base_date - timedelta(days=9)

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

            if d==self.event_date_time.date():
                j=0

            seven_days_ago = d - timedelta(days=6)
            fourteeen_days_ago = d - timedelta(days=13)

            injury_risk_dict = {}
            # first let's update our historical data
            injury_risk_dict = self.update_historical_symptoms(d, injury_risk_dict)

            injury_risk_dict = self.update_historic_session_stats(d, injury_risk_dict)

            injury_risk_dict = self.process_todays_symptoms(d, injury_risk_dict)
            # now process todays sessions
            daily_sessions = [n for n in self.training_sessions if n.event_date.date() == d]

            session_mapping_dict = {}

            for session in daily_sessions:
                session_functional_movement = SessionFunctionalMovement(session, injury_risk_dict)
                current_session = session_functional_movement.process(d, load_stats)

                # save all updates from processing back to the session - TODO: make sure this is the best place/time to save this info
                session_datastore = SessionDatastore()
                session_datastore.update(current_session, self.user_id, format_date(d))

                session_mapping_dict[current_session] = session_functional_movement.functional_movement_mappings

            daily_injury_risk_dict = self.merge_daily_sessions(d, session_mapping_dict, injury_risk_dict)

            #for b in session_functional_movement.body_parts:
            for body_part_side, body_part_injury_risk in daily_injury_risk_dict.items():

                if body_part_side not in injury_risk_dict:
                    injury_risk_dict[body_part_side] = BodyPartInjuryRisk()

                if body_part_side not in self.eccentric_volume_dict:
                    self.eccentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
                if d not in self.eccentric_volume_dict[body_part_side]:
                    self.eccentric_volume_dict[body_part_side][d] = 0
                self.eccentric_volume_dict[body_part_side][d] += body_part_injury_risk.eccentric_volume_today

                if body_part_side not in self.prime_mover_eccentric_volume_dict:
                    self.prime_mover_eccentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
                if d not in self.prime_mover_eccentric_volume_dict[body_part_side]:
                    self.prime_mover_eccentric_volume_dict[body_part_side][d] = 0
                self.prime_mover_eccentric_volume_dict[body_part_side][d] += body_part_injury_risk.prime_mover_eccentric_volume_today

                if body_part_side not in self.synergist_eccentric_volume_dict:
                    self.synergist_eccentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
                if d not in self.synergist_eccentric_volume_dict[body_part_side]:
                    self.synergist_eccentric_volume_dict[body_part_side][d] = 0
                self.synergist_eccentric_volume_dict[body_part_side][d] += body_part_injury_risk.synergist_eccentric_volume_today

                if body_part_side not in self.concentric_volume_dict:
                    self.concentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
                if d not in self.concentric_volume_dict[body_part_side]:
                    self.concentric_volume_dict[body_part_side][d] = 0
                self.concentric_volume_dict[body_part_side][d] += body_part_injury_risk.concentric_volume_today

                if body_part_side not in self.prime_mover_concentric_volume_dict:
                    self.prime_mover_concentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
                if d not in self.prime_mover_concentric_volume_dict[body_part_side]:
                    self.prime_mover_concentric_volume_dict[body_part_side][d] = 0
                self.prime_mover_concentric_volume_dict[body_part_side][d] += body_part_injury_risk.prime_mover_concentric_volume_today

                if body_part_side not in self.synergist_concentric_volume_dict:
                    self.synergist_concentric_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
                if d not in self.synergist_concentric_volume_dict[body_part_side]:
                    self.synergist_concentric_volume_dict[body_part_side][d] = 0
                self.synergist_concentric_volume_dict[body_part_side][d] += body_part_injury_risk.synergist_concentric_volume_today

                if body_part_side not in self.total_volume_dict:
                    self.total_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
                if d not in self.total_volume_dict[body_part_side]:
                    self.total_volume_dict[body_part_side][d] = 0
                self.total_volume_dict[body_part_side][d] += body_part_injury_risk.concentric_volume_today + body_part_injury_risk.eccentric_volume_today

                if body_part_side not in self.prime_mover_total_volume_dict:
                    self.prime_mover_total_volume_dict[body_part_side] = {}  # now we have a dictionary of dictionaries
                if d not in self.prime_mover_total_volume_dict[body_part_side]:
                    self.prime_mover_total_volume_dict[body_part_side][d] = 0
                self.prime_mover_total_volume_dict[body_part_side][d] += body_part_injury_risk.prime_mover_concentric_volume_today + body_part_injury_risk.prime_mover_eccentric_volume_today

                eccentric_volume_dict = self.eccentric_volume_dict[body_part_side]
                concentric_volume_dict = self.concentric_volume_dict[body_part_side]
                prime_mover_eccentric_volume_dict = self.prime_mover_eccentric_volume_dict[body_part_side]
                prime_mover_concentric_volume_dict = self.prime_mover_concentric_volume_dict[body_part_side]
                synergist_eccentric_volume_dict = self.synergist_eccentric_volume_dict[body_part_side]
                synergist_concentric_volume_dict = self.synergist_concentric_volume_dict[body_part_side]

                # this is handled in the session merge
                # if b.is_compensating:
                #     injury_risk_dict[b.body_part_side].last_compensation_date = d
                #     injury_risk_dict[b.body_part_side].compensating_source = b.compensation_source

                last_week_eccentric_volume_dict = dict(
                    filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago, eccentric_volume_dict.items()))

                last_week_concentric_volume_dict = dict(
                    filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago, concentric_volume_dict.items()))

                current_week_eccentric_volume_dict = dict(
                    filter(lambda elem: d > elem[0] >= seven_days_ago, eccentric_volume_dict.items()))

                current_week_concentric_volume_dict = dict(
                    filter(lambda elem: d > elem[0] >= seven_days_ago, concentric_volume_dict.items()))

                today_eccentric_volume_dict = dict(
                    filter(lambda elem: elem[0] == d, eccentric_volume_dict.items())
                    )

                today_concentric_volume_dict = dict(
                    filter(lambda elem: elem[0] == d, concentric_volume_dict.items()))

                last_week_eccentric_volume = sum(last_week_eccentric_volume_dict.values())
                last_week_concentric_volume = sum(last_week_concentric_volume_dict.values())

                todays_eccentric_volume = sum(today_eccentric_volume_dict.values())
                todays_concentric_volume = sum(today_concentric_volume_dict.values())

                current_week_concentric_volume = sum(current_week_concentric_volume_dict.values())
                current_week_eccentric_volume = sum(current_week_eccentric_volume_dict.values())

                injury_risk_dict[body_part_side].eccentric_volume_this_week = current_week_eccentric_volume
                injury_risk_dict[body_part_side].eccentric_volume_last_week = last_week_eccentric_volume
                injury_risk_dict[body_part_side].eccentric_volume_today = todays_eccentric_volume

                injury_risk_dict[body_part_side].concentric_volume_this_week = current_week_concentric_volume
                injury_risk_dict[body_part_side].concentric_volume_last_week = last_week_concentric_volume
                injury_risk_dict[body_part_side].concentric_volume_today = todays_concentric_volume

                eccentric_volume_ramp = injury_risk_dict[body_part_side].eccentric_volume_ramp()
                total_volume_ramp = injury_risk_dict[body_part_side].total_volume_ramp()

                if eccentric_volume_ramp > 1.0 or total_volume_ramp > 1.0:
                    injury_risk_dict[body_part_side].last_excessive_strain_date = d
                    injury_risk_dict[body_part_side].last_inhibited_date = d

                if 1.0 < eccentric_volume_ramp <= 1.05:
                    injury_risk_dict[body_part_side].last_functional_overreaching_date = d
                elif 1.05 < eccentric_volume_ramp:
                    injury_risk_dict[body_part_side].last_non_functional_overreaching_date = d

                elif 1.0 < total_volume_ramp <= 1.1:
                    injury_risk_dict[body_part_side].last_functional_overreaching_date = d
                elif 1.1 < total_volume_ramp:
                    injury_risk_dict[body_part_side].last_non_functional_overreaching_date = d
        return injury_risk_dict

    def process_todays_sessions(self, base_date, injury_risk_dict, load_stats):

        daily_sessions = [n for n in self.training_sessions if n.event_date.date() == base_date]

        #reset
        for body_part_side, body_part_injury_risk in injury_risk_dict.items():

            injury_risk_dict[body_part_side].eccentric_volume_today = 0
            injury_risk_dict[body_part_side].concentric_volume_today = 0
            injury_risk_dict[body_part_side].last_compensation_date = None
            injury_risk_dict[body_part_side].compensating_source = None

        session_mapping_dict = {}

        for session in daily_sessions:
            session_functional_movement = SessionFunctionalMovement(session, injury_risk_dict)
            current_session = session_functional_movement.process(base_date, load_stats)

            # save all updates from processing back to the session - TODO: make sure this is the best place/time to save this info
            session_datastore = SessionDatastore()
            session_datastore.update(current_session, self.user_id, format_date(base_date))

            session_mapping_dict[current_session] = session_functional_movement.functional_movement_mappings

        injury_risk_dict = self.merge_daily_sessions(base_date, session_mapping_dict, injury_risk_dict)

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
            injury_risk_dict[body_part_side].prime_mover_concentric_volume_today = 0
            injury_risk_dict[body_part_side].prime_mover_eccentric_volume_today = 0
            injury_risk_dict[body_part_side].prime_mover_total_volume_today = 0
            injury_risk_dict[body_part_side].synergist_concentric_volume_today = 0
            injury_risk_dict[body_part_side].synergist_eccentric_volume_today = 0
            injury_risk_dict[body_part_side].synergist_total_volume_today = 0
            injury_risk_dict[body_part_side].eccentric_volume_today = 0
            injury_risk_dict[body_part_side].concentric_volume_today = 0
            injury_risk_dict[body_part_side].last_compensation_date = None
            injury_risk_dict[body_part_side].compensating_source = None

        for session, functional_movement_list in session_functional_movement_dict_list.items():
            for functional_movement in functional_movement_list:
                # note: BodyPartFunctionalMovement hashes on body part side
                for prime_mover in functional_movement.prime_movers:  # list of BodyPartFunctionalMovement objects
                    body_part_side = BodyPartSide(prime_mover.body_part_side.body_part_location, prime_mover.body_part_side.side)
                    injury_risk_dict[body_part_side].prime_mover_concentric_volume_today += prime_mover.concentric_volume
                    injury_risk_dict[body_part_side].prime_mover_eccentric_volume_today += prime_mover.eccentric_volume
                    injury_risk_dict[
                        body_part_side].prime_mover_total_volume_today += prime_mover.total_volume()
                    if prime_mover.is_compensating:
                        injury_risk_dict[body_part_side].last_compensation_date = base_date
                        injury_risk_dict[body_part_side].compensating_source = prime_mover.compensation_source

                for synergist in functional_movement.synergists:
                    body_part_side = BodyPartSide(synergist.body_part_side.body_part_location,
                                                  synergist.body_part_side.side)
                    injury_risk_dict[body_part_side].synergist_concentric_volume_today += synergist.concentric_volume
                    injury_risk_dict[body_part_side].synergist_eccentric_volume_today += synergist.eccentric_volume
                    injury_risk_dict[
                        body_part_side].synergist_total_volume_today += synergist.total_volume()
                    if synergist.is_compensating:
                        injury_risk_dict[body_part_side].last_compensation_date = base_date
                        #TODO - take merge compensation sources here
                        injury_risk_dict[body_part_side].compensating_source = synergist.compensation_source

        for body_part_side, body_part_injury_risk in injury_risk_dict.items():
            injury_risk_dict[body_part_side].concentric_volume_today += (injury_risk_dict[body_part_side].prime_mover_concentric_volume_today +
                                                                         injury_risk_dict[body_part_side].synergist_concentric_volume_today)
            injury_risk_dict[body_part_side].eccentric_volume_today += (injury_risk_dict[body_part_side].prime_mover_eccentric_volume_today +
                                                                         injury_risk_dict[body_part_side].synergist_eccentric_volume_today)

            eccentric_volume_ramp = injury_risk_dict[body_part_side].eccentric_volume_ramp()
            total_volume_ramp = injury_risk_dict[body_part_side].total_volume_ramp()

            if eccentric_volume_ramp > 1.0 or total_volume_ramp > 1.0:
                injury_risk_dict[body_part_side].last_excessive_strain_date = base_date
                injury_risk_dict[body_part_side].last_inhibited_date = base_date

            if 1.0 < eccentric_volume_ramp <= 1.05:
                injury_risk_dict[body_part_side].last_functional_overreaching_date = base_date
            elif 1.05 < eccentric_volume_ramp:
                injury_risk_dict[body_part_side].last_non_functional_overreaching_date = base_date

            elif 1.0 < total_volume_ramp <= 1.1:
                injury_risk_dict[body_part_side].last_functional_overreaching_date = base_date
            elif 1.1 < total_volume_ramp:
                injury_risk_dict[body_part_side].last_non_functional_overreaching_date = base_date


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

            # any sharp symptoms get marked inflammation

            if target_symptom.sharp is not None and target_symptom.sharp > 0:

                if target_body_part_side in injury_risk_dict:
                    sharp_count = injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days
                    if injury_risk_dict[target_body_part_side].last_sharp_date is None or injury_risk_dict[target_body_part_side].last_sharp_date < base_date:
                        injury_risk_dict[target_body_part_side].last_sharp_date = base_date
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
                        injury_risk_dict[target_body_part_side].last_sharp_level = target_symptom.sharp
                        injury_risk_dict[target_body_part_side].last_inflammation_date = base_date
                        sharp_count = injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days
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

                # moderate severity or 2 reports in last 10 days
                # TODO: is moderate to high ache severity > 3?
                if target_symptom.ache > 3 or ache_count >= 2:
                    injury_risk_dict[target_body_part_side].last_inflammation_date = base_date

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
                if is_ligament:
                    related_muscles = self.functional_anatomy_processor.get_related_muscles_for_ligament(
                        target_body_part_side.body_part_location.value)
                else:
                    related_muscles = self.functional_anatomy_processor.get_related_muscles_for_joint(
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
                related_muscles = self.functional_anatomy_processor.get_related_muscles_for_joint(
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
                related_muscles = self.functional_anatomy_processor.get_related_muscles_for_joint(
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
