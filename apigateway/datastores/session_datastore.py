from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from models.session import SessionType, SessionFactory
from exceptions import NoSuchEntityException

class SessionDatastore(object):
    mongo_collection = 'dailyplan'

    def get(self, user_id, event_date, session_type, session_id=None):
        sessions = _get_sessions_from_mongo(self, user_id, event_date, session_type)
        if session_id is None:
            return sessions
        else:
            for session in sessions:
                if session.id == session_id:
                    return [session]
            raise NoSuchEntityException('No session could be found for the session_id: {} of session_type: {}'.format(session_id, SessionType(session_type)))


    def insert(self, item, user_id, event_date):
        session_type = item.session_type().value
        session_type_name = _get_session_type_name(session_type, 'mongo')
        session = item.json_serialise()
        query = {"user_id": user_id, "date": event_date}
        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.update_one(query, {'$push': {session_type_name: session}})

    def update(self, item, user_id, event_date):
        session_type = item.session_type().value
        session = item.json_serialise()
        session_type_name = _get_session_type_name(session_type, 'mongo')
        query = {"user_id": user_id, "date": event_date}
        mongo_collection = get_mongo_collection(self.mongo_collection)
        result = mongo_collection.update_one(query, {'$pull': {session_type_name: {'session_id': item.id}}})
        if result.modified_count == 0:
            raise NoSuchEntityException('No session could be found for the session_id: {} of session_type: {}'.format(session_id, SessionType(session_type)))
        else:
            mongo_collection.update_one(query, {'$push': {session_type_name: session}})


    def delete(self, user_id, event_date, session_type, session_id):
        session_type_name = _get_session_type_name(session_type, 'mongo')
        query = {"user_id": user_id, "date": event_date}
        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.update_one(query, {'$pull': {session_type_name: {'session_id': session_id}}})


    def upsert(self, user_id, event_date, session_type, item=None, data=None):
        if item is None:
            session = _create_session(user_id, session_type, data)
            self.insert(session, user_id, event_date)
        else:
            if data is None:
                self.insert(item, user_id, event_date)
            else:
                update_item(item, data)
                self.update(item, user_id, event_date)


    def _get_sessions_from_mongo(self, user_id, event_date, session_type):
        daily_plan_store = DailyPlanDatastore()
        daily_plan = daily_plan_store.get(user_id=user_id,
                                          start_date=event_date,
                                          end_date=event_date)
        plan = daily_plan[0]
        session_type_name = _get_session_type_name(session_type, 'object')
        sessions = getattr(plan, session_type_name)
        return sessions

    def _update_sessions_mongo(self, user_id, event_date, session_type, sessions):
        session_type_name = _get_session_type_name(session_type, 'mongo')
        query = {"user_id": user_id, "date": event_date}
        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.update_one(query, {'$set': {session_type_name: sessions}})

def _create_session(user_id, session_type, data):
    session = SessionFactory()
    session = session.create(SessionType(session_type))
    for key, value in data.items():
        setattr(session, key, value)
    return session

def _update_session(session, data):
    for key, value in data.items():
        setattr(session, key, value)


def _get_session_type_name(session_type, destination):
    if destination == 'mongo':
        if session_type == 0:
            session_type_name = 'practice_sessions'
        elif session_type == 1:
            session_type_name = 'cross_training_sessions'
        elif session_type == 2:
            session_type_name = 'game_sessions'
        elif session_type == 3:
            session_type_name = 'tournament_sessions'
        elif session_type == 4:
            session_type_name = 'bump_up_sessions'
        elif session_type == 5:
            session_type_name = 'corrective_sessions'
    elif destination == 'object':
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

    return session_type_name
