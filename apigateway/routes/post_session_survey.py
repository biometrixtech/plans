from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint

from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException
from models.post_session_survey import PostSessionSurvey
from models.session import SessionType
from utils import format_datetime, run_async


app = Blueprint('post_session_survey', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.post_session_survey.put')
def handle_post_session_survey_create():
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = format_datetime(request.json['event_date'])
        if event_date is None:
            raise InvalidSchemaException('event_date is not formatted correctly')
    if 'session_type' not in request.json:
        raise InvalidSchemaException('Missing required parameter session_type')
    else:
        try:
            session_type = SessionType(request.json['session_type']).value
        except ValueError:
            raise InvalidSchemaException('session_type not recognized')

    session_id = request.json.get('session_id', '')
    if len(session_id) == 0:
        session_id = None

    survey = PostSessionSurvey(event_date_time=event_date,
    						   user_id=request.json['user_id'],
    						   session_id=session_id,
    						   session_type=session_type,
    						   survey=request.json['survey']
                               )
    store = PostSessionSurveyDatastore()
    store.put(survey)

    run_async('POST', f"athlete/{request.json['user_id']}/daily_plan")

    return {'message': 'success'}, 201
