# from abc import abstractmethod, ABCMeta
from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection


class DailyReadinessDatastore(object):
    @xray_recorder.capture('datastore.DailyReadinessDatastore.get')
    def get(self, date_time=None, user_id=None, collection=None):
        return self._query_mongodb(user_id, collection)

    def put(self, items, collection):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item, collection)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.DailyReadinessDatastore._query_mongodb')
    def _query_mongodb(self, user_id, collection):
        mongo_collection = get_mongo_collection(collection)
        query0 = {'user_id': user_id}
        query1 = {'soreness': 1, '_id': 0}
        mongo_result = list(mongo_collection.find(query0, query1).sort([('date_time', -1)]).limit(1))
        ret = []
        for soreness in mongo_result[0]['soreness']:
            if soreness['severity'] > 1:
                ret.append(soreness['body_part'])

        return ret

    @xray_recorder.capture('datastore.DailyReadinessDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        item = self.item_to_mongodb(item)
        mongo_collection = get_mongo_collection(collection)
        query = {'user_id': item['user_id'], 'date_time': item['date_time']}
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


class WeeklyCrossTrainingDatastore(object):
    # @xray_recorder.capture('datastore.WeeklyCrossTrainingDatastore.get')
    def get(self, user_id=None, week_start=None, collection=None):
        return self._query_mongodb(user_id, week_start, collection)

    # @xray_recorder.capture('datastore.WeeklyCrossTrainingDatastore.put')
    def put(self, items, collection):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item, collection)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.WeeklyCrossTrainingDatastore._query_mongodb')
    def _query_mongodb(self, user_id, week_start, collection):
        mongo_collection = get_mongo_collection(collection)
        query = {'user_id': user_id, 'week_start': week_start}
        return list(mongo_collection.find(query))

    @xray_recorder.capture('datastore.WeeklyCrossTrainingDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        item = self.item_to_mongodb(item)
        mongo_collection = get_mongo_collection(collection)
        query = {'user_id': item['user_id'], 'week_start': item['week_start']}
        record = self.get(item['user_id'], item['week_start'], collection)
        if len(record) == 0:
            mongo_collection.insert_one(item)
        elif len(record) == 1:
            mongo_collection.update_one(query, {'$set': {'cross_training': item['cross_training']}}, upsert=False)

    @staticmethod
    def item_to_mongodb(weeklytraining):
        item = {
            'user_id': weeklytraining.user_id,
            'week_start': weeklytraining.week_start,
            'cross_training': weeklytraining.cross_training,
            'sports': weeklytraining.sports,
        }
        return item



class WeeklyTrainingDatastore(object):
    # @xray_recorder.capture('datastore.WeeklyCrossTrainingDatastore.get')
    def get(self, user_id=None, week_start=None, collection=None):
        return self._query_mongodb(user_id, week_start, collection)

    # @xray_recorder.capture('datastore.WeeklyCrossTrainingDatastore.put')
    def put(self, items, collection):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item, collection)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.WeeklyTrainingDatastore._query_mongodb')
    def _query_mongodb(self, user_id, week_start, collection):
        mongo_collection = get_mongo_collection(collection)
        query = {'user_id': user_id, 'week_start': week_start}
        return list(mongo_collection.find(query))

    @xray_recorder.capture('datastore.WeeklyTrainingDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        item = self.item_to_mongodb(item)
        mongo_collection = get_mongo_collection(collection)
        query = {'user_id': item['user_id'], 'week_start': item['week_start']}
        record = self.get(item['user_id'], item['week_start'], collection)
        if len(record) == 0:
            mongo_collection.insert_one(item)
        elif len(record) == 1:
            mongo_collection.update_one(query, {'$set': {'sports': item['sports']}}, upsert=False)

    @staticmethod
    def item_to_mongodb(weeklytraining):
        item = {
            'user_id': weeklytraining.user_id,
            'week_start': weeklytraining.week_start,
            'cross_training': weeklytraining.cross_training,
            'sports': weeklytraining.sports,
        }
        return item


class DailyPlanDatastore(object):
    def get(self, user_id=None, date=None, collection=None):
        return self._query_mongodb(user_id, date, collection)

    def put(self, items, collection):
        pass

    @xray_recorder.capture('datastore.DailyPlanDatastore._query_mongodb')
    def _query_mongodb(self, user_id, date, collection):
        mongo_collection = get_mongo_collection(collection)
        # output = list(mongo_collection.find({'user_id': user_id, 'date': date}).limit(1))
        output = list(mongo_collection.find({'userId': user_id, 'date': date}, {'_id': 0}).limit(1))
        if len(output) == 1:
            return output[0]
            # return self.item_to_output(output[0])
        else:
            return None

    @xray_recorder.capture('datastore.DailyPlanDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        pass

    @staticmethod
    def item_to_oputput(dailyplan):
        item = {
            'user_id': dailyplan['user_id'],
            'date': dailyplan['date'],
            'practice': dailyplan['practice_sessions'],
            'recovery_am': dailyplan['recovery_am'],
            'recovery_pm': dailyplan['recovery_pm']
        }
        return item

