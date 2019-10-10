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
        twenty_days_ago = self.event_date_time.date() - timedelta(days=19)

        todays_symptoms = [s for s in self.symptoms if s.event_date_time.date() == self.event_date_time.date()]

        for t in todays_symptoms:

            # Inflammation
            # TODO: make sure t is a muscle

            inflammation_related_joint_symptoms =[s for s in self.symptoms if s.body_part.body_part_location.value in
                                                  functional_anatomy_processor.get_related_joints(t.body_part.body_part_location.value) and
                                                  ((s.sharp is not None and s.sharp > 0) or (s.ache is not None and s.ache > 0)) and
                                                  s.event_date_time >= ten_days_ago]

            if ((t.sharp is not None and t.sharp > 0) or (t.ache is not None and t.ache > 0) or
                    len(inflammation_related_joint_symptoms) > 1):  # require a least two occurrences in last 10 days
                t.inflammation = 1

            # Muscle Spasm
            # TODO: make sure t is a muscle

            muscle_spasm_related_joint_symptoms = [s for s in self.symptoms if s.body_part.body_part_location.value in
                                                   functional_anatomy_processor.get_related_joints(
                                                       t.body_part.body_part_location.value) and
                                                   (
                                                           (s.sharp is not None and s.sharp > 0) or
                                                           (s.tight is not None and s.tight > 0) or
                                                           (s.ache is not None and s.ache >= 4)
                                                   ) and
                                                  s.event_date_time.date() == self.event_date_time.date()]

            muscle_spasm_related_joint_ache = [s for s in self.symptoms if s.body_part.body_part_location.value in
                                               functional_anatomy_processor.get_related_joints(
                                                       t.body_part.body_part_location.value) and
                                               (s.ache is not None and s.ache > 0) and
                                               ten_days_ago <= s.event_date_time.date() <= three_days_ago]

            muscle_spasm_ache = [s for s in self.symptoms if (s.ache is not None and s.ache > 0) and
                                 ten_days_ago <= s.event_date_time.date() <= three_days_ago]

            if ((t.sharp is not None and t.sharp > 0) or (t.tight is not None and t.tight > 0) or
                    len(muscle_spasm_related_joint_symptoms) > 0  # daily so just need > 0
                    or len(muscle_spasm_related_joint_ache) > 1
                    or len(muscle_spasm_ache) > 1):
                t.muscle_spasm = 1

            # Adhesions
            # TODO make sure t is a muscle

            adhesions_related_joint_tight_sharp = [s for s in self.symptoms if s.body_part.body_part_location.value in
                                                   functional_anatomy_processor.get_related_joints(
                                                       t.body_part.body_part_location.value) and
                                                   (
                                                           (s.tight is not None and s.tight > 0) or
                                                           (s.sharp is not None and s.sharp > 0)
                                                   )
                                                   and twenty_days_ago <= s.event_date_time.date() <= three_days_ago]

            adhesions_tight_sharp = [s for s in self.symptoms if (
                    (s.tight is not None and s.tight > 0) or
                    (s.sharp is not None and s.sharp > 0)
            ) and
                                     twenty_days_ago <= s.event_date_time.date() <= three_days_ago]

            adhesions_related_joint_ache = [s for s in self.symptoms if s.body_part.body_part_location.value in
                                            functional_anatomy_processor.get_related_joints(
                                                       t.body_part.body_part_location.value) and
                                            s.ache is not None and s.ache > 0
                                            and twenty_days_ago <= s.event_date_time.date() <= three_days_ago]

            adhesions_ache = [s for s in self.symptoms if (s.ache is not None and s.ache > 0) and
                              twenty_days_ago <= s.event_date_time.date() <= three_days_ago]

            if (t.knots is not None and t.knots > 0 or
                len(adhesions_related_joint_tight_sharp) >= 3 or
                len(adhesions_tight_sharp) >= 3 or
                    len(adhesions_related_joint_ache) >= 4 or
                    len(adhesions_ache) >= 4):
                t.adhesions = 1




