class InjuryRiskDatastore(object):

    def __init__(self):
        self.injury_risk = None


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
        return {}

    def _put_mongodb(self, item):
        pass