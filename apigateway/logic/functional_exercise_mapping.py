from models.functional_movement_modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining, WarmUp, CoolDown, FunctionalStrength
from models.functional_movement_activities import MovementPrep, MobilityWOD, ResponsiveRecovery, MovementIntegrationPrep, ActiveRest


class ExerciseAssignmentCalculator(object):

    def __init__(self, injury_risk_dict, exercise_library_datastore, completed_exercise_datastore, event_date_time, relative_load_level=3):

        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        self.injury_risk_dict = injury_risk_dict
        self.event_date_time = event_date_time
        self.relative_load_level = relative_load_level

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
        movement_integration_prep.fill_exercises(self.exercise_library, self.injury_risk_dict)
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

        # determine if we need active rest

        # determine if we need active recovery

        # determine if we need ice, cwi

        return responsive_recovery
