# import datetime
from config import get_mongo_collection
import datetime
from models.daily_readiness import DailyReadiness
from models.soreness import CompletedExercise
from logic.stats_processing import StatsProcessing
from logic.training_plan_management import TrainingPlanManager
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from datastores.datastore_collection import DatastoreCollection
from utils import format_datetime, format_date


class Persona(object):
    def __init__(self, user_id):
        self.user_id = user_id
        self.soreness_history = None
        self.session_history = None
        self.daily_plan = None

    def create_history(self, days):
        self.clear_user()
        event_date = datetime.datetime.now() - datetime.timedelta(days=days)
        for i in range(days):
            date_time = format_datetime(event_date)
            today_date = format_date(event_date)
            soreness = []
            for body_part in self.soreness_history:
                if body_part['severity'][i] is not None:
                    soreness.append({'body_part': body_part['body_part'],
                                     'side': body_part['side'],
                                     'pain': body_part['pain'],
                                     'severity': body_part['severity'][i]})

            if len(soreness) > 0:
                readiness_data = {'date_time': date_time,
                                  'soreness': soreness}
                self.create_readiness(readiness_data)
                self.create_plan(today_date)
                exercise_list = [ex.exercise.id for ex in self.daily_plan.pre_recovery.inhibit_exercises]
                self.complete_exercises(exercise_list, format_datetime(event_date + datetime.timedelta(hours=1)))
                print(today_date)
            self.update_stats(format_date(event_date))
            event_date = event_date + datetime.timedelta(days=1)

        self.update_stats(format_date(event_date))

    def clear_user(self):
        readiness = get_mongo_collection('dailyreadiness')
        daily_plan = get_mongo_collection('dailyplan')
        stats = get_mongo_collection('athletestats')
        exercises = get_mongo_collection('completedexercises')

        readiness.delete_many({"user_id": self.user_id})
        daily_plan.delete_many({"user_id": self.user_id})
        exercises.delete_many({"athlete_id": self.user_id})
        stats.delete_one({"athlete_id": self.user_id})

    def create_plan(self, event_date):
        plan_manager = TrainingPlanManager(self.user_id, DatastoreCollection())
        self.daily_plan = plan_manager.create_daily_plan(event_date=event_date)


    def update_stats(self, event_date):
        StatsProcessing(self.user_id, event_date=event_date, datastore_collection=DatastoreCollection()).process_athlete_stats()

    def create_readiness(self, data):
        daily_readiness = DailyReadiness(
                                        user_id=self.user_id,
                                        event_date=data['date_time'],
                                        soreness=data['soreness'],  # dailysoreness object array
                                        sleep_quality=None,
                                        readiness=None
                                    )
        store = DailyReadinessDatastore()
        store.put(daily_readiness)

    def complete_exercises(self, exercise_list, event_date):
        exercise_store = CompletedExerciseDatastore()

        for exercise in exercise_list:
            exercise_store.put(CompletedExercise(athlete_id=self.user_id,
                                                 exercise_id=exercise,
                                                 event_date=event_date))
