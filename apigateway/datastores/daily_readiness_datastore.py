from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.daily_readiness import DailyReadiness
from utils import format_datetime, parse_datetime
from fathomapi.utils.exceptions import NoSuchEntityException


class DailyReadinessDatastore(object):
    mongo_collection = 'dailyreadiness'

    @xray_recorder.capture('datastore.DailyReadinessDatastore.get')
    def get(self, user_id, start_date=None, end_date=None, last_only=True):
        return self._query_mongodb(user_id, start_date, end_date, last_only)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.DailyReadinessDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date_time, end_date_time, last_only):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if start_date_time is None and end_date_time is None:
            if isinstance(user_id, list):
                query = {'user_id': {'$in': user_id}}
            else:
                query = {'user_id': user_id}
        else:
            start_date_time = format_datetime(start_date_time)
            end_date_time = format_datetime(end_date_time)
            if isinstance(user_id, list):
                query = {'user_id': {'$in': user_id}, 'event_date': {'$gte': start_date_time, '$lte': end_date_time}}
            else:
                query = {'user_id': user_id, 'event_date': {'$gte': start_date_time, '$lte': end_date_time}}
        if last_only:
            mongo_result = mongo_collection.find_one(query, sort=[('event_date', -1)])

            if mongo_result is not None:
                return [DailyReadiness(
                                      event_date=mongo_result['event_date'],
                                      user_id=mongo_result['user_id'],
                                      soreness=mongo_result['soreness'],
                                      sleep_quality=mongo_result['sleep_quality'],
                                      readiness=mongo_result['readiness'],
                                      wants_functional_strength=mongo_result.get('wants_functional_strength', False)
                                    )]

            else:
                raise NoSuchEntityException("readiness survey does not exist for the user")
        else:
            mongo_cursor = mongo_collection.find(query)
            ret = []

            for mongo_result in mongo_cursor:
                daily_readiness = DailyReadiness(
                    event_date=mongo_result['event_date'],
                    user_id=mongo_result['user_id'],
                    soreness=mongo_result['soreness'],
                    sleep_quality=mongo_result['sleep_quality'],
                    readiness=mongo_result['readiness'],
                    wants_functional_strength=mongo_result.get('wants_functional_strength', False))
                ret.append(daily_readiness)

            return ret

    @xray_recorder.capture('datastore.DailyReadinessDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()
        del item['sore_body_parts']
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': item['user_id'], 'event_date': format_datetime(item['event_date'])}
        mongo_collection.replace_one(query, item, upsert=True)
