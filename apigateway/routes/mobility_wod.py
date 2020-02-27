from flask import request, Blueprint
import copy

from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from models.stats import AthleteStats
from models.daily_plan import DailyPlan
from models.soreness_base import BodyPartLocation
from logic.survey_processing import SurveyProcessing, create_plan
from utils import parse_datetime, format_date, fix_early_survey_event_date, get_timezone, _check_plan_exists

datastore_collection = DatastoreCollection()
athlete_stats_datastore = datastore_collection.athlete_stats_datastore
daily_plan_datastore = datastore_collection.daily_plan_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore

app = Blueprint('mobility_wod', __name__)


@app.route('/<uuid:user_id>/', methods=['POST'])
@require.authenticated.any
@require.body({'event_date_time': str})
@xray_recorder.capture('routes.mobility_wod.create')
def handle_rom_wod_create(user_id):
    validate_data()
    event_date = parse_datetime(request.json['event_date_time'])
    event_date = fix_early_survey_event_date(event_date)
    timezone = get_timezone(event_date)

    # find/create daily plan
    plan_event_date = format_date(event_date)
    if _check_plan_exists(user_id, plan_event_date):
        plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]
    else:
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
    plan.train_later = False

    # set up processing
    hist_update = False
    athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
    if athlete_stats is None:
        athlete_stats = AthleteStats(user_id)
        athlete_stats.event_date = event_date
    if athlete_stats.api_version in [None, '4_4', '4_5']:
        hist_update = True
    athlete_stats.api_version = Config.get('API_VERSION')
    athlete_stats.timezone = timezone
    survey_processor = SurveyProcessing(user_id, event_date,
                                        athlete_stats=athlete_stats,
                                        datastore_collection=datastore_collection)
    survey_processor.user_age = request.json.get('user_age', 20)

    # process new symptoms, if any sent
    if 'symptoms' in request.json:
        for symptom in request.json['symptoms']:
            if symptom is None:
                continue
            survey_processor.create_soreness_from_survey(symptom)
        plan.symptoms.extend(survey_processor.soreness)

    # process new session, if any sent
    if len(request.json.get('sessions', [])) > 0:
        sessions = request.json['sessions']
        for session in sessions:
            survey_processor.create_session_from_survey(session)
        plan.training_sessions.extend(survey_processor.sessions)

    # save the daily plan
    daily_plan_datastore.put(plan)

    # save heart_rate_data if it exists in any of the sessions
    if len(survey_processor.heart_rate_data) > 0:
        heart_rate_datastore.put(survey_processor.heart_rate_data)

    if survey_processor.stats_processor is not None and survey_processor.stats_processor.historic_data_loaded:
        plan_copy = copy.deepcopy(plan)
        if plan_event_date in [p.event_date for p in survey_processor.stats_processor.all_plans]:
            survey_processor.stats_processor.all_plans.remove([p for p in survey_processor.stats_processor.all_plans if p.event_date == plan_event_date][0])
        survey_processor.stats_processor.all_plans.append(plan_copy)
    plan = create_plan(user_id,
                       event_date,
                       athlete_stats=survey_processor.athlete_stats,
                       stats_processor=survey_processor.stats_processor,
                       datastore_collection=datastore_collection,
                       visualizations=False,
                       hist_update=hist_update,
                       force_on_demand=True)

    return {'daily_plans': [plan]}, 201


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
