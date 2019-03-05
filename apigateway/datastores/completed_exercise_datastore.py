from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.soreness import CompletedExercise, CompletedExerciseSummary
from utils import format_datetime
from fathomapi.utils.exceptions import InvalidSchemaException


class CompletedExerciseDatastore(object):
    def __init__(self, mongo_collection='completedexercises'):
        self.mongo_collection = mongo_collection

    @xray_recorder.capture('datastore.CompletedExerciseDatastore.get')
    def get(self, athlete_id, start_date, end_date, get_summary=True):
        return self._query_mongodb(athlete_id, start_date, end_date, get_summary)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    def delete(self, items=None, athlete_id=None, start_date=None, end_date=None):
        if items is None and athlete_id is None:
            raise InvalidSchemaException("Need to provide one of items and athlete_id")
        if items is not None:
            if not isinstance(items, list):
                items = [items]
            for item in items:
                self._delete_mongodb(item=item, athlete_id=athlete_id, start_date=start_date, end_date=end_date)
        else:
            self._delete_mongodb(item=items, athlete_id=athlete_id, start_date=start_date, end_date=end_date)

    @xray_recorder.capture('datastore.CompletedExerciseDatastore._query_mongodb')
    def _query_mongodb(self, athlete_id, start_date, end_date, get_summary):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        ret = []
        query = {"$and": [{'athlete_id': athlete_id, 'event_date': {'$gte': start_date, '$lte': end_date}}]}

        if not get_summary:

            mongo_cursor = mongo_collection.find(query)

            for mongo_result in mongo_cursor:

                completed_exercise = CompletedExercise(athlete_id=mongo_result['athlete_id'],
                                                       exercise_id=mongo_result['exercise_id'],
                                                       event_date=mongo_result['event_date'])
                ret.append(completed_exercise)

        else:
            mongo_cursor = mongo_collection.aggregate([
                {'$match': query},
                {"$group": {"_id": {"athlete_id": "$athlete_id", "exercise_id": "$exercise_id"},
                            "exposures": {"$sum": 1}}}])

            agg_list = list(mongo_cursor)
            for mongo_result in agg_list:
                completed_exercise_summary = CompletedExerciseSummary(athlete_id=mongo_result['_id']['athlete_id'],
                                                                      exercise_id=mongo_result['_id']['exercise_id'],
                                                                      exposures=mongo_result['exposures'])
                ret.append(completed_exercise_summary)

        return ret

    @xray_recorder.capture('datastore.CompletedExerciseDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.insert_one(item)

    @xray_recorder.capture('datastore.CompletedExerciseDatastore._delete_mongodb')
    def _delete_mongodb(self, item, athlete_id, start_date, end_date):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        query = {}
        if item is not None:
            query['athlete_id'] = item.athlete_id
            query['event_date'] = format_datetime(item.event_date)
        else:
            if isinstance(athlete_id, list):
                query['athlete_id'] = {'$in': athlete_id}
            else:
                query['athlete_id'] = athlete_id
            if start_date is not None and end_date is not None:
                query['event_date'] = {'$gte': start_date, '$lte': end_date}

        if len(query) > 0:
            mongo_collection.delete_many(query)
