from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.season import AthleteSeason, Season

class AthleteSeasonDatastore(object):
    @xray_recorder.capture('datastore.AthleteSeasonDatastore.get')
    def get(self, user_id=None, collection='athleteseason'):
        return self._query_mongodb(user_id, collection)

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
    def _query_mongodb(self, user_id, collection):
        mongo_collection = get_mongo_collection(collection)
        cursor = mongo_collection.find({'user_id': user_id})
        ret = []
        for athlete_season in cursor:
            seasons = []
            for season in athlete_season['seasons']:
                seasons.append(Season(sport=season['sport'],
                                      competition_level=season['competition_level'],
                                      positions=season['positions'],
                                      start_date=season['start_date'],
                                      end_date=season['end_date'])
                              )
            ret.append(AthleteSeason(user_id=user_id,
                                     seasons=seasons))
        return ret
        
    @xray_recorder.capture('datastore.AthleteSeasonDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        existing_season = self.get(user_id=item.user_id)
        mongo_collection = get_mongo_collection(collection)
        if len(existing_season) == 0:
            item = self.item_to_mongodb(item)
            mongo_collection.insert_one(item)
        else:
            existing_season = existing_season[0]
            existing_season.seasons += item.seasons
            existing_season = self.item_to_mongodb(existing_season)
            mongo_collection.replace_one({'user_id': item.user_id}, existing_season)

    @staticmethod
    def item_to_mongodb(athlete_season):
        seasons = []
        for season in athlete_season.seasons:
            seasons.append(season.json_serialise())
        item = {
            'user_id': athlete_season.user_id,
            'seasons': seasons,
        }
        return item
