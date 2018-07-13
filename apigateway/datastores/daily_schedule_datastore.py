from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from datetime import date, datetime, timedelta
import models.session as session
import uuid


class DailyScheduleDatastore(object):
    @xray_recorder.capture('datastore.DailyScheduleDatastore.get')
    def get(self, user_id=None, target_date=date.today(), collection='training'):
        return self._query_mongodb(user_id, target_date, collection)

    @xray_recorder.capture('datastore.DailyScheduleDatastore.put')
    def put(self, items, collection):
        pass

    @xray_recorder.capture('datastore.DailyScheduleDatastore._query_mongodb')
    def _query_mongodb(self, user_id, target_date, collection):

        scheduled_sessions = []

        target_date = target_date.strftime('%Y-%m-%d')
        dt = datetime.strptime(target_date, '%Y-%m-%d')
        start = dt - timedelta(days=dt.weekday())
        # start = target_date - timedelta(days=dt.weekday())
        week_start = start.strftime('%Y-%m-%d')

        mongo_collection = get_mongo_collection(collection)
        query = {'user_id': user_id, 'week_start': week_start}

        schedule_cursor = mongo_collection.find(query)
        day_of_week = dt.weekday()

        for schedule in schedule_cursor:

            cross_training = schedule["cross_training"]
            cross_training_days_of_week = cross_training["days_of_week"]
            if cross_training_days_of_week is not None and len(cross_training_days_of_week) > 0:
                if day_of_week in cross_training_days_of_week:
                    cross_training_session = session.StrengthConditioningSession()
                    cross_training_session.day_of_week = session.DayOfWeek(day_of_week)
                    cross_training_session.date = target_date
                    cross_training_session.id = str(uuid.uuid4())
                    cross_training_session.duration_minutes = cross_training["duration"]
                    cross_training_session.description = ",".join(cross_training["activities"])
                    scheduled_sessions.append(cross_training_session)

            sports = schedule["sports"]
            for sport in sports:
                practice = sport["practice"]
                competition = sport["competition"]
                practice_days_of_week = practice["days_of_week"]
                if practice_days_of_week is not None and len(practice_days_of_week) > 0:
                    if day_of_week in practice_days_of_week:
                        practice_session = session.PracticeSession()
                        practice_session.day_of_week = session.DayOfWeek(day_of_week)
                        practice_session.date = target_date
                        practice_session.id = str(uuid.uuid4())
                        practice_session.duration_minutes = practice["duration"]
                        practice_session.description = "Practice (" + sport["sport"] + ")"
                        scheduled_sessions.append(practice_session)
                competition_days_of_week = competition["days_of_week"]
                if competition_days_of_week is not None and len(competition_days_of_week) > 0:
                    if day_of_week in competition_days_of_week:
                        game_session = session.Game()
                        game_session.day_of_week = session.DayOfWeek(day_of_week)
                        game_session.date = target_date
                        game_session.id = str(uuid.uuid4())
                        game_session.duration_minutes = 0  # TODO: look up from internal data
                        game_session.description = "Competition (" + sport["sport"] + ")"
                        scheduled_sessions.append(game_session)

        return scheduled_sessions

    @staticmethod
    def item_to_mongodb(dailytraining):
        pass


