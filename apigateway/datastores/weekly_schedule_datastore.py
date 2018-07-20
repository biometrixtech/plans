from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.weekly_schedule import WeeklySchedule


class WeeklyScheduleDatastore(object):
    mongo_collection = get_mongo_collection('trainingschedule')
    @xray_recorder.capture('datastore.WeeklyScheduleDatastore.get')
    def get(self, user_id=None, week_start=None):
        return self._query_mongodb(user_id, week_start)

    @xray_recorder.capture('datastore.WeeklyScheduleDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.WeeklyScheduleDatastore._query_mongodb')
    def _query_mongodb(self, user_id, week_start):
        query = {'user_id': user_id, 'week_start': week_start}
        cursor = self.mongo_collection.find(query)
        ret = []
        for schedule in cursor:
            weekly_schedule = WeeklySchedule(user_id=schedule['user_id'],
                                             week_start=schedule['week_start'],
                                             cross_training=schedule['cross_training'],
                                             sports=schedule['sports'])
            ret.append(weekly_schedule)
        return ret

    @staticmethod
    def item_to_mongodb(weeklytraining):
        item = {
            'user_id': weeklytraining.user_id,
            'week_start': weeklytraining.week_start,
            'cross_training': weeklytraining.cross_training,
            'sports': weeklytraining.sports,
        }
        return item


class WeeklyCrossTrainingDatastore(WeeklyScheduleDatastore):
    @xray_recorder.capture('datastore.WeeklyCrossTrainingDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = self.item_to_mongodb(item)
        query = {'user_id': item['user_id'], 'week_start': item['week_start']}
        record = self.get(item['user_id'], item['week_start'])
        if len(record) == 0:
            self.mongo_collection.insert_one(item)
        elif len(record) == 1:
            self.mongo_collection.update_one(query, {'$set': {'cross_training': item['cross_training']}}, upsert=False)


class WeeklyTrainingDatastore(WeeklyScheduleDatastore):
    @xray_recorder.capture('datastore.WeeklyTrainingDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = self.item_to_mongodb(item)
        query = {'user_id': item['user_id'], 'week_start': item['week_start']}
        record = self.get(item['user_id'], item['week_start'])
        if len(record) == 0:
            self.mongo_collection.insert_one(item)
        elif len(record) == 1:
            self.mongo_collection.update_one(query, {'$set': {'sports': item['sports']}}, upsert=False)
