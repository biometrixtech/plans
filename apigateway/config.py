from pymongo import MongoClient
import os
import boto3
import json
from botocore.exceptions import ClientError
from exceptions import ApplicationException

global DATABASE


def get_mongo_collection(collection):
    mongo_collection = os.environ['MONGO_COLLECTION_' + collection.upper()]
    try:
        collection = DATABASE[mongo_collection]
    except Exception as e:
        print(e)
        database = get_mongo_database()
        collection = database[mongo_collection]

    return collection


def get_mongo_database():
    config = get_secret('mongo')
    os.environ["MONGO_HOST"] = config['host']
    os.environ["MONGO_REPLICASET"] = config['replicaset']
    os.environ["MONGO_DATABASE"] = config['database']
    os.environ["MONGO_USER"] = config['user']
    os.environ["MONGO_PASSWORD"] = config['password']
    os.environ["MONGO_COLLECTION_DAILYREADINESS"] = config['collection_dailyreadiness']
    os.environ["MONGO_COLLECTION_DAILYPLAN"] = config['collection_dailyplan']
    os.environ["MONGO_COLLECTION_EXERCISELIBRARY"] = config['collection_exerciselibrary']
    os.environ["MONGO_COLLECTION_TRAININGSCHEDULE"] = config['collection_trainingschedule']
    os.environ["MONGO_COLLECTION_ATHLETESEASON"] = config['collection_athleteseason']
    os.environ["MONGO_COLLECTION_ATHLETESTATS"] = config['collection_athletestats']
    host = os.environ['MONGO_HOST']
    replicaset =os.environ['MONGO_REPLICASET']
    user = os.environ['MONGO_USER']
    password = os.environ['MONGO_PASSWORD']
    mongo_database = os.environ['MONGO_DATABASE']
    # config = get_secret('mongo')
    mongo_client = MongoClient(
        host,
        replicaset=replicaset if replicaset != '---' else None,
        ssl=True,
        serverSelectionTimeoutMS=10000,
    )
    database = mongo_client[mongo_database]
    database.authenticate(user, password, mechanism='SCRAM-SHA-1', source='admin')
    return database

def get_secret(secret_name):
    client = boto3.client('secretsmanager')
    try:
        os.environ['ENVIRONMENT']
    except:
        os.environ['ENVIRONMENT'] = 'dev'
    try:
        secret_name = '/'.join(['plans', os.environ['ENVIRONMENT'], secret_name])
        get_secret_value_response = client.get_secret_value(SecretId=secret_name)
    except ClientError as e:
        raise ApplicationException('SecretsManagerError', json.dumps(e.response), 500)
    else:
        if 'SecretString' in get_secret_value_response:
            return json.loads(get_secret_value_response['SecretString'])
        else:
            return get_secret_value_response['SecretBinary']

DATABASE = get_mongo_database()
