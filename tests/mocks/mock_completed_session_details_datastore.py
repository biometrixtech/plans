class CompletedSessionDetailsDatastore(object):

    def __init__(self):
        self.completed_sessions = []

    def side_load_planned_workout(self, workouts):
        self.completed_sessions = workouts

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
        if event_date_time is not None:
            sessions = [c for c in self.completed_sessions if event_date_time.date() == c.event_date_time.date()]
            return sessions
        elif start_date_time is not None and end_date_time is None:
            sessions = [c for c in self.completed_sessions if start_date_time >= c.event_date_time.date()]
            return sessions
        elif start_date_time is not None and end_date_time is not None:
            sessions = [c for c in self.completed_sessions if start_date_time <= c.event_date_time.date() <= end_date_time]
            return sessions
        return self.completed_sessions

    def _put_mongodb(self, item):
        self.completed_sessions.append(item)
