from datastores import athlete_stats_datastore, completed_exercise_datastore, daily_plan_datastore
from datastores import daily_readiness_datastore, exercise_datastore, heart_rate_datastore
from datastores import post_session_survey_datastore, session_datastore
from datastores import sleep_history_datastore
from datastores import cleared_soreness_datastore
from datastores import asymmetry_datastore


class DatastoreCollection(object):

    def __init__(self):
        self.athlete_stats_datastore = athlete_stats_datastore.AthleteStatsDatastore()
        self.completed_exercise_datastore = completed_exercise_datastore.CompletedExerciseDatastore()
        self.daily_plan_datastore = daily_plan_datastore.DailyPlanDatastore()
        self.daily_readiness_datastore = daily_readiness_datastore.DailyReadinessDatastore()
        self.exercise_datastore = exercise_datastore.ExerciseLibraryDatastore()
        self.heart_rate_datastore = heart_rate_datastore.HeartRateDatastore()
        self.post_session_survey_datastore = post_session_survey_datastore.PostSessionSurveyDatastore()
        self.session_datastore = session_datastore.SessionDatastore()
        self.sleep_history_datastore = sleep_history_datastore.SleepHistoryDatastore()
        self.cleared_soreness_datastore = cleared_soreness_datastore.ClearedSorenessDatastore()
        self.asymmetry_datastore = asymmetry_datastore.AsymmetryDatastore()
