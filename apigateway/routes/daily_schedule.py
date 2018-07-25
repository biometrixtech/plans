from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import datetime
import os

from decorators import authentication_required
from exceptions import InvalidSchemaException
from config import get_mongo_collection
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.session_datastore import SessionDatastore, _create_session
from models.daily_plan import DailyPlan

app = Blueprint('daily_schedule', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.daily_schedule')
def handle_daily_schedule_create():
    user_id = request.json['user_id']
    event_date = request.json['event_date']
    if not check_plan_exists():
        plan = DailyPlan(event_date=event_date)
        plan.user_id = user_id
        DailyPlanDatastore().put(plan)

    sessions = request.json['sessions']
    session_store = SessionDatastore()
    for session in sessions:
        item = _create_session(user_id=user_id,
                               session_type=session['session_type'],
                               data={'description':'test'})
        session_store.insert(item, user_id=user_id, event_date=event_date)



def check_plan_exists():
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": request.json['user_id'],
                               "date": request.json['event_date']}) == 1:
        return True
    else:
        return False
