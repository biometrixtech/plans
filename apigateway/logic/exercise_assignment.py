from models.functional_movement_modalities import MovementIntegrationPrepModality, ActiveRestAfterTraining, ActiveRecoveryModality, ColdWaterImmersion, Ice, IceSession
from models.body_parts import BodyPartLocation, BodyPartFactory
from models.goal import AthleteGoalType, AthleteGoal


class ExerciseAssignment(object):

    def __init__(self, injury_risk_dict, exercise_library_datastore, completed_exercise_datastore, event_date_time, relative_load_level=3, aggregated_injury_risk_dict=None):
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
        movement_integration_prep.set_plan_dosage()
        movement_integration_prep.set_exercise_dosage_ranking()
        movement_integration_prep.aggregate_dosages()
        movement_integration_prep.set_winners()
        movement_integration_prep.scale_all_active_time()
        movement_integration_prep.reconcile_default_plan_with_active_time()
    
        return [movement_integration_prep]

    def get_active_rest(self, force_data=False, force_on_demand=True):
        # get activity
        active_rest = ActiveRestAfterTraining(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level, force_on_demand=force_on_demand)
        active_rest.fill_exercises(self.exercise_library, self.injury_risk_dict)
        active_rest.set_plan_dosage()
        active_rest.set_exercise_dosage_ranking()
        active_rest.aggregate_dosages()
        active_rest.set_winners()
        active_rest.scale_all_active_time()
        active_rest.reconcile_default_plan_with_active_time()
    
        return [active_rest]

    def get_responsive_recovery(self, source_session_id, force_data=False, force_on_demand=True, ice_cwi=True):
        active_recovery = ActiveRecoveryModality(self.event_date_time)
        active_recovery.fill_exercises(self.exercise_library, self.injury_risk_dict, high_intensity_session=self.high_intensity_session)
        active_recovery.set_plan_dosage()
        active_recovery.set_exercise_dosage_ranking()
        active_recovery.aggregate_dosages()
        active_recovery.set_winners()
        active_recovery.scale_all_active_time()
        active_recovery.reconcile_default_plan_with_active_time()
        active_recovery.source_training_session_id = source_session_id
        if active_recovery.get_total_exercises() > 0:
            exercise_activity = [active_recovery]
        else:
            active_rest = self.get_active_rest(force_data=force_data, force_on_demand=force_on_demand)[0]
            active_rest.source_training_session_id = source_session_id
            if active_rest.get_total_exercises() == 0:
                exercise_activity = []
            else:
                exercise_activity = [active_rest]
        if ice_cwi:
            cold_water_immersion = self.get_cold_water_immersion()

            ice_session = self.get_ice_session()
            ice = self.adjust_ice_session(ice_session, cold_water_immersion)
            return exercise_activity, ice, cold_water_immersion
        else:
            return  exercise_activity, None, None

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
                ice = Ice(body_part_location=body_part_side.body_part_location, side=body_part_side.side)
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
            ice_session = IceSession(self.event_date_time, minutes=min(minutes))
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