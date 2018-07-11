from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.daily_readiness import DailyReadiness
from utils import format_datetime


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
        mongo_result = mongo_collection.find_one(query, sort=[('date_time', -1)])
        print(mongo_result)
        return self.item_from_mongodb(mongo_result)

    @xray_recorder.capture('datastore.DailyReadinessDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = self.item_to_mongodb(item)
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': item['user_id'], 'date_time': format_datetime(item['date_time'])}
        mongo_collection.replace_one(query, item, upsert=True)

    @staticmethod
    def item_to_mongodb(dailyreadiness):
        item = {
            'date_time': dailyreadiness.date_time,
            'user_id': dailyreadiness.user_id,
            'soreness': dailyreadiness.get_soreness(),
            'sleep_quality': dailyreadiness.sleep_quality,
            'readiness': dailyreadiness.readiness,
        }
        return {k: v for k, v in item.items() if v}

    @staticmethod
    def item_from_mongodb(mongo_result):
        return DailyReadiness(
            user_id=mongo_result['user_id'],
            date_time=mongo_result['date_time'],
            soreness=mongo_result['soreness'],  # dailysoreness object array
            sleep_quality=mongo_result['sleep_quality'],
            readiness=mongo_result['readiness']
        )
