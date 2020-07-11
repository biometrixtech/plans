class CompletedSessionDetailsDatastore(object):

    def __init__(self):
        self.completed_sessions = []

    def side_load_planned_workout(self, workout):
        self.completed_sessions = workout

    def get(self, program_id=None, event_date_time=None, start_date_time=None, end_date_time=None):
        return self._query_mongodb(program_id, event_date_time, start_date_time, end_date_time)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, program_id, event_date_time, start_date_time, end_date_time):
        return self.completed_sessions

    def _put_mongodb(self, item):
        self.completed_sessions.append(item)
