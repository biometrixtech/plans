from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import datetime

from decorators import authentication_required
from exceptions import InvalidSchemaException
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.session_datastore import SessionDatastore, _create_session
from models.daily_plan import DailyPlan
from utils import format_date, format_datetime, parse_datetime
app = Blueprint('daily_schedule', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.daily_schedule')
def handle_daily_schedule_create():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = format_date(request.json['event_date'])
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')

    user_id = request.json['user_id']
    if not _check_plan_exists():
        plan = DailyPlan(event_date=event_date)
        plan.user_id = user_id
        plan.last_updated = format_datetime(datetime.datetime.utcnow())
        DailyPlanDatastore().put(plan)

    sessions = request.json['sessions']
    session_store = SessionDatastore()
    for session in sessions:
        session_data = _get_session_data(session)
        item = _create_session(user_id=user_id,
                               session_type=session['session_type'],
                               data=session_data)
        session_store.insert(item, user_id=user_id, event_date=event_date)

    return {'message': 'success'}, 201


def _check_plan_exists():
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": request.json['user_id'],
                               "date": request.json['event_date']}) == 1:
        return True
    else:
        return False

def _get_session_data(session):
    date = format_date(parse_datetime(session['start_time']))
    time = format_datetime(session['start_time'])

    session_data = {"date": date,
                   "time": time,
                   "duration_minutes": session['duration']
                   }
    return session_data