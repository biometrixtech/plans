class SymptomDatastore(object):

    def __init__(self):
        self.symptoms = []

    def side_load(self, symptoms):
        self.symptoms = symptoms

    def get(self, user_id, event_date_time=None, start_date_time=None, end_date_time=None):
        return self._query_mongodb(user_id, event_date_time, start_date_time, end_date_time)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, user_id, event_date_time, start_date_time, end_date_time):
        return self.symptoms

    def _put_mongodb(self, item):
        self.symptoms = item