from flask import request, Blueprint
import datetime

from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from models.daily_readiness import DailyReadiness
from models.soreness import MuscleSorenessSeverity, BodyPartLocation
from models.stats import AthleteStats
from utils import parse_datetime, format_date, format_datetime, parse_date
from models.session import SessionType, SessionFactory, StrengthConditioningType
from models.post_session_survey import PostSessionSurvey, PostSurvey
from models.daily_plan import DailyPlan
from models.sport import SportName

app = Blueprint('daily_readiness', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.daily_readiness.create')
def handle_daily_readiness_create():
    validate_data()
    event_date = parse_datetime(request.json['date_time'])
    if event_date.hour < 3:
        event_date = datetime.datetime(
                            year=event_date.year, 
                            month=event_date.month,
                            day=event_date.day - 1,
                            hour=23,
                            minute=59,
                            second=59
                            )
    user_id = request.json['user_id']
    daily_readiness = DailyReadiness(
        user_id=user_id,
        event_date=format_datetime(event_date),
        soreness=request.json['soreness'],  # dailysoreness object array
        sleep_quality=request.json['sleep_quality'],
        readiness=request.json['readiness'],
        wants_functional_strength=(request.json['wants_functional_strength']
                                   if 'wants_functional_strength' in request.json else False)
    )

    all_sessions = []
    need_new_plan = False
    off_day = False
    if 'sessions' in request.json and len(request.json['sessions']) > 0:
        need_new_plan = True
        for session in request.json['sessions']:
            session_event_date = parse_datetime(session['event_date'])
            session_type = session['session_type']
            try:
                sport_name = session['sport_name']
                sport_name = SportName(sport_name)
            except:
                sport_name = SportName(None)
            try:
                strength_and_conditioning_type = session['strength_and_conditioning_type']
                strength_and_conditioning_type = StrengthConditioningType(strength_and_conditioning_type)
            except:
                strength_and_conditioning_type = StrengthConditioningType(None)
            try:
                duration = session["duration"]
            except:
                raise InvalidSchemaException("Missing required parameter duration")
            description = session.get('description', "")
            plan_event_date = format_date(event_date)
            if session_event_date.hour >= 3:
                session_event_date = format_datetime(session_event_date - datetime.timedelta(days=1))
            else:
                session_event_date = format_datetime(session_event_date)
            session_data = {"sport_name": sport_name,
                            "strength_and_conditioning_type": strength_and_conditioning_type,
                            "description": description,
                            "duration_minutes": duration,
                            "event_date": session_event_date}
            session_data['post_session_survey'] = PostSurvey(event_date=format_datetime(event_date),
                                                             survey=session['post_session_survey']
                                                             ).json_serialise()
            all_sessions.append(_create_session(session_type, session_data))
    if 'no_sessions' in request.json and request.json['no_sessions']:
        need_new_plan = True
        off_day = True
    if need_new_plan:
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.last_sensor_sync = DailyPlanDatastore().get_last_sensor_sync(user_id, plan_event_date)
        plan.training_sessions = all_sessions
        plan.sessions_planned = off_day
        DailyPlanDatastore().put(plan)

    store = DailyReadinessDatastore()
    store.put(daily_readiness)

    need_stats_update = False
    soreness = daily_readiness.soreness
    severe_soreness = [s for s in soreness if not s.pain]
    severe_pain = [s for s in soreness if s.pain]
    if len(soreness) > 0 or 'current_sport_name' in request.json or 'current_position' in request.json:
        need_stats_update = True

    if need_stats_update:
        plan_event_date = format_date(event_date)
        athlete_stats_store = AthleteStatsDatastore()
        athlete_stats = athlete_stats_store.get(athlete_id=request.json['user_id'])
        if athlete_stats is None:
            athlete_stats = AthleteStats(request.json['user_id'])
        athlete_stats.event_date = plan_event_date
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

        athlete_stats_store.put(athlete_stats)

    Service('plans', Config.get('API_VERSION')).call_apigateway_async('POST', f"athlete/{request.json['user_id']}/daily_plan")

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

    start_time = parse_date(format_date(current_time - datetime.timedelta(days=2)))
    sore_body_parts = []
    severe_soreness_today_yesterday = False
    try:
        readiness_surveys = daily_readiness_store.get(user_id, start_date=start_time, end_date=current_time, last_only=False)
        # readiness_surveys = sorted(readiness_surveys, key=lambda k: k.event_date, reverse=True)
        if len(readiness_surveys) != 0:
            for rs_survey in readiness_surveys:
                sore_body_parts.extend(rs_survey.json_serialise()['sore_body_parts'])
                if rs_survey.event_date > start_time + datetime.timedelta(days=1):
                    if len([s for s in rs_survey.soreness if s.severity >= 4]):
                        severe_soreness_today_yesterday = True
    except NoSuchEntityException:
        pass

    post_session_store = PostSessionSurveyDatastore()
    post_session_surveys = post_session_store.get(user_id=user_id, start_date=start_time, end_date=current_time)
    post_session_surveys = [s for s in post_session_surveys if s is not None and start_time <= s.event_date_time < current_time]
    if len(post_session_surveys) != 0:
        for ps_survey in post_session_surveys:
            sore_body_parts += [{"body_part": s.body_part.location.value, "side": s.side} for s in ps_survey.survey.soreness if s.severity > 1]
            if ps_survey.event_date_time > start_time + datetime.timedelta(days=1):
                if len([s for s in ps_survey.survey.soreness if s.severity >= 4]):
                    severe_soreness_today_yesterday = True
    sore_body_parts = [dict(t) for t in {tuple(d.items()) for d in sore_body_parts}]

    athlete_stats_store = AthleteStatsDatastore()
    athlete_stats = athlete_stats_store.get(athlete_id=user_id)

    current_sport_name = None
    current_position = None
    functional_strength_eligible = False
    completed_functional_strength_sessions = 0

    if athlete_stats is not None:
        current_sport_name = athlete_stats.current_sport_name.value if athlete_stats.current_sport_name is not None else None
        current_position = athlete_stats.current_position.value if athlete_stats.current_position is not None else None
        functional_strength_eligible = False
        if (athlete_stats.functional_strength_eligible and (athlete_stats.next_functional_strength_eligible_date is None
                or parse_datetime(athlete_stats.next_functional_strength_eligible_date) < current_time) and
            not severe_soreness_today_yesterday):
            functional_strength_eligible = True

        completed_functional_strength_sessions = athlete_stats.completed_functional_strength_sessions

    return {
               'body_parts': sore_body_parts,
               'current_position': current_position,
               'current_sport_name': current_sport_name,
               'functional_strength_eligible': functional_strength_eligible,
               'completed_functional_strength_sessions': completed_functional_strength_sessions
           }, 200


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

    # validate sleep_quality
    if 'sleep_quality' not in request.json:
        raise InvalidSchemaException('Missing required parameter sleep_quality')
    elif request.json['sleep_quality'] not in range(1, 11):
        raise InvalidSchemaException('sleep_quality need to be between 1 and 10')

    # validate readiness
    if 'readiness' not in request.json:
        raise InvalidSchemaException('Missing required parameter readiness')
    elif request.json['readiness'] not in range(1, 11):
        raise InvalidSchemaException('readiness need to be between 1 and 10')


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