from fathomapi.utils.exceptions import NoSuchEntityException
from models.soreness import CompletedExercise
from models.functional_movement_activities import ActivityType


class ActivitiesProcessing(object):
    def __init__(self, data_store_collection):
        self.completed_exercise_datastore = data_store_collection.completed_exercise_datastore

    def save_completed_exercises(self, exercise_list, user_id, event_date):
        for exercise in exercise_list:
            self.completed_exercise_datastore.put(CompletedExercise(athlete_id=user_id, exercise_id=str(exercise),
                                                                    event_date=event_date))

    def mark_activity_completed(self, activity, completed_date_time, activity_type, user_id, completed_exercises):
        completed_activity = activity.__getattribute__(ActivityType(activity_type).name)
        if completed_activity is not None:
            completed_activity.completed = True
            completed_activity.completed_date_time = completed_date_time
            if ActivityType(activity_type) in [ActivityType.movement_integration_prep, ActivityType.active_rest, ActivityType.active_recovery]:
                self.save_completed_exercises(completed_exercises, user_id, completed_date_time)
        else:
            raise NoSuchEntityException()

    def mark_activity_started(self, activity, start_date_time, activity_type):
        started_activity = activity.__getattribute__(ActivityType(activity_type).name)
        if started_activity is not None:
            started_activity.start_date_time = start_date_time
        else:
            raise NoSuchEntityException()
