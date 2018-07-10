from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import json
import os
import datetime
import jwt
# import uuid

# from auth import get_accessory_id_from_auth
from datastore import DailyPlanDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException
from models.daily_plan import DailyPlan


app = Blueprint('daily_plan', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.daily_plan.get')
def handle_daily_plan_get():

    user_id = request.json['user_id']
    # date = datetime.datetime.today().strftime("%Y-%m-%d")
    date = '2018-06-27' # pass dummy date
    store = DailyPlanDatastore()
    daily_plan = store.get(user_id, date, collection='dailyplan')
    return {'daily_plan': daily_plan}, 200

