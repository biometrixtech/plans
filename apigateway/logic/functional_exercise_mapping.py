from models.functional_movement_modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining, WarmUp, CoolDown, FunctionalStrength
from models.functional_movement_activities import MovementPrep, MobilityWOD, ResponsiveRecovery, MovementIntegrationPrep, ActiveRest, ActiveRecovery, ColdWaterImmersion, Ice, IceSession
from models.body_parts import BodyPartLocation, BodyPartFactory
from models.goal import AthleteGoalType, AthleteGoal


class ExerciseAssignmentCalculator(object):

    def __init__(self, injury_risk_dict, exercise_library_datastore, completed_exercise_datastore, event_date_time, relative_load_level=3, aggregated_injury_risk_dict=None):
        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        self.injury_risk_dict = injury_risk_dict
        self.aggregated_injury_risk_dict = aggregated_injury_risk_dict or {}
        self.event_date_time = event_date_time
        self.relative_load_level = relative_load_level
        self.sport_cardio = False
        self.sport_body_parts = None

    def get_pre_active_rest(self, force_data=False, force_on_demand=False):

        if len(self.injury_risk_dict) > 0 or force_data:
            active_rest = ActiveRestBeforeTraining(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
            active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
            active_rest.set_plan_dosage()
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            active_rest.set_winners()
            active_rest.scale_all_active_time()
            active_rest.reconcile_default_plan_with_active_time()
            if active_rest.get_total_exercises() > 0:
                return [active_rest]
        return []

    def get_post_active_rest(self, force_data=False, force_on_demand=False):

        if len(self.injury_risk_dict) > 0 or force_data:
            active_rest = ActiveRestAfterTraining(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
            active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
            active_rest.set_plan_dosage()
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            active_rest.set_winners()
            active_rest.scale_all_active_time()
            active_rest.reconcile_default_plan_with_active_time()
            if active_rest.get_total_exercises() > 0:
                return [active_rest]
        return []

    def get_warm_up(self):
        warm_up = WarmUp(self.event_date_time)
        warm_up.fill_exercises(self.exercise_library, {})
        return [warm_up]

    def get_cool_down(self):
        cool_down = CoolDown(self.event_date_time)
        cool_down.fill_exercises(self.exercise_library, {})
        return [cool_down]

    def get_functional_strength(self):
        functional_strength = FunctionalStrength(self.event_date_time)
        functional_strength.fill_exercises(self.exercise_library, {})
        return [functional_strength]

    def get_movement_prep(self, athlete_id, force_data=False, force_on_demand=True):
        # get activity
        movement_integration_prep = MovementIntegrationPrep(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
        movement_integration_prep.fill_exercises(self.exercise_library, self.injury_risk_dict, sport_cardio=self.sport_cardio, sport_body_parts=self.sport_body_parts)
        movement_integration_prep.set_plan_dosage()
        movement_integration_prep.set_exercise_dosage_ranking()
        movement_integration_prep.aggregate_dosages()
        movement_integration_prep.set_winners()
        movement_integration_prep.scale_all_active_time()
        movement_integration_prep.reconcile_default_plan_with_active_time()

        # create movement prep and add activity
        movement_prep = MovementPrep(athlete_id, self.event_date_time)
        movement_prep.movement_integration_prep = movement_integration_prep

        return movement_prep

    def get_mobility_wod(self, athlete_id, force_data=False, force_on_demand=True):

        # get activity
        active_rest = ActiveRest(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
        active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
        active_rest.set_plan_dosage()
        active_rest.set_exercise_dosage_ranking()
        active_rest.aggregate_dosages()
        active_rest.set_winners()
        active_rest.scale_all_active_time()
        active_rest.reconcile_default_plan_with_active_time()

        # create mobility wod and add activity
        mobility_wod = MobilityWOD(athlete_id, self.event_date_time)
        mobility_wod.active_rest = active_rest

        return mobility_wod

    def get_responsive_recovery(self, athlete_id, force_data=False, force_on_demand=True):
        responsive_recovery = ResponsiveRecovery(athlete_id, self.event_date_time)

        active_recovery = ActiveRecovery(self.event_date_time)
        active_recovery.fill_exercises(self.exercise_library, self.injury_risk_dict)
        active_recovery.set_plan_dosage()
        active_recovery.set_exercise_dosage_ranking()
        active_recovery.aggregate_dosages()
        active_recovery.set_winners()
        active_recovery.scale_all_active_time()
        active_recovery.reconcile_default_plan_with_active_time()
        if active_recovery.get_total_exercises() > 0:
            responsive_recovery.active_recovery = active_recovery
        else:
            responsive_recovery.active_recovery = None

        if responsive_recovery.active_recovery is None:

            active_rest = ActiveRest(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
            active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
            active_rest.set_plan_dosage()
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            active_rest.set_winners()
            active_rest.scale_all_active_time()
            active_rest.reconcile_default_plan_with_active_time()
            if active_rest.get_total_exercises() > 0:
                responsive_recovery.active_rest = active_rest
            else:
                responsive_recovery.active_rest = None
            responsive_recovery.active_rest = active_rest
        cold_water_immersion = self.get_cold_water_immersion()
        responsive_recovery.cold_water_immersion = cold_water_immersion

        ice_session = self.get_ice_session()
        responsive_recovery.ice = self.adjust_ice_session(ice_session, cold_water_immersion)

        return responsive_recovery

    def get_cold_water_immersion(self):

        cold_water_immersion = None

        cwi_assigned = False
        for body_part, body_part_injury_risk in self.injury_risk_dict.items():

            base_date = self.event_date_time.date()

            if (self.is_lower_body_part(body_part.location)
                    and body_part_injury_risk.last_non_functional_overreaching_date == base_date
                    and not cwi_assigned):
                cold_water_immersion = ColdWaterImmersion(self.event_date_time)
                goal = AthleteGoal("Recovery", 1, AthleteGoalType.high_load)
                cold_water_immersion.goals.add(goal)
                cwi_assigned = True
                continue

        return cold_water_immersion

    def get_ice_session(self):

        ice_session = None

        ice_list = []

        minutes = []

        body_part_factory = BodyPartFactory()

        for body_part_side, body_part_injury_risk in self.aggregated_injury_risk_dict.items():
            base_date = self.event_date_time.date()

            if body_part_injury_risk.last_inflammation_date == base_date:
                #ice = Ice(body_part_location=body_part.body_part_location, side=body_part.side)

                if body_part_factory.is_joint(body_part_side) or body_part_factory.is_ligament(body_part_side):
                    ice_list.append(body_part_side)
                    minutes.append(10)
                else:
                    if body_part_injury_risk.last_sharp_date == self.event_date_time.date() and body_part_injury_risk.last_sharp_level >= 7:
                        ice_list.append(body_part_side)
                        minutes.append(15)

        if len(ice_list) > 0:
            ice_session = IceSession(self.event_date_time, minutes=min(minutes))
            ice_session.goal = AthleteGoal("Care", 1, AthleteGoalType.pain)
            body_part_ice_list = list(set(ice_list))
            ice_session.body_parts = [Ice.json_deserialise(body_part_side.json_serialise()) for body_part_side in body_part_ice_list]

            return ice_session

        return ice_session

    @staticmethod
    def is_lower_body_part(body_part_location):

        if (
                body_part_location == BodyPartLocation.hip_flexor or
                body_part_location == BodyPartLocation.hip or
                body_part_location == BodyPartLocation.deep_rotators_hip or
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

    def adjust_ice_session(self, ice_session, cold_water_immersion_session):

        if ice_session is not None and cold_water_immersion_session is not None:
            ice_session.body_parts = list(b for b in ice_session.body_parts if not self.is_lower_body_part(b.body_part_location))

            if len(ice_session.body_parts) == 0:
                ice_session = None

        return ice_session
