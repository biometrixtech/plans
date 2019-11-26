from flask import request, Blueprint
import os
import copy
import datetime

from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from models.session import SessionType, SessionSource
from models.asymmetry import Asymmetry
from models.daily_plan import DailyPlan
from models.stats import AthleteStats
from routes.environments import is_fathom_environment
from utils import parse_datetime, format_date, format_datetime, get_timezone, get_local_time
from config import get_mongo_collection
from logic.survey_processing import SurveyProcessing, create_session, update_session, create_plan, cleanup_plan
from logic.athlete_status_processing import AthleteStatusProcessing
from logic.session_processing import merge_sessions
from models.functional_movement import MovementPatterns

datastore_collection = DatastoreCollection()
athlete_stats_datastore = datastore_collection.athlete_stats_datastore
daily_plan_datastore = datastore_collection.daily_plan_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore
session_datastore = datastore_collection.session_datastore

app = Blueprint('session', __name__)


@app.route('/<uuid:user_id>/', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str, 'sessions': list})
@xray_recorder.capture('routes.session.create')
def handle_session_create(user_id=None):

    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    timezone = get_timezone(event_date)
    plan_update_required = False
    train_later = False
    hist_update = False
    if 'sessions_planned' in request.json and request.json['sessions_planned']:
        train_later = True
    athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
    if athlete_stats is None:
        athlete_stats = AthleteStats(user_id)
        athlete_stats.event_date = event_date
    if athlete_stats.api_version in [None, '4_4', '4_5']:
        hist_update = True
    athlete_stats.api_version = Config.get('API_VERSION')
    athlete_stats.timezone = timezone

    plan_event_date = format_date(event_date)
    survey_processor = SurveyProcessing(user_id, event_date,
                                        athlete_stats=athlete_stats,
                                        datastore_collection=datastore_collection)
    survey_processor.user_age = request.json.get('user_age', 20)
    for session in request.json['sessions']:
        if session is None:
            continue
        survey_processor.create_session_from_survey(session)

    visualizations = is_fathom_environment()

    # update daily pain and soreness in athlete_stats
    survey_processor.patch_daily_and_historic_soreness(survey='post_session')

    # check if any of the non-ignored and non-deleted sessions are high load
    for session in survey_processor.sessions:
        if not session.deleted and not session.ignored:
            plan_update_required = True
            break
    #survey_processor.check_high_relative_load_sessions(survey_processor.sessions)

    # check if plan exists, if not create a new one and save it to database, also check if existing one needs updating flags

    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = daily_plan_datastore.get_last_sensor_sync(user_id, plan_event_date)
    else:
        plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]
        if plan_update_required and not plan.sessions_planned:
            plan.sessions_planned = True
        #if not survey_processor.athlete_stats.high_relative_load_session and len(plan.training_sessions) > 0:
        #    survey_processor.check_high_relative_load_sessions(plan.training_sessions)

    # add sessions to plan and write to mongo
    plan.train_later = train_later
    plan.training_sessions.extend(survey_processor.sessions)

    # apple_ids_to_merge = None
    # session_ids_to_merge = None
    # destination_session_id = None
    # destination_session = None

    # if "apple_ids_to_merge" in request.json:
    #     apple_ids_to_merge = request.json["apple_ids_to_merge"]

    # if "session_ids_to_merge" in request.json:
    #     session_ids_to_merge = request.json["session_ids_to_merge"]

    # if "destination_session_id" in request.json:
    #     destination_session_id = request.json["destination_session_id"]

    # if "destination_session" in request.json:
    #     destination_session = request.json["destination_session"]

    # plan.training_sessions = merge_sessions(apple_ids_to_merge,
    #                                         session_ids_to_merge,
    #                                         destination_session_id,
    #                                         destination_session,
    #                                         survey_processor.sessions,
    #                                         plan.training_sessions)

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
                           datastore_collection=datastore_collection,
                           visualizations=visualizations,
                           hist_update=hist_update)
    else:
        plan = cleanup_plan(plan, visualizations)

    # update users database if health data received
    if is_fathom_environment():
        if "health_sync_date" in request.json and request.json['health_sync_date'] is not None:
            Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                    endpoint=f"user/{user_id}",
                                                                                    body={"health_sync_date": request.json['health_sync_date']})
        Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                endpoint=f"user/{user_id}",
                                                                                body={"timezone": timezone,
                                                                                      "plans_api_version": Config.get('API_VERSION')})
    return {'daily_plans': [plan]}, 201


@app.route('/<uuid:user_id>/<uuid:session_id>', methods=['DELETE'])
@require.authenticated.any
@require.body({'event_date': str, 'session_type': int})
@xray_recorder.capture('routes.session.delete')
def handle_session_delete(session_id, user_id=None):
    _validate_schema()
    #user_id = principal_id

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


@app.route('/<uuid:user_id>/<uuid:session_id>', methods=['PATCH'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.session.update')
def handle_session_update(session_id, user_id=None):
    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_date = format_date(event_date)

    # create session
    survey_processor = SurveyProcessing(user_id,
                                        event_date,
                                        datastore_collection=datastore_collection)
    session = request.json['sessions'][0]


    # get existing session
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException("Plan does not exist for the user to update session")

    session_obj = session_datastore.get(user_id=user_id,
                                        event_date=plan_event_date,
                                        session_id=session_id
                                        )[0]
    # update existing session with new data
    if session_obj.source == SessionSource.user:
        survey_processor.create_session_from_survey(session)
        new_session = survey_processor.sessions[0]
        session_obj.event_date = new_session.event_date
        session_obj.end_date = new_session.end_date
        session_obj.duration_health = new_session.duration_health
        session_obj.calories = new_session.calories
        session_obj.distance = new_session.distance
        session_obj.source = SessionSource.user_health
        session_datastore.update(session_obj,
                                 user_id=user_id,
                                 event_date=plan_event_date
                                 )
        # write hr data if it exists
        if len(survey_processor.heart_rate_data) > 0:
            heart_rate_datastore.put(survey_processor.heart_rate_data)
        if is_fathom_environment():
            if "health_sync_date" in request.json and request.json['health_sync_date'] is not None:
                Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                        endpoint=f"user/{user_id}",
                                                                                        body={"health_sync_date": request.json['health_sync_date']})

        return {'message': 'success'}, 200

    elif session_obj.source == SessionSource.three_sensor:
        athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
        timezone = get_timezone(event_date)
        if athlete_stats is None:
            athlete_stats = AthleteStats(user_id)
            athlete_stats.event_date = event_date
        survey_processor.athlete_stats = athlete_stats
        survey_processor.create_session_from_survey(session)
        new_session = survey_processor.sessions[0]
        updated_date = get_local_time(datetime.datetime.now(), timezone)
        # update existing session with new data
        session_obj.post_session_survey = new_session.post_session_survey
        session_obj.last_updated = updated_date
        # write session
        session_datastore.update(session_obj,
                                 user_id=user_id,
                                 event_date=plan_event_date
                                 )
        # update plan
        visualizations = is_fathom_environment()
        hist_update = False
        if athlete_stats.api_version in [None, '4_4', '4_5']:
            hist_update = True
        athlete_stats.api_version = Config.get('API_VERSION')
        athlete_stats.timezone = timezone
        plan = create_plan(user_id,
                           event_date,
                           athlete_stats=athlete_stats,
                           datastore_collection=datastore_collection,
                           visualizations=visualizations,
                           hist_update=hist_update)

        return {'daily_plans': [plan]}, 200

    return {'message': 'success'}, 200


@app.route('/<uuid:user_id>/sensor_data', methods=['POST'])
@require.authenticated.any
@require.body({'last_sensor_sync': str, 'sessions': list})
@xray_recorder.capture('routes.session.add_sensor_data')
def handle_session_sensor_data(user_id=None):
    #user_id = principal_id

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


@app.route('/<uuid:user_id>/three_sensor_data', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.session.add_sensor_data')
def handle_session_three_sensor_data(user_id):
    #user_id = request.json['user_id']
    athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
    if athlete_stats is not None:
        timezone = athlete_stats.timezone
    else:
        timezone = '-04:00'
    event_date = parse_datetime(request.json['event_date'])
    event_date = get_local_time(event_date, timezone)
    end_date = request.json.get('end_date')
    if end_date is not None:
        end_date = parse_datetime(end_date)
        end_date = get_local_time(end_date, timezone)

    updated_date = get_local_time(datetime.datetime.now(), timezone)
    plan_event_day = format_date(event_date)
    # update last_sensor_syc date
    if not _check_plan_exists(user_id, plan_event_day):
        plan = DailyPlan(event_date=plan_event_day)
        plan.user_id = user_id
    else:
        plan = daily_plan_datastore.get(user_id, plan_event_day, plan_event_day)[0]

    session_id = request.json['session_id']
    asymmetry = request.json.get('asymmetry', {})
    movement_patterns = request.json.get('movement_patterns', {})
    duration = request.json.get('seconds_duration', 0)
    duration_minutes = round(duration / 60, 2)
    session_obj = create_session(6, {'description': 'three_sensor_data',
                                     'event_date': event_date,
                                     'end_date': end_date,
                                     'completed_date_time': end_date,
                                     'last_updated': updated_date,
                                     'sport_name': 17,
                                     'source': 3,
                                     'duration_sensor': duration,
                                     'duration_minutes': duration_minutes})
    # update other fields
    session_obj.id = session_id
    session_obj.asymmetry = Asymmetry.json_deserialise(asymmetry)
    session_obj.movement_patterns = MovementPatterns.json_deserialise(movement_patterns)

    # does session already exist
    found = False
    for s in range(0, len(plan.training_sessions)):
        if plan.training_sessions[s].id == session_id:
            plan.training_sessions[s].description = 'three_sensor_data'
            plan.training_sessions[s].event_date = event_date
            plan.training_sessions[s].end_date = end_date
            plan.training_sessions[s].completed_date_time = end_date
            plan.training_sessions[s].last_updated = updated_date
            plan.training_sessions[s].sport_name = 17
            plan.training_sessions[s].source = 3
            plan.training_sessions[s].duration_sensor = duration
            plan.training_sessions[s].duration_minutes = duration_minutes
            plan.training_sessions[s].asymmetry = session_obj.asymmetry
            plan.training_sessions[s].movement_patterns = session_obj.movement_patterns
            found = True
            break

    if not found:
        # add to plans and store plan
        plan.training_sessions.append(session_obj)

    daily_plan_datastore.put(plan)

    return {'message': 'success'}


@app.route('/<uuid:user_id>/typical', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.typical_sessions')
def handle_get_typical_sessions(user_id=None):
    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])

    filtered_sessions = AthleteStatusProcessing(user_id, event_date, datastore_collection).get_typical_sessions()
    
    return {'typical_sessions': filtered_sessions}, 200


@app.route('/<uuid:user_id>/no_sessions', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.no_sessions_planned')
def handle_no_sessions_planned(user_id=None):
    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    hist_update = False
    plan_event_date = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = daily_plan_datastore.get_last_sensor_sync(user_id, plan_event_date)
    else:
        plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]

    visualizations = is_fathom_environment()
    plan.sessions_planned = False
    plan.train_later = False
    daily_plan_datastore.put(plan)
    athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
    if athlete_stats.api_version in [None, '4_4', '4_5']:
        hist_update = True
    plan = create_plan(user_id,
                       event_date,
                       athlete_stats=athlete_stats,
                       update_stats=True,
                       datastore_collection=datastore_collection,
                       visualizations=visualizations,
                       hist_update=hist_update)

    return {'daily_plans': [plan]}, 200


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
