from flask import request, Blueprint
import datetime
import os
from bson import ObjectId

from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import ForbiddenException
from fathomapi.utils.xray import xray_recorder
from config import get_mongo_collection, get_mongo_database
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from utils import format_date, parse_datetime, parse_date, validate_uuid4

from models.app_logs import AppLogs

app = Blueprint('misc', __name__)
USERS_API_VERSION = os.environ['USERS_API_VERSION']


@app.route('/<uuid:user_id>/clear_user_data', methods=['POST'])
@require.body({'event_date': str})
@require.authenticated.self
@xray_recorder.capture('routes.misc.clearuser')
def handle_clear_user_data(user_id=None):
    # users_service = Service('users', '2_0')
    # user_data = users_service.call_apigateway_sync(method='GET',
    #                                                endpoint=f'user/{principal_id}')
    # user_email = user_data['user']['personal_data']['email']
    # if email not in [
    #     "dipesh+mvp@fathomai.com",
    #     "dipesh@fathomai.com",
    #     "mazen+mvp@fathomai.com",
    #     "mazen@fathomai.com",
    #     "chrisp+mvp@fathomai.com",
    #     "ivonna+mvp@fathomai.com",
    #     "gabby+mvp@fathomai.com",
    #     "maria+mvp@fathomai.com",
    #     "melissa+mvp@fathomai.com",
    #     "amina+mvp@fathomai.com",
    #     "paul+mvp@fathomai.com",
    #     "hello+demo1@fathomai.com",
    #     "hello+demo2@fathomai.com",
    #     "hello+demo3@fathomai.com",
    #     "hello+demo4@fathomai.com",
    #     "hello+demo5@fathomai.com"
    # ]:
    #     raise ForbiddenException("The user is not allowed to perform this action.")
    #user_id = principal_id

    current_time = parse_datetime(request.json['event_date'])

    # get collections
    readiness = get_mongo_collection('dailyreadiness')
    daily_plan = get_mongo_collection('dailyplan')
    stats = get_mongo_collection('athletestats')
    exercises = get_mongo_collection('completedexercises')

    today = format_date(current_time)
    tomorrow = format_date(current_time + datetime.timedelta(days=1))

    result = readiness.delete_many({"user_id": user_id, "event_date": {"$gte": today, "$lt": tomorrow}})
    print("readiness surveys deleted: {}".format(result.deleted_count))
    result = daily_plan.delete_one({"user_id": user_id, "date": today})
    print("daily plans deleted: {}".format(result.deleted_count))
    result = exercises.delete_many({"athlete_id": user_id, "event_date": {"$gte": today, "$lt": tomorrow}})
    print("completed exercises deleted: {}".format(result.deleted_count))
    # Update stats to reset it to yesterday's state
    yesterday = format_date(current_time - datetime.timedelta(days=1))
    res = Service('plans', Config.get('API_VERSION')).call_apigateway_sync('POST', f"athlete/{user_id}/stats", body={"event_date": yesterday})
    print(res)

    if 'clear_all' in request.json and request.json['clear_all']:
        readiness.delete_many({"user_id": user_id})
        daily_plan.delete_many({"user_id": user_id})
        exercises.delete_many({"athlete_id": user_id})
        stats.delete_one({"athlete_id": user_id})

    return {'message': 'success'}, 200


@app.route('/cognito_migration', methods=['PATCH'])
@xray_recorder.capture('routes.misc.cognito_migration')
def handle_data_migration():
    """update user_id in all relevant mongo collections to the new id
        collections to update:
            ---v3 data---
            athleteStats: athlete_id
            completedExercises: athlete_id
            dailyPlan: user_id
            dailyReadiness: user_id
            ---v2 data---
            activeBlockStats: userId
            dateStats: userId
            progCompDateStats: userId
            progCompStats: userId
            sessionStats: userId
            twoMinuteStats: userId
    """
    legacy_user_id = request.json['legacy_user_id']
    user_id = request.json['user_id']
    query = {"user_id": legacy_user_id}
    mongo_collection = get_mongo_collection('dailyplan')
    mongo_collection.update_many(query, {'$set': {'user_id': user_id}})
    mongo_collection = get_mongo_collection('dailyreadiness')
    mongo_collection.update_many(query, {'$set': {'user_id': user_id}})

    query = {"athlete_id": legacy_user_id}
    mongo_collection = get_mongo_collection('athletestats')
    mongo_collection.update_many(query, {'$set': {'athlete_id': user_id}})
    mongo_collection = get_mongo_collection('completedexercises')
    mongo_collection.update_many(query, {'$set': {'athlete_id': user_id}})

    mongo_database = get_mongo_database()

    query = {"userId": str(legacy_user_id)}
    mongo_collection = mongo_database['activeBlockStats']
    mongo_collection.update_many(query, {'$set': {'userId': user_id}})
    mongo_collection = mongo_database['dateStats']
    mongo_collection.update_many(query, {'$set': {'userId': user_id}})
    mongo_collection = mongo_database['progCompDateStats']
    mongo_collection.update_many(query, {'$set': {'userId': user_id}})
    mongo_collection = mongo_database['progCompStats']
    mongo_collection.update_many(query, {'$set': {'userId': user_id}})
    mongo_collection = mongo_database['sessionStats']
    mongo_collection.update_many(query, {'$set': {'userId': user_id}})
    mongo_collection = mongo_database['twoMinuteStats']
    mongo_collection.update_many(query, {'$set': {'userId': user_id}})

    return {'message': 'success'}, 200


@app.route('/<uuid:user_id>/app_logs', methods=['POST'])
@require.authenticated.self
@xray_recorder.capture('routes.misc.app_logs')
def handle_app_open_tracking(user_id=None):
    event_date = request.json['event_date']
    mongo_collection = get_mongo_collection('applogs')
    log = AppLogs(user_id, event_date)
    log.os_name = request.json.get('os_name', None)
    log.os_version = request.json.get('os_version', None)
    log.app_version = request.json.get('app_version', None)
    log.plans_api_version = Config.get('API_VERSION')

    mongo_collection.replace_one(log.get_filter_condition(), log.json_serialise(), upsert=True)

    return {'message': 'success'}, 200


@app.route('/<uuid:user_id>/copy_test_data', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.misc.copy_test_data')
def handle_test_data_copy(user_id=None):
    """Copy data for test user from test collection
    """
    if Config.get('ENVIRONMENT') == 'production':
        raise ForbiddenException("This API is only allowed in develop/test environment")
    #user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])

    mongo_database = get_mongo_database()
    stats_collection_test = mongo_database['athleteStatsTest']

    # Datastores for personas collections
    athlete_stats_datastore_test = AthleteStatsDatastore(mongo_collection='athletestatstest')
    rs_datastore_test = DailyReadinessDatastore(mongo_collection='dailyreadinesstest')
    daily_plan_datastore_test = DailyPlanDatastore(mongo_collection='dailyplantest')
    # completed_exercises_datastore_test = CompletedExerciseDatastore(get_mongo_collection='completedexercisestest')

    # datastores to copy data to
    athlete_stats_datastore = AthleteStatsDatastore()
    rs_datastore = DailyReadinessDatastore()
    daily_plan_datastore = DailyPlanDatastore()
    completed_exercises_datastore = CompletedExerciseDatastore()

    if request.json["copy_all"]:
        mongo_results = stats_collection_test.find()
        athlete_stats = []
        for mongo_result in mongo_results:
            athlete_stats.append(athlete_stats_datastore_test.get_athlete_stats_from_mongo(mongo_result))
        user_id = [stat.athlete_id for stat in athlete_stats]
    else:
        athlete_stats = [athlete_stats_datastore_test.get(user_id)]

    # clear all existing data
    rs_datastore.delete(user_id=user_id)
    daily_plan_datastore.delete(user_id=user_id)
    completed_exercises_datastore.delete(athlete_id=user_id)
    athlete_stats_datastore.delete(athlete_id=user_id)

    # get data from test collections
    # readiness_surveys = rs_datastore_test.get(user_id, last_only=False)
    # if len(readiness_surveys) == 0:
    #     raise ForbiddenException("No data present to copy")
    daily_plans = daily_plan_datastore_test.get(user_id)

    # update to current date
    update_dates(daily_plans, athlete_stats, event_date)

    # write the updated data
    # rs_datastore.put(readiness_surveys)
    daily_plan_datastore.put(daily_plans)
    athlete_stats_datastore.put(athlete_stats)

    return {'message': 'success'}, 202


def update_dates(daily_plans, athlete_stats, event_date):
    athlete_today = athlete_stats[0].event_date
    day_diff = (event_date - athlete_today).days
    delta = datetime.timedelta(days=day_diff)
    # for rs_survey in rs_surveys:
    #     rs_survey.event_date += delta

    for plan in daily_plans:
        plan.event_date = format_date(parse_date(plan.event_date) + delta)
        for ts in plan.training_sessions:
            ts.event_date += delta
            if ts.post_session_survey is not None:
                ts.post_session_survey.event_date += delta
        if plan.daily_readiness_survey is not None:
            plan.daily_readiness_survey.event_date += delta
    for stat in athlete_stats:
        stat.event_date = event_date
        for hs in stat.historic_soreness:
            if hs.streak_start_date is not None:
                hs.streak_start_date = hs.streak_start_date + delta
            if hs.last_reported_date_time is not None:
                hs.last_reported_date_time = hs.last_reported_date_time + delta


@app.route('/dailycron', methods=['POST'])
@xray_recorder.capture('routes.misc.dailycron')
def handle_dailycron():
    # This route will be called daily via a CloudWatch Scheduled Event.
    Service('plans', Config.get('API_VERSION')).call_apigateway_async('POST', 'misc/activeusers', body={})

    return {'status': 'Success'}, 200


@app.route('/activeusers', methods=['POST'])
@require.authenticated.any
@require.body({})
@xray_recorder.capture('routes.misc.activeusers')
def handle_activeusers():
    last_user = request.json.get('last_user', None)
    # This route will be invoked daily.  It should scan to find users which meet
    # some definition of 'active', and for each one should push to the plans service with them
    batch_users, last_user = _get_user_batch(last_user)

    # remove users that are api_version < 4_4 (they'll go throuh the old route)
    batch_users = [user for user in batch_users if user['api_version'] != '4_3']

    now = datetime.datetime.now()
    three_am_today = datetime.datetime(now.year, now.month, now.day, 3, 0, 0)

    # group users by timezone to dictate when to execute
    timezones = set(user['timezone'] for user in batch_users)
    print(timezones)
    for timezone in timezones:
        execute_at = three_am_today - datetime.timedelta(minutes=_get_offset(timezone))  # this will be specific for timezone
        tz_users = [user for user in batch_users if user['timezone'] == timezone]
        body = {"timezone": timezone}

        # now group users by their last used api version
        api_versions = set(user['api_version'] for user in tz_users)
        for api_version in api_versions:
            tz_api_users = [user for user in tz_users if user['api_version'] == api_version]
            tz_api_calls = []
            for user in tz_api_users:
                tz_api_calls.append({'method': 'POST', 'endpoint': f"athlete/{user['id']}/active", 'body': body})

            print(f'{len(tz_api_calls)} users (in this batch) for timezone: {timezone} and api_version: {api_version}')
            # schedule async calls to happen at 3am local time for the user
            plans_service = Service('plans', api_version)
            plans_service.call_apigateway_async_multi(calls=tz_api_calls, jitter=10 * 60, execute_at=execute_at)

    # check if we've reached end of list, if not trigger next batch
    if last_user is not None:
        print('Triggering next batch')
        self_service = Service('plans', Config.get('API_VERSION'))
        self_service.call_apigateway_async('POST', 'misc/activeusers', body={'last_user': str(last_user)}, execute_at=now + datetime.timedelta(seconds=60))

    return {'status': 'Success'}


def _get_user_batch(last_user):
    end_reached = False
    stats_collection = get_mongo_collection('athletestats')
    if last_user is None:
        query = {}
    else:
        query = {"_id": {"$gt": ObjectId(last_user)}}
    users = stats_collection.find(query, projection=["athlete_id", "timezone", "api_version"], limit=100)
    if users.count() < 100:
        end_reached = True
    batch_users = []
    for user in users:
        last_user = user['_id']
        if isinstance(user['athlete_id'], str) and validate_uuid4(user['athlete_id']):
            batch_users.append(
                    {
                        'id': user['athlete_id'],
                        'timezone': user.get('timezone', '-04:00'),
                        'api_version': user.get('api_version', '4_3')
                    }
            )
    if end_reached:
        last_user = None
    return batch_users, last_user


def _get_offset(tz):
    offset = tz.split(":")
    hour_offset = int(offset[0])
    minute_offset = int(offset[1])
    if hour_offset < 0:
        minute_offset = hour_offset * 60 - minute_offset
    else:
        minute_offset += hour_offset * 60
    return minute_offset
