from aws_xray_sdk.core import xray_recorder
from decorators import authentication_required
from flask import Blueprint
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.daily_schedule_datastore import DailyScheduleDatastore
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from logic.training_plan_management import TrainingPlanManager
from utils import format_datetime
from serialisable import json_serialise
import boto3
import datetime
import json
import os


app = Blueprint('athlete', __name__)
iotd_client = boto3.client('iot-data')


@app.route('/<uuid:athlete_id>/daily_plan', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.athlete.daily_plan.create')
def create_daily_plan(athlete_id):
    daily_plan_outcome = TrainingPlanManager(athlete_id, DailyReadinessDatastore(), DailyScheduleDatastore(),
                                     DailyPlanDatastore()).create_daily_plan()
    # daily_plan.last_updated = format_datetime(datetime.datetime.now())

    push_plan_update(athlete_id, daily_plan_outcome)
    return {'message': 'Update requested'}, 202


@xray_recorder.capture('routes.athlete.daily_plan.push')
def push_plan_update(user_id, daily_plan_outcome):
    iotd_client.publish(
        topic='plans/{}/athlete/{}/daily_plan'.format(os.environ['ENVIRONMENT'], user_id),
        payload=json.dumps({'daily_plan': 'Plan Outcome: ' + str(daily_plan_outcome)}, default=json_serialise).encode()
    )
