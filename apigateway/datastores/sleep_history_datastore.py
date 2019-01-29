from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.sleep_data import DailySleepData, SleepEvent


class SleepHistoryDatastore(object):
    mongo_collection = 'sleephistory'

    @xray_recorder.capture('datastore.SleepHistoryDatastore.get')
    def get(self, user_id, start_date=None, end_date=None):
        if end_date is None:
            end_date = start_date
        return self._query_mongodb(user_id, start_date=start_date, end_date=end_date)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.SleepHistoryDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if isinstance(user_id, list):
            query = {'user_id': {'$in': user_id}, 'event_date': {'$gte': start_date, '$lte': end_date}}
        else:
            query = {'user_id': user_id, 'event_date': {'$gte': start_date, '$lte': end_date}}

        mongo_cursor = mongo_collection.find(query)

        return [self.sleep_data_from_mongo(daily_sleep) for daily_sleep in mongo_cursor]

    @xray_recorder.capture('datastore.SleepHistoryDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.replace_one({"user_id": item['user_id'], "event_date": item['event_date']},
                                     item,
                                     upsert=True)

    def sleep_data_from_mongo(self, mongo_result):
        daily_sleep_data = DailySleepData(user_id=mongo_result['user_id'],
                                          event_date=mongo_result['event_date'])
        daily_sleep_data.sleep_events = [SleepEvent(se) for se in mongo_result['sleep_events']]

        return daily_sleep_data