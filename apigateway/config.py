from pymongo import MongoClient
import os
import boto3
from botocore.exceptions import ClientError
from exceptions import ApplicationException

def get_mongo_config(instance):
    keys = ['host', 'replicaset', 'user', 'password', 'database']
    config = get_secret('mongo')
    print(config)
    # config = {k.lower(): os.environ.get('MONGO_{}_{}'.format(k.upper(), instance.upper()), None) for k in keys}
    return config


def get_mongo_database(instance):
    config = get_mongo_config(instance)
    mongo_client = MongoClient(
        config['host'],
        replicaset=config['replicaset'] if config['replicaset'] != '---' else None,
        ssl=True,
    )
    database = mongo_client[config['database']]
    database.authenticate(config['user'], config['password'], mechanism='SCRAM-SHA-1', source='admin')

    return database


def get_mongo_collection(instance, collection_override=None):
    config = get_mongo_config(instance)
    database = get_mongo_database(instance)
    return database[collection_override if collection_override is not None else config['collection']]


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