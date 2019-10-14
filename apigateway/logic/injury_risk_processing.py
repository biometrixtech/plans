from datetime import datetime, timedelta
from logic.functional_anatomy_processing import FunctionalAnatomyProcessor
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.functional_movement import BodyPartInjuryRisk, SessionFunctionalMovement


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
        self.eccentric_volume_dict = {}
        self.concentric_volume_dict = {}

    def process(self, update_historical_date=False):

        if update_historical_date:
            self.update_historical_data()
        else:
            self.process_todays_symptoms(self.event_date_time, self.injury_risk_dict)
            self.process_todays_sessions(self.event_date_time, self.injury_risk_dict)

        return self.injury_risk_dict

    def reset_reported_symptoms(self, injury_risk_dict):

        for b in self.injury_risk_dict.keys():
            injury_risk_dict[b].last_sharp_date = None
            injury_risk_dict[b].last_ache_date = None
            injury_risk_dict[b].last_tight_date = None
            injury_risk_dict[b].sharp_count_last_3_20_days = 0
            injury_risk_dict[b].sharp_count_last_0_10_days = 0
            injury_risk_dict[b].ache_count_last_3_20_days = 0
            injury_risk_dict[b].ache_count_last_0_10_days = 0
            injury_risk_dict[b].ache_count_last_3_10_days = 0
            injury_risk_dict[b].tight_count_last_3_20_days = 0

    def update_historical_symptoms(self, base_date, injury_risk_dict):

        twenty_days_ago = base_date.date() - timedelta(days=19)
        ten_days_ago = base_date.date() - timedelta(days=9)
        three_days_ago = base_date.date() - timedelta(days=2)

        last_20_days_symptoms = [s for s in self.symptoms if
                                 base_date.date() >= s.event_date_time.date() >= twenty_days_ago]

        self.reset_reported_symptoms(injury_risk_dict)

        for s in last_20_days_symptoms:
            target_body_part_side = BodyPartSide(s.body_part.body_part_location, s.side)
            if s.sharp > 0:
                if target_body_part_side not in injury_risk_dict:
                    injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if injury_risk_dict[target_body_part_side].last_sharp_date < s.event_date_time.date():
                    injury_risk_dict[target_body_part_side].last_sharp_date = s.event_date_time.date()
                    if s.event_date_time.date() <= three_days_ago:
                        injury_risk_dict[target_body_part_side].sharp_count_last_3_20_days += 1
                    if s.event_date_time.date() >= ten_days_ago:
                        injury_risk_dict[target_body_part_side].sharp_count_last_0_10_days += 1
            if s.ache > 0:
                if target_body_part_side not in injury_risk_dict:
                    injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if injury_risk_dict[target_body_part_side].last_ache_date < s.event_date_time.date():
                    injury_risk_dict[target_body_part_side].last_ache_date = s.event_date_time.date()
                    if s.event_date_time.date() <= three_days_ago:
                        injury_risk_dict[target_body_part_side].ache_count_last_3_20_days += 1
                    if s.event_date_time.date() >= ten_days_ago:
                        injury_risk_dict[target_body_part_side].ache_count_last_0_10_days += 1
                    if three_days_ago >= s.event_date_time.date() >= ten_days_ago:
                        injury_risk_dict[target_body_part_side].ache_count_last_3_10_days += 1
            if s.tight > 0:
                if target_body_part_side not in injury_risk_dict:
                    injury_risk_dict[target_body_part_side] = BodyPartInjuryRisk()
                if injury_risk_dict[target_body_part_side].last_tight_date < s.event_date_time.date():
                    injury_risk_dict[target_body_part_side].last_tight_date = s.event_date_time.date()
                    if s.event_date_time.date() <= three_days_ago:
                        injury_risk_dict[target_body_part_side].tight_count_last_3_20_days += 1

        return injury_risk_dict

    def update_historical_data(self):

        combined_dates = []
        combined_dates.extend([s.event_date_time.date() for s in self.training_sessions])

        #last_20_days_symptoms = [s for s in self.symptoms if s.event_date_time.date() >= self.twenty_days_ago.date()]
        combined_dates.extend([s.event_date_time.date() for s in self.symptoms])

        combined_dates = list(set(combined_dates))
        combined_dates.sort()

        #days_1_15 = [d for d in combined_dates if d < self.twenty_days_ago.date()]

        injury_risk_dict = {}

        # for d in days_1_15:
        #     initial_sessions = [t for t in self.training_sessions if t.event_date_time.date() == d]
        #     for s in initial_sessions:
        #         session_functional_movement = SessionFunctionalMovement(s, injury_risk_dict)
        #         session_functional_movement.process()
        #
        #         # update injury_risk_dict from session, calculate ramp, etc.

        #self.reset_reported_symptoms() # --> maybe start with brand new injury risk dict?

        #combined_dates = [d for d in combined_dates if d >= self.twenty_days_ago.date()]

        for d in combined_dates:

            seven_days_ago = d - timedelta(days=6)
            fourteeen_days_ago = d - timedelta(days=13)

            # first let's update our historical data
            injury_risk_dict = self.update_historical_symptoms(d, injury_risk_dict)

            injury_risk_dict = self.process_todays_symptoms(d, injury_risk_dict)
            # now process todays sessions
            daily_sessions = [n for n in self.training_sessions if n.event_date_time.date() == d]

            for session in daily_sessions:
                session_functional_movement = SessionFunctionalMovement(session, injury_risk_dict)
                session_functional_movement.process(d)
                for b in session_functional_movement.body_parts:

                    if b.body_part_side not in injury_risk_dict:
                        injury_risk_dict[b.body_part_side] = BodyPartInjuryRisk()

                    if b.body_part_side not in self.eccentric_volume_dict:
                        self.eccentric_volume_dict[b.body_part_side] = {}  # not we have a dictionary of dictionaries
                    self.eccentric_volume_dict[b.body_part_side][d] += b.eccentric_volume

                    if b.body_part_side not in self.concentric_volume_dict:
                        self.concentric_volume_dict[b.body_part_side] = {}  # not we have a dictionary of dictionaries
                    self.concentric_volume_dict[b.body_part_side][d] += b.concentric_volume

                    eccentric_volume_dict = self.eccentric_volume_dict[b.b.body_part_side]
                    concentric_volume_dict = self.concentric_volume_dict[b.b.body_part_side]

                    last_week_eccentric_volume_dict = dict(
                        filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago, eccentric_volume_dict))

                    last_week_concentric_volume_dict = dict(
                        filter(lambda elem: fourteeen_days_ago <= elem[0] < seven_days_ago, concentric_volume_dict))

                    current_week_eccentric_volume_dict = dict(
                        filter(lambda elem: d > elem[0] >= seven_days_ago, eccentric_volume_dict))

                    current_week_concentric_volume_dict = dict(
                        filter(lambda elem: d > elem[0] >= seven_days_ago, concentric_volume_dict))

                    last_week_eccentric_volume = sum(last_week_eccentric_volume_dict.values())
                    last_week_concentric_volume = sum(last_week_concentric_volume_dict.values())

                    todays_eccentric_volume = current_week_eccentric_volume_dict[d]
                    todays_concentric_volume = current_week_concentric_volume_dict[d]

                    current_week_concentric_volume = sum(current_week_concentric_volume_dict.values())
                    current_week_eccentric_volume = sum(current_week_eccentric_volume_dict.values())

                    injury_risk_dict[b.b.body_part_side].eccentric_volume_this_week = current_week_eccentric_volume
                    injury_risk_dict[b.b.body_part_side].eccentric_volume_last_week = last_week_eccentric_volume
                    injury_risk_dict[b.b.body_part_side].eccentric_volume_today = todays_eccentric_volume

                    injury_risk_dict[b.b.body_part_side].concentric_volume_this_week = current_week_concentric_volume
                    injury_risk_dict[b.b.body_part_side].concentric_volume_last_week = last_week_concentric_volume
                    injury_risk_dict[b.b.body_part_side].concentric_volume_today = todays_concentric_volume

                    eccentric_volume_ramp = injury_risk_dict[b.b.body_part_side].eccentric_volume_ramp()
                    total_volume_ramp = injury_risk_dict[b.b.body_part_side].total_volume_ramp()

                    if eccentric_volume_ramp > 1.0 or total_volume_ramp > 1.0:
                        injury_risk_dict[b.body_part_side].last_excessive_strain_date = d
                        injury_risk_dict[b.body_part_side].last_inflammation_date = d
                        injury_risk_dict[b.body_part_side].last_inhibited_date = d

                    if 1.0 < eccentric_volume_ramp <= 1.05:
                        injury_risk_dict[b.body_part_side].last_functional_overreaching_date = d
                    elif 1.05 < eccentric_volume_ramp:
                        injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = d

                    if 1.0 < total_volume_ramp <= 1.1:
                        injury_risk_dict[b.body_part_side].last_functional_overreaching_date = d
                    elif 1.1 < total_volume_ramp:
                        injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = d

    def process_todays_sessions(self, base_date, injury_risk_dict):

        daily_sessions = [n for n in self.training_sessions if n.event_date.date() == base_date.date()]

        for session in daily_sessions:
            session_functional_movement = SessionFunctionalMovement(session, injury_risk_dict)
            session_functional_movement.process(base_date)
            for b in session_functional_movement.body_parts:

                if b.body_part_side not in injury_risk_dict:
                    injury_risk_dict[b.body_part_side] = BodyPartInjuryRisk()

                injury_risk_dict[b.body_part_side].eccentric_volume_today += b.eccentric_volume
                injury_risk_dict[b.body_part_side].concentric_volume_today += b.concentric_volume

                eccentric_volume_ramp = injury_risk_dict[b.body_part_side].eccentric_volume_ramp()
                total_volume_ramp = injury_risk_dict[b.body_part_side].total_volume_ramp()

                if eccentric_volume_ramp > 1.0 or total_volume_ramp > 1.0:
                    injury_risk_dict[b.body_part_side].last_excessive_strain_date = base_date
                    injury_risk_dict[b.body_part_side].last_inflammation_date = base_date
                    injury_risk_dict[b.body_part_side].last_inhibited_date = base_date

                if 1.0 < eccentric_volume_ramp <= 1.05:
                    injury_risk_dict[b.body_part_side].last_functional_overreaching_date = base_date
                elif 1.05 < eccentric_volume_ramp:
                    injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = base_date

                if 1.0 < total_volume_ramp <= 1.1:
                    injury_risk_dict[b.body_part_side].last_functional_overreaching_date = base_date
                elif 1.1 < total_volume_ramp:
                    injury_risk_dict[b.body_part_side].last_non_functional_overreaching_date = base_date

    def process_todays_symptoms(self, base_date, injury_risk_dict):

        todays_symptoms = [s for s in self.symptoms if s.reported_date_time.date() == base_date.date()]

        for t in todays_symptoms:

            related_joints = self.functional_anatomy_processor.get_related_joints(t.body_part.location.value)

            # Inflammation
            # TODO: make sure t is a muscle
            # TODO: check for ligament or severity-based measures

            injury_risk_dict = self.identify_inflammation_today(base_date, related_joints, t, todays_symptoms, injury_risk_dict)

            # Muscle Spasm
            # TODO: make sure t is a muscle
            injury_risk_dict = self.identify_muscle_spasm_today(base_date, related_joints, t, todays_symptoms, injury_risk_dict)

            # Adhesions
            # TODO make sure t is a muscle
            injury_risk_dict = self.identify_adhesions_today(base_date, related_joints, t, injury_risk_dict)

        return injury_risk_dict

    def identify_inflammation_today(self, event_date_time, related_joints, target_symptom, todays_symptoms, injury_risk_dict):

        max_related_joint_sharp_count_last_10_days = 0
        max_related_joint_ache_count_last_10_days = 0

        for r in related_joints:
            # are any already in our historical list? update if yes, add if not; keep track of counts for diagnosis
            body_part_side = BodyPartSide(BodyPartLocation(r), target_symptom.side)

            todays_sharp_symptoms = [s for s in todays_symptoms
                                     if s.body_part.location == body_part_side.body_part_location
                                     and s.body_part.side == body_part_side.side and s.sharp > 0]
            todays_ache_symptoms = [s for s in todays_symptoms
                                    if s.body_part.location == body_part_side.body_part_location
                                    and s.body_part.side == body_part_side.side and s.ache > 0]

            if body_part_side in injury_risk_dict:
                sharp_count = injury_risk_dict[body_part_side].sharp_count_last_0_10_days
                if injury_risk_dict[body_part_side].last_sharp_date < event_date_time.date():
                    if len(todays_sharp_symptoms) > 0:
                        injury_risk_dict[body_part_side].last_sharp_date = event_date_time.date()
                        injury_risk_dict[body_part_side].sharp_count_last_0_10_days += 1
                        sharp_count = injury_risk_dict[body_part_side].sharp_count_last_0_10_days
                max_related_joint_sharp_count_last_10_days = max(max_related_joint_sharp_count_last_10_days,
                                                                 sharp_count)
                ache_count = injury_risk_dict[body_part_side].ache_count_last_0_10_days
                if injury_risk_dict[body_part_side].last_ache_date < event_date_time.date():

                    if len(todays_ache_symptoms) > 0:
                        injury_risk_dict[body_part_side].last_ache_date = event_date_time.date()
                        injury_risk_dict[body_part_side].ache_count_last_0_10_days += 1
                        ache_count = injury_risk_dict[body_part_side].ache_count_last_0_10_days
                max_related_joint_ache_count_last_10_days = max(max_related_joint_ache_count_last_10_days, ache_count)
            elif len(todays_sharp_symptoms) > 0 or len(todays_ache_symptoms) > 0:

                body_part_injury_risk = BodyPartInjuryRisk()

                if len(todays_sharp_symptoms) > 0:
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    body_part_injury_risk.last_sharp_date = event_date_time.date()
                if len(todays_ache_symptoms) > 0:
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    body_part_injury_risk.last_ache_date = event_date_time.date()

                injury_risk_dict[body_part_side] = body_part_injury_risk
                max_related_joint_sharp_count_last_10_days = max(max_related_joint_sharp_count_last_10_days, 1)
                max_related_joint_ache_count_last_10_days = max(max_related_joint_ache_count_last_10_days, 1)

        if ((target_symptom.sharp is not None and target_symptom.sharp > 0) or (target_symptom.ache is not None and target_symptom.ache > 0) or
                max_related_joint_sharp_count_last_10_days > 1 or max_related_joint_ache_count_last_10_days > 1):  # require a least two occurrences in last 10 days
            # update the injury risk dict accordingly
            target_body_part_side = BodyPartSide(target_symptom.body_part.location, target_symptom.side)
            if target_body_part_side in injury_risk_dict:
                injury_risk_dict[target_body_part_side].last_inflammation_date = event_date_time.date()
                injury_risk_dict[target_body_part_side].last_inhibited_date = event_date_time.date()
            else:
                body_part_injury_risk = BodyPartInjuryRisk()
                body_part_injury_risk.last_inflammation_date = event_date_time.date()
                body_part_injury_risk.last_inhibited_date = event_date_time.date()
                injury_risk_dict[target_body_part_side] = body_part_injury_risk

        # now treat everything with excessive strain in last 2 days as inflammation
        two_days_ago = event_date_time.date() - timedelta(days=1)
        excessive_strain_body_parts = dict(filter(lambda elem: elem[1].last_excessive_strain_date is not None and
                                                               elem[1].last_excessive_strain_date >= two_days_ago,
                                                  injury_risk_dict.items()))

        for b, e in excessive_strain_body_parts.items():
            injury_risk_dict[b].last_inflammation_date = event_date_time.date()

        return injury_risk_dict

    def identify_muscle_spasm_today(self, event_date_time, related_joints, target_symptom, todays_symptoms, injury_risk_dict):

        related_joint_sharp = False
        related_joint_tight = False
        related_joint_ache = False
        reported_ache_3_10_days = False

        target_body_part_side = BodyPartSide(target_symptom.body_part.location, target_symptom.side)

        for r in related_joints:
            # are any already in our historical list? update if yes, add if not; keep track of counts for diagnosis
            body_part_side = BodyPartSide(BodyPartLocation(r), target_symptom.side)

            todays_sharp_symptoms = [s for s in todays_symptoms
                                     if s.body_part.location == body_part_side.body_part_location
                                     and s.body_part.side == body_part_side.side and s.sharp > 0]
            todays_tight_symptoms = [s for s in todays_symptoms
                                    if s.body_part.location == body_part_side.body_part_location
                                    and s.body_part.side == body_part_side.side and s.tight > 0]

            # TODO: is moderate to high ache severity > 3?
            todays_ache_symptoms = [s for s in todays_symptoms
                                     if s.body_part.location == body_part_side.body_part_location
                                     and s.body_part.side == body_part_side.side and s.ache > 3]

            if len(todays_sharp_symptoms) > 0:
                related_joint_sharp = True
                if body_part_side in injury_risk_dict:
                    if injury_risk_dict[body_part_side].last_sharp_date < event_date_time.date():
                        injury_risk_dict[body_part_side].last_sharp_date = event_date_time.date()
                        injury_risk_dict[body_part_side].sharp_count_last_0_10_days += 1
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.sharp_count_last_0_10_days += 1
                    body_part_injury_risk.last_sharp_date = event_date_time.date()
                    injury_risk_dict[body_part_injury_risk] = body_part_injury_risk

            if len(todays_tight_symptoms) > 0:
                related_joint_tight = True
                if body_part_side in injury_risk_dict:
                    if injury_risk_dict[body_part_side].last_tight_date < event_date_time.date():
                        injury_risk_dict[body_part_side].last_tight_date = event_date_time.date()
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_tight_date = event_date_time.date()
                    injury_risk_dict[body_part_injury_risk] = body_part_injury_risk

            if len(todays_ache_symptoms) > 0:
                related_joint_ache = True
                if body_part_side in injury_risk_dict:
                    # this is a little misleading as this is only looking at higher aches, but still trying to capture what we know
                    if injury_risk_dict[body_part_side].last_ache_date < event_date_time.date():
                        injury_risk_dict[body_part_side].last_ache_date = event_date_time.date()
                        injury_risk_dict[body_part_side].ache_count_last_0_10_days += 1
                else:
                    body_part_injury_risk = BodyPartInjuryRisk()
                    body_part_injury_risk.last_ache_date = event_date_time.date()
                    body_part_injury_risk.ache_count_last_0_10_days += 1
                    injury_risk_dict[body_part_injury_risk] = body_part_injury_risk

            if body_part_side in injury_risk_dict:
                if injury_risk_dict[body_part_side].ache_count_last_3_10_days >= 2:
                    related_joint_ache = True

        if target_body_part_side in injury_risk_dict:
            if injury_risk_dict[target_body_part_side].ache_count_last_3_10_days >= 2:
                reported_ache_3_10_days = True

        if ((target_symptom.tight is not None and target_symptom.tight > 0) or (target_symptom.sharp is not None and target_symptom.sharp > 0) or
                (target_symptom.ache is not None and target_symptom.ache > 3) or
                related_joint_sharp or related_joint_tight or related_joint_ache or reported_ache_3_10_days):
            if target_body_part_side in injury_risk_dict:
                injury_risk_dict[target_body_part_side].last_muscle_spasm_date = event_date_time.date()
                injury_risk_dict[target_body_part_side].last_tight_date = event_date_time.date()
            else:
                body_part_injury_risk = BodyPartInjuryRisk()
                body_part_injury_risk.last_muscle_spasm_date = event_date_time.date()
                body_part_injury_risk.last_tight_date = event_date_time.date()
                injury_risk_dict[target_body_part_side] = body_part_injury_risk

        return injury_risk_dict

    def identify_adhesions_today(self, event_date_time, related_joints, target_symptom, injury_risk_dict):

        related_tight_count = False
        related_sharp_count = False
        related_ache_count = False
        reported_tight_count = False
        reported_sharp_count = False
        reported_ache_count = False

        target_body_part_side = BodyPartSide(target_symptom.body_part.location, target_symptom.side)

        for r in related_joints:
            # are any already in our historical list? update if yes, add if not; keep track of counts for diagnosis
            body_part_side = BodyPartSide(BodyPartLocation(r), target_symptom.side)

            if body_part_side in injury_risk_dict:
                if injury_risk_dict[body_part_side].tight_count_last_3_20_days >= 3:
                    related_tight_count = True
                if injury_risk_dict[body_part_side].sharp_count_last_3_20_days >= 3:
                    related_sharp_count = True
                if injury_risk_dict[body_part_side].ache_count_last_3_20_days >= 4:
                    related_ache_count = True

        if target_body_part_side in injury_risk_dict:
            if injury_risk_dict[target_body_part_side].tight_count_last_3_20_days >= 3:
                reported_tight_count = True
            if injury_risk_dict[target_body_part_side].sharp_count_last_3_20_days >= 3:
                reported_sharp_count = True
            if injury_risk_dict[target_body_part_side].ache_count_last_3_20_days >= 3:
                reported_ache_count = True

        if ((target_symptom.knots is not None and target_symptom.knots > 0) or related_tight_count or
            related_sharp_count or related_ache_count or reported_tight_count or reported_sharp_count or
                reported_ache_count):
            if target_body_part_side in injury_risk_dict:
                injury_risk_dict[target_body_part_side].last_adhesions_date = event_date_time.date()
                injury_risk_dict[target_body_part_side].last_short_date = event_date_time.date()
            else:
                body_part_injury_risk = BodyPartInjuryRisk()
                body_part_injury_risk.last_adhesions_date = event_date_time.date()
                body_part_injury_risk.last_short_date = event_date_time.date()
                injury_risk_dict[target_body_part_side] = body_part_injury_risk

        return injury_risk_dict



