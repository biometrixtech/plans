from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint

from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.session_datastore import SessionDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException, NoSuchEntityException
from models.session import SessionType, SessionFactory
from models.daily_plan import DailyPlan
from utils import parse_datetime, format_date, format_datetime, run_async
from config import get_mongo_collection
from logic.athlete import SportName

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
        event_date = format_datetime(request.json['event_date'])
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')
    if 'session_type' not in request.json:
        raise InvalidSchemaException('Missing required parameter session_type')
    else:
        try:
            session_type = SessionType(request.json['session_type']).value
        except ValueError:
            raise InvalidSchemaException('session_type not recognized')
    user_id = request.json['user_id']
    sport = request.json['sport']
    sport = SportName(sport).name
    duration = request.json["duration"]
    description = request.json.get('description', "")
    date = format_date(parse_datetime(event_date))
    if not _check_plan_exists(user_id, date):
        plan = DailyPlan(event_date=date)
        plan.user_id = user_id
        DailyPlanDatastore().put(plan)
    session_data = {"sport": sport,
                    "description": description,
                    "duration_minutes": duration,
                    "event_date": event_date}

    session = _create_session(user_id, session_type, session_data)

    store = SessionDatastore()

    store.insert(item=session,
                 user_id=user_id,
                 event_date=date
                 )

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
        event_date = format_date(parse_datetime(request.json['event_date']))
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')
    if 'session_type' not in request.json:
        raise InvalidSchemaException('Missing required parameter session_type')
    else:
        try:
            session_type = SessionType(request.json['session_type']).value
        except ValueError:
            raise InvalidSchemaException('session_type not recognized')
    user_id = request.json['user_id']
    if not _check_plan_exists(user_id, event_date):
        raise NoSuchEntityException("Plan does not exist for the user to delete session")

    store = SessionDatastore()

    store.delete(user_id=user_id,
                 event_date=event_date,
                 session_type=session_type,
                 session_id=session_id)

    # update_plan(event_date)

    return {'message': 'success'}, 200


@app.route('/sensor_data', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.session.add_sensor_data')
def handle_session_sensor_data():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter user_id')
    user_id = request.json['user_id']

    store = SessionDatastore()

    sessions = request.json['sessions']
    for session in sessions:
        sensor_data = get_sensor_data(session)
        sensor_data['data_transferred'] = True
        event_date = session.get('event_date', "")
        session_type = session.get('session_type', 0)
        if event_date == "":
            event_date = format_date(parse_datetime(sensor_data['sensor_start_date_time']))
        if not _check_plan_exists(user_id, event_date):
            plan = DailyPlan(event_date=event_date)
            plan.user_id = user_id
            DailyPlanDatastore().put(plan)

        session_id = session.get('session_id', None)
        if session_id is None:
            session_obj = _create_session(user_id, session_type, sensor_data)
            store.insert(session_obj, user_id, event_date)
        else:
            session_obj = store.get(user_id, event_date, session_type, session_id)[0]
            _update_session(session_obj, sensor_data)
            store.update(session_obj, user_id, event_date)

    # update_plan(event_date)

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


def _create_session(user_id, session_type, data):
    factory = SessionFactory()
    session = factory.create(SessionType(session_type))
    _update_session(session, data)
    # for key, value in data.items():
    #     setattr(session, key, value)
    return session

def _update_session(session, data):
    for key, value in data.items():
        setattr(session, key, value)


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False

def update_plan(event_date):
    endpoint = "athlete/{}/daily_plan".format(request.json['user_id'])
    headers = {'Authorization': request.headers['Authorization'],
                'Content-Type': 'application/json'}
    body = {'event_date': event_date}
    run_async(endpoint, method='POST', body=body, headers=headers)
 