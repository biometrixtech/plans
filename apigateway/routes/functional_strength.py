from flask import request, Blueprint

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from models.exercise import CompletedExercise
from utils import format_date, parse_datetime, format_datetime
from config import get_mongo_collection
from datetime import timedelta

app = Blueprint('functional_strength', __name__)


@app.route('/', methods=['PATCH'])
@require.authenticated.any
@xray_recorder.capture('routes.functional_strength')
def handle_functional_strength_update():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = parse_datetime(request.json['event_date'])
    try:
        user_id = request.json['user_id']
    except:
        raise InvalidSchemaException('user_id is required')
    try:
        completed_exercises = request.json['completed_exercises']
    except:
        completed_exercises = []

    plan_event_date = format_date(event_date)
    fs_event_date = format_datetime(event_date)
    if event_date.hour < 3:
        plan_event_date = format_date(event_date - timedelta(days=1))
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')
    store = DailyPlanDatastore()

    plan = store.get(user_id=user_id, start_date=plan_event_date, end_date=plan_event_date)[0]

    if plan.functional_strength_session is not None:
        plan.functional_strength_session.completed = True
        plan.functional_strength_session.event_date = fs_event_date
    plan.functional_strength_completed = True
    plan.completed_functional_strength_sessions = plan.completed_functional_strength_sessions + 1
    store.put(plan)

    athlete_stats_store = AthleteStatsDatastore()
    athlete_stats = athlete_stats_store.get(athlete_id=user_id)
    athlete_stats.completed_functional_strength_sessions += 1
    athlete_stats.next_functional_strength_eligible_date = format_datetime(parse_datetime(fs_event_date) + timedelta(days=1))
    athlete_stats_store.put(athlete_stats)

    save_completed_exercises(completed_exercises, user_id, fs_event_date)

    survey_complete = plan.daily_readiness_survey_completed()
    landing_screen, nav_bar_indicator = plan.define_landing_screen()
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = survey_complete
    plan['landing_screen'] = 1.0
    plan['nav_bar_indicator'] = nav_bar_indicator
    del plan['daily_readiness_survey'], plan['user_id']

    return {'daily_plans': [plan]}, 202


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.functional_strength')
def handle_functional_strength_start():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = parse_datetime(request.json['event_date'])
    try:
        user_id = request.json['user_id']
    except:
        raise InvalidSchemaException('user_id is required')

    plan_event_date = format_date(event_date)
    fs_start_date = format_datetime(event_date)
    if event_date.hour < 3:
        plan_event_date = format_date(event_date - datetime.timedelta(days=1))
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')
    store = DailyPlanDatastore()

    plan = store.get(user_id=user_id,
                     start_date=plan_event_date,
                     end_date=plan_event_date)[0]

    if plan.functional_strength_session is not None:
        plan.functional_strength_session.start_date = fs_start_date
        # TODO: need to implement this route
        # plans_service = Service('plans', Config.get('API_VERSION'))
        # body = {"event_date": recovery_start_date}
        # plans_service.call_apigateway_async(method='POST',
        #                                     endpoint=f'/athlete/{user_id}/fs_started',
        #                                     body=body)
    store.put(plan)

    return {'message': 'success'}, 200


def save_completed_exercises(exercise_list, user_id, event_date):
    exercise_store = CompletedExerciseDatastore()

    for exercise in exercise_list:
        exercise_store.put(CompletedExercise(athlete_id=user_id,
                                             exercise_id=exercise,
                                             event_date=event_date))


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False
