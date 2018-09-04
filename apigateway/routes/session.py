from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import datetime

from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.session_datastore import SessionDatastore
# from datastore.post_session_survey import PostSessionSurveyDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException, NoSuchEntityException, ForbiddenException
from models.session import SessionType, SessionFactory, StrengthConditioningType
from models.post_session_survey import PostSessionSurvey, PostSurvey
from models.daily_plan import DailyPlan
from utils import parse_datetime, format_date, format_datetime, run_async
from config import get_mongo_collection
from models.athlete import SportName

app = Blueprint('session', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.session.create')
def handle_session_create():
    _validate_schema()

    event_date = parse_datetime(request.json['event_date'])
    session_type = request.json['session_type']
    user_id = request.json['user_id']
    try:
        sport_name = request.json['sport_name']
        sport_name = SportName(sport_name)
    except:
        sport_name = SportName(None)
    try:
        strength_and_conditioning_type = request.json['strength_and_conditioning_type']
        strength_and_conditioning_type = StrengthConditioningType(strength_and_conditioning_type)
    except:
        strength_and_conditioning_type = StrengthConditioningType(None)
    try:
        duration = request.json["duration"]
    except:
        raise InvalidSchemaException("Missing required parameter duration")
    description = request.json.get('description', "")
    plan_event_date = format_date(event_date)
    session_event_date = format_datetime(event_date)
    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = DailyPlanDatastore().get_last_sensor_sync(user_id, plan_event_date)
        
        DailyPlanDatastore().put(plan)

    session_data = {"sport_name": sport_name,
                    "strength_and_conditioning_type": strength_and_conditioning_type,
                    "description": description,
                    "duration_minutes": duration,
                    "event_date": session_event_date}
    if 'post_session_survey' in request.json:
        survey = PostSurvey(event_date=session_event_date,
                            survey=request.json['post_session_survey']
                            )
        session_data['post_session_survey'] = survey.json_serialise()

    session = _create_session(session_type, session_data)

    store = SessionDatastore()

    store.insert(item=session,
                 user_id=user_id,
                 event_date=plan_event_date
                 )
    plan = DailyPlanDatastore().get(user_id, plan_event_date, plan_event_date)[0]
    if not plan.sessions_planned:
        plan.sessions_planned = True
        DailyPlanDatastore().put(plan)

    update_plan(user_id, plan_event_date)
    return {'message': 'success'}, 201


@app.route('/<uuid:session_id>', methods=['DELETE'])
@authentication_required
@xray_recorder.capture('routes.session.delete')
def handle_session_delete(session_id):
    _validate_schema()

    event_date = parse_datetime(request.json['event_date'])
    session_type = request.json['session_type']
    user_id = request.json['user_id']
    plan_event_date = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException("Plan does not exist for the user to delete session")

    store = SessionDatastore()

    store.delete(user_id=user_id,
                 event_date=plan_event_date,
                 session_type=session_type,
                 session_id=session_id
                 )

    # update_plan(user_id, event_date)

    return {'message': 'success'}, 200


@app.route('/<uuid:session_id>', methods=['PATCH'])
@authentication_required
@xray_recorder.capture('routes.session.update')
def handle_session_update(session_id):
    _validate_schema()
    event_date = parse_datetime(request.json['event_date'])
    session_type = request.json['session_type']
    user_id = request.json['user_id']
    try:
        sport_name = request.json['sport_name']
        sport_name = SportName(sport_name)
    except:
        sport_name = SportName(None)
    try:
        strength_and_conditioning_type = request.json['strength_and_conditioning_type']
        strength_and_conditioning_type = StrengthConditioningType(strength_and_conditioning_type)
    except:
        strength_and_conditioning_type = StrengthConditioningType(None)
    session_event_date = format_datetime(event_date)
    plan_event_date = format_date(event_date)
    duration = request.json.get("duration", None)
    description = request.json.get('description', "")
    session_data = {"sport_name": sport_name,
                    "strength_and_conditioning_type": strength_and_conditioning_type,
                    "description": description,
                    "duration_minutes": duration,
                    "event_date": session_event_date}

    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException("Plan does not exist for the user to update session")
    if 'post_session_survey' in request.json:
        survey = PostSurvey(event_date_time=event_date,
                            survey=request.json['post_session_survey']
                            )
        session_data['post_session_survey'] = survey.json_serialise()

    store = SessionDatastore()
    session_obj = store.get(user_id=user_id, 
                            event_date=plan_event_date,
                            session_id=session_id
                            )[0]
    if session_obj.post_session_survey:
        raise ForbiddenException("Cannot modify a Session that's already logged")
    else:
        if session_type != session_obj.session_type().value:
            session_data = session_obj.json_serialise()
            session_data['id'] = session_data['session_id']
            del session_data['session_type'], session_data['session_id']
            session_obj = _create_session(session_type, session_data)
        _update_session(session_obj, session_data)
        store.update(session_obj,
                     user_id=user_id,
                     event_date=plan_event_date
                     )
    plan = DailyPlanDatastore().get(user_id, plan_event_date, plan_event_date)[0]
    if not plan.sessions_planned:
        plan.sessions_planned = True
        DailyPlanDatastore().put(plan)

    return {'message': 'success'}, 200


@app.route('/sensor_data', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.session.add_sensor_data')
def handle_session_sensor_data():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter user_id')
    if 'last_sensor_sync' not in request.json:
        raise InvalidSchemaException('Missing required parameter user_id')
    user_id = request.json['user_id']

    # update last_sensor_syc date
    last_sensor_sync = request.json['last_sensor_sync']
    sensor_sync_date = format_date(parse_datetime(last_sensor_sync))
    daly_plan_store = DailyPlanDatastore()
    if not _check_plan_exists(user_id, sensor_sync_date):
        plan = DailyPlan(event_date=sensor_sync_date)
        plan.user_id = user_id
    else:
        plan = daly_plan_store.get(user_id, sensor_sync_date, sensor_sync_date)[0]
    plan.last_sensor_sync = last_sensor_sync
    daly_plan_store.put(plan)
    updated_dates = [sensor_sync_date]

    session_store = SessionDatastore()

    sessions = request.json['sessions']
    for session in sessions:
        sensor_data = get_sensor_data(session)
        sensor_data['data_transferred'] = True
        plan_event_date = session.get('event_date', "")
        session_type = session.get('session_type', 0)
        if plan_event_date == "":
            plan_event_date = format_date(parse_datetime(sensor_data['sensor_start_date_time']))
        if not _check_plan_exists(user_id, plan_event_date):
            plan = DailyPlan(event_date=plan_event_date)
            plan.user_id = user_id
            plan.last_sensor_sync = last_sensor_sync
            daly_plan_store.put(plan)

        session_id = session.get('session_id', None)
        if session_id is None:
            session_obj = _create_session(session_type, sensor_data)
            session_store.insert(session_obj,
                                 user_id=user_id,
                                 event_date=plan_event_date
                                 )
        else:
            session_obj = session_store.get(user_id=user_id,
                                            event_date=plan_event_date,
                                            session_type=session_type,
                                            session_id=session_id)[0]
            _update_session(session_obj, sensor_data)
            session_store.update(session_obj,
                                 user_id=user_id,
                                 event_date=plan_event_date
                                 )
        if plan_event_date not in updated_dates:
            plan = daly_plan_store.get(user_id, plan_event_date, plan_event_date)[0]
            plan.last_sensor_sync = last_sensor_sync
            plan.sessions_planned = True
            daly_plan_store.put(plan)
            updated_dates.append(plan_event_date)


    # update_plan(user_id, event_date)
    plan = daly_plan_store.get(user_id, plan_event_date, plan_event_date)[0]
    survey_complete = plan.daily_readiness_survey_completed()
    landing_screen, nav_bar_indicator = plan.define_landing_screen()
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = survey_complete
    plan['landing_screen'] = landing_screen
    plan['nav_bar_indicator'] = nav_bar_indicator
    del plan['daily_readiness_survey'], plan['user_id']
    return {'message': 'success',
            'daily_plan': plan}, 200


@app.route('/typical', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.typical_sessions')
def handle_get_typical_sessions():
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

    dailyplan_store = DailyPlanDatastore()
    start_date = format_date(event_date - datetime.timedelta(days=14))
    end_date = format_date(event_date)
    plans = dailyplan_store.get(
                                user_id=user_id,
                                start_date=start_date,
                                end_date=end_date
                                )
    sessions = []
    for plan in plans:
        sessions.extend(plan.training_sessions)

    sessions = [s for s in sessions if s.event_date is not None]
    sessions = [{'sport_name': s.sport_name.value,
                 'strength_and_conditioning_type': s.strength_and_conditioning_type.value,
                 'session_type': s.session_type().value,
                 'event_date': format_datetime(s.event_date),
                 'duration': s.duration_minutes,
                 'count': 1} for s in sessions]
    sessions = sorted(sessions, key=lambda k: k['event_date'], reverse=True)
    filtered_sessions = []
    for session in sessions:
        if session['session_type'] == 1 and session['strength_and_conditioning_type'] is None:
            pass
        elif session['session_type'] in [0, 2, 3, 6] and session['sport_name'] is None:
            pass
        elif len(filtered_sessions) == 0:
            filtered_sessions.append(session)
        else:
            exists = [session['sport_name'] == s['sport_name'] and \
                      session['strength_and_conditioning_type'] == s['strength_and_conditioning_type'] and \
                      session['session_type'] == s['session_type'] for s in filtered_sessions]
            if any(exists):
                session = [filtered_sessions[i] for i in range(len(exists)) if exists[i]][0]
                session['count'] += 1
            else:
                filtered_sessions.append(session)
    filtered_sessions = sorted(filtered_sessions, key=lambda k: k['count'], reverse=True)

    return {'typical_sessions': filtered_sessions[0:4]}, 200

def get_sensor_data(session):
    start_time = format_datetime(session['start_time'])
    end_time = format_datetime(session['end_time'])
    low_duration = session['low_duration'] if session['low_duration'] is not None else 0
    mod_duration = session['mod_duration'] if session['mod_duration'] is not None else 0
    high_duration = session['high_duration'] if session['high_duration'] is not None else 0
    inactive_duration = session['inactive_duration'] if session['inactive_duration'] is not None else 0
    low_duration = round(low_duration / 60, 2)
    mod_duration = round(mod_duration / 60, 2)
    high_duration = round(high_duration / 60, 2)
    inactive_duration = round(inactive_duration / 60, 2)
    duration = low_duration + mod_duration + high_duration
    
    
    low_accel = session['low_accel'] if session['low_accel'] is not None else 0
    mod_accel = session['mod_accel'] if session['mod_accel'] is not None else 0
    high_accel = session['high_accel'] if session['high_accel'] is not None else 0
    inactive_accel = session['inactive_accel'] if session['inactive_accel'] is not None else 0
    total_accel = low_accel + mod_accel + high_accel
    
    sensor_data = {"sensor_start_date_time": start_time,
                   "sensor_end_date_time": end_time,
                   "duration_sensor": duration,
                   "low_intensity_minutes": low_duration,
                   "mod_intensity_minutes": mod_duration,
                   "high_intensity_minutes": high_duration,
                   "inactive_minutes": inactive_duration,
                   "external_load": total_accel,
                   "low_intensity_load": low_accel,
                   "mod_intensity_load": mod_accel,
                   "high_intensity_load": high_accel,
                   "inactive_load": inactive_accel
                   }
    return sensor_data


def _create_session(session_type, data):
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


def update_plan(user_id, event_date):
    run_async('POST', f"athlete/{user_id}/daily_plan", body={'event_date': event_date})


def _validate_schema():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        parse_datetime(request.json['event_date'])
    if 'session_type' not in request.json:
        raise InvalidSchemaException('Missing required parameter session_type')
    else:
        try:
            SessionType(request.json['session_type']).value
        except ValueError:
            raise InvalidSchemaException('session_type not recognized')
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter user_id')
