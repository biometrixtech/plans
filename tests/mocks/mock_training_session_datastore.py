class TrainingSessionDatastore(object):

    def __init__(self):
        self.training_sessions = []

    def side_load(self, training_sessions):
        self.training_sessions = training_sessions

    def get(self, session_id=None, user_id=None, event_date_time=None, start_date_time=None, end_date_time=None, read_session_load_dict=True):
        return self._query_mongodb(session_id, user_id, event_date_time, start_date_time, end_date_time, read_session_load_dict)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, session_id, user_id, event_date_time, start_date_time, end_date_time, read_session_load_dict):
        return self.training_sessions

    def _put_mongodb(self, item):
        self.training_sessions = item
