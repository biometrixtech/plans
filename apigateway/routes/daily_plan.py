from flask import request, Blueprint
import datetime

from utils import format_date, format_datetime, parse_datetime
from datastores.daily_plan_datastore import DailyPlanDatastore
from logic.athlete_status_processing import AthleteStatusProcessing

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder

app = Blueprint('daily_plan', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.daily_plan.get')
def handle_daily_plan_get():
    validate_input(request)

    user_id = request.json['user_id']
    event_date = request.json.get('event_date', format_datetime(datetime.datetime.utcnow()))
    event_date = parse_datetime(event_date)

    start_date = request.json['start_date']
    if 'end_date' in request.json:
        end_date = request.json['end_date']
    else:
        start_date = format_date(event_date)
        end_date = start_date
    store = DailyPlanDatastore()
    items = store.get(user_id, start_date, end_date)
    daily_plans = []
    need_soreness_sessions = False
    for plan in items:
        survey_complete = plan.daily_readiness_survey_completed()
        if plan.event_date == format_date(event_date) and not survey_complete:
            need_soreness_sessions = True
        landing_screen, nav_bar_indicator = plan.define_landing_screen()
        plan = plan.json_serialise()
        plan['daily_readiness_survey_completed'] = survey_complete
        plan['landing_screen'] = landing_screen
        plan['nav_bar_indicator'] = nav_bar_indicator
        del plan['daily_readiness_survey'], plan['user_id']
        daily_plans.append(plan)
    if need_soreness_sessions:
        previous_soreness_processor = AthleteStatusProcessing(user_id, event_date)
        (
            sore_body_parts,
            hist_sore_status,
            clear_candidates,
            dormant_tipping_candidates,
            current_sport_name,
            current_position,
            functional_strength_eligible,
            completed_functional_strength_sessions
        ) = previous_soreness_processor.get_previous_soreness()
        readiness = {
                      'body_parts': sore_body_parts,
                      'dormant_tipping_candidates': dormant_tipping_candidates,
                      'hist_sore_status': hist_sore_status,
                      'clear_candidates': clear_candidates,
                      'current_position': current_position,
                      'current_sport_name': current_sport_name,
                      'functional_strength_eligible': functional_strength_eligible,
                      'completed_functional_strength_sessions': completed_functional_strength_sessions
                     }

        typical_sessions = previous_soreness_processor.get_typical_sessions()
    else:
        readiness = {}
        typical_sessions = []

    return {'daily_plans': daily_plans,
            'readiness': readiness,
            'typical_sessions': typical_sessions}, 200


def validate_input(request):
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'user_id' not in request.json:
        raise InvalidSchemaException('Missing required parameter user_id')
    if 'start_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter start_date')
    else:
        try:
            datetime.datetime.strptime(request.json['start_date'], "%Y-%m-%d")
        except:
            raise InvalidSchemaException('start_date needs to be in format yyyy-mm-dd')
    if 'end_date' in request.json:
        try:
            datetime.datetime.strptime(request.json['end_date'], "%Y-%m-%d")
        except:
            raise InvalidSchemaException('end_date needs to be in format yyyy-mm-dd')
