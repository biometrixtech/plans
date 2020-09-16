import boto3
# from botocore.exceptions import ResourceNotFoundException
import json
import pymongo
import os
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

def _secret_exists(secret_name):
    client = boto3.client(service_name="secretsmanager")
    try:
        result = client.describe_secret(SecretId=secret_name)
    except client.exceptions.ResourceNotFoundException as e:
        return False
    return True


def create_secret(service='plans', secret_type='mongo', env='demo', copy_from_env=None, secrets=None):
    if secret_type == 'mongo':
        description = "access to mongodb on atlas"
    elif secret_type == 'service_jwt_key':
        description = 'RS256 key for signing JWTs'
    else:
        description = ""
    client = boto3.client(service_name="secretsmanager")
    secret_name = f'{service}/{env}/{secret_type}'
    if copy_from_env is not None:
        original_secret_name =  f'{service}/{copy_from_env}/{secret_type}'
        secret_string = json.loads(client.get_secret_value(SecretId=original_secret_name)['SecretString'])
    else:
        secret_string = secrets or {}
    # check if already exists
    if not _secret_exists(secret_name):
        result = client.create_secret(
                Name=secret_name,
                Description=description,
                SecretString=json.dumps(secret_string)
        )
        print('here')
    else:
        print('secret already exists')

def update_secrets(env='demo', secret='mongo'):

    client = boto3.client(service_name="secretsmanager")
    secret_name = f'plans/{env}/{secret}'

    # get original secrets
    secrets = json.loads(client.get_secret_value(SecretId=secret_name)['SecretString'])
    if secret == 'mongo':
        secrets_to_update = {
            "collection_movementprep": "movementPrep",
            "collection_mobilitywod": "mobilityWOD",
            "collection_responsiverecovery": "responsiveRecovery",
            "collection_symptom": "symptom",
            "collection_trainingsession": "trainingSession",
            "collection_athletestats": "userStats",
            "collection_workoutprogram": "workoutProgram"
        }
    elif secret == 'provider_info':
        secrets_to_update = {
            'consolidate_dosage': "true"
        }
    else:
        secrets_to_update = {}
    if env == 'demo' and secret=='mongo':
        for key, value in secrets_to_update.items():
            secrets_to_update[key] = f'{value}Demo'

    # update secrets
    secrets.update(secrets_to_update)

    client.update_secret(SecretId=secret_name, SecretString=json.dumps(secrets))


def add_new_secret(env='demo', secret='mongo', new_secrets=None):

    client = boto3.client(service_name="secretsmanager")
    secret_name = f'plans/{env}/{secret}'

    # get original secrets
    secrets = json.loads(client.get_secret_value(SecretId=secret_name)['SecretString'])
    if new_secrets is None:
        new_secrets = {}
    if env == 'demo' and secret=='mongo':
        for key, value in new_secrets.items():
            new_secrets[key] = f'{value}Demo'

    # update secrets
    secrets.update(new_secrets)

    client.update_secret(SecretId=secret_name, SecretString=json.dumps(secrets))


def create_mongo_collection(env="demo"):
    os.environ['ENVIRONMENT'] = env
    from config import get_mongo_database
    database = get_mongo_database()
    # my_collection = database['movementPrepDemo']
    # my_collection.create_index("movement_prep_id")
    # my_collection.create_index([("user_id", pymongo.ASCENDING),
    #                             ("created_date_time", pymongo.ASCENDING)])


    # my_collection = database['mobilityWODDemo']
    # my_collection.create_index("mobility_wod_id")
    # my_collection.create_index([("user_id", pymongo.ASCENDING),
    #                             ("created_date_time", pymongo.ASCENDING)])

    # my_collection = database['responsiveRecoveryDemo']
    # my_collection.create_index("responsive_recovery_id")
    # my_collection.create_index([("user_id", pymongo.ASCENDING),
    #                             ("created_date_time", pymongo.ASCENDING)])
    #
    # my_collection = database['trainingSessionDemo']
    # my_collection.create_index("session_id")
    # my_collection.create_index([("user_id", pymongo.ASCENDING),
    #                             ("event_date", pymongo.ASCENDING)])
    #
    #
    # my_collection = database['workoutProgramDemo']
    # my_collection.create_index("session_id")
    # my_collection.create_index([("user_id", pymongo.ASCENDING),
    #                             ("event_date_time", pymongo.ASCENDING)])

    # my_collection = database['responsiveRecoveryDemo']
    # my_collection.create_index("responsive_recovery_id")
    # my_collection.create_index([("user_id", pymongo.ASCENDING),
    #                             ("created_date_time", pymongo.ASCENDING)])

    # my_collection = database['symptomDemo']
    # my_collection.create_index([("user_id", pymongo.ASCENDING),
    #                             ("reported_date_time", pymongo.ASCENDING)])

    # my_collection = database['userStatsDemo']
    # my_collection.create_index("athlete_id")
    # my_collection.create_index("event_date")
    # my_collection.create_index("api_version")

    # my_collection = database['injuryRisk']
    # my_collection.create_index("user_id")



    my_collection = database['plannedWorkoutLoad']
    my_collection.create_index([("user_profile_id", pymongo.ASCENDING),
                                ("workout_id", pymongo.ASCENDING),
                                ("program_id", pymongo.ASCENDING)])

    my_collection = database['completedSessionDetails']
    my_collection.create_index([("user_id", pymongo.ASCENDING),
                                ("workout_id", pymongo.ASCENDING),
                                ("provider_id", pymongo.ASCENDING)])

if __name__ == '__main__':
    # update_secrets(secret='provider_info')
    # for env in ['dev', 'demo', 'test']:
    # for env in ['dev']:
    #     # add_new_secret(env=env, secret='provider_info', new_secrets={'hr_rpe_model_filename': 'hr_rpe.joblib',
    #     #                                                              'model_bucket': 'biometrix-globalmodels',
    #     #                                                              'bodyweight_ratio_model_filename': 'bodyweight_ratio.joblib'})
    #     add_new_secret(env=env, secret='mongo', new_secrets={'collection_completedsessiondetails': 'completedSessionDetails',
    #                                                          'collection_plannedworkoutload': 'plannedWorkoutLoad'})

#     secrets = {
#     "p": "-CJqKFE5Y-jN25qSVHFXtBi10NofV37OegUrO4FO7x8Fg4VkgLkwWE-JiTEvivgqqZrfaezNv3UKXG7UmBbaTZkkFf6656uSAiTIhDo8ochU6yPxATtnlIxdYrndsUZxFDEIaUGQOkuLWbuxzBx1bhKZcJhqJot0zf7rNvUAxPE",
#     "kty": "RSA",
#     "q": "pJyahZ8Zt43WbaZRgQR1rTmgmG-n-EbZPWXEQVxoTffE5HT3CY9XAM6lBQQOI5Vs_EWTuCIWux4C8BEc7EA4WJodMIicfOLRiMFOzAnBeMLd6HATw1KIjPOt4f9SqJOd1shrfDm8uQOdqJHaNhe2Ya9jbAiHTjrw7kupMSwCP_0",
#     "d": "MHehuMKOTbsI4aNE2DTWtnnmqhUyFhiT--g00PyTQql_UsE0p3sjank9ZgG7ZrMzPyqz_JCaAbjXXOJMyDbDQlZbrg3qChGXCn9-LpY9EhMnxicS0kDppNblOYVryhYEmko9MzuG36-3TR0ttjeISUyKTH5KzwSAFX46yDj7T2j2d5QIpd8mAOJmEiaBtQJIbTHVaVEHqdqBrZib9VtByXBGcQattpWcRACH9LYBGiUkWyxpox5Oubj8Krq4C9RoUjX8d1J-k6OBP06FDvO4vIJK0y8AfBwFXIAt7TdtQUokKcEVu46Y0r6CHhARYCorNJjeL4OYX-kLen25TSMhAQ",
#     "e": "AQAB",
#     "use": "sig",
#     "kid": "demo_001",
#     "qi": "kit2dZfCUR9ec8BsWBSwABTz0L1FbJMFDaOzpZr5AEsw-ORtRSbRa6alVlEeKpnumSyyhxLL6M6-U_KmcusRuDHQ2NMFEr0D72Nh1Yje9jjYkSB_EH36vT4vlaB-NNC5NW3ARgIed2itBJh58gW8Qwz9UQR2e3myHIpLUsWwb88",
#     "dp": "IHxA8a5QmSfta4a9CZkdJlLl2sXzvHy5g3gRxOSU9PFWw3U_Ryr3jVg8ZV2vH76Ft1azUSbTePFVvew0oQS859PYyZhj19i6cNVn-we00Glt1KsL7mFcmjIWN8qln4PdYgtZUo5m13r0b3cHO_Wt2g9NT1Rk8U7op99r4_IHe8E",
#     "alg": "RS256",
#     "dq": "dGJE3jSe-ihOczgkaBO_H7qe0Sggmml9LuvE1nF_TaDglKYeA6RU3z07b1Burrn3VGXdC1MOvz141kNDL8Y4EGzmNmpgOewkOYxzKc-7-qXMP4r-bhrscLvZNPBQgN_duP37ANnRlP35ejWlEpmxWV-n67ob8DO8JL9Z4Go9LQ",
#     "n": "n43WwLyN9_47uf8oUc5MX-K_SuPQniaAVy__6Zduu7Oxj_pVmW7Hv8OcnWKE6vHG75C7Up1greRxpUmGOv3vje80x33d2IsZTtVeJ95oUUXSwKqt32_su9p6UlUk-gFSC5wagj8w9SD1NYAP4tn4FuZhICfNjrpKtiqyKBDqqKuiaUERpb0q_2q3E-PvU5jHaqUKOPBRtlrdOZX05JkjH1sLW3v6_0Y27uv--RXXf6Fm0czZUh6TDwKs_b44Cn1Up8nfxnDTr8xHZg_2eeh_DciZ784WHxk_ZDyTcHmTuijpez5K-W1pbMdx4FLa9e1O1307YTxzBRDBHtKXSBvxLQ"
# }
    create_mongo_collection(env='dev')
#     create_secret(service='users', env='demo', secret_type='service_jwt_key', secrets=secrets)
#     pass