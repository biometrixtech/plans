from flask import request, Blueprint
import io
import uuid
import boto3
from boto3.s3.transfer import TransferConfig
import base64
import datetime

from datastores.workout_datastore import WorkoutDatastore
from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import ApplicationException
from fathomapi.utils.xray import xray_recorder
from utils import format_datetime

_ingest_s3_bucket = boto3.resource('s3').Bucket(Config.get('PERFORMANCE_DATA_S3_BUCKET'))
# Need to use single threading to prevent X Ray tracing errors
_s3_config = TransferConfig(use_threads=False)

app = Blueprint('performance_data', __name__)


@app.route('/<uuid:user_id>/<string:program_id>/upload', methods=['PUT'])
@require.authenticated.any
@xray_recorder.capture('routes.performance_data.upload')
def handle_performance_data_upload(user_id, program_id):
    event_date_time = format_datetime(datetime.datetime.now())
    unique_key = f'http://session.fathomai.com/{user_id}_{program_id}_{event_date_time}'
    session_id = str(uuid.uuid5(uuid.NAMESPACE_URL, unique_key))

    if program_exists(program_id):
        if request.headers['Content-Type'] == 'application/octet-stream':
            data = base64.b64decode(request.get_data())
            api_version = Config.get('API_VERSION')
            if len(api_version.split('_')) > 2:
                api_version = '_'.join(api_version.split('_')[0:2])
            file_name = f'{api_version}_lambda_version/{user_id}/{program_id}/{session_id}.zip'
            f = io.BytesIO(data)
            _ingest_s3_bucket.upload_fileobj(f, file_name, Config=_s3_config)
        else:
            raise ApplicationException(
                415,
                'UnsupportedContentType',
                'This endpoint requires the Content-Type application/octet-stream with binary content'
            )
        return {'session_id': session_id}, 201
    else:
        return {'message': 'Workout Program with the provided ID does not exist'}, 404


def program_exists(program_id):
    if WorkoutDatastore().get(program_id=program_id, json=True) is not None:
        return True
    return False
