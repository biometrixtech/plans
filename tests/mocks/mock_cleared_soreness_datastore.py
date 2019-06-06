class ClearedSorenessDatastore(object):

    def __init__(self):
        self.cleared_doms = None

    def side_load_athlete_stats(self, cleared_doms):
        self.cleared_doms = cleared_doms

    def get(self, athlete_id, start_date=None, end_date=None):
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
        return self.cleared_doms

    def _put_mongodb(self, item):
        pass