from flask import request, Blueprint

from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from models.daily_readiness import DailyReadiness
from models.soreness_base import BodyPartLocation
from models.stats import AthleteStats
from models.daily_plan import DailyPlan
from logic.survey_processing import SurveyProcessing, create_plan
from config import get_mongo_collection
from utils import parse_datetime, format_date, format_datetime, fix_early_survey_event_date, get_timezone

datastore_collection = DatastoreCollection()
athlete_stats_datastore = datastore_collection.athlete_stats_datastore
daily_plan_datastore = datastore_collection.daily_plan_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore
session_datastore = datastore_collection.session_datastore
sleep_history_datastore = datastore_collection.sleep_history_datastore

app = Blueprint('movement_prep', __name__)


@app.route('/<uuid:user_id>/', methods=['POST'])
@require.authenticated.any
@require.body({'event_date_time': str})
@xray_recorder.capture('routes.movement_prep.create')
def handle_movement_prep_create(user_id):
    validate_data()
    event_date = parse_datetime(request.json['event_date_time'])
    event_date = fix_early_survey_event_date(event_date)

    timezone = get_timezone(event_date)
    # user_id = principal_id
    daily_readiness = DailyReadiness(
        user_id=user_id,
        event_date=format_datetime(event_date),
        soreness=request.json.get('soreness', []),
        sleep_quality=None,
        readiness=None,
        wants_functional_strength=False
    )

    train_later = True
    hist_update = False
    plan_event_date = format_date(event_date)
    athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
    if athlete_stats is None:
        athlete_stats = AthleteStats(user_id)
        athlete_stats.event_date = event_date
    if athlete_stats.api_version in [None, '4_4', '4_5']:
        hist_update = True
    athlete_stats.api_version = Config.get('API_VERSION')
    athlete_stats.timezone = timezone
    survey_processor = SurveyProcessing(user_id, event_date, athlete_stats, datastore_collection)
    survey_processor.user_age = request.json.get('user_age', 20)

    if 'sessions' in request.json and len(request.json['sessions']) > 0:

        for session in request.json['sessions']:
            if session is None:
                continue
            survey_processor.create_session_from_survey(session)

    # if need_new_plan:
    if _check_plan_exists(user_id, plan_event_date):
        plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]
        plan.user_id = user_id
        plan.training_sessions.extend(survey_processor.sessions)
    else:
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
        plan.training_sessions = survey_processor.sessions

    plan.train_later = train_later
    if len(survey_processor.heart_rate_data) > 0:
        heart_rate_datastore.put(survey_processor.heart_rate_data)

    plan.daily_readiness_survey = daily_readiness
    daily_plan_datastore.put(plan)

    survey_processor.soreness = daily_readiness.soreness
    #survey_processor.patch_daily_and_historic_soreness(survey='readiness')

    plan = create_plan(user_id,
                       event_date,
                       athlete_stats=survey_processor.athlete_stats,
                       stats_processor=survey_processor.stats_processor,
                       datastore_collection=datastore_collection,
                       visualizations=False,
                       hist_update=hist_update,
                       force_on_demand=True)

    return {'daily_plans': [plan]}, 201


@xray_recorder.capture('routes.movement_prep.validate')
def validate_data():
    parse_datetime(request.json['event_date_time'])

    if 'soreness' in request.json:
        if not isinstance(request.json['soreness'], list):
            raise InvalidSchemaException(f"Property soreness must be of type list")
        for soreness in request.json['soreness']:
            try:
                BodyPartLocation(soreness['body_part'])
            except ValueError:
                raise InvalidSchemaException('body_part not recognized')
            soreness['body_part'] = int(soreness['body_part'])


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False
