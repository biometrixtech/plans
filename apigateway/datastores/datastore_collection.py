from datastores import athlete_stats_datastore, completed_exercise_datastore, daily_plan_datastore
from datastores import daily_readiness_datastore, exercise_datastore
from datastores import post_session_survey_datastore, season_datastore, session_datastore
from datastores import weekly_schedule_datastore


class DatastoreCollection(object):

    def __init__(self):
        self.athlete_stats_datastore = athlete_stats_datastore.AthleteStatsDatastore()
        self.completed_exercise_datastore = completed_exercise_datastore.CompletedExerciseDatastore()
        self.daily_plan_datastore = daily_plan_datastore.DailyPlanDatastore()
        self.daily_readiness_datastore = daily_readiness_datastore.DailyReadinessDatastore()
        self.exercise_datastore = exercise_datastore.ExerciseLibraryDatastore()
        self.post_session_survey_datastore = post_session_survey_datastore.PostSessionSurveyDatastore()
        self.season_datastore = season_datastore.AthleteSeasonDatastore()
        self.session_datastore = session_datastore.SessionDatastore()
        self.weekly_schedule_datastore = weekly_schedule_datastore.WeeklyScheduleDatastore()
