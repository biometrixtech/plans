from aws_xray_sdk.core import xray_recorder
from config import get_mongo_collection
from models.asymmetry import SessionAsymmetry


class AsymmetryDatastore(object):
    mongo_collection = 'asymmetry'

    @xray_recorder.capture('datastore.AsymmetryDatastore.get')
    def get(self, session_id=None):
        return self._query_mongodb(session_id=session_id)

    def put(self, items):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item)
        except Exception as e:
            raise e

    @xray_recorder.capture('datastore.AsymmetryDatastore._query_mongodb')
    def _query_mongodb(self, session_id):
        mongo_collection = get_mongo_collection(self.mongo_collection)
        if session_id is not None:
            query = {'session_id': session_id}

            mongo_result = mongo_collection.find_one(query)

            if mongo_result is not None:
                return SessionAsymmetry.json_deserialise(mongo_result)
            else:
                return None

    @xray_recorder.capture('datastore.AsymmetryDatastore._put_mongodb')
    def _put_mongodb(self, item):
        item = item.json_serialise()

        mongo_collection = get_mongo_collection(self.mongo_collection)
        mongo_collection.replace_one({"session_id": item['session_id']},
                                     item,
                                     upsert=True)

