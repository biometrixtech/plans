from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import jwt
import datetime

from datastores.daily_readiness_datastore import DailyReadinessDatastore
from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException, NoSuchEntityException
from models.daily_readiness import DailyReadiness
from models.soreness import MuscleSorenessSeverity, BodyPartLocation
from utils import parse_datetime, format_datetime, run_async

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

    run_async('POST', f"athlete/{request.json['user_id']}/daily_plan")

    return {'message': 'success'}, 201


@app.route('/previous', methods=['GET'])
@authentication_required
@xray_recorder.capture('routes.daily_readiness.previous')
def handle_daily_readiness_get():
    daily_readiness_store = DailyReadinessDatastore()
    user_id = jwt.decode(request.headers['Authorization'], verify=False)['user_id']
    current_time = datetime.datetime.now()
    start_time = current_time - datetime.timedelta(hours=48)
    sore_body_parts = []
    try:
        daily_readiness = daily_readiness_store.get(user_id, start_date=start_time, end_date=current_time)
        if len(daily_readiness) != 0:
            sore_body_parts = daily_readiness[0].json_serialise()['sore_body_parts']
    except NoSuchEntityException:
        pass

    post_session_store = PostSessionSurveyDatastore()
    post_session_surveys = post_session_store.get(user_id=user_id, start_date=start_time, end_date=current_time)
    post_session_surveys = [s for s in post_session_surveys if s is not None and s.event_date < format_datetime(current_time) and s.event_date > format_datetime(start_time)]
    if len(post_session_surveys) != 0:
        post_session_surveys = sorted(post_session_surveys, key=lambda k: k.survey.event_date, reverse=True)
        sore_body_parts += [{"body_part": s.body_part.location.value, "side": s.side} for s in post_session_surveys[0].survey.soreness if s.severity > 1]
    sore_body_parts = [dict(t) for t in {tuple(d.items()) for d in sore_body_parts}]
    return {'body_parts': sore_body_parts}, 200


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
