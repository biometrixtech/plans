from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException
from utils import format_date, format_datetime

from models.symptom import Symptom


class SymptomDatastore(object):
    def __init__(self, mongo_collection='symptoms'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.SymptomDatastore.get')
    def get(self, user_id, event_date_time=None, start_date_time=None, end_date_time=None):
        """
        user_id: uuid
        event_date_time: datetime.datetime
        start_date_time: datetime.datetime
        end_date_time: datetime.datetime
        """
        return self._query_mongodb(user_id, event_date_time, start_date_time, end_date_time)

    @xray_recorder.capture('datastore.SymptomDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.SymptomDatastore._query_mongodb')
    def _query_mongodb(self, user_id, event_date_time, start_date_time, end_date_time):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if user_id is None:
            raise InvalidSchemaException("Need to provide user_id")
        else:
            query = {'user_id': user_id}
            if event_date_time is not None:
                event_date = format_date(event_date_time)
                query['reported_date_time'] = {'$regex': f'^{event_date}'}
            elif start_date_time is not None and end_date_time is not None:
                query['reported_date_time'] = {'$gte': format_datetime(start_date_time), '$lte': format_datetime(end_date_time)}
            elif start_date_time is not None:
                query['reported_date_time'] = {'$gte': format_datetime(start_date_time)}
            else:
                raise InvalidSchemaException("Need to provide either event_date_time or start_date_time and/or end_date_time")
            mongo_cursor = mongo_collection.find(query)

            ret = []
            for movement_prep in mongo_cursor:
                ret.append(Symptom.json_deserialise(movement_prep))
            return ret

    @xray_recorder.capture('datastore.SymptomDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'id': item['id']}
        mongo_collection.replace_one(query, item, upsert=True)
