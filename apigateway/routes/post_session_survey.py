from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint

from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException
from models.post_session_survey import PostSessionSurvey


app = Blueprint('post_session_survey', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.post_session_survey.put')
def handle_post_session_survey_create():
    session_id = request.json.get('session_id', None)
    survey = PostSessionSurvey(event_date=request.json['event_date'],
    						   user_id=request.json['user_id'],
    						   session_id=session_id,
    						   session_type=request.json['session_type'],
    						   survey=request.json['survey']
                               )
    store = PostSessionSurveyDatastore()
    store.put(survey)
    return {'message': 'success'}, 201
