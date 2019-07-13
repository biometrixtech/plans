from models.body_parts import BodyPartFactory
from models.soreness import AthleteGoal, AthleteGoalType, BodyPartSide, HistoricSorenessStatus
from models.trigger import Trigger, TriggerType


class TriggerFactory(object):
    def __init__(self, event_date_time, athlete_stats, soreness_list, training_sessions):
        self.event_date_time = event_date_time
        self.triggers = []
        self.high_relative_load_session = False
        self.high_relative_intensity_session = False
        self.high_relative_load_session_sport_names = set()
        self.muscular_strain_high = False

        self.soreness_list = soreness_list
        self.training_sessions = training_sessions
        self.eligible_for_high_load_trigger = athlete_stats.eligible_for_high_load_trigger if athlete_stats is not None else False

        if self.eligible_for_high_load_trigger:
            self.set_high_relative_load_session(athlete_stats)
            self.high_relative_intensity_session = self.process_training_sessions_intensity()

        self.set_muscular_strain_high(athlete_stats)

    def set_muscular_strain_high(self, athlete_stats):

        if athlete_stats is not None and len(athlete_stats.muscular_strain) > 0:
            athlete_stats.muscular_strain.sort(key=lambda x: x.date, reverse=True)
            if athlete_stats.muscular_strain[0].value < 50.0:
                self.muscular_strain_high = True

    def set_high_relative_load_session(self, athlete_stats):

        todays_sessions = list(
            h for h in athlete_stats.high_relative_load_sessions if h.date.date() == self.event_date_time.date())

        for t in todays_sessions:
            self.high_relative_load_session = True
            self.high_relative_load_session_sport_names.add(t.sport_name)

    def process_training_sessions_intensity(self):

        high_relative_intensity_session = False

        for t in self.training_sessions:
            if t.high_intensity():
                high_relative_intensity_session = True
                self.high_relative_load_session_sport_names.add(t.sport_name)

        return high_relative_intensity_session

    def load_triggers(self):

        body_part_factory = BodyPartFactory()

        self.triggers = []

        if self.high_relative_load_session or self.high_relative_intensity_session:

            for sport_name in self.high_relative_load_session_sport_names:
                trigger = Trigger(TriggerType.high_volume_intensity)  # 0
                trigger.sport_name = sport_name
                self.triggers.append(trigger)

        hist_soreness = list(s for s in self.soreness_list if not s.is_dormant_cleared() and not s.pain and
                             (s.is_persistent_soreness() or
                              s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
                             (self.event_date_time - s.first_reported_date_time).days < 30)

        if len(hist_soreness) > 0:

            for soreness in hist_soreness:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                trigger = Trigger(TriggerType.hist_sore_less_30)  # 7
                trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                trigger.antagonists = body_part.antagonists
                trigger.synergists = body_part.synergists
                trigger.severity = soreness.severity
                trigger.pain = False
                self.triggers.append(trigger)

        if self.muscular_strain_high:
            trigger = Trigger(TriggerType.overreaching_high_muscular_strain)  # 8
            self.triggers.append(trigger)

        for soreness in self.soreness_list:

            days_diff = None
            if soreness.first_reported_date_time is not None:
                days_diff = (self.event_date_time - soreness.first_reported_date_time).days
            body_part = body_part_factory.get_body_part(soreness.body_part)

            if self.eligible_for_high_load_trigger:
                if (soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and not soreness.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    if days_diff is not None and days_diff >= 30:
                        for sport_name in self.high_relative_load_session_sport_names:
                            trigger = Trigger(TriggerType.hist_sore_greater_30_high_volume_intensity)  # 1
                            trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                            trigger.severity = soreness.severity
                            trigger.sport_name = sport_name
                            trigger.pain = False
                            self.triggers.append(trigger)

                elif (soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and soreness.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    for sport_name in self.high_relative_load_session_sport_names:
                        trigger = Trigger(TriggerType.hist_pain_high_volume_intensity)  # 2
                        trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                        trigger.severity = soreness.severity
                        trigger.sport_name = sport_name
                        trigger.pain = True
                        trigger.historic_soreness_status = soreness.historic_soreness_status
                        self.triggers.append(trigger)

                elif (not soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and not soreness.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    if days_diff is not None and days_diff >= 30:
                        trigger = Trigger(TriggerType.hist_sore_greater_30_no_sore_today_high_volume_intensity)  # 3
                        trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                        trigger.severity = soreness.severity
                        trigger.pain = False
                        trigger.historic_soreness_status = soreness.historic_soreness_status
                        self.triggers.append(trigger)

                elif (not soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and soreness.pain and soreness.is_acute_pain() and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    trigger = Trigger(TriggerType.acute_pain_no_pain_today_high_volume_intensity)  # 4
                    trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                    trigger.severity = soreness.severity
                    trigger.pain = True
                    trigger.historic_soreness_status = soreness.historic_soreness_status
                    self.triggers.append(trigger)

                elif (not soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and soreness.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    if soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:
                        # goal.trigger = "No Pain Reported Today + Acute, Pers, Pers-2 Pain"
                        trigger = Trigger(TriggerType.pers_pers2_pain_no_pain_sore_today_high_volume_intensity)  # 5
                        trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                        trigger.severity = soreness.severity
                        trigger.pain = True
                        trigger.historic_soreness_status = soreness.historic_soreness_status
                        self.triggers.append(trigger)
                    elif soreness.is_acute_pain():
                        trigger = Trigger(TriggerType.acute_pain_no_pain_today_high_volume_intensity)
                        trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                        trigger.severity = soreness.severity
                        trigger.pain = True
                        trigger.historic_soreness_status = soreness.historic_soreness_status
                        self.triggers.append(trigger)
            else:
                trigger = Trigger(TriggerType.not_enough_history_for_high_volume_intensity)  # 25
                self.triggers.append(trigger)

            if soreness.daily and not soreness.pain:

                if soreness.historic_soreness_status == HistoricSorenessStatus.doms:
                    trigger = Trigger(TriggerType.sore_today_doms)  # 11
                    trigger.historic_soreness_status = soreness.historic_soreness_status

                elif ((soreness.is_persistent_soreness() or
                       soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
                      (self.event_date_time - soreness.first_reported_date_time).days < 30):
                    trigger = Trigger(TriggerType.hist_sore_less_30_sore_today)  # 12
                    trigger.historic_soreness_status = soreness.historic_soreness_status

                elif ((soreness.is_persistent_soreness() or
                       soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
                      (self.event_date_time - soreness.first_reported_date_time).days >= 30):

                    trigger = Trigger(TriggerType.hist_sore_greater_30_sore_today)  # 13
                    trigger.historic_soreness_status = soreness.historic_soreness_status

                else:  # somehow missed doms
                    trigger = Trigger(TriggerType.sore_today)  # 10
                    trigger.historic_soreness_status = soreness.historic_soreness_status

                if body_part is not None:
                    trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                    trigger.severity = soreness.severity
                    trigger.pain = False
                    self.triggers.append(trigger)

            if (soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None and
                    (soreness.is_acute_pain() or soreness.is_persistent_pain() or
                     soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain)):

                    body_part = body_part_factory.get_body_part(soreness.body_part)

                    if body_part is not None:
                        trigger = Trigger(TriggerType.hist_pain)  # 16
                        trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                        trigger.severity = soreness.severity
                        trigger.pain = True
                        trigger.historic_soreness_status = soreness.historic_soreness_status
                        self.triggers.append(trigger)

            if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None \
                    and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:

                if not soreness.pain and days_diff >= 30:

                    body_part = body_part_factory.get_body_part(soreness.body_part)

                    if body_part is not None:
                        trigger = Trigger(TriggerType.hist_sore_greater_30)  # 19
                        trigger.severity = soreness.severity
                        trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                        trigger.antagonists = body_part.antagonists
                        trigger.synergists = body_part.synergists
                        trigger.pain = False
                        trigger.historic_soreness_status = soreness.historic_soreness_status
                        self.triggers.append(trigger)

                elif ((soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain or soreness.is_persistent_pain())
                      and not soreness.daily):
                    goal = AthleteGoal("Increase prevention efficacy", 1, AthleteGoalType.preempt_corrective)
                    if days_diff is not None and days_diff < 30:
                        trigger = Trigger(TriggerType.pers_pers2_pain_less_30_no_pain_today)  # 21

                    else:
                        trigger = Trigger(TriggerType.pers_pers2_pain_greater_30_no_pain_today)  # 22
                    trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                    trigger.severity = soreness.severity
                    trigger.pain = True
                    trigger.historic_soreness_status = soreness.historic_soreness_status
                    self.triggers.append(trigger)

            if soreness.daily and soreness.pain:

                body_part = body_part_factory.get_body_part(soreness.body_part)

                if soreness.severity < 3:
                    if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
                            soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
                        trigger = Trigger(TriggerType.no_hist_pain_pain_today_severity_1_2)  # 14

                    else:
                        trigger = Trigger(TriggerType.hist_pain_pain_today_severity_1_2)  # 23

                else:
                    if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
                            soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
                        trigger = Trigger(TriggerType.no_hist_pain_pain_today_high_severity_3_5)  # 15

                    else:
                        trigger = Trigger(TriggerType.hist_pain_pain_today_severity_3_5)  # 24

                if body_part is not None:
                    trigger.body_part = BodyPartSide(soreness.body_part.location, soreness.side)
                    trigger.pain = True
                    trigger.historic_soreness_status = soreness.historic_soreness_status
                    trigger.severity = soreness.severity
                    self.triggers.append(trigger)



