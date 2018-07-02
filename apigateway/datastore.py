from abc import abstractmethod, ABCMeta
from aws_xray_sdk.core import xray_recorder
# from boto3.dynamodb.conditions import Key, Attr
# from botocore.exceptions import ClientError
from decimal import Decimal
from datetime import datetime
from pymongo import MongoClient
import os

from exceptions import DuplicateEntityException
from models.soreness_and_injury import SorenessAndInjury
from config import get_mongo_collection


class Datastore(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def get(self, date, user_id=None, soreness=None, training_group_id=None):
        pass

    @abstractmethod
    def put(self, alerts):
        pass


class MongodbDatastore(Datastore):

    def put(self, items, allow_patch=False):
        if not isinstance(items, list):
            items = [items]
        try:
            for item in items:
                self._put_mongodb(item, allow_patch)
        except ClientError as e:
            if 'ConditionalCheckFailed' in str(e) and not allow_patch:
                raise DuplicateEntityException
            raise e

    def _put_mongodb(self, item, allow_patch=False):
        item = self.item_to_mongodb(item)
        mongo_database = get_mongo_database('SESSION')
        # mongo_collection= mongo_database[os.environ['MONGO_COLLECTION_SESSION']]
        mongo_collection= mongo_database['test']
        query = {'user_id': user_id, 'date': date}
        mongo_collection_date.replace_one(query, item, upsert=True)


    @staticmethod
    @abstractmethod
    def item_to_mongodb(item):
        pass


class SorenessDatastore(MongodbDatastore):
    @staticmethod
    def item_to_mongodb(soreness_and_injury):
        item = {
            'date': soreness_and_injury.date,
            'user_id': soreness_and_injury.user_id,
            'soreness': soreness_and_injury.soreness,
            'sleep_quality': soreness_and_injury.sleep_quality,
            'readiness': soreness_and_injury.readiness,
        }

        return {k: v for k, v in item.items() if v}


