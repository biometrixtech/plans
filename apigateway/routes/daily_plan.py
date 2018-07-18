from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import json
import datetime

from datastores.daily_plan_datastore import DailyPlanDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException

app = Blueprint('daily_plan', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.daily_plan.get')
def handle_daily_plan_get():
    validate_input(request)

    user_id = request.json['user_id']
    start_date = request.json['start_date']
    if 'end_date' in request.json:
        end_date = request.json['end_date']
    else:
        end_date = start_date
    store = DailyPlanDatastore()
    items = store.get(user_id, start_date, end_date)
    daily_plans = []
    for plan in items:
        survey_complete = plan.daily_readiness_survey_completed()
        plan = plan.json_serialise()
        plan['daily_readiness_survey_completed'] = survey_complete
        del plan['daily_readiness_survey'], plan['user_id']
        daily_plans.append(plan)

    return {'daily_plans': daily_plans}, 200


def validate_input(request):
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter user_id')
    if 'start_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter start_date')
    else:
        try:
            datetime.datetime.strptime(request.json['start_date'], "%Y-%m-%d")
        except:
            raise InvalidSchemaException('start_date needs to be in format yyyy-mm-dd')
    if 'end_date' in request.json:
        try:
            datetime.datetime.strptime(request.json['end_date'], "%Y-%m-%d")
        except:
            raise InvalidSchemaException('end_date needs to be in format yyyy-mm-dd')
