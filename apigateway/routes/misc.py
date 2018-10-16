from flask import request, Blueprint
import datetime
from utils import format_date, parse_datetime

from config import get_mongo_collection, get_mongo_database
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import ForbiddenException
from fathomapi.utils.xray import xray_recorder

app = Blueprint('misc', __name__)
USERS_API_VERSION = '2_0'

@app.route('/clear_user_data', methods=['POST'])
@require.body({'event_date': str})
@require.authenticated.any
@xray_recorder.capture('routes.misc.clearuser')
def handle_clear_user_data(principal_id=None):
    users_service = Service('users', USERS_API_VERSION)
    print(users_service.name, users_service.version, principal_id)
    print(f'/user/{principal_id}')
    user_data = users_service.call_apigateway_sync(method='GET',
                                                   endpoint=f"user/{principal_id}")
    user_email = user_data['user']['personal_data']['email']
    if email not in [
        "dipesh+mvp@fathomai.com",
        "dipesh@fathomai.com",
        "mazen+mvp@fathomai.com",
        "mazen@fathomai.com",
        "chrisp+mvp@fathomai.com",
        "ivonna+mvp@fathomai.com",
        "gabby+mvp@fathomai.com",
        "maria+mvp@fathomai.com",
        "melissa+mvp@fathomai.com",
        "amina+mvp@fathomai.com",
        "paul+mvp@fathomai.com",
        "hello+demo1@fathomai.com",
        "hello+demo2@fathomai.com",
        "hello+demo3@fathomai.com",
        "hello+demo4@fathomai.com",
        "hello+demo5@fathomai.com"
    ]:
        raise ForbiddenException("The user is not allowed to perform this action.")
    user_id = principal_id

    current_time = parse_datetime(request.json['event_date'])

    if current_time.hour < 3:
        current_time -= datetime.timedelta(days=1)

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
    Service('plans', Config.get('API_VERSION')).call_apigateway_sync('POST', f"athlete/{athlete_id}/stats")

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
