from aws_xray_sdk.core import xray_recorder
from decorators import authentication_required
from flask import Blueprint, request
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from datastores.exercise_datastore import ExerciseLibraryDatastore
from logic.training_plan_management import TrainingPlanManager
from logic.stats_processing import StatsProcessing
from utils import format_datetime, run_async
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
    daily_plan = TrainingPlanManager(athlete_id, ExerciseLibraryDatastore(), DailyReadinessDatastore(),
                                     PostSessionSurveyDatastore(), DailyPlanDatastore()).create_daily_plan()
    # daily_plan.last_updated = format_datetime(datetime.datetime.now())
    print(request)
    push_plan_update(athlete_id, daily_plan)

    endpoint = "athlete/{}/stats".format(athlete_id)
    headers = {'Authorization': request.headers['Authorization'],
                'Content-Type': 'applicaiton/json'}
    body = {'event_date': request.json['event_date']}
    run_async(endpoint, method='POST', body=body, headers=headers)

    return {'message': 'Update requested'}, 202


@app.route('/<uuid:athlete_id>/stats', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.athlete.stats.update')
def update_athlete_stats(athlete_id):
    event_date = request.json['event_date']
    StatsProcessing(athlete_id, event_date, DailyReadinessDatastore(), PostSessionSurveyDatastore()).calc_athlete_stats()
    return {'message': 'Update requested'}, 202


@xray_recorder.capture('routes.athlete.daily_plan.push')
def push_plan_update(user_id, daily_plan):
    iotd_client.publish(
        topic='plans/{}/athlete/{}/daily_plan'.format(os.environ['ENVIRONMENT'], user_id),
        payload=json.dumps({'daily_plan': daily_plan}, default=json_serialise).encode()
    )
