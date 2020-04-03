from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from utils import format_date

from models.functional_movement_activities import MovementPrep


class MovementPrepDatastore(object):
    def __init__(self, mongo_collection='movementprep'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.MovementPrepDatastore.get')
    def get(self, movement_prep_id=None, user_id=None, event_date_time=None):
        """
        :param movement_prep_id: uuid
        :param user_id: uuid
        :param event_date_time: datetime.datetime
        :return:
        """
        return self._query_mongodb(movement_prep_id, user_id, event_date_time)

    @xray_recorder.capture('datastore.MovementPrepDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.MovementPrepDatastore._query_mongodb')
    def _query_mongodb(self, movement_prep_id=None, user_id=None, event_date_time=None):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if movement_prep_id is not None:
            mongo_result = mongo_collection.find_one({'movement_prep_id': movement_prep_id})
            if mongo_result is not None:
                movement_prep = MovementPrep.json_deserialise(mongo_result)
                return movement_prep
            else:
                raise NoSuchEntityException(f'Movement Prep with the provided id not found')
        else:
            if user_id is not None and event_date_time is not None:
                event_date = format_date(event_date_time)
                query = {'user_id': user_id, 'created_date_time': {'$regex': f'^{event_date}'}}
                mongo_cursor = mongo_collection.find(query)

                ret = []
                for movement_prep in mongo_cursor:
                    ret.append(MovementPrep.json_deserialise(movement_prep))
                return ret
            else:
                raise InvalidSchemaException("Need to provide either movement_prep_id or user_id-event_date_time")

    @xray_recorder.capture('datastore.MovementPrepDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'movement_prep_id': item['movement_prep_id']}
        mongo_collection.replace_one(query, item, upsert=True)
