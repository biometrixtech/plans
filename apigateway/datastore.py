from abc import abstractmethod, ABCMeta
from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection


class Datastore(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, date_time=None, user_id=None, soreness=None, sleep_quality=None, readiness=None):
        pass


class MongodbDatastore(Datastore):

    def put(self, items, allow_patch=False):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item, allow_patch)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.MongodbDatastore.put')
    def _query_mongodb(self, user_id):
        mongo_collection = get_mongo_collection()
        query0 = {'user_id': user_id}
        query1 = {'soreness': 1, '_id': 0}
        mongo_result = list(mongo_collection.find(query0, query1).sort([('date_time', -1)]).limit(1))
        ret = []
        for soreness in mongo_result[0]['soreness']:
            if soreness['severity'] > 1:
                ret.append(soreness['body_part'])

        return ret

    @xray_recorder.capture('datastore.MongodbDatastore.put')
    def _put_mongodb(self, item, allow_patch=False):
        item = self.item_to_mongodb(item)
        mongo_collection = get_mongo_collection()
        query = {'user_id': item['user_id'], 'date_time': item['date_time']}
        mongo_collection.replace_one(query, item, upsert=True)


    @staticmethod
    @abstractmethod
    def item_to_mongodb(item):
        pass


class DailyReadinessDatastore(MongodbDatastore):
    @xray_recorder.capture('datastore.DailyReadinessDatastore.get')
    def get(self, date_time=None, user_id=None, soreness=None, sleep_quality=None, readiness=None):
        return self._query_mongodb(user_id)

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
