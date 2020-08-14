class MobilityWodDatastore(object):

    def __init__(self):
        self.mobility_wod = None

    def side_load(self, mobility_wod):
        self.mobility_wod = mobility_wod

    def get(self, movement_wod_id=None, user_id=None, event_date_time=None):
        return self._query_mongodb(movement_wod_id, user_id, event_date_time)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, movement_wod_id=None, user_id=None, event_date_time=None):
        return self.mobility_wod

    def _put_mongodb(self, item):
        self.mobility_wod = item