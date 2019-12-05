from flask import request, Blueprint
import datetime
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
# from models.asymmetry import AsymmetryType
from utils import parse_datetime

datastore_collection = DatastoreCollection()


app = Blueprint('three_sensor', __name__)


@app.route('/<uuid:user_id>/biomechanics_detail', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.three_sensor.get')
def handle_biomechanics_detail_get(user_id=None):
    asymmetry_type = 0

    if 'data_type' in request.json:
        asymmetry_type = request.json["data_type"]

    event_date = parse_datetime(request.json['event_date'])

    sessions = get_sessions_detail(user_id, event_date, asymmetry_type)

    return {'sessions': sessions}, 200


@app.route('/<uuid:user_id>/biomechanics_detail/<uuid:session_id>', methods=['GET'])
@require.authenticated.any
@xray_recorder.capture('routes.three_sensor.get_session')
def handle_biomechanics_detail_get_session(user_id=None, session_id=None):

    session = get_session_detail(session_id)

    return {'session': session}, 200


def get_sessions_detail(user_id, event_date, asymmetry_type_value):

    datastore = DatastoreCollection().asymmetry_datastore
    day_35 = (event_date - datetime.timedelta(days=35)).date()

    user_sessions = sorted(datastore.get(user_id=user_id, sessions=7, data_type=asymmetry_type_value), key=lambda i: i.event_date)
    user_sessions = [session for session in user_sessions if session.event_date.date() >= day_35]
    sessions = [s.json_serialise(api=True) for s in user_sessions]

    return sessions


def get_session_detail(session_id):

    datastore = DatastoreCollection().asymmetry_datastore

    session = datastore.get(session_id=session_id)
    if session is not None:
        return session.json_serialise(api=True, get_all=True)
    else:
        return {
                'session_id': session_id,
                'seconds_duration': None,
                'asymmetry': {
                    'apt': None,
                    'ankle_pitch': None,
                    'hip_drop': None,
                    'knee_valgus': None,
                    'hip_rotation': None
                }
        }
