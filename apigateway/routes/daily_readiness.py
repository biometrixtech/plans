from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import jwt

from datastores.daily_readiness_datastore import DailyReadinessDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException
from models.daily_readiness import DailyReadiness
from logic.soreness_and_injury import MuscleSorenessSeverity, BodyPartLocation
from utils import parse_datetime
import requests

app = Blueprint('daily_readiness', __name__)

@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.daily_readiness.create')
def handle_daily_readiness_create():
    validate_data()

    daily_readiness = DailyReadiness(
        user_id=request.json['user_id'],
        event_date=request.json['date_time'],
        soreness=request.json['soreness'],  # dailysoreness object array
        sleep_quality=request.json['sleep_quality'],
        readiness=request.json['readiness']

    )
    store = DailyReadinessDatastore()
    store.put(daily_readiness)

    # endpoint = "https://apis.{}.fathomai.com/plans/athlete/{}/daily_plan".format(os.environ['ENVIRONMENT'], request.json['user_id'])
    # headers = {'Authorization': request.headers['Authorization'],
    #             'Content-Type': 'applicaiton/json'}
 
    # r = requests.post(url=endpoint, headers=headers)


    return {'message': 'success'}, 201


@app.route('/previous', methods=['GET'])
@authentication_required
@xray_recorder.capture('routes.daily_readiness.previous')
def handle_daily_readiness_get():
    store = DailyReadinessDatastore()
    user_id = jwt.decode(request.headers['Authorization'], verify=False)['user_id']
    daily_readiness = store.get(user_id=user_id)
    return {'body_parts': daily_readiness.json_serialise()['sore_body_parts']}, 200


@xray_recorder.capture('routes.daily_readiness.validate')
def validate_data():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')

    if 'date_time' not in request.json:
        raise InvalidSchemaException('Missing required parameter date_time')
    parse_datetime(request.json['date_time'])

    # validate soreness
    if 'soreness' not in request.json:
        raise InvalidSchemaException('Missing required parameter soreness')
    if not isinstance(request.json['soreness'], list):
        raise InvalidSchemaException('soreness must be a list')
    for soreness in request.json['soreness']:
        try:
            BodyPartLocation(soreness['body_part'])
        except ValueError:
            raise InvalidSchemaException('body_part not recognized')
        try:
            MuscleSorenessSeverity(soreness['severity'])
        except ValueError:
            raise InvalidSchemaException('severity not recognized')
        # for valid ones, force values to be integer
        soreness['body_part'] = int(soreness['body_part'])
        soreness['severity'] = int(soreness['severity'])

    # validate sleep_quality
    if 'sleep_quality' not in request.json:
        raise InvalidSchemaException('Missing required parameter sleep_quality')
    elif request.json['sleep_quality'] not in range(1, 11):
        raise InvalidSchemaException('sleep_quality need to be between 1 and 10')

    # validate readiness
    if 'readiness' not in request.json:
        raise InvalidSchemaException('Missing required parameter readiness')
    elif request.json['readiness'] not in range(1, 11):
        raise InvalidSchemaException('readiness need to be between 1 and 10')
