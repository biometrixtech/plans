from pymongo import MongoClient
import os
import boto3
import json
from botocore.exceptions import ClientError

from fathomapi.api.config import Config
from fathomapi.utils.exceptions import ApplicationException


def get_mongo_collection(collection):
    database = get_mongo_database()
    mongo_collection = os.environ['MONGO_COLLECTION_' + collection.upper()]

    return database[mongo_collection]


_database = None


def get_mongo_database():
    global _database
    
    if _database is None:
        config = get_secret('mongo')
        for key, value in config.items():
            os.environ[f'MONGO_{key}'.upper()] = value
        # os.environ["MONGO_HOST"] = config['host']
        # os.environ["MONGO_REPLICASET"] = config['replicaset']
        # os.environ["MONGO_DATABASE"] = config['database']
        # os.environ["MONGO_USER"] = config['user']
        # os.environ["MONGO_PASSWORD"] = config['password']
        # os.environ["MONGO_COLLECTION_DAILYREADINESS"] = config['collection_dailyreadiness']
        # os.environ["MONGO_COLLECTION_DAILYPLAN"] = config['collection_dailyplan']
        # os.environ["MONGO_COLLECTION_EXERCISELIBRARY"] = config['collection_exerciselibrary']
        # # os.environ["MONGO_COLLECTION_TRAININGSCHEDULE"] = config['collection_trainingschedule']
        # # os.environ["MONGO_COLLECTION_ATHLETESEASON"] = config['collection_athleteseason']
        # os.environ["MONGO_COLLECTION_ATHLETESTATS"] = config['collection_athletestats']
        # os.environ["MONGO_COLLECTION_COMPLETEDEXERCISES"] = config['collection_completedexercises']
        # os.environ["MONGO_COLLECTION_APPLOGS"] = config['collection_applogs']
        # os.environ["MONGO_COLLECTION_HEARTRATE"] = config['collection_heartrate']
        # os.environ["MONGO_COLLECTION_SLEEPHISTORY"] = config['collection_sleephistory']
        # os.environ["MONGO_COLLECTION_CLEAREDSORENESS"] = config['collection_clearedsoreness']
        # os.environ["MONGO_COLLECTION_ASYMMETRY"] = config['collection_asymmetry']
        # os.environ["MONGO_COLLECTION_DAILYREADINESSTEST"] = config['collection_dailyreadinesstest']
        # os.environ["MONGO_COLLECTION_DAILYPLANTEST"] = config['collection_dailyplantest']
        # os.environ["MONGO_COLLECTION_ATHLETESTATSTEST"] = config['collection_athletestatstest']
        # os.environ["MONGO_COLLECTION_COMPLETEDEXERCISESTEST"] = config['collection_completedexercisestest']
        # os.environ["MONGO_COLLECTION_INJURYRISK"] = config['collection_injuryrisk']
        # os.environ["MONGO_COLLECTION_HISTINJURYRISK"] = config['collection_histinjuryrisk']
    
        host = Config.get('MONGO_HOST')
        replicaset = Config.get('MONGO_REPLICASET')
        user = Config.get('MONGO_USER')
        password = Config.get('MONGO_PASSWORD')
        mongo_database = Config.get('MONGO_DATABASE')
        mongo_client = MongoClient(
            host,
            replicaset=replicaset if replicaset != '---' else None,
            ssl=True,
            serverSelectionTimeoutMS=10000,
        )
        _database = mongo_client[mongo_database]
        _database.authenticate(user, password, mechanism='SCRAM-SHA-1', source='admin')
    
    return _database


def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    try:
        secret_name = '/'.join(['plans', Config.get('ENVIRONMENT'), secret_name])
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise ApplicationException('SecretsManagerError', json.dumps(e.response), 500)
    else:
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            return get_secret_value_response['SecretBinary']
