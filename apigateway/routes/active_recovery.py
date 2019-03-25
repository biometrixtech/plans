from flask import request, Blueprint
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from models.soreness import CompletedExercise
from logic.survey_processing import create_plan
from utils import format_date, parse_datetime, format_datetime, validate_request_body
from config import get_mongo_collection

datastore_collection = DatastoreCollection()
daily_plan_datastore = datastore_collection.daily_plan_datastore
completed_exercise_datastore = datastore_collection.completed_exercise_datastore

app = Blueprint('active_recovery', __name__)


@app.route('/', methods=['PATCH'])
@require.authenticated.any
@xray_recorder.capture('routes.active_recovery')
def handle_active_recovery_update(principal_id=None):
    user_id = principal_id
    required_parameters = {'event_date', 'recovery_type'}
    validate_request_body(required_parameters, request.json)
    # if not isinstance(request.json, dict):
    #     raise InvalidSchemaException('Request body must be a dictionary')
    # if not required_parameters <= request.json.keys():
    #     InvalidSchemaException(f"Missing required parameter(s): {', '.join(required_parameters - request.json.keys())}")

    event_date = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']
    completed_exercises = request.json.get('completed_exercises', [])

    plan_event_date = format_date(event_date)
    recovery_event_date = format_datetime(event_date)

    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')

    save_exercises = True
    plan = daily_plan_datastore.get(user_id=user_id, start_date=plan_event_date, end_date=plan_event_date)[0]
    if recovery_type == 'pre':
        if plan.pre_recovery_completed:
            save_exercises = False
        plan.pre_recovery_completed = True  # plan
        plan.pre_recovery.completed = True  # recovery
        plan.pre_recovery.event_date = recovery_event_date
        plan.pre_recovery.display_exercises = False

    elif recovery_type == 'post':
        if plan.post_recovery.completed:
            save_exercises = False
        plan.post_recovery_completed = True  # plan
        plan.post_recovery.completed = True  # recovery
        plan.post_recovery.event_date = recovery_event_date
        plan.post_recovery.display_exercises = False

    daily_plan_datastore.put(plan)

    if save_exercises:
        save_completed_exercises(completed_exercises, user_id, recovery_event_date)

    survey_complete = plan.daily_readiness_survey_completed()
    landing_screen, nav_bar_indicator = plan.define_landing_screen()
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = survey_complete
    plan['landing_screen'] = landing_screen
    plan['nav_bar_indicator'] = nav_bar_indicator
    del plan['daily_readiness_survey'], plan['user_id']

    return {'daily_plans': [plan]}, 202


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.active_recovery.start')
def handle_active_recovery_start(principal_id=None):
    user_id = principal_id
    required_parameters = {'event_date', 'recovery_type'}
    validate_request_body(required_parameters, request.json)

    event_date = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']
    plan_event_date = format_date(event_date)
    recovery_start_date = format_datetime(event_date)
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')

    plan = daily_plan_datastore.get(user_id=user_id,
                                    start_date=plan_event_date,
                                    end_date=plan_event_date)[0]
    plans_service = Service('plans', Config.get('API_VERSION'))
    body = {"event_date": recovery_start_date}
    if recovery_type == 'pre':
        plan.pre_recovery.start_date = recovery_start_date
        plans_service.call_apigateway_async(method='POST',
                                            endpoint=f'/athlete/{user_id}/prep_started',
                                            body=body)

    elif recovery_type == 'post':
        plan.post_recovery.start_date = recovery_start_date
        plans_service.call_apigateway_async(method='POST',
                                            endpoint=f'/athlete/{user_id}/recovery_started',
                                            body=body)

    daily_plan_datastore.put(plan)

    return {'message': 'success'}, 200


@app.route('/active_time', methods=['PATCH'])
@require.authenticated.any
@xray_recorder.capture('routes.active_time')
def handle_workout_active_time(principal_id=None):
    user_id = principal_id
    required_parameters = {'event_date', 'active_time'}
    validate_request_body(required_parameters, request.json)

    event_date = parse_datetime(request.json['event_date'])
    target_minutes = request.json['active_time']
    plan_event_date = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')

    plan = create_plan(user_id, event_date, target_minutes=target_minutes, update_stats=False, datastore_collection=datastore_collection)

    return {'daily_plans': [plan]}, 200


def save_completed_exercises(exercise_list, user_id, event_date):
    for exercise in exercise_list:
        completed_exercise_datastore.put(CompletedExercise(athlete_id=user_id,
                                                           exercise_id=exercise,
                                                           event_date=event_date))


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False
