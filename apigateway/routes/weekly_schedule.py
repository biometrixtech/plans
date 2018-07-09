from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import json
import os
import datetime
import jwt
# import uuid

# from auth import get_accessory_id_from_auth
from datastore import WeeklyCrossTrainingDatastore, WeeklyTrainingDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException, ApplicationException, NoSuchEntityException, DuplicateEntityException
from models.weekly_schedule import WeeklyCrossTrainingSchedule, WeeklyTrainingSchedule
from logic.soreness_and_injury import SorenessType, MuscleSorenessSeverity, JointSorenessSeverity, BodyPart


app = Blueprint('weekly_schedule', __name__)


@app.route('/cross_training', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.weekly_schedule.cross_training.create')
def handle_crosstraining_schedule_create():
    validate_data(request)
    days = request.json['days']
    today = datetime.datetime.today()
    today_weekday = today.weekday()
    if today_weekday < 4:
        delta = today_weekday
    elif today_weekday >=4:
        delta = 7 - today_weekday

    dates = []
    for day in days:
        dates.append((today + datetime.timedelta(days=day-delta)).strftime("%Y-%m-%d"))

    monday_delta = -today_weekday
    week_start = (today + datetime.timedelta(days=monday_delta)).strftime("%Y-%m-%d")

    schedule = WeeklyCrossTrainingSchedule(
        user_id=request.json['user_id'],
        week_start=week_start,
        dates=dates,
        activities=request.json['activities'],
        duration=request.json['durations'],
    )

    store = WeeklyCrossTrainingDatastore()

    store.put(schedule, collection='crosstraining')
    return {'message': 'success'}, 201

@app.route('/cross_training/get_schedule', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.weekly_schedule.cross_training.get')
def handle_crosstraining_schedule_get():
    pass


@app.route('/cross_training/update', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.weekly_schedule.cross_training.update')
def handle_crosstraining_schedule_update():
    pass


@app.route('/training', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.weekly_schedule.training.create')
def handle_training_schedule_create():
    validate_data(request)
    days = request.json['days']
    today = datetime.datetime.today()
    today_weekday = today.weekday()
    if today_weekday < 4:
        delta = today_weekday
    elif today_weekday >=4:
        delta = 7 - today_weekday

    dates = []
    for day in days:
        dates.append((today + datetime.timedelta(days=day-delta)).strftime("%Y-%m-%d"))

    monday_delta = -today_weekday
    week_start = (today + datetime.timedelta(days=monday_delta)).strftime("%Y-%m-%d")

    schedules = []
    for sport in request.json['schedules']:
        schedule = WeeklyTrainingSchedule(
            user_id=request.json['user_id'],
            week_start=week_start,
            sport=sport['sport'],
            practice=sport['practice'],
            competition=sport['competition']
        )
        schedules.append(schedule)

    store = WeeklyTrainingDatastore()

    store.put(schedules, collection='training')
    return {'message': 'success'}, 201

@app.route('/training/get_schedule', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.weekly_schedule.cross_training.get')
def handle_training_schedule_get():
    pass


@app.route('/training/update', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.weekly_schedule.cross_training.update')
def handle_training_schedule_update():
    pass


@xray_recorder.capture('routes.weekly_schedule.validate')
def validate_data(request):
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter user_id')