from flask import request, Blueprint
import datetime
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from models.asymmetry import AsymmetryType
from utils import parse_datetime

datastore_collection = DatastoreCollection()


app = Blueprint('three_sensor', __name__)


@app.route('/<uuid:user_id>/biomechanics_detail', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.three_sensor.get')
def handle_biomechanics_detail_get(user_id=None):
    asymmetry_type = 0

    if request.json['data_type']:
        asymmetry_type = request.json["data_type"]

    event_date = parse_datetime(request.json['event_date'])

    sessions = get_sessions_detail(user_id, event_date, asymmetry_type)

    return {'sessions': sessions}, 200


def get_sessions_detail(user_id, event_date, asymmetry_type_value):

    datastore = DatastoreCollection().asymmetry_datastore
    day_35 = (event_date - datetime.timedelta(days=35)).date()

    user_sessions = sorted(datastore.get(user_id=user_id, sessions=7, data_type=asymmetry_type_value), key=lambda i:i.event_date)
    user_sessions = [session for session in user_sessions if session.event_date.date() >= day_35]
    sessions = [s.json_serialise(api=True) for s in user_sessions]

    return sessions

