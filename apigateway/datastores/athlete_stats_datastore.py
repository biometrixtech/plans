from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.stats import AthleteStats
from exceptions import NoSuchEntityException


class AthleteStatsDatastore(object):
    mongo_collection = 'athletestats'

    @xray_recorder.capture('datastore.AthlteStatsDatastore.get')
    def get(self, athlete_id):
        return self._query_mongodb(athlete_id)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.AthleteStatsDatastore._query_mongodb')
    def _query_mongodb(self, athlete_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'athlete_id': athlete_id}
        mongo_result = mongo_collection.find_one(query)

        if mongo_result is not None:
            athlete_stats = AthleteStats(athlete_id=mongo_result['athlete_id'])
            athlete_stats.event_date = mongo_result['event_date']
            athlete_stats.acute_avg_RPE = mongo_result['acute_avg_RPE']
            athlete_stats.acute_avg_readiness = mongo_result['acute_avg_readiness']
            athlete_stats.acute_avg_sleep_quality = mongo_result['acute_avg_sleep_quality']
            athlete_stats.acute_avg_max_soreness = mongo_result['acute_avg_max_soreness']
            athlete_stats.chronic_avg_RPE = mongo_result['chronic_avg_RPE']
            athlete_stats.chronic_avg_readiness = mongo_result['chronic_avg_readiness']
            athlete_stats.chronic_avg_max_soreness = mongo_result['chronic_avg_max_soreness']
            return athlete_stats

        else:
            return None

    @xray_recorder.capture('datastore.AthleteStatsDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'athlete_id': item['athlete_id']}
        mongo_collection.replace_one(query, item, upsert=True)
