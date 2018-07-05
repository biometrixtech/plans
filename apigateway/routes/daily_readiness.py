from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import json
import os
import datetime
# import uuid

# from auth import get_accessory_id_from_auth
from datastore import DailyReadinessDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException, ApplicationException, NoSuchEntityException, DuplicateEntityException
from models.daily_readiness import DailyReadiness
from logic.soreness_and_injury import SorenessType, MuscleSorenessSeverity, JointSorenessSeverity, BodyPart


app = Blueprint('daily_readiness', __name__)


@app.route('/daily_readiness', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.daily_readiness.create')
def handle_daily_readiness_create():
    validate_data(request)

    daily_readiness = DailyReadiness(
        user_id=request.json['user_id'],
        date_time=request.json['date_time'],
        soreness=request.json['soreness'],  # dailysoreness object array
        sleep_quality=request.json['sleep_quality'],
        readiness=request.json['readiness']

    )
    store = DailyReadinessDatastore()
    try:
        store.put(daily_readiness)
        return {'message': 'success'}, 201
        # return {'daily_readiness': daily_readiness}, 201
    except DuplicateEntityException:
        print(json.dumps({'message': 'daily_readiness already created for user {}'.format(daily_readiness.get_id())}))
        return {'duplicate daily_readiness record'}, 201



@app.route('daily_readiness/previous', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.daily_readiness.previous')
def handle_get_previous_soreness():
    current_time = datetime.datetime.now()
    store = DailyReadinessDatastore()
    soreness = store.get(user_id=request.json['user_id'])
    return {'body_part': soreness}, 200



@xray_recorder.capture('routes.daily_readiness.validate')
def validate_data(request):
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'date_time' not in request.json:
        raise InvalidSchemaException('Missing required parameter date_time')
    else:
        try:
            datetime.datetime.strptime(request.json['date_time'], "%Y-%m-%d %H:%M:%S.%f")
        except:
            try:
                datetime.datetime.strptime(request.json['date_time'], "%Y-%m-%d %H:%M:%S")
            except:
                raise InvalidSchemaException('date_time needs to be in format yyyy-mm-dd hh:mm:ss.xxxx or yyyy-mm-dd hh:mm:ss')


# check to make sure date_time is date and time
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter user_id')

    # validate soreness
    if 'soreness' not in request.json:
        raise InvalidSchemaException('Missing required parameter soreness')
    elif not isinstance(request.json['soreness'], list):
        raise InvalidSchemaException('soreness must be a list')
    else:
        for soreness in request.json['soreness']:
            if not BodyPart(soreness['body_part']):
                raise InvalidSchemaException('body_part not recognized')
            elif not MuscleSorenessSeverity(soreness['severity']):
                raise InvalidSchemaException('severity not recognized')
            # for valid ones, force values to be integer
            soreness['body_part'] = int(soreness['body_part'])
            soreness['severity'] = int(soreness['severity'])

    # validate sleep_quality
    if 'sleep_quality' not in request.json:
        raise InvalidSchemaException('Missing required parameter sleep_quality')
    elif request.json['sleep_quality'] not in range(1, 11):
        raise InvalidSchemaException('sleep_quality need to be between 1 and 10')

    # vlaidate readiness
    if 'readiness' not in request.json:
        raise InvalidSchemaException('Missing required parameter readiness')
    elif request.json['readiness'] not in range(1, 11):
        raise InvalidSchemaException('readiness need to be between 1 and 10')