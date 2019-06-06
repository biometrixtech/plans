from flask import request, Blueprint
import datetime

from utils import format_date, format_datetime, parse_datetime
from datastores.datastore_collection import DatastoreCollection
from logic.athlete_status_processing import AthleteStatusProcessing
from logic.survey_processing import create_plan, cleanup_plan

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder

datastore_collection = DatastoreCollection()
daily_plan_datastore = datastore_collection.daily_plan_datastore

app = Blueprint('daily_plan', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@require.body({'start_date': str})
@xray_recorder.capture('routes.daily_plan.get')
def handle_daily_plan_get(principal_id=None):
    validate_input()
    user_id = principal_id
    event_date = request.json.get('event_date', format_datetime(datetime.datetime.utcnow()))
    event_date = parse_datetime(event_date)

    start_date = request.json['start_date']
    if 'end_date' in request.json:
        end_date = request.json['end_date']
    else:
        start_date = format_date(event_date)
        end_date = start_date
    items = daily_plan_datastore.get(user_id, start_date, end_date)
    daily_plans = []
    need_soreness_sessions = False
    for plan in items:
        survey_complete = plan.daily_readiness_survey_completed()
        if plan.event_date == format_date(event_date) and not survey_complete:
            need_soreness_sessions = True
        if plan.event_date == format_date(event_date) and plan.trends is None:
            plan = create_plan(user_id, event_date, update_stats=True)
        else:
            plan = cleanup_plan(plan)
        daily_plans.append(plan)
    if need_soreness_sessions:
        previous_soreness_processor = AthleteStatusProcessing(user_id, event_date, datastore_collection=datastore_collection)
        (
            sore_body_parts,
            hist_sore_status,
            clear_candidates,
            dormant_tipping_candidates,
            current_sport_name,
            current_position,
            # functional_strength_eligible,
            # completed_functional_strength_sessions
        ) = previous_soreness_processor.get_previous_soreness()
        readiness = {
                      'body_parts': sore_body_parts,
                      'dormant_tipping_candidates': dormant_tipping_candidates,
                      'hist_sore_status': hist_sore_status,
                      'clear_candidates': clear_candidates,
                      'current_position': current_position,
                      'current_sport_name': current_sport_name,
                      # 'functional_strength_eligible': functional_strength_eligible,
                      # 'completed_functional_strength_sessions': completed_functional_strength_sessions
                     }

        typical_sessions = previous_soreness_processor.get_typical_sessions()
    else:
        readiness = {}
        typical_sessions = []

    return {'daily_plans': daily_plans,
            'readiness': readiness,
            'typical_sessions': typical_sessions}, 200


def validate_input():
    try:
        format_date(request.json['start_date'])
        format_date(request.json.get('end_date', None))
        format_datetime(request.json.get('event_date', None))
    except Exception:
        raise InvalidSchemaException('Incorrectly formatted date')
