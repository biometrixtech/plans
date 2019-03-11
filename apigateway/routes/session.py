from flask import request, Blueprint
import datetime
import os

from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.session_datastore import SessionDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from datastores.heart_rate_datastore import HeartRateDatastore
# from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from models.session import SessionType, SessionSource
from models.daily_plan import DailyPlan
from utils import parse_datetime, format_date, format_datetime
from config import get_mongo_collection
from logic.survey_processing import SurveyProcessing, create_session, update_session, create_plan
from logic.athlete_status_processing import AthleteStatusProcessing

app = Blueprint('session', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.session.create')
def handle_session_create():
    user_id = request.json['user_id']
    event_date = parse_datetime(request.json['event_date'])
    plan_update_required = False
    athlete_stats = AthleteStatsDatastore().get(athlete_id=user_id)
    plan_event_date = format_date(event_date)
    survey_processor = SurveyProcessing(user_id, event_date, athlete_stats)
    for session in request.json['sessions']:
        if session is None:
            continue
        survey_processor.create_session_from_survey(session)

    # update daily pain and soreness in athlete_stats
    survey_processor.patch_daily_and_historic_soreness(survey='post_session')

    # check that not all sessions are deleted or ignored
    for session in survey_processor.sessions:
        if not session.deleted and not session.ignored:
            plan_update_required = True
            break

    # check if plan exists, if not create a new one and save it to database, also check if existing one needs updating flags
    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = DailyPlanDatastore().get_last_sensor_sync(user_id, plan_event_date)
        DailyPlanDatastore().put(plan)
    else:
        plan = DailyPlanDatastore().get(user_id, plan_event_date, plan_event_date)[0]
        if plan_update_required and (not plan.sessions_planned or plan.session_from_readiness):
            plan.sessions_planned = True
            plan.session_from_readiness = False
            DailyPlanDatastore().put(plan)

    # save all the sessions to database
    store = SessionDatastore()
    for session in survey_processor.sessions:
        store.insert(item=session,
                     user_id=user_id,
                     event_date=plan_event_date
                     )
    # save updated athlete stats
    if survey_processor.athlete_stats is not None:
        AthleteStatsDatastore().put(survey_processor.athlete_stats)
    # save heart_rate_data if it exists in any of the sessions
    if len(survey_processor.heart_rate_data) > 0:
        HeartRateDatastore().put(survey_processor.heart_rate_data)
    # update plan
    if plan_update_required:
        plan = create_plan(user_id, event_date)
    # update users database if health data received
    if "health_sync_date" in request.json and request.json['health_sync_date'] is not None:
        Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                endpoint=f"user/{user_id}",
                                                                                body={"health_sync_date": request.json['health_sync_date']})
    return {'daily_plans': [plan]}, 201


@app.route('/<uuid:session_id>', methods=['DELETE'])
@require.authenticated.any
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
@require.authenticated.any
@xray_recorder.capture('routes.session.update')
def handle_session_update(session_id):
    user_id = request.json['user_id']
    event_date = parse_datetime(request.json['event_date'])
    plan_event_date = format_date(event_date)

    # create session
    survey_processor = SurveyProcessing(user_id, event_date)
    session = request.json['sessions'][0]
    survey_processor.create_session_from_survey(session)
    new_session = survey_processor.sessions[0]

    # get existing session
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException("Plan does not exist for the user to update session")
    store = SessionDatastore()
    session_obj = store.get(user_id=user_id,
                            event_date=plan_event_date,
                            session_id=session_id
                            )[0]
    # update existing session with new data
    if session_obj.source == SessionSource.user:
        session_obj.event_date = new_session.event_date
        session_obj.end_date = new_session.end_date
        session_obj.duration_health = new_session.duration_health
        session_obj.calories = new_session.calories
        session_obj.distance = new_session.distance
        session_obj.source = SessionSource.combined
        store.update(session_obj,
                     user_id=user_id,
                     event_date=plan_event_date
                     )
    # write hr data if it exists
    if len(survey_processor.heart_rate_data) > 0:
        HeartRateDatastore().put(survey_processor.heart_rate_data)
    if "health_sync_date" in request.json and request.json['health_sync_date'] is not None:
        Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                endpoint=f"user/{user_id}",
                                                                                body={"health_sync_date": request.json['health_sync_date']})

    return {'message': 'success'}, 200


@app.route('/sensor_data', methods=['POST'])
@require.authenticated.any
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
            session_obj = create_session(session_type, sensor_data)
            session_store.insert(session_obj,
                                 user_id=user_id,
                                 event_date=plan_event_date
                                 )
        else:
            session_obj = session_store.get(user_id=user_id,
                                            event_date=plan_event_date,
                                            session_type=session_type,
                                            session_id=session_id)[0]
            update_session(session_obj, sensor_data)
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
    plan = daly_plan_store.get(user_id, sensor_sync_date, sensor_sync_date)[0]
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
@require.authenticated.any
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

    filtered_sessions = AthleteStatusProcessing(user_id, event_date).get_typical_sessions()
    
    return {'typical_sessions': filtered_sessions}, 200


@app.route('/no_sessions', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.no_sessions_planned')
def handle_no_sessions_planned():
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

    plan_event_date = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = DailyPlanDatastore().get_last_sensor_sync(user_id, plan_event_date)
        plan.sessions_planned = False
        DailyPlanDatastore().put(plan)
    else:
        plan = DailyPlanDatastore().get(user_id, plan_event_date, plan_event_date)[0]
        if plan.sessions_planned:
            plan.sessions_planned = False
            DailyPlanDatastore().put(plan)


    survey_complete = plan.daily_readiness_survey_completed()
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = survey_complete
    if plan['pre_recovery_completed']:
        plan['landing_screen'] = 1.0
        plan['nav_bar_indicator'] = 1.0
    else:
        plan['landing_screen'] = 1.0
        plan['nav_bar_indicator'] = 0.0

    del plan['daily_readiness_survey'], plan['user_id']
    return {'message': 'success',
            'daily_plan': plan}, 200


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


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False


# def update_plan(user_id, event_date):
#     body={'event_date': format_date(event_date),
#           'last_updated': format_datetime(event_date)}
#     Service('plans', Config.get('API_VERSION')).call_apigateway_async('POST', f"athlete/{user_id}/daily_plan", body=body)


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
