from flask import request, Blueprint
import os
import copy
from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from models.daily_plan import DailyPlan
from models.stats import AthleteStats
from routes.environments import is_fathom_environment
from utils import parse_datetime, format_date, get_timezone, _check_plan_exists
from logic.survey_processing import SurveyProcessing, create_plan

datastore_collection = DatastoreCollection()
athlete_stats_datastore = datastore_collection.athlete_stats_datastore
daily_plan_datastore = datastore_collection.daily_plan_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore
session_datastore = datastore_collection.session_datastore


app = Blueprint('symptoms', __name__)


@app.route('/<uuid:user_id>/', methods=['POST'])
@require.authenticated.any
# @require.body({'event_date': str})
@xray_recorder.capture('routes.symptoms.post')
def handle_add_symptoms(user_id=None):
    event_date_string = request.json.get('event_date') or request.json.get('event_date_time')
    event_date = parse_datetime(event_date_string)
    timezone = get_timezone(event_date)
    hist_update = False
    athlete_stats = athlete_stats_datastore.get(athlete_id=user_id)
    if athlete_stats is None:
        athlete_stats = AthleteStats(user_id)
        athlete_stats.event_date = event_date
    if athlete_stats.api_version in [None, '4_4', '4_5']:
        hist_update = True
    athlete_stats.api_version = Config.get('API_VERSION')
    athlete_stats.timezone = timezone

    plan_event_date = format_date(event_date)
    survey_processor = SurveyProcessing(user_id, event_date,
                                        athlete_stats=athlete_stats,
                                        datastore_collection=datastore_collection)
    survey_processor.user_age = request.json.get('user_age', 20)
    symptoms = request.json.get('soreness') or request.json.get('symptoms') or []
    for symptom in symptoms:
        if symptom is None:
            continue
        survey_processor.create_soreness_from_survey(symptom)

    visualizations = is_fathom_environment()

    # check if plan exists, if not create a new one and save it to database, also check if existing one needs updating flags
    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
    else:
        plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]

    plan.symptoms.extend(survey_processor.symptoms)

    daily_plan_datastore.put(plan)

    if is_fathom_environment():
        # update plan
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
                           visualizations=visualizations,
                           hist_update=hist_update)

        # update users database if health data received
        if is_fathom_environment():
            Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
                                                                                    endpoint=f"user/{user_id}",
                                                                                    body={"timezone": timezone,
                                                                                          "plans_api_version": Config.get('API_VERSION')})
        return {'daily_plans': [plan]}, 201
    else:
        return {'message': 'success'}, 201
