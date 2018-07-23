from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from logic.soreness_and_injury import DailySoreness, BodyPart, BodyPartLocation
from models.daily_readiness import DailyReadiness
from utils import format_datetime, parse_datetime
from exceptions import NoSuchEntityException
import datetime


class DailyReadinessDatastore(object):
    mongo_collection = 'readiness'

    @xray_recorder.capture('datastore.DailyReadinessDatastore.get')
    def get(self, user_id, start_date=None, end_date=None, last_only=True):
        return self._query_mongodb(user_id, start_date, end_date)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.DailyReadinessDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date, last_only=True):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if start_date is None and end_date is None:
            query = {'user_id': user_id}
        else:
            start_date_time = datetime.datetime.strptime(start_date, "%Y-%m-%d")
            end_date_time = datetime.datetime.strptime(end_date, "%Y-%m-%d")
            start_time = format_datetime(
                datetime.datetime(start_date_time.year, start_date_time.month, start_date_time.day, 0, 0, 0))
            end_time = format_datetime(
                datetime.datetime(end_date_time.year, end_date_time.month, end_date_time.day, 0, 0, 0))
            query = {'user_id': user_id, 'event_date': {'$gte': start_time, '$lte': end_time}}
        if last_only:
            mongo_result = mongo_collection.find_one(query, sort=[('event_date', -1)])

            if mongo_result is not None:
                return [DailyReadiness(
                                      event_date=mongo_result['event_date'],
                                      user_id=mongo_result['user_id'],
                                      soreness=mongo_result['soreness'],
                                      sleep_quality=mongo_result['sleep_quality'],
                                      readiness=mongo_result['readiness'])]

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
                    readiness=mongo_result['readiness'])
                ret.append(daily_readiness)

            return ret

    @xray_recorder.capture('datastore.DailyReadinessDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()
        del item['sore_body_parts']
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': item['user_id'], 'event_date': format_datetime(item['event_date'])}
        mongo_collection.replace_one(query, item, upsert=True)
