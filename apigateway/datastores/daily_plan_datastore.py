from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.daily_plan import DailyPlan
import models.session as session
import models.exercise as exercise
from utils import  format_datetime, parse_datetime

class DailyPlanDatastore(object):
    mongo_collection = 'dailyplan'

    def get(self, user_id=None, start_date=None, end_date=None, day_of_week=None):
        return self._query_mongodb(user_id, start_date, end_date, day_of_week)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.DailyPlanDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date, day_of_week):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if day_of_week is None:
            query0 = {'user_id': user_id, 'date': {'$gte': start_date, '$lte': end_date}}
            # query1 = {'_id': 0, 'last_updated': 0, 'user_id': 0}
        else:
            query0 = {'user_id': user_id, 'date': {'$gte': start_date, '$lte': end_date}, 'day_of_week': day_of_week}
        mongo_cursor = mongo_collection.find(query0)
        ret = []

        for plan in mongo_cursor:
            # ret.append(self.item_to_response(plan))
            daily_plan = DailyPlan(event_date=plan['date'])
            daily_plan.user_id = plan.get('user_id', None)
            daily_plan.training_sessions = \
                [_external_session_from_mongodb(s, session.SessionType) for s in plan.get('training_sessions', [])]
            daily_plan.practice_sessions = \
                [_external_session_from_mongodb(s, session.SessionType.practice) for s in plan.get('practice_sessions', [])]
            daily_plan.strength_conditioning_sessions = \
                [_external_session_from_mongodb(s, session.SessionType.strength_and_conditioning)
                 for s in plan.get('cross_training_sessions', [])]
            daily_plan.games = \
                [_external_session_from_mongodb(s, session.SessionType.game)
                 for s in plan.get('game_sessions', [])]
            # daily_plan.tournaments = \
            #     [_external_session_from_mongodb(s, session.SessionType.tournament)
            #      for s in plan['tournament_sessions']]
            daily_plan.pre_recovery = _recovery_session_from_mongodb(plan['pre_recovery']) if plan.get('pre_recovery', None) is not None else None
            daily_plan.post_recovery = _recovery_session_from_mongodb(plan['post_recovery']) if plan.get('post_recovery', None) is not None else None
            daily_plan.completed_post_recovery_sessions = \
                [_recovery_session_from_mongodb(s) for s in plan.get('completed_post_recovery_sessions', [])]
            # daily_plan.corrective_sessions = \
            #    [_external_session_from_mongodb(s, session.SessionType.corrective)
            #     for s in plan['corrective_sessions']]
            daily_plan.bump_up_sessions = \
                [_external_session_from_mongodb(s, session.SessionType.bump_up)
                 for s in plan.get('bump_up_sessions', [])]
            daily_plan.daily_readiness_survey = plan.get('daily_readiness_survey', None)
            daily_plan.updated = plan.get('updated', None)
            daily_plan.last_updated = plan.get('last_updated', None)
            daily_plan.pre_recovery_completed = plan.get('pre_recovery_completed', False)
            daily_plan.post_recovery_completed = plan.get('post_recovery_completed', False)
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

        if item.pre_recovery is not None:
            am_recovery_bson = self.get_recovery_bson(item.pre_recovery)

        if item.post_recovery is not None:
            pm_recovery_bson = self.get_recovery_bson(item.post_recovery)

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
                               'pre_recovery': am_recovery_bson,
                               'post_recovery': pm_recovery_bson,
                               'last_updated': item.last_updated})
        '''
        query = {'user_id': item.user_id, 'date': item.event_date}
        collection.replace_one(query, item.json_serialise(), upsert=True)

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
    attrs_from_mongo = ["description",
                        "sport",
                        "event_date",
                        "session_type",
                        "sport_name",
                        "duration",
                        "data_transferred",
                        "duration_minutes",
                        "external_load",
                        "high_intensity_minutes",
                        "mod_intensity_minutes",
                        "low_intensity_minutes",
                        "high_intensity_load",
                        "mod_intensity_load",
                        "low_intensity_load",
                        "sensor_start_date_time",
                        "sensor_end_date_time",
                        "post_session_survey"]
    for key in attrs_from_mongo:
        setattr(mongo_session, key, _key_present(key, mongo_result))

    return mongo_session

def _recovery_session_from_mongodb(mongo_result):

    recovery_session = session.RecoverySession()
    recovery_session.start_time = _key_present("start_time", mongo_result)
    recovery_session.end_time = _key_present("end_time", mongo_result)
    recovery_session.impact_score = _key_present("impact_score", mongo_result)
    recovery_session.goal_text = _key_present("goal_text", mongo_result)
    recovery_session.why_text = _key_present("why_text", mongo_result)
    recovery_session.duration_minutes = _key_present("minutes_duration", mongo_result)
    recovery_session.completed = mongo_result.get("completed", False)
    recovery_session.display_exercises = mongo_result.get("display_exercises", False)
    recovery_session.inhibit_exercises = [_assigned_exercises_from_mongodb(s)
                                          for s in mongo_result['inhibit_exercises']]
    recovery_session.lengthen_exercises = [_assigned_exercises_from_mongodb(s)
                                         for s in mongo_result['lengthen_exercises']]
    recovery_session.activate_exercises = [_assigned_exercises_from_mongodb(s)
                                           for s in mongo_result['activate_exercises']]
    recovery_session.integrate_exercises = [_assigned_exercises_from_mongodb(s)
                                            for s in mongo_result['integrate_exercises']]
    return recovery_session


def _assigned_exercises_from_mongodb(mongo_result):

    assigned_exercise = exercise.AssignedExercise(_key_present("library_id", mongo_result))
    assigned_exercise.exercise.name = _key_present("name", mongo_result)
    assigned_exercise.exercise.display_name = _key_present("display_name", mongo_result)
    assigned_exercise.exercise.youtube_id = _key_present("youtube_id", mongo_result)
    assigned_exercise.exercise.description = _key_present("description", mongo_result)
    assigned_exercise.exercise.bilateral = _key_present("bilateral", mongo_result)
    assigned_exercise.exercise.unit_of_measure = _key_present("unit_of_measure", mongo_result)
    assigned_exercise.position_order = _key_present("position_order", mongo_result)
    assigned_exercise.reps_assigned = _key_present("reps_assigned", mongo_result)
    assigned_exercise.sets_assigned = _key_present("sets_assigned", mongo_result)
    assigned_exercise.exercise.seconds_per_set = _key_present("seconds_per_set", mongo_result)
    assigned_exercise.exercise.seconds_per_rep = _key_present("seconds_per_rep", mongo_result)
    assigned_exercise.goal_text = _key_present("goal_text", mongo_result)
    return assigned_exercise

def _key_present(key_name, dictionary):
    if key_name in dictionary:
        return dictionary[key_name]
    else:
        return ""
