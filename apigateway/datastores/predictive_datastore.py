from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.stats import AthleteStats
from fathomapi.utils.exceptions import InvalidSchemaException


class PredictiveDatastore(object):
    def __init__(self, mongo_collection='athletestats'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.PredictiveDatastore.get')
    def get(self):
        return self._query_mongodb()

    @xray_recorder.capture('datastore.PredictiveDatastore._query_mongodb')
    def _query_mongodb(self):
        mongo_collection = get_mongo_collection(self.mongo_collection)

        query = {}
        projection = ['athlete_id']
        mongo_results = mongo_collection.find(query, limit=1000, projection=projection)
        athlete_stats_list = []
        for mongo_result in mongo_results:
            athlete_stats_list.append(mongo_result)

        return athlete_stats_list

