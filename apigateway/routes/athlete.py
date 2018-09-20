from aws_xray_sdk.core import xray_recorder
from decorators import authentication_required
from flask import Blueprint
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from datastores.datastore_collection import DatastoreCollection
from logic.training_plan_management import TrainingPlanManager
from logic.stats_processing import StatsProcessing
from utils import run_async
from serialisable import json_serialise
import boto3
import json
import os


app = Blueprint('athlete', __name__)
iotd_client = boto3.client('iot-data')


@app.route('/<uuid:athlete_id>/daily_plan', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.athlete.daily_plan.create')
def create_daily_plan(athlete_id):
    daily_plan = TrainingPlanManager(athlete_id, DatastoreCollection()).create_daily_plan()
    # daily_plan.last_updated = format_datetime(datetime.datetime.now())
    push_plan_update(athlete_id, daily_plan)

    run_async('POST', f"athlete/{athlete_id}/stats")

    return {'message': 'Update requested'}, 202


@app.route('/<uuid:athlete_id>/stats', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.athlete.stats.update')
def update_athlete_stats(athlete_id):
    StatsProcessing(athlete_id, event_date=None, datastore_collection=DatastoreCollection()).process_athlete_stats()
    return {'message': 'Update requested'}, 202


@xray_recorder.capture('routes.athlete.daily_plan.push')
def push_plan_update(user_id, daily_plan):
    iotd_client.publish(
        topic='plans/{}/athlete/{}/daily_plan'.format(os.environ['ENVIRONMENT'], user_id),
        payload=json.dumps({'daily_plan': daily_plan}, default=json_serialise).encode()
    )
