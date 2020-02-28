from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from utils import format_date

from models.functional_movement_activities import ResponsiveRecovery


class ResponsiveRecovery(object):
    def __init__(self, mongo_collection='responsiverecovery'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.ResponsiveRecovery.get')
    def get(self, responsive_recovery_id=None, user_id=None, event_date_time=None):
        return self._query_mongodb(responsive_recovery_id, user_id, event_date_time)

    @xray_recorder.capture('datastore.ResponsiveRecovery.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.ResponsiveRecovery._query_mongodb')
    def _query_mongodb(self, responsive_recovery_id=None, user_id=None, event_date_time=None):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if responsive_recovery_id is not None:
            mongo_result = mongo_collection.find_one({'responsive_recovery_id': responsive_recovery_id})
            if mongo_result is not None:
                responsive_recovery = ResponsiveRecovery.json_deserialise(mongo_result)
                return responsive_recovery
            else:
                raise NoSuchEntityException(f'Responsive Recovery with the provided id not found')
        else:
            if user_id is not None and event_date_time is not None:
                event_date = format_date(event_date_time)
                query = {'user_id': user_id, 'created_date_time': {'$regex': f'^{event_date}'}}
                mongo_cursor = mongo_collection.find(query)

                ret = []
                for responsive_recovery in mongo_cursor:
                    ret.append(ResponsiveRecovery.json_deserialise(responsive_recovery))
                return ret
            else:
                raise InvalidSchemaException("Need to provide either id or user_id-event_date_time")

    @xray_recorder.capture('datastore.ResponsiveRecovery._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'responsive_recovery_id': item['responsive_recovery_id']}
        mongo_collection.replace_one(query, item, upsert=True)
