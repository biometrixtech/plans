from flask import request, Blueprint
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from models.soreness import CompletedExercise
from routes.environments import is_fathom_environment
from logic.survey_processing import create_plan, cleanup_plan, add_modality_on_demand, process_stats
from utils import format_date, parse_datetime, format_datetime
from config import get_mongo_collection

datastore_collection = DatastoreCollection()
daily_plan_datastore = datastore_collection.daily_plan_datastore
completed_exercise_datastore = datastore_collection.completed_exercise_datastore
athlete_stats_datastore = datastore_collection.athlete_stats_datastore

app = Blueprint('active_recovery', __name__)


@app.route('/<uuid:user_id>/exercise_modalities', methods=['PATCH'])
@require.authenticated.any
@require.body({'event_date': str, 'recovery_type': str})
@xray_recorder.capture('routes.active_recovery.exercise_modalities.complete')
def handle_exercise_modalities_complete(user_id=None):
    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']
    completed_exercises = request.json.get('completed_exercises', [])
    recovery_index = request.json.get('recovery_index', 0)

    visualizations = is_fathom_environment()

    plan_event_day = format_date(event_date)
    recovery_event_date = format_datetime(event_date)

    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    save_exercises = True
    plan = daily_plan_datastore.get(user_id=user_id,
                                    start_date=plan_event_day,
                                    end_date=plan_event_day)[0]
    # if recovery_type == 'pre_active_rest':
    #     if recovery_index + 1 > len(plan.pre_active_rest):
    #         raise NoSuchEntityException('No pre active rest found with that index')
    #     if plan.pre_active_rest[recovery_index].completed:
    #         save_exercises = False
    #     plan.pre_active_rest_completed = True  # plan
    #     plan.pre_active_rest[recovery_index].completed = True  # recovery
    #     plan.pre_active_rest[recovery_index].completed_date_time = recovery_event_date

    # elif recovery_type == 'post_active_rest':
    #     if recovery_index + 1 > len(plan.post_active_rest):
    #         raise NoSuchEntityException('No post active rest found with that index')
    #     if plan.post_active_rest[recovery_index].completed:
    #         save_exercises = False
    #     plan.post_active_rest_completed = True  # plan
    #     plan.post_active_rest[recovery_index].completed = True  # recovery
    #     plan.post_active_rest[recovery_index].completed_date_time = recovery_event_date
    # elif recovery_type in ['warm_up', 'cool_down', 'functional_strength']:
    modalities = [m for m in plan.modalities if m.type.name == recovery_type and not m.completed]
    if len(modalities) > 0:
        modality = modalities[0]
        modality.completed = True
        modality.completed_date_time = recovery_event_date
    else:
        save_exercises = False

    daily_plan_datastore.put(plan)

    if save_exercises:
        save_completed_exercises(completed_exercises, user_id, recovery_event_date)

    plan = cleanup_plan(plan, visualizations=visualizations)

    return {'daily_plans': [plan]}, 202


@app.route('/<uuid:user_id>/exercise_modalities', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str, 'recovery_type': str})
@xray_recorder.capture('routes.active_recovery.exercise_modalities.start')
def handle_exercise_modalities_start(user_id=None):
    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']
    recovery_index = request.json.get('recovery_index', 0)

    plan_event_day = format_date(event_date)
    recovery_start_date = format_datetime(event_date)
    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    plan = daily_plan_datastore.get(user_id=user_id,
                                    start_date=plan_event_day,
                                    end_date=plan_event_day)[0]
    # plans_service = Service('plans', Config.get('API_VERSION'))
    # body = {"event_date": recovery_start_date}
    # if recovery_type == 'pre_active_rest':
    #     if recovery_index + 1 > len(plan.pre_active_rest):
    #         raise NoSuchEntityException('No pre active rest found with that index')
    #     plan.pre_active_rest[recovery_index].start_date_time = recovery_start_date
    #     plans_service.call_apigateway_async(method='POST',
    #                                         endpoint=f'/athlete/{user_id}/prep_started',
    #                                         body=body)
    #
    # elif recovery_type == 'post_active_rest':
    #     if recovery_index + 1 > len(plan.post_active_rest):
    #         raise NoSuchEntityException('No post active rest found with that index')
    #     plan.post_active_rest[recovery_index].start_date_time = recovery_start_date
    #     plans_service.call_apigateway_async(method='POST',
    #                                         endpoint=f'/athlete/{user_id}/recovery_started',
    #                                         body=body)
    #
    # elif recovery_type in ['warm_up', 'cool_down', 'functional_strength']:
    modalities = [m for m in plan.modalities if m.type.name == recovery_type and not m.completed]
    if len(modalities) > 0:
        modality = modalities[0]
        modality.start_date_time = recovery_start_date

    daily_plan_datastore.put(plan)

    return {'message': 'success'}, 200


@app.route('/<uuid:user_id>/get_mobilize', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.active_recovery.get_mobilize')
def handle_request_mobilize(user_id=None):
    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_day = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    plan = daily_plan_datastore.get(user_id=user_id,
                                    start_date=plan_event_day,
                                    end_date=plan_event_day)[0]

    visualizations = is_fathom_environment()

    if plan.train_later:
        if len(plan.pre_active_rest) == 0:
            force_data = True
        elif plan.pre_active_rest[0].force_data:
            force_data = True
        else:
            force_data = False
    else:
        if len(plan.post_active_rest) == 0:
            force_data = True
        elif plan.post_active_rest[0].force_data:
            force_data = True
        else:
            force_data = False
    hist_update = False
    athlete_stats = athlete_stats_datastore.get(user_id)
    if athlete_stats.api_version in [None, '4_4', '4_5']:
        hist_update = True
    plan = create_plan(user_id,
                       event_date,
                       update_stats=True,
                       athlete_stats=athlete_stats,
                       datastore_collection=datastore_collection,
                       force_data=force_data,
                       mobilize_only=True,
                       visualizations=visualizations,
                       hist_update=hist_update)

    # plan = cleanup_plan(plan, visualizations=visualizations)

    return {'daily_plans': [plan]}, 200


@app.route('/<uuid:user_id>/body_part_modalities', methods=['PATCH'])
@require.authenticated.any
@require.body({'event_date': str, 'recovery_type': str})
@xray_recorder.capture('routes.active_recovery.body_part_modalities.complete')
def handle_body_part_modalities_complete(user_id=None):
    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    recovery_type = request.json['recovery_type']
    completed_body_parts = request.json.get('completed_body_parts', [])

    visualizations = is_fathom_environment()

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

    # survey_complete = plan.daily_readiness_survey_completed()
    # landing_screen, nav_bar_indicator = plan.define_landing_screen()
    # plan = plan.json_serialise()
    # plan['daily_readiness_survey_completed'] = survey_complete
    # plan['landing_screen'] = landing_screen
    # plan['nav_bar_indicator'] = nav_bar_indicator
    # del plan['daily_readiness_survey'], plan['user_id']

    plan = cleanup_plan(plan, visualizations=visualizations)

    return {'daily_plans': [plan]}, 202


@app.route('/<uuid:user_id>/body_part_modalities', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str, 'recovery_type': str})
@xray_recorder.capture('routes.active_recovery.body_part_modalities.start')
def handle_body_part_modalities_start(user_id=None):
    #user_id = principal_id
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
        plan.cold_water_immersion.start_date_time = start_date_time

    daily_plan_datastore.put(plan)

    return {'message': 'success'}, 200


@app.route('/<uuid:user_id>/get_modality', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str, 'type': int})
@xray_recorder.capture('routes.active_recovery.get_modality')
def handle_request_modality(user_id=None):
    event_date = parse_datetime(request.json['event_date'])
    modality_type = request.json['type']
    plan_event_day = format_date(event_date)
    if not _check_plan_exists(user_id, plan_event_day):
        raise NoSuchEntityException('Plan not found for the user')

    plan = daily_plan_datastore.get(user_id=user_id,
                                    start_date=plan_event_day,
                                    end_date=plan_event_day)[0]

    visualizations = is_fathom_environment()

    force_data = False
    if modality_type == 0:
        pre_active_rests = [m for m in plan.modalities if m.type.value == modality_type]
        if len(pre_active_rests) == 0:
            force_data = True
        elif pre_active_rests[0].force_data:
            force_data = True
        else:
            force_data = False
    elif modality_type == 1:
        post_active_rests = [m for m in plan.modalities if m.type.value == modality_type]
        if len(post_active_rests) == 0:
            force_data = True
        elif post_active_rests[0].force_data:
            force_data = True
        else:
            force_data = False

    athlete_stats = athlete_stats_datastore.get(user_id)

    hist_update = False
    if athlete_stats.api_version in [None, '4_4', '4_5']:
        hist_update = True
    if hist_update:
        athlete_stats = process_stats(user_id, event_date, athlete_stats, hist_update)
        athlete_stats_datastore.put(athlete_stats)

    plan = add_modality_on_demand(user_id, event_date, modality_type=modality_type, athlete_stats=athlete_stats,
                                  visualizations=visualizations, force_data=force_data)

    return {'daily_plans': [plan]}, 200


def save_completed_exercises(exercise_list, user_id, event_date):
    for exercise in exercise_list:
        completed_exercise_datastore.put(CompletedExercise(athlete_id=user_id,
                                                           exercise_id=exercise,
                                                           event_date=event_date))


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    return mongo_collection.count({"user_id": user_id, "date": event_date}) == 1
