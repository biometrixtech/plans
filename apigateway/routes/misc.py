from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import datetime
import jwt
from utils import format_date, parse_datetime

from config import get_mongo_collection, get_mongo_database
from decorators import authentication_required
from exceptions import ForbiddenException, InvalidSchemaException
app = Blueprint('misc', __name__)


@app.route('/clear_user_data', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.misc.clearuser')
def handle_clear_user_data():
    user_id = jwt.decode(request.headers['Authorization'], verify=False)['user_id']
    if user_id not in  ["c4f3ba9c-c874-4687-bbb8-67633a6a6d7d", # dipesh+mvp@fathomai.com
                        "a1233423-73d3-4761-ac92-89cc15921d34", # mazen+mvp@fathomai.com
                        "e155d933-8353-4157-8c17-061c7d1e7dcb", # chris+mvp@fathomai.com
                        "b0501843-f067-48c3-a99b-bf3b56f4db04", # ivonna+mvp@fathomai.com
                        "f45d72a8-4569-42b7-bbfd-79e810983b00", # gabby+mvp@fathomai.com
                        "9930c5cd-0ae7-43f3-aee4-de621e935525", # maria+mvp@fathomai.com
                        "a045f81b-477a-4a31-ae65-1dd46bcafc0c", # melissa+mvp@fathomai.com
                        "1092081e-30f9-4886-b94f-36f993ba9065", # amina+mvp@fathomai.com
                        "bf9f61b3-a985-49ef-b733-9f34309942a5", # paul+mvp@fathomai.com
                        "ad328899-f8e6-4070-8878-73bf84c79699", # hello+demo1@fathomai.com
                        "c1394094-c8e2-4880-b940-237d41d4118e", # hello+demo2@fathomai.com
                        "9138da93-d054-45d2-9149-2572523b49da", # hello+demo3@fathomai.com
                        "865f9e91-00b6-418b-a037-5a5d322a7e34", # hello+demo4@fathomai.com
                        "74bfd848-dc85-4025-a612-ff76d1b9eaa9", # hello+demo5@fathomai.com
                        ]:
        raise ForbiddenException("The user is not allowed to perform this action.")
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        current_time = parse_datetime(request.json['event_date'])
    if current_time.hour < 3:
        current_time -= datetime.timedelta(days=1)
    today = format_date(current_time)
    tomorrow = format_date(current_time + datetime.timedelta(days=1))
    readiness = get_mongo_collection('dailyreadiness')
    result = readiness.delete_many({"user_id": user_id, "event_date": {"$gte": today, "$lt": tomorrow}})
    print("readiness surveys deleted: {}".format(result.deleted_count))
    daily_plan = get_mongo_collection('dailyplan')
    result = daily_plan.delete_one({"user_id": user_id, "date": today})
    print("daily plans deleted: {}".format(result.deleted_count))

    if 'clear_all' in request.json:
        if request.json['clear_all']:
            stats = get_mongo_collection('athletestats')
            execises = get_mongo_collection('completedexercises')
            stats.delete_one({"athlete_id": user_id})
            exercises.delete_many({"athlete_id": user_id, "event_date": {"$gte": today, "$lt": tomorrow}})
            print("readiness surveys deleted: {}".format(result.deleted_count))

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
    # Sample code for mongo update
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
