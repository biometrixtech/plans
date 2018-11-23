from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from models.session import SessionType, SessionFactory
from models.post_session_survey import PostSessionSurvey, PostSurvey
from utils import format_datetime, parse_date


class PostSessionSurveyDatastore(object):
    mongo_collection = 'dailyplan'

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

    @xray_recorder.capture('datastore.PostSessionSurveyDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date):

        if start_date is not None and end_date is not None:
            start_time = start_date.strftime("%Y-%m-%d")
            end_time = end_date.strftime("%Y-%m-%d")
        else:
            start_time = None
            end_time = None
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query0 = {'user_id': user_id, 'date': {'$gte': start_time, '$lte': end_time}}
        # query1 = {'_id': 0, 'last_reported': 0, 'user_id': 0}
        mongo_cursor = mongo_collection.find(query0)
        ret = []

        for plan in mongo_cursor:
            training_session_surveys = \
                [_post_session_survey_from_mongodb(s, user_id, s["session_id"], s["session_type"], plan["date"])
                 for s in plan.get('training_sessions', []) if s is not None]
            practice_session_surveys = \
                [_post_session_survey_from_mongodb(s, user_id, s["session_id"], SessionType.practice, plan["date"])
                 for s in plan.get('practice_sessions', []) if s is not None]
            strength_conditioning_session_surveys = \
                [_post_session_survey_from_mongodb(s, user_id, s["session_id"], SessionType.strength_and_conditioning, plan["date"])
                 for s in plan.get('cross_training_sessions', []) if s is not None]
            game_surveys = \
                [_post_session_survey_from_mongodb(s, user_id, s["session_id"], SessionType.game, plan["date"])
                 for s in plan.get('game_sessions', []) if s is not None]
            bump_up_session_surveys = \
                [_post_session_survey_from_mongodb(s, user_id, s["session_id"], SessionType.bump_up, plan["date"])
                 for s in plan.get('bump_up_sessions', []) if s is not None]

            ret.extend([s for s in practice_session_surveys if s is not None])
            ret.extend([s for s in strength_conditioning_session_surveys if s is not None])
            ret.extend([s for s in game_surveys if s is not None])
            ret.extend([s for s in bump_up_session_surveys if s is not None])
            ret.extend([s for s in training_session_surveys if s is not None])

        return ret


    @xray_recorder.capture('datastore.PostSessionSurveyDatastore._put_mongodb')
    def _put_mongodb(self, item):
        daily_plan_store = DailyPlanDatastore()
        daily_plan = daily_plan_store.get(user_id=item.user_id,
                                          start_date=item.event_date,
                                          end_date=item.event_date)
        '''
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
        '''

        plan = daily_plan[0]
        # sessions = getattr(plan, session_type_name)
        sessions = getattr(plan, 'training_sessions')
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

        '''
        if session_type == 1:
            session_type_name = 'cross_training_sessions'
        elif session_type == 2:
            session_type_name = 'game_sessions'
        elif session_type == 3:
            session_type_name = 'tournament_sessions'
        '''

        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {"user_id": item.user_id, "date": item.event_date}
        # mongo_collection.update_one(query, {'$set': {session_type_name: sessions}})
        mongo_collection.update_one(query, {'$set': {'training_sessions': sessions}})


def _post_session_survey_from_mongodb(mongo_result, user_id, session_id, session_type, event_date):

    survey_result = mongo_result["post_session_survey"]
    if survey_result is not None:
        if "event_date" in survey_result:
            post_session_survey = PostSessionSurvey(survey_result["event_date"], user_id, session_id, session_type, survey_result)
        else:
            post_session_survey = PostSessionSurvey(format_datetime(parse_date(event_date)), user_id, session_id, session_type, survey_result)
        return post_session_survey
    else:
        return None
