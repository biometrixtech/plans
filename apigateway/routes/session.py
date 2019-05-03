from flask import request, Blueprint
import os
import copy

from datastores.datastore_collection import DatastoreCollection
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from models.session import SessionType, SessionSource
from models.daily_plan import DailyPlan
from utils import parse_datetime, format_date, format_datetime
from config import get_mongo_collection
from logic.survey_processing import SurveyProcessing, create_session, update_session, create_plan, cleanup_plan
from logic.athlete_status_processing import AthleteStatusProcessing
from logic.training_volume_processing import TrainingVolumeProcessing

datastore_collection = DatastoreCollection()
athlete_stats_datastore = datastore_collection.athlete_stats_datastore
daily_plan_datastore = datastore_collection.daily_plan_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore
session_datastore = datastore_collection.session_datastore

app = Blueprint('session', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str, 'sessions': list})
@xray_recorder.capture('routes.session.create')
def handle_session_create(principal_id=None):

    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    # training_volume_processing = TrainingVolumeProcessing(event_date, event_date)
    plan_update_required = False
    train_later = False
    if 'sessions_planned' in request.json and request.json['sessions_planned']:
        train_later = True
    athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
    plan_event_date = format_date(event_date)
    survey_processor = SurveyProcessing(user_id, event_date,
                                        athlete_stats=athlete_stats,
                                        datastore_collection=datastore_collection)
    for session in request.json['sessions']:
        if session is None:
            continue
        survey_processor.create_session_from_survey(session)

    # update daily pain and soreness in athlete_stats
    survey_processor.patch_daily_and_historic_soreness(survey='post_session')

    # check if any of the non-ignored and non-deleted sessions are high load
    high_relative_load_session_present = False
    sport_name = None
    for session in survey_processor.sessions:
        if not session.deleted and not session.ignored:
            plan_update_required = True
            if TrainingVolumeProcessing.is_last_session_high_relative_load(event_date, session, athlete_stats.high_relative_load_benchmarks):
                high_relative_load_session_present = True
                sport_name = session.sport_name
    survey_processor.athlete_stats.high_relative_load_session = high_relative_load_session_present
    survey_processor.athlete_stats.high_relative_load_session_sport_name = sport_name

    # check if plan exists, if not create a new one and save it to database, also check if existing one needs updating flags

    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = daily_plan_datastore.get_last_sensor_sync(user_id, plan_event_date)
    else:
        plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]
        plan.train_later = train_later
        if plan_update_required and (not plan.sessions_planned or plan.session_from_readiness):
            plan.sessions_planned = True
            # plan.session_from_readiness = False

    # add sessions to plan and write to mongo
    plan.training_sessions.extend(survey_processor.sessions)
    daily_plan_datastore.put(plan)

    # save heart_rate_data if it exists in any of the sessions
    if len(survey_processor.heart_rate_data) > 0:
        heart_rate_datastore.put(survey_processor.heart_rate_data)

    # update plan
    if plan_update_required:
        if survey_processor.stats_processor is not None and survey_processor.stats_processor.historic_data_loaded:
            plan_copy = copy.deepcopy(plan)
            if plan_event_date in [p.event_date for p in survey_processor.stats_processor.all_plans]:
                survey_processor.stats_processor.all_plans.remove([p for p in survey_processor.stats_processor.all_plans if p.event_date == plan_event_date][0])
            survey_processor.stats_processor.all_plans.append(plan_copy)
        plan = create_plan(user_id,
                           event_date,
                           athlete_stats=survey_processor.athlete_stats,
                           stats_processor=survey_processor.stats_processor,
                           datastore_collection=datastore_collection)
    else:
        plan = cleanup_plan(plan)

    # update users database if health data received
    if "health_sync_date" in request.json and request.json['health_sync_date'] is not None:
        Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                endpoint=f"user/{user_id}",
                                                                                body={"health_sync_date": request.json['health_sync_date']})
    return {'daily_plans': [plan]}, 201


@app.route('/<uuid:session_id>', methods=['DELETE'])
@require.authenticated.any
@require.body({'event_date': str, 'session_type': int})
@xray_recorder.capture('routes.session.delete')
def handle_session_delete(session_id, principal_id=None):
    _validate_schema()
    user_id = principal_id

    event_date = parse_datetime(request.json['event_date'])
    session_type = request.json['session_type']
    plan_event_date = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException("Plan does not exist for the user to delete session")

    session_datastore.delete(user_id=user_id,
                             event_date=plan_event_date,
                             session_type=session_type,
                             session_id=session_id
                             )

    # update_plan(user_id, event_date)

    return {'message': 'success'}, 200


@app.route('/<uuid:session_id>', methods=['PATCH'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.session.update')
def handle_session_update(session_id, principal_id=None):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_date = format_date(event_date)

    # create session
    survey_processor = SurveyProcessing(user_id,
                                        event_date,
                                        datastore_collection=datastore_collection)
    session = request.json['sessions'][0]
    survey_processor.create_session_from_survey(session)
    new_session = survey_processor.sessions[0]

    # get existing session
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException("Plan does not exist for the user to update session")

    session_obj = session_datastore.get(user_id=user_id,
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
        session_datastore.update(session_obj,
                                 user_id=user_id,
                                 event_date=plan_event_date
                                 )
    # write hr data if it exists
    if len(survey_processor.heart_rate_data) > 0:
        heart_rate_datastore.put(survey_processor.heart_rate_data)
    if "health_sync_date" in request.json and request.json['health_sync_date'] is not None:
        Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                endpoint=f"user/{user_id}",
                                                                                body={"health_sync_date": request.json['health_sync_date']})

    return {'message': 'success'}, 200


@app.route('/sensor_data', methods=['POST'])
@require.authenticated.any
@require.body({'last_sensor_sync': str, 'sessions': list})
@xray_recorder.capture('routes.session.add_sensor_data')
def handle_session_sensor_data(principal_id=None):
    user_id = principal_id

    # update last_sensor_syc date
    last_sensor_sync = request.json['last_sensor_sync']
    sensor_sync_date = format_date(parse_datetime(last_sensor_sync))
    if not _check_plan_exists(user_id, sensor_sync_date):
        plan = DailyPlan(event_date=sensor_sync_date)
        plan.user_id = user_id
    else:
        plan = daily_plan_datastore.get(user_id, sensor_sync_date, sensor_sync_date)[0]
    plan.last_sensor_sync = last_sensor_sync
    daily_plan_datastore.put(plan)
    updated_dates = [sensor_sync_date]

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
            daily_plan_datastore.put(plan)

        session_id = session.get('session_id', None)
        if session_id is None:
            session_obj = create_session(session_type, sensor_data)
            session_datastore.insert(session_obj,
                                     user_id=user_id,
                                     event_date=plan_event_date
                                     )
        else:
            session_obj = session_datastore.get(user_id=user_id,
                                                event_date=plan_event_date,
                                                session_type=session_type,
                                                session_id=session_id)[0]
            update_session(session_obj, sensor_data)
            session_datastore.update(session_obj,
                                     user_id=user_id,
                                     event_date=plan_event_date
                                     )
        if plan_event_date not in updated_dates:
            plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]
            plan.last_sensor_sync = last_sensor_sync
            plan.sessions_planned = True
            daily_plan_datastore.put(plan)
            updated_dates.append(plan_event_date)

    # update_plan(user_id, event_date)
    plan = daily_plan_datastore.get(user_id, sensor_sync_date, sensor_sync_date)[0]
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
@require.body({'event_date': str})
@xray_recorder.capture('routes.typical_sessions')
def handle_get_typical_sessions(principal_id=None):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])

    filtered_sessions = AthleteStatusProcessing(user_id, event_date, datastore_collection).get_typical_sessions()
    
    return {'typical_sessions': filtered_sessions}, 200


@app.route('/no_sessions', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.no_sessions_planned')
def handle_no_sessions_planned(principal_id=None):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])

    plan_event_date = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = daily_plan_datastore.get_last_sensor_sync(user_id, plan_event_date)
        plan.sessions_planned = False
        daily_plan_datastore.put(plan)
    else:
        plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]
        if plan.sessions_planned:
            plan.sessions_planned = False
            daily_plan_datastore.put(plan)

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


def _validate_schema():
    if not SessionType.has_value(request.json['session_type']):
        raise InvalidSchemaException('session_type not recognized')
