from config import get_mongo_collection
import datetime
from models.user_stats import UserStats
# from models.daily_plan import DailyPlan
# from models.daily_readiness import DailyReadiness
# from models.soreness import CompletedExercise
# from models.session import SessionFactory, SessionType
# from models.post_session_survey import PostSurvey
from logic.user_stats_processing import UserStatsProcessing
# from logic.training_plan_management import TrainingPlanManager
# from logic.survey_processing import SurveyProcessing
# from datastores.daily_plan_datastore import DailyPlanDatastore
# from datastores.completed_exercise_datastore import CompletedExerciseDatastore
# from datastores.session_datastore import SessionDatastore
from datastores.datastore_collection import DatastoreCollection
# from utils import format_datetime, format_date, parse_datetime
# from tests.mock_users.output_injury_risk_dict import InjuryRiskDictOutputProcessor
# from tests.mock_users.three_sensor_api import ThreeSensorAPIRequestProcessor
# import os
# import json
# import requests
# from movement_pattern_history import create_elasticity_adf, create_asymmetry
# from collections import OrderedDict
from datetime import timedelta
from models.training_volume import StandardErrorRange
from models.movement_tags import Gender


class DemoPersona(object):

    def __init__(self, user_id):
        self.user_id = user_id
        self.user_stats = None

    def update_stats(self, event_date, force_historical=False):
        self.user_stats = UserStatsProcessing(self.user_id,
                                              event_date=event_date,
                                              datastore_collection=DatastoreCollection()).process_user_stats(force_historical_process=force_historical)
        DatastoreCollection().user_stats_datastore.put(self.user_stats)

    def create_history(self, days, suffix='', clear_history=True, start_date_time=datetime.datetime.now()):

        if clear_history:
            self.clear_user(suffix)

    def clear_user(self, suffix=''):
        readiness = get_mongo_collection('dailyreadiness')
        daily_plan = get_mongo_collection('dailyplan')
        stats = get_mongo_collection('userstats')
        # stats = get_mongo_collection('athletestats')
        exercises = get_mongo_collection('completedexercises')
        training_sessions = get_mongo_collection('trainingsession')
        heartrate = get_mongo_collection('heartrate')
        injuryrisk = get_mongo_collection('injuryrisk')
        responsiverecovery = get_mongo_collection('responsiverecovery')
        movementprep = get_mongo_collection('movementprep')
        mobilitywod = get_mongo_collection('mobilitywod')

        readiness.delete_many({"user_id": self.user_id})
        daily_plan.delete_many({"user_id": self.user_id})
        exercises.delete_many({"athlete_id": self.user_id})
        stats.delete_one({"athlete_id": self.user_id})
        training_sessions.delete_many({"user_id": self.user_id})
        heartrate.delete_many({"user_id": self.user_id})
        injuryrisk.delete_one({"user_id": self.user_id})
        responsiverecovery.delete_many({"user_id": self.user_id})
        movementprep.delete_many({"user_id": self.user_id})
        mobilitywod.delete_many({"user_id": self.user_id})

    def create_stats(self, user_profile, event_date):
        user_stats = UserStats(athlete_id=self.user_id)
        user_stats.event_date = event_date
        user_stats.athlete_height = user_profile['height']
        user_stats.athlete_gender = Gender[user_profile['user_gender']]
        user_stats.athlete_age = user_profile['user_age']
        user_stats.athlete_weight = user_profile['user_weight']
        user_stats.vo2_max = StandardErrorRange(observed_value=user_profile['vo2_max'])

        stats_collection = get_mongo_collection('userstats')
        query = {'athlete_id': self.user_id}
        stats_collection.replace_one(query, user_stats.json_serialise(), upsert=True)

