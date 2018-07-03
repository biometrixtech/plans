from pymongo import MongoClient
import os
import boto3
import json
from botocore.exceptions import ClientError
from exceptions import ApplicationException


def get_mongo_collection():
    keys = ['host', 'replicaset', 'user', 'password', 'database', 'collection']
    config = get_secret('mongo')
    mongo_client = MongoClient(
        config['host'],
        replicaset=config['replicaset'] if config['replicaset'] != '---' else None,
        ssl=True,
    )
    database = mongo_client[config['database']]
    database.authenticate(config['user'], config['password'], mechanism='SCRAM-SHA-1', source='admin')
    collection = database[config['collection']]

    return collection


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