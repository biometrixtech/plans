from flask import request, Blueprint
import datetime

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.session_datastore import SessionDatastore
from models.daily_plan import DailyPlan
from models.session import SessionFactory, SessionType
from utils import format_date, format_datetime, parse_datetime
from models.sport import SportName

app = Blueprint('daily_schedule', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.daily_schedule')
def handle_daily_schedule_create():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = parse_datetime(request.json['event_date'])
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        user_id = request.json['user_id']

    cutoff_time = 3
    if event_date.hour < cutoff_time:
        plan_event_date = event_date - datetime.timedelta(days=1)
    else:
        plan_event_date = event_date

    plan_event_date = format_date(plan_event_date)
    session_store = SessionDatastore()
    past_sessions = []

    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_updated = format_datetime(datetime.datetime.utcnow())
        DailyPlanDatastore().put(plan)
    else:
        daily_plan = DailyPlanDatastore().get(user_id,
                                              start_date=plan_event_date,
                                              end_date=plan_event_date)[0]
        sessions = daily_plan.get_past_sessions(event_date)
        past_sessions.extend([s.json_serialise() for s in sessions])
        

    sessions = request.json['sessions']
    for session in sessions:
        session_data = _get_session_data(session)
        item = _create_session(user_id=user_id,
                               session_type=session['session_type'],
                               data=session_data)
        if item.event_date < event_date:
            past_sessions.append(item.json_serialise())
        session_store.insert(item, user_id=user_id, event_date=plan_event_date)

    past_sessions = _filter_response_data(past_sessions)
    return {'past_sessions': past_sessions}, 201


@app.route('/typical', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.typical_schedule')
def handle_get_typical_schedule():
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = parse_datetime(request.json['event_date'])
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        user_id = request.json['user_id']

    cutoff_time = 3

    if event_date.hour < cutoff_time:
        event_date -= datetime.timedelta(days=1)

    day_of_week = event_date.weekday()
    dailyplan_store = DailyPlanDatastore()
    start_date = format_date(event_date - datetime.timedelta(days=14))
    end_date = format_date(event_date - datetime.timedelta(days=7))
    plans = dailyplan_store.get(
                                user_id=user_id,
                                start_date=start_date,
                                end_date=end_date,
                                day_of_week=day_of_week
                                )
    sessions = []
    for plan in plans:
        sessions.extend(plan.training_sessions)
        sessions.extend(plan.practice_sessions)
        sessions.extend(plan.games)
        sessions.extend(plan.strength_conditioning_sessions)
        sessions.extend(plan.tournaments)

    sessions = [s for s in sessions if s.event_date is not None]
    sessions = [{'sport_name': s.sport_name.value,
                 'session_type': s.session_type().value,
                 'event_date': format_datetime(s.event_date),
                 'duration': s.duration_minutes} for s in sessions]
    sessions = sorted(sessions, key=lambda k: k['event_date'], reverse=True)
    filtered_sessions = []
    for session in sessions:
        if len(filtered_sessions) == 0:
            filtered_sessions.append(session)
        else:
            exists = [session['sport_name'] == s['sport_name'] and \
                      session['session_type'] == s['session_type'] for s in filtered_sessions]
            if any(exists):
                pass
            else:
                filtered_sessions.append(session)

    return {'typical_sessions': sessions}, 200



def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False

def _get_session_data(session):
    event_date = parse_datetime(session['event_date'])
    try:
        sport_name = session['sport_name']
        sport_name = SportName(sport_name)
    except:
        sport_name = SportName(None)
    try:
        duration_minutes = session["duration"]
    except:
        raise InvalidSchemaException("duration is missing for the session")

    session_data = {"event_date": event_date,
                    "sport_name": sport_name,    
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
