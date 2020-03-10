from flask import request, Blueprint

from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from models.session import SessionType
from models.user_stats import UserStats
from logic.api_processing import APIProcessing
from utils import parse_datetime, get_timezone

datastore_collection = DatastoreCollection()
user_stats_datastore = datastore_collection.user_stats_datastore
training_session_datastore = datastore_collection.training_session_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore
workout_program_datastore = datastore_collection.workout_program_datastore

app = Blueprint('training_session', __name__)


@app.route('/<uuid:user_id>/<uuid:session_id>', methods=['PATCH'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.training_session.update')
def handle_session_update(session_id, user_id):
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
    api_processor.user_age = request.json.get('user_age', 20)

    session = request.json['session']
    existing_session = training_session_datastore.get(session_id=session_id)

    api_processor.create_session_from_survey(session)
    new_session = api_processor.sessions[0]

    existing_session.event_date = new_session.event_date
    existing_session.end_date = new_session.end_date
    existing_session.calories = new_session.calories if new_session.calories is not None else existing_session.calories
    existing_session.distance = new_session.distance if new_session.distance is not None else existing_session.distance
    existing_session.sport_name = new_session.sport_name if new_session.sport_name is not None else existing_session.sport_name
    existing_session.description = new_session.description if new_session.description != '' else existing_session.description
    existing_session.duration_minutes = new_session.duration_minutes if new_session.duration_minutes is not None else existing_session.duration_minutes
    existing_session.session_RPE = new_session.session_RPE if new_session.session_RPE != existing_session.session_RPE else existing_session.session_RPE
    existing_session.workout_program_module = new_session.workout_program_module if new_session.workout_program_module is not None else existing_session.workout_program_module

    # store the workout_program and heart rate, if any exist
    if len(api_processor.workout_programs) > 0:
        workout_program_datastore.put(api_processor.workout_programs)

    if len(api_processor.heart_rate_data) > 0:
        heart_rate_datastore.put(api_processor.heart_rate_data)

    api_processor.update_stats_injury_risk()

    return {'message': 'success'}, 200


@xray_recorder.capture('routes.responsive_recovery.validate')
def validate_data():
    if not isinstance(request.json['event_date_time'], str):
        raise InvalidSchemaException(f"Property event_date_time must be of type string")
    else:
        parse_datetime(request.json['event_date_time'])

    if 'session' not in request.json:
        raise InvalidSchemaException('session is required parameter to receive Responsive Recovery')
    else:
        session = request.json['session']
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
