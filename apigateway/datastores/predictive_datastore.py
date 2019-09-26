from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.stats import AthleteStats
from fathomapi.utils.exceptions import InvalidSchemaException


class PredictiveDatastore(object):
    def __init__(self, mongo_collection='athletestats'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.AthleteStatsDatastore.get')
    def get(self):
        return self._query_mongodb()

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def delete(self, athlete_id=None):
        if athlete_id is None:
            raise InvalidSchemaException("Need to provide athlete_id to delete")
        self._delete_mongodb(athlete_id=athlete_id)

    @xray_recorder.capture('datastore.AthleteStatsDatastore._query_mongodb')
    def _query_mongodb(self):
        mongo_collection = get_mongo_collection(self.mongo_collection)

        query = {}
        projection = ['athlete_id']
        mongo_results = mongo_collection.find(query, limit=1000, projection=projection)
        athlete_stats_list = []
        for mongo_result in mongo_results:
            athlete_stats_list.append(mongo_result)

        return athlete_stats_list


    @xray_recorder.capture('datastore.AthleteStatsDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'athlete_id': item['athlete_id']}
        mongo_collection.replace_one(query, item, upsert=True)

    @xray_recorder.capture('datastore.AthleteStatsDatastore._delete_mongodb')
    def _delete_mongodb(self, athlete_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {}
        if isinstance(athlete_id, list):
            query['athlete_id'] = {'$in': athlete_id}
        else:
            query['athlete_id'] = athlete_id
        if len(query) > 0:
            mongo_collection.delete_many(query)
