from models.functional_movement_modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining, WarmUp, CoolDown, FunctionalStrength


class ExerciseAssignmentCalculator(object):

    def __init__(self, injury_risk_dict, exercise_library_datastore, completed_exercise_datastore, event_date_time, relative_load_level=3):

        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        self.injury_risk_dict = injury_risk_dict
        self.event_date_time = event_date_time
        self.relative_load_level = relative_load_level

    def get_pre_active_rest(self, force_data=False):

        if len(self.injury_risk_dict) > 0 or force_data:
            active_rest = ActiveRestBeforeTraining(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level)
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

    def get_post_active_rest(self, force_data=False):

        if len(self.injury_risk_dict) > 0 or force_data:
            active_rest = ActiveRestAfterTraining(self.event_date_time, force_data=force_data, relative_load_level=self.relative_load_level)
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
        warm_up = WarmUp()
        warm_up.fill_exercises(self.exercise_library, {})
        return warm_up

    def get_cool_down(self):
        cool_down = CoolDown()
        cool_down.fill_exercises(self.exercise_library, {})
        return cool_down

    def get_functional_strength(self):
        functional_strength = FunctionalStrength()
        functional_strength.fill_exercises(self.exercise_library, {})
        return functional_strength
