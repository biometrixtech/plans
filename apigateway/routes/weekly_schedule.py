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
    # if today_weekday < 4:
    #     delta = today_weekday
    # elif today_weekday >=4:
    #     delta = 7 - today_weekday

    # dates = []
    # for day in days:
    #     dates.append((today + datetime.timedelta(days=day-delta)).strftime("%Y-%m-%d"))

    if today_weekday < 4:
        monday_delta = -today_weekday
    elif today_weekday >= 4:
        monday_delta =  7 - today_weekday
    week_start = (today + datetime.timedelta(days=monday_delta)).strftime("%Y-%m-%d")

    schedule = WeeklyCrossTrainingSchedule(
        user_id=request.json['user_id'],
        week_start=week_start,
        dates=request.json['days'],
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
    today = datetime.datetime.today()
    today_weekday = today.weekday()
    # if today_weekday < 4:
    #     delta = today_weekday
    # elif today_weekday >= 4:
    #     delta = 7 - today_weekday

    if today_weekday < 4:
        monday_delta = -today_weekday
    elif today_weekday >= 4:
        monday_delta =  7 - today_weekday
    week_start = (today + datetime.timedelta(days=monday_delta)).strftime("%Y-%m-%d")

    # for sport in request.json['sports']:
    #     practice_days = sport['practice']['days']
    #     practice_dates = convert_date(practice_days)
    #     sport['practice']['days'] = practice_dates
    #     competition_days = sport['competition']['days']
    #     competition_dates = convert_date(competition_days)
    #     sport['competition']['days'] = competition_dates

    schedule = WeeklyTrainingSchedule(
        user_id=request.json['user_id'],
        week_start=week_start,
        sports=request.json['sports'],
    )
    store = WeeklyTrainingDatastore()

    store.put(schedule, collection='training')
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


def convert_date(days):
    today = datetime.datetime.today()
    dates = []
    for day in days:
        day = today + datetime.timedelta(days=day)
        dates.append(day.strftime("%Y-%m-%d"))
    return dates