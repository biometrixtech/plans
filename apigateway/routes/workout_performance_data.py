from flask import request, Blueprint

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import ApplicationException
from fathomapi.utils.xray import xray_recorder

# import boto3
# import zipfile
import io
import boto3
from boto3.s3.transfer import TransferConfig
import base64


app = Blueprint('performance_data', __name__)

_ingest_s3_bucket = boto3.resource('s3').Bucket('fathom-otf')
# Need to use single threading to prevent X Ray tracing errors
_s3_config = TransferConfig(use_threads=False)

@app.route('/<uuid:user_id>/upload', methods=['PUT'])
@require.authenticated.any
@xray_recorder.capture('routes.performance_data.upload')
def handle_performance_data_upload(user_id):
    # if request.headers['Content-Type'] == 'application/zip':
    #     # data = request.get_data().encode()
    #     data = base64.b64decode(request.get_data())
    #     print(type(data))
    #     # f = io.StringIO(data)
    #     f = io.BytesIO(data)
    #     _ingest_s3_bucket.upload_fileobj(f, 'test_file.zip', Config=_s3_config)
    if request.headers['Content-Type'] == 'application/octet-stream':
        data = base64.b64decode(request.get_data())
        f = io.BytesIO(data)
        _ingest_s3_bucket.upload_fileobj(f, 'test_file_octet.zip', Config=_s3_config)
    else:
        raise ApplicationException(
            415,
            'UnsupportedContentType',
            'This endpoint requires the Content-Type application/zip with a zip file'
        )

    return {'message': 'Received'}, 202
