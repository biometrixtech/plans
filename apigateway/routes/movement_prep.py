from flask import request, Blueprint

from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from models.functional_movement_activities import ActivityType
from models.session import SessionType
from models.soreness_base import BodyPartLocation
from models.user_stats import UserStats
from logic.api_processing import APIProcessing
from logic.activities_processing import ActivitiesProcessing
from utils import parse_datetime, get_timezone
from routes.environments import consolidated_dosage

consolidated = consolidated_dosage()

datastore_collection = DatastoreCollection()
user_stats_datastore = datastore_collection.user_stats_datastore
symptom_datastore = datastore_collection.symptom_datastore
# training_session_datastore = datastore_collection.training_session_datastore
workout_program_datastore = datastore_collection.workout_program_datastore
movement_prep_datastore = datastore_collection.movement_prep_datastore

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
    # process stored planned session
    if 'program_id' in request.json:
        program_id = request.json['program_id']
        if program_id is not None:
            api_processor.create_planned_workout_from_id(program_id)

    # process planned session
    elif 'session' in request.json:
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

    return {'movement_prep': movement_prep.json_serialise(api=True, consolidated=consolidated)}, 201


@app.route('/<uuid:user_id>/<uuid:movement_prep_id>/start_activity', methods=['POST'])
@require.authenticated.any
@require.body({'event_date_time': str})
@xray_recorder.capture('routes.movement_prep.start')
def handle_movement_prep_start(user_id, movement_prep_id):
    # validate_data()
    event_date_time = parse_datetime(request.json['event_date_time'])
    activity_type = request.json['activity_type']

    # read in movement prep and validate that it belongs the the correct user
    movement_prep = movement_prep_datastore.get(movement_prep_id=movement_prep_id)
    if movement_prep.user_id != user_id:
        return {'message': 'user_id and movement_prep_id do not match'}, 404

    # update movement prep and write to db
    activity_proc = ActivitiesProcessing(datastore_collection)
    activity_proc.mark_activity_started(movement_prep, event_date_time, activity_type)

    movement_prep_datastore.put(movement_prep)

    return {'message': 'success'}


@app.route('/<uuid:user_id>/<uuid:movement_prep_id>/complete_activity', methods=['POST'])
@require.authenticated.any
@require.body({'event_date_time': str})
@xray_recorder.capture('routes.movement_prep.complete')
def handle_movement_prep_complete(user_id, movement_prep_id):
    # validate_data()
    event_date_time = parse_datetime(request.json['event_date_time'])
    activity_type = request.json['activity_type']
    completed_exercises = request.json.get('completed_exercises', [])

    # read in movement prep and validate that it belongs the the correct user
    movement_prep = movement_prep_datastore.get(movement_prep_id=movement_prep_id)
    if movement_prep.user_id != user_id:
        return {'message': 'user_id and movement_prep_id do not match'}, 404

    # update movement prep and write to db
    activity_proc = ActivitiesProcessing(datastore_collection)
    try:
        activity_proc.mark_activity_completed(movement_prep, event_date_time, activity_type, user_id, completed_exercises)
    except AttributeError:
        raise InvalidSchemaException(f"{ActivityType(activity_type).name} does not exist for Movement Prep")
    except NoSuchEntityException:
        raise NoSuchEntityException(f"Provided Movement Prep does not contain a valid {ActivityType(activity_type).name}")

    movement_prep_datastore.put(movement_prep)

    return {'message': 'success'}


@app.route('/<uuid:user_id>/<uuid:movement_prep_id>', methods=['GET'])
@require.authenticated.any
@xray_recorder.capture('routes.movement_prep.get')
def handle_movement_prep_get(user_id, movement_prep_id):
    # get movement prep from db and validate that it belongs to the user
    movement_prep = movement_prep_datastore.get(movement_prep_id=movement_prep_id)
    if movement_prep.user_id != user_id:
        return {'message': 'user_id and movement_prep_id do not match'}, 404

    return {'movement_prep': movement_prep.json_serialise(api=True, consolidated=consolidated)}


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
