from flask import request, Blueprint
import datetime
import os

from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from datastores.heart_rate_datastore import HeartRateDatastore
from datastores.sleep_history_datastore import SleepHistoryDatastore
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from models.daily_readiness import DailyReadiness
from models.soreness import MuscleSorenessSeverity, BodyPartLocation, HistoricSorenessStatus
from models.stats import AthleteStats
from models.daily_plan import DailyPlan
from models.heart_rate import SessionHeartRate, HeartRateData
from models.sleep_data import DailySleepData, SleepEvent
from logic.survey_processing import SurveyProcessing
from logic.athlete_status_processing import AthleteStatusProcessing
from utils import parse_datetime, format_date, format_datetime, parse_date, fix_early_survey_event_date

app = Blueprint('daily_readiness', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.daily_readiness.create')
def handle_daily_readiness_create():
    validate_data()
    event_date = parse_datetime(request.json['date_time'])
    event_date = fix_early_survey_event_date(event_date)
    
    user_id = request.json['user_id']
    daily_readiness = DailyReadiness(
        user_id=user_id,
        event_date=format_datetime(event_date),
        soreness=request.json['soreness'],  # dailysoreness object array
        sleep_quality=request.json.get('sleep_quality', None),
        readiness=request.json.get('readiness', None),
        wants_functional_strength=(request.json['wants_functional_strength']
                                   if 'wants_functional_strength' in request.json else False)
    )

    all_sessions = []
    all_session_heart_rates = []
    need_new_plan = False
    sessions_planned = True
    sessions_planned_readiness = True
    session_from_readiness = False
    need_stats_update = False
    session_RPE = None
    session_RPE_event_date = None
    plan_event_date = format_date(event_date)
    if 'sessions_planned' in request.json and not request.json['sessions_planned']:
        need_new_plan = True
        sessions_planned = False
        sessions_planned_readiness = False
    if 'sessions' in request.json and len(request.json['sessions']) > 0:
        need_new_plan = True
        sessions_planned = True
        session_from_readiness = True
        need_stats_update = True
        for session in request.json['sessions']:
            session_obj = SurveyProcessing().create_session_from_survey(session)
            if session_RPE is not None and session_obj.post_session_survey.RPE is not None:
                session_RPE = max(session_obj.post_session_survey.RPE, session_RPE)
            elif session_obj.post_session_survey.RPE is not None:
                session_RPE = session_obj.post_session_survey.RPE
            session_RPE_event_date = plan_event_date
            if 'hr_data' in session and len(session['hr_data']) > 0:
                session_heart_rate = SessionHeartRate(user_id=user_id,
                                                      session_id=session_obj.id,
                                                      event_date=session_obj.event_date)
                session_heart_rate.hr_workout = [HeartRateData(SurveyProcessing().cleanup_hr_data_from_api(hr)) for hr in session['hr_data']]
                all_session_heart_rates.append(session_heart_rate)
            all_sessions.append(session_obj)

    if "sleep_data" in request.json and len(request.json['sleep_data']) > 0:
        daily_sleep_data = DailySleepData(user_id=user_id,
                                          event_date=plan_event_date)
        daily_sleep_data.sleep_events = [SleepEvent(SurveyProcessing().cleanup_sleep_data_from_api(sd)) for sd in request.json['sleep_data']]
        SleepHistoryDatastore().put(daily_sleep_data)

    if need_new_plan:
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = DailyPlanDatastore().get_last_sensor_sync(user_id, plan_event_date)
        plan.training_sessions = all_sessions
        plan.sessions_planned = sessions_planned
        plan.session_from_readiness = session_from_readiness
        plan.sessions_planned_readiness = sessions_planned_readiness
        DailyPlanDatastore().put(plan)
        if len(all_session_heart_rates) > 0:
            HeartRateDatastore().put(all_session_heart_rates)

    athlete_stats = AthleteStatsDatastore().get(athlete_id=request.json['user_id'])
    if athlete_stats is None:
        athlete_stats = AthleteStats(request.json['user_id'])

    if "clear_candidates" in request.json and len(request.json['clear_candidates']) > 0:
        SurveyProcessing().process_clear_status_answers(request.json['clear_candidates'], athlete_stats, event_date, daily_readiness.soreness)

    store = DailyReadinessDatastore()
    store.put(daily_readiness)

    soreness = daily_readiness.soreness
    severe_soreness = [s for s in soreness if not s.pain]
    severe_pain = [s for s in soreness if s.pain]
    if len(soreness) > 0 or 'current_sport_name' in request.json or 'current_position' in request.json:
        need_stats_update = True

    if need_stats_update:
        athlete_stats.event_date = plan_event_date
        athlete_stats.session_RPE = session_RPE
        athlete_stats.session_RPE_event_date = session_RPE_event_date
        athlete_stats.update_readiness_soreness(severe_soreness)
        athlete_stats.update_readiness_pain(severe_pain)
        athlete_stats.update_daily_soreness()
        athlete_stats.update_daily_pain()
        athlete_stats.daily_severe_soreness_event_date = plan_event_date
        athlete_stats.daily_severe_pain_event_date = plan_event_date

        for s in daily_readiness.soreness:
            athlete_stats.update_historic_soreness(s, plan_event_date)

        if 'current_sport_name' in request.json or 'current_position' in request.json:
            if 'current_sport_name' in request.json:
                athlete_stats.current_sport_name = request.json['current_sport_name']
            if 'current_position' in request.json:
                athlete_stats.current_position = request.json['current_position']

    AthleteStatsDatastore().put(athlete_stats)

    body = {"event_date": plan_event_date,
            "last_updated": format_datetime(event_date)}
    Service('plans', Config.get('API_VERSION')).call_apigateway_async('POST',
                                                                      f"athlete/{request.json['user_id']}/daily_plan",
                                                                      body)
    if "health_sync_date" in request.json and request.json['health_sync_date'] is not None:
        Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                endpoint=f"user/{user_id}",
                                                                                body={"health_sync_date": request.json['health_sync_date']})


    return {'message': 'success'}, 201


@app.route('/previous', methods=['POST', 'GET'])
@require.authenticated.any
@xray_recorder.capture('routes.daily_readiness.previous')
def handle_daily_readiness_get(principal_id=None):
    daily_readiness_store = DailyReadinessDatastore()
    user_id = principal_id

    if request.method == 'POST':
        if 'event_date' not in request.json:
            raise InvalidSchemaException('Missing required parameter event_date')
        else:
            current_time = parse_datetime(request.json['event_date'])
    elif request.method == 'GET':
        current_time = datetime.datetime.now()
    previous_soreness_processor = AthleteStatusProcessing(user_id, current_time)
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

