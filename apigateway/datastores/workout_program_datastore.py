from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from utils import format_date, format_datetime

from models.workout_program import WorkoutProgramModule


class WorkoutProgramDatastore(object):
    def __init__(self, mongo_collection='workoutprogram'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.WorkoutProgramDatastore.get')
    def get(self, session_id=None, user_id=None, event_date_time=None, start_date_time=None, end_date_time=None):
        """
        user_id: uuid
        event_date_time: datetime.datetime
        start_date_time: datetime.datetime
        end_date_time: datetime.datetime
        """
        return self._query_mongodb(session_id, user_id, event_date_time, start_date_time, end_date_time)

    @xray_recorder.capture('datastore.WorkoutProgramDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.WorkoutProgramDatastore._query_mongodb')
    def _query_mongodb(self, session_id, user_id, event_date_time, start_date_time, end_date_time):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if session_id is not None:
            mongo_result = mongo_collection.find_one({'session_id': session_id})
            if mongo_result is not None:
                workout_program = WorkoutProgramModule.json_deserialise(mongo_result)
                return workout_program
            else:
                raise NoSuchEntityException(f'WorkoutProgram for session with the provided id not found')
        else:
            if user_id is None:
                raise InvalidSchemaException("Need to provide user_id or session_id")
            else:
                query = {'user_id': user_id}
                if event_date_time is not None:
                    event_date = format_date(event_date_time)
                    query['event_date'] = {'$regex': f'^{event_date}'}
                elif start_date_time is not None and end_date_time is not None:
                    query['event_date'] = {'$gte': format_datetime(start_date_time), '$lte': format_datetime(end_date_time)}
                else:
                    raise InvalidSchemaException("Need to provide either event_date_time or start_date_time and end_date_time when querying by user_id")
                mongo_cursor = mongo_collection.find(query)

                ret = []
                for workout_program in mongo_cursor:
                    ret.append(WorkoutProgramModule.json_deserialise(workout_program))
                return ret

    @xray_recorder.capture('datastore.WorkoutProgramDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'session_id': item['session_id']}
        mongo_collection.replace_one(query, item, upsert=True)
