import boto3
import io

from logic.performance_data_parser import PerformanceDataParser
# from routes.environments import consolidated_dosage
from routes.responsive_recovery import get_responsive_recovery
from utils import parse_datetime

# consolidated = consolidated_dosage()


def lambda_handler(event, _):
    print(f"Starting unzipping for file {event['Records'][0]['s3']['object']['key']}")
    s3_key = ""
    s3_bucket = ""
    try:
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
        responsive_recovery = get_responsive_recovery(user_id, event_date_time=parse_datetime(workout_data['event_date_time']), session=session)
        # print(responsive_recovery.json_serialise(api=True, consolidated=True))
        # TODO: content delivery


    except Exception as e:
        print(e)
        print(f'Error getting object {s3_key} from bucket {s3_bucket}. Make sure they exist and your bucket is in the same region as this function.')
        raise e
