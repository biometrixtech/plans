from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.session import CompletedFunctionalStrengthSession, CompletedFunctionalStrengthSummary
from exceptions import NoSuchEntityException


class FunctionalStrengthDatastore(object):
    mongo_collection = 'functionalstrength'

    @xray_recorder.capture('datastore.FunctionalStrengthDatastore.get')
    def get(self, user_id, start_date, end_date, get_summary=True):
        return self._query_mongodb(user_id, start_date, end_date, get_summary)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.FunctionalStrengthDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date, get_summary):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        ret = []
        query = {"$and": [{'user_id': user_id, 'event_date': {'$gte': start_date, '$lte': end_date}}]}

        if not get_summary:

            mongo_cursor = mongo_collection.find(query)

            for mongo_result in mongo_cursor:

                completed_fs_session = CompletedFunctionalStrengthSession(user_id=mongo_result['user_id'],
                                                                          event_date=mongo_result['event_date'])
                ret.append(completed_fs_session)

        else:
            mongo_cursor = mongo_collection.aggregate([
                {'$match': query},
                {"$group": {"_id": {"user_id": "$user_id"},
                            "completed_count": {"$sum": 1}}}])

            for mongo_result in mongo_cursor:
                completed_fs_summary = CompletedFunctionalStrengthSummary(user_id=mongo_result['$_id.user_id'],
                                                                          completed_count=mongo_result['completed_count'])
                ret.append(completed_fs_summary)

        return ret

    @xray_recorder.capture('datastore.FunctionalStrengthDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.insert_one(item)
