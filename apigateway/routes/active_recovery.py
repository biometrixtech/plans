from flask import request, Blueprint
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from models.soreness import CompletedExercise
from utils import format_date, parse_datetime, format_datetime
from config import get_mongo_collection

datastore_collection = DatastoreCollection()
daily_plan_datastore = datastore_collection.daily_plan_datastore
completed_exercise_datastore = datastore_collection.completed_exercise_datastore

app = Blueprint('active_recovery', __name__)


@app.route('/exercise_modalities', methods=['PATCH'])
@require.authenticated.any
@require.body({'event_date': str, 'recovery_type': str})
@xray_recorder.capture('routes.active_recovery.exercise_modalities.complete')
def handle_exercise_modalities_complete(principal_id=None):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']
    completed_exercises = request.json.get('completed_exercises', [])

    plan_event_day = format_date(event_date)
    recovery_event_date = format_datetime(event_date)

    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    save_exercises = True
    plan = daily_plan_datastore.get(user_id=user_id,
                                    start_date=plan_event_day,
                                    end_date=plan_event_day)[0]
    if recovery_type == 'pre_active_rest':
        if plan.pre_active_rest.completed:
            save_exercises = False
        plan.pre_active_rest_completed = True  # plan
        plan.pre_active_rest.completed = True  # recovery
        plan.pre_active_rest.completed_date_time = recovery_event_date

    elif recovery_type == 'post_active_rest':
        if plan.post_active_rest.completed:
            save_exercises = False
        plan.post_active_rest_completed = True  # plan
        plan.post_active_rest.completed = True  # recovery
        plan.post_active_rest.completed_date_time = recovery_event_date

    elif recovery_type == 'warm_up':
        plan.warm_up.completed_date_time = recovery_event_date
        plan.warm_up.completed = True
        if plan.warm_up.completed:
            save_exercises = False

    elif recovery_type == 'cool_down':
        plan.cool_down.completed_date_time = recovery_event_date
        plan.cool_down.completed = True
        if plan.cool_down.completed:
            save_exercises = False

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


@app.route('/exercise_modalities', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str, 'recovery_type': str})
@xray_recorder.capture('routes.active_recovery.exercise_modalities.start')
def handle_exercise_modalities_start(principal_id=None):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']

    plan_event_day = format_date(event_date)
    recovery_start_date = format_datetime(event_date)
    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    plan = daily_plan_datastore.get(user_id=user_id,
                                    start_date=plan_event_day,
                                    end_date=plan_event_day)[0]
    plans_service = Service('plans', Config.get('API_VERSION'))
    body = {"event_date": recovery_start_date}
    if recovery_type == 'pre_active_rest':
        plan.pre_active_rest.start_date_time = recovery_start_date
        plans_service.call_apigateway_async(method='POST',
                                            endpoint=f'/athlete/{user_id}/prep_started',
                                            body=body)

    elif recovery_type == 'post_active_rest':
        plan.post_active_rest.start_date_time = recovery_start_date
        plans_service.call_apigateway_async(method='POST',
                                            endpoint=f'/athlete/{user_id}/recovery_started',
                                            body=body)

    elif recovery_type == 'warm_up':
        plan.warm_up.start_date_time = recovery_start_date

    elif recovery_type == 'cool_down':
        plan.cool_down.start_date_time = recovery_start_date

    daily_plan_datastore.put(plan)

    return {'message': 'success'}, 200


@app.route('/body_part_modalities', methods=['PATCH'])
@require.authenticated.any
@require.body({'event_date': str, 'recovery_type': str})
@xray_recorder.capture('routes.active_recovery.body_part_modalities.complete')
def handle_body_part_modalities_complete(principal_id=None):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']
    completed_body_parts = request.json.get('completed_body_parts', [])

    plan_event_day = format_date(event_date)

    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    plan = daily_plan_datastore.get(user_id=user_id, start_date=plan_event_day, end_date=plan_event_day)[0]

    if recovery_type == 'heat':
        plan.heat.completed_date_time = event_date
        plan.heat.completed = True
        for completed_body_part in completed_body_parts:
            assigned_body_part = [body_part for body_part in plan.heat.body_parts if
                                  body_part.body_part_location.value == completed_body_part['body_part_location'] and
                                  body_part.side == completed_body_part['side']][0]
            assigned_body_part.completed = True

    elif recovery_type == 'ice':
        plan.ice.completed_date_time = event_date
        plan.ice.completed = True
        for completed_body_part in completed_body_parts:
            assigned_body_part = [body_part for body_part in plan.ice.body_parts if
                                  body_part.body_part_location.value == completed_body_part['body_part_location'] and
                                  body_part.side == completed_body_part['side']][0]
            assigned_body_part.completed = True

    elif recovery_type == 'cold_water_immersion':
        plan.cold_water_immersion.completed_date_time = event_date
        plan.cold_water_immersion.completed = True

    daily_plan_datastore.put(plan)

    survey_complete = plan.daily_readiness_survey_completed()
    landing_screen, nav_bar_indicator = plan.define_landing_screen()
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = survey_complete
    plan['landing_screen'] = landing_screen
    plan['nav_bar_indicator'] = nav_bar_indicator
    del plan['daily_readiness_survey'], plan['user_id']

    return {'daily_plans': [plan]}, 202


@app.route('/body_part_modalities', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str, 'recovery_type': str})
@xray_recorder.capture('routes.active_recovery.body_part_modalities.start')
def handle_body_part_modalities_start(principal_id=None):
    user_id = principal_id
    start_date_time = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']

    plan_event_day = format_date(start_date_time)
    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    plan = daily_plan_datastore.get(user_id=user_id,
                                    start_date=plan_event_day,
                                    end_date=plan_event_day)[0]
    if recovery_type == 'heat':
        plan.heat.start_date_time = start_date_time

    elif recovery_type == 'ice':
        plan.ice.start_date_time = start_date_time

    elif recovery_type == 'cold_water_immersion':
        plan.cold_water_immersion.start_date_time = event_date

    daily_plan_datastore.put(plan)

    return {'message': 'success'}, 200


'''deprecated
@app.route('/active_time', methods=['PATCH'])
@require.authenticated.any
@require.body({'event_date': str, 'active_time': int})
@xray_recorder.capture('routes.active_time')
def handle_workout_active_time(principal_id=None):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    target_minutes = request.json['active_time']

    plan_event_day = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    plan = create_plan(user_id, event_date, target_minutes=target_minutes, update_stats=False, datastore_collection=datastore_collection)

    return {'daily_plans': [plan]}, 200
'''


def save_completed_exercises(exercise_list, user_id, event_date):
    for exercise in exercise_list:
        completed_exercise_datastore.put(CompletedExercise(athlete_id=user_id,
                                                           exercise_id=exercise,
                                                           event_date=event_date))


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    return mongo_collection.count({"user_id": user_id, "date": event_date}) == 1
