from flask import request, Blueprint

from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from models.soreness_base import BodyPartLocation
from models.user_stats import UserStats
from logic.api_processing import APIProcessing
from utils import parse_datetime, get_timezone

datastore_collection = DatastoreCollection()
user_stats_datastore = datastore_collection.user_stats_datastore
symptom_datastore = datastore_collection.symptom_datastore


app = Blueprint('report_symptoms', __name__)


@app.route('/<uuid:user_id>/', methods=['POST'])
@require.authenticated.any
@require.body({'event_date_time': str})
@xray_recorder.capture('routes.report_symptoms.post')
def handle_add_symptom(user_id):
    validate_data()
    event_date_time = parse_datetime(request.json['event_date_time'])
    timezone = get_timezone(event_date_time)

    # set up processing
    user_stats = user_stats_datastore.get(athlete_id=user_id)
    if user_stats is None:
        user_stats = UserStats(user_id)
        user_stats.event_date = event_date_time
    user_stats.api_version = Config.get('API_VERSION')
    user_stats.timezone = timezone
    api_processor = APIProcessing(
            user_id,
            event_date_time,
            user_stats=user_stats,
            datastore_collection=datastore_collection
    )

    # get symptoms
    if 'symptoms' in request.json:
        for symptom in request.json['symptoms']:
            if symptom is None:
                continue
            api_processor.create_symptom_from_survey(symptom)

    # store the symptoms
    if len(api_processor.symptoms) > 0:
        symptom_datastore.put(api_processor.symptoms)

    # update injury risk dict with the new information
    api_processor.update_stats_injury_risk()

    return {'message': 'success'}, 200


@xray_recorder.capture('routes.report_symptoms.validate')
def validate_data():
    if not isinstance(request.json['event_date_time'], str):
        raise InvalidSchemaException(f"Property event_date_time must be of type string")
    else:
        parse_datetime(request.json['event_date_time'])

    if 'symptoms' in request.json:
        if not isinstance(request.json['symptoms'], list):
            raise InvalidSchemaException(f"Property symptoms must be of type list")
        for symptom in request.json['symptoms']:
            try:
                BodyPartLocation(symptom['body_part'])
            except ValueError:
                raise InvalidSchemaException('body_part not recognized')
            symptom['body_part'] = int(symptom['body_part'])
    else:
        InvalidSchemaException(f"symptoms is a required field")
