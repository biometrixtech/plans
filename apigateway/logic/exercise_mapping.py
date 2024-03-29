from models.modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining, ColdWaterImmersion, CoolDown, Heat, WarmUp, Ice, HeatSession, IceSession
from models.soreness import Alert
from models.soreness_base import HistoricSorenessStatus, BodyPartLocation, BodyPartSide
from models.goal import AthleteGoalType, AthleteGoal
from models.trigger import TriggerType
from logic.trigger_processing import TriggerFactory


class ExerciseAssignmentCalculator(object):

    def __init__(self, trigger_factory, exercise_library_datastore, completed_exercise_datastore, training_sessions,
                 soreness_list, event_date_time, historic_soreness=[]):
        #self.athlete_id = athlete_stats.athlete_id
        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        self.training_sessions = training_sessions
        self.soreness_list = soreness_list
        self.event_date_time = event_date_time

        self.high_relative_load_session = trigger_factory.high_relative_load_session
        self.high_relative_load_session_sport_names = trigger_factory.high_relative_load_session_sport_names
        self.high_relative_intensity_session = False
        self.eligible_for_high_load_trigger = trigger_factory.eligible_for_high_load_trigger

        #self.muscular_strain_increasing = athlete_stats.muscular_strain_increasing
        self.muscular_strain_high = trigger_factory.muscular_strain_high
        self.doms = list(d for d in historic_soreness if d.historic_soreness_status == HistoricSorenessStatus.doms)

        #if self.eligible_for_high_load_trigger:
        #    self.set_high_relative_load_session(athlete_stats)
        #    self.high_relative_intensity_session = self.process_training_sessions_intensity()
        #self.set_muscular_strain_high(athlete_stats)
        self.trigger_list = trigger_factory.triggers

    def set_muscular_strain_high(self, athlete_stats):

        if len(athlete_stats.muscular_strain) > 0:
            athlete_stats.muscular_strain.sort(key=lambda x: x.date, reverse=True)
            if athlete_stats.muscular_strain[0].value < 50.0:
                self.muscular_strain_high = True

    def set_high_relative_load_session(self, athlete_stats):

        todays_sessions = list(h for h in athlete_stats.high_relative_load_sessions if h.date.date() == self.event_date_time.date())

        for t in todays_sessions:
            self.high_relative_load_session = True
            self.high_relative_load_session_sport_names.add(t.sport_name)

    def get_progression_list(self, exercise):

        dict = {}
        # dict["9"] = ["121"]

        dict["10"] = ["12", "11", "13", "120"]

        dict["29"] = ["63", "64"]

        dict["6"] = ["117"]
        dict["46"] = ["117"]

        # 28 and 49 are in the same bucket, and 119 and 122 are in the same bucket.  This should be ok
        dict["28"] = ["122"]
        dict["49"] = ["119"]

        dict["67"] = ["78", "68", "31"]
        dict["81"] = ["82", "83", "110"]

        dict["85"] = ["86", "87", "88"]
        dict["89"] = ["90", "91", "92"]
        dict["103"] = ["104"]
        dict["106"] = ["105", "113"]
        dict["108"] = ["124"]
        dict["115"] = ["114", "65", "66", "107"]
        dict["135"] = ["136", "138"]

        if exercise in dict:
            return dict[exercise]
        else:
            return []

    def get_exercise_dictionary(self, exercise_list):

        exercise_dict = {}

        for e in exercise_list:
            exercise_dict[e] = self.get_progression_list(e)

        return exercise_dict

    def get_heat(self):

        bring_the_heat = []
        minutes = []
        alerts = []

        for t in self.trigger_list:

            goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
            heat = None

            # if (1.5 <= s.severity <= 5 and s.first_reported_date_time is not None and not s.is_dormant_cleared()
            #     and s.historic_soreness_status is not HistoricSorenessStatus.doms):
            #     days_diff = (self.event_date_time - s.first_reported_date_time).days
            #
            #     if not s.pain and days_diff >= 30:
            if t.trigger_type in [TriggerType.hist_sore_greater_30,
                                  TriggerType.pers_pers2_pain_less_30_no_pain_today,
                                  TriggerType.pers_pers2_pain_greater_30_no_pain_today] and 1.5 <= t.severity <= 5:
                if t.trigger_type == TriggerType.hist_sore_greater_30: # 19
                    if 1.5 <= t.severity < 3.5:
                        minutes.append(10)
                    else:
                        minutes.append(15)
                    #heat = Heat(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    #goal.trigger = "Pers, Pers-2 Soreness > 30d"
                    #goal.trigger_type = TriggerType.hist_sore_greater_30  # 19

                # elif ((s.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain or s.is_persistent_pain())
                #       and not s.daily):
                #     if days_diff < 30:
                elif t.trigger_type == TriggerType.pers_pers2_pain_less_30_no_pain_today: # 21
                    #goal.trigger = "Acute, Pers, Pers-2 Pain <= 30d"
                    #goal.trigger_type = TriggerType.pers_pers2_pain_less_30_no_pain_today  # 21
                    minutes.append(10)
                else:
                    #goal.trigger = "Acute, Pers, Pers-2 Pain > 30d"
                    #goal.trigger_type = TriggerType.pers_pers2_pain_greater_30_no_pain_today  # 22
                    minutes.append(15)
                heat = Heat(body_part_location=t.body_part.body_part_location, side=t.body_part.side)

            if heat is not None:
                heat.goals.add(goal)
                bring_the_heat.append(heat)
                # alert = Alert(goal)
                # alert.body_part = t.body_part
                # alerts.append(alert)

        if len(bring_the_heat) > 0:
            heat_session = HeatSession(minutes=max(minutes))
            heat_session.body_parts = bring_the_heat
            heat_session.alerts = alerts

            return heat_session
        else:
            return None

    def process_training_sessions_intensity(self):

        high_relative_intensity_session = False

        for t in self.training_sessions:
            if t.high_intensity():
                high_relative_intensity_session = True
                self.high_relative_load_session_sport_names.add(t.sport_name)

        return high_relative_intensity_session

    def get_pre_active_rest(self, force_data=False):

        if (len(self.trigger_list) > 0 or len(self.soreness_list) > 0 or self.muscular_strain_high
                or self.high_relative_load_session or self.high_relative_intensity_session or force_data):
            active_rest = ActiveRestBeforeTraining(self.event_date_time, force_data)
            active_rest.fill_exercises(self.trigger_list, self.exercise_library, self.high_relative_load_session,
                                       self.high_relative_intensity_session,
                                       self.muscular_strain_high,
                                       self.high_relative_load_session_sport_names)
            active_rest.set_plan_dosage(self.soreness_list, self.muscular_strain_high)
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            active_rest.set_winners()
            active_rest.scale_all_active_time()
            active_rest.reconcile_default_plan_with_active_time()
            if active_rest.get_total_exercises() > 0:
                return [active_rest]
        return []

    def get_post_active_rest(self, force_data=False):

        if (len(self.trigger_list) > 0 or len(self.soreness_list) > 0 or self.muscular_strain_high
                or self.high_relative_load_session or self.high_relative_intensity_session or force_data):
            active_rest = ActiveRestAfterTraining(self.event_date_time, force_data)
            active_rest.fill_exercises(self.trigger_list, self.exercise_library,self.high_relative_load_session,
                                       self.high_relative_intensity_session,
                                       self.muscular_strain_high,
                                       self.high_relative_load_session_sport_names)
            active_rest.set_plan_dosage(self.soreness_list, self.muscular_strain_high)
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            active_rest.set_winners()
            active_rest.scale_all_active_time()
            active_rest.reconcile_default_plan_with_active_time()
            if active_rest.get_total_exercises() > 0:
                return [active_rest]
        return []

    def get_warm_up(self):

        # warm_up = None

        if (self.muscular_strain_high or self.high_relative_load_session
                or len(self.soreness_list) > 0 or len(self.trigger_list) > 0):
            warm_up = WarmUp(self.event_date_time)
            warm_up.fill_exercises(self.trigger_list, self.exercise_library, self.high_relative_load_session,
                                   self.high_relative_intensity_session, self.muscular_strain_high,
                                   self.high_relative_load_session_sport_names)
            warm_up.set_exercise_dosage_ranking()

            if warm_up.get_total_exercises() > 0:
                return [warm_up]
        return []

    def get_cool_down(self):

        cool_down = None

        if self.high_relative_load_session or self.high_relative_intensity_session:

            #for sport_name in self.high_relative_load_session_sport_names:
            cool_down = CoolDown(self.high_relative_load_session, self.high_relative_intensity_session,
                                 self.muscular_strain_high, self.event_date_time)
            cool_down.fill_exercises(self.trigger_list, self.exercise_library, self.high_relative_load_session,
                                     self.high_relative_intensity_session, self.muscular_strain_high,
                                     self.high_relative_load_session_sport_names)
            cool_down.set_plan_dosage(self.soreness_list, self.muscular_strain_high)
            cool_down.set_exercise_dosage_ranking()
            cool_down.aggregate_dosages()
            cool_down.set_winners()
            cool_down.scale_all_active_time()
            cool_down.default_plan = "Complete"

            if cool_down is not None and cool_down.get_total_exercises() > 0:
                return [cool_down]
        return []

    def get_ice(self):

        ice_list = []
        minutes = []
        alerts = []
        ankle_knee_elbow = [BodyPartLocation.ankle, BodyPartLocation.knee, BodyPartLocation.elbow]

        for t in self.trigger_list:
            ice = None
            if t.trigger_type in [TriggerType.no_hist_pain_pain_today_severity_1_2,
                                  TriggerType.no_hist_pain_pain_today_high_severity_3_5,
                                  TriggerType.hist_pain_pain_today_severity_1_2,
                                  TriggerType.hist_pain_pain_today_severity_3_5]:
            #if s.daily and s.pain:
                goal = AthleteGoal("Pain", 1, AthleteGoalType.pain)
                #goal.trigger = "Pain Reported Today"
                # if s.severity < 3:
                #     if (not s.is_acute_pain() and not s.is_persistent_pain() and
                #             s.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
                #         goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
                #     else:
                #         goal.trigger_type = TriggerType.hist_pain_pain_today_severity_1_2  # 23
                # else:
                #     if (not s.is_acute_pain() and not s.is_persistent_pain() and
                #             s.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
                #         goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
                #     else:
                #         goal.trigger_type = TriggerType.hist_pain_pain_today_severity_3_5  # 24

                if t.severity < 3.5:
                    ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    ice.repeat_every_3hrs_for_24hrs = False

                    if t.body_part.body_part_location in ankle_knee_elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)
                elif 3.5 <= t.severity < 4.5 and not self.is_lower_body_part(t.body_part.body_part_location):
                    ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    ice.repeat_every_3hrs_for_24hrs = True
                    if t.body_part.body_part_location == BodyPartLocation.elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)
                elif 4.5 <= t.severity <= 5.0 and not self.is_lower_body_part(t.body_part.body_part_location):
                    ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    ice.repeat_every_3hrs_for_24hrs = True
                    if t.body_part.body_part_location == BodyPartLocation.elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)
                # if ice is not None:
                #     ice.goals.add(goal)
                #     ice_list.append(ice)

            # elif (s.daily and not s.pain and s.historic_soreness_status is not None and s.historic_soreness_status
            #         is not s.is_dormant_cleared() and
            #       (s.is_persistent_soreness() or s.historic_soreness_status ==
            #         HistoricSorenessStatus.persistent_2_soreness) and s.first_reported_date_time is not None):
            #     days_diff = (self.event_date_time - s.first_reported_date_time).days
            #     if days_diff >= 30 and s.severity >= 1.5:
            elif t.trigger_type == TriggerType.hist_sore_greater_30_sore_today and t.severity >= 1.5: # 13
                goal = AthleteGoal("Soreness", 1, AthleteGoalType.sore)
                #goal.trigger = "Soreness Reported Today + Pers, Pers-2 Soreness > 30d"
                #goal.trigger_type = TriggerType.hist_sore_greater_30_sore_today # 13

                if 1.5 <= t.severity < 3.5:
                    ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    ice.repeat_every_3hrs_for_24hrs = False
                    minutes.append(15)
                elif not self.is_lower_body_part(t.body_part.body_part_location) and 3.5 <= t.severity <= 5.0:
                    ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    ice.repeat_every_3hrs_for_24hrs = True
                    if t.body_part.body_part_location == BodyPartLocation.elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)

            # elif (s.historic_soreness_status is not None and not s.is_dormant_cleared()
            #       and s.historic_soreness_status is not HistoricSorenessStatus.doms
            #       and s.severity >= 1.5 and not s.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):
            #
            #     days_diff = (self.event_date_time - s.first_reported_date_time).days
            #     if days_diff >= 30 and s.severity >= 1.5:
            elif t.trigger_type == TriggerType.hist_sore_greater_30_high_volume_intensity and t.severity >= 1.5:  # 1
                goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
                #goal.trigger = "No Soreness Reported Today + Historic Soreness > 30d + logged hig vol/intensity"
                #goal.trigger_type = TriggerType.hist_sore_greater_30_high_volume_intensity  # 1
                ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                ice.repeat_every_3hrs_for_24hrs = False
                if t.body_part.body_part_location in ankle_knee_elbow:
                    minutes.append(10)
                else:
                    minutes.append(15)

            # elif (s.historic_soreness_status is not None and not s.is_dormant_cleared()
            #       and s.historic_soreness_status is not HistoricSorenessStatus.doms
            #       and s.severity >= 1.5 and s.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):
            elif t.trigger_type == TriggerType.hist_pain_high_volume_intensity and t.severity >= 1.5:  # 2
                goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
                #goal.trigger = "No Pain Reported Today + Acute, Pers, Pers-2 Pain"
                #goal.trigger_type = TriggerType.hist_pain_high_volume_intensity  # 2
                ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                ice.repeat_every_3hrs_for_24hrs = False

                if t.body_part.body_part_location in ankle_knee_elbow:
                    minutes.append(10)
                else:
                    minutes.append(15)

            # elif (not s.daily and s.historic_soreness_status is not None and not s.is_dormant_cleared()
            #       and s.historic_soreness_status is not HistoricSorenessStatus.doms
            #       and s.severity >= 1.5 and not s.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):
            #
            #     days_diff = (self.event_date_time - s.first_reported_date_time).days
            #     if days_diff >= 30 and s.severity >= 1.5:
            elif t.trigger_type == TriggerType.hist_sore_greater_30_no_sore_today_high_volume_intensity and t.severity >= 1.5:  # 3
                    goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
                    #goal.trigger = "No Soreness Reported Today + Historic Soreness > 30d + logged hig vol/intensity"
                    #goal.trigger_type = TriggerType.hist_sore_greater_30_no_sore_today_high_volume_intensity  # 3
                    ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    ice.repeat_every_3hrs_for_24hrs = False
                    if t.body_part.body_part_location in ankle_knee_elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)

                    # if ice is not None:
                    #     ice.goals.add(goal)
                    #     ice_list.append(ice)

            # elif (not s.daily and s.historic_soreness_status is not None and not s.is_dormant_cleared()
            #       and s.historic_soreness_status is not HistoricSorenessStatus.doms
            #       and s.severity >= 1.5 and s.pain and s.is_acute_pain() and
            #       (self.high_relative_load_session or self.high_relative_intensity_session)):
            # elif t.trigger_type == TriggerType.acute_pain_no_pain_today_high_volume_intensity and t.severity >= 1.5:  # 4
            #     goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
            #     #goal.trigger_type = TriggerType.acute_pain_no_pain_today_high_volume_intensity  # 4
            #     ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
            #     ice.repeat_every_3hrs_for_24hrs = False
            #
            #     if t.body_part.body_part_location in ankle_knee_elbow:
            #         minutes.append(10)
            #     else:
            #         minutes.append(15)
            # elif (not s.daily and s.historic_soreness_status is not None and not s.is_dormant_cleared()
            #       and s.historic_soreness_status is not HistoricSorenessStatus.doms
            #       and s.severity >= 1.5 and s.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):
            elif t.trigger_type in [TriggerType.pers_pers2_pain_no_pain_sore_today_high_volume_intensity,
                                    TriggerType.acute_pain_no_pain_today_high_volume_intensity] and t.severity >= 1.5:  # 5
                goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
                #if s.is_persistent_pain() or s.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:
                if t.trigger_type == TriggerType.pers_pers2_pain_no_pain_sore_today_high_volume_intensity:  # 5
                    #goal.trigger = "No Pain Reported Today + Acute, Pers, Pers-2 Pain"
                    #goal.trigger_type = TriggerType.pers_pers2_pain_no_pain_sore_today_high_volume_intensity  # 5
                    ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    ice.repeat_every_3hrs_for_24hrs = False

                    if t.body_part.body_part_location in ankle_knee_elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)

                #elif s.is_acute_pain():
                elif t.trigger_type == TriggerType.acute_pain_no_pain_today_high_volume_intensity:  # 4
                    #goal.trigger_type = TriggerType.acute_pain_no_pain_today_high_volume_intensity
                    ice = Ice(body_part_location=t.body_part.body_part_location, side=t.body_part.side)
                    ice.repeat_every_3hrs_for_24hrs = False

                    if t.body_part.body_part_location in ankle_knee_elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)

            if ice is not None:
                ice.goals.add(goal)
                ice_list.append(ice)
                # if goal.trigger_type not in [TriggerType(1), TriggerType(2), TriggerType(4), TriggerType(5)]:  # 4 and 5 in plans but not in insights/trends, 1 and 2 are added to insights/trends elsewhere
                #     alert = Alert(goal)
                #     alert.body_part = BodyPartSide(s.body_part.location, s.side)
                #     alerts.append(alert)

        for d in self.doms:
            days = (self.event_date_time.date() - d.first_reported_date_time.date()).days
            if days <= 2 and 2 <= d.max_severity <= 5: #or  # moderate or severe DOMS (not minor doms)
                    #(days <= 2 and 2 <= d.max_severity <= 3) or  # moderate DOMS
                    #(days <= 2 and 3 < d.max_severity <= 5)):  # severe DOMS
                if not self.is_lower_body_part(d.body_part_location):
                    goal = AthleteGoal("Soreness", 1, AthleteGoalType.sore)
                    #goal.trigger = "Soreness Reported Today as DOMS"
                    #goal.trigger_type = TriggerType.sore_today_doms  # 11

                    if d.body_part_location == BodyPartLocation.elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)

                    ice = Ice(body_part_location=d.body_part_location, side=d.side)
                    ice.repeat_every_3hrs_for_24hrs = True
                    ice.goals.add(goal)
                    # alert = Alert(goal)
                    # alert.body_part = BodyPartSide(d.body_part_location, d.side)
                    # alerts.append(alert)
                    if ice not in ice_list:
                        ice_list.append(ice)

        if len(ice_list) > 0:
            ice_session = IceSession(minutes=min(minutes))
            ice_session.body_parts = ice_list
            ice_session.alerts = alerts

            return ice_session
        else:
            return None

    def get_cold_water_immersion(self):

        cold_water_immersion = None

        alerts = []
        for t in self.trigger_list:
            # if self.is_lower_body_part(s.body_part.location) and s.daily and s.severity >= 3.5:
            #     if s.pain:
            if t.trigger_type in [TriggerType.no_hist_pain_pain_today_severity_1_2,
                                  TriggerType.no_hist_pain_pain_today_high_severity_3_5]: #14, 15
                if self.is_lower_body_part(t.body_part.body_part_location) and t.severity >= 3.5:
                    goal = AthleteGoal("Pain", 1, AthleteGoalType.pain)
                    #goal.trigger = "Pain Reported Today"
                    # if s.severity < 3:
                    #     goal.trigger_type = TriggerType.no_hist_pain_pain_today_severity_1_2  # 14
                    # else:
                    #     goal.trigger_type = TriggerType.no_hist_pain_pain_today_high_severity_3_5  # 15
                    if cold_water_immersion is None:
                        cold_water_immersion = ColdWaterImmersion()
                    cold_water_immersion.goals.add(goal)
                    # alert = Alert(goal)
                    # alert.body_part = t.body_part
                    # alerts.append(alert)

            # elif (not s.pain and s.historic_soreness_status is not None
            #         and (s.is_persistent_soreness() or
            #       s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness)
            #       and s.first_reported_date_time is not None):
            #     days_diff = (self.event_date_time - s.first_reported_date_time).days
            #     if days_diff >= 30 and s.severity >= 3.5:
            elif t.trigger_type == TriggerType.hist_sore_greater_30_sore_today: # 13
                if self.is_lower_body_part(t.body_part.body_part_location) and t.severity >= 3.5:
                    goal = AthleteGoal("Soreness", 1, AthleteGoalType.sore)
                    #goal.trigger = "Soreness Reported Today + Pers, Pers-2 Soreness > 30d"
                    #goal.trigger_type = TriggerType.hist_sore_greater_30_sore_today  # 13
                    if cold_water_immersion is None:
                        cold_water_immersion = ColdWaterImmersion()
                    cold_water_immersion.goals.add(goal)
                    # alert = Alert(goal)
                    # alert.body_part = t.body_part
                    # alerts.append(alert)

        for d in self.doms:
            days = (self.event_date_time.date() - d.first_reported_date_time.date()).days
            if days <= 2 and 2 <= d.max_severity <= 5:  # or  # moderate or severe DOMS (not minor doms)
            # if ((days == 2 and d.max_severity  == 1) or  # minor DOMS
            #         (days <= 2 and 2 <= d.max_severity <= 3) or  # moderate DOMS
            #         (days <= 2 and 3 < d.max_severity <= 5)):  # severe DOMS
                if self.is_lower_body_part(d.body_part_location):
                    goal = AthleteGoal("Soreness", 1, AthleteGoalType.sore)
                    #goal.trigger = "Soreness Reported Today as DOMS"
                    goal.trigger_type = TriggerType.sore_today_doms  # 11
                    if cold_water_immersion is None:
                        cold_water_immersion = ColdWaterImmersion()
                    cold_water_immersion.goals.add(goal)
                    # alert = Alert(goal)
                    # alert.body_part = BodyPartSide(d.body_part_location, d.side)
                    # alerts.append(alert)
        if cold_water_immersion is not None:
            cold_water_immersion.alerts = alerts

        return cold_water_immersion

    def adjust_ice_session(self, ice_session, cold_water_immersion_session):

        if ice_session is not None and cold_water_immersion_session is not None:
            ice_session.body_parts = list(b for b in ice_session.body_parts if not self.is_lower_body_part(b.body_part_location))

            if len(ice_session.body_parts) == 0:
                cold_water_immersion_session.alerts.extend(ice_session.alerts)
                ice_session = None

        return ice_session

    @staticmethod
    def is_lower_body_part(body_part_location):

        if (
                body_part_location == BodyPartLocation.hip_flexor or
                body_part_location == BodyPartLocation.hip or
                body_part_location == BodyPartLocation.knee or
                body_part_location == BodyPartLocation.ankle or
                body_part_location == BodyPartLocation.foot or
                body_part_location == BodyPartLocation.achilles or
                body_part_location == BodyPartLocation.groin or
                body_part_location == BodyPartLocation.quads or
                body_part_location == BodyPartLocation.shin or
                body_part_location == BodyPartLocation.it_band or
                body_part_location == BodyPartLocation.it_band_lateral_knee or
                body_part_location == BodyPartLocation.glutes or
                body_part_location == BodyPartLocation.hamstrings or
                body_part_location == BodyPartLocation.calves
        ):
            return True
        else:
            return False

    def generate_alerts(self):
        alerts = []
        # if self.eligible_for_high_load_trigger:
        #     if self.high_relative_load_session or self.high_relative_intensity_session:
        #         for s in self.soreness_list:
        #             goal = None
        #             if s.pain and (s.is_acute_pain() or s.is_persistent_pain() or s.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain):
        #                 goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
        #                 goal.trigger_type = TriggerType.hist_pain_high_volume_intensity  # 2
        #             elif (not s.pain and s.historic_soreness_status is not None
        #                   and (s.is_persistent_soreness()
        #                        or s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness)
        #                   and s.first_reported_date_time is not None):
        #                     days_diff = (self.event_date_time - s.first_reported_date_time).days
        #                     if days_diff >= 30:
        #                         goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
        #                         goal.trigger_type = TriggerType.hist_sore_greater_30_high_volume_intensity  # 1
        #             if goal is not None:
        #                 for sport_name in self.high_relative_load_session_sport_names:
        #                     alert = Alert(goal)
        #                     alert.body_part = BodyPartSide(s.body_part.location, s.side)
        #                     alert.sport_name = sport_name
        #                     alerts.append(alert)
        # else:
        #     goal = AthleteGoal(None, 1, AthleteGoalType.sport)
        #     goal.trigger_type = TriggerType.not_enough_history_for_high_volume_intensity  # 25
        #     alert = Alert(goal)
        #     alerts.append(alert)

        return alerts
