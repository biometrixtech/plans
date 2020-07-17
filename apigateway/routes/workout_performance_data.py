from flask import request, Blueprint
import io
import uuid
import boto3
from boto3.s3.transfer import TransferConfig
import base64
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import ApplicationException
from fathomapi.utils.xray import xray_recorder


app = Blueprint('performance_data', __name__)


@app.route('/<uuid:user_id>/upload', methods=['PUT'])
@require.authenticated.any
@xray_recorder.capture('routes.performance_data.upload')
def handle_performance_data_upload(user_id):
    session_id = str(uuid.uuid4())

    _ingest_s3_bucket = boto3.resource('s3').Bucket('fathom-otf2')
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

    return {'message': 'Received'}, 202
