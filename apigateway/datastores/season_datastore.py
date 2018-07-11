from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection


class AthleteSeasonDatastore(object):
    @xray_recorder.capture('datastore.AthleteSeasonDatastore.get')
    def get(self, user_id=None, week_start=None, collection='athleteseason'):
        return self._query_mongodb(user_id, week_start, collection)

    @xray_recorder.capture('datastore.AthleteSeasonDatastore.put')
    def put(self, items, collection='athleteseason'):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item, collection)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.AthleteSeasonDatastore._query_mongodb')
    def _query_mongodb(self, user_id, week_start, collection):
        mongo_collection = get_mongo_collection(collection)
        
    @xray_recorder.capture('datastore.AthleteSeasonDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        mongo_collection = get_mongo_collection(collection)
        item = self.item_to_mongodb(item)
        mongo_collection.insert_one(item)

    @staticmethod
    def item_to_mongodb(season):
        sports = []
        for sport in season.sports:
            sports.append(sport.json_serialise())
        item = {
            'user_id': season.user_id,
            'sports': sports,
        }
        return item
