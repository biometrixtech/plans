from models.body_parts import BodyPartFactory, BodyPartLocation, BodyPart
from models.session import SessionSource
from models.soreness_base import HistoricSorenessStatus, BodyPartSide
from models.goal import AthleteGoalType, AthleteGoal
from models.trigger import TriggerType, Trigger


class TriggerFactory(object):
    def __init__(self, event_date_time, athlete_stats, soreness_list, training_sessions):
        self.event_date_time = event_date_time
        self.triggers = []

        if athlete_stats is not None and athlete_stats.triggers is not None:
            self.triggers = athlete_stats.triggers
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

    def set_trigger(self, trigger_type, soreness=None, sport_name=None):

        trigger_index = -1

        if soreness is None and sport_name is None:

            trigger_index = next((i for i, x in enumerate(self.triggers) if trigger_type == x.trigger_type), -1)

        elif soreness is not None and sport_name is None:

            body_part = BodyPartSide(soreness.body_part.location, soreness.side)

            trigger_index = next((i for i, x in enumerate(self.triggers) if trigger_type == x.trigger_type and
                                  body_part.body_part_location == x.body_part.body_part_location and
                                  body_part.side == x.body_part.side and
                                  soreness.pain == x.pain and
                                  soreness.historic_soreness_status == x.historic_soreness_status), -1)

        elif soreness is not None and sport_name is not None:

            body_part = BodyPartSide(soreness.body_part.location, soreness.side)

            trigger_index = next((i for i, x in enumerate(self.triggers) if trigger_type == x.trigger_type and
                                  body_part.body_part_location == x.body_part.body_part_location and
                                  body_part.side == x.body_part.side and
                                  soreness.pain == x.pain and
                                  soreness.historic_soreness_status == x.historic_soreness_status and
                                  sport_name == x.sport_name), -1)

        elif sport_name is not None:

            trigger_index = next((i for i, x in enumerate(self.triggers) if trigger_type == x.trigger_type and
                                  sport_name == x.sport_name), -1)

        if trigger_index > -1:

            if self.triggers[trigger_index].deleted_date_time is not None:
                self.triggers[trigger_index].deleted_date_time = None
                self.triggers[trigger_index].created_date_time = self.event_date_time
                self.triggers[trigger_index].modified_date_time = self.event_date_time
            else:
                self.triggers[trigger_index].modified_date_time = self.event_date_time

            if soreness is not None:
                self.triggers[trigger_index].severity = soreness.severity
                self.triggers[trigger_index].source_date_time = soreness.status_changed_date_time

        else:

            trigger = Trigger(trigger_type)
            trigger.created_date_time = self.event_date_time
            trigger.modified_date_time = self.event_date_time

            if soreness is not None:
                body_part_factory = BodyPartFactory()
                body_part = body_part_factory.get_body_part(soreness.body_part)

                body_part_side = BodyPartSide(soreness.body_part.location, soreness.side)

                trigger.body_part = body_part_side
                trigger.pain = soreness.pain
                trigger.severity = soreness.severity
                trigger.historic_soreness_status = soreness.historic_soreness_status
                trigger.agonists = self.convert_body_part_list(body_part_side, body_part.agonists)
                trigger.antagonists = self.convert_body_part_list(body_part_side, body_part.antagonists)
                trigger.synergists = self.convert_body_part_list(body_part_side, body_part.synergists)
                trigger.source_date_time = soreness.status_changed_date_time

            trigger.sport_name = sport_name
            self.triggers.append(trigger)


    def convert_body_part_list(self, body_part_side, body_part_list):

        body_part_side_list = []
        body_part_factory = BodyPartFactory()

        if body_part_side.side == 1 or body_part_side.side == 2:
            for b in body_part_list:
                body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(b), None))
                if body_part.bilateral:
                    body_part_side_new = BodyPartSide(BodyPartLocation(b), body_part_side.side)
                else:
                    body_part_side_new = BodyPartSide(BodyPartLocation(b), side=0)

                body_part_side_list.append(body_part_side_new)
        else:
            for b in body_part_list:
                body_part = body_part_factory.get_body_part(BodyPart(BodyPartLocation(b), None))
                if body_part.bilateral:
                    body_part_side_1 = BodyPartSide(BodyPartLocation(b), side=1)
                    body_part_side_2 = BodyPartSide(BodyPartLocation(b), side=2)
                    body_part_side_list.append(body_part_side_1)
                    body_part_side_list.append(body_part_side_2)
                else:
                    body_part_side_new = BodyPartSide(BodyPartLocation(b), side=0)
                    body_part_side_list.append(body_part_side_new)

        return body_part_side_list

    def load_triggers(self):

        if self.high_relative_load_session or self.high_relative_intensity_session:

            for sport_name in self.high_relative_load_session_sport_names:
                self.set_trigger(TriggerType.high_volume_intensity, sport_name=sport_name)  # 0

        hist_soreness = list(s for s in self.soreness_list if not s.is_dormant_cleared() and not s.pain and
                             (s.is_persistent_soreness() or
                              s.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
                             (self.event_date_time.date() - s.first_reported_date_time.date()).days < 30)

        if len(hist_soreness) > 0:

            for soreness in hist_soreness:
                self.set_trigger(TriggerType.hist_sore_less_30, soreness=soreness)  # 7

        if self.muscular_strain_high:
            self.set_trigger(TriggerType.overreaching_high_muscular_strain)  # 8

        for session in self.training_sessions:
            if session.source == SessionSource.three_sensor:
                if session.asymmetry is not None:
                    if session.left_apt != session.right_apt:
                        self.set_trigger(TriggerType.movement_error_apt_asymmetry, soreness=None, sport_name=None) # 110

        for soreness in self.soreness_list:

            days_diff = None
            if soreness.first_reported_date_time is not None:
                days_diff = (self.event_date_time.date() - soreness.first_reported_date_time.date()).days

            if self.eligible_for_high_load_trigger:
                if (soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and not soreness.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    if days_diff is not None and days_diff >= 30:
                        for sport_name in self.high_relative_load_session_sport_names:
                            self.set_trigger(TriggerType.hist_sore_greater_30_high_volume_intensity, soreness=soreness, sport_name=sport_name)  # 1

                elif (soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and soreness.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    for sport_name in self.high_relative_load_session_sport_names:
                        self.set_trigger(TriggerType.hist_pain_high_volume_intensity, soreness=soreness, sport_name=sport_name)  # 2

                elif (not soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and not soreness.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    if days_diff is not None and days_diff >= 30:
                        self.set_trigger(TriggerType.hist_sore_greater_30_no_sore_today_high_volume_intensity, soreness=soreness)  # 3

                elif (not soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and soreness.pain and soreness.is_acute_pain() and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    self.set_trigger(TriggerType.acute_pain_no_pain_today_high_volume_intensity, soreness=soreness)  # 4

                elif (not soreness.daily and soreness.historic_soreness_status is not None and not soreness.is_dormant_cleared()
                      and soreness.historic_soreness_status is not HistoricSorenessStatus.doms
                      and soreness.pain and (self.high_relative_load_session or self.high_relative_intensity_session)):

                    if soreness.is_persistent_pain() or soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain:
                        self.set_trigger(TriggerType.pers_pers2_pain_no_pain_sore_today_high_volume_intensity, soreness=soreness)  # 5

                    elif soreness.is_acute_pain():
                        self.set_trigger(TriggerType.acute_pain_no_pain_today_high_volume_intensity, soreness=soreness)

            else:
                self.set_trigger(TriggerType.not_enough_history_for_high_volume_intensity)  # 25

            if soreness.daily and not soreness.pain:

                if soreness.historic_soreness_status == HistoricSorenessStatus.doms:
                    self.set_trigger(TriggerType.sore_today_doms, soreness=soreness)  # 11

                elif ((soreness.is_persistent_soreness() or
                       soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
                      days_diff is not None and days_diff < 30):
                    self.set_trigger(TriggerType.hist_sore_less_30_sore_today,soreness=soreness)  # 12

                elif ((soreness.is_persistent_soreness() or
                       soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_soreness) and
                      days_diff is not None and days_diff >= 30):

                    self.set_trigger(TriggerType.hist_sore_greater_30_sore_today, soreness=soreness)  # 13

                else:  # somehow missed doms
                    self.set_trigger(TriggerType.sore_today, soreness=soreness)  # 10

            if (soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None and
                    (soreness.is_acute_pain() or soreness.is_persistent_pain() or
                     soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain)):

                self.set_trigger(TriggerType.hist_pain, soreness=soreness)  # 16

            if soreness.historic_soreness_status is not None and soreness.first_reported_date_time is not None \
                    and not soreness.is_dormant_cleared() and soreness.historic_soreness_status is not HistoricSorenessStatus.doms:

                if not soreness.pain and days_diff is not None and days_diff >= 30:

                    self.set_trigger(TriggerType.hist_sore_greater_30, soreness=soreness)  # 19

                elif ((soreness.historic_soreness_status == HistoricSorenessStatus.persistent_2_pain or soreness.is_persistent_pain())
                      and not soreness.daily):

                    if days_diff is not None and days_diff < 30:
                        self.set_trigger(TriggerType.pers_pers2_pain_less_30_no_pain_today, soreness=soreness)  # 21

                    else:
                        self.set_trigger(TriggerType.pers_pers2_pain_greater_30_no_pain_today,soreness=soreness)  # 22

            if soreness.daily and soreness.pain:

                if soreness.severity < 3:
                    if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
                            soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
                        self.set_trigger(TriggerType.no_hist_pain_pain_today_severity_1_2,soreness=soreness)  # 14

                    else:
                        self.set_trigger(TriggerType.hist_pain_pain_today_severity_1_2, soreness=soreness)  # 23

                else:
                    if (not soreness.is_acute_pain() and not soreness.is_persistent_pain() and
                            soreness.historic_soreness_status is not HistoricSorenessStatus.persistent_2_pain):
                        self.set_trigger(TriggerType.no_hist_pain_pain_today_high_severity_3_5, soreness=soreness)  # 15

                    else:
                        self.set_trigger(TriggerType.hist_pain_pain_today_severity_3_5,soreness=soreness)  # 24

        for t in self.triggers:
            if t.created_date_time != self.event_date_time and t.modified_date_time != self.event_date_time:
                t.deleted_date_time = self.event_date_time

        self.triggers = [t for t in self.triggers if t.deleted_date_time is None]


