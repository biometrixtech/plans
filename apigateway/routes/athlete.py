from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from flask import Blueprint, request
from datastores.datastore_collection import DatastoreCollection
from logic.training_plan_management import TrainingPlanManager
from logic.stats_processing import StatsProcessing
from logic.metrics_processing import MetricsProcessing
from logic.user_stats_processing import UserStatsProcessing
from models.stats import AthleteStats
from utils import parse_date, parse_datetime, format_date
from routes.environments import is_fathom_environment
import datetime
import pytz
import random
import os


app = Blueprint('athlete', __name__)
USERS_API_VERSION = os.environ['USERS_API_VERSION']


@app.route('/<uuid:athlete_id>/daily_plan', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete.daily_plan.create')
def create_daily_plan(athlete_id):
    event_date = request.json.get('event_date', None)
    # target_minutes = request.json.get('target_minutes', 15)
    last_updated = request.json.get('last_updated', None)
    plan_manager = TrainingPlanManager(athlete_id, DatastoreCollection())
    visualizations = is_fathom_environment()
    daily_plan = plan_manager.create_daily_plan(event_date=event_date,
                                                # target_minutes=target_minutes,
                                                last_updated=last_updated,
                                                visualizations=visualizations)
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
    if is_fathom_environment():
        athlete_stats = StatsProcessing(athlete_id, event_date=parse_date(event_date), datastore_collection=DatastoreCollection()).process_athlete_stats()

        if event_date is not None:
            metrics = MetricsProcessing().get_athlete_metrics_from_stats(athlete_stats, event_date)
            athlete_stats.metrics = metrics

        DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
    else:
        user_stats = UserStatsProcessing(athlete_id, event_date=parse_date(event_date), datastore_collection=DatastoreCollection()).process_user_stats(force_historical_process=False)
        DatastoreCollection().user_stats_datastore.put(user_stats)

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
    except Exception as e:
        print(e)
        pass

    if is_fathom_environment():
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
        athlete_stats.event_date = datetime.datetime.now().replace(tzinfo=pytz.utc)

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
    if (plan and  # plan exists
            len(plan.pre_active_rest) > 0 and  # pre_active_rest is assigned
            _are_exercises_assigned(plan.pre_active_rest[0], 'pre') and  # and exercises are present
            plan.pre_active_rest[0].start_date_time is None and  # and not started
            plan.pre_active_rest[0].active and  # and still active
            not plan.pre_active_rest_completed):  # and one hasn't been completed previously
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
    if (plan and  # plan is present
            len(plan.post_active_rest) > 0 and  # post_active_rest is assigned
            _are_exercises_assigned(plan.post_active_rest[0], 'post') and  # and exercises are present
            plan.post_active_rest[0].start_date_time is None and  # and not started
            plan.post_active_rest[0].active and  # is still active
            not plan.post_active_rest_completed):  # and one hasn't been completed previously
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
    return {"message": "Scheduled"}, 202


@app.route('/<uuid:athlete_id>/recovery_started', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.recovery_pn')
def schedule_recovery_completion_push_notification(athlete_id):
    execute_at = datetime.datetime.now() + datetime.timedelta(minutes=60)
    body = {"recovery_type": "recovery",
            "event_date": format_date(parse_datetime(request.json["event_date"]))}
    plans_service = Service('plans', Config.get('API_VERSION'))
    plans_service.call_apigateway_async(method='POST',
                                        endpoint=f'/athlete/{athlete_id}/send_completion_notification',
                                        body=body,
                                        execute_at=execute_at)
    return {"message": "Scheduled"}, 202


@app.route('/<uuid:athlete_id>/send_completion_notification', methods=['POST'])
@require.authenticated.service
@xray_recorder.capture('routes.athlete.completion_pn')
def manage_recovery_completion_push_notification(athlete_id):
    recovery_type = request.json['recovery_type']
    event_date = request.json['event_date']
    plan = _get_plan(athlete_id, event_date)
    if (recovery_type == 'prep' and  # is pre_active_rest
            plan and len(plan.pre_active_rest) > 0 and  # and pre_active_rest is assigned
            plan.pre_active_rest[0].start_date_time is not None and  # and started
            plan.pre_active_rest[0].active and  # and is still active
            not plan.pre_active_rest[0].completed):  # and not completed
        body = {"message": "Take time to invest in yourself. Let's finish your exercises!",
                "call_to_action": "COMPLETE_ACTIVE_PREP"}
        _notify_user(athlete_id, body)
        return {'message': 'User Notified'}, 200

    elif (recovery_type == 'recovery' and  # is post_active_rest
            plan and len(plan.post_active_rest) > 0 and  # and post_active_rest is assigned
            plan.post_active_rest[0].start_date_time is not None and  # and started
            plan.post_active_rest[0].active and  # and is still active
            not plan.post_active_rest[0].completed):  # and not completed
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
    today = datetime.datetime.now()
    fourteen_days = today - datetime.timedelta(days=14)
    daily_plans = DatastoreCollection().daily_plan_datastore.get(user_id=athlete_id, start_date=format_date(fourteen_days), end_date=format_date(today), stats_processing=True)
    if any([plan.daily_readiness_survey_completed() for plan in daily_plans]):
        return True
    else:
        return False


def _notify_user(athlete_id, body):
    if is_fathom_environment():
        users_service = Service('users', USERS_API_VERSION)
        users_service.call_apigateway_async(method='POST',
                                            endpoint=f'/user/{athlete_id}/notify',
                                            body=body)


def _randomize_trigger_time(start_time, window, tz_offset):
    offset_from_start = random.randint(0, window)
    local_date = parse_datetime(start_time) + datetime.timedelta(seconds=offset_from_start)
    utc_date = local_date - datetime.timedelta(minutes=tz_offset)
    return utc_date.replace(tzinfo=None)


def _are_exercises_assigned(rec, rec_type):
    exercises = (len(rec.inhibit_exercises) +
                 len(rec.static_stretch_exercises) +
                 len(rec.static_integrate_exercises) +
                 len(rec.isolated_activate_exercises))
    if rec_type == 'pre':
        exercises += len(rec.active_stretch_exercises)
    return exercises > 0


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
