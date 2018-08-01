from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint

from decorators import authentication_required
from exceptions import InvalidSchemaException, NoSuchEntityException
from datastores.daily_plan_datastore import DailyPlanDatastore
from utils import format_date
from config import get_mongo_collection

app = Blueprint('active_recovery', __name__)


@app.route('/', methods=['PATCH'])
@authentication_required
@xray_recorder.capture('routes.active_recovery')
def handle_active_recovery_update():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = format_date(request.json['event_date'])
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')
    try:
        user_id = request.json['user_id']
    except:
        raise InvalidSchemaException('user_id is required')
    try:
        recovery_type = request.json['recovery_type']
    except:
        raise InvalidSchemaException('recovery_type is required')
    if not _check_plan_exists(user_id, event_date):
        raise NoSuchEntityException('Plan not found for the user')
    store = DailyPlanDatastore()
    plan = store.get(user_id=user_id, start_date=event_date, end_date=event_date)[0]
    if recovery_type == 'pre':
        plan.pre_recovery_completed = True
        if plan.pre_recovery is not None:
            plan.pre_recovery.completed = True
    elif recovery_type == 'post':
        plan.post_recovery_completed = True
        if plan.post_recovery is not None:
            plan.post_recovery.completed = True

    store.put(plan)

    survey_complete = plan.daily_readiness_survey_completed()
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = survey_complete
    del plan['daily_readiness_survey'], plan['user_id']


    return {'daily_plans': [plan]}, 202


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False
