from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.delayed_onset_muscle_soreness import DelayedOnsetMuscleSoreness
from utils import format_datetime
from fathomapi.utils.exceptions import InvalidSchemaException


class ClearedSorenessDatastore(object):
    def __init__(self, mongo_collection='clearedsoreness'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.ClearedSorenessDatastore.get')
    def get(self, user_id, start_date_time, end_date_time):
        return self._query_mongodb(user_id, start_date_time, end_date_time)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    # def delete(self, items=None, user_id=None, start_date_time=None, end_date_time=None):
    #     if items is None and user_id is None:
    #         raise InvalidSchemaException("Need to provide one of items and user_id")
    #     if items is not None:
    #         if not isinstance(items, list):
    #             items = [items]
    #         for item in items:
    #             self._delete_mongodb(item=item, user_id=user_id, start_date_time=start_date_time, end_date_time=end_date_time)
    #     else:
    #         self._delete_mongodb(item=items, user_id=user_id, start_date_time=start_date_time, end_date_time=end_date_time)

    @xray_recorder.capture('datastore.ClearedSorenessDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date_time, end_date_time):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        ret = []
        query = {}
        if isinstance(user_id, list):
            query['user_id'] = {'$in': user_id}
        else:
            query['user_id'] = user_id
        if start_date_time is not None:
            query['first_reported_date_time'] = {'$gte': start_date_time}
        if end_date_time is not None:
            query['cleared_date_time'] = {'$lte': end_date_time}

        mongo_cursor = mongo_collection.find(query)

        for mongo_result in mongo_cursor:
            doms = DelayedOnsetMuscleSoreness.json_deserialise(mongo_result)
            ret.append(doms)

        return ret

    @xray_recorder.capture('datastore.ClearedSorenessDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise(cleared=True)

        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.insert_one(item)

    # @xray_recorder.capture('datastore.ClearedSorenessDatastore._delete_mongodb')
    # def _delete_mongodb(self, item, user_id, start_date_time, end_date_time):
    #     mongo_collection = get_mongo_collection(self.mongo_collection)
    #     query = {}
    #     if item is not None:
    #         query['user_id'] = item.user_id
    #         query['event_date'] = format_datetime(item.event_date)
    #     else:
    #         if isinstance(user_id, list):
    #             query['user_id'] = {'$in': user_id}
    #         else:
    #             query['user_id'] = user_id
    #         if start_date_time is not None and end_date_time is not None:
    #             query['event_date'] = {'$gte': start_date_time, '$lte': end_date_time}

    #     if len(query) > 0:
    #         mongo_collection.delete_many(query)
