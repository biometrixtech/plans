from flask import request, Blueprint
import datetime
import os

from datastores.datastore_collection import DatastoreCollection
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from models.daily_readiness import DailyReadiness
from models.soreness import MuscleSorenessSeverity, BodyPartLocation
from models.stats import AthleteStats
from models.daily_plan import DailyPlan
from models.sleep_data import DailySleepData, SleepEvent
from logic.survey_processing import SurveyProcessing, cleanup_sleep_data_from_api, create_plan
from logic.athlete_status_processing import AthleteStatusProcessing
from config import get_mongo_collection
from utils import parse_datetime, format_date, format_datetime, fix_early_survey_event_date

datastore_collection = DatastoreCollection()
athlete_stats_datastore = datastore_collection.athlete_stats_datastore
daily_plan_datastore = datastore_collection.daily_plan_datastore
daily_readiness_datastore = datastore_collection.daily_readiness_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore
session_datastore = datastore_collection.session_datastore
sleep_history_datastore = datastore_collection.sleep_history_datastore

app = Blueprint('daily_readiness', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.daily_readiness.create')
def handle_daily_readiness_create(principal_id=None):
    validate_data()
    event_date = parse_datetime(request.json['date_time'])
    event_date = fix_early_survey_event_date(event_date)

    user_id = principal_id
    daily_readiness = DailyReadiness(
        user_id=user_id,
        event_date=format_datetime(event_date),
        soreness=request.json['soreness'],  # dailysoreness object array
        sleep_quality=request.json.get('sleep_quality', None),
        readiness=request.json.get('readiness', None),
        wants_functional_strength=(request.json['wants_functional_strength']
                                   if 'wants_functional_strength' in request.json else False)
    )

    need_new_plan = False
    sessions_planned = True
    sessions_planned_readiness = True
    session_from_readiness = False
    plan_event_date = format_date(event_date)
    athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
    if athlete_stats is None:
        athlete_stats = AthleteStats(user_id)
        athlete_stats.event_date = plan_event_date
    survey_processor = SurveyProcessing(user_id, event_date, athlete_stats, datastore_collection)

    if 'sessions_planned' in request.json and not request.json['sessions_planned']:
        need_new_plan = True
        sessions_planned = False
        sessions_planned_readiness = False
    if 'sessions' in request.json and len(request.json['sessions']) > 0:
        need_new_plan = True
        sessions_planned = True
        session_from_readiness = True
        for session in request.json['sessions']:
            if session is None:
                continue
            survey_processor.create_session_from_survey(session)

    if "sleep_data" in request.json and len(request.json['sleep_data']) > 0:
        daily_sleep_data = DailySleepData(user_id=user_id,
                                          event_date=plan_event_date)
        daily_sleep_data.sleep_events = [SleepEvent(cleanup_sleep_data_from_api(sd)) for sd in
                                         request.json['sleep_data']]
        sleep_history_datastore.put(daily_sleep_data)

    if need_new_plan:
        if _check_plan_exists(user_id, plan_event_date):
            plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]
            plan.user_id = user_id
            plan.training_sessions.extend(survey_processor.sessions)
        else:
            plan = DailyPlan(event_date=plan_event_date)
            plan.user_id = user_id
            # plan.last_sensor_sync = DailyPlanDatastore().get_last_sensor_sync(user_id, plan_event_date)
            plan.training_sessions = survey_processor.sessions
        plan.sessions_planned = sessions_planned
        plan.session_from_readiness = session_from_readiness
        plan.sessions_planned_readiness = sessions_planned_readiness
        daily_plan_datastore.put(plan)
        if len(survey_processor.heart_rate_data) > 0:
            heart_rate_datastore.put(survey_processor.heart_rate_data)

    if "clear_candidates" in request.json and len(request.json['clear_candidates']) > 0:
        survey_processor.process_clear_status_answers(request.json['clear_candidates'], event_date,
                                                      daily_readiness.soreness)

    daily_readiness_datastore.put(daily_readiness)

    survey_processor.soreness = daily_readiness.soreness
    survey_processor.patch_daily_and_historic_soreness(survey='readiness')

    if 'current_sport_name' in request.json or 'current_position' in request.json:
        if 'current_sport_name' in request.json:
            survey_processor.athlete_stats.current_sport_name = request.json['current_sport_name']
        if 'current_position' in request.json:
            survey_processor.athlete_stats.current_position = request.json['current_position']

    plan = create_plan(user_id,
                       event_date,
                       athlete_stats=survey_processor.athlete_stats,
                       stats_processor=survey_processor.stats_processor,
                       datastore_collection=datastore_collection)
    if "health_sync_date" in request.json and request.json['health_sync_date'] is not None:
        Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                endpoint=f"user/{user_id}",
                                                                                body={"health_sync_date": request.json['health_sync_date']})


    return {'daily_plans': [plan]}, 201


@app.route('/previous', methods=['POST', 'GET'])
@require.authenticated.any
@xray_recorder.capture('routes.daily_readiness.previous')
def handle_daily_readiness_get(principal_id=None):
    user_id = principal_id

    if request.method == 'POST':
        if 'event_date' not in request.json:
            raise InvalidSchemaException('Missing required parameter event_date')
        else:
            current_time = parse_datetime(request.json['event_date'])
    else:
        current_time = datetime.datetime.now()
    previous_soreness_processor = AthleteStatusProcessing(user_id, current_time, datastore_collection)
    (
        sore_body_parts,
        hist_sore_status,
        clear_candidates,
        dormant_tipping_candidates,
        current_sport_name,
        current_position,
        functional_strength_eligible,
        completed_functional_strength_sessions
        ) = previous_soreness_processor.get_previous_soreness()

    typical_sessions = previous_soreness_processor.get_typical_sessions()
    return {
            "readiness": {
                          'body_parts': sore_body_parts,
                          'dormant_tipping_candidates': dormant_tipping_candidates,
                          'hist_sore_status': hist_sore_status,
                          'clear_candidates': clear_candidates,
                          'current_position': current_position,
                          'current_sport_name': current_sport_name,
                          'functional_strength_eligible': functional_strength_eligible,
                          'completed_functional_strength_sessions': completed_functional_strength_sessions
                         },
            "typical_sessions": typical_sessions} , 200


@xray_recorder.capture('routes.daily_readiness.validate')
def validate_data():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')

    if 'date_time' not in request.json:
        raise InvalidSchemaException('Missing required parameter date_time')
    parse_datetime(request.json['date_time'])

    # validate soreness
    if 'soreness' not in request.json:
        raise InvalidSchemaException('Missing required parameter soreness')
    if not isinstance(request.json['soreness'], list):
        raise InvalidSchemaException('soreness must be a list')
    for soreness in request.json['soreness']:
        try:
            BodyPartLocation(soreness['body_part'])
        except ValueError:
            raise InvalidSchemaException('body_part not recognized')
        try:
            MuscleSorenessSeverity(soreness['severity'])
        except ValueError:
            raise InvalidSchemaException('severity not recognized')
        # for valid ones, force values to be integer
        soreness['body_part'] = int(soreness['body_part'])
        soreness['severity'] = int(soreness['severity'])

def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False
