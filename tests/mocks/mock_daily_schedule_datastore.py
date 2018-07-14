from datetime import date, datetime
import models.session as session
import uuid


class DailyScheduleDatastore(object):
    def get(self, user_id=None, target_date=date.today().strftime('%Y-%m-%d'), collection='training'):
        return self._query_mongodb(user_id, target_date, collection)

    def put(self, items, collection):
        pass

    def _query_mongodb(self, user_id, target_date, collection):

        if user_id == "morning_practice":

            scheduled_sessions = []

            practice_session = session.PracticeSession()
            practice_session.date = datetime.strftime(target_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            practice_session.id = str(uuid.uuid4())

            scheduled_sessions.append(practice_session)

            return scheduled_sessions
        elif user_id == "morning_practice_2":
            scheduled_sessions = []

            practice_session = session.PracticeSession()
            practice_session.date = datetime.strftime(target_date, "%Y-%m-%dT%H:%M:%S.%fZ")
            practice_session.id = str(uuid.uuid4())

            scheduled_sessions.append(practice_session)

            return scheduled_sessions
        else:
            scheduled_sessions = []

            return scheduled_sessions

    @staticmethod
    def item_to_mongodb(dailytraining):
        pass


