from datastores import athlete_stats_datastore, completed_exercise_datastore, daily_plan_datastore
from datastores import daily_readiness_datastore, exercise_datastore, heart_rate_datastore
from datastores import post_session_survey_datastore, session_datastore
from datastores import sleep_history_datastore
from datastores import cleared_soreness_datastore
from datastores import asymmetry_datastore
from datastores import injury_risk_datastore, hist_injury_risk_datastore
from datastores import local_exercise_datastore

from datastores import training_session_datastore
from datastores import workout_program_datastore
from datastores import symptom_datastore
from datastores import user_stats_datastore
from datastores import movement_prep_datastore
from datastores import mobility_wod_datastore
from datastores import responsive_recovery_datastore


class DatastoreCollection(object):

    def __init__(self):
        self.athlete_stats_datastore = athlete_stats_datastore.AthleteStatsDatastore()
        self.completed_exercise_datastore = completed_exercise_datastore.CompletedExerciseDatastore()
        self.daily_plan_datastore = daily_plan_datastore.DailyPlanDatastore()
        self.daily_readiness_datastore = daily_readiness_datastore.DailyReadinessDatastore()
        self.exercise_datastore = local_exercise_datastore.ExerciseLibraryDatastore()
        self.heart_rate_datastore = heart_rate_datastore.HeartRateDatastore()
        self.post_session_survey_datastore = post_session_survey_datastore.PostSessionSurveyDatastore()
        self.session_datastore = session_datastore.SessionDatastore()
        self.sleep_history_datastore = sleep_history_datastore.SleepHistoryDatastore()
        self.cleared_soreness_datastore = cleared_soreness_datastore.ClearedSorenessDatastore()
        self.asymmetry_datastore = asymmetry_datastore.AsymmetryDatastore()
        self.injury_risk_datastore = injury_risk_datastore.InjuryRiskDatastore()
        self.hist_injury_risk_datastore = hist_injury_risk_datastore.HistInjuryRiskDatastore()

        self.training_session_datastore = training_session_datastore.TrainingSessionDatastore()
        self.workout_program_datastore = workout_program_datastore.WorkoutProgramDatastore()
        self.symptom_datastore = symptom_datastore.SymptomDatastore()
        self.user_stats_datastore = user_stats_datastore.UserStatsDatastore()
        self.movement_prep_datastore = movement_prep_datastore.MovementPrepDatastore()
        self.mobility_wod_datastore = mobility_wod_datastore.MobilityWODDatastore()
        self.responsive_recovery_datastore = responsive_recovery_datastore.ResponsiveRecoveryDatastore()