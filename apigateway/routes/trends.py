from flask import request, Blueprint
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from models.insights import InsightType
from models.athlete_trend import VisualizationType
from utils import parse_datetime, format_date

datastore_collection = DatastoreCollection()

app = Blueprint('trends', __name__)


@app.route('plan_alerts/clear', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.trends.plan_alerts.clear')
def handle_alerts_cleared(principal_id):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_day = format_date(event_date)
    plan = DatastoreCollection().daily_plan_datastore.get(user_id, start_date=plan_event_day, end_date=plan_event_day)[0]
    athlete_stats = DatastoreCollection().athlete_stats_datastore.get(user_id)
    cleared_insight_type = InsightType(request.json['insight_type'])
    cleared_trend_categories = [category for category in plan.trends.trend_categories if category.insight_type == cleared_insight_type]
    if len(cleared_trend_categories) > 0:
        cleared_trend_category = cleared_trend_categories[0]
        if len(cleared_trend_category.plan_alerts) > 0:
            cleared_trend_category.plan_alerts[0].cleared_date_time = event_date
            athlete_stats.trend_categories = plan.trends.trend_categories
            DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
            DatastoreCollection().daily_plan_datastore.put(plan)
        else:
            print(f"No Plan Alerts found for Trend Category {cleared_insight_type.name}")
    else:
        print(f"Trend Category {cleared_insight_type.name} not found")

    return {'message': 'success'}, 200


@app.route('first_time_experience/category', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.trends.first_time_experience.category')
def handle_fte_category(principal_id):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_day = format_date(event_date)
    plan = DatastoreCollection().daily_plan_datastore.get(user_id, start_date=plan_event_day, end_date=plan_event_day)[0]
    athlete_stats = DatastoreCollection().athlete_stats_datastore.get(user_id)
    fte_insight_type = InsightType(request.json['insight_type'])
    trend_category = [category for category in plan.trends.trend_categories if category.insight_type == fte_insight_type][0]
    trend_category.first_time_experience = False
    athlete_stats.trend_categories = plan.trends.trend_categories
    DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
    DatastoreCollection().daily_plan_datastore.put(plan)

    return {'message': 'success'}, 200


@app.route('first_time_experience/view', methods=['POST'])
@require.authenticated.any
@require.body({'event_date': str})
@xray_recorder.capture('routes.trends.first_time_experience.view')
def handle_fte_view(principal_id):
    user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_day = format_date(event_date)
    plan = DatastoreCollection().daily_plan_datastore.get(user_id, start_date=plan_event_day, end_date=plan_event_day)[0]
    athlete_stats = DatastoreCollection().athlete_stats_datastore.get(user_id)
    fte_insight_type = InsightType(request.json['insight_type'])
    fte_viz_type = VisualizationType(request.json['visualization_type'])
    fte_trend_category = [category for category in plan.trends.trend_categories if category.insight_type == fte_insight_type][0]
    fte_view = [trend for trend in fte_trend_category.trends if trend.visualization_type == fte_viz_type]
    fte_view.first_time_experience = False
    athlete_stats.trend_categories = plan.trends.trend_categories
    DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
    DatastoreCollection().daily_plan_datastore.put(plan)

    return {'message': 'success'}, 200
