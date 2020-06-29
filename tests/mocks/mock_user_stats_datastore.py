class UserStatsDatastore(object):

    def __init__(self):
        self.user_stats = None

    def side_load(self, user_stats):
        self.user_stats = user_stats

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
        return self.user_stats

    def _put_mongodb(self, item):
        self.user_stats = item