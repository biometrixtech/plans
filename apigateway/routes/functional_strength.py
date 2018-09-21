from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint

from decorators import authentication_required
from exceptions import InvalidSchemaException, NoSuchEntityException
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from models.exercise import CompletedExercise
from utils import format_date, parse_datetime, format_datetime
from config import get_mongo_collection

app = Blueprint('functional_strength', __name__)


@app.route('/', methods=['PATCH'])
@authentication_required
@xray_recorder.capture('routes.functional_strength')
def handle_functional_strength_update():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = parse_datetime(request.json['event_date'])
    fs_start_date = format_datetime(parse_datetime(request.json['start_date'])) if 'start_date' in request.json else None
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
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')
    store = DailyPlanDatastore()

    plan = store.get(user_id=user_id, start_date=plan_event_date, end_date=plan_event_date)[0]

    if plan.functional_strength_session is not None:
        plan.functional_strength_session.completed = True
        plan.functional_strength_session.start_date = fs_start_date
        plan.functional_strength_session.event_date = fs_event_date
    plan.functional_strength_completed = True
    plan.completed_functional_strength_sessions = plan.completed_functional_strength_sessions + 1

    store.put(plan)

    save_completed_exercises(completed_exercises, user_id, fs_event_date)

    survey_complete = plan.daily_readiness_survey_completed()
    landing_screen, nav_bar_indicator = plan.define_landing_screen()
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = survey_complete
    plan['landing_screen'] = landing_screen
    plan['nav_bar_indicator'] = nav_bar_indicator
    del plan['daily_readiness_survey'], plan['user_id']

    return {'daily_plans': [plan]}, 202


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
