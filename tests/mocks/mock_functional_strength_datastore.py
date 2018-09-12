class FunctionalStrengthDatastore(object):

    def __init__(self):
        self.completed_sessions = None
        self.completed_summaries = None

    def side_load_completd_exercises(self, completed_sessions):
        self.completed_sessions = completed_sessions

    def side_load_completd_exercise_summaries(self, completed_summaries):
        self.completed_summaries = completed_summaries

    def get(self, user_id, start_date, end_date, get_summary=True):
        return self._query_mongodb(get_summary)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, get_summary):
        if get_summary:
            return self.completed_summaries
        else:
            return self.completed_sessions

    def _put_mongodb(self, item):
        pass