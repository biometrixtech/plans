from tests.mocks import mock_athlete_stats_datastore, mock_completed_exercise_datastore, mock_daily_plan_datastore
from tests.mocks import mock_daily_readiness_datastore, mock_exercise_datastore, mock_functional_strength_datastore
from tests.mocks import mock_post_session_survey_datastore


class DatastoreCollection(object):

    def __init__(self):
        self.athlete_stats_datastore = mock_athlete_stats_datastore.AthleteStatsDatastore()
        self.completed_exercise_datastore = mock_completed_exercise_datastore.CompletedExerciseDatastore()
        self.daily_plan_datastore = mock_daily_plan_datastore.DailyPlanDatastore()
        self.daily_readiness_datastore = mock_daily_readiness_datastore.DailyReadinessDatastore()
        self.exercise_datastore = mock_exercise_datastore.ExerciseLibraryDatastore()
        self.functional_strength_datastore = mock_functional_strength_datastore.FunctionalStrengthDatastore()
        self.post_session_survey_datastore = mock_post_session_survey_datastore.PostSessionSurveyDatastore()
