from flask import request, Blueprint
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from models.soreness import CompletedExercise
from utils import format_date, parse_datetime, format_datetime
from config import get_mongo_collection

datastore_collection = DatastoreCollection()
daily_plan_datastore = datastore_collection.daily_plan_datastore
completed_exercise_datastore = datastore_collection.completed_exercise_datastore

app = Blueprint('insights', __name__)


@app.route('/read', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.active_recovery.exercise_modalities.complete')
def handle_insights_read(principal_id=None):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    # insight = request.json['insight']
    # insight.read_date_time = event_date

    return {'message': 'success'}, 200

  