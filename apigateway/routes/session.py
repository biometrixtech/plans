from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint

from datastores.session_datastore import SessionDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException
from models.post_session_survey import PostSessionSurvey
from models.session import SessionType, SessionFactory
from utils import format_date, run_async


app = Blueprint('session', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.session.create')
def handle_session_create():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = format_date(request.json['event_date'])
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')
    if 'session_type' not in request.json:
        raise InvalidSchemaException('Missing required parameter session_type')
    else:
        try:
            session_type = SessionType(request.json['session_type']).value
        except ValueError:
            raise InvalidSchemaException('session_type not recognized')
    description = request.json.get('description', "")

    session = SessionFactory()
    session = session.create(SessionType(session_type))
    session.description = description

    store = SessionDatastore()

    store.insert(user_id=request.json['user_id'],
                 event_date=event_date,
                 item=session)

    return {'message': 'success'}, 201


@app.route('/<uuid:session_id>', methods=['DELETE'])
@authentication_required
@xray_recorder.capture('routes.session.delete')
def handle_session_delete(session_id):
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = format_date(request.json['event_date'])
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')
    if 'session_type' not in request.json:
        raise InvalidSchemaException('Missing required parameter session_type')
    else:
        try:
            session_type = SessionType(request.json['session_type']).value
        except ValueError:
            raise InvalidSchemaException('session_type not recognized')

    store = SessionDatastore()

    store.delete(user_id=request.json['user_id'],
                 event_date=event_date,
                 session_type=session_type,
                 session_id=session_id)

    update_plan()

    return {'message': 'success'}, 200


@app.route('/sensor_data', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.session.add_sensor_data')
def handle_session_sensor_data():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = format_date(request.json['event_date'])
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')
    if 'session_type' not in request.json:
        session_type = 0
    else:
        try:
            session_type = SessionType(request.json['session_type']).value
        except ValueError:
            raise InvalidSchemaException('session_type not recognized')

    store = SessionDatastore()

    sensor_data = request.json['sensor_data']
    sensor_data['data_transferred'] = True

    # we're assuming that the session does not exist
    store.upsert(user_id=request.json['user_id'],
                 event_date=event_date,
                 session_type=session_type,
                 data=sensor_data)

    update_plan()

    return {'message': 'success'}, 200


def update_plan():
    endpoint = "athlete/{}/daily_plan".format(request.json['user_id'])
    headers = {'Authorization': request.headers['Authorization'],
                'Content-Type': 'applicaiton/json'}
    run_async(endpoint, method='POST', body=None, headers=headers)
 