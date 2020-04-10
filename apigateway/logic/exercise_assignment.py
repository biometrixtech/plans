from models.functional_movement_modalities import MovementIntegrationPrepModality, ActiveRestBeforeTraining, ActiveRestAfterTraining, ActiveRecoveryModality, ColdWaterImmersionModality, IceModality, IceSessionModalities
from models.functional_movement_activities import MovementPrep, MobilityWOD, MovementIntegrationPrep, ActiveRest, ResponsiveRecovery, ActiveRecovery, ColdWaterImmersion, IceSession, Ice
from models.body_parts import BodyPartLocation, BodyPartFactory
from models.goal import AthleteGoalType, AthleteGoal
import pickle


class ExerciseAssignment(object):

    def __init__(self, injury_risk_dict, exercise_library_datastore, completed_exercise_datastore,
                 event_date_time, relative_load_level=3, aggregated_injury_risk_dict=None,
                 log_intermediary_data=False):
        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        self.injury_risk_dict = injury_risk_dict
        self.aggregated_injury_risk_dict = aggregated_injury_risk_dict or {}
        self.event_date_time = event_date_time
        self.relative_load_level = relative_load_level
        self.sport_cardio_plyometrics = False
        self.sport_body_parts = {}
        self.high_intensity_session = False
        self.log_intermediary_data = log_intermediary_data

    def set_and_scale_dosage(self, activity):
        activity.set_plan_dosage()
        activity.set_exercise_dosage_ranking()
        if self.log_intermediary_data:
            activity.exercise_phases_pre_scaling = pickle.loads(pickle.dumps(activity.exercise_phases))
        activity.aggregate_dosages()
        activity.set_winners_2()
        activity.scale_all_active_time()
        activity.reconcile_default_plan_with_active_time()

    def get_pre_active_rest(self, force_data=False, force_on_demand=False):

        if len(self.injury_risk_dict) > 0 or force_data:
            active_rest = ActiveRestBeforeTraining(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
            active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
            active_rest.set_plan_dosage()
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            # active_rest.set_winners()
            active_rest.set_winners_2()
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
            # active_rest.set_winners()
            active_rest.set_winners_2()
            active_rest.scale_all_active_time()
            active_rest.reconcile_default_plan_with_active_time()
            if active_rest.get_total_exercises() > 0:
                return [active_rest]
        return []

    def get_movement_prep(self, athlete_id, force_data=False, force_on_demand=True):
        # get activity
        movement_integration_prep = MovementIntegrationPrep(
                self.event_date_time,
                force_data=force_data,
                relative_load_level=self.relative_load_level,
                force_on_demand=force_on_demand,
                sport_cardio_plyometrics=self.sport_cardio_plyometrics)
        movement_integration_prep.fill_exercises(self.exercise_library, self.injury_risk_dict, sport_body_parts=self.sport_body_parts)
        self.set_and_scale_dosage(movement_integration_prep)
        # movement_integration_prep.set_plan_dosage()
        # movement_integration_prep.set_exercise_dosage_ranking()
        # movement_integration_prep.aggregate_dosages()
        # movement_integration_prep.set_winners()
        # movement_integration_prep.scale_all_active_time()
        # movement_integration_prep.reconcile_default_plan_with_active_time()

        # create movement prep and add activity
        movement_prep = MovementPrep(athlete_id, self.event_date_time)
        movement_prep.movement_integration_prep = movement_integration_prep

        return movement_prep

    def get_mobility_wod(self, athlete_id, force_data=False, force_on_demand=True):

        # get activity
        active_rest = ActiveRest(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
        active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
        self.set_and_scale_dosage(active_rest)
        # active_rest.set_plan_dosage()
        # active_rest.set_exercise_dosage_ranking()
        # active_rest.aggregate_dosages()
        # active_rest.set_winners()
        # active_rest.scale_all_active_time()
        # active_rest.reconcile_default_plan_with_active_time()

        # create mobility wod and add activity
        mobility_wod = MobilityWOD(athlete_id, self.event_date_time)
        mobility_wod.active_rest = active_rest

        return mobility_wod

    def get_movement_integration_prep(self, force_data=False, force_on_demand=True):
        # get activity
        movement_integration_prep = MovementIntegrationPrepModality(
                self.event_date_time,
                force_data=force_data,
                relative_load_level=self.relative_load_level,
                force_on_demand=force_on_demand,
                sport_cardio_plyometrics=self.sport_cardio_plyometrics
        )
        movement_integration_prep.fill_exercises(self.exercise_library, self.injury_risk_dict, sport_body_parts=self.sport_body_parts)
        self.set_and_scale_dosage(movement_integration_prep)
        # movement_integration_prep.set_plan_dosage()
        # movement_integration_prep.set_exercise_dosage_ranking()
        # movement_integration_prep.aggregate_dosages()
        # movement_integration_prep.set_winners()
        # movement_integration_prep.scale_all_active_time()
        # movement_integration_prep.reconcile_default_plan_with_active_time()
        if movement_integration_prep.get_total_exercises() > 0:
            return [movement_integration_prep]

        return []

    def get_active_rest(self, force_data=False, force_on_demand=True):
        # get activity
        active_rest = ActiveRestAfterTraining(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
        active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
        self.set_and_scale_dosage(active_rest)
        # active_rest.set_plan_dosage()
        # active_rest.set_exercise_dosage_ranking()
        # active_rest.aggregate_dosages()
        # active_rest.set_winners()
        # active_rest.scale_all_active_time()
        # active_rest.reconcile_default_plan_with_active_time()
        # return [active_rest]
        if active_rest.get_total_exercises() > 0:
            return [active_rest]

        return []

    def get_responsive_recovery(self, athlete_id, force_data=False, force_on_demand=True):
        responsive_recovery = ResponsiveRecovery(athlete_id, self.event_date_time)

        active_recovery = ActiveRecovery(self.event_date_time)
        active_recovery.fill_exercises(self.exercise_library, self.injury_risk_dict, high_intensity_session=self.high_intensity_session)
        self.set_and_scale_dosage(active_recovery)
        # active_recovery.set_plan_dosage()
        # active_recovery.set_exercise_dosage_ranking()
        # active_recovery.aggregate_dosages()
        # active_recovery.set_winners()
        # active_recovery.scale_all_active_time()
        # active_recovery.reconcile_default_plan_with_active_time()
        if active_recovery.get_total_exercises() > 0:
            responsive_recovery.active_recovery = active_recovery
        else:
            responsive_recovery.active_recovery = None

        if responsive_recovery.active_recovery is None:

            active_rest = ActiveRest(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
            active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
            self.set_and_scale_dosage(active_rest)
            # active_rest.set_plan_dosage()
            # active_rest.set_exercise_dosage_ranking()
            # active_rest.aggregate_dosages()
            # active_rest.set_winners()
            # active_rest.scale_all_active_time()
            # active_rest.reconcile_default_plan_with_active_time()
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

    def get_responsive_recovery_modality(self, source_session_id, force_data=False, force_on_demand=True, ice_cwi=True):
        exercise_activity = []
        active_recovery = ActiveRecoveryModality(self.event_date_time)
        active_recovery.fill_exercises(self.exercise_library, self.injury_risk_dict, high_intensity_session=self.high_intensity_session)
        self.set_and_scale_dosage(active_recovery)
        # active_recovery.set_plan_dosage()
        # active_recovery.set_exercise_dosage_ranking()
        # active_recovery.aggregate_dosages()
        # active_recovery.set_winners()
        # active_recovery.scale_all_active_time()
        # active_recovery.reconcile_default_plan_with_active_time()
        active_recovery.source_training_session_id = source_session_id
        if active_recovery.get_total_exercises() > 0:
            exercise_activity = [active_recovery]
        else:
            active_rest = self.get_active_rest(force_data=force_data, force_on_demand=force_on_demand)
            if len(active_rest) > 0:
                active_rest = active_rest[0]
                active_rest.source_training_session_id = source_session_id
                if active_rest.get_total_exercises() > 0:
                    exercise_activity = [active_rest]
        if ice_cwi:
            cold_water_immersion = self.get_cold_water_immersion_modality()

            ice_session = self.get_ice_session_modality()
            ice = self.adjust_ice_session(ice_session, cold_water_immersion)
            return exercise_activity, ice, cold_water_immersion
        else:
            return exercise_activity, None, None

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

    def get_cold_water_immersion_modality(self):

        cold_water_immersion = None

        cwi_assigned = False
        for body_part, body_part_injury_risk in self.injury_risk_dict.items():

            base_date = self.event_date_time.date()

            if (self.is_lower_body_part(body_part.location)
                    and body_part_injury_risk.last_non_functional_overreaching_date == base_date
                    and not cwi_assigned):
                cold_water_immersion = ColdWaterImmersionModality(self.event_date_time)
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
                # ice = Ice(body_part_location=body_part.body_part_location, side=body_part.side)

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

    def get_ice_session_modality(self):

        ice_session = None

        ice_list = []

        minutes = []

        body_part_factory = BodyPartFactory()

        for body_part_side, body_part_injury_risk in self.aggregated_injury_risk_dict.items():
            base_date = self.event_date_time.date()
            if body_part_injury_risk.last_inflammation_date == base_date:
                ice = IceModality(body_part_location=body_part_side.body_part_location, side=body_part_side.side)
                goal = AthleteGoal("Care", 1, AthleteGoalType.pain)

                if body_part_factory.is_joint(body_part_side) or body_part_factory.is_ligament(body_part_side):
                    ice_list.append(ice)
                    minutes.append(10)
                else:
                    if body_part_injury_risk.last_sharp_date == self.event_date_time.date() and body_part_injury_risk.last_sharp_level >= 7:
                        ice_list.append(ice)
                        minutes.append(15)
                ice.goals.add(goal)

        if len(ice_list) > 0:
            ice_session = IceSessionModalities(self.event_date_time, minutes=min(minutes))
            ice_session.body_parts = ice_list

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
