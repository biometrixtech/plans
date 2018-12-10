import models.soreness
from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.daily_plan import DailyPlan
import models.session as session
import models.exercise as exercise
from models.post_session_survey import PostSurvey

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
            # query1 = {'_id': 0, 'last_reported': 0, 'user_id': 0}
        else:
            query0 = {'user_id': user_id, 'date': {'$gte': start_date, '$lte': end_date}, 'day_of_week': day_of_week}
        mongo_cursor = mongo_collection.find(query0)
        ret = []

        for plan in mongo_cursor:
            # ret.append(self.item_to_response(plan))
            daily_plan = DailyPlan(event_date=plan['date'])
            daily_plan.user_id = plan.get('user_id', None)
            daily_plan.training_sessions = \
                [_external_session_from_mongodb(s, session.SessionType(s['session_type'])) for s in plan.get('training_sessions', [])]
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
            daily_plan.last_sensor_sync = plan.get('last_sensor_sync', None)
            daily_plan.sessions_planned = plan.get('sessions_planned', True)
            daily_plan.functional_strength_eligible = plan.get('functional_strength_eligible', False)
            daily_plan.completed_functional_strength_sessions = plan.get('completed_functional_strength_sessions', 0)
            daily_plan.functional_strength_session = _functional_strength_session_from_mongodb(plan['functional_strength_session']) if plan.get('functional_strength_session', None) is not None else None
            daily_plan.functional_strength_completed = plan.get('functional_strength_completed', False)
            daily_plan.session_from_readiness = plan.get('session_from_readiness', False)
            daily_plan.sessions_planned_readiness = plan.get('sessions_planned_readiness', True)
            ret.append(daily_plan)

        if len(ret) == 0:
            plan = DailyPlan(event_date=end_date)
            plan.user_id = user_id
            plan.last_sensor_sync = self.get_last_sensor_sync(user_id, end_date)
            ret.append(plan)

        return ret

    @xray_recorder.capture('datastore.DailyPlanDatastore._put_mongodb')
    def _put_mongodb(self, item):
        collection = get_mongo_collection(self.mongo_collection)
        query = {'user_id': item.user_id, 'date': item.event_date}
        collection.replace_one(query, item.json_serialise(), upsert=True)


    def get_last_sensor_sync(self, user_id, event_date):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query0 = {'user_id': user_id, 'date': {'$lte': event_date}, 'last_sensor_sync': {'$exists': True, '$ne': None } }
        query1 = {'_id': 0, "last_sensor_sync": 1, "date": 1}
        mongo_cursor = mongo_collection.find_one(query0, query1, sort=[("date", -1)])
        if mongo_cursor is not None:
            last_sensor_sync = mongo_cursor.get('last_sensor_sync')
            return last_sensor_sync
        else:
            return None



def _external_session_from_mongodb(mongo_result, session_type):

    factory = session.SessionFactory()
    mongo_session = factory.create(session_type)
    mongo_session.id = mongo_result["session_id"]
    attrs_from_mongo = ["description",
                        "sport_name",
                        "strength_and_conditioning_type",
                        "event_date",
                        "duration_minutes",
                        "data_transferred",
                        "duration_sensor",
                        "external_load",
                        "high_intensity_minutes",
                        "mod_intensity_minutes",
                        "low_intensity_minutes",
                        "inactive_minutes",
                        "high_intensity_load",
                        "mod_intensity_load",
                        "low_intensity_load",
                        "inactive_load",
                        "sensor_start_date_time",
                        "sensor_end_date_time",
                        "deleted"]
    for key in attrs_from_mongo:
        setattr(mongo_session, key, _key_present(key, mongo_result))
    if "post_session_survey" in mongo_result and mongo_result["post_session_survey"] is not None:
        mongo_session.post_session_survey = PostSurvey(mongo_result["post_session_survey"], mongo_result["post_session_survey"]["event_date"])
    else:
        mongo_session.post_session_survey = None

    return mongo_session

def _recovery_session_from_mongodb(mongo_result):

    recovery_session = session.RecoverySession()
    recovery_session.start_date = _key_present("start_date", mongo_result)
    recovery_session.event_date = _key_present("event_date", mongo_result)
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
    recovery_session.inhibit_iterations = mongo_result.get("inhibit_iterations", 0)
    recovery_session.lengthen_iterations = mongo_result.get("lengthen_iterations", 0)
    recovery_session.activate_iterations = mongo_result.get("activate_iterations", 0)
    recovery_session.integrate_iterations = mongo_result.get("integrate_iterations", 0)
    return recovery_session



def _functional_strength_session_from_mongodb(mongo_result):
    functional_strength_session = session.FunctionalStrengthSession()
    functional_strength_session.equipment_required = _key_present("equipment_required", mongo_result)
    functional_strength_session.warm_up = [_assigned_exercises_from_mongodb(s)
                                          for s in mongo_result['warm_up']]
    functional_strength_session.dynamic_movement = [_assigned_exercises_from_mongodb(s)
                                          for s in mongo_result['dynamic_movement']]
    functional_strength_session.stability_work = [_assigned_exercises_from_mongodb(s)
                                          for s in mongo_result['stability_work']]
    functional_strength_session.victory_lap = [_assigned_exercises_from_mongodb(s)
                                          for s in mongo_result['victory_lap']]
    functional_strength_session.duration_minutes = _key_present("minutes_duration", mongo_result)
    functional_strength_session.warm_up_target_minutes = _key_present("warm_up_target_minutes", mongo_result)
    functional_strength_session.dynamic_movement_target_minutes = _key_present("dynamic_movement_target_minutes", mongo_result)
    functional_strength_session.stability_work_target_minutes = _key_present("stability_work_target_minutes", mongo_result)
    functional_strength_session.victory_lap_target_minutes = _key_present("victory_lap_target_minutes", mongo_result)
    functional_strength_session.warm_up_max_percentage = _key_present("warm_up_max_percentage", mongo_result)
    functional_strength_session.dynamic_movement_max_percentage = _key_present("dynamic_movement_max_percentage", mongo_result)
    functional_strength_session.stability_work_max_percentage = _key_present("stability_work_max_percentage", mongo_result)
    functional_strength_session.victory_lap_max_percentage = _key_present("victory_lap_max_percentage", mongo_result)
    functional_strength_session.completed = mongo_result.get("completed", False)
    functional_strength_session.start_date = _key_present("start_date", mongo_result)
    functional_strength_session.event_date = _key_present("event_date", mongo_result)
    functional_strength_session.sport_name = _key_present("sport_name", mongo_result)
    functional_strength_session.position = _key_present("position", mongo_result)
    return functional_strength_session

def _assigned_exercises_from_mongodb(mongo_result):

    assigned_exercise = models.soreness.AssignedExercise(_key_present("library_id", mongo_result))
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
        return None
