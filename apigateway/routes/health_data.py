from flask import request, Blueprint
# import os

from utils import format_date, parse_datetime
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.heart_rate_datastore import HeartRateDatastore
from datastores.sleep_history_datastore import SleepHistoryDatastore
from logic.survey_processing import SurveyProcessing
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
# from fathomapi.comms.service import Service

app = Blueprint('health_data', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.health_data.write')
def handle_previous_health_data_write():
    user_id = request.json['user_id']
    event_date = request.json['event_date']
    start_date = format_date(request.json['start_date'])
    end_date = format_date(request.json['end_date'])
    survey_processor = SurveyProcessing(user_id, parse_datetime(event_date))
    survey_processor.plans = DailyPlanDatastore().get(user_id=user_id, start_date=start_date, end_date=end_date)
    if 'sessions' in request.json and len(request.json['sessions']) > 0:
        survey_processor.process_historic_health_data(request.json['sessions'], event_date)
    else:
        survey_processor.plans = []
        survey_processor.heart_rate_data = []
    
    if "sleep_data" in request.json and len(request.json['sleep_data']) > 0:
        survey_processor.process_historic_sleep_data(request.json['sleep_data'])
    else:
        survey_processor.sleep_history = []

    if len(survey_processor.plans) > 0:
        DailyPlanDatastore().put(survey_processor.plans)
    if len(survey_processor.heart_rate_data) > 0:
        HeartRateDatastore().put(survey_processor.heart_rate_data)
    if len(survey_processor.sleep_history) > 0:
        SleepHistoryDatastore().put(survey_processor.sleep_history)

    # Service('users', os.environ['USERS_API_VERSION']).call_apigateway_async(method='PATCH',
    #                                                                         endpoint=f"user/{user_id}",
    #                                                                         body={"previous_health_sync_date": event_date})



    return {'message': "success"}, 200