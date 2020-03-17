from flask import request, Blueprint

from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from models.session import SessionType
from models.soreness_base import BodyPartLocation
from models.user_stats import UserStats
from logic.api_processing import APIProcessing
from utils import parse_datetime, get_timezone

datastore_collection = DatastoreCollection()
user_stats_datastore = datastore_collection.user_stats_datastore
symptom_datastore = datastore_collection.symptom_datastore
training_session_datastore = datastore_collection.training_session_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore
workout_program_datastore = datastore_collection.workout_program_datastore

app = Blueprint('mobility_wod', __name__)


@app.route('/<uuid:user_id>/', methods=['POST'])
@require.authenticated.self
@require.body({'event_date_time': str})
@xray_recorder.capture('routes.mobility_wod.create')
def handle_rom_wod_create(user_id):
    validate_data()
    event_date_time = parse_datetime(request.json['event_date_time'])
    # event_date = fix_early_survey_event_date(event_date)
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
    api_processor.user_age = request.json.get('user_age', 20)

    # process new symptoms, if any sent
    if 'symptoms' in request.json:
        for symptom in request.json['symptoms']:
            if symptom is None:
                continue
            api_processor.create_symptom_from_survey(symptom)

    # process new session, if any sent
    if len(request.json.get('sessions', [])) > 0:
        sessions = request.json['sessions']
        for session in sessions:
            api_processor.create_session_from_survey(session)

    # store the symptoms, session, workout_program and heart rate, if any exist
    if len(api_processor.symptoms) > 0:
        symptom_datastore.put(api_processor.symptoms)

    # Session will be saved during create_actiity
    # if len(api_processor.sessions) > 0:
    #     training_session_datastore.put(api_processor.sessions)

    if len(api_processor.workout_programs) > 0:
        workout_program_datastore.put(api_processor.workout_programs)

    if len(api_processor.heart_rate_data) > 0:
        heart_rate_datastore.put(api_processor.heart_rate_data)

    mobility_wod = api_processor.create_activity(
            activity_type='mobility_wod'
    )

    return {'mobility_wod': mobility_wod.json_serialise()}, 201


@xray_recorder.capture('routes.mobility_wod.validate')
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

    if 'sessions' in request.json:
        if not isinstance(request.json['sessions'], list):
            raise InvalidSchemaException(f"Property sessions must be of type list")
        request.json['sessions'] = [session for session in request.json['sessions'] if session is not None]
        for session in request.json['sessions']:
            try:
                parse_datetime(session['event_date'])
            except KeyError:
                raise InvalidSchemaException('event_date is required parameter for a session')
            except ValueError:
                raise InvalidSchemaException('event_date must be in ISO8601 format')
            try:
                SessionType(session['session_type'])
            except KeyError:
                raise InvalidSchemaException('session_type is required parameter for a session')
            except ValueError:
                raise InvalidSchemaException('invalid session_type')
