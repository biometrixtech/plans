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
from datastore import SorenessDatastore
# from decorators import authentication_required
from exceptions import InvalidSchemaException, ApplicationException, NoSuchEntityException, DuplicateEntityException
from models.soreness_and_injury import SorenessAndInjury

app = Blueprint('soreness', __name__)


# @authentication_required
# @xray_recorder.capture('routes.session.create')
@app.route('/soreness', methods=['POST'])
def handle_soreness_create():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'date' not in request.json:
        raise InvalidSchemaException('Missing required parameter date')

    # now = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    soreness = SorenessAndInjury(
        user_id=request.json['user_id'],
        date=request.json['date'],
        soreness=request.json['soreness'],  # dailysoreness object array
        sleep_quality=request.json['sleep_quality'],
        readiness=request.json['readiness']

    )
    print(soreness)
    store = SorenessDatastore()
    try:
        store.put(soreness)
        return {'soreness': soreness}, 201
    except DuplicateEntityException:
        print(json.dumps({'message': 'soreness already created for user {}'.format(soreness.get_id())}))
        return {'duplicate sorenss record'}, 201
