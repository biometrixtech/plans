from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.heart_rate import SessionHeartRate, HeartRateData


class HeartRateDatastore(object):
    mongo_collection = 'heartrate'

    @xray_recorder.capture('datastore.HeartRateDatastore.get')
    def get(self, user_id, start_date=None, end_date=None, session_id=None):
        return self._query_mongodb(user_id, start_date=None, end_date=None)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.HeartRateDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date, session_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if session_id is not None:
            query = {'user_id': user_id, 'session_id': session_id}
        else:
            if isinstance(user_id, list):
                query = {'user_id': {'$in': user_id}, 'event_date': {'$gte': start_date, '$lte': end_date}}
            else:
                query = {'user_id': user_id, 'event_date': {'$gte': start_date, '$lte': end_date}}

        mongo_cursor = mongo_collection.find(query)

        return [session_heart_rate_from_mongo(session_hr) for session_hr in mongo_cursor]

    @xray_recorder.capture('datastore.HeartRateDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.replace_one({"session_id": item['session_id']},
                                     item,
                                     upsert=True)

    def session_heart_rate_from_mongo(mongo_result):
        session_heart_rate = SessionHeartRate(user_id=mongo_result['user_id'], 
                                              session_id=mongo_result['session_id'],
                                              event_date=mongo_result['event_date'])
        session_heart_rate.hr_pre_workout = [HeartRateData(hr) for hr in mongo_result['hr_pre_workout']]
        session_heart_rate.hr_workout = [HeartRateData(hr) for hr in mongo_result['hr_workout']]
        session_heart_rate.hr_post_workout = [HeartRateData(hr) for hr in mongo_result['hr_post_workout']]

        return session_heart_rate