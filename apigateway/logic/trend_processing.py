from models.athlete_trend import TrendDashboardCategory, PlanAlert, Trend, TrendCategory, TrendData, VisualizationType, LegendColor, BoldText
from models.trigger import TriggerType, Trigger
from models.chart_data import PainFunctionalLimitationChartData, TightOverUnderactiveChartData
from models.insights import InsightType
from models.body_parts import BodyPartFactory
from models.soreness_base import BodyPartSide
from logic.goal_focus_text_generator import RecoveryTextGenerator


class TrendProcessor(object):
    def __init__(self, trigger_list, athlete_trend_categories=None, dashboard_categories=None):
        self.athlete_trend_categories = [] if athlete_trend_categories is None else athlete_trend_categories
        self.trigger_list = trigger_list
        self.dashboard_categories = [] if dashboard_categories is None else dashboard_categories

        self.initialize_trend_categories()

    def get_antagonists_syngergists(self, triggers):

        antagonists = []
        synergists = []

        body_part_factory = BodyPartFactory()

        for t in triggers:
            if body_part_factory.is_joint(t.body_part):
                antagonists.extend(t.agonists)
            antagonists.extend(t.antagonists)
            synergists.extend(t.synergists)

        return antagonists, synergists

    def initialize_trend_categories(self):

        if len(self.athlete_trend_categories) == 0:

            trend_category = self.create_movement_dysfunction_category()

            self.athlete_trend_categories.append(trend_category)

    def get_limitation_trend(self, category_index):

        limitation_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                                 x.title == "Functional Limitation"), -1)
        if limitation_index == -1:
            limitation_trend = self.create_limitation_trend()
            self.athlete_trend_categories[category_index].trends.append(limitation_trend)
            limitation_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[limitation_index]

    def set_limitation_trend(self, category_index, limitation_trend):

        index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.title == "Functional Limitation"), -1)

        if index == -1:
            self.athlete_trend_categories[category_index].trends.append(limitation_trend)
        else:
            self.athlete_trend_categories[category_index].trends[index] = limitation_trend

    def get_muscle_trend(self, category_index):

        muscle_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.title == "Muscle Over & Under Activity"), -1)
        if muscle_index == -1:
            muscle_trend = self.create_muscle_trend()
            self.athlete_trend_categories[category_index].trends.append(muscle_trend)
            muscle_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[muscle_index]

    def set_muscle_trend(self, category_index, muscle_trend):

        muscle_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.title == "Muscle Over & Under Activity"), -1)

        if muscle_index == -1:
            self.athlete_trend_categories[category_index].trends.append(muscle_trend)
        else:
            self.athlete_trend_categories[category_index].trends[muscle_index] = muscle_trend

    def get_category_index(self, insight_type):

        category_index = next((i for i, x in enumerate(self.athlete_trend_categories) if
                               x.insight_type == insight_type), -1)
        if category_index == -1:
            trend_category = self.create_movement_dysfunction_category()
            self.athlete_trend_categories.append(trend_category)
            category_index = len(self.athlete_trend_categories) - 1
        return category_index

    def create_movement_dysfunction_category(self):
        trend_category = TrendCategory(InsightType.movement_dysfunction_compensation)
        trend_category.title = "Movement Dysfunction or Compensation"
        trend_category.first_time_experience = True

        muscle_trend = self.create_muscle_trend()
        trend_category.trends.append(muscle_trend)

        limitation_trend = self.create_limitation_trend()
        trend_category.trends.append(limitation_trend)

        return trend_category

    def create_limitation_trend(self):
        limitation_trend = Trend(TriggerType.hist_sore_greater_30)
        limitation_trend.title = "Functional Limitation"
        limitation_trend.title_color = LegendColor.error_light
        limitation_trend.text.append("Your data suggests pain or functional limitations.")
        limitation_trend.text.append("Really. We're not kidding.")

        bold_text_1 = BoldText()
        bold_text_1.text = "Really"
        bold_text_1.color = LegendColor.error_light

        bold_text_2 = BoldText()
        bold_text_2.text = "pain"
        bold_text_2.color = LegendColor.warning_light

        bold_text_3 = BoldText()
        bold_text_3.text = "functional limitations"
        bold_text_3.color = LegendColor.warning_light

        limitation_trend.bold_text.append(bold_text_1)
        limitation_trend.bold_text.append(bold_text_2)
        limitation_trend.bold_text.append(bold_text_3)

        limitation_trend.icon = "view3icon.png"
        limitation_trend.visible = False
        limitation_trend.first_time_experience = True
        limitation_trend.plan_alert_short_title = "functional limitation"
        return limitation_trend

    def create_muscle_trend(self):
        muscle_trend = Trend(TriggerType.hist_pain)
        muscle_trend.title = "Muscle Over & Under Activity"
        muscle_trend.title_color = LegendColor.warning_light
        muscle_trend.text.append("Your data suggests tight muscle stuff.")
        muscle_trend.text.append("Seriously. We're not kidding.")

        bold_text_1 = BoldText()
        bold_text_1.text = "Seriously"
        bold_text_1.color = LegendColor.error_light

        bold_text_2 = BoldText()
        bold_text_2.text = "tight muscle"
        bold_text_2.color = LegendColor.warning_light
        muscle_trend.bold_text.append(bold_text_1)
        muscle_trend.bold_text.append(bold_text_2)

        muscle_trend.icon = "view1icon.png"
        muscle_trend.visible = False
        muscle_trend.first_time_experience = True
        muscle_trend.plan_alert_short_title = "muscle over-activity"
        return muscle_trend

    def process_triggers(self):

        trend_category_index = self.get_category_index(InsightType.movement_dysfunction_compensation)
        self.set_tight_over_under_muscle_view(trend_category_index)
        self.set_pain_functional_limitation(trend_category_index)

        if len(self.athlete_trend_categories[trend_category_index].trends) > 0:
            first_times = list(t for t in self.athlete_trend_categories[trend_category_index].trends if t.last_date_time is not None and t.first_time_experience)
            none_dates = list(t for t in self.athlete_trend_categories[trend_category_index].trends if t.last_date_time is None)
            full_dates = list(t for t in self.athlete_trend_categories[trend_category_index].trends if t.last_date_time is not None and not t.first_time_experience)

            self.athlete_trend_categories[trend_category_index].trends = []

            new_modified_trigger_count = 0
            plan_alert_short_title = ""

            if len(first_times) > 0:
                first_times = sorted(first_times, key=lambda x: (x.last_date_time, x.priority), reverse=True)
                plan_alert_short_title = first_times[0].plan_alert_short_title
                for f in first_times:
                    new_modified_trigger_count += len(f.triggers)

            if len(full_dates) > 0:
                full_dates = sorted(full_dates, key=lambda x: (x.last_date_time, x.priority), reverse=True)
                if len(plan_alert_short_title) == 0:
                    plan_alert_short_title = full_dates[0].plan_alert_short_title
                for f in full_dates:
                    new_modified_trigger_count += len(f.triggers)

            self.athlete_trend_categories[trend_category_index].trends.extend(first_times)
            self.athlete_trend_categories[trend_category_index].trends.extend(full_dates)
            self.athlete_trend_categories[trend_category_index].trends.extend(none_dates)

            visible_trends = list(t for t in self.athlete_trend_categories[trend_category_index].trends if t.visible)

            trends_visible = False

            if len(visible_trends) > 0:
                trends_visible = True

                # plans alert text
                plan_alert = self.get_plan_alert(new_modified_trigger_count, plan_alert_short_title,
                                                 trend_category_index, visible_trends)
                self.athlete_trend_categories[trend_category_index].plan_alerts.append(plan_alert)

            self.athlete_trend_categories[trend_category_index].visible = trends_visible

    def get_plan_alert(self, new_modified_trigger_count, plan_alert_short_title, trend_category_index, visible_trends):

        header_text = str(new_modified_trigger_count) + " Tissue Related Insights"
        body_text = "New signs of " + plan_alert_short_title
        if len(visible_trends) > 1:
            if len(visible_trends) == 2:
                body_text += " and " + str(len(visible_trends) - 1) + " other meaningful insight"
            else:
                body_text += " and " + str(len(visible_trends) - 1) + " other meaningful insights"
        body_text += " in your data. Tap to view more."
        plan_alert = PlanAlert(self.athlete_trend_categories[trend_category_index].insight_type)
        plan_alert.title = header_text
        plan_alert.text = body_text
        bold_text_1 = BoldText()
        bold_text_1.text = plan_alert_short_title
        plan_alert.bold_text.append(bold_text_1)
        return plan_alert

    def get_latest_trigger_date_time(self, triggers):

        if len(triggers) > 0:

            status_changed_date_time = None

            # turns out we are only interested when a new body part is added or when a historic soreness status changes
            #created_triggers = sorted(triggers, key=lambda x: x.created_date_time, reverse=True)
            #modified_triggers = sorted(triggers, key=lambda x: x.modified_date_time, reverse=True)
            status_changed_triggers = [t for t in triggers if t.source_date_time is not None]
            if len(status_changed_triggers) > 0:
                status_triggers = sorted(triggers, key=lambda x: x.source_date_time, reverse=True)
                status_changed_date_time = status_triggers[0].source_date_time

            #last_created_date_time = created_triggers[0].created_date_time
            #last_modified_date_time = modified_triggers[0].modified_date_time

            if status_changed_date_time is not None:
                return status_changed_date_time
            #elif last_modified_date_time is not None:
            #    return max(last_modified_date_time, last_created_date_time)
            #else:
            #    return last_created_date_time

        else:
            return None

    def set_tight_over_under_muscle_view(self, category_index):

        trigger_type_1 = TriggerType.hist_sore_less_30
        triggers_1 = list(t for t in self.trigger_list if t.trigger_type == trigger_type_1)

        trigger_type_2 = TriggerType.hist_sore_greater_30
        triggers_2 = list(t for t in self.trigger_list if t.trigger_type == trigger_type_2)

        if len(triggers_1) > 0 or len(triggers_2) > 0:

            antagonists_1, synergists_1 = self.get_antagonists_syngergists(triggers_1)
            antagonists_2, synergists_2 = self.get_antagonists_syngergists(triggers_2)

            trend = self.get_muscle_trend(category_index)

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

            all_triggers = []
            all_triggers.extend(triggers_1)
            all_triggers.extend(triggers_2)

            # rank triggers
            sorted_triggers = sorted(all_triggers, key=lambda x: (x.source_date_time, x.trigger_type), reverse=True)

            text_generator = RecoveryTextGenerator()
            body_part_factory = BodyPartFactory()

            top_candidates = list(s for s in sorted_triggers if s.source_date_time == sorted_triggers[0].source_date_time)

            trigger_header_text, is_plural = self.get_body_part_title_text(body_part_factory, top_candidates)

            if is_plural:
                trend_data.title = "Your " + trigger_header_text + " are overactive"
            else:
                trend_data.title = "Your " + trigger_header_text + " is overactive"

            trend_data.title = trend_data.title.title()
            trend_data.title_color = LegendColor.warning_light

            body_part_text = text_generator.get_body_part_text(top_candidates[0].body_part.body_part_location, None)
            body_part_text.title()

            trend_data.text = body_part_text + " overactivity is often caused by chronic over-compensations for weak or under-active muscles elsewhere.\n"

            bold_text_3 = BoldText()
            bold_text_3.text = body_part_text
            bold_text_3.color = LegendColor.error_light
            trend_data.bold_text.append(bold_text_3)

            # bold_text_4 = BoldText()
            # bold_text_4.text = "specific"
            # bold_text_4.color = LegendColor.warning_light

            # trend_data.bold_text.append(bold_text_4)

            trend.trend_data = trend_data

            trend.visible = True
            trend.priority = 0

            trend.triggers = all_triggers

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)

            # Now create dashboard category card
            trend_dashboard_category = TrendDashboardCategory(self.athlete_trend_categories[category_index].insight_type)
            trend_dashboard_category.title = "Tissue Related Insights"
            trend_dashboard_category.text = "weakness identified in"

            if top_candidates[0].trigger_type == TriggerType.hist_sore_greater_30:
                trigger_dictionary = {}
                for t in top_candidates[0].antagonists:
                    body_part = body_part_factory.get_body_part(t)
                    trigger_dictionary[t] = body_part.treatment_priority

                sorted_trigger_items = sorted(trigger_dictionary.items(), key=lambda x: x[1])
                trend_dashboard_category.body_part = BodyPartSide(sorted_trigger_items[0][0].body_part_location,
                                                                                            sorted_trigger_items[0][0].side)
                trend_dashboard_category.body_part_text = text_generator.get_body_part_text(sorted_trigger_items[0][0].body_part_location,
                                                                                            sorted_trigger_items[0][0].side)
            else:
                trigger_dictionary = {}
                for t in top_candidates[0].synergists:
                    body_part = body_part_factory.get_body_part(t)
                    trigger_dictionary[t] = body_part.treatment_priority

                sorted_trigger_items = sorted(trigger_dictionary.items(), key=lambda x: x[1])
                trend_dashboard_category.body_part = BodyPartSide(sorted_trigger_items[0][0].body_part_location,
                                                                  sorted_trigger_items[0][0].side)
                trend_dashboard_category.body_part_text = text_generator.get_body_part_text(sorted_trigger_items[0][0].body_part_location,
                                                                                            sorted_trigger_items[0][0].side)

            if len(all_triggers) > 1:
                trend_dashboard_category.footer = "and " + str(len(all_triggers) - 1) + " more..."

            self.dashboard_categories.append(trend_dashboard_category)

        else:
            trend = self.create_muscle_trend()
            self.set_muscle_trend(category_index, trend)

    def get_body_part_title_text(self, body_part_factory, top_candidates):

        text_generator = RecoveryTextGenerator()
        is_plural = False

        if len(top_candidates) == 1:
            trigger_header_text = text_generator.get_body_part_text(top_candidates[0].body_part.body_part_location,
                                                                    top_candidates[0].body_part.side)
        else:
            trigger_dictionary = {}
            for t in top_candidates:
                body_part = body_part_factory.get_body_part(t.body_part)
                trigger_dictionary[t] = body_part.treatment_priority

            # still could have a tie (two body parts)
            sorted_trigger_items = sorted(trigger_dictionary.items(), key=lambda x: x[1])
            if len(sorted_trigger_items) > 1:
                if sorted_trigger_items[0][1] == sorted_trigger_items[1][1]:
                    trigger_header_text = text_generator.get_body_part_text_plural(
                        top_candidates[0].body_part.body_part_location, None)
                    is_plural = True
                else:
                    trigger_header_text = text_generator.get_body_part_text(
                        top_candidates[0].body_part.body_part_location, top_candidates[0].body_part.side)
            else:
                trigger_header_text = text_generator.get_body_part_text(top_candidates[0].body_part.body_part_location,
                                                                        top_candidates[0].body_part.side)
        return trigger_header_text, is_plural

    def set_pain_functional_limitation(self, category_index):

        trigger_type = TriggerType.hist_pain
        triggers = list(t for t in self.trigger_list if t.trigger_type == trigger_type)

        if len(triggers) > 0:
            antagonists, synergists = self.get_antagonists_syngergists(triggers)

            trend = self.get_limitation_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.pain_functional_limitation
            trend_data.add_visualization_data()
            pain_functional_data = PainFunctionalLimitationChartData()
            pain_functional_data.overactive.extend([t.body_part for t in triggers])
            pain_functional_data.underactive.extend([a for a in antagonists])
            pain_functional_data.underactive_needing_care.extend([s for s in synergists])
            pain_functional_data.remove_duplicates()
            trend_data.data = [pain_functional_data]

            all_triggers = []
            all_triggers.extend(triggers)

            trend.triggers = all_triggers

            # rank triggers
            sorted_triggers = sorted(all_triggers, key=lambda x: (x.source_date_time, x.trigger_type), reverse=True)

            text_generator = RecoveryTextGenerator()
            body_part_factory = BodyPartFactory()

            top_candidates = list(
                s for s in sorted_triggers if s.source_date_time == sorted_triggers[0].source_date_time)

            trigger_header_text, is_plural = self.get_body_part_title_text(body_part_factory, top_candidates)

            if is_plural:
                trend_data.title = "Your " + trigger_header_text + " are functionally limited"
            else:
                trend_data.title = "Your " + trigger_header_text + " is functionally limited"

            trend_data.title = trend_data.title.title()
            trend_data.title_color = LegendColor.warning_light

            body_part_text = text_generator.get_body_part_text(top_candidates[0].body_part.body_part_location, None)
            body_part_text.title()

            trend_data.text = body_part_text + " pain is often caused by doing painful things that tend to cause pain when doing painful things.\n"

            bold_text_3 = BoldText()
            bold_text_3.text = body_part_text
            bold_text_3.color = LegendColor.error_light

            # bold_text_4 = BoldText()
            # bold_text_4.text = "specific"
            # bold_text_4.color = LegendColor.warning_light
            trend_data.bold_text.append(bold_text_3)
            #trend_data.bold_text.append(bold_text_4)

            trend.trend_data = trend_data
            trend.visible = True
            trend.priority = 1

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)

            # Now create dashboard category card
            trend_dashboard_category = TrendDashboardCategory(self.athlete_trend_categories[category_index].insight_type)
            trend_dashboard_category.title = "Pain Related Insights"
            trend_dashboard_category.text = "pain identified in"

            trend_dashboard_category.body_part = top_candidates[0].body_part
            trend_dashboard_category.body_part_text = body_part_text

            if len(all_triggers) > 1:
                trend_dashboard_category.footer = "and " + str(len(all_triggers) - 1) + " more..."

            self.dashboard_categories.append(trend_dashboard_category)

        else:
            trend = self.create_limitation_trend()
            self.set_limitation_trend(category_index, trend)




