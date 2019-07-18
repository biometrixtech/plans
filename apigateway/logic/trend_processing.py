from models.athlete_trend import AthleteTrends, PlanAlert, Trend, TrendCategory, TrendData, VisualizationType, LegendColor, BoldText
from models.trigger import TriggerType, Trigger
from models.chart_data import OveractiveUnderactiveChartData, TightOverUnderactiveChartData
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
        tight_muscle_trend = self.get_tight_over_under_muscle_view()
        #over_under_muscle_trend = self.get_overactive_underactive_muscle_view()
        plan_alert = PlanAlert(InsightType.movement_dysfunction_compensation)
        plan_alert.title = "Movement Dysfunction or Compensation"
        if tight_muscle_trend is not None:
            trend_category.trends.append(tight_muscle_trend)
            plan_alert.views.append("1")
            plan_alert.text += "tight muscle over-under"
        # if over_under_muscle_trend is not None:
        #     trend_category.trends.append(over_under_muscle_trend)
        #     plan_alert.views.append("2")
        #     plan_alert.text += "overactive underactive muscle;"
        if len(trend_category.trends) > 0:
            trend_category.plan_alerts.append(plan_alert)
            self.athlete_trends.trend_categories.append(trend_category)

    def get_latest_trigger_date_time(self, triggers):

        if len(triggers) > 0:

            status_changed_date_time = None

            created_triggers = sorted(triggers, key=lambda x: x.created_date_time, reverse=True)
            modified_triggers = sorted(triggers, key=lambda x: x.modified_date_time, reverse=True)
            status_changed_triggers = [t for t in triggers if t.source_date_time is not None]
            if len(status_changed_triggers) > 0:
                status_triggers = sorted(triggers, key=lambda x: x.source_date_time, reverse=True)
                status_changed_date_time = status_triggers[0].source_date_time

            last_created_date_time = created_triggers[0].created_date_time
            last_modified_date_time = modified_triggers[0].modified_date_time

            if status_changed_date_time is not None:
                return status_changed_date_time
            elif last_modified_date_time is not None:
                return max(last_modified_date_time, last_created_date_time)
            else:
                return last_created_date_time

        else:
            return None

    def get_tight_over_under_muscle_view(self):

        trigger_type_1 = TriggerType.hist_sore_less_30
        triggers_1 = list(t for t in self.trigger_list if t.trigger_type == trigger_type_1)

        trigger_type_2 = TriggerType.hist_sore_greater_30
        triggers_2 = list(t for t in self.trigger_list if t.trigger_type == trigger_type_2)

        if len(triggers_1) > 0 or len(triggers_2) > 0:
            antagonists_1, synergists_1 = self.get_antagonists_syngergists(triggers_1)
            antagonists_2, synergists_2 = self.get_antagonists_syngergists(triggers_2)
            trend = Trend(trigger_type_1)
            trend.title = "Muscle Over & Under Activity"
            trend.title_color = LegendColor.warning_light
            trend.text.append("Your data suggests tight muscle stuff.")
            trend.text.append("Seriously. We're not kidding.")

            bold_text_1 = BoldText()
            bold_text_1.text = "Seriously"
            bold_text_1.color = LegendColor.error_light

            bold_text_2 = BoldText()
            bold_text_2.text = "tight muscle"
            bold_text_2.color = LegendColor.warning_light
            trend.bold_text.append(bold_text_1)
            trend.bold_text.append(bold_text_2)

            trend.icon = "view1icon.png"
            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.tight_overactice_underactive
            trend_data.add_visualization_data()
            tight_under_data = TightOverUnderactiveChartData()
            tight_under_data.overactive.extend([t.body_part for t in triggers_1])
            tight_under_data.overactive.extend([t.body_part for t in triggers_2])
            tight_under_data.underactive.extend([a for a in antagonists_2])
            tight_under_data.underactive_needing_care.extend([s for s in synergists_1])
            tight_under_data.underactive_needing_care.extend([s for s in synergists_2])
            tight_under_data.remove_duplicates()
            trend_data.data = [tight_under_data]
            trend_data.text = "This is a specific description of all your tight muscles..."

            bold_text_3 = BoldText()
            bold_text_3.text = "all your tight muscles"
            bold_text_3.color = LegendColor.error_light

            bold_text_4 = BoldText()
            bold_text_4.text = "specific"
            bold_text_4.color = LegendColor.warning_light
            trend_data.bold_text.append(bold_text_3)
            trend_data.bold_text.append(bold_text_4)

            trend_data.title = "Trigger Specific Title"
            trend_data.title_color = LegendColor.warning_light
            trend.trend_data = trend_data

            all_triggers = []
            all_triggers.extend(triggers_1)
            all_triggers.extend(triggers_2)

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)
            return trend
        else:
            return None

    # def get_overactive_underactive_muscle_view(self):
    #
    #     trigger_type = TriggerType.hist_sore_greater_30
    #     triggers = list(t for t in self.trigger_list if t.trigger_type == trigger_type)
    #     if len(triggers) > 0:
    #         antagonists, synergists = self.get_antagonists_syngergists(triggers)
    #         trend = Trend(trigger_type)
    #         trend.title = "Overactive & Underactive Muscle"
    #         trend.text = "Your data suggests several imbalances in muscle activation which can lead to performance inefficiencies...."
    #         trend_data = TrendData()
    #         trend_data.visualization_type = VisualizationType.overactive_underactive
    #         trend_data.add_visualization_data()
    #         over_under_data = OveractiveUnderactiveChartData()
    #         over_under_data.overactive_body_parts = [t.body_part for t in triggers]
    #         over_under_data.underactive_body_parts = [a for a in antagonists]
    #         trend_data.data = [over_under_data]
    #         trend_data.text = "This is a specific description of all your o/u body parts..."
    #         trend_data.title = "Trigger Specific Title"
    #         trend.trend_data = trend_data
    #         trend.last_date_time = self.get_latest_trigger_date_time(triggers)
    #         return trend
    #     else:
    #         return None





