from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException

from models.training_load import CompletedSessionDetails


class CompletedSessionDetailsDatastore(object):
    def __init__(self, mongo_collection='completedsessiondetails'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.CompletedSessionDetailsDatastore.get')
    def get(self, user_id=None, workout_id=None, provider_id=None):
        """
        user_id: uuid
        workout_id: uuid/string
        provider_id: uuid/string
        """
        return self._query_mongodb(user_id, workout_id, provider_id)

    @xray_recorder.capture('datastore.CompletedSessionDetailsDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.CompletedSessionDetailsDatastore._query_mongodb')
    def _query_mongodb(self, user_id, workout_id, provider_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if user_id is not None:
            query = {'user_id': user_id}
            if workout_id is not None:
                query['workout_id'] = workout_id
            elif provider_id is not None:
                query['provider_id'] = provider_id
            mongo_cursor = mongo_collection.find(query)
        elif workout_id is not None:  # get the specific workout for all user profiles
            query = {'workout_id': workout_id}
            mongo_cursor = mongo_collection.find(query)
        elif provider_id is not None:  # get the all workouts for all user profiles for specific program
            query = {'provider_id': provider_id}
            mongo_cursor = mongo_collection.find(query)
        else:
            raise InvalidSchemaException("Need to provide either some combination of user_profile_id, program_id and workout_id")
        ret = []
        for session_details in mongo_cursor:
            ret.append(CompletedSessionDetails.json_deserialise(session_details))
        return ret

    @xray_recorder.capture('datastore.CompletedSessionDetailsDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': item['user_id'], 'workout_id': item['workout_id'], 'provider_id': item['workout_id']}
        mongo_collection.replace_one(query, item, upsert=True)
