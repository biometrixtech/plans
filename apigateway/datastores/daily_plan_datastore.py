import datetime
from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from models.daily_plan import DailyPlan
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
        if stats_processing:
            mongo_cursor = mongo_collection.find(query, {'date': 1, user_id: 1, 'training_sessions': 1, 'daily_readiness_survey': 1})
        else:
            mongo_cursor = mongo_collection.find(query)
        ret = []

        for plan in mongo_cursor:
            daily_plan = DailyPlan.json_deserialise(plan, stats_processing)
            daily_plan.daily_readiness_survey = _daily_readiness_from_mongo(plan.get('daily_readiness_survey', None), user_id)
            ret.append(daily_plan)

        if len(ret) == 0 and not isinstance(user_id, list):
            plan = DailyPlan(event_date=end_date)
            plan.user_id = user_id
            # plan.last_sensor_sync = self.get_last_sensor_sync(user_id, end_date)
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


'''deprecated
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
    recovery_session.inhibit_exercises = [AssignedExercise.json_deserialise(s)
                                          for s in mongo_result['inhibit_exercises']]
    recovery_session.lengthen_exercises = [AssignedExercise.json_deserialise(s)
                                           for s in mongo_result['lengthen_exercises']]
    recovery_session.activate_exercises = [AssignedExercise.json_deserialise(s)
                                           for s in mongo_result['activate_exercises']]
    recovery_session.integrate_exercises = [AssignedExercise.json_deserialise(s)
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
'''


def _daily_readiness_from_mongo(mongo_result, user_id):
    if mongo_result is None:
        return None
    if isinstance(mongo_result, dict):
        return DailyReadiness(
                               event_date=mongo_result['event_date'],
                               user_id=user_id,
                               soreness=mongo_result['soreness'],
                               readiness=mongo_result['readiness'],
                               sleep_quality=mongo_result['sleep_quality'],
                               # wants_functional_strength=mongo_result.get('wants_functional_strength', False)
                             )
    elif isinstance(mongo_result, str):
        start_date = parse_date(mongo_result)
        end_date = start_date + datetime.timedelta(days=1)
        try:
            return DailyReadinessDatastore().get(user_id, start_date=start_date, end_date=end_date)[0]
        except NoSuchEntityException:
            return None
    else:
        return None
