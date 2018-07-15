from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from models.daily_plan import DailyPlan
from models.session import SessionType, SessionFactory

class SessionDatastore(object):
    mongo_collection = 'dailyplan'

    def create(self, user_id, event_date, session_type, description=""):
        daily_plan_store = DailyPlanDatastore()
        daily_plan = daily_plan_store.get(user_id=user_id,
                                          start_date=event_date,
                                          end_date=event_date)
        session_type = session_type
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
        sessions = [s.json_serialise() for s in sessions]
        session = SessionFactory()
        session = session.create(SessionType(session_type))
        session_json = session.json_serialise()
        session_json['description'] = description
        sessions.append(session_json)

        if session_type == 1:
            session_type_name = 'cross_training_sessions'
        elif session_type == 2:
            session_type_name = 'game_sessions'
        elif session_type == 3:
            session_type_name = 'tournament_sessions'

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {"user_id": user_id, "date": event_date}
        mongo_collection.update_one(query, {'$set': {session_type_name: sessions}})


    def delete(self, user_id, event_date, session_type, session_id):
        daily_plan_store = DailyPlanDatastore()
        daily_plan = daily_plan_store.get(user_id=user_id,
                                          start_date=event_date,
                                          end_date=event_date)
        session_type = session_type
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
        sessions = [s.json_serialise() for s in sessions]
        for session in sessions:
            if session['session_id'] == session_id:
                sessions.remove(session)
                break

        if session_type == 1:
            session_type_name = 'cross_training_sessions'
        elif session_type == 2:
            session_type_name = 'game_sessions'
        elif session_type == 3:
            session_type_name = 'tournament_sessions'

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {"user_id": user_id, "date": event_date}
        mongo_collection.update_one(query, {'$set': {session_type_name: sessions}})

   