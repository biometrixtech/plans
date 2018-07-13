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
            return self.item_from_mongodb(mongo_result)
        else:
            raise NoSuchEntityException("readiness survey does not exist for the user")

    @xray_recorder.capture('datastore.DailyReadinessDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = self.item_to_mongodb(item)
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': item['user_id'], 'event_date': format_datetime(item['event_date'])}
        mongo_collection.replace_one(query, item, upsert=True)

    @staticmethod
    def item_to_mongodb(dailyreadiness):
        """
        :param DailyReadiness dailyreadiness:
        :return: dict
        """
        item = {
            'event_date': dailyreadiness.event_date,
            'user_id': dailyreadiness.user_id,
            # TODO: this needs to be reconciled so that soreness if input is the same as soreness in output
            # currently there's discrepency in what the two objects are.
            'soreness': dailyreadiness.soreness, #[s.json_serialise() for s in dailyreadiness.soreness],
            'sleep_quality': dailyreadiness.sleep_quality,
            'readiness': dailyreadiness.readiness,
        }
        return {k: v for k, v in item.items() if v}

    @staticmethod
    def item_from_mongodb(mongo_result):
        """
        :param dict mongo_result:
        :return: DailyReadiness
        """
        return DailyReadiness(
            user_id=mongo_result['user_id'],
            event_date=mongo_result['event_date'],
            soreness=[_soreness_from_mongodb(s, mongo_result) for s in mongo_result['soreness']],
            sleep_quality=mongo_result['sleep_quality'],
            readiness=mongo_result['readiness']
        )


def _soreness_from_mongodb(soreness_mongo_result, parent_mongo_result):
    soreness = DailySoreness()
    soreness.body_part = BodyPart(BodyPartLocation(soreness_mongo_result['body_part']), None)
    soreness.severity = soreness_mongo_result['severity']
    soreness.side = soreness_mongo_result['side']
    soreness.reported_date_time = parent_mongo_result['event_date']
    return soreness
