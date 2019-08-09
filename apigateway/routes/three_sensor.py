from flask import request, Blueprint
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection

datastore_collection = DatastoreCollection()


app = Blueprint('three_sensor', __name__)


@app.route('/biomechanics_detail', methods=['POST'])
@require.authenticated.any
# @require.body({'event_date': str})
@xray_recorder.capture('routes.three_sensor.get')
def handle_biomechanics_detail_get(principal_id=None):
    # user_id = principal_id
    user_id = 'tester'
    datastore = DatastoreCollection().asymmetry_datastore

    user_sessions = datastore.get(user_id=user_id, sessions=7)
    sessions = [s.json_serialise(api=True) for s in user_sessions]

    return {'sessions': sessions}, 200
