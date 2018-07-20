from pymongo import MongoClient
import os
import boto3
import json
from aws_xray_sdk.core import xray_recorder
from botocore.exceptions import ClientError
# from exceptions import ApplicationException


@xray_recorder.capture('config.get_mongo')
def get_mongo_collection(collection):
    host = os.environ['MONGO_HOST']
    replicaset =os.environ['MONGO_REPLICASET']
    user = os.environ['MONGO_USER']
    password = os.environ['MONGO_PASSWORD']
    mongo_database = os.environ['MONGO_DATABASE']
    mongo_collection = os.environ['MONGO_COLLECTION_' + collection.upper()]
    # config = get_secret('mongo')
    mongo_client = MongoClient(
        host,
        replicaset=replicaset if replicaset != '---' else None,
        ssl=True,
        serverSelectionTimeoutMS=10000,
    )
    database = mongo_client[mongo_database]
    database.authenticate(user, password, mechanism='SCRAM-SHA-1', source='admin')
    collection = database[mongo_collection]

    return collection

@xray_recorder.capture('config.get_secret')
def get_secret(secret_name):
    client = boto3.client('secretsmanager')
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
