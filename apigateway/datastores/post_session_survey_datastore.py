from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from logic.training import DailyPlan
from logic.session import SessionType, SessionFactory

class PostSessionSurveyDatastore(object):
    mongo_collection = 'dailyplan'

    def get(self, user_id=None, event_date=None):
        return self._query_mongodb(user_id, event_date)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.PostSessionSurveyDatastore._query_mongodb')
    def _query_mongodb(self, user_id, event_date):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        pass

    @xray_recorder.capture('datastore.PostSessionSurveyDatastore._put_mongodb')
    def _put_mongodb(self, item):
        daily_plan_store = DailyPlanDatastore()
        daily_plan = daily_plan_store.get(user_id=item.user_id,
                                          start_date=item.event_date,
                                          end_date=item.event_date)
        session_type = item.session_type
        if session_type == 0:
            session_type_name = 'practice_sessions'
        elif session_type == 1:
            session_type_name = 'strength_conditioning_sessions'
        elif session_type == 2:
            session_type_name = 'games'
        elif session_type == 3:
            session_type_name = 'tournaments'
        elif session_type == 4:
            session_type_name = 'bump_up_sessions'
        elif session_type == 5:
            session_type_name = 'corrective_sessions'

        plan = daily_plan[0]
        sessions = getattr(plan, session_type_name)
        if item.session_id is not None:
            for session in sessions:
                if session['session_id'] == item.session_id:
                    session['post_session_survey'] = item.survey.json_serialise()
                    break
        else:
            session = SessionFactory()
            session = session.create(SessionType(item.session_type))
            session_json = {'session_id': str(session.id),
                            'post_session_survey': item.survey.json_serialise()
                           }
            sessions.append(session_json)

        if session_type == 1:
            session_type_name = 'cross_training_sessions'
        elif session_type == 2:
            session_type_name = 'game_sessions'
        elif session_type == 3:
            session_type_name = 'tournament_sessions'
        
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {"user_id": item.user_id, "date": item.event_date}
        mongo_collection.update_one(query, {'$set': {session_type_name: sessions}})
