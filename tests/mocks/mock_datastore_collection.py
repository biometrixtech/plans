from tests.mocks import mock_athlete_stats_datastore, mock_completed_exercise_datastore, mock_daily_plan_datastore
from tests.mocks import mock_daily_readiness_datastore, mock_exercise_datastore
from tests.mocks import mock_post_session_survey_datastore, mock_cleared_soreness_datastore
from tests.mocks import mock_injury_risk_datastore
from tests.mocks import mock_workout_datastore
from tests.mocks import mock_user_stats_datastore
from tests.mocks import mock_symptom_datastore
from tests.mocks import mock_training_session_datastore
from tests.mocks import mock_movement_prep_datastore
from tests.mocks import mock_mobility_wod_datastore
from tests.mocks import mock_responsive_recovery_datastore

class DatastoreCollection(object):

    def __init__(self):
        self.athlete_stats_datastore = mock_athlete_stats_datastore.AthleteStatsDatastore()
        self.completed_exercise_datastore = mock_completed_exercise_datastore.CompletedExerciseDatastore()
        self.daily_plan_datastore = mock_daily_plan_datastore.DailyPlanDatastore()
        self.daily_readiness_datastore = mock_daily_readiness_datastore.DailyReadinessDatastore()
        self.exercise_datastore = mock_exercise_datastore.ExerciseLibraryDatastore()
        self.post_session_survey_datastore = mock_post_session_survey_datastore.PostSessionSurveyDatastore()
        self.cleared_soreness_datastore = mock_cleared_soreness_datastore.ClearedSorenessDatastore()
        self.injury_risk_datastore = mock_injury_risk_datastore.InjuryRiskDatastore()
        self.workout_datastore = mock_workout_datastore.WorkoutDatastore()
        self.user_stats_datastore = mock_user_stats_datastore.UserStatsDatastore()
        self.symptom_datastore = mock_symptom_datastore.SymptomDatastore()
        self.training_session_datastore = mock_training_session_datastore.TrainingSessionDatastore()
        self.movement_prep_datastore = mock_movement_prep_datastore.MovementPrepDatastore()
        self.mobility_wod_datastore = mock_mobility_wod_datastore.MobilityWodDatastore()
        self.responsive_recovery_datastore = mock_responsive_recovery_datastore.ResponsiveRecoveryDatastore()

