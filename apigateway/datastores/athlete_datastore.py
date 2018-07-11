from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from logic.training import DailyPlan

class DailyPlanDatastore(object):
    def get(self, user_id=None, start_date=None, end_date=None, collection=None):
        return self._query_mongodb(user_id, start_date, end_date, collection)

    def put(self, items, collection):
        if not isinstance(items, list):
            items = [items]
        for item in items:
            self._put_dynamodb(item, collection)

    @xray_recorder.capture('datastore.DailyPlanDatastore._query_mongodb')
    def _query_mongodb(self, user_id, start_date, end_date, collection):
        mongo_collection = get_mongo_collection(collection)
        query0 = {'user_id': user_id, 'date': {'$gte': start_date, '$lte': end_date}}
        query1 = {'_id': 0, 'last_updated': 0, 'user_id': 0}
        mongo_cursor = mongo_collection.find(query0, query1)
        ret = []
        for plan in mongo_cursor:
            daily_plan = DailyPlan(date=plan['date'])
            daily_plan.practice_sessions = plan['practice_sessions']
            daily_plan.strength_conditioning_sessions = plan['cross_training_session']
            daily_plan.games = plan['games']
            daily_plan.tournaments = plan['tournaments']
            daily_plan.recovery_am = plan['recovery_am']
            daily_plan.recovery_pm = plan['recovery_pm']
            daily_plan.corrective_sessions = plan['corrective_sessions']
            daily_plan.bump_up_sessions = plan['bump_up_sessions']
            daily_plan.daily_readiness_survey = plan.get('daily_readiness_survey', None)
            daily_plan.updated = plan.get('updated', None)
            daily_plan.last_updated = plan.get('last_update', None)
            ret.append(daily_plan)
        return ret

    @xray_recorder.capture('datastore.DailyPlanDatastore._put_mongodb')
    def _put_mongodb(self, item, collection):
        pass

    @staticmethod
    def item_to_response(daily_plan):
        item = {
            'date': daily_plan['date'],
            'practice_sessions': daily_plan['practice_sessions'],
            'recovery_am': daily_plan['recovery_am'],
            'recovery_pm': daily_plan['recovery_pm'],
            'games': daily_plan['games'],
            'tournaments': daily_plan['tournaments'],
            'strength_conditioning_sessions': daily_plan['strength_conditioning_sessions'],
            'corrective_sessions': daily_plan['corrective_sessions'],
            'bump_up_sessions': daily_plan['bump_up_sessions'],
        }
        return item