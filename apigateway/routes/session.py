from flask import request, Blueprint
import datetime

from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.session_datastore import SessionDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException, ForbiddenException
from fathomapi.utils.xray import xray_recorder
from models.session import SessionType, SessionFactory
from models.daily_plan import DailyPlan
from utils import parse_datetime, format_date, format_datetime
from config import get_mongo_collection
from logic.survey_processing import SurveyProcessing

app = Blueprint('session', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.session.create')
def handle_session_create():
    _validate_schema()
    user_id = request.json['user_id']
    athlete_stats = AthleteStatsDatastore().get(athlete_id=user_id)
    session = SurveyProcessing().create_session_from_survey(request.json, athlete_stats=athlete_stats)
    plan_event_date = format_date(session.event_date)

    if 'post_session_survey' in request.json:
        # update session_RPE
        if athlete_stats.session_RPE is not None:
            athlete_stats.session_RPE = max(session.post_session_survey.RPE, athlete_stats.session_RPE)
        else:
            athlete_stats.session_RPE = session.post_session_survey.RPE
        athlete_stats.session_RPE_event_date = plan_event_date

        # update severe soreness and severe pain
        soreness = session.post_session_survey.soreness
        severe_soreness = [s for s in soreness if not s.pain]
        severe_pain = [s for s in soreness if s.pain]
        athlete_stats.daily_severe_soreness_event_date = plan_event_date
        athlete_stats.daily_severe_pain_event_date = plan_event_date
        athlete_stats.update_post_session_soreness(severe_soreness)
        athlete_stats.update_post_session_pain(severe_pain)
        athlete_stats.update_daily_soreness()
        athlete_stats.update_daily_pain()
        # update historic soreness
        for s in soreness:
            athlete_stats.update_historic_soreness(s, plan_event_date)
    AthleteStatsDatastore().put(athlete_stats)

    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = DailyPlanDatastore().get_last_sensor_sync(user_id, plan_event_date)
        
        DailyPlanDatastore().put(plan)

    # session = _create_session(session_type, session_data)

    store = SessionDatastore()

    store.insert(item=session,
                 user_id=user_id,
                 event_date=plan_event_date
                 )
    plan = DailyPlanDatastore().get(user_id, plan_event_date, plan_event_date)[0]
    if not plan.sessions_planned or plan.session_from_readiness:
        plan.sessions_planned = True
        plan.session_from_readiness = False
        DailyPlanDatastore().put(plan)

    update_plan(user_id, session.event_date)
    return {'message': 'success'}, 201


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
    _validate_schema()
    user_id = request.json['user_id']
    session_data = SurveyProcessing().create_session_from_survey(request.json, return_dict=True)
    plan_event_date = format_date(session_data['event_date'])
    session_type = request.json['session_type']

    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException("Plan does not exist for the user to update session")
    store = SessionDatastore()
    session_obj = store.get(user_id=user_id, 
                            event_date=plan_event_date,
                            session_id=session_id
                            )[0]
    if session_obj.post_session_survey:
        raise ForbiddenException("Cannot modify a Session that's already logged")
    else:
        if session_type != session_obj.session_type().value:
            session_data_existing = session_obj.json_serialise()
            session_data_existing['id'] = session_data_existing['session_id']
            del session_data_existing['session_type'], session_data_existing['session_id']
            session_obj = _create_session(session_type, session_data_existing)
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
    body={'event_date': format_date(event_date),
          'last_updated': format_datetime(event_date)}
    Service('plans', Config.get('API_VERSION')).call_apigateway_async('POST', f"athlete/{user_id}/daily_plan", body=body)


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
