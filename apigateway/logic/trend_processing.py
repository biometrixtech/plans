from models.athlete_trend import AthleteTrends, PlanAlert, Trend, TrendCategory, TrendData, VisualizationType
from models.trigger import TriggerType, Trigger
from models.chart_data import OveractiveUnderactiveChartData, TightUnderactiveChartData
from models.insights import InsightType



class TrendProcessor(object):
    def __init__(self, trigger_list):
        self.athlete_trends = None
        self.trigger_list = trigger_list

    def get_antagonists_syngergists(self, triggers):

        antagonists = []
        synergists = []
        for t in triggers:
            antagonists.extend(t.antagonists)
            synergists.extend(t.synergists)

        return antagonists, synergists

    def process_triggers(self):

        self.athlete_trends = AthleteTrends()

        trend_category = TrendCategory(InsightType.movement_dysfunction_compensation)
        trend_category.title = "Movement Dysfunction or Compensation"
        tight_muscle_trend = self.get_tight_muscle_view()
        over_under_muscle_trend = self.get_overactive_underactive_muscle_view()
        plan_alert = PlanAlert()
        plan_alert.category = "Movement Dysfunction or Compensation"
        if tight_muscle_trend is not None:
            trend_category.trends.append(tight_muscle_trend)
            plan_alert.views.append("1")
            plan_alert.text += "tight muscle;"
        if over_under_muscle_trend is not None:
            trend_category.trends.append(over_under_muscle_trend)
            plan_alert.views.append("2")
            plan_alert.text += "overactive underactive muscle;"
        if len(trend_category.trends) > 0:
            trend_category.plan_alerts.append(plan_alert)
            self.athlete_trends.trend_categories.append(trend_category)

    def get_latest_trigger_date_time(self, triggers):

        if len(triggers) > 0:

            created_triggers = sorted(triggers, key=lambda x: x.created_date_time, reverse=True)
            modified_triggers = sorted(triggers, key=lambda x: x.modified_date_time, reverse=True)

            last_created_date_time = created_triggers[0].created_date_time
            last_modified_date_time = modified_triggers[0].modified_date_time

            if last_modified_date_time is not None:
                return max(last_modified_date_time, last_created_date_time)
            else:
                return last_created_date_time

        else:
            return None

    def get_tight_muscle_view(self):

        trigger_type = TriggerType.hist_sore_less_30
        triggers = list(t for t in self.trigger_list if t.trigger_type == trigger_type)
        if len(triggers) > 0:
            antagonists, synergists = self.get_antagonists_syngergists(triggers)
            trend = Trend(trigger_type)
            trend.title = "Tight Muscle"
            trend.text = "Your data suggests tight muscle stuff"
            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.tight_muscle
            trend_data.add_visualization_data()
            tight_under_data = TightUnderactiveChartData()
            tight_under_data.tight_body_parts = [t.body_part.body_part_location.value for t in triggers]
            tight_under_data.underactive_body_parts = [s for s in synergists]
            trend_data.data = tight_under_data
            trend_data.text = "This is a specific description of all your tight muscles..."
            trend.data = trend_data
            trend.last_date_time = self.get_latest_trigger_date_time(triggers)
            return trend
        else:
            return None

    def get_overactive_underactive_muscle_view(self):

        trigger_type = TriggerType.hist_sore_greater_30
        triggers = list(t for t in self.trigger_list if t.trigger_type == trigger_type)
        if len(triggers) > 0:
            antagonists, synergists = self.get_antagonists_syngergists(triggers)
            trend = Trend(trigger_type)
            trend.title = "Overactive & Underactive Muscle"
            trend.text = "Your data suggests several imbalances in muscle activation which can lead to performance inefficiencies...."
            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.overactive_underactive
            trend_data.add_visualization_data()
            over_under_data = OveractiveUnderactiveChartData()
            over_under_data.overactive_body_parts = [t.body_part.body_part_location.value for t in triggers]
            over_under_data.underactive_body_parts = [a for a in antagonists]
            trend_data.data = over_under_data
            trend_data.text = "This is a specific description of all your o/u body parts..."
            trend.data = trend_data
            trend.last_date_time = self.get_latest_trigger_date_time(triggers)
            return trend
        else:
            return None





