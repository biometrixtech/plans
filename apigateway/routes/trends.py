from flask import request, Blueprint
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from logic.survey_processing import cleanup_plan
from models.insights import InsightType
# from models.styles import VisualizationType
from routes.environments import is_fathom_environment
from utils import parse_datetime, format_date

datastore_collection = DatastoreCollection()

app = Blueprint('trends', __name__)


@app.route('/<uuid:user_id>/plan_alerts/clear', methods=['POST'])
@require.authenticated.self
@require.body({'event_date': str})
@xray_recorder.capture('routes.trends.plan_alerts.clear')
def handle_alerts_cleared(user_id):
    # user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_day = format_date(event_date)
    plan = DatastoreCollection().daily_plan_datastore.get(user_id, start_date=plan_event_day, end_date=plan_event_day)[0]
    # athlete_stats = DatastoreCollection().athlete_stats_datastore.get(user_id)
    # cleared_insight_type = InsightType(request.json['insight_type'])
    # cleared_trend_categories_plan = [category for category in plan.trends.trend_categories if category.insight_type == cleared_insight_type]
    # if len(cleared_trend_categories_plan) > 0:
    #     cleared_trend_category_plan = cleared_trend_categories_plan[0]
    #     cleared_trend_category_plan.plan_alerts = []
    #     for cat in plan.trends.dashboard.trend_categories:
    #         if cat.insight_type == cleared_insight_type:
    #             cat.unread_alerts = False
    #             break
    #     DatastoreCollection().daily_plan_datastore.put(plan)
    # cleared_trend_categories_stats = [category for category in athlete_stats.trend_categories if category.insight_type == cleared_insight_type]
    # if len(cleared_trend_categories_stats) > 0:
    #     cleared_trend_category_stats = cleared_trend_categories_stats[0]
    #     if len(cleared_trend_category_stats.plan_alerts) > 0:
    #         cleared_trend_category_stats.plan_alerts[0].cleared_date_time = event_date
    #         DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
    #     else:
    #         print(f"No Plan Alerts found for Trend Category {cleared_insight_type.name}")
    # else:
    #     print(f"Trend Category {cleared_insight_type.name} not found")

    visualizations = is_fathom_environment()
    plan = cleanup_plan(plan, visualizations=visualizations)
    return {'daily_plans': [plan]}, 200


@app.route('/<uuid:user_id>/first_time_experience/category', methods=['POST'])
@require.authenticated.self
@require.body({'event_date': str})
@xray_recorder.capture('routes.trends.first_time_experience.category')
def handle_fte_category(user_id):
    # user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_day = format_date(event_date)
    plan = DatastoreCollection().daily_plan_datastore.get(user_id, start_date=plan_event_day, end_date=plan_event_day)[0]
    athlete_stats = DatastoreCollection().athlete_stats_datastore.get(user_id)
    fte_insight_type = InsightType(request.json['insight_type'])
    fte_insight_categories = [category for category in plan.trends.insight_categories if category.insight_type == fte_insight_type]
    if len(fte_insight_categories) > 0:
        fte_insight_category = fte_insight_categories[0]
        fte_insight_category.first_time_experience = False
        athlete_stats.insight_categories = plan.trends.insight_categories
        DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
        DatastoreCollection().daily_plan_datastore.put(plan)
    else:
        print(f"Trend Category {fte_insight_type.name} not found")

    visualizations = is_fathom_environment()
    plan = cleanup_plan(plan, visualizations=visualizations)
    return {'daily_plans': [plan]}, 200


@app.route('/<uuid:user_id>/first_time_experience/view', methods=['POST'])
@require.authenticated.self
@require.body({'event_date': str})
@xray_recorder.capture('routes.trends.first_time_experience.view')
def handle_fte_view(user_id):
    # user_id = principal_id
    event_date = parse_datetime(request.json['event_date'])
    plan_event_day = format_date(event_date)
    plan = DatastoreCollection().daily_plan_datastore.get(user_id, start_date=plan_event_day, end_date=plan_event_day)[0]
    # athlete_stats = DatastoreCollection().athlete_stats_datastore.get(user_id)
    # fte_insight_type = InsightType(request.json['insight_type'])
    # fte_viz_type = VisualizationType(request.json['visualization_type'])
    # fte_trend_categories = [category for category in plan.trends.trend_categories if category.insight_type == fte_insight_type]
    # if len(fte_trend_categories) > 0:
    #     fte_trend_category = fte_trend_categories[0]
    #     fte_trend_category.first_time_experience = False
    #     fte_trend_category.first_time_experience_modal = None
    #     fte_views = [trend for trend in fte_trend_category.trends if trend.visualization_type == fte_viz_type]
    #     if len(fte_views) > 0:
    #         fte_view = fte_views[0]
    #         fte_view.first_time_experience = False
    #         athlete_stats.trend_categories = plan.trends.trend_categories
    #         DatastoreCollection().athlete_stats_datastore.put(athlete_stats)
    #         DatastoreCollection().daily_plan_datastore.put(plan)
    #     else:
    #         print(f"No View found for Visualization Type {fte_viz_type.name}")
    # else:
    #     print(f"Trend Category {fte_insight_type.name} not found")

    visualizations = is_fathom_environment()
    plan = cleanup_plan(plan, visualizations=visualizations)
    return {'daily_plans': [plan]}, 200
