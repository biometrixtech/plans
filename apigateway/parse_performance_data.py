import boto3
import io
from logic.performance_data_parser import PerformanceDataParser

from datastores.datastore_collection import DatastoreCollection
from routes.environments import consolidated_dosage
from routes.responsive_recovery import get_responsive_recovery
from utils import parse_datetime

consolidated = consolidated_dosage()

datastore_collection = DatastoreCollection()
user_stats_datastore = datastore_collection.user_stats_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore
workout_program_datastore = datastore_collection.workout_program_datastore
responsive_recovery_datastore = datastore_collection.responsive_recovery_datastore


def lambda_handler(event, _):
    print(f"Starting unzipping for file {event['Records'][0]['s3']['object']['key']}")
    s3_key = ""
    s3_bucket = ""
    try:
        print(event)
        record = event['Records'][0]
        s3_bucket = record['s3']['bucket']['name']
        s3_key = record['s3']['object']['key']

        ids = s3_key.split('/')
        user_id = ids[-3]
        program_id = ids[-2]
        session_id = ids[-1]
        s3_resource = boto3.resource('s3')
        s3_object = s3_resource.Object(s3_bucket, s3_key)

        fileobj = s3_object.get()
        print('Got Fileobj')
        body = fileobj["Body"].read()
        print('Read Content')
        content = io.BytesIO(body)
        print('Converted Content')

        data_parser = PerformanceDataParser()
        data_parser.parse_fileobj(content, program_id)
        workout_data = data_parser.get_completed_workout(user_id)
        workout_data['session_id'] = session_id

        session = {
            'session_id': 'session_id',
            'event_date': workout_data['event_date_time'],
            'end_date': workout_data['workout_sections'][-1]['end_date_time'],
            'session_type': 7,
            'duration': workout_data['duration'],
            'workout_program_module': workout_data
        }
        # use session to create responsive recovery
        #
        responsive_recovery = get_responsive_recovery(user_id, event_date_time=parse_datetime(workout_data['event_date_time']), session=session)
        print(responsive_recovery.json_serialise(api=True, consolidated=True))


    except Exception as e:
        print(e)
        print(f'Error getting object {s3_key} from bucket {s3_bucket}. Make sure they exist and your bucket is in the same region as this function.')
        raise e


# def get_responsive_recovery(user_id, event_date_time, timezone, session, user_age):
#
#     # set up processing
#     user_stats = user_stats_datastore.get(athlete_id=user_id)
#     if user_stats is None:
#         user_stats = UserStats(user_id)
#         user_stats.event_date = event_date_time
#     user_stats.api_version = Config.get('API_VERSION')
#     user_stats.timezone = timezone
#     api_processor = APIProcessing(
#             user_id,
#             event_date_time,
#             user_stats=user_stats,
#             datastore_collection=datastore_collection
#     )
#
#     api_processor.create_session_from_survey(session)
#
#     if len(api_processor.workout_programs) > 0:
#         workout_program_datastore.put(api_processor.workout_programs)
#
#     if len(api_processor.heart_rate_data) > 0:
#         heart_rate_datastore.put(api_processor.heart_rate_data)
#
#     responsive_recovery = api_processor.create_activity(
#             activity_type='responsive_recovery'
#     )