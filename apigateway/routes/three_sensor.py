from flask import request, Blueprint
import datetime
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from utils import parse_datetime

datastore_collection = DatastoreCollection()


app = Blueprint('three_sensor', __name__)


@app.route('/biomechanics_detail', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.three_sensor.get')
def handle_biomechanics_detail_get(principal_id=None):
    user_id = principal_id
    datastore = DatastoreCollection().asymmetry_datastore
    event_date = parse_datetime(request.json['event_date'])
    day_35 = (event_date - datetime.timedelta(days=35)).date()

    user_sessions = sorted(datastore.get(user_id=user_id, sessions=7), key=lambda i:i.event_date)
    user_sessions = [session for session in user_sessions if session.event_date.date() >= day_35]
    sessions = [s.json_serialise(api=True) for s in user_sessions]

    return {'sessions': sessions}, 200
