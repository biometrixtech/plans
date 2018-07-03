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

app = Blueprint('daily_readiness', __name__)


# @authentication_required
# @xray_recorder.capture('routes.session.create')
@app.route('/daily_readiness', methods=['POST'])
def handle_daily_readiness_create():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'date_time' not in request.json:
        raise InvalidSchemaException('Missing required parameter date_time')

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
