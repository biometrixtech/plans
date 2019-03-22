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
from models.stats import AthleteStats
from utils import parse_datetime, format_date
import boto3
import datetime
import random
import os


app = Blueprint('athlete', __name__)
iotd_client = boto3.client('iot-data')
USERS_API_VERSION = os.environ['USERS_API_VERSION']


@app.route('/<uuid:athlete_id>/daily_plan', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.daily_plan.create')
def create_daily_plan(athlete_id):
    event_date = request.json.get('event_date', None)
    target_minutes = request.json.get('target_minutes', 15)
    last_updated = request.json.get('last_updated', None)
    plan_manager = TrainingPlanManager(athlete_id, DatastoreCollection())
    daily_plan = plan_manager.create_daily_plan(event_date=event_date,
                                                target_minutes=target_minutes,
                                                last_updated=last_updated)
    body = {"message": "Your plan is ready!",
            "call_to_action": "VIEW_PLAN",
            "last_updated": last_updated}
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
    event_date = request.json.get('event_date', None)
    athlete_stats = StatsProcessing(athlete_id, event_date=event_date, datastore_collection=DatastoreCollection()).process_athlete_stats()

    if event_date is not None:
        metrics = MetricsProcessing().get_athlete_metrics_from_stats(athlete_stats, event_date)
        athlete_stats.metrics = metrics

    DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
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
        event_date = format_date(datetime.datetime.now())
        stats_update_time = event_date + 'T03:30:00Z'
        trigger_event_date = _randomize_trigger_time(stats_update_time, 10*60, minute_offset)

        Service('plans', Config.get('API_VERSION')).call_apigateway_async(method='POST',
                                                                          endpoint=f"athlete/{athlete_id}/stats",
                                                                          body={"event_date": event_date},
                                                                          execute_at=trigger_event_date)
    except:
        pass
    if not _is_athlete_active(athlete_id):
        return {'message': 'Athlete is not active'}, 200

    _schedule_notifications(athlete_id)

    return {'message': 'Processed'}, 202


@app.route('/<uuid:athlete_id>/survey', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.survey')
def process_athlete_survey(athlete_id):
    athlete_stats = DatastoreCollection().athlete_stats_datastore.get(athlete_id=athlete_id)
    if athlete_stats is None:
        athlete_stats = AthleteStats(athlete_id)

    if 'typical_weekly_sessions' in request.json:
        athlete_stats.typical_weekly_sessions = request.json['typical_weekly_sessions']
        typ_sessions_exp_workout = {"0-1": 0.5, "2-4": 3.0, "5+": 5.0, None: None}
        athlete_stats.expected_weekly_workouts = typ_sessions_exp_workout[request.json['typical_weekly_sessions']]
    if 'wearable_devices' in request.json:
        athlete_stats.wearable_devices = request.json['wearable_devices']
    DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
    return {'message': 'success'}, 200


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
    readiness_event_date = _randomize_trigger_time(readiness_start, 60*60, minute_offset)
    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f"athlete/{athlete_id}/send_daily_readiness_notification",
                                        body=body,
                                        execute_at=readiness_event_date)

    # schedule prep and recovery PN check
    prep_rec_start = trigger_event_date + 'T18:00:00Z'
    prep_event_date = _randomize_trigger_time(prep_rec_start, 210*60, minute_offset)
    recovery_event_date = _randomize_trigger_time(prep_rec_start, 210*60, minute_offset)

    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f"athlete/{athlete_id}/send_active_prep_notification",
                                        body=body,
                                        execute_at=prep_event_date)
    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f"athlete/{athlete_id}/send_recovery_notification",
                                        body=body,
                                        execute_at=recovery_event_date)


@app.route('/<uuid:athlete_id>/send_daily_readiness_notification', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.readiness_pn')
def manage_readiness_push_notification(athlete_id):
    event_date = request.json['event_date']
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
    event_date = request.json['event_date']
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
    event_date = request.json['event_date']
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
    execute_at = datetime.datetime.now() + datetime.timedelta(minutes=60)
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
    execute_at = datetime.datetime.now() + datetime.timedelta(minutes=60)
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
    event_date = request.json['event_date']
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
    local_date = parse_datetime(start_time) + datetime.timedelta(seconds=offset_from_start)
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
