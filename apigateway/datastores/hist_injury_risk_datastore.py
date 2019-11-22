from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection

from models.athlete_injury_risk import AthleteHistInjuryRisk


class HistInjuryRiskDatastore(object):
    def __init__(self, mongo_collection='histinjuryrisk'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.HistInjuryRiskDatastore.get')
    def get(self, user_id):
        return self._query_mongodb(user_id)

    @xray_recorder.capture('datastore.HistInjuryRiskDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.HistInjuryRiskDatastore._query_mongodb')
    def _query_mongodb(self, user_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)

        query = {'user_id': user_id}
        mongo_result = mongo_collection.find_one(query)
        if mongo_result is not None:
            athlete_injury_risk = AthleteHistInjuryRisk.json_deserialise(mongo_result)
            return athlete_injury_risk.items
        return {}

    @xray_recorder.capture('datastore.HistInjuryRiskDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': item['user_id']}
        mongo_collection.replace_one(query, item, upsert=True)
