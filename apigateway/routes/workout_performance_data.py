from flask import request, Blueprint

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, ApplicationException
from fathomapi.utils.xray import xray_recorder

# import boto3
import zipfile

app = Blueprint('performance_data', __name__)



@app.route('/<uuid:user_id>/upload', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.performance_data.upload')
def handle_performance_data_upload(user_id):
    print(user_id)

    if request.headers['Content-Type'] == 'application/zip':
        data = request.get_data()
        # zipfiles = zipfile.ZipFile(data)
        # print(zipfiles)

        # from cStringIO import StringIO
        # import zipfile
        # zfp = zipfile.ZipFile(StringIO(data), "r")


    else:
        raise ApplicationException(
            415,
            'UnsupportedContentType',
            'This endpoint requires the Content-Type application/zip with a zip file'
        )

    return {'message': 'Received'}, 202
