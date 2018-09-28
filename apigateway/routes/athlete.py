from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from flask import Blueprint, request
from datastores.datastore_collection import DatastoreCollection
from logic.training_plan_management import TrainingPlanManager
from logic.stats_processing import StatsProcessing
from serialisable import json_serialise
from utils import parse_date, parse_datetime, format_date, format_datetime
import boto3
import json
import os
import datetime
import random


app = Blueprint('athlete', __name__)
iotd_client = boto3.client('iot-data')


@app.route('/<uuid:athlete_id>/daily_plan', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.daily_plan.create')
def create_daily_plan(athlete_id):
    daily_plan = TrainingPlanManager(athlete_id, DatastoreCollection()).create_daily_plan()
    # daily_plan.last_updated = format_datetime(datetime.datetime.now())
    push_plan_update(athlete_id, daily_plan)

    Service('plans', Config.get('API_VERSION')).call_apigateway_async('POST', f"athlete/{athlete_id}/stats")

    return {'message': 'Update requested'}, 202


@app.route('/<uuid:athlete_id>/stats', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.stats.update')
def update_athlete_stats(athlete_id):
    StatsProcessing(athlete_id, event_date=None, datastore_collection=DatastoreCollection()).process_athlete_stats()
    return {'message': 'Update requested'}, 202

@app.route('/<uuid:athlete_id>/active', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.pn.manage')
def manage_athlete_push_notification(athlete_id):
    if _is_athlete_active(athlete_id):
        current_time_utc = datetime.datetime.utcnow()
        current_time_local = current_time_utc + datetime.timedelta(hours=request.json['timezone'])
        current_date_local = current_time_local.date()

        readiness_date_local = format_date(current_date_local) + 'T08:00:00Z'
        readiness_date_local = parse_datetime(readiness_date_local) + datetime.timedelta(minutes=random.randint(0, 60))
        readiness_date_utc = readiness_date_local - datetime.timedelta(hours=request.json['timezone'])
        readiness_event_date = format_datetime(readiness_date_utc)

        prep_date_local = format_date(current_date_local) + 'T18:00:00Z'
        prep_pn_time = random.randint(0, 90)
        prep_date_local = parse_datetime(prep_date_local) + datetime.timedelta(minutes=prep_pn_time)
        prep_date_utc = prep_date_local - datetime.timedelta(hours=request.json['timezone'])
        prep_event_date = format_datetime(prep_date_utc)

        recovery_date_utc = prep_date_utc + datetime.timedelta(minutes=random.randint(0, 210-prep_pn_time))
        recovery_event_date = format_datetime(recovery_date_utc)

        body = {"event_date": format_date(current_date_local)}
        Service('plans', Config.get('API_VERSION')).call_apigateway_sync('POST', f"athlete/{athlete_id}/send_daily_readiness_notification", body=body, execute_at=readiness_event_date)
        Service('plans', Config.get('API_VERSION')).call_apigateway_sync('POST', f"athlete/{athlete_id}/send_active_prep_notification", body=body, execute_at=prep_event_date)
        Service('plans', Config.get('API_VERSION')).call_apigateway_sync('POST', f"athlete/{athlete_id}/send_recovery_notification", body=body, execute_at=recovery_event_date)
    else:
        raise ValueError


@app.route('/<uuid:athlete_id>/send_daily_readiness_notification', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.readiness_pn')
def manage_readiness_push_notification(athlete_id):
    event_date = format_date(parse_date(request.json['event_date']))
    plan = _get_plan(athlete_id, event_date)
    if not plan or not plan.daily_readiness_survey_completed():
        body = {"message": "Good morning, Ivonna. Let’s make the most of your day! Tap to get started.",
                "call_to_action": "COMPLETE_DAILY_READINESS"}
        Service('users', '2_0').call_apigateway_sync('POST', f'/user/{user.id}/notify', body=body)

@app.route('/<uuid:athlete_id>/send_active_prep_notification', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.prep_pn')
def manage_prep_push_notification(athlete_id):
    event_date = format_date(parse_date(request.json['event_date']))
    plan = _get_plan(athlete_id, event_date)
    if plan and not plan.pre_recovery_completed and plan.pre_recovery.impact_score > 3:
        body = {"message": "Your self care ritual is ready. Take time to invest in yourself.",
                "call_to_action": "COMPLETE_ACTIVE_PREP"}
        Service('users', '2_0').call_apigateway_sync('POST', f'/user/{user.id}/notify', body=body)


@app.route('/<uuid:athlete_id>/send_recovery_notification', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.recovery_pn')
def manage_recovery_push_notification(athlete_id):
    event_date = format_date(parse_date(request.json['event_date']))
    plan = _get_plan(athlete_id, event_date)
    if plan and not plan.post_recovery_completed and plan.post_recovery.impact_score > 3:
        body = {"message": "Your self care ritual is ready. Take time to invest in yourself.",
                "call_to_action": "COMPLETE_ACTIVE_RECOVERY"}
        Service('users', '2_0').call_apigateway_sync('POST', f'/user/{user.id}/notify', body=body)


def _get_plan(user_id, event_date):
    plans = DatastoreCollection().daily_plan_datastore.get(user_id, event_date, event_date)
    if len(plans) == 0:
        return False
    else:
        return plan[0]

def _is_athlete_active(athlete_id):
    athlete_stats = DatastoreCollection().athlete_stats_datastore.get(athlete_id=athlete_id)
    if athlete_stats is not None and athlete_stats.event_date > datetime.datetime.now() - datetime.timedelta(days=14):
        return True
    else:
        return False


@xray_recorder.capture('routes.athlete.daily_plan.push')
def push_plan_update(user_id, daily_plan):
    iotd_client.publish(
        topic='plans/{}/athlete/{}/daily_plan'.format(os.environ['ENVIRONMENT'], user_id),
        payload=json.dumps({'daily_plan': daily_plan}, default=json_serialise).encode()
    )
