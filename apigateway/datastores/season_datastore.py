from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.athlete_season import AthleteSeason, Season

class AthleteSeasonDatastore(object):
    mongo_collection = get_mongo_collection('athleteseason')
    @xray_recorder.capture('datastore.AthleteSeasonDatastore.get')
    def get(self, user_id=None):
        return self._query_mongodb(user_id)

    @xray_recorder.capture('datastore.AthleteSeasonDatastore.put')
    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.AthleteSeasonDatastore._query_mongodb')
    def _query_mongodb(self, user_id):
        cursor = self.mongo_collection.find({'user_id': user_id})
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
    def _put_mongodb(self, item):
        athlete_seasons = self.get(user_id=item.user_id)
        if len(athlete_seasons) == 0:
            item = self.item_to_mongodb(item)
            self.mongo_collection.insert_one(item)
        else:
            athlete_seasons = athlete_seasons[0]
            for season in item.seasons:
                insert = True
                for existing_season in athlete_seasons.seasons:
                    if season.is_similar(existing_season):
                        insert = False
                if insert:
                    athlete_seasons.seasons.append(season)
            athlete_seasons = self.item_to_mongodb(athlete_seasons)
            self.mongo_collection.replace_one({'user_id': item.user_id}, athlete_seasons)


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
