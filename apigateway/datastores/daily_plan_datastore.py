import datetime
from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException
from models.daily_plan import DailyPlan
import models.session as session
import models.soreness
from models.post_session_survey import PostSurvey
from models.daily_readiness import DailyReadiness
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from utils import parse_date


class DailyPlanDatastore(object):
    def __init__(self, mongo_collection='dailyplan'):
        self.mongo_collection = mongo_collection

    def get(self, user_id=None, start_date=None, end_date=None, day_of_week=None, stats_processing=False):
        return self._query_mongodb(user_id, start_date, end_date, day_of_week, stats_processing)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def delete(self, items=None, user_id=None, start_date=None, end_date=None):
        if items is None and user_id is None:
            raise InvalidSchemaException("Need to provide one of items and user_id")
        if items is not None:
            if not isinstance(items, list):
                items = [items]
            for item in items:
                self._delete_mongodb(item=item, user_id=user_id, start_date=start_date, end_date=end_date)
        else:
            self._delete_mongodb(item=items, user_id=user_id, start_date=start_date, end_date=end_date)

    @xray_recorder.capture('datastore.DailyPlanDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date, day_of_week, stats_processing):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {}
        if isinstance(user_id, list):
            query['user_id'] = {'$in': user_id}
        else:
            query['user_id'] = user_id
        if start_date is not None and end_date is not None:
            query['date'] = {'$gte': start_date, '$lte': end_date}
        if day_of_week is not None:
            query['day_of_week'] = day_of_week
        mongo_cursor = mongo_collection.find(query)
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
            if not stats_processing:
                daily_plan.pre_recovery = _recovery_session_from_mongodb(plan['pre_recovery']) if plan.get('pre_recovery', None) is not None else None
                daily_plan.post_recovery = _recovery_session_from_mongodb(plan['post_recovery']) if plan.get('post_recovery', None) is not None else None
                daily_plan.completed_post_recovery_sessions = \
                    [_recovery_session_from_mongodb(s) for s in plan.get('completed_post_recovery_sessions', [])]
                daily_plan.functional_strength_session = \
                    _functional_strength_session_from_mongodb(plan['functional_strength_session']) if plan.get('functional_strength_session', None) is not None else None
                # daily_plan.corrective_sessions = \
                #    [_external_session_from_mongodb(s, session.SessionType.corrective)
                #     for s in plan['corrective_sessions']]
            daily_plan.bump_up_sessions = \
                [_external_session_from_mongodb(s, session.SessionType.bump_up)
                 for s in plan.get('bump_up_sessions', [])]
            daily_plan.daily_readiness_survey = _daily_readiness_from_mongo(plan.get('daily_readiness_survey', None), user_id)
            daily_plan.updated = plan.get('updated', None)
            daily_plan.last_updated = plan.get('last_updated', None)
            daily_plan.pre_recovery_completed = plan.get('pre_recovery_completed', False)
            daily_plan.post_recovery_completed = plan.get('post_recovery_completed', False)
            daily_plan.last_sensor_sync = plan.get('last_sensor_sync', None)
            daily_plan.sessions_planned = plan.get('sessions_planned', True)
            daily_plan.functional_strength_eligible = plan.get('functional_strength_eligible', False)
            daily_plan.completed_functional_strength_sessions = plan.get('completed_functional_strength_sessions', 0)
            daily_plan.functional_strength_completed = plan.get('functional_strength_completed', False)
            daily_plan.session_from_readiness = plan.get('session_from_readiness', False)
            daily_plan.sessions_planned_readiness = plan.get('sessions_planned_readiness', True)
            ret.append(daily_plan)

        if len(ret) == 0 and not isinstance(user_id, list):
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

    @xray_recorder.capture('datastore.DailyPlanDatastore._delete_mongodb')
    def _delete_mongodb(self, item, user_id, start_date, end_date):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {}
        if item is not None:
            query['user_id'] = item.user_id
            query['date'] = item.event_date
        else:
            if isinstance(user_id, list):
                query['user_id'] = {'$in': user_id}
            else:
                query['user_id'] = user_id
            if start_date is not None and end_date is not None:
                query['date'] = {'$gte': start_date, '$lte': end_date}

        if len(query) > 0:
            mongo_collection.delete_many(query)

    def get_last_sensor_sync(self, user_id, event_date):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query0 = {'user_id': user_id, 'date': {'$lte': event_date}, 'last_sensor_sync': {'$exists': True, '$ne': None}}
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
                        "created_date",
                        "event_date",
                        "end_date",
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
                        "deleted",
                        "ignored",
                        "duration_health",
                        "calories",
                        "distance",
                        "source"]
    for key in attrs_from_mongo:
        setattr(mongo_session, key, mongo_result.get(key, None))
    if "post_session_survey" in mongo_result and mongo_result["post_session_survey"] is not None:
        mongo_session.post_session_survey = PostSurvey(mongo_result["post_session_survey"], mongo_result["post_session_survey"]["event_date"])
        mongo_session.session_RPE = mongo_session.post_session_survey.RPE if mongo_session.post_session_survey.RPE is not None else None
    else:
        mongo_session.post_session_survey = None

    return mongo_session


def _recovery_session_from_mongodb(mongo_result):

    recovery_session = session.RecoverySession()
    recovery_session.start_date = mongo_result.get("start_date", None)
    recovery_session.event_date = mongo_result.get("event_date", None)
    recovery_session.impact_score = mongo_result.get("impact_score", 0)
    recovery_session.goal_text = mongo_result.get("goal_text", "")
    recovery_session.why_text = mongo_result.get("why_text", "")
    recovery_session.duration_minutes = mongo_result.get("minutes_duration", 0)
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
    functional_strength_session.equipment_required = mongo_result.get("equipment_required", [])
    functional_strength_session.warm_up = [_assigned_exercises_from_mongodb(s)
                                           for s in mongo_result['warm_up']]
    functional_strength_session.dynamic_movement = [_assigned_exercises_from_mongodb(s)
                                                    for s in mongo_result['dynamic_movement']]
    functional_strength_session.stability_work = [_assigned_exercises_from_mongodb(s)
                                                  for s in mongo_result['stability_work']]
    functional_strength_session.victory_lap = [_assigned_exercises_from_mongodb(s)
                                               for s in mongo_result['victory_lap']]
    functional_strength_session.duration_minutes = mongo_result.get("minutes_duration", 0)
    functional_strength_session.warm_up_target_minutes = mongo_result.get("warm_up_target_minutes", 0)
    functional_strength_session.dynamic_movement_target_minutes = mongo_result.get("dynamic_movement_target_minutes", 0)
    functional_strength_session.stability_work_target_minutes = mongo_result.get("stability_work_target_minutes", 0)
    functional_strength_session.victory_lap_target_minutes = mongo_result.get("victory_lap_target_minutes", 0)
    functional_strength_session.warm_up_max_percentage = mongo_result.get("warm_up_max_percentage", 0)
    functional_strength_session.dynamic_movement_max_percentage = mongo_result.get("dynamic_movement_max_percentage", 0)
    functional_strength_session.stability_work_max_percentage = mongo_result.get("stability_work_max_percentage", 0)
    functional_strength_session.victory_lap_max_percentage = mongo_result.get("victory_lap_max_percentage", 0)
    functional_strength_session.completed = mongo_result.get("completed", False)
    functional_strength_session.start_date = mongo_result.get("start_date", None)
    functional_strength_session.event_date = mongo_result.get("event_date", None)
    functional_strength_session.sport_name = mongo_result.get("sport_name", None)
    functional_strength_session.position = mongo_result.get("position", None)
    return functional_strength_session


def _assigned_exercises_from_mongodb(mongo_result):

    assigned_exercise = models.soreness.AssignedExercise(mongo_result.get("library_id", None))
    assigned_exercise.exercise.name = mongo_result.get("name", "")
    assigned_exercise.exercise.display_name = mongo_result.get("display_name", "")
    assigned_exercise.exercise.youtube_id = mongo_result.get("youtube_id", "")
    assigned_exercise.exercise.description = mongo_result.get("description", "")
    assigned_exercise.exercise.bilateral = mongo_result.get("bilateral", False)
    assigned_exercise.exercise.unit_of_measure = mongo_result.get("unit_of_measure", None)
    assigned_exercise.position_order = mongo_result.get("position_order", 0)
    assigned_exercise.reps_assigned = mongo_result.get("reps_assigned", 0)
    assigned_exercise.sets_assigned = mongo_result.get("sets_assigned", 0)
    assigned_exercise.exercise.seconds_per_set = mongo_result.get("seconds_per_set", 0)
    assigned_exercise.exercise.seconds_per_rep = mongo_result.get("seconds_per_rep", 0)
    assigned_exercise.goal_text = mongo_result.get("goal_text", "")
    assigned_exercise.equipment_required = mongo_result.get("equipment_required", [])
    return assigned_exercise


def _daily_readiness_from_mongo(mongo_result, user_id):
    if mongo_result is None:
        return None
    if isinstance(mongo_result, dict):
        return DailyReadiness(
                               event_date=mongo_result['event_date'],
                               user_id=mongo_result['user_id'],
                               soreness=mongo_result['soreness'],
                               readiness=mongo_result['readiness'],
                               sleep_quality=mongo_result['sleep_quality'],
                               wants_functional_strength=mongo_result.get('wants_functional_strength', False)
                             )
    elif isinstance(mongo_result, str):
        start_date = parse_date(mongo_result)
        end_date = start_date + datetime.timedelta(days=1)
        return DailyReadinessDatastore().get(user_id, start_date=start_date, end_date=end_date)[0]
    else:
        return None
