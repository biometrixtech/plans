from models.soreness import CompletedExercise
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore


class ModalitiesProcessing(object):
    def __init__(self, data_store_collection):
        self.completed_exercise_datastore = data_store_collection.completed_exercise_datastore
        self.daily_plan_datastore = data_store_collection.daily_plan_datastore

    def save_completed_exercises(self, exercise_list, user_id, event_date):
        for exercise in exercise_list:
            self.completed_exercise_datastore.put(CompletedExercise(athlete_id=user_id, exercise_id=exercise,
                                                                    event_date=event_date))

    def mark_modality_completed(self, plan_event_day, recovery_event_date, recovery_type, user_id, completed_exercises):
        save_exercises = True
        plan = self.daily_plan_datastore.get(user_id=user_id, start_date=plan_event_day, end_date=plan_event_day)[0]
        modalities = [m for m in plan.modalities if m.type.value == recovery_type and not m.completed]
        if len(modalities) > 0:
            modality = modalities[0]
            modality.completed = True
            modality.completed_date_time = recovery_event_date
        else:
            save_exercises = False
        self.daily_plan_datastore.put(plan)
        if save_exercises:
            self.save_completed_exercises(completed_exercises, user_id, recovery_event_date)
        return plan
