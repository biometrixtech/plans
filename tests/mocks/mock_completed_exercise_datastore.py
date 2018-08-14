class CompletedExerciseDatastore(object):

    def __init__(self):
        self.completed_exercises = None
        self.completed_exercise_summaries = None

    def side_load_completd_exercises(self, completed_exercises):
        self.completed_exercises = completed_exercises

    def side_load_completd_exercise_summaries(self, completed_exercise_summaries):
        self.completed_exercise_summaries = completed_exercise_summaries

    def get(self, athlete_id, start_date, end_date, get_summary=True):
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
            return self.completed_exercise_summaries
        else:
            return self.completed_exercises

    def _put_mongodb(self, item):
        pass