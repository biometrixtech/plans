from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from logic.soreness_and_injury import DailySoreness, BodyPart, BodyPartLocation
from models.daily_readiness import DailyReadiness
from utils import format_datetime
from exceptions import NoSuchEntityException


class DailyReadinessDatastore(object):
    mongo_collection = 'readiness'

    @xray_recorder.capture('datastore.DailyReadinessDatastore.get')
    def get(self, user_id):
        return self._query_mongodb(user_id)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.DailyReadinessDatastore._query_mongodb')
    def _query_mongodb(self, user_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': user_id}
        mongo_result = mongo_collection.find_one(query, sort=[('event_date', -1)])
        if mongo_result is not None:
            return DailyReadiness(
                                  event_date=mongo_result['event_date'],
                                  user_id=mongo_result['user_id'],
                                  soreness=mongo_result['soreness'],
                                  sleep_quality=mongo_result['sleep_quality'],
                                  readiness=mongo_result['readiness'])
        else:
            raise NoSuchEntityException("readiness survey does not exist for the user")

    @xray_recorder.capture('datastore.DailyReadinessDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()
        del item['sore_body_parts']
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': item['user_id'], 'event_date': format_datetime(item['event_date'])}
        mongo_collection.replace_one(query, item, upsert=True)
