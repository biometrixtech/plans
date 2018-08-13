from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import datetime
import jwt
from utils import format_date, parse_datetime

from config import get_mongo_collection
from decorators import authentication_required
from exceptions import ForbiddenException, InvalidSchemaException
app = Blueprint('misc', __name__)


@app.route('/clear_user_data', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.misc.clearuser')
def handle_clear_user_data():
    user_id = jwt.decode(request.headers['Authorization'], verify=False)['user_id']
    if user_id not in  ['c4f3ba9c-c874-4687-bbb8-67633a6a6d7d', # dipesh
                        'a1233423-73d3-4761-ac92-89cc15921d34', # mazen
                        '', # demo1 (test)
                        '', # demo2 (test)
                        '', # demo3 (test)
                        '', # demo4 (test)
                        '', # demo5 (test)
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
    readiness.delete_many({"user_id": user_id, "event_date": {"$gte": today, "$lt": tomorrow}})
    daily_plan = get_mongo_collection('dailyplan')
    daily_plan.delete_one({"user_id": user_id, "date": today})

    return {'message': 'Success'}, 200
