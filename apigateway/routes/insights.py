from flask import request, Blueprint
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from models.soreness import TriggerType
from utils import parse_datetime, format_date

datastore_collection = DatastoreCollection()
daily_plan_datastore = datastore_collection.daily_plan_datastore
completed_exercise_datastore = datastore_collection.completed_exercise_datastore

app = Blueprint('insights', __name__)


@app.route('/read', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.active_recovery.exercise_modalities.complete')
def handle_insights_read(principal_id):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_day = format_date(event_date)
    plan = DatastoreCollection().daily_plan_datastore.get(user_id, start_date=plan_event_day, end_date=plan_event_day)[0]
    athlete_stats = DatastoreCollection().athlete_stats_datastore.get(user_id)
    exposed_triggers = set(athlete_stats.exposed_triggers)
    insights = request.json['insights']
    for read_insight in insights:
        read_trigger_type = TriggerType(read_insight['trigger_type'])
        for existing_insight in plan.insights:
            if read_trigger_type == existing_insight.trigger_type:
                existing_insight.read = True
                exposed_triggers.add(read_trigger_type)
                continue
    if len(athlete_stats.exposed_triggers) != len(exposed_triggers):
        athlete_stats.exposed_triggers = list(exposed_triggers)
        DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
    DatastoreCollection().daily_plan_datastore.put(plan)

    return {'message': 'success'}, 200
