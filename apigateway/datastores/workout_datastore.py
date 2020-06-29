from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from utils import format_date, format_datetime

from models.planned_exercise import PlannedWorkout


class WorkoutDatastore(object):
    def __init__(self, mongo_collection='workout'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.WorkoutDatastore.get')
    def get(self, program_id=None, event_date=None, start_date=None, end_date=None):
        """
        program_id: uuid
        event_date: datetime.date
        start_date: datetime.date
        end_date: datetime.date
        """
        return self._query_mongodb(program_id, event_date, start_date, end_date)

    @xray_recorder.capture('datastore.WorkoutDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.WorkoutDatastore._query_mongodb')
    def _query_mongodb(self, program_id, event_date, start_date, end_date):

        mongo_collection = get_mongo_collection(self.mongo_collection)
        if program_id is not None:
            mongo_result = mongo_collection.find_one({'program_id': program_id})
            if mongo_result is not None:
                session = PlannedWorkout.json_deserialise(mongo_result)
                return session
            else:
                raise NoSuchEntityException(f'Workout with the provided id not found')
        else:
            query = {}
            if event_date is not None:
                query['event_date'] = format_date(event_date)
            elif start_date is not None and end_date is not None:
                query['event_date'] = {'$gte': format_date(start_date), '$lte': format_date(end_date)}
            else:
                raise InvalidSchemaException("Need to provide either event_date or start_date and end_date when not querying by program_id")
            mongo_cursor = mongo_collection.find(query)

            ret = []
            for session in mongo_cursor:
                ret.append(PlannedWorkout.json_deserialise(session))
            return ret

    @xray_recorder.capture('datastore.WorkoutDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'program_id': item['program_id']}
        mongo_collection.replace_one(query, item, upsert=True)
