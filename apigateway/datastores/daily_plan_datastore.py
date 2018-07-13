from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.daily_plan import DailyPlan
import models.session as session
from utils import  format_datetime, parse_datetime

class DailyPlanDatastore(object):
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

    #@xray_recorder.capture('datastore.DailyPlanDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query0 = {'user_id': user_id, 'date': {'$gte': start_date, '$lte': end_date}}
        # query1 = {'_id': 0, 'last_updated': 0, 'user_id': 0}
        mongo_cursor = mongo_collection.find(query0)
        ret = []

        for plan in mongo_cursor:
            # ret.append(self.item_to_response(plan))
            daily_plan = DailyPlan(event_date=plan['date'])
            daily_plan.user_id = plan.get('user_id', None)
            daily_plan.practice_sessions = \
                [_external_session_from_mongodb(s, session.SessionType.practice) for s in plan['practice_sessions']]
            daily_plan.strength_conditioning_sessions = \
                [_external_session_from_mongodb(s, session.SessionType.strength_and_conditioning)
                 for s in plan['cross_training_sessions']]
            daily_plan.games = \
                [_external_session_from_mongodb(s, session.SessionType.game)
                 for s in plan['game_sessions']]
            # daily_plan.tournaments = \
            #     [_external_session_from_mongodb(s, session.SessionType.tournament)
            #      for s in plan['tournament_sessions']]
            daily_plan.recovery_am = plan.get('recovery_am', [])
            daily_plan.recovery_pm = plan.get('recovery_pm', [])
            # daily_plan.corrective_sessions = \
            #    [_external_session_from_mongodb(s, session.SessionType.corrective)
            #     for s in plan['corrective_sessions']]
            daily_plan.bump_up_sessions = \
                [_external_session_from_mongodb(s, session.SessionType.bump_up)
                 for s in plan['bump_up_sessions']]
            daily_plan.daily_readiness_survey = plan.get('daily_readiness_survey', None)
            daily_plan.updated = plan.get('updated', None)
            daily_plan.last_updated = plan.get('last_updated', None)
            ret.append(daily_plan)

        if len(ret) == 0:
            plan = DailyPlan(event_date=end_date)
            plan.user_id = user_id
            ret.append(plan)

        return ret

    @xray_recorder.capture('datastore.DailyPlanDatastore._put_mongodb')
    def _put_mongodb(self, item):
        collection = get_mongo_collection(self.mongo_collection)

        '''Deprecated
        practice_session_bson = ()
        cross_training_session_bson = ()
        game_session_bson = ()
        bump_up_session_bson = ()
        am_recovery_bson = ()
        pm_recovery_bson = ()

        if item.recovery_am is not None:
            am_recovery_bson = self.get_recovery_bson(item.recovery_am)

        if item.recovery_pm is not None:
            pm_recovery_bson = self.get_recovery_bson(item.recovery_pm)

        for practice_session in item.practice_sessions:
            practice_session_bson += ({'session_id': str(practice_session.id),
                                       'post_session_survey': practice_session.post_session_survey
                                       },)

        for cross_training_session in item.strength_conditioning_sessions:
            cross_training_session_bson += ({'session_id': str(cross_training_session.id),
                                             'post_session_survey': cross_training_session.post_session_survey
                                             },)

        for game_session in item.games:
            game_session_bson += ({'session_id': str(game_session.id),
                                   'post_session_survey': game_session.post_session_survey
                                   },)

        for bump_up_session in item.bump_up_sessions:
            bump_up_session_bson += ({'session_id': str(bump_up_session.id),
                                      'post_session_survey': bump_up_session.post_session_survey
                                      },)

        collection.insert_one({'user_id': item.athlete_id,
                               'date': item.date.strftime('%Y-%m-%d'),
                               'practice_sessions': practice_session_bson,
                               'bump_up_sessions': bump_up_session_bson,
                               'cross_training_sessions': cross_training_session_bson,
                               'game_sessions': game_session_bson,
                               'recovery_am': am_recovery_bson,
                               'recovery_pm': pm_recovery_bson,
                               'last_updated': item.last_updated})
        '''
        collection.insert_one(item.json_serialise())

    '''Deprecated
    def get_recovery_bson(self, recovery_session):
        exercise_bson = ()
        for recovery_exercise in recovery_session.recommended_exercises():
            exercise_bson += ({'name': recovery_exercise.exercise.name,
                               'position_order': recovery_exercise.position_order,
                               'reps_assigned': recovery_exercise.reps_assigned,
                               'sets_assigned': recovery_exercise.sets_assigned,
                               'seconds_duration': recovery_exercise.duration()
                               },)
        recovery_bson = ({'minutes_duration': recovery_session.duration_minutes,
                          'start_time': str(recovery_session.start_time),
                          'end_time': str(recovery_session.end_time),
                          'impact_score': recovery_session.impact_score,
                          'exercises': exercise_bson
                          })

        return recovery_bson
    '''
def _external_session_from_mongodb(mongo_result, session_type):

    factory = session.SessionFactory()
    mongo_session = factory.create(session_type)
    mongo_session.id = mongo_result["session_id"]
    mongo_session.description = _key_present("description", mongo_result)
    mongo_session.data_transferred = _key_present("data_transferred", mongo_result)
    mongo_session.duration_minutes = _key_present("duration_minutes", mongo_result)
    mongo_session.post_session_survey = _key_present("post_session_survey", mongo_result)

    return mongo_session

def _key_present(key_name, dictionary):
    if key_name in dictionary:
        return dictionary[key_name]
    else:
        return ""
