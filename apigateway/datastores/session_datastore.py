from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from models.session import SessionType
from exceptions import NoSuchEntityException

class SessionDatastore(object):
    mongo_collection = 'dailyplan'

    @xray_recorder.capture('datastore.SessionDatastore.get')
    def get(self, user_id, event_date, session_type=None, session_id=None):
        sessions = self._get_sessions_from_mongo(user_id, event_date, session_type)

        if session_id is None:
            return sessions
        else:
            for session in sessions:
                if session.id == session_id:
                    return [session]
            raise NoSuchEntityException('No session could be found for the session_id: {} of session_type: {}'.format(session_id, SessionType(session_type)))

    @xray_recorder.capture('datastore.SessionDatastore.insert')
    def insert(self, item, user_id, event_date):
        session_type = item.session_type().value
        # session_type_name = _get_session_type_name(session_type, 'mongo')
        session = item.json_serialise()
        query = {"user_id": user_id, "date": event_date}
        mongo_collection = get_mongo_collection(self.mongo_collection)
        # mongo_collection.update_one(query, {'$push': {session_type_name: session}})
        mongo_collection.update_one(query, {'$push': {'training_sessions': session}})

    @xray_recorder.capture('datastore.SessionDatastore.update')
    def update(self, item, user_id, event_date):
        session_type = item.session_type().value
        session = item.json_serialise()
        # session_type_name = _get_session_type_name(session_type, 'mongo')
        query = {"user_id": user_id, "date": event_date}
        mongo_collection = get_mongo_collection(self.mongo_collection)
        # result = mongo_collection.update_one(query, {'$pull': {session_type_name: {'session_id': item.id}}})
        result = mongo_collection.update_one(query, {'$pull': {'training_sessions': {'session_id': item.id}}})
        if result.modified_count == 0:
            raise NoSuchEntityException('No session could be found for the session_id: {} of session_type: {}'.format(item.id, SessionType(session_type)))
        else:
            # mongo_collection.update_one(query, {'$push': {session_type_name: session}})
            mongo_collection.update_one(query, {'$push': {'training_sessions': session}})

    @xray_recorder.capture('datastore.SessionDatastore.delete')
    def delete(self, user_id, event_date, session_type, session_id):
        # session_type_name = _get_session_type_name(session_type, 'mongo')
        query = {"user_id": user_id, "date": event_date}
        mongo_collection = get_mongo_collection(self.mongo_collection)
        # mongo_collection.update_one(query, {'$pull': {session_type_name: {'session_id': session_id}}})
        mongo_collection.update_one(query, {'$pull': {'training_sessions': {'session_id': session_id}}})


    def _get_sessions_from_mongo(self, user_id, event_date, session_type=None):
        daily_plan_store = DailyPlanDatastore()
        plan = daily_plan_store.get(user_id=user_id,
                                    start_date=event_date,
                                    end_date=event_date)
        plan = plan[0]
        if session_type is None:
            external_sessions = []
            external_sessions.extend(getattr(plan, 'practice_sessions'))
            external_sessions.extend(getattr(plan, 'strength_conditioning_sessions'))
            external_sessions.extend(getattr(plan, 'games'))
            external_sessions.extend(getattr(plan, 'training_sessions'))
        else:
            # session_type_name = _get_session_type_name(session_type, 'object')
            # external_sessions = getattr(plan, session_type_name)
            external_sessions = getattr(plan, 'training_sessions')

        return external_sessions


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

