class MovementPrepDatastore(object):

    def __init__(self):
        self.movement_prep = None

    def side_load(self, movement_prep):
        self.movement_prep = movement_prep

    def get(self, movement_prep_id=None, user_id=None, event_date_time=None):
        return self._query_mongodb(movement_prep_id, user_id, event_date_time)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, movement_prep_id=None, user_id=None, event_date_time=None):
        return self.movement_prep

    def _put_mongodb(self, item):
        self.movement_prep = item