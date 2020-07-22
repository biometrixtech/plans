from flask import request, Blueprint
import io
import uuid
import boto3
from boto3.s3.transfer import TransferConfig
import base64
import datetime

from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import ApplicationException
from fathomapi.utils.xray import xray_recorder
from utils import format_datetime


app = Blueprint('performance_data', __name__)


@app.route('/<uuid:user_id>/<string:program_id>/upload', methods=['PUT'])
@require.authenticated.any
@xray_recorder.capture('routes.performance_data.upload')
def handle_performance_data_upload(user_id, program_id):
    event_date_time = format_datetime(datetime.datetime.now())
    unique_key = f'http://session.fathomai.com/{user_id}_{program_id}_{event_date_time}'
    session_id = str(uuid.uuid5(uuid.NAMESPACE_URL, unique_key))

    # session_id = str(uuid.uuid4())

    _ingest_s3_bucket = boto3.resource('s3').Bucket(Config.get('PERFORMANCE_DATA_S3_BUCKET'))
    # _ingest_s3_bucket = boto3.resource('s3').Bucket('fathom-otf2')
    # Need to use single threading to prevent X Ray tracing errors
    _s3_config = TransferConfig(use_threads=False)
    if request.headers['Content-Type'] == 'application/octet-stream':
        data = base64.b64decode(request.get_data())
        f = io.BytesIO(data)
        _ingest_s3_bucket.upload_fileobj(f, f'input/{user_id}/{session_id}.zip', Config=_s3_config)
    else:
        raise ApplicationException(
            415,
            'UnsupportedContentType',
            'This endpoint requires the Content-Type application/zip with a zip file'
        )

    return {'session_id': session_id}, 201
