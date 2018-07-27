from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import datetime

from datastores.session_datastore import SessionDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException
from models.session import SessionType, SessionFactory
from utils import parse_datetime, format_date, format_datetime, run_async


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

    store = SessionDatastore()

    sessions = request.json['sessions']
    for session in sessions:
        sensor_data = get_sensor_data(session)
        sensor_data['data_transferred'] = True
        event_date = session.get('event_date', "")
        if event_date == "":
            event_date = datetime.datetime.strptime(sensor_data['sensor_start_date_time'], "%Y-%m-%dT%H:%M:%SZ").date()
            event_date = datetime.datetime.strftime(event_date, "%Y-%m-%d")

        # For now we're assuming session does not exist and just inserting a new session
        # without trying to match (upsert is essentially insert)
        store.upsert(user_id=request.json['user_id'],
                     event_date=event_date,
                     session_type=0,
                     data=sensor_data)

    update_plan()

    return {'message': 'success'}, 200


def get_sensor_data(session):
    start_time = format_datetime(session['start_time'])
    end_time = format_datetime(session['end_time'])

    low_duration = session['low_duration'] / 60
    mod_duration = session['mod_duration'] / 60
    high_duration = session['high_duration'] / 60
    duration = low_duration + mod_duration + high_duration
    
    
    low_accel = session['low_accel'] * 1000
    mod_accel = session['mod_accel'] * 1000
    high_accel = session['high_accel'] * 1000
    total_accel = low_accel + mod_accel + high_accel
    
    sensor_data = {"sensor_start_date_time": start_time,
                   "sensor_end_date_time": end_time,
                   "duration_sensor": duration,
                   "low_intensity_minutes": low_duration,
                   "mod_intensity_minutes": mod_duration,
                   "high_intensity_minutes": high_duration,
                   "external_load": total_accel,
                   "low_intensity_load": low_accel,
                   "mod_intensity_load": mod_accel,
                   "high_intensity_load": high_accel
                   }
    return sensor_data
#


def update_plan():
    endpoint = "athlete/{}/daily_plan".format(request.json['user_id'])
    headers = {'Authorization': request.headers['Authorization'],
                'Content-Type': 'applicaiton/json'}
    run_async(endpoint, method='POST', body=None, headers=headers)
 