from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import base64
# import boto3
# import datetime
import json
import re
import os
# import uuid

# from auth import get_accessory_id_from_auth
from datastore import DailyReadinessDatastore
# from decorators import authentication_required
from exceptions import InvalidSchemaException, ApplicationException, NoSuchEntityException, DuplicateEntityException
from models.daily_readiness import DailyReadiness
from logic.soreness_and_injury import SorenessType, MuscleSorenessSeverity, JointSorenessSeverity, BodyPart


app = Blueprint('daily_readiness', __name__)


# @authentication_required
# @xray_recorder.capture('routes.session.create')
@app.route('/daily_readiness', methods=['POST'])
def handle_daily_readiness_create():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'date_time' not in request.json:
        raise InvalidSchemaException('Missing required parameter date_time')
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
            else:
                soreness['body_part'] = int(soreness['body_part'])
            if not SorenessType(soreness['soreness_type']):
                raise InvalidSchemaException('soreness_type not recognized')
            else:
                if SorenessType(soreness['soreness_type']) == SorenessType.muscle_related:
                    if not MuscleSorenessSeverity(soreness['severity']):
                        raise InvalidSchemaException('severity not recognized')
                elif SorenessType(soreness['soreness_type']) == SorenessType.joint_related:
                    if not JointSorenessSeverity(soreness['severity']):
                        raise InvalidSchemaException('severity not recognized')

    # validate sleep_quality
    if 'sleep_quality' not in request.json:
        raise InvalidSchemaException('Missing required parameter sleep_quality')
    elif request.json['sleep_quality'] not in [1,2,3,4,5,6,7,8,9,10]:
        raise InvalidSchemaException('sleep_quality need to be between 1 and 10')

    # vlaidate readiness
    if 'readiness' not in request.json:
        raise InvalidSchemaException('Missing required parameter readiness')
    elif request.json['readiness'] not in [1,2,3,4,5,6,7,8,9,10]:
        raise InvalidSchemaException('readiness need to be between 1 and 10')



    # now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
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
        return {'daily_readiness': daily_readiness}, 201
    except DuplicateEntityException:
        print(json.dumps({'message': 'daily_readiness already created for user {}'.format(daily_readiness.get_id())}))
        return {'duplicate daily_readiness record'}, 201
