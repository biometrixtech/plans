from models.functional_movement_modalities import ActiveRestBeforeTraining, ActiveRestAfterTraining


class ExerciseAssignmentCalculator(object):

    def __init__(self, injury_hist_dict, exercise_library_datastore, completed_exercise_datastore, event_date_time):

        self.exercise_library_datastore = exercise_library_datastore
        self.completed_exercise_datastore = completed_exercise_datastore
        self.exercise_library = self.exercise_library_datastore.get()
        self.injury_hist_dict = injury_hist_dict
        self.event_date_time = event_date_time

    def get_pre_active_rest(self, force_data=False):

        if len(self.injury_hist_dict) > 0 or force_data:
            active_rest = ActiveRestBeforeTraining(self.event_date_time, force_data)
            active_rest.fill_exercises(self.exercise_library, self.injury_hist_dict)
            #TODO : figure this out
            #active_rest.set_plan_dosage(self.soreness_list, self.muscular_strain_high)
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            active_rest.set_winners()
            active_rest.scale_all_active_time()
            active_rest.reconcile_default_plan_with_active_time()
            if active_rest.get_total_exercises() > 0:
                return [active_rest]
        return []

    def get_post_active_rest(self, force_data=False):

        if len(self.injury_hist_dict) > 0 or force_data:
            active_rest = ActiveRestAfterTraining(self.event_date_time, force_data)
            active_rest.fill_exercises(self.exercise_library, self.injury_hist_dict)
            #TODO : figure this out
            #active_rest.set_plan_dosage(self.soreness_list, self.muscular_strain_high)
            active_rest.set_exercise_dosage_ranking()
            active_rest.aggregate_dosages()
            active_rest.set_winners()
            active_rest.scale_all_active_time()
            active_rest.reconcile_default_plan_with_active_time()
            if active_rest.get_total_exercises() > 0:
                return [active_rest]
        return []


