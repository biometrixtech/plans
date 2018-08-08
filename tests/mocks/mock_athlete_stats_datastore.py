class AthleteStatsDatastore(object):

    def __init__(self):
        self.athlete_stats = None

    def side_load_athlete_stats(self, athlete_stats):
        self.athlete_stats = athlete_stats

    def get(self, athlete_id):
        return self._query_mongodb()

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self):
        return self.athlete_stats

    def _put_mongodb(self, item):
        pass