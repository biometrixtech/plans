class ResponsiveRecoveryDatastore(object):

    def __init__(self):
        self.responsive_recovery = None

    def side_load(self, responsive_recovery):
        self.responsive_recovery = responsive_recovery

    def get(self, responsive_recovery_id=None, user_id=None, event_date_time=None):
        return self._query_mongodb(responsive_recovery_id, user_id, event_date_time)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, responsive_recovery_id=None, user_id=None, event_date_time=None):
        return self.responsive_recovery

    def _put_mongodb(self, item):
        self.responsive_recovery = item