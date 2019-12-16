from models.modality import ActiveRestBeforeTraining, ActiveRestAfterTraining, WarmUp, CoolDown, FunctionalStrength


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
                functional_strength = FunctionalStrength(self.event_date_time)  # TODO: revert this
                functional_strength.display_image = 'dynamic_flexibility'
                # functional_strength.goals = active_rest.goals
                functional_strength.exercise_phases = active_rest.exercise_phases[1:3]
                functional_strength.set_plan_dosage()
                functional_strength.set_exercise_dosage_ranking()
                functional_strength.aggregate_dosages()
                functional_strength.set_winners()
                functional_strength.scale_all_active_time()
                functional_strength.reconcile_default_plan_with_active_time()
                return [active_rest, functional_strength]
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
                cool_down = CoolDown(self.event_date_time)  # TODO: revert this
                cool_down.display_image = 'dynamic_flexibility'
                cool_down.goals = active_rest.goals
                cool_down.exercise_phases = active_rest.exercise_phases[1:3]
                return [active_rest, cool_down]
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
