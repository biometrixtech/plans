# import datetime
from config_mock import get_mongo_collection
import datetime
from models.daily_plan import DailyPlan
from models.daily_readiness import DailyReadiness
from models.soreness import CompletedExercise
from models.session import SessionFactory, SessionType
from models.post_session_survey import PostSurvey
from logic.stats_processing import StatsProcessing
from logic.training_plan_management import TrainingPlanManager
from logic.survey_processing import SurveyProcessing
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from datastores.session_datastore import SessionDatastore
from datastores.datastore_collection import DatastoreCollection
from utils import format_datetime, format_date, parse_datetime
from tests.mock_users.output_injury_risk_dict import InjuryRiskDictOutputProcessor
from tests.mock_users.three_sensor_api import ThreeSensorAPIRequestProcessor
import os
import json
import requests
from movement_pattern_history import create_elastticity_adf
from collections import OrderedDict
from datetime import timedelta


class Persona(object):
    def __init__(self, user_id, plans_version=4.5):
        self.user_id = user_id
        self.soreness_history = None
        self.session_history = None
        self.daily_plan = None
        self.daily_readiness = None
        self.athlete_stats = None
        self.rpes = []
        self.plans_version = plans_version
        self.elasticity_adf_dictionary = {}
        self.three_session_history = {}

    def create_history(self, days, suffix='', clear_history=True, start_date_time=datetime.datetime.now(), end_today=False, rpes=[], jwt=None, visualizations=True, log_output=False, user_name='test'):

        proc = InjuryRiskDictOutputProcessor('../../ird', self.user_id, user_name)

        if log_output:
            proc.write_headers()

        self.rpes = rpes
        if clear_history:
            self.clear_user(suffix)
        if end_today:
            start_date_time = start_date_time + datetime.timedelta(days=1)
        event_date = start_date_time - datetime.timedelta(days=days)
        self.update_stats(event_date)
        last_plan_date = None
        for i in range(days):
            # date_time = format_datetime(event_date)
            today_date = format_date(event_date)
            date_time = event_date
            soreness = []
            for body_part in self.soreness_history:
                if body_part['severity'][i] is not None:
                    soreness.append({'body_part': body_part['body_part'],
                                     'side': body_part['side'],
                                     'pain': body_part['pain'],
                                     'severity': body_part['severity'][i]})

            if len(soreness) > 0 or (len(self.rpes) > 0 and self.rpes[i] is not None) or (self.elasticity_adf_dictionary is not None and self.elasticity_adf_dictionary[i] is not None):

                if len(soreness) > 0:
                    readiness_data = {'date_time': format_datetime(date_time),
                                      'soreness': soreness}
                    self.create_readiness(readiness_data)

                    self.create_plan(event_date, i, visualizations)
                else:
                    self.daily_readiness = None
                    self.create_plan(event_date, i, visualizations)

                if self.elasticity_adf_dictionary[i] is not None:
                    todays_regression_history = self.elasticity_adf_dictionary[i]
                    body = OrderedDict()
                    body["event_date"] = format_datetime(date_time)
                    body["session_id"] = self.three_session_history[i]["session_id"]
                    body["seconds_duration"] = self.three_session_history[i]["seconds_duration"]
                    body["end_date"] = format_datetime(date_time + timedelta(seconds=body["seconds_duration"]))
                    body['movement_patterns'] = create_elastticity_adf(todays_regression_history)

                    self.send_three_sensor_data_to_plans(self.user_id,jwt,body)
                    self.create_plan_light(event_date)

                last_plan_date = event_date
                if self.daily_plan.pre_active_rest is not None and len(self.daily_plan.pre_active_rest) > 0:
                    exercise_list = [ex.exercise.id for ex in self.daily_plan.pre_active_rest[0].inhibit_exercises.values()]
                    self.complete_exercises(exercise_list, format_datetime(event_date + datetime.timedelta(hours=1)))
                if log_output:
                    proc.write_day(today_date)
                print(today_date)

            event_date = event_date + datetime.timedelta(days=1)
            # if not end_today:
            #     self.update_stats(event_date)
            # else:
            #     if i < days - 1:
            #         self.update_stats(event_date)

        # if not end_today:
        #     self.update_stats(event_date)
        if log_output:
            proc.close()
        return last_plan_date

    def clear_user(self, suffix=''):
        readiness = get_mongo_collection('dailyreadiness', suffix)
        daily_plan = get_mongo_collection('dailyplan', suffix)
        stats = get_mongo_collection('athletestats', suffix)
        exercises = get_mongo_collection('completedexercises', suffix)
        asymmetry = get_mongo_collection('asymmetry', suffix)
        injuryrisk = get_mongo_collection('injuryrisk', suffix)

        readiness.delete_many({"user_id": self.user_id})
        daily_plan.delete_many({"user_id": self.user_id})
        exercises.delete_many({"athlete_id": self.user_id})
        stats.delete_one({"athlete_id": self.user_id})
        asymmetry.delete_many({"user_id": self.user_id})
        injuryrisk.delete_one({"user_id": self.user_id})

    def create_plan(self, event_date, day_number, visualizations):
        self.daily_plan = DailyPlan(format_date(event_date))
        self.daily_plan.user_id = self.user_id
        self.daily_plan.daily_readiness_survey = self.daily_readiness
        # self.daily_plan.session_from_readiness = True
        if len(self.rpes) > 0:
            self.add_session(event_date, self.rpes[day_number])
        else:
            self.add_session(event_date)
        store = DailyPlanDatastore()
        store.put(self.daily_plan)
        self.update_stats(event_date)

        if self.daily_readiness is not None:
            survey_processor = SurveyProcessing(self.user_id, event_date, self.athlete_stats, DatastoreCollection())
            survey_processor.soreness = self.daily_readiness.soreness
            survey_processor.patch_daily_and_historic_soreness(survey='readiness')
            self.athlete_stats = survey_processor.athlete_stats

        plan_manager = TrainingPlanManager(self.user_id, DatastoreCollection(), )
        self.daily_plan = plan_manager.create_daily_plan(event_date=format_date(event_date), last_updated=format_datetime(event_date), athlete_stats=self.athlete_stats, visualizations=visualizations)

    def create_plan_light(self, event_date):
        plan_manager = TrainingPlanManager(self.user_id, DatastoreCollection(), )
        self.daily_plan = plan_manager.create_daily_plan(event_date=format_date(event_date),
                                                         last_updated=format_datetime(event_date),
                                                         athlete_stats=self.athlete_stats,
                                                         visualizations=False)

    def update_stats(self, event_date):
        self.athlete_stats = StatsProcessing(self.user_id, event_date=event_date, datastore_collection=DatastoreCollection()).process_athlete_stats()
        DatastoreCollection().athlete_stats_datastore.put(self.athlete_stats)

    def create_readiness(self, data):
        self.daily_readiness = DailyReadiness(
                                            user_id=self.user_id,
                                            event_date=data['date_time'],
                                            soreness=data['soreness'],  # dailysoreness object array
                                            sleep_quality=None,
                                            readiness=None
                                        )
        # store = DailyReadinessDatastore()
        # store.put(daily_readiness)

    def complete_exercises(self, exercise_list, event_date):
        exercise_store = CompletedExerciseDatastore()

        for exercise in exercise_list:
            exercise_store.put(CompletedExercise(athlete_id=self.user_id,
                                                 exercise_id=exercise,
                                                 event_date=event_date))

    def add_session(self, event_date, rpe=5):
        if rpe is not None:
            ps_event_date = event_date + datetime.timedelta(minutes=40)
            session = SessionFactory().create(SessionType(6))
            session.event_date = ps_event_date
            session.sport_name = 72
            session.duration_minutes = 30
            session.post_session_survey = PostSurvey(survey={'RPE': rpe, 'soreness': []}, event_date=format_datetime(ps_event_date))
            store = SessionDatastore()
            store.insert(session, self.user_id, format_date(event_date))
            self.daily_plan.training_sessions.append(session)

    def send_three_sensor_data_to_plans(self, user_id, jwt, body):
        url = 'https://apis.{env}.fathomai.com/plans/4_6/session/{user_id}/three_sensor_data'.format(
            env=os.environ['ENVIRONMENT'], user_id=user_id, version=self.plans_version)
        # proc = ThreeSensorAPIRequestProcessor(event_date, session_id, seconds_duration, end_date)
        # body = proc.get_body(asymmetry_patterns, movement_patterns)
        headers = {"Content-Type": "application/json", "Authorization": jwt}
        response = requests.post(url, data=json.dumps(body), headers=headers)

        return response
