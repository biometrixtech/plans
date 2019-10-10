from datetime import datetime, timedelta
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor

class InjuryRiskProcessor(object):
    def __init__(self, event_date_time, symptoms_list, training_session_list):
        self.event_date_time = event_date_time
        self.symptoms = symptoms_list
        self.training_sessions = training_session_list

    def export_symptoms(self):

        return self.symptoms

    def get_daily_symptoms(self):

        functional_anatomy_processor = FunctionalAnatomyProcessor()

        three_days_ago = self.event_date_time.date() - timedelta(days=2)
        ten_days_ago = self.event_date_time.date() - timedelta(days=9)

        # TODO: determine if we need to include yesterday with today
        todays_symptoms = [s for s in self.symptoms if s.event_date_time.date() == self.event_date_time.date()]

        for t in todays_symptoms:

            # Inflammation
            # TODO: make sure t is a muscle

            inflammation_related_joint_symptoms =[s for s in self.symptoms if s.body_part.body_part_location.value in
                                                  functional_anatomy_processor.get_related_joints(t.body_part.body_part_location.value) and
                                                  ((s.sharp is not None and s.sharp > 0) or (s.ache is not None and s.ache > 0)) and
                                                  s.event_date_time >= ten_days_ago]

            # TODO: incorporate "historic pattern" rather than just len > 0
            if ((t.sharp is not None and t.sharp > 0) or (t.ache is not None and t.ache > 0) or
                    len(inflammation_related_joint_symptoms) > 0):
                t.inflammation = 1

            # Muscle Spasm
            # TODO: make sure t is a muscle

            muscle_spasm_related_joint_symptoms = [s for s in self.symptoms if s.body_part.body_part_location.value in
                                                   functional_anatomy_processor.get_related_joints(
                                                       t.body_part.body_part_location.value) and
                                                   ((s.sharp is not None and s.sharp > 0) or (
                                                               s.tight is not None and s.tight > 0)) and
                                                  s.event_date_time.date() >= self.event_date_time.date()]

            # TODO: add in moderate to high severity condition
            # TODO: incorporate "historic pattern" rather than just len > 0
            muscle_spasm_related_joint_ache = [s for s in self.symptoms if s.body_part.body_part_location.value in
                                                   functional_anatomy_processor.get_related_joints(
                                                       t.body_part.body_part_location.value) and
                                                   ((s.ache is not None and s.sharp > 0)) and
                                                   ten_days_ago <= s.event_date_time.date() <= three_days_ago]

            if ((t.sharp is not None and t.sharp > 0) or (t.tight is not None and t.tight > 0) or
                    len(muscle_spasm_related_joint_symptoms) > 0 or len(muscle_spasm_related_joint_ache) > 0):
                t.muscle_spasm = 1






