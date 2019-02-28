from flask import request, Blueprint
import datetime
import os
from utils import format_date, parse_datetime, parse_date
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from config import get_mongo_collection, get_mongo_database
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import ForbiddenException
from fathomapi.utils.xray import xray_recorder

from models.app_logs import AppLogs

app = Blueprint('misc', __name__)
USERS_API_VERSION = os.environ['USERS_API_VERSION']

@app.route('/clear_user_data', methods=['POST'])
@require.body({'event_date': str})
@require.authenticated.any
@xray_recorder.capture('routes.misc.clearuser')
def handle_clear_user_data(principal_id=None):
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
    user_id = principal_id

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

    return {'message': 'success'}, 202


@app.route('/app_logs', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.misc.app_logs')
def handle_app_open_tracking(principal_id=None):
    event_date = request.json['event_date']
    mongo_collection = get_mongo_collection('applogs')
    log = AppLogs(principal_id, event_date)
    log.os_name = request.json.get('os_name', None)
    log.os_version = request.json.get('os_version', None)
    log.app_version = request.json.get('app_version', None)
    log.plans_api_version = Config.get('API_VERSION')

    mongo_collection.replace_one(log.get_filter_condition(), log.json_serialise(), upsert=True)

    return {'message': 'success'}, 200


@app.route('/copy_test_data', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.misc.copy_test_data')
def handle_test_data_copy(principal_id=None):
    """Copy data for test user from test collection
    """
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])

    # get required collections
    plan_collection = get_mongo_collection('dailyplan')
    readiness_collection = get_mongo_collection('dailyreadiness')
    stats_collection = get_mongo_collection('athletestats')
    completed_exercises_collection = get_mongo_collection('completedexercises')

    mongo_database = get_mongo_database()
    plan_collection_test = mongo_database['dailyPlanTest']
    readiness_collection_test = mongo_database['dailyReadinessTest']
    stats_collection_test = mongo_database['athleteStatsTest']
    # completed_exercises_collection_test = mongo_database['completedExercisesTest']

    # clear all existing data
    readiness_collection.delete_many({"user_id": user_id})
    plan_collection.delete_many({"user_id": user_id})
    completed_exercises_collection.delete_many({"athlete_id": user_id})
    stats_collection.delete_one({"athlete_id": user_id})
    # get data from test collections
    rs_datastore = DailyReadinessDatastore()
    readiness_surveys = rs_datastore.get(user_id,
                                         last_only=False,
                                         mongo_collection=readiness_collection_test)
    daily_plan_datastore = DailyPlanDatastore()
    daily_plans = daily_plan_datastore.get(user_id,
                                           mongo_collection=plan_collection_test)
    athlete_stats_datastore = AthleteStatsDatastore()
    athlete_stats = athlete_stats_datastore.get(user_id,
                                                mongo_collection=stats_collection_test)

    update_dates(readiness_surveys, daily_plans, athlete_stats, event_date)
    rs_datastore.put(readiness_surveys)
    daily_plan_datastore.put(daily_plans)
    athlete_stats_datastore.put(athlete_stats)

    return {'message': 'success'}, 202

def update_dates(rs_surveys, daily_plans, athlete_stats, event_date):
    athlete_today = parse_date(athlete_stats.event_date)
    day_diff = (event_date - athlete_today).days
    for rs_survey in rs_surveys:
        rs_survey.event_date += datetime.timedelta(days=day_diff)

    for plan in daily_plans:
        plan.event_date = format_date(parse_date(plan.event_date) + datetime.timedelta(days=day_diff))
    athlete_stats.event_date = format_date(event_date)


