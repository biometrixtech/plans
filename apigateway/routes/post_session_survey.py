from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint

from datastores.post_session_survey_datastore import PostSessionSurveyDatastore
from decorators import authentication_required
from exceptions import InvalidSchemaException


app = Blueprint('post_session_survey', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.post_session_survey.put')
def handle_post_session_survey_put():
    post_session_survey = PostSesssionSurvey()
    store = PostSessionSurveyDatastore()
    store.put(post_session_survey)
    return {'message': 'success'}, 201
