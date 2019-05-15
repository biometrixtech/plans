import models.soreness
# from logic.exercise_generator import ExerciseAssignments
# import logic.soreness_processing as soreness_and_injury
from models.exercise import ExerciseBuckets, Phase
from models.modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining, ColdWaterImmersion, CoolDown, Heat, WarmUp, Ice, HeatSession, IceSession
from models.soreness import AthleteGoal, AthleteGoalType, AssignedExercise, BodyPartLocation, HistoricSorenessStatus, Soreness, BodyPart, TriggerType, Alert, BodyPartSide
from models.sport import SportName
# from logic.goal_focus_text_generator import RecoveryTextGenerator
# from datetime import  timedelta
# from utils import format_datetime, parse_date


class ExerciseAssignmentCalculator(object):

    def __init__(self, athlete_stats, exercise_library_datastore, completed_exercise_datastore, training_sessions,
                 soreness_list, event_date_time):
        self.athlete_id = athlete_stats.athlete_id
        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        # self.exercises_for_body_parts = self.get_exercises_for_body_parts()
        #self.is_active_prep = is_active_prep
        #  self.injury_history_present = injury_history_present
        self.training_sessions = training_sessions
        self.soreness_list = soreness_list
        self.event_date_time = event_date_time
        self.high_relative_intensity_session = self.process_training_sessions_intensity()
        self.high_relative_load_session = False
        self.high_relative_load_session_sport_names = set()

        self.muscular_strain_increasing = athlete_stats.muscular_strain_increasing
        self.doms = athlete_stats.delayed_onset_muscle_soreness

        self.set_high_relative_load_session(athlete_stats, training_sessions)

    def set_high_relative_load_session(self, athlete_stats, training_sessions):

        for t in training_sessions:
            if t.sport_name in athlete_stats.duration_load_ramp:
                if (athlete_stats.duration_load_ramp[t.sport_name].observed_value is None or
                        athlete_stats.duration_load_ramp[t.sport_name].observed_value > 1.1):
                    self.high_relative_load_session = True
                    self.high_relative_load_session_sport_names.add(t.sport_name)
            # else:
            #     self.high_relative_load_session = True
            #     self.high_relative_load_session_sport_names.add(t.sport_name)

    def get_progression_list(self, exercise):

        dict = {}
        #dict["9"] = ["121"]

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

        pain_reported_today = False

        pain_today = list(p for p in self.soreness_list if p.daily and p.pain)
        if len(pain_today) > 0:
            pain_reported_today = True

        for s in self.soreness_list:

            goal = AthleteGoal("Preemptive, Prepare for Training", 1, AthleteGoalType.preempt_corrective)
            heat = None

            if 1.5 <= s.severity <= 5 and s.first_reported_date_time is not None and not s.is_dormant_cleared():
                days_diff = (self.event_date_time - s.first_reported_date_time).days

                if not s.pain and days_diff >= 30:
                    if 1.5 <= s.severity < 3.5:
                        minutes.append(10)
                    else:
                        minutes.append(15)
                    heat = Heat(body_part_location=s.body_part.location, side=s.side)
                    #goal.trigger = "Pers, Pers-2 Soreness > 30d"
                    goal.trigger_type = TriggerType.hist_sore_greater_30

                elif ((s.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain or s.is_persistent_pain())
                      and not pain_reported_today):
                    if days_diff <= 30:
                        #goal.trigger = "Acute, Pers, Pers-2 Pain <= 30d"
                        goal.trigger_type = TriggerType.pers_pers2_pain_less_30_no_pain_today
                        minutes.append(10)
                    else:
                        #goal.trigger = "Acute, Pers, Pers-2 Pain > 30d"
                        goal.trigger_type = TriggerType.pers_pers2_pain_greater_30_no_pain_today
                        minutes.append(15)
                    heat = Heat(body_part_location=s.body_part.location, side=s.side)

            if heat is not None:
                heat.goals.add(goal)
                bring_the_heat.append(heat)
                alert = Alert(goal)
                alert.body_part = BodyPartSide(s.body_part.location, s.side)
                alerts.append(alert)

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

        return high_relative_intensity_session

    def get_pre_active_rest(self, force_data=False):

        if (len(self.soreness_list) > 0 or self.muscular_strain_increasing
                or self.high_relative_load_session or self.high_relative_intensity_session or force_data):
            active_rest = ActiveRestBeforeTraining(self.event_date_time, force_data)
            active_rest.fill_exercises(self.soreness_list, self.exercise_library, self.high_relative_load_session,
                                       self.high_relative_intensity_session,
                                       self.muscular_strain_increasing,
                                       self.high_relative_load_session_sport_names)
            active_rest.set_plan_dosage(self.soreness_list, self.muscular_strain_increasing)
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            return [active_rest]
        else:
            return []

    def get_post_active_rest(self, force_data=False):

        if (len(self.soreness_list) > 0 or self.muscular_strain_increasing
                or self.high_relative_load_session or self.high_relative_intensity_session):
            active_rest = ActiveRestAfterTraining(self.event_date_time, force_data)
            active_rest.fill_exercises(self.soreness_list, self.exercise_library,self.high_relative_load_session,
                                       self.high_relative_intensity_session,
                                       self.muscular_strain_increasing,
                                       self.high_relative_load_session_sport_names)
            active_rest.set_plan_dosage(self.soreness_list, self.muscular_strain_increasing)
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            return [active_rest]
        else:
            return []

    def get_warm_up(self):

        # warm_up = None

        if (self.muscular_strain_increasing or self.high_relative_load_session
                or len(self.soreness_list) > 0):
            warm_up = WarmUp(self.event_date_time)
            warm_up.fill_exercises(self.soreness_list, self.exercise_library, self.high_relative_load_session,
                                   self.high_relative_intensity_session, self.muscular_strain_increasing,
                                   self.high_relative_load_session_sport_names)
            warm_up.set_exercise_dosage_ranking()

            return [warm_up]
        else:
            return []

    def get_cool_down(self):

        cool_down = None

        if self.high_relative_load_session or self.high_relative_intensity_session:
            #for s in soreness_list:
            #    if s.first_reported_date_time is not None and not s.is_dormant_cleared():
            #        days_diff = (event_date_time - s.first_reported_date_time).days
            #        if (not s.pain and days_diff > 30) or s.pain:
            for sport_name in self.high_relative_load_session_sport_names:
                cool_down = CoolDown(self.high_relative_load_session, self.high_relative_intensity_session,
                                     self.muscular_strain_increasing, self.event_date_time)
                cool_down.fill_exercises(self.soreness_list, self.exercise_library, self.high_relative_load_session, self.high_relative_intensity_session, self.muscular_strain_increasing,
                                         [sport_name])
                cool_down.set_plan_dosage(self.soreness_list, self.muscular_strain_increasing)
                cool_down.set_exercise_dosage_ranking()
                cool_down.aggregate_dosages()
            #    break

            return [cool_down]
        else:
            return []

    def get_ice(self):

        ice_list = []
        minutes = []
        alerts = []
        low_parts = [BodyPartLocation.ankle, BodyPartLocation.knee, BodyPartLocation.elbow]

        for s in self.soreness_list:
            ice = None
            if s.daily and s.pain:
                goal = AthleteGoal("Care for Pain", 1, AthleteGoalType.pain)
                #goal.trigger = "Pain Reported Today"
                if s.severity < 3:
                    goal.trigger_type = TriggerType.pain_today
                else:
                    goal.trigger_type = TriggerType.pain_today_high

                if s.severity < 3.5:
                    ice = Ice(body_part_location=s.body_part.location, side=s.side)
                    ice.repeat_every_3hrs_for_24hrs = False

                    if s.body_part.location in low_parts:
                        minutes.append(10)
                    else:
                        minutes.append(15)
                elif 3.5 <= s.severity < 4.5 and not self.is_lower_body_part(s.body_part.location):
                    ice = Ice(body_part_location=s.body_part.location, side=s.side)
                    ice.repeat_every_3hrs_for_24hrs = True
                    if s.body_part.location == BodyPartLocation.elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)
                # if ice is not None:
                #     ice.goals.add(goal)
                #     ice_list.append(ice)

            elif (s.daily and not s.pain and s.historic_soreness_status is not None and s.historic_soreness_status
                    is not s.is_dormant_cleared() and
                  (s.is_persistent_soreness() or s.historic_soreness_status ==
                    HistoricSorenessStatus.persistent_2_soreness) and s.first_reported_date_time is not None):
                days_diff = (self.event_date_time - s.first_reported_date_time).days
                if days_diff > 30 and s.severity >= 1.5:
                    goal = AthleteGoal("Care for Soreness", 1, AthleteGoalType.sore)
                    #goal.trigger = "Soreness Reported Today + Pers, Pers-2 Soreness > 30d"
                    goal.trigger_type = TriggerType.hist_sore_greater_30_sore_today
                    ice = Ice(body_part_location=s.body_part.location, side=s.side)
                    if 1.5 <= s.severity < 3.5:
                        ice.repeat_every_3hrs_for_24hrs = False
                        minutes.append(15)
                    elif not self.is_lower_body_part(s.body_part.location) and 3.5 <= s.severity <= 5.0:
                        ice.repeat_every_3hrs_for_24hrs = True
                        if s.body_part.location == BodyPartLocation.elbow:
                            minutes.append(10)
                        else:
                            minutes.append(15)

                    # if ice is not None:
                    #     ice.goals.add(goal)
                    #     ice_list.append(ice)

            elif (not s.daily and s.historic_soreness_status is not None and not s.is_dormant_cleared()
                  and s.severity >= 1.5 and not s.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                days_diff = (self.event_date_time - s.first_reported_date_time).days
                if days_diff > 30 and s.severity >= 1.5:
                    goal = AthleteGoal("Preemptive, Prepare for Training", 1, AthleteGoalType.preempt_corrective)
                    #goal.trigger = "No Soreness Reported Today + Historic Soreness > 30d + logged hig vol/intensity"
                    goal.trigger_type = TriggerType.hist_sore_greater_30_no_sore_today_3_high_volume_intensity
                    ice = Ice(body_part_location=s.body_part.location, side=s.side)
                    ice.repeat_every_3hrs_for_24hrs = False
                    if s.body_part.location in low_parts:
                        minutes.append(10)
                    else:
                        minutes.append(15)

                    # if ice is not None:
                    #     ice.goals.add(goal)
                    #     ice_list.append(ice)

            elif (not s.daily and s.historic_soreness_status is not None and not s.is_dormant_cleared()
                  and s.severity >= 1.5 and s.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                goal = AthleteGoal("Preemptive, Prepare for Training", 1, AthleteGoalType.preempt_corrective)
                #goal.trigger = "No Pain Reported Today + Acute, Pers, Pers-2 Pain"
                goal.trigger_type = TriggerType.pers_pers2_pain_no_pain_sore_today_high_volume_intensity
                ice = Ice(body_part_location=s.body_part.location, side=s.side)
                ice.repeat_every_3hrs_for_24hrs = False

                if s.body_part.location in low_parts:
                    minutes.append(10)
                else:
                    minutes.append(15)

            if ice is not None:
                ice.goals.add(goal)
                ice_list.append(ice)
                alert = Alert(goal)
                alert.body_part = BodyPartSide(s.body_part.location, s.side)
                alerts.append(alert)

        for d in self.doms:
            days = (self.event_date_time - d.first_reported_date_time).days
            if ((days == 2 and d.max_severity == 1) or  # minor DOMS
                    (days <= 2 and 2 <= d.max_severity <= 3) or  # moderate DOMS
                    (days <= 2 and 3 < d.max_severity <= 5)):  # severe DOMS
                if d.body_part.location not in low_parts:
                    goal = AthleteGoal("Care for Soreness, Reactive", 1, AthleteGoalType.sore)
                    #goal.trigger = "Soreness Reported Today as DOMS"
                    goal.trigger_type = TriggerType.sore_today_doms

                    if d.body_part.location == BodyPartLocation.elbow:
                        minutes.append(10)
                    else:
                        minutes.append(15)

                    ice = Ice(body_part_location=d.body_part.location, side=d.side)
                    ice.repeat_every_3hrs_for_24hrs = True
                    ice.goals.add(goal)
                    alert = Alert(goal)
                    alert.body_part = BodyPartSide(d.body_part.location, d.side)
                    alerts.append(alert)
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

        low_parts = [BodyPartLocation.ankle, BodyPartLocation.knee, BodyPartLocation.elbow]

        for s in self.soreness_list:
            if self.is_lower_body_part(s.body_part.location) and s.daily and s.severity >= 3.5:
                if s.pain:

                    goal = AthleteGoal("Care for Pain", 1, AthleteGoalType.pain)
                    #goal.trigger = "Pain Reported Today"
                    if s.severity < 3:
                        goal.trigger_type = TriggerType.pain_today
                    else:
                        goal.trigger_type = TriggerType.pain_today_high
                    if cold_water_immersion is None:
                        cold_water_immersion = ColdWaterImmersion()
                    cold_water_immersion.goals.add(goal)

                elif not s.pain and s.historic_soreness_status is not None and s.historic_soreness_status is not s.is_dormant_cleared() and s.first_reported_date_time is not None:
                    days_diff = (self.event_date_time - s.first_reported_date_time).days
                    if days_diff > 30 and s.severity >= 3.5:
                        goal = AthleteGoal("Care for Soreness", 1, AthleteGoalType.sore)
                        #goal.trigger = "Soreness Reported Today + Pers, Pers-2 Soreness > 30d"
                        goal.trigger_type = TriggerType.hist_sore_greater_30_sore_today
                        if cold_water_immersion is None:
                            cold_water_immersion = ColdWaterImmersion()
                        cold_water_immersion.goals.add(goal)

        for d in self.doms:
            days = (self.event_date_time - d.first_reported_date_time).days
            if ((days == 2 and d.max_severity  == 1) or  # minor DOMS
                    (days <= 2 and 2 <= d.max_severity <= 3) or  # moderate DOMS
                    (days <= 2 and 3 < d.max_severity <= 5)):  # severe DOMS
                if d.body_part.location in low_parts:
                    goal = AthleteGoal("Care for Soreness, Reactive", 1, AthleteGoalType.sore)
                    #goal.trigger = "Soreness Reported Today as DOMS"
                    goal.trigger_type = TriggerType.sore_today_doms
                    if cold_water_immersion is None:
                        cold_water_immersion = ColdWaterImmersion()
                    cold_water_immersion.goals.add(goal)

        return cold_water_immersion

    def adjust_ice_session(self, ice_session, cold_water_immersion_session):

        if ice_session is not None and cold_water_immersion_session is not None:
            ice_session.body_parts = list(b for b in ice_session.body_parts if not self.is_lower_body_part(b.body_part_location))

            if len(ice_session.body_parts) == 0:
                ice_session = None

        return ice_session

    @staticmethod
    def is_lower_body_part(body_part_location):

        if (
                body_part_location == BodyPartLocation.hip_flexor or
                body_part_location == BodyPartLocation.knee or
                body_part_location == BodyPartLocation.ankle or
                body_part_location == BodyPartLocation.foot or
                body_part_location == BodyPartLocation.achilles or
                body_part_location == BodyPartLocation.groin or
                body_part_location == BodyPartLocation.quads or
                body_part_location == BodyPartLocation.shin or
                body_part_location == BodyPartLocation.outer_thigh or
                body_part_location == BodyPartLocation.glutes or
                body_part_location == BodyPartLocation.hamstrings or
                body_part_location == BodyPartLocation.calves
        ):
            return True
        else:
            return False
