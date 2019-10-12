from datetime import datetime, timedelta
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.functional_movement import BodyPartInjuryRisk


class InjuryRiskProcessor(object):
    def __init__(self, event_date_time, symptoms_list, training_session_list, injury_risk_dict):
        self.event_date_time = event_date_time
        self.symptoms = symptoms_list
        self.training_sessions = training_session_list
        self.injury_risk_dict = injury_risk_dict
        self.two_days_ago = self.event_date_time.date() - timedelta(days=1)
        self.three_days_ago = self.event_date_time.date() - timedelta(days=2)
        self.ten_days_ago = self.event_date_time.date() - timedelta(days=9)
        self.twenty_days_ago = self.event_date_time.date() - timedelta(days=19)
        self.functional_anatomy_processor = FunctionalAnatomyProcessor()

    def process_all_sessions(self):
        pass

    def process(self, update_historical_symptoms=False):

        if update_historical_symptoms:
            self.update_historical_symptoms()

        self.process_todays_symptoms()

    def reset_reported_symptoms(self):

        for b in self.injury_risk_dict.keys():
            self.injury_risk_dict[b].last_sharp_date = None
            self.injury_risk_dict[b].last_ache_date = None
            self.injury_risk_dict[b].last_tight_date = None
            self.injury_risk_dict[b].sharp_count_last_3_20_days = 0
            self.injury_risk_dict[b].sharp_count_last_0_10_days = 0
            self.injury_risk_dict[b].ache_count_last_3_20_days = 0
            self.injury_risk_dict[b].ache_count_last_0_10_days = 0
            self.injury_risk_dict[b].ache_count_last_3_10_days = 0
            self.injury_risk_dict[b].tight_count_last_3_20_days = 0

    def update_historical_symptoms(self):

        last_20_days_symptoms = [s for s in self.symptoms if s.event_date_time.date() >= self.ten_days_ago]
        last_20_days_symptoms = sorted(last_20_days_symptoms, key=lambda x:x.event_date_time)

        self.reset_reported_symptoms()

        for s in last_20_days_symptoms:
            target_body_part_side = BodyPartSide(s.body_part.body_part_location, s.side)
            if s.sharp > 0:
                if target_body_part_side not in self.injury_risk_dict:
                    self.injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if self.injury_risk_dict[target_body_part_side].last_sharp_date < s.event_date_time.date():
                    self.injury_risk_dict[target_body_part_side].last_sharp_date = s.event_date_time.date()
                    if s.event_date_time.date() <= self.three_days_ago:
                        self.injury_risk_dict[target_body_part_side].sharp_count_last_3_20_days += 1
                    if s.event_date_time.date() >= self.ten_days_ago:
                        self.injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
            if s.ache > 0:
                if target_body_part_side not in self.injury_risk_dict:
                    self.injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if self.injury_risk_dict[target_body_part_side].last_ache_date < s.event_date_time.date():
                    self.injury_risk_dict[target_body_part_side].last_ache_date = s.event_date_time.date()
                    if s.event_date_time.date() <= self.three_days_ago:
                        self.injury_risk_dict[target_body_part_side].ache_count_last_3_20_days += 1
                    if s.event_date_time.date() >= self.ten_days_ago:
                        self.injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    if self.three_days_ago >= s.event_date_time.date() >= self.ten_days_ago:
                        self.injury_risk_dict[target_body_part_side].ache_count_last_3_10_days += 1
            if s.tight > 0:
                if target_body_part_side not in self.injury_risk_dict:
                    self.injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if self.injury_risk_dict[target_body_part_side].last_tight_date < s.event_date_time.date():
                    self.injury_risk_dict[target_body_part_side].last_tight_date = s.event_date_time.date()
                    if s.event_date_time.date() <= self.three_days_ago:
                        self.injury_risk_dict[target_body_part_side].tight_count_last_3_20_days += 1

    def process_todays_symptoms(self):

        todays_symptoms = [s for s in self.symptoms if s.event_date_time.date() == self.event_date_time.date()]

        for t in todays_symptoms:

            related_joints = self.functional_anatomy_processor.get_related_joints(t.body_part.body_part_location.value)

            # Inflammation
            # TODO: make sure t is a muscle
            # TODO: check for ligament or severity-based measures

            self.identify_inflammation_today(related_joints, t, todays_symptoms)

            # Muscle Spasm
            # TODO: make sure t is a muscle
            self.identify_muscle_spasm_today(related_joints, t, todays_symptoms)

            # Adhesions
            # TODO make sure t is a muscle
            self.identify_adhesions_today(related_joints, t)

    def identify_inflammation_today(self, related_joints, target_symptom, todays_symptoms):

        max_related_joint_sharp_count_last_10_days = 0
        max_related_joint_ache_count_last_10_days = 0

        for r in related_joints:
            # are any already in our historical list? update if yes, add if not; keep track of counts for diagnosis
            body_part_side = BodyPartSide(BodyPartLocation(r), target_symptom.body_part.side)

            todays_sharp_symptoms = [s for s in todays_symptoms
                                     if s.body_part.body_part_location == body_part_side.body_part_location
                                     and s.body_part.side == body_part_side.side and s.sharp > 0]
            todays_ache_symptoms = [s for s in todays_symptoms
                                    if s.body_part.body_part_location == body_part_side.body_part_location
                                    and s.body_part.side == body_part_side.side and s.ache > 0]

            if body_part_side in self.injury_risk_dict:
                sharp_count = self.injury_risk_dict[body_part_side].sharp_count_last_0_10_days
                if self.injury_risk_dict[body_part_side].last_sharp_date < self.event_date_time.date():
                    if len(todays_sharp_symptoms) > 0:
                        self.injury_risk_dict[body_part_side].last_sharp_date = self.event_date_time.date()
                        self.injury_risk_dict[body_part_side].sharp_count_last_0_10_days += 1
                        sharp_count = self.injury_risk_dict[body_part_side].sharp_count_last_0_10_days
                max_related_joint_sharp_count_last_10_days = max(max_related_joint_sharp_count_last_10_days,
                                                                 sharp_count)
                ache_count = self.injury_risk_dict[body_part_side].ache_count_last_0_10_days
                if self.injury_risk_dict[body_part_side].last_ache_date < self.event_date_time.date():

                    if len(todays_ache_symptoms) > 0:
                        self.injury_risk_dict[body_part_side].last_ache_date = self.event_date_time.date()
                        self.injury_risk_dict[body_part_side].ache_count_last_0_10_days += 1
                        ache_count = self.injury_risk_dict[body_part_side].ache_count_last_0_10_days
                max_related_joint_ache_count_last_10_days = max(max_related_joint_ache_count_last_10_days, ache_count)
            elif len(todays_sharp_symptoms) > 0 or len(todays_ache_symptoms) > 0:

                body_part_injury_risk = BodyPartInjuryRisk()

                if len(todays_sharp_symptoms) > 0:
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    body_part_injury_risk.last_sharp_date = self.event_date_time.date()
                if len(todays_ache_symptoms) > 0:
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    body_part_injury_risk.last_ache_date = self.event_date_time.date()

                self.injury_risk_dict[body_part_side] = body_part_injury_risk
                max_related_joint_sharp_count_last_10_days = max(max_related_joint_sharp_count_last_10_days, 1)
                max_related_joint_ache_count_last_10_days = max(max_related_joint_ache_count_last_10_days, 1)

        if ((target_symptom.sharp is not None and target_symptom.sharp > 0) or (target_symptom.ache is not None and target_symptom.ache > 0) or
                max_related_joint_sharp_count_last_10_days > 1 or max_related_joint_ache_count_last_10_days > 1):  # require a least two occurrences in last 10 days
            # update the injury risk dict accordingly
            target_body_part_side = BodyPartSide(target_symptom.body_part.body_part_location, target_symptom.side)
            if target_body_part_side in self.injury_risk_dict:
                self.injury_risk_dict[target_body_part_side].last_inflammation_date = self.event_date_time.date()
                self.injury_risk_dict[target_body_part_side].last_inhibited_date = self.event_date_time.date()
            else:
                body_part_injury_risk = BodyPartInjuryRisk()
                body_part_injury_risk.last_inflammation_date = self.event_date_time.date()
                body_part_injury_risk.last_inhibited_date = self.event_date_time.date()
                self.injury_risk_dict[target_body_part_side] = body_part_injury_risk

        # now treat everything with excessive strain in last 2 days as inflammation
        excessive_strain_body_parts = dict(filter(lambda elem: elem.last_excessive_strain_date >= self.two_days_ago, self.injury_risk_dict))

        for b, e in excessive_strain_body_parts.items():
            self.injury_risk_dict[b].last_inflammation_date = self.event_date_time.date()

    def identify_muscle_spasm_today(self, related_joints, target_symptom, todays_symptoms):

        related_joint_sharp = False
        related_joint_tight = False
        related_joint_ache = False
        reported_ache_3_10_days = False

        target_body_part_side = BodyPartSide(target_symptom.body_part.body_part_location, target_symptom.side)

        for r in related_joints:
            # are any already in our historical list? update if yes, add if not; keep track of counts for diagnosis
            body_part_side = BodyPartSide(BodyPartLocation(r), target_symptom.body_part.side)

            todays_sharp_symptoms = [s for s in todays_symptoms
                                     if s.body_part.body_part_location == body_part_side.body_part_location
                                     and s.body_part.side == body_part_side.side and s.sharp > 0]
            todays_tight_symptoms = [s for s in todays_symptoms
                                    if s.body_part.body_part_location == body_part_side.body_part_location
                                    and s.body_part.side == body_part_side.side and s.tight > 0]

            # TODO: is moderate to high ache severity > 3?
            todays_ache_symptoms = [s for s in todays_symptoms
                                     if s.body_part.body_part_location == body_part_side.body_part_location
                                     and s.body_part.side == body_part_side.side and s.ache > 3]

            if len(todays_sharp_symptoms) > 0:
                related_joint_sharp = True
                if body_part_side in self.injury_risk_dict:
                    if self.injury_risk_dict[body_part_side].last_sharp_date < self.event_date_time.date():
                        self.injury_risk_dict[body_part_side].last_sharp_date = self.event_date_time.date()
                        self.injury_risk_dict[body_part_side].sharp_count_last_0_10_days += 1
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    body_part_injury_risk.last_sharp_date = self.event_date_time.date()
                    self.injury_risk_dict[body_part_injury_risk] = body_part_injury_risk

            if len(todays_tight_symptoms) > 0:
                related_joint_tight = True
                if body_part_side in self.injury_risk_dict:
                    if self.injury_risk_dict[body_part_side].last_tight_date < self.event_date_time.date():
                        self.injury_risk_dict[body_part_side].last_tight_date = self.event_date_time.date()
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_tight_date = self.event_date_time.date()
                    self.injury_risk_dict[body_part_injury_risk] = body_part_injury_risk

            if len(todays_ache_symptoms) > 0:
                related_joint_ache = True
                if body_part_side in self.injury_risk_dict:
                    # this is a little misleading as this is only looking at higher aches, but still trying to capture what we know
                    if self.injury_risk_dict[body_part_side].last_ache_date < self.event_date_time.date():
                        self.injury_risk_dict[body_part_side].last_ache_date = self.event_date_time.date()
                        self.injury_risk_dict[body_part_side].ache_count_last_0_10_days += 1
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_ache_date = self.event_date_time.date()
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    self.injury_risk_dict[body_part_injury_risk] = body_part_injury_risk

            if body_part_side in self.injury_risk_dict:
                if self.injury_risk_dict[body_part_side].ache_count_last_3_10_days >= 2:
                    related_joint_ache = True

        if target_body_part_side in self.injury_risk_dict:
            if self.injury_risk_dict[target_body_part_side].ache_count_last_3_10_days >= 2:
                reported_ache_3_10_days = True

        if ((target_symptom.tight is not None and target_symptom.tight > 0) or (target_symptom.sharp is not None and target_symptom.sharp > 0) or
                (target_symptom.ache is not None and target_symptom.ache > 3) or
                related_joint_sharp or related_joint_tight or related_joint_ache or reported_ache_3_10_days):
            if target_body_part_side in self.injury_risk_dict:
                self.injury_risk_dict[target_body_part_side].last_muscle_spasm_date = self.event_date_time.date()
                self.injury_risk_dict[target_body_part_side].last_tight_date = self.event_date_time.date()
            else:
                body_part_injury_risk = BodyPartInjuryRisk()
                body_part_injury_risk.last_muscle_spasm_date = self.event_date_time.date()
                body_part_injury_risk.last_tight_date = self.event_date_time.date()
                self.injury_risk_dict[target_body_part_side] = body_part_injury_risk

    def identify_adhesions_today(self, related_joints, target_symptom):

        related_tight_count = False
        related_sharp_count = False
        related_ache_count = False
        reported_tight_count = False
        reported_sharp_count = False
        reported_ache_count = False

        target_body_part_side = BodyPartSide(target_symptom.body_part.body_part_location, target_symptom.side)

        for r in related_joints:
            # are any already in our historical list? update if yes, add if not; keep track of counts for diagnosis
            body_part_side = BodyPartSide(BodyPartLocation(r), target_symptom.body_part.side)

            if body_part_side in self.injury_risk_dict:
                if self.injury_risk_dict[body_part_side].tight_count_last_3_20_days >= 3:
                    related_tight_count = True
                if self.injury_risk_dict[body_part_side].sharp_count_last_3_20_days >= 3:
                    related_sharp_count = True
                if self.injury_risk_dict[body_part_side].ache_count_last_3_20_days >= 4:
                    related_ache_count = True

        if target_body_part_side in self.injury_risk_dict:
            if self.injury_risk_dict[target_body_part_side].tight_count_last_3_20_days >= 3:
                reported_tight_count = True
            if self.injury_risk_dict[target_body_part_side].sharp_count_last_3_20_days >= 3:
                reported_sharp_count = True
            if self.injury_risk_dict[target_body_part_side].ache_count_last_3_20_days >= 3:
                reported_ache_count = True

        if ((target_symptom.knots is not None and target_symptom.knots > 0) or related_tight_count or
            related_sharp_count or related_ache_count or reported_tight_count or reported_sharp_count or
                reported_ache_count):
            if target_body_part_side in self.injury_risk_dict:
                self.injury_risk_dict[target_body_part_side].last_adhesions_date = self.event_date_time.date()
                self.injury_risk_dict[target_body_part_side].last_short_date = self.event_date_time.date()
            else:
                body_part_injury_risk = BodyPartInjuryRisk()
                body_part_injury_risk.last_adhesions_date = self.event_date_time.date()
                body_part_injury_risk.last_short_date = self.event_date_time.date()
                self.injury_risk_dict[target_body_part_side] = body_part_injury_risk





