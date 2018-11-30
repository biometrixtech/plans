from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from fathomapi.utils.exceptions import NoSuchEntityException
from flask import Blueprint, request
from datastores.datastore_collection import DatastoreCollection
from logic.training_plan_management import TrainingPlanManager
from logic.stats_processing import StatsProcessing
from logic.metrics_processing import MetricsProcessing
from serialisable import json_serialise
from utils import parse_date, parse_datetime, format_date, format_datetime
import boto3
import json
import os
import datetime
import random


app = Blueprint('athlete', __name__)
iotd_client = boto3.client('iot-data')
USERS_API_VERSION = '2_0'


@app.route('/<uuid:athlete_id>/daily_plan', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.daily_plan.create')
def create_daily_plan(athlete_id):
    daily_plan = TrainingPlanManager(athlete_id, DatastoreCollection()).create_daily_plan()
    # daily_plan.last_updated = format_datetime(datetime.datetime.now())
    # push_plan_update(athlete_id, daily_plan)
    body = {"message": "Your plan is ready!",
            "call_to_action": "VIEW_PLAN"}
    _notify_user(athlete_id, body)
    event_date = daily_plan.event_date
    Service('plans', Config.get('API_VERSION')).call_apigateway_async(method='POST',
                                                                      endpoint=f"athlete/{athlete_id}/stats",
                                                                      body={"event_date": event_date})

    return {'message': 'Update requested'}, 202


@app.route('/<uuid:athlete_id>/stats', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.stats.update')
def update_athlete_stats(athlete_id):
    if 'event_date' in request.json:
        event_date = request.json['event_date']
    else:
        event_date = None
    StatsProcessing(athlete_id, event_date=event_date, datastore_collection=DatastoreCollection()).process_athlete_stats()

    if event_date is not None:
        Service('plans', Config.get('API_VERSION')).call_apigateway_async(method='POST',
                                                                          endpoint=f"athlete/{athlete_id}/metrics",
                                                                          body={"event_date": event_date})
    return {'message': 'Update requested'}, 202


@app.route('/<uuid:athlete_id>/metrics', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.metrics.update')
def get_athlete_metrics(athlete_id):
    event_date = request.json['event_date']
    athlete_stats = DatastoreCollection().athlete_stats_datastore.get(athlete_id=athlete_id)
    metrics = MetricsProcessing().get_athlete_metrics_from_stats(athlete_stats, event_date)
    athlete_stats.metrics = metrics
    DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
    return {'message': 'Update requested'}, 202


@app.route('/<uuid:athlete_id>/active', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.pn.manage')
def manage_athlete_push_notification(athlete_id):
    # Make sure stats are consistent
    try:
        minute_offset = _get_offset()
        event_date = format_date(datetime.datetime.now() + datetime.timedelta(minutes=minute_offset))
        Service('plans', Config.get('API_VERSION')).call_apigateway_async(method='POST',
                                                                          endpoint=f"athlete/{athlete_id}/stats",
                                                                          body={"event_date": event_date})
    except:
        pass
    if not _is_athlete_active(athlete_id):
        return {'message': 'Athlete is not active'}, 200

    _schedule_notifications(athlete_id)

    return {'message': 'Processed'}, 202


def _schedule_notifications(athlete_id):
    """
    Schedule checks for three notifications
    1) readiness -- between 10am and 11am local time
    2) prep -- between 6pm and 9:30pm local time
    3) recovery -- between 6pm and 9:30pm local time
    Checks are to be performed for the date it scheduled for which could be different from
    the current local date
    """
    minute_offset = _get_offset()
    plans_service = Service('plans', Config.get('API_VERSION'))
    trigger_event_date = format_date(datetime.datetime.now())
    body = {"event_date": trigger_event_date}

    # schedule readiness PN check
    readiness_start = trigger_event_date + 'T10:00:00Z'
    readiness_event_date = _randomize_trigger_time(readiness_start, 60, minute_offset)
    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f"athlete/{athlete_id}/send_daily_readiness_notification",
                                        body=body,
                                        execute_at=readiness_event_date)

    # schedule prep and recovery PN check
    prep_rec_start = trigger_event_date + 'T18:00:00Z'
    prep_event_date = _randomize_trigger_time(prep_rec_start, 210, minute_offset)
    recovery_event_date = _randomize_trigger_time(prep_rec_start, 210, minute_offset)

    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f"athlete/{athlete_id}/send_active_prep_notification",
                                        body=body,
                                        execute_at=prep_event_date)
    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f"athlete/{athlete_id}/send_recovery_notification",
                                        body=body,
                                        execute_at=recovery_event_date)
    print(readiness_event_date, prep_event_date, recovery_event_date)


@app.route('/<uuid:athlete_id>/send_daily_readiness_notification', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.readiness_pn')
def manage_readiness_push_notification(athlete_id):
    event_date = format_date(parse_date(request.json['event_date']))
    plan = _get_plan(athlete_id, event_date)
    if not plan or not plan.daily_readiness_survey_completed():
        body = {"message": "Good morning, {first_name}. Let’s make the most of your day! Tap to get started.",
                "call_to_action": "COMPLETE_DAILY_READINESS"}
        _notify_user(athlete_id, body)
        return {'message': 'User Notified'}, 200
    else:
        return {'message': 'Do not need to notify user'}, 200


@app.route('/<uuid:athlete_id>/send_active_prep_notification', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.prep_pn')
def manage_prep_push_notification(athlete_id):
    event_date = format_date(parse_date(request.json['event_date']))
    plan = _get_plan(athlete_id, event_date)
    if plan and not plan.pre_recovery_completed and plan.pre_recovery.start_date is None and plan.pre_recovery.impact_score >= 3 and _are_exercises_assigned(plan.pre_recovery) and plan.post_recovery.goal_text == "":
        body = {"message": "Your prep exercises are ready! Tap to to get started!",
                "call_to_action": "COMPLETE_ACTIVE_PREP"}
        _notify_user(athlete_id, body)
        return {'message': 'User Notified'}, 200
    else:
        return {'message': 'Do not need to notify user'}, 200


@app.route('/<uuid:athlete_id>/send_recovery_notification', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.recovery_pn')
def manage_recovery_push_notification(athlete_id):
    event_date = format_date(parse_date(request.json['event_date']))
    plan = _get_plan(athlete_id, event_date)
    if plan and not plan.post_recovery_completed and plan.post_recovery.start_date is None and plan.post_recovery.impact_score >= 3 and _are_exercises_assigned(plan.post_recovery):
        body = {"message": "Your recovery exercises are ready! Tap to begin taking care!",
                "call_to_action": "COMPLETE_ACTIVE_RECOVERY"}
        _notify_user(athlete_id, body)
        return {'message': 'User Notified'}, 200
    else:
        return {'message': 'Do not need to notify user'}, 200


@app.route('/<uuid:athlete_id>/prep_started', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.completion_pn')
def schedule_prep_completion_push_notification(athlete_id):
    execute_at = datetime.datetime.now() + datetime.timedelta(minutes=30)
    print(f"scheduled prep notification at {execute_at}")
    body = {"recovery_type": "prep",
            "event_date": format_date(parse_datetime(request.json["event_date"]))}
    plans_service = Service('plans', Config.get('API_VERSION'))
    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f'/athlete/{athlete_id}/send_completion_notification',
                                        body=body,
                                        execute_at=execute_at)
    return {"messate": "Scheduled"}, 202

@app.route('/<uuid:athlete_id>/recovery_started', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.recovery_pn')
def schedule_recovery_completion_push_notification(athlete_id):
    execute_at = datetime.datetime.now() + datetime.timedelta(minutes=30)
    # execute_at = format_datetime(execute_at)
    body = {"recovery_type": "recovery",
            "event_date": format_date(parse_datetime(request.json["event_date"]))}
    plans_service = Service('plans', Config.get('API_VERSION'))
    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f'/athlete/{athlete_id}/send_completion_notification',
                                        body=body,
                                        execute_at=execute_at)
    return {"messate": "Scheduled"}, 202

@app.route('/<uuid:athlete_id>/send_completion_notification', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.completion_pn')
def manage_recovery_completion_push_notification(athlete_id):
    recovery_type = request.json['recovery_type']
    event_date = format_date(parse_date(request.json['event_date']))
    plan = _get_plan(athlete_id, event_date)
    if recovery_type=='prep' and plan and plan.pre_recovery.start_date is not None and not plan.pre_recovery_completed and plan.post_recovery.goal_text == "":
        body = {"message": "Take time to invest in yourself. Let's finish your exercises!",
                "call_to_action": "COMPLETE_ACTIVE_PREP"}
        _notify_user(athlete_id, body)
        return {'message': 'User Notified'}, 200

    elif recovery_type=='recovery' and plan and plan.post_recovery.start_date is not None and not plan.post_recovery.completed:
        body = {"message": "Take time to invest in yourself. Let's finish your exercises!",
                "call_to_action": "COMPLETE_ACTIVE_RECOVERY"}
        _notify_user(athlete_id, body)
        return {'message': 'User Notified'}, 200
    else:
        return {'message': 'Do not need to notify user'}, 200


def _get_plan(user_id, event_date):
    plans = DatastoreCollection().daily_plan_datastore.get(user_id, event_date, event_date)
    plan = plans[0]
    if not plan.daily_readiness_survey_completed():
        return False
    else:
        return plan


def _is_athlete_active(athlete_id):
    try:
        daily_readiness = DatastoreCollection().daily_readiness_datastore.get(user_id=athlete_id, last_only=True)[0]
        if format_date(daily_readiness.event_date) >= format_date(datetime.datetime.now() - datetime.timedelta(days=14)):
            return True
        else:
            return False
    except NoSuchEntityException:
        return False


def _notify_user(athlete_id, body):
    users_service = Service('users', USERS_API_VERSION)
    users_service.call_apigateway_async(method='POST',
                                       endpoint=f'/user/{athlete_id}/notify',
                                       body=body)


def _randomize_trigger_time(start_time, window, tz_offset):
    offset_from_start = random.randint(0, window)
    local_date = parse_datetime(start_time) + datetime.timedelta(minutes=offset_from_start)
    utc_date = local_date - datetime.timedelta(minutes=tz_offset)
    return utc_date

def _are_exercises_assigned(rec):
    exercises = (len(rec.inhibit_exercises) +
                 len(rec.lengthen_exercises) +
                 len(rec.activate_exercises) +
                 len (rec.integrate_exercises))
    if exercises > 0:
        return True
    else:
        return False

def _get_offset():
    tz = request.json['timezone']
    offset = tz.split(":")
    hour_offset = int(offset[0])
    minute_offset = int(offset[1])
    if hour_offset < 0:
        minute_offset = hour_offset * 60 - minute_offset
    else:
        minute_offset += hour_offset * 60
    return minute_offset
