from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException

from models.planned_exercise import PlannedWorkoutLoad


class PlannedWorkoutLoadDatastore(object):
    def __init__(self, mongo_collection='plannedworkoutload'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.PlannedWorkoutLoadDatastore.get')
    def get(self, user_profile_id=None, program_module_id=None, program_id=None):
        """
        program_id: uuid
        event_date: datetime.date
        start_date: datetime.date
        end_date: datetime.date
        """
        return self._query_mongodb(user_profile_id, program_module_id, program_id)

    @xray_recorder.capture('datastore.PlannedWorkoutLoadDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.PlannedWorkoutLoadDatastore._query_mongodb')
    def _query_mongodb(self, user_profile_id, program_module_id, program_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if user_profile_id is not None:
            query = {'user_profile_id': user_profile_id}
            if program_module_id is not None:
                query['program_module_id'] = program_module_id
            elif program_id is not None:
                query['program_id'] = program_id
            mongo_cursor = mongo_collection.find(query)
        elif program_module_id is not None:  # get the specific workout for all user profiles
            query = {'program_module_id': program_module_id}
            mongo_cursor = mongo_collection.find(query)
        elif program_id is not None:  # get the all workouts for all user profiles for specific program
            query = {'program_id': program_id}
            mongo_cursor = mongo_collection.find(query)
        else:
            raise InvalidSchemaException("Need to provide either some combination of user_profile_id, program_id and program_module_id")
        ret = []
        for workout_load in mongo_cursor:
            ret.append(PlannedWorkoutLoad.json_deserialise(workout_load))
        return ret

    @xray_recorder.capture('datastore.PlannedWorkoutLoadDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_profile_id': item['user_profile_id'], 'program_id': item['program_id'], 'program_module_id': item['program_module_id']}
        mongo_collection.replace_one(query, item, upsert=True)
