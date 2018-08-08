from aws_xray_sdk.core import xray_recorder
from models.session import SessionType, SessionFactory
from models.post_session_survey import PostSessionSurvey, PostSurvey
from tests.testing_utilities import TestUtilities
from datetime import datetime


class PostSessionSurveyDatastore(object):
    mongo_collection = 'dailyplan'

    def __init__(self):
        self.post_session_surveys = []
        self.daily_plan = None

    def side_load_surveys(self, post_session_surveys):
        self.post_session_surveys = post_session_surveys

    def side_load_plan(self, daily_plan):
        self.daily_plan = daily_plan

    def get(self, user_id=None, start_date=None, end_date=None):
        return self._query_mongodb(user_id, start_date, end_date)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def _query_mongodb(self, user_id, start_date, end_date):

        return self.post_session_surveys

    @xray_recorder.capture('datastore.PostSessionSurveyDatastore._put_mongodb')
    def _put_mongodb(self, item):
        session_type = item.session_type.value
        if session_type == 0:
            session_type_name = 'practice_sessions'
        elif session_type == 1:
            session_type_name = 'strength_conditioning_sessions'
        elif session_type == 2:
            session_type_name = 'games'
        elif session_type == 3:
            session_type_name = 'tournaments'
        elif session_type == 4:
            session_type_name = 'bump_up_sessions'
        elif session_type == 5:
            session_type_name = 'corrective_sessions'

        plan = self.daily_plan
        sessions = getattr(plan, session_type_name)
        sessions = [s.json_serialise() for s in sessions]
        if item.session_id is not None:
            for session in sessions:
                if session['session_id'] == item.session_id:
                    session['post_session_survey'] = item.survey.json_serialise()
                    break
        else:
            session = SessionFactory()
            session = session.create(SessionType(item.session_type))
            session_json = session.json_serialise()
            session_json['post_session_survey'] = item.survey.json_serialise()

            sessions.append(session_json)

        if session_type == 1:
            session_type_name = 'cross_training_sessions'
        elif session_type == 2:
            session_type_name = 'game_sessions'
        elif session_type == 3:
            session_type_name = 'tournament_sessions'

        query = {"user_id": item.user_id, "date": item.event_date}
        # mongo_collection.update_one(query, {'$set': {session_type_name: sessions}})


