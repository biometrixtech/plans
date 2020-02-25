from flask import request, Blueprint
import copy

from datastores.datastore_collection import DatastoreCollection
from fathomapi.api.config import Config
from fathomapi.utils.decorators import require
# from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from models.session import Session
# from models.soreness_base import BodyPartLocation
from models.stats import AthleteStats
from models.daily_plan import DailyPlan
from logic.survey_processing import SurveyProcessing, create_plan, cleanup_plan
from utils import parse_datetime, format_date, fix_early_survey_event_date, get_timezone, _check_plan_exists

datastore_collection = DatastoreCollection()
athlete_stats_datastore = datastore_collection.athlete_stats_datastore
daily_plan_datastore = datastore_collection.daily_plan_datastore
heart_rate_datastore = datastore_collection.heart_rate_datastore

app = Blueprint('rom_wod', __name__)


@app.route('/<uuid:user_id>/', methods=['POST'])
@require.authenticated.any
@require.body({'event_date_time': str})
@xray_recorder.capture('routes.rom_wod.create')
def handle_rom_wod_create(user_id):
    validate_data()
    event_date = parse_datetime(request.json['event_date_time'])
    event_date = fix_early_survey_event_date(event_date)

    timezone = get_timezone(event_date)
    plan_update_required = False
    train_later = False
    hist_update = False
    # if 'sessions_planned' in request.json and request.json['sessions_planned']:
    #     train_later = True
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

    # check if plan exists, if not create a new one
    if not _check_plan_exists(user_id, plan_event_date):
        plan = DailyPlan(event_date=plan_event_date)
        plan.user_id = user_id
    else:
        plan = daily_plan_datastore.get(user_id, plan_event_date, plan_event_date)[0]

    for session in request.json['sessions']:
        create_new = True
        if session is None:
            continue
        # if id is already present, it's potentially a patch. Check if session already exists and overwrite if it does
        if session.get('session_id') or session.get('id') is not None:
            session_id = session.get('session_id') or session.get('id')
            for s in range(0, len(plan.training_sessions)):
                if plan.training_sessions[s].id == session_id:
                    create_new = False
                    if session.get('source', 0) == 3:
                        session['last_updated'] = event_date

                    new_session = Session.json_deserialise(session)
                    plan.training_sessions[s] = new_session
                    plan_update_required = True
                    if new_session.post_session_survey is not None:
                        survey_processor.soreness.extend(new_session.post_session_survey.soreness)
                    break
        if create_new:
            survey_processor.create_session_from_survey(session)

    # update daily pain and soreness in athlete_stats
    # survey_processor.patch_daily_and_historic_soreness(survey='post_session')

    # check if any of the non-ignored and non-deleted sessions are high load
    for session in survey_processor.sessions:
        if not session.deleted and not session.ignored:
            plan_update_required = True
            if not plan.sessions_planned:
                plan.sessions_planned = True
            break

    plan.training_sessions.extend(survey_processor.sessions)
    plan.train_later = train_later

    daily_plan_datastore.put(plan)

    # save heart_rate_data if it exists in any of the sessions
    if len(survey_processor.heart_rate_data) > 0:
        heart_rate_datastore.put(survey_processor.heart_rate_data)

    # update plan
    if plan_update_required:
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
    else:
        plan = cleanup_plan(plan, False)

    return {'daily_plans': [plan]}, 201


@xray_recorder.capture('routes.rom_wod.validate')
def validate_data():
    parse_datetime(request.json['event_date_time'])

    # if 'soreness' in request.json:
    #     if not isinstance(request.json['soreness'], list):
    #         raise InvalidSchemaException(f"Property soreness must be of type list")
    #     for soreness in request.json['soreness']:
    #         try:
    #             BodyPartLocation(soreness['body_part'])
    #         except ValueError:
    #             raise InvalidSchemaException('body_part not recognized')
    #         soreness['body_part'] = int(soreness['body_part'])
