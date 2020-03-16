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
# training_session_datastore = datastore_collection.training_session_datastore
workout_program_datastore = datastore_collection.workout_program_datastore

app = Blueprint('movement_prep', __name__)


@app.route('/<uuid:user_id>/', methods=['POST'])
@require.authenticated.any
@require.body({'event_date_time': str})
@xray_recorder.capture('routes.movement_prep.create')
def handle_movement_prep_create(user_id):
    validate_data()
    event_date_time = parse_datetime(request.json['event_date_time'])
    # event_date_time = fix_early_survey_event_date(event_date_time)
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

    # process planned session
    if 'session' in request.json:
        session = request.json['session']
        if session is not None:
            api_processor.create_session_from_survey(session)

    # get symptoms
    if 'symptoms' in request.json:
        for symptom in request.json['symptoms']:
            if symptom is None:
                continue
            api_processor.create_symptom_from_survey(symptom)

    # store the symptoms, session and workout_program, if any exist
    if len(api_processor.symptoms) > 0:
        symptom_datastore.put(api_processor.symptoms)

    # Session will be saved during create_actiity
    # if len(api_processor.sessions) > 0:
    #     training_session_datastore.put(api_processor.sessions)

    if len(api_processor.workout_programs) > 0:
        workout_program_datastore.put(api_processor.workout_programs)

    # create movement_prep
    movement_prep = api_processor.create_activity(
            activity_type='movement_prep'
    )

    return {'movement_prep': movement_prep.json_serialise()}, 201


@xray_recorder.capture('routes.movement_prep.validate')
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

    if 'session' not in request.json:
        raise InvalidSchemaException('session is required parameter to receive Movement Prep')
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
        if 'hr_data' in session:
            print("There should be no hr_data for planned session")
            del session['hr_data']
