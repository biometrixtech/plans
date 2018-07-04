from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import base64
# import boto3
# import datetime
import json
import re
import os
# import uuid

# from auth import get_accessory_id_from_auth
from datastore import SorenessDatastore
# from decorators import authentication_required
from exceptions import InvalidSchemaException, ApplicationException, NoSuchEntityException, DuplicateEntityException
from models.soreness_and_injury import SorenessAndInjury

app = Blueprint('soreness', __name__)


@app.route('/soreness', methods=['POST'])
# @authentication_required
# @xray_recorder.capture('routes.session.create')
def handle_soreness_create():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')

    # now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    soreness = SorenessAndInjury(
        user_id=request.json['user_id'],
        date=request.json['date'],
        soreness=request.json['soreness'],  # dailysoreness object array
        sleep_quality=request.json['sleep_quality'],
        readiness=request.json['readiness']

    )

    store = SorenessDatastore()
    try:
        store.put(soreness)
        return {'soreness': soreness}, 201
    except DuplicateEntityException:
        print(json.dumps({'message': 'soreness already created with id {}'.format(soreness.get_id())}))
        return {'session': get_session_by_id(session.get_id(), store)}, 201


# # @app.route('/<session_id>', methods=['GET'])
# # @authentication_required
# @xray_recorder.capture('routes.session.get')
# def handle_session_get(session_id):
#     session = get_session_by_id(session_id)
#     xray_recorder.current_segment().put_annotation('accessory_id', session.accessory_id)
#     xray_recorder.current_segment().put_annotation('user_id', session.user_id)
#     return {'session': session}


# @app.route('/<session_id>/upload', methods=['POST'])
# @authentication_required
# @xray_recorder.capture('routes.session.upload')
# def handle_session_upload(session_id):
#     session = get_session_by_id(session_id)
#     xray_recorder.current_segment().put_annotation('accessory_id', session.accessory_id)
#     xray_recorder.current_segment().put_annotation('sensor_id', ','.join(session.sensor_ids))
#     xray_recorder.current_segment().put_annotation('user_id', session.user_id)

#     # Need to use single threading to prevent X Ray tracing errors
#     config = TransferConfig(use_threads=False)
#     s3_transfer = S3Transfer(client=boto3.client('s3'), config=config)

#     if request.headers['Content-Type'] == 'application/octet-stream':
#         with open('/tmp/binary', 'wb') as f:
#             f.write(base64.b64decode(request.get_data()))

#     elif request.headers['Content-Type'] == 'application/json':
#         if isinstance(request.json, dict) and 'src' in request.json:
#             match = re.match('^s3://(?P<bucket>biometrix-[a-zA-Z0-9\-]+)/(?P<key>.+)$', request.json['src'])
#             if match is not None:
#                 # Download the file from the foreign S3 bucket
#                 print(json.dumps({'message': 'Downloading from s3://{}/{}'.format(match.group('bucket'), match.group('key'))}))
#                 s3_transfer.download_file(match.group('bucket'), match.group('key'), '/tmp/binary')

#     if not os.path.isfile('/tmp/binary'):
#         raise ApplicationException(
#             415,
#             'UnsupportedContentType',
#             'This endpoint requires the Content-Type application/octet-stream with a binary file content, or application/json with a `src` key referring to an S3 bucket'
#         )

#     # For now, we integrate with the ingest subservice by saving the file to the S3 ingest bucket.
#     s3_bucket = os.environ['S3_INGEST_BUCKET_NAME']
#     part_number = str(int(datetime.datetime.now().timestamp() * 1000))
#     s3_key = '{}_{}'.format(session.session_id, part_number)
#     print(json.dumps({'message': 'Uploading to s3://{}/{}'.format(s3_bucket, s3_key)}))
#     s3_transfer.upload_file('/tmp/binary', s3_bucket, s3_key)

#     return {'session': session}


# @app.route('/<session_id>', methods=['PATCH'])
# @authentication_required
# @xray_recorder.capture('routes.session.patch')
# def handle_session_patch(session_id):
#     store = SessionDatastore()
#     session = get_session_by_id(session_id, store)
#     xray_recorder.current_segment().put_annotation('accessory_id', session.accessory_id)
#     xray_recorder.current_segment().put_annotation('user_id', session.user_id)

#     if 'session_status' in request.json:
#         allowed_transitions = [
#             ('UPLOAD_IN_PROGRESS', 'UPLOAD_COMPLETE'),
#             ('PROCESSING_COMPLETE', 'UPLOAD_IN_PROGRESS'),
#             ('PROCESSING_FAILED', 'UPLOAD_IN_PROGRESS'),
#         ]
#         if (session.session_status, request.json['session_status']) in allowed_transitions:
#             session.session_status = request.json['session_status']
#         else:
#             # https://app.asana.com/0/654140198477919/673983533272813
#             return {'message': 'Currently at status {}, cannot change to {}'.format(session.session_status, request.json['session_status'])}, 200
#             # raise InvalidSchemaException('Transition from {} to {} is not allowed'.format(session.session_status, request.json['session_status']))

#     store.put(session, True)
#     return {'session': session}


# @xray_recorder.capture('routes.session.get_session_by_id')
# def get_session_by_id(session_id, store=None):
#     session_id = session_id.lower()

#     if not validate_uuid(session_id, 5) and not validate_uuid(session_id, 4):
#         raise InvalidSchemaException('session_id must be a uuid, not "{}"'.format(session_id))

#     store = store or SessionDatastore()
#     session = store.get(session_id=session_id)
#     if len(session) == 1:
#         return session[0]
#     else:
#         raise NoSuchEntityException()


# def validate_uuid(uuid_string, version):
#     try:
#         val = uuid.UUID(uuid_string, version=version)
#         # If the uuid_string is a valid hex code, but an invalid uuid4, the UUID.__init__
#         # will convert it to a valid uuid4. This is bad for validation purposes.
#         return val.hex == uuid_string.replace('-', '')
#     except ValueError:
#         # If it's a value error, then the string is not a valid hex code for a UUID.
#         return False
