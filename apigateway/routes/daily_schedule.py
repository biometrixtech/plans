from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import datetime

from decorators import authentication_required
from exceptions import InvalidSchemaException
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.session_datastore import SessionDatastore
from models.daily_plan import DailyPlan
from models.session import SessionFactory, SessionType
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
        current_time = parse_datetime(request.json['event_date'])
        event_date = format_date(current_time)
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')

    session_store = SessionDatastore()
    user_id = request.json['user_id']
    past_sessions = []

    if not _check_plan_exists(user_id, event_date):
        plan = DailyPlan(event_date=event_date)
        plan.user_id = user_id
        plan.last_updated = format_datetime(datetime.datetime.utcnow())
        DailyPlanDatastore().put(plan)
    else:
        daily_plan = DailyPlanDatastore().get(user_id, start_date=event_date, end_date=event_date)[0]
        sessions = daily_plan.get_past_sessions(current_time)
        past_sessions.extend([s.json_serialise() for s in sessions])
        

    sessions = request.json['sessions']
    for session in sessions:
        session_data = _get_session_data(session)
        item = _create_session(user_id=user_id,
                               session_type=session['session_type'],
                               data=session_data)
        if item.event_date < current_time:
            past_sessions.append(item.json_serialise())
        session_store.insert(item, user_id=user_id, event_date=event_date)

    past_sessions = _filter_response_data(past_sessions)
    return {'past_sessions': past_sessions}, 201


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False

def _get_session_data(session):
    event_date = parse_datetime(session['event_date'])
    duration_minutes = session.get('duration', None)
    if duration_minutes is None:
        raise InvalidSchemaException("duration is missing for the session")

    session_data = {"event_date": event_date,
                    "duration_minutes": duration_minutes,
                    "description": session.get("description", "")
                   }
    return session_data

def _create_session(user_id, session_type, data):
    factory = SessionFactory()
    session = factory.create(SessionType(session_type))
    for key, value in data.items():
        setattr(session, key, value)
    return session


def _update_session(session, data):
    for key, value in data.items():
        setattr(session, key, value)

def _filter_response_data(past_sessions):
    keys_to_return = ['session_id', 'event_date', 'description', 'duration_minutes']
    past_sessions = [{ key: s[key] for key in keys_to_return } for s in past_sessions]
    return past_sessions
