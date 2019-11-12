from models.athlete_trend import TrendDashboardCategory, PlanAlert, Trend, TrendCategory, TrendData, \
    FirstTimeExperienceElement, CategoryFirstTimeExperienceModal
from models.styles import BoldText, LegendColor, VisualizationType
from models.trigger import TriggerType, Trigger
from models.chart_data import Prevention3sChartData, RecoveryChartData, CareChartData
from models.insights import InsightType
from models.body_parts import BodyPartFactory
from models.soreness_base import BodyPartSide, BodyPartLocation, BodyPartSideViz
from models.athlete_trend import TriggerTile
from models.insights import Insight, InsightData, PlotLegend, InsightVisualizationData
from models.sport import SportName
from logic.goal_focus_text_generator import RecoveryTextGenerator
from copy import deepcopy
from math import ceil
from datetime import datetime, timedelta


class TrendProcessor(object):
    def __init__(self, injury_hist_dict, event_date_time, athlete_trend_categories=None, dashboard_categories=None, athlete_insight_categories=None):
        self.athlete_insight_categories = [] if athlete_insight_categories is None else athlete_insight_categories
        self.athlete_trend_categories = [] if athlete_trend_categories is None else athlete_trend_categories
        self.injury_hist_dict = injury_hist_dict
        self.dashboard_categories = [] if dashboard_categories is None else dashboard_categories
        self.event_date_time = event_date_time
        self.initialize_trend_categories()

    def initialize_trend_categories(self):

        del_list = []

        for c in range(0, len(self.athlete_trend_categories)):
            if (self.athlete_trend_categories[c].insight_type in [InsightType.stress,
                                                                  InsightType.response,
                                                                  InsightType.biomechanics,
                                                                  InsightType.movement_dysfunction_compensation]):
                del_list.append(c)

        del_list.sort(reverse=True)

        for d in del_list:
            del(self.athlete_trend_categories[d])

        care_index = next((i for i, x in enumerate(self.athlete_trend_categories) if InsightType.care == x.insight_type), -1)

        if care_index == -1:
            care_category = self.create_care_category()
            care_insight_category = deepcopy(care_category)
            self.athlete_trend_categories.append(care_category)
            self.athlete_insight_categories.append(care_insight_category)
        else:
            self.remove_old_trends(care_index, VisualizationType.care_today)

        prevention_index = next(
            (i for i, x in enumerate(self.athlete_trend_categories) if InsightType.prevention == x.insight_type), -1)

        if prevention_index == -1:
            prevention_category = self.create_prevention_category()
            prevention_insight_category = deepcopy(prevention_category)
            self.athlete_trend_categories.append(prevention_category)
            self.athlete_insight_categories.append(prevention_insight_category)
        else:
            self.remove_old_trends(prevention_index, VisualizationType.prevention)

        recovery_index = next(
            (i for i, x in enumerate(self.athlete_trend_categories) if InsightType.personalized_recovery == x.insight_type), -1)

        if recovery_index == -1:
            personalized_recovery_category = self.create_personalized_recovery_category()
            recovery_insight_category = deepcopy(personalized_recovery_category)
            self.athlete_trend_categories.append(personalized_recovery_category)
            self.athlete_insight_categories.append(recovery_insight_category)
        else:
            self.remove_old_trends(recovery_index, VisualizationType.personalized_recovery)

    def remove_old_trends(self, cat_index, viz_type):
        del_list = []
        trends = self.athlete_trend_categories[cat_index].trends
        for t in range(len(trends)):
            if trends[t].visualization_type == viz_type:
                del_list.append(t)
        del_list.sort(reverse=True)
        for d in del_list:
            del trends[d]

    def get_care_trend(self, category_index):

        care_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                                 x.visualization_type == VisualizationType.care), -1)
        if care_index == -1:
            care_trend = self.create_care_trend()
            self.athlete_trend_categories[category_index].trends.append(care_trend)
            care_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[care_index]

    def set_care_trend(self, category_index, care_trend):

        index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.care), -1)

        if index == -1:
            self.athlete_trend_categories[category_index].trends.append(care_trend)
        else:
            self.athlete_trend_categories[category_index].trends[index] = care_trend

    def get_prevention_trend(self, category_index):

        limitation_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                                 x.visualization_type == VisualizationType.prevention3s), -1)
        if limitation_index == -1:
            limitation_trend = self.create_prevention_trend()
            self.athlete_trend_categories[category_index].trends.append(limitation_trend)
            limitation_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[limitation_index]

    def set_prevention_trend(self, category_index, prevention_trend):

        index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                      x.visualization_type == VisualizationType.prevention3s), -1)

        if index == -1:
            self.athlete_trend_categories[category_index].trends.append(prevention_trend)
        else:
            self.athlete_trend_categories[category_index].trends[index] = prevention_trend

    def get_personalized_recovery_trend(self, category_index):

        muscle_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.recovery), -1)
        if muscle_index == -1:
            muscle_trend = self.create_personalized_recovery_trend()
            self.athlete_trend_categories[category_index].trends.append(muscle_trend)
            muscle_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[muscle_index]

    def set_personalized_recovery_trend(self, category_index, recovery_trend):

        muscle_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.recovery), -1)

        if muscle_index == -1:
            self.athlete_trend_categories[category_index].trends.append(recovery_trend)
        else:
            self.athlete_trend_categories[category_index].trends[muscle_index] = recovery_trend

    def get_category_index(self, insight_type):

        category_index = next((i for i, x in enumerate(self.athlete_trend_categories) if
                               x.insight_type == insight_type), -1)
        if category_index == -1:
            trend_category = self.create_personalized_recovery_category()
            self.athlete_trend_categories.append(trend_category)
            category_index = len(self.athlete_trend_categories) - 1
        return category_index

    def get_insight_category_index(self, insight_type):

        category_index = next((i for i, x in enumerate(self.athlete_insight_categories) if
                               x.insight_type == insight_type), -1)
        if category_index == -1:
            trend_category = self.create_personalized_recovery_category()
            self.athlete_insight_categories.append(trend_category)
            category_index = len(self.athlete_trend_categories) - 1
        return category_index

    def create_personalized_recovery_category(self):
        trend_category = TrendCategory(InsightType.personalized_recovery)
        trend_category.title = "Personalized Recovery"
        trend_category.first_time_experience = True

        muscle_trend = self.create_personalized_recovery_trend()
        trend_category.trends.append(muscle_trend)

        trend_category.trend_data = Insight()

        modal = CategoryFirstTimeExperienceModal()
        modal.title = "Personalized Recovery - FTE"
        modal.body = ("We monitor your data for signs of imbalances in  muscle activation, range of motion and more.\n\n" +
                        "These imbalances can create inefficiency in speed & power production, over-strain tissues making them short and tight, and even increase soft tissue injury risk.\n\n" +
                        "We try to find and help address two types of body-part specific imbalances:")
        element_1 = FirstTimeExperienceElement()
        element_1.title = "Tissue Under\n& Over Activity"
        element_1.image = "view1icon.png"

        modal.categories.append(element_1)

        modal.subtext = 'Tap “Continue” to see your unique findings.'

        trend_category.first_time_experience_modal = modal

        return trend_category

    def create_prevention_category(self):
        trend_category = TrendCategory(InsightType.prevention)
        trend_category.title = "Prevention"
        trend_category.first_time_experience = True

        limitation_trend = self.create_prevention_trend()
        trend_category.trends.append(limitation_trend)

        trend_category.trend_data = Insight()

        modal = CategoryFirstTimeExperienceModal()
        modal.title = "Prevention - FTE"
        modal.body = ("We monitor your data for signs of imbalances in  muscle activation, range of motion and more.\n\n" +
                        "These imbalances can create inefficiency in speed & power production, over-strain tissues making them short and tight, and even increase soft tissue injury risk.\n\n" +
                        "We try to find and help address two types of body-part specific imbalances:")

        element_2 = FirstTimeExperienceElement()
        element_2.title = "Functional\nLimitations"
        element_2.image = "view3icon.png"

        modal.categories.append(element_2)

        modal.subtext = 'Tap “Continue” to see your unique findings.'

        trend_category.first_time_experience_modal = modal

        return trend_category

    def create_care_category(self):
        trend_category = TrendCategory(InsightType.care)
        trend_category.title = "Care"
        trend_category.first_time_experience = True

        daily_trend = self.create_care_trend()
        trend_category.trends.append(daily_trend)

        trend_category.trend_data = Insight()

        modal = CategoryFirstTimeExperienceModal()
        modal.title = "Care - FTE"
        modal.body = ("We monitor your data for signs of imbalances in  muscle activation, range of motion and more.\n\n" +
                        "These imbalances can create inefficiency in speed & power production, over-strain tissues making them short and tight, and even increase soft tissue injury risk.\n\n" +
                        "We try to find and help address two types of body-part specific imbalances:")

        element_2 = FirstTimeExperienceElement()
        element_2.title = "Functional\nLimitations"
        element_2.image = "view3icon.png"

        modal.categories.append(element_2)

        modal.subtext = 'Tap “Continue” to see your unique findings.'

        trend_category.first_time_experience_modal = modal

        return trend_category

    def create_care_trend(self):
        daily_trend = Trend(TriggerType.sore_today)
        daily_trend.title = "Daily Care"
        daily_trend.title_color = LegendColor.error_light
        daily_trend.text.append("Your pain may lead to elevated strain on other muscles and soft tissue injury.")
        daily_trend.text.append(
            "Most people, knowingly or not, change the way they move to distribute force away from areas of pain. " +
            "This over-stresses supporting tissues and limbs which adopt more force and stress than they’re used to. " +
            "This often leads accumulated muscle damage and the eventual development of new injuries. See your factors below.")

        daily_trend.icon = "view3icon.png"
        daily_trend.video_url = "https://d2xll36aqjtmhz.cloudfront.net/view3context.mp4"
        daily_trend.visualization_type = VisualizationType.care
        daily_trend.visible = False
        daily_trend.first_time_experience = True

        return daily_trend

    def create_prevention_trend(self):
        limitation_trend = Trend(TriggerType.hist_sore_greater_30)
        limitation_trend.title = "Injury Cycle Risks"
        limitation_trend.title_color = LegendColor.error_light
        limitation_trend.text.append("Your pain may lead to elevated strain on other muscles and soft tissue injury.")
        limitation_trend.text.append("Most people, knowingly or not, change the way they move to distribute force away from areas of pain. "+
                                     "This over-stresses supporting tissues and limbs which adopt more force and stress than they’re used to. "+
                                     "This often leads accumulated muscle damage and the eventual development of new injuries. See your factors below.")


        limitation_trend.icon = "view3icon.png"
        limitation_trend.video_url = "https://d2xll36aqjtmhz.cloudfront.net/view3context.mp4"
        limitation_trend.visualization_type = VisualizationType.prevention3s
        limitation_trend.visible = False
        limitation_trend.first_time_experience = True
        return limitation_trend

    def create_personalized_recovery_trend(self):
        muscle_trend = Trend(TriggerType.hist_pain)
        muscle_trend.title = "Muscle Over & Under-Activity"
        muscle_trend.title_color = LegendColor.warning_light
        muscle_trend.text.append("Your data suggests you may have some imbalances in muscle activation which can lead to performance inefficiencies like decreased speed and power output.")
        muscle_trend.text.append("If these imbalances persist, they can turn into strength dysfunctions which alter your biomechanics and elevate soft tissue injury risk."+
                                 " Addressing these imbalances early is important for athletic resilience.")

        muscle_trend.icon = "view1icon.png"
        muscle_trend.video_url = "https://d2xll36aqjtmhz.cloudfront.net/view1context.mp4"
        muscle_trend.visualization_type = VisualizationType.recovery
        muscle_trend.visible = False
        muscle_trend.first_time_experience = True
        return muscle_trend

    def process_triggers(self):

        personalized_recovery_category_index = self.get_category_index(InsightType.personalized_recovery)
        prevention_category_index = self.get_category_index(InsightType.prevention)
        care_category_index = self.get_category_index(InsightType.care)
        self.set_recovery(personalized_recovery_category_index)
        self.set_prevention(prevention_category_index)
        self.set_care(care_category_index)

        for c in range(0, len(self.athlete_trend_categories)):
            if len(self.athlete_trend_categories[c].trends) > 0:
                none_dates = list(t for t in self.athlete_trend_categories[c].trends if t.last_date_time is None)
                full_dates = list(t for t in self.athlete_trend_categories[c].trends if t.last_date_time is not None)

                self.athlete_trend_categories[c].trends = []

                new_modified_trigger_count = 0
                plan_alert_short_title = ""

                if len(full_dates) > 0:
                    full_dates = sorted(full_dates, key=lambda x: (x.last_date_time, x.priority), reverse=True)
                    # if len(plan_alert_short_title) == 0:
                    #     plan_alert_short_title = full_dates[0].plan_alert_short_title
                    # for f in full_dates:
                    #     new_modified_trigger_count += len(f.triggers)

                self.athlete_trend_categories[c].trends.extend(full_dates)
                self.athlete_trend_categories[c].trends.extend(none_dates)

                visible_trends = list(t for t in self.athlete_trend_categories[c].trends if t.visible)

                trends_visible = False

                if len(visible_trends) > 0:

                    trends_visible = True

                    # Now create dashboard category card
                    self.dashboard_categories = []

                else:
                    self.athlete_trend_categories[c].plan_alerts = []

                self.athlete_trend_categories[c].visible = trends_visible

    # def get_plan_alert(self, new_modified_trigger_count, plan_alert_short_title, trend_category_index, visible_trends):
    #
    #     #header_text = str(new_modified_trigger_count) + " Tissue Related Insights"
    #     #header_text = "New Tissue Related Insights"
    #     header_text = "Signs of Imbalance"
    #     body_text = "Signs of " + plan_alert_short_title
    #     if len(visible_trends) > 1:
    #         # we're bringing this back later
    #         # if len(visible_trends) == 2:
    #         #     body_text += " and " + str(len(visible_trends) - 1) + " other meaningful insight"
    #         # else:
    #         #     body_text += " and " + str(len(visible_trends) - 1) + " other meaningful insights"
    #         body_text += " and other insights"
    #     body_text += " in your data. Tap to view more."
    #     plan_alert = PlanAlert(self.athlete_trend_categories[trend_category_index].insight_type)
    #     plan_alert.title = header_text
    #     plan_alert.text = body_text
    #     bold_text_1 = BoldText()
    #     bold_text_1.text = plan_alert_short_title
    #     plan_alert.bold_text.append(bold_text_1)
    #     return plan_alert

    def get_title_text_for_body_parts(self, body_parts, side, use_plural=True):

        is_plural = False

        text_generator = RecoveryTextGenerator()
        body_part_factory = BodyPartFactory()

        converted_body_parts = []

        for b in body_parts:
            body_part = body_part_factory.get_body_part(b)
            body_part.bilateral = body_part_factory.get_bilateral(body_part.location)
            if body_part.treatment_priority is None:
                body_part.treatment_priority = 99
            converted_body_parts.append(body_part)

            if body_part.location is None:
                h=0

        if side == 0:
            converted_body_parts = set(converted_body_parts)

        bilateral_body_parts = list(b for b in converted_body_parts if b.bilateral)
        bilateral_body_parts = sorted(bilateral_body_parts, key=lambda x: x.treatment_priority)
        non_bilateral_body_parts = list(b for b in converted_body_parts if not b.bilateral)
        non_bilateral_body_parts = sorted(non_bilateral_body_parts, key=lambda x: x.treatment_priority)

        sorted_body_parts = []
        sorted_body_parts.extend(bilateral_body_parts)
        sorted_body_parts.extend(non_bilateral_body_parts)

        title_text = ""

        for b in range(0, len(sorted_body_parts)):
            if side == 0:
                if use_plural:
                    body_part_text = text_generator.get_body_part_text_plural(sorted_body_parts[b].location,
                                                                           side).title()
                    is_plural = True
                else:
                    body_part_text = text_generator.get_body_part_text(sorted_body_parts[b].location,
                                                                              side).title()

            else:
                if sorted_body_parts[b].bilateral:
                    body_part_text = text_generator.get_body_part_text(sorted_body_parts[b].location,
                                                                       side).title()
                else:
                    body_part_text = text_generator.get_body_part_text(sorted_body_parts[b].location,
                                                                       None).title()
            if b == len(sorted_body_parts) - 2:
                body_part_text += " & "
            elif b <= len(sorted_body_parts) - 3:
                body_part_text += ", "
            title_text += body_part_text

        return title_text, is_plural

    # def get_latest_trigger_date_time(self, triggers):
    #
    #     if len(triggers) > 0:
    #
    #         last_created_date_time = None
    #
    #         # turns out we are only interested when a new body part is added or when a historic soreness status changes
    #         created_triggers = sorted(triggers, key=lambda x: x.created_date_time, reverse=True)
    #         #modified_triggers = sorted(triggers, key=lambda x: x.modified_date_time, reverse=True)
    #         #status_changed_triggers = [t for t in triggers if t.source_date_time is not None]
    #         if len(created_triggers) > 0:
    #             status_triggers = sorted(triggers, key=lambda x: x.created_date_time, reverse=True)
    #             created_date_time = status_triggers[0].created_date_time
    #
    #             last_created_date_time = created_triggers[0].created_date_time
    #         #last_modified_date_time = modified_triggers[0].modified_date_time
    #
    #         #if status_changed_date_time is not None:
    #         #    return status_changed_date_time
    #         #elif last_modified_date_time is not None:
    #         #    return max(last_modified_date_time, last_created_date_time)
    #         #else:
    #         return last_created_date_time
    #
    #     else:
    #         return None

    # def get_over_under_active_dashboard_card(self, category_index, trend):
    #     trend_dashboard_category = TrendDashboardCategory(self.athlete_trend_categories[category_index].insight_type)
    #     trend_dashboard_category.title = "Signs of Imbalance"
    #     if trend.top_priority_trigger.priority == 1:
    #         trend_dashboard_category.text = "Elevated strain on"
    #     else:
    #         trend_dashboard_category.text = "Potential weakness in"
    #     trend_dashboard_category.body_part = trend.dashboard_body_part
    #     trend_dashboard_category.body_part_text = trend.dashboard_body_part_text
    #     trend_dashboard_category.color = LegendColor.splash_x_light
    #     body_part_set = set()
    #     body_part_location_set = set()
    #     for t in self.trigger_list:
    #         if t.body_part is not None:
    #             body_part_set.add(t.body_part)  # not sure we need this
    #             body_part_location_set.add(t.body_part.body_part_location)
    #     if len(body_part_location_set) > 1:
    #         trend_dashboard_category.body_part_text += " and more..."
    #     return trend_dashboard_category

    # def get_body_part_title_text(self, body_part_factory, top_candidates):
    #
    #     text_generator = RecoveryTextGenerator()
    #     is_plural = False
    #
    #     if len(top_candidates) == 1:
    #         trigger_header_text = text_generator.get_body_part_text(top_candidates[0].body_part.body_part_location,
    #                                                                 top_candidates[0].body_part.side)
    #     else:
    #         trigger_dictionary = {}
    #         for t in top_candidates:
    #             body_part = body_part_factory.get_body_part(t.body_part)
    #             trigger_dictionary[t.body_part] = body_part.treatment_priority
    #
    #         # still could have a tie (two body parts)
    #         sorted_trigger_items = sorted(trigger_dictionary.items(), key=lambda x: x[1])
    #         if len(sorted_trigger_items) > 1:
    #             if sorted_trigger_items[0][1] == sorted_trigger_items[1][1]:
    #                 trigger_header_text = text_generator.get_body_part_text_plural(
    #                     top_candidates[0].body_part.body_part_location, None)
    #                 is_plural = True
    #             else:
    #                 trigger_header_text = text_generator.get_body_part_text(
    #                     top_candidates[0].body_part.body_part_location, top_candidates[0].body_part.side)
    #         else:
    #             trigger_header_text = text_generator.get_body_part_text(top_candidates[0].body_part.body_part_location,
    #                                                                     top_candidates[0].body_part.side)
    #     return trigger_header_text, is_plural

    # def get_highest_priority_body_part_from_triggers(self, body_part_factory, top_candidates):
    #
    #     if len(top_candidates) == 1:
    #         if top_candidates[0].body_part is not None:
    #             return top_candidates[0], top_candidates[0].body_part.side == 0
    #         else:
    #             return top_candidates[0], True
    #     else:
    #         for t in top_candidates:
    #             if t.body_part is not None:
    #                 body_part = body_part_factory.get_body_part(t.body_part)
    #                 t.body_part_priority = body_part.treatment_priority
    #
    #         # still could have a tie (two body parts)
    #         sorted_triggers = sorted(top_candidates, key=lambda x: x.body_part_priority)
    #
    #         if len(sorted_triggers) > 1:
    #             if sorted_triggers[0].body_part_priority == sorted_triggers[1].body_part_priority:
    #                 return sorted_triggers[0], True
    #             else:
    #                 if sorted_triggers[0].body_part is not None:
    #                     return sorted_triggers[0], sorted_triggers[0].body_part.side == 0
    #                 else:
    #                     return sorted_triggers[0], True
    #         else:
    #             if sorted_triggers[0].body_part is not None:
    #                 return sorted_triggers[0], sorted_triggers[0].body_part.side == 0
    #             else:
    #                 return sorted_triggers[0], True

    # def get_title_body_part_and_text(self, body_parts, side):
    #
    #     text_generator = RecoveryTextGenerator()
    #     body_part_factory = BodyPartFactory()
    #
    #     converted_body_parts = []
    #
    #     for b in body_parts:
    #         body_part = body_part_factory.get_body_part(b)
    #         converted_body_parts.append(body_part)
    #
    #     sorted_body_parts = sorted(converted_body_parts, key=lambda x: x.treatment_priority)
    #
    #     if side == 0:
    #         body_part_side = BodyPartSide(sorted_body_parts[0].location, None)
    #         body_part_text = text_generator.get_body_part_text_plural(sorted_body_parts[0].location, None).title()
    #     else:
    #         if sorted_body_parts[0].bilateral:
    #             body_part_side = BodyPartSide(sorted_body_parts[0].location, side)
    #             body_part_text = text_generator.get_body_part_text(sorted_body_parts[0].location, side).title()
    #         else:
    #             body_part_side = BodyPartSide(sorted_body_parts[0].location, None)
    #             body_part_text = text_generator.get_body_part_text(sorted_body_parts[0].location, None).title()
    #
    #     return body_part_side, body_part_text

    def set_care(self, category_index):

        inflamed = []
        muscle_spasm = []
        knots = []
        inflamed_low = []
        inflamed_mod = []
        inflamed_high = []

        for body_part_side, body_part_injury_risk in self.injury_hist_dict.items():
            is_inflammation = False
            is_muscle_spasm = False
            is_knots = False

            if (body_part_injury_risk.last_inflammation_date is not None and
                    body_part_injury_risk.last_inflammation_date == self.event_date_time.date()):
                is_inflammation = True

            if (body_part_injury_risk.last_muscle_spasm_date is not None and
                    body_part_injury_risk.last_muscle_spasm_date == self.event_date_time.date()):
                is_muscle_spasm = True

            if (body_part_injury_risk.last_knots_date is not None and
                    body_part_injury_risk.last_knots_date == self.event_date_time.date()):
                is_knots = True

            #if is_inflammation and not is_muscle_spasm and not is_knots:
            if is_inflammation:
                inflammation_severity = body_part_injury_risk.get_inflammation_severity(self.event_date_time.date())
                if inflammation_severity >= 7:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.error_light)
                    inflamed_high.append(body_part_side_viz)
                elif 4 <= inflammation_severity < 7:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.error_x_light)
                    inflamed_mod.append(body_part_side_viz)
                else:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.error_xx_light)
                    inflamed_low.append(body_part_side_viz)
                inflamed.append(body_part_side_viz)

            #if not is_inflammation and not is_muscle_spasm and is_knots:
            if not is_inflammation and is_knots:
                tight_severity = body_part_injury_risk.last_knots_level
                if tight_severity >= 7:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.warning_light)
                elif 4 <= tight_severity < 7:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.warning_x_light)
                else:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.warning_xx_light)
                knots.append(body_part_side_viz)

            #if not is_inflammation and is_muscle_spasm and not is_knots:
            if not is_inflammation and not is_knots and is_muscle_spasm:
                muscle_spasm_severity = body_part_injury_risk.get_muscle_spasm_severity(self.event_date_time.date())
                if muscle_spasm_severity >= 7:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.warning_light)
                elif 4 <= muscle_spasm_severity < 7:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.warning_x_light)
                else:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.warning_xx_light)
                muscle_spasm.append(body_part_side_viz)

        if len(inflamed) > 0 or len(muscle_spasm) > 0 and len(knots) > 0:

            trend = self.get_care_trend(category_index)

            care_index = self.get_insight_category_index(InsightType.care)

            insight_category = self.athlete_insight_categories[care_index]
            insight_category.active = True

            inflamed_list = []
            inflamed_list.extend(inflamed_high)
            inflamed_list.extend(inflamed_mod)
            inflamed_high.extend(inflamed_low)

            tight_list = []
            tight_list.extend(muscle_spasm)
            tight_list.extend(knots)

            inflamed_list, tight_list = self.remove_duplicates_two_lists(inflamed_list, tight_list)
            inflamed_high = [i for i in inflamed_high if i in inflamed_list]
            inflamed_mod = [i for i in inflamed_mod if i in inflamed_list]
            inflamed_low = [i for i in inflamed_low if i in inflamed_list]
            muscle_spasm = [m for m in muscle_spasm if m in tight_list]
            knots = [k for k in knots if k in tight_list]

            inflamed_data = self.get_inflamed_insight_data(inflamed_high, inflamed_low, inflamed_mod)
            tight_data = self.get_tight_insight_data(muscle_spasm, knots)

            insight_category.trend_data.data.append(inflamed_data)
            insight_category.trend_data.data.append(tight_data)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.care
            trend_data.add_visualization_data()
            care_data = CareChartData()

            care_data.inflamed.extend(inflamed)
            care_data.tight.extend(muscle_spasm)
            care_data.tight.extend(knots)

            care_data.remove_duplicates()
            trend_data.data = [care_data]

            trend.trigger_tiles = []
            if len(inflamed_high) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(inflamed_high, "Inflamed - High", LegendColor.error_light))
            if len(inflamed_mod) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(inflamed_mod, "Inflamed - Mod", LegendColor.error_light))
            if len(inflamed_low) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(inflamed_low, "Inflamed - Low", LegendColor.error_light))
            if len(muscle_spasm) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(muscle_spasm, "Tight - Muscle Spasms", LegendColor.warning_light))
            if len(knots) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(knots, "Tight - Adhesions", LegendColor.warning_light))


            # trend.trigger_tiles.extend(self.get_trigger_tiles(inflamed))
            # trend.trigger_tiles.extend(self.get_trigger_tiles(muscle_spasm_tight))

            # rank triggers
            #sorted_triggers = sorted(all_triggers, key=lambda x: (x.created_date_time, x.priority), reverse=True)

            #trend.triggers = all_triggers

            trend.trend_data = trend_data
            trend.visible = True
            trend.priority = 1

            #trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)
            trend.last_date_time = self.event_date_time

            self.set_care_trend(category_index, trend)

        else:
            trend = self.create_care_trend()
            self.set_care_trend(category_index, trend)

    def get_inflamed_insight_data(self, inflamed_high, inflamed_low, inflamed_mod):

        inflamed_data = InsightData()
        inflamed_data.title = 'inflamed'
        inflamed_data.active = True
        inflamed_data.color = LegendColor.error_light
        low_plot_legend = PlotLegend(LegendColor.error_xx_light, 'Low', 0)
        mod_plot_legend = PlotLegend(LegendColor.error_x_light, 'Mod', 1)
        high_plot_legend = PlotLegend(LegendColor.error_light, 'High', 2)
        inflamed_viz_data = InsightVisualizationData()
        inflamed_viz_data.plot_legends = [high_plot_legend, mod_plot_legend, low_plot_legend]
        inflamed_data.visualization_data = inflamed_viz_data
        if len(inflamed_high) == 0 and len(inflamed_mod) == 0 and len(inflamed_low) == 0:
            empty_trigger_tile = TriggerTile()
            title_text = "No Signs of Inflammation"
            empty_trigger_tile.title = title_text
            empty_trigger_tile.text = "You haven't reported any symptoms which indicate tissue inflammation."
            bold_1 = BoldText()
            bold_1.text = title_text
            bold_1.color = LegendColor.slate_light
            empty_trigger_tile.bold_text.append(bold_1)
        if len(inflamed_high) > 0:
            high_trigger_tile = TriggerTile()
            high_trigger_tile.body_parts = inflamed_high
            title_text = "Severe Inflammation"
            high_trigger_tile.title = title_text
            high_trigger_tile.text = "Severe pain & soreness are signs of inflammation and tissue damage. To help reduce inflammation, give these areas some rest, do your 'Care' activities, and avoid any movements that cause pain."
            bold_1 = BoldText()
            bold_1.text = title_text
            bold_1.color = LegendColor.error_light
            high_trigger_tile.bold_text.append(bold_1)
            inflamed_data.trigger_tiles.append(high_trigger_tile)
        if len(inflamed_mod) > 0:
            mod_trigger_tile = TriggerTile()
            mod_trigger_tile.body_parts = inflamed_mod
            title_text = "Moderate Inflammation"
            mod_trigger_tile.title = title_text
            mod_trigger_tile.text = "These tissues have signs of inflammation and shortening which can restrict mobility and alter muscle activation. This leads to movement compensations in training which elevate injury risk and recovery need."
            bold_1 = BoldText()
            bold_1.text = title_text
            bold_1.color = LegendColor.error_light
            mod_trigger_tile.bold_text.append(bold_1)
            inflamed_data.trigger_tiles.append(mod_trigger_tile)
        if len(inflamed_low) > 0:
            low_trigger_tile = TriggerTile()
            low_trigger_tile.body_parts = inflamed_low
            title_text = "Mild Inflammation"
            low_trigger_tile.title = title_text
            low_trigger_tile.color = LegendColor.error_light
            low_trigger_tile.text = "These tissues likely have mild inflammation. For optimal movement efficiency, reduce this inflammation with the foam rolling and stretching activities created for you in your 'Care' plan."
            bold_1 = BoldText()
            bold_1.text = title_text
            bold_1.color = LegendColor.error_xx_light
            low_trigger_tile.bold_text.append(bold_1)
            inflamed_data.trigger_tiles.append(low_trigger_tile)
        return inflamed_data

    def get_tight_insight_data(self, tight_spasm, tight_adhesions):

        tight_data = InsightData()
        tight_data.title = 'tight'
        tight_data.active = True
        tight_data.color = LegendColor.warning_light
        low_plot_legend = PlotLegend(LegendColor.warning_xx_light, 'Low', 0)
        mod_plot_legend = PlotLegend(LegendColor.warning_x_light, 'Mod', 1)
        high_plot_legend = PlotLegend(LegendColor.warning_light, 'High', 2)
        tight_viz_data = InsightVisualizationData()
        tight_viz_data.plot_legends = [high_plot_legend, mod_plot_legend, low_plot_legend]
        tight_data.visualization_data = tight_viz_data
        if len(tight_spasm) == 0 and len(tight_adhesions) == 0:
            empty_trigger_tile = TriggerTile()
            title_text = "No Signs of Tightness"
            empty_trigger_tile.title = title_text
            empty_trigger_tile.text = "You haven't reported any symptoms which indicate tissue tightness."
            bold_1 = BoldText()
            bold_1.text = title_text
            bold_1.color = LegendColor.slate_light
            empty_trigger_tile.bold_text.append(bold_1)
        if len(tight_spasm) > 0:
            high_trigger_tile = TriggerTile()
            high_trigger_tile.body_parts = tight_spasm
            title_text = "Muscle Spasm"
            high_trigger_tile.title = title_text
            high_trigger_tile.text = "Tightness in a tissue can change the way you move, causing compensations during training. Your 'Care' activities help 'release' this tightness."
            bold_1 = BoldText()
            bold_1.text = title_text
            bold_1.color = LegendColor.warning_light
            high_trigger_tile.bold_text.append(bold_1)
            tight_data.trigger_tiles.append(high_trigger_tile)
        if len(tight_adhesions) > 0:
            mod_trigger_tile = TriggerTile()
            mod_trigger_tile.body_parts = tight_adhesions
            title_text = "Tightness Causing Damage"
            mod_trigger_tile.title = title_text
            mod_trigger_tile.text = "Chronic tightness and inflammation leads to muscles forming knots which decrease the tissue's ability to produce and absorb force. Training in this condition further damages the muscle and diverts stress to other tissues- elevating the risk of injury."
            bold_1 = BoldText()
            bold_1.text = title_text
            bold_1.color = LegendColor.warning_light
            mod_trigger_tile.bold_text.append(bold_1)
            tight_data.trigger_tiles.append(mod_trigger_tile)

        return tight_data

    def remove_duplicates_two_lists(self, list_high, list_low):

        unc_delete = []

        id = 0
        for u in list_low:
            index = next((i for i, x in enumerate(list_high) if u == x), -1)

            if index > -1:
                unc_delete.append(id)
            id += 1

        unc_delete.sort(reverse=True)  # need to remove in reverse order so we don't mess up indexes along the way

        for d in unc_delete:
            del (list_low[d])

        return list_high, list_low

    def set_recovery(self, category_index):

        two_days_ago = self.event_date_time.date() - timedelta(days=1)

        training_stress = []
        high_stress = []
        mod_stress = []
        low_stress = []
        compensating = []
        movement_dysfunction = []

        last_date_time = self.event_date_time - timedelta(days=1)

        for body_part_side, body_part_injury_risk in self.injury_hist_dict.items():

            is_training_stress_today = False
            is_compensating = False
            is_elevated_stress = False
            # is_functional_overreaching_today = False
            # is_non_functional_overreaching = False

            if (body_part_injury_risk.last_compensation_date is not None and
                    body_part_injury_risk.last_compensation_date == self.event_date_time.date() and
                    body_part_injury_risk.total_compensation_percent_tier < 4):
                is_compensating = True

            if 0 < body_part_injury_risk.total_volume_percent_tier < 4:
                is_training_stress_today = True

            # if body_part_injury_risk.last_functional_overreaching_date is not None and body_part_injury_risk.last_functional_overreaching_date == self.event_date_time.date():
            #     is_functional_overreaching_today = True
            #
            # if body_part_injury_risk.last_non_functional_overreaching_date is not None and body_part_injury_risk.last_non_functional_overreaching_date >= two_days_ago:
            #     is_non_functional_overreaching = True

            if (body_part_injury_risk.last_movement_dysfunction_stress_date is not None and
                    body_part_injury_risk.last_movement_dysfunction_stress_date == self.event_date_time.date()):
                is_elevated_stress = True

            if is_elevated_stress:
                if body_part_injury_risk.total_compensation_percent_tier == 1:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                        LegendColor.yellow_light)
                elif body_part_injury_risk.total_compensation_percent_tier == 2:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                        LegendColor.yellow_x_light)
                else:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.yellow_xx_light)
                movement_dysfunction.append(body_part_side_viz)

            if is_compensating and not is_elevated_stress:
                if body_part_injury_risk.total_compensation_percent_tier == 1:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                        LegendColor.yellow_light)
                elif body_part_injury_risk.total_compensation_percent_tier == 2:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                        LegendColor.yellow_x_light)
                else:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.yellow_xx_light)
                compensating.append(body_part_side_viz)

            if not is_compensating and not is_elevated_stress and is_training_stress_today:
                if body_part_injury_risk.total_volume_percent_tier == 1:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                            LegendColor.success_light)
                    high_stress.append(body_part_side_viz)

                elif body_part_injury_risk.total_volume_percent_tier == 2:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                             LegendColor.success_x_light)
                    mod_stress.append(body_part_side_viz)

                else:
                    body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                         LegendColor.success_xx_light)
                    low_stress.append(body_part_side_viz)
                training_stress.append(body_part_side_viz)

        if len(training_stress) > 0 or len(compensating) > 0 or len(movement_dysfunction) > 0:

            trend = self.get_personalized_recovery_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.recovery
            trend_data.add_visualization_data()
            recovery_data = RecoveryChartData()

            recovery_data.training_stress.extend(training_stress)
            recovery_data.compensation_stress.extend(compensating)
            recovery_data.compensation_stress.extend(movement_dysfunction)

            recovery_data.remove_duplicates()
            trend_data.data = [recovery_data]

            trend.trigger_tiles = []
            if len(compensating) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(compensating, "Symptom Reporting", LegendColor.yellow_light))
            if len(movement_dysfunction) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(movement_dysfunction, "Movement Dysfunction", LegendColor.yellow_light))
            if len(high_stress) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(high_stress, "Training - High", LegendColor.success_light))
            if len(mod_stress) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(mod_stress, "Training - Mod", LegendColor.success_light))
            if len(low_stress) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(low_stress, "Training - Low", LegendColor.success_light))

            # trend.trigger_tiles.extend(self.get_trigger_tiles(excessive_strain_nfo))
            # trend.trigger_tiles.extend(self.get_trigger_tiles(compensating))
            # trend.trigger_tiles.extend(self.get_trigger_tiles(excessive_strain_fo))

            trend.trend_data = trend_data

            trend.visible = True
            trend.priority = 0

            #trend.triggers = all_triggers

            #trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)
            trend.last_date_time = self.event_date_time

            self.set_personalized_recovery_trend(category_index, trend)

        else:
            trend = self.create_personalized_recovery_trend()
            self.set_personalized_recovery_trend(category_index, trend)

    def set_prevention(self, category_index):

        short = []
        joint_artho = []
        overactive = []
        tendin = []
        underactive_weak = []
        underactive_inhibited = []
        limited_mobility_2 = []
        limited_mobility_3 = []
        underactive_weak_2 = []
        underactive_weak_3 = []

        for body_part_side, body_part_injury_risk in self.injury_hist_dict.items():

            is_short = False
            is_overactive_short = False
            is_joint_arthro = False
            is_tendin = False
            is_weak = False
            is_inhibited = False

            if self.is_body_part_short(body_part_injury_risk):
                is_short = True

            if body_part_injury_risk.overactive_short_count_last_0_20_days >= 3:
                is_overactive_short = True

            if body_part_injury_risk.underactive_long_count_last_0_20_days >= 3:
                is_inhibited = True

            if (body_part_injury_risk.last_weak_date is not None and
                    body_part_injury_risk.weak_count_last_0_20_days >= 3):
                is_weak = True

            if (body_part_injury_risk.last_altered_joint_arthokinematics_date is not None and
                    body_part_injury_risk.last_altered_joint_arthokinematics_date == self.event_date_time.date()):
                is_joint_arthro = True

            if ((body_part_injury_risk.last_tendinopathy_date is not None and
                    body_part_injury_risk.last_tendinopathy_date == self.event_date_time.date()) or
                    (body_part_injury_risk.last_tendinosis_date is not None and
                     body_part_injury_risk.last_tendinosis_date == self.event_date_time.date())):
                is_tendin = True

            if is_overactive_short and not is_joint_arthro and not is_tendin:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.warning_light)
                overactive.append(body_part_side_viz)

            if is_weak and not is_overactive_short and not is_joint_arthro and not is_tendin:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.splash_light)
                underactive_weak.append(body_part_side_viz)

            if not is_weak and is_inhibited and not is_overactive_short and not is_joint_arthro and not is_tendin:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.splash_light)
                underactive_inhibited.append(body_part_side_viz)

            if is_short and not is_overactive_short and not is_weak and not is_inhibited and not is_joint_arthro and not is_tendin:
                # making this priority 2 (mod)
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.warning_x_light)
                short.append(body_part_side_viz)

            if is_joint_arthro and not is_tendin and not is_overactive_short and not is_weak and not is_inhibited and not is_short:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.warning_light)
                joint_artho.append(body_part_side_viz)

            if is_tendin and not is_joint_arthro and not is_overactive_short and not is_weak and not is_inhibited and not is_short:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.warning_light)
                tendin.append(body_part_side_viz)

            if body_part_injury_risk.limited_mobility_tier == 2:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.warning_x_light)
                limited_mobility_2.append(body_part_side_viz)
            elif body_part_injury_risk.limited_mobility_tier == 3:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.warning_xx_light)
                limited_mobility_3.append(body_part_side_viz)

            if body_part_injury_risk.underactive_weak_tier == 2:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.splash_m_light)
                underactive_weak_2.append(body_part_side_viz)
            elif body_part_injury_risk.underactive_weak_tier == 3:
                body_part_side_viz = BodyPartSideViz(body_part_side.body_part_location, body_part_side.side,
                                                     LegendColor.splash_x_light)
                underactive_weak_3.append(body_part_side_viz)

        # since we're reverse sorting, 2 is a higher priority than 1

        if (len(short) > 0 or len(joint_artho) > 0 or len(overactive) > 0 or len(tendin) > 0 or
                len(underactive_weak) > 0 or len(underactive_inhibited) > 0 or
                len(limited_mobility_2) > 0 or len(limited_mobility_3) > 0 or
                len(underactive_weak_2) > 0 or len(underactive_weak_3) > 0):

            trend = self.get_prevention_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.prevention3s
            trend_data.add_visualization_data()
            prevention_data = Prevention3sChartData()

            prevention_data.limited_mobility.extend(overactive)
            prevention_data.limited_mobility.extend(short)
            prevention_data.limited_mobility.extend(joint_artho)
            prevention_data.limited_mobility.extend(tendin)
            prevention_data.limited_mobility.extend(limited_mobility_2)
            prevention_data.limited_mobility.extend(limited_mobility_3)

            prevention_data.underactive.extend(underactive_weak)
            prevention_data.underactive.extend(underactive_inhibited)
            prevention_data.underactive.extend(underactive_weak_2)
            prevention_data.underactive.extend(underactive_weak_3)

            prevention_data.remove_duplicates()
            trend_data.data = [prevention_data]

            trend.trigger_tiles = []
            if len(short) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(short, "Short - Adhesions", LegendColor.warning_light))
            if len(overactive) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(overactive, "Overactive", LegendColor.warning_light))
            if len(joint_artho) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(joint_artho, "Altered Arthrokinematics", LegendColor.warning_light))
            if len(tendin) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(tendin, "Tendinopathy or Tendinosis", LegendColor.warning_light))
            if len(limited_mobility_2) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(limited_mobility_2, "Signs of Pattern", LegendColor.warning_light))
            if len(limited_mobility_3) > 0:
                trend.trigger_tiles.extend(
                    self.get_body_part_list_trigger_tiles(limited_mobility_3, "Tracking for Pattern", LegendColor.warning_light))

            if len(underactive_weak) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(underactive_weak, "Weak", LegendColor.splash_light))
            if len(underactive_inhibited) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(underactive_inhibited, "Inhibited", LegendColor.splash_light))
            if len(underactive_weak_2) > 0:
                trend.trigger_tiles.extend(self.get_body_part_list_trigger_tiles(underactive_weak_2, "Signs of Pattern", LegendColor.splash_light))
            if len(underactive_weak_3) > 0:
                trend.trigger_tiles.extend(
                    self.get_body_part_list_trigger_tiles(underactive_weak_3, "Tracking for Pattern", LegendColor.splash_light))

            # underactive_list = []
            # underactive_list.extend(underactive_weak)
            # underactive_list.extend(underactive_inhibited)
            #
            # underactive_list = list(set(underactive_list))
            # trend.trigger_tiles.extend(self.get_short_non_adhesions_trigger_tiles(underactive_list))

            # trend.trigger_tiles.extend(self.get_trigger_tiles(underactive_weak))
            # trend.trigger_tiles.extend(self.get_trigger_tiles(underactive_inhibited))
            # trend.trigger_tiles.extend(self.get_trigger_tiles(overactive))
            # trend.trigger_tiles.extend(self.get_trigger_tiles(short_adhesions))
            # trend.trigger_tiles.extend(self.get_trigger_tiles(short_non_adhesions))

            # rank triggers
            #sorted_triggers = sorted(all_triggers, key=lambda x: (x.created_date_time, x.priority), reverse=True)

            #trend.triggers = all_triggers

            trend.trend_data = trend_data
            trend.visible = True
            trend.priority = 1

            #trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)
            trend.last_date_time = self.event_date_time

            self.set_prevention_trend(category_index, trend)

        else:
            trend = self.create_prevention_trend()
            self.set_prevention_trend(category_index, trend)

    def is_body_part_short(self, body_part_injury_risk):

        is_short = False

        if body_part_injury_risk.knots_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.tight_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.sharp_count_last_0_20_days >= 3:
            is_short = True
        if body_part_injury_risk.ache_count_last_0_20_days >= 4:
            is_short = True
        if body_part_injury_risk.short_count_last_0_20_days >= 3:
            is_short = True
        return is_short

    def get_body_part_list_trigger_tiles(self, body_part_sides, title, color):

        care_fss_body_parts = set()
        tiles = []
        statistic_text = ""
        bold_statistic_text = []
        # mobilize_suffix = "to improve tissue range of motion"
        # aggregate to muscle group level
        muscle_groups = []
        for b in body_part_sides:
            muscle_group = b.body_part_location.get_muscle_group(b.body_part_location)
            if isinstance(muscle_group, bool):
                muscle_groups.append(b.body_part_location)
            else:
                muscle_groups.append(muscle_group)

        #sideless_body_parts = [b.body_part_location for b in body_part_sides]
        sideless_body_parts = [b for b in muscle_groups]
        sideless_body_parts = list(set(sideless_body_parts))

        body_part_text_string = ''

        first_time = True

        tile_1 = TriggerTile()

        for body_part_side in sideless_body_parts:

            body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts([body_part_side], 0)
            if len(body_part_text_1) == 0:
                body_part_text_1 = "PRIME MOVER"
            if body_part_text_1 not in care_fss_body_parts:

                if not first_time:
                    body_part_text_string += ", "

                body_part_text_string += body_part_text_1

                care_fss_body_parts.add(body_part_text_1)
                first_time = False

        # tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
        tile_1.text = title
        tile_1.description = body_part_text_string
        bold_1 = BoldText()
        bold_1.text = body_part_text_string
        bold_1.color = color
        tile_1.bold_text.append(bold_1)
        # tile_1.statistic_text = statistic_text
        # tile_1.bold_statistic_text = bold_statistic_text
        ## tile_1.trigger_type = t.trigger_type
        tiles.append(tile_1)
        return tiles

    # def get_functional_limitation_dashboard_card(self, category_index, trend):
    #     trend_dashboard_category = TrendDashboardCategory(self.athlete_trend_categories[category_index].insight_type)
    #     trend_dashboard_category.title = "Signs of Imbalance"
    #     trend_dashboard_category.text = "Elevated strain on"
    #     trend_dashboard_category.color = LegendColor.warning_light
    #     trend_dashboard_category.body_part = trend.dashboard_body_part
    #     trend_dashboard_category.body_part_text = trend.dashboard_body_part_text
    #     body_part_set = set()
    #     body_part_location_set = set()
    #     for t in self.trigger_list:
    #         if t.body_part is not None:
    #             body_part_set.add(t.body_part)  # not sure we need this
    #             body_part_location_set.add(t.body_part.body_part_location)
    #     if len(body_part_location_set) > 1:
    #         trend_dashboard_category.body_part_text += " and more..."
    #     return trend_dashboard_category

    # def get_short_adhesions_trigger_tiles(self, body_part_sides):
    #
    #     care_fss_body_parts = set()
    #     tiles = []
    #     statistic_text = ""
    #     bold_statistic_text = []
    #     mobilize_suffix = "to lengthen tissues which show signs of shortening"
    #
    #     sideless_body_parts = [b.body_part_location for b in body_part_sides]
    #     sideless_body_parts = list(set(sideless_body_parts))
    #
    #     for body_part_side in sideless_body_parts:
    #         tile_1 = TriggerTile()
    #         body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts([body_part_side], 0)
    #         if len(body_part_text_1) == 0:
    #             body_part_text_1 = "PRIME MOVER"
    #         if body_part_text_1 not in care_fss_body_parts:
    #             care_fss_body_parts.add(body_part_text_1)
    #             tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #             tile_1.description = mobilize_suffix
    #             bold_1 = BoldText()
    #             bold_1.text = "Foam Roll & Static Stretch"
    #             bold_1.color = LegendColor.warning_x_light
    #             tile_1.bold_text.append(bold_1)
    #             tile_1.statistic_text = statistic_text
    #             tile_1.bold_statistic_text = bold_statistic_text
    #             #tile_1.trigger_type = t.trigger_type
    #             tiles.append(tile_1)
    #     return tiles

    # def get_short_non_adhesions_trigger_tiles(self, body_part_sides):
    #
    #     care_fss_body_parts = set()
    #     tiles = []
    #     statistic_text = ""
    #     bold_statistic_text = []
    #     mobilize_suffix = "to inhibit muscle overactivity causing biomechanical imbalances"
    #     sideless_body_parts = [b.body_part_location for b in body_part_sides]
    #     sideless_body_parts = list(set(sideless_body_parts))
    #
    #     for body_part_side in sideless_body_parts:
    #         tile_1 = TriggerTile()
    #         body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts([body_part_side], 0)
    #         if len(body_part_text_1) == 0:
    #             body_part_text_1 = "PRIME MOVER"
    #         if body_part_text_1 not in care_fss_body_parts:
    #             care_fss_body_parts.add(body_part_text_1)
    #             tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #             tile_1.description = mobilize_suffix
    #             bold_1 = BoldText()
    #             bold_1.text = "Foam Roll & Static Stretch"
    #             bold_1.color = LegendColor.warning_light
    #             tile_1.bold_text.append(bold_1)
    #             tile_1.statistic_text = statistic_text
    #             tile_1.bold_statistic_text = bold_statistic_text
    #             # tile_1.trigger_type = t.trigger_type
    #             tiles.append(tile_1)
    #     return tiles

    # def get_weak_underactive_trigger_tiles(self, body_part_sides):
    #
    #     care_fss_body_parts = set()
    #     tiles = []
    #     statistic_text = ""
    #     bold_statistic_text = []
    #     mobilize_suffix = "to improve strength deficiencies indicated by your biomechanics"
    #     sideless_body_parts = [b.body_part_location for b in body_part_sides]
    #     sideless_body_parts = list(set(sideless_body_parts))
    #
    #     for body_part_side in sideless_body_parts:
    #         tile_1 = TriggerTile()
    #         body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts([body_part_side], 0)
    #         if len(body_part_text_1) == 0:
    #             body_part_text_1 = "PRIME MOVER"
    #         if body_part_text_1 not in care_fss_body_parts:
    #             care_fss_body_parts.add(body_part_text_1)
    #             tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #             tile_1.description = mobilize_suffix
    #             bold_1 = BoldText()
    #             bold_1.text = "Foam Roll & Static Stretch"
    #             bold_1.color = LegendColor.splash_light
    #             tile_1.bold_text.append(bold_1)
    #             tile_1.statistic_text = statistic_text
    #             tile_1.bold_statistic_text = bold_statistic_text
    #             # tile_1.trigger_type = t.trigger_type
    #             tiles.append(tile_1)
    #     return tiles

    # def get_muscle_spasm_trigger_tiles(self, body_part_sides):
    #
    #     care_fss_body_parts = set()
    #     tiles = []
    #     statistic_text = ""
    #     bold_statistic_text = []
    #     #mobilize_suffix = "to improve tissue range of motion"
    #     sideless_body_parts = [b.body_part_location for b in body_part_sides]
    #     sideless_body_parts = list(set(sideless_body_parts))
    #
    #     body_part_text_string = ''
    #
    #     first_time = True
    #
    #     tile_1 = TriggerTile()
    #
    #     for body_part_side in sideless_body_parts:
    #
    #         body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts([body_part_side], 0)
    #         if len(body_part_text_1) == 0:
    #             body_part_text_1 = "PRIME MOVER"
    #         if body_part_text_1 not in care_fss_body_parts:
    #
    #             if not first_time:
    #                 body_part_text_string += ", "
    #
    #             body_part_text_string += body_part_text_1
    #
    #             care_fss_body_parts.add(body_part_text_1)
    #
    #     #tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #     tile_1.text = "Muscle Spasm"
    #     tile_1.description = body_part_text_string
    #     # bold_1 = BoldText()
    #     # bold_1.text = "Foam Roll & Static Stretch"
    #     # bold_1.color = LegendColor.warning_x_light
    #     # tile_1.bold_text.append(bold_1)
    #     # tile_1.statistic_text = statistic_text
    #     # tile_1.bold_statistic_text = bold_statistic_text
    #     ## tile_1.trigger_type = t.trigger_type
    #     tiles.append(tile_1)
    #     return tiles

    # def get_compensation_trigger_tiles(self, body_part_sides):
    #
    #     care_fss_body_parts = set()
    #     tiles = []
    #     statistic_text = ""
    #     bold_statistic_text = []
    #     mobilize_suffix = "to address asymmetric stress resulting from compensations"
    #     sideless_body_parts = [b.body_part_location for b in body_part_sides]
    #     sideless_body_parts = list(set(sideless_body_parts))
    #
    #     for body_part_side in sideless_body_parts:
    #         tile_1 = TriggerTile()
    #         body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts([body_part_side], 0)
    #         if len(body_part_text_1) == 0:
    #             body_part_text_1 = "PRIME MOVER"
    #         if body_part_text_1 not in care_fss_body_parts:
    #             care_fss_body_parts.add(body_part_text_1)
    #             tile_1.text = "Foam Roll & Stretch your " + body_part_text_1
    #             tile_1.description = mobilize_suffix
    #             bold_2 = BoldText()
    #             bold_2.text = "Foam Roll & Stretch"
    #             bold_2.color = LegendColor.splash_x_light
    #             tile_1.bold_text.append(bold_2)
    #             tile_1.statistic_text = statistic_text
    #             tile_1.bold_statistic_text = bold_statistic_text
    #             #tile_1.trigger_type = t.trigger_type
    #             tiles.append(tile_1)
    #
    #     return tiles

    # def get_inflamed_trigger_tiles(self, body_part_sides):
    #
    #     care_fss_body_parts = set()
    #     tiles = []
    #     statistic_text = ""
    #     bold_statistic_text = []
    #     mobilize_suffix = "to minimize compensations resulting from likely inflammation"
    #     sideless_body_parts = [b.body_part_location for b in body_part_sides]
    #     sideless_body_parts = list(set(sideless_body_parts))
    #
    #     for body_part_side in sideless_body_parts:
    #         tile_1 = TriggerTile()
    #         body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts([body_part_side], 0)
    #         if len(body_part_text_1) == 0:
    #             body_part_text_1 = "PRIME MOVER"
    #         if body_part_text_1 not in care_fss_body_parts:
    #             care_fss_body_parts.add(body_part_text_1)
    #             tile_1.text = "Foam Roll & Stretch your " + body_part_text_1
    #             tile_1.description = mobilize_suffix
    #             bold_2 = BoldText()
    #             bold_2.text = "Foam Roll & Stretch"
    #             bold_2.color = LegendColor.warning_light
    #             tile_1.bold_text.append(bold_2)
    #             tile_1.statistic_text = statistic_text
    #             tile_1.bold_statistic_text = bold_statistic_text
    #             #tile_1.trigger_type = t.trigger_type
    #             tiles.append(tile_1)
    #
    #     return tiles

    # def get_excessive_strain_trigger_tiles(self, body_part_sides, is_moderate):
    #
    #     care_fss_body_parts = set()
    #     tiles = []
    #     statistic_text = ""
    #     bold_statistic_text = []
    #     mobilize_suffix = "to increase blood flow & expedite healing after unaccustomed loading"
    #     sideless_body_parts = [b.body_part_location for b in body_part_sides]
    #     sideless_body_parts = list(set(sideless_body_parts))
    #
    #     for body_part_side in sideless_body_parts:
    #         tile_1 = TriggerTile()
    #         body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts([body_part_side], 0)
    #         if len(body_part_text_1) == 0:
    #             body_part_text_1 = "PRIME MOVER"
    #         if body_part_text_1 not in care_fss_body_parts:
    #             care_fss_body_parts.add(body_part_text_1)
    #             tile_1.text = "Mobilize muscles used in " + body_part_text_1
    #             tile_1.description = mobilize_suffix
    #             bold_2 = BoldText()
    #             bold_2.text = "Mobilize muscles"
    #             if is_moderate:
    #                 bold_2.color = LegendColor.splash_xx_light
    #             else:
    #                 bold_2.color = LegendColor.splash_light
    #             tile_1.bold_text.append(bold_2)
    #             tile_1.statistic_text = statistic_text
    #             tile_1.bold_statistic_text = bold_statistic_text
    #             # tile_1.trigger_type = t.trigger_type
    #             tiles.append(tile_1)
    #
    #     return tiles

    # def get_trigger_tiles(self, trigger_list):
    #
    #     body_part_factory = BodyPartFactory()
    #
    #     tiles = []
    #
    #     #trigger_7_flagged = False
    #
    #     # trigger_7_list = [t for t in trigger_list if t.trigger_type == TriggerType.hist_sore_less_30]
    #     #
    #     # filtered_trigger_list = [t for t in trigger_list if t.trigger_type != TriggerType.hist_sore_less_30]
    #
    #     for f in trigger_list:
    #         if f.severity is None:
    #             f.severity = 0
    #
    #     filtered_trigger_list = sorted(trigger_list, key=lambda x: (x.priority, x.severity), reverse=True)
    #
    #     recovery_body_parts = set()
    #     prevention_fr_body_parts = set()
    #     prevention_strenghten_body_parts = set()
    #     prevention_heat_body_parts = set()
    #     care_fss_body_parts = set()
    #     care_fs_body_parts = set()
    #     care_ice_body_parts = set()
    #     pain_body_part_severity = {}
    #     soreness_body_part_severity = {}
    #
    #     for t in filtered_trigger_list:
    #
    #         if t.trigger_type == TriggerType.movement_error_apt_asymmetry:
    #             mobilize_suffix = "to address asymmetric stress accumulated in training"
    #             statistic_text = ""
    #             bold_statistic_text = []
    #             if t.metric is not None:
    #                 statistic_text = str(t.metric) + "% Hip Asymmetry"
    #                 bold_stat_text = BoldText()
    #                 bold_stat_text.text = str(t.metric) + "%"
    #                 bold_statistic_text.append(bold_stat_text)
    #             tile_1 = TriggerTile()
    #             body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.overactive_tight_first, 0)
    #             if len(body_part_text_1) == 0:
    #                 body_part_text_1 = "PRIME MOVER"
    #             if body_part_text_1 not in recovery_body_parts:
    #                 recovery_body_parts.add(body_part_text_1)
    #                 tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #                 tile_1.description = mobilize_suffix
    #                 bold_1 = BoldText()
    #                 bold_1.text = "Foam Roll & Static Stretch"
    #                 bold_1.color = LegendColor.warning_light
    #                 tile_1.bold_text.append(bold_1)
    #                 tile_1.statistic_text = statistic_text
    #                 tile_1.bold_statistic_text = bold_statistic_text
    #                 tile_1.trigger_type = t.trigger_type
    #                 tiles.append(tile_1)
    #
    #             tile_2 = TriggerTile()
    #             body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(t.elevated_stress, 0)
    #             if len(body_part_text_2) == 0:
    #                 body_part_text_2 = "PRIME MOVER"
    #             if body_part_text_2 not in recovery_body_parts:
    #                 recovery_body_parts.add(body_part_text_1)
    #                 tile_2.text = "Foam Roll & Stretch your " + body_part_text_2
    #                 tile_2.description = mobilize_suffix
    #                 bold_2 = BoldText()
    #                 bold_2.text = "Foam Roll & Stretch"
    #                 bold_2.color = LegendColor.splash_x_light
    #                 tile_2.bold_text.append(bold_2)
    #                 tile_2.statistic_text = statistic_text
    #                 tile_2.bold_statistic_text = bold_statistic_text
    #                 tile_2.trigger_type = t.trigger_type
    #                 tiles.append(tile_2)
    #
    #         elif t.trigger_type == TriggerType.movement_error_historic_apt_asymmetry:
    #             mobilize_suffix = "to correct imbalances causing Pelvic Tilt Asymmetry"
    #             statistic_text = ""
    #             bold_statistic_text = []
    #             if t.metric is not None:
    #                 statistic_text = "Hip Asymmetry Trend"
    #                 bold_stat_text = BoldText()
    #                 bold_stat_text.text = "Hip"
    #                 bold_statistic_text.append(bold_stat_text)
    #             tile_1 = TriggerTile()
    #             body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.overactive_tight_first, 0)
    #             if len(body_part_text_1) == 0:
    #                 body_part_text_1 = "PRIME MOVER"
    #             if body_part_text_1 not in recovery_body_parts:
    #                 recovery_body_parts.add(body_part_text_1)
    #                 tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #                 tile_1.description = mobilize_suffix
    #                 bold_1 = BoldText()
    #                 bold_1.text = "Foam Roll & Static Stretch"
    #                 bold_1.color = LegendColor.warning_light
    #                 tile_1.bold_text.append(bold_1)
    #                 tile_1.statistic_text = statistic_text
    #                 tile_1.bold_statistic_text = bold_statistic_text
    #                 tile_1.trigger_type = t.trigger_type
    #                 tiles.append(tile_1)
    #
    #             tile_2 = TriggerTile()
    #             body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(t.underactive_weak, 0)
    #             if len(body_part_text_2) == 0:
    #                 body_part_text_2 = "PRIME MOVER"
    #             if body_part_text_2 not in recovery_body_parts:
    #                 recovery_body_parts.add(body_part_text_1)
    #                 tile_2.text = "Strengthen your " + body_part_text_2
    #                 tile_2.description = mobilize_suffix
    #                 bold_2 = BoldText()
    #                 bold_2.text = "Strengthen"
    #                 bold_2.color = LegendColor.splash_light
    #                 tile_2.bold_text.append(bold_2)
    #                 tile_2.statistic_text = statistic_text
    #                 tile_2.bold_statistic_text = bold_statistic_text
    #                 tile_2.trigger_type = t.trigger_type
    #                 tiles.append(tile_2)
    #
    #         elif t.trigger_type == TriggerType.hist_sore_greater_30:
    #             mobilize_suffix = "to correct observed imbalances"
    #             statistic_text = ""
    #             bold_statistic_text = []
    #             if t.source_first_reported_date_time is not None:
    #                 weeks = ceil((self.event_date_time.date() - t.source_first_reported_date_time.date()).days / 7)
    #                 if weeks > 1:
    #                     statistic_text = str(weeks) + " Weeks of Soreness"
    #                 else:
    #                     weeks = 1
    #                     statistic_text = str(weeks) + " Week of Soreness"
    #                 bold_stat_text = BoldText()
    #                 bold_stat_text.text = str(weeks)
    #                 bold_statistic_text.append(bold_stat_text)
    #             tile_1 = TriggerTile()
    #             body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.agonists, 0)
    #             if len(body_part_text_1) == 0:
    #                 body_part_text_1 = "PRIME MOVER"
    #             if body_part_text_1 not in prevention_fr_body_parts:
    #                 prevention_fr_body_parts.add(body_part_text_1)
    #                 tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #                 tile_1.description = mobilize_suffix
    #                 bold_1 = BoldText()
    #                 bold_1.text = "Foam Roll & Static Stretch"
    #                 bold_1.color = LegendColor.warning_light
    #                 tile_1.bold_text.append(bold_1)
    #                 tile_1.statistic_text = statistic_text
    #                 tile_1.bold_statistic_text = bold_statistic_text
    #                 tile_1.trigger_type = t.trigger_type
    #                 tiles.append(tile_1)
    #             tile_2 = TriggerTile()
    #             a_s_2 = []
    #             a_s_2.extend(t.antagonists)
    #             #a_s_2.extend(t.synergists)
    #             body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(a_s_2, 0)
    #             if body_part_text_2 not in prevention_strenghten_body_parts:
    #                 prevention_strenghten_body_parts.add(body_part_text_2)
    #                 tile_2.text = "Strengthen your " + body_part_text_2
    #                 tile_2.description = mobilize_suffix
    #                 bold_2 = BoldText()
    #                 bold_2.text = "Strengthen"
    #                 bold_2.color = LegendColor.splash_light
    #                 tile_2.bold_text.append(bold_2)
    #                 tile_2.statistic_text = statistic_text
    #                 tile_2.bold_statistic_text = bold_statistic_text
    #                 tile_2.trigger_type = t.trigger_type
    #                 tiles.append(tile_2)
    #             tile_3 = TriggerTile()
    #             body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
    #             if body_part_text_3 not in prevention_heat_body_parts:
    #                 prevention_heat_body_parts.add(body_part_text_3)
    #                 tile_3.text = "Heat your " + body_part_text_3 + " before training"
    #                 tile_3.description = "to temporarily improve mobility & increase the efficacy of stretching"
    #                 bold_3 = BoldText()
    #                 bold_3.text = "Heat"
    #                 bold_3.color = LegendColor.warning_light
    #                 tile_3.bold_text.append(bold_3)
    #                 tile_3.statistic_text = statistic_text
    #                 tile_3.bold_statistic_text = bold_statistic_text
    #                 tile_3.trigger_type = t.trigger_type
    #                 tiles.append(tile_3)
    #
    #         elif t.trigger_type == TriggerType.hist_pain:
    #             statistic_text = ""
    #             bold_statistic_text = []
    #             if t.source_first_reported_date_time is not None:
    #                 weeks = ceil((self.event_date_time.date() - t.source_first_reported_date_time.date()).days / 7)
    #                 if weeks > 1:
    #                     statistic_text = str(weeks) + " Weeks of Pain"
    #                 else:
    #                     weeks = 1
    #                     statistic_text = str(weeks) + " Week of Pain"
    #                 bold_stat_text = BoldText()
    #                 bold_stat_text.text = str(weeks)
    #                 bold_statistic_text.append(bold_stat_text)
    #             if not body_part_factory.is_joint(t.body_part):
    #                 mobilize_suffix = "to correct imbalances exacerbating your pain"
    #                 tile_1 = TriggerTile()
    #                 body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.agonists, 0)
    #                 if len(body_part_text_1) == 0:
    #                     body_part_text_1 = "PRIME MOVER"
    #                 if body_part_text_1 not in prevention_fr_body_parts:
    #                     prevention_fr_body_parts.add(body_part_text_1)
    #                     tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #                     tile_1.description = mobilize_suffix
    #                     bold_1 = BoldText()
    #                     bold_1.text = "Foam Roll & Static Stretch"
    #                     bold_1.color = LegendColor.error_light
    #                     tile_1.bold_text.append(bold_1)
    #                     tile_1.statistic_text = statistic_text
    #                     tile_1.bold_statistic_text = bold_statistic_text
    #                     tile_1.trigger_type = t.trigger_type
    #                     tiles.append(tile_1)
    #
    #                 tile_2 = TriggerTile()
    #                 a_s_2 = []
    #                 a_s_2.extend(t.antagonists)
    #                 #a_s_2.extend(t.synergists)
    #                 body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(a_s_2, 0)
    #                 if body_part_text_2 not in prevention_strenghten_body_parts:
    #                     prevention_strenghten_body_parts.add(body_part_text_2)
    #                     bold_2 = BoldText()
    #                     bold_2.text = "Strengthen"
    #                     bold_2.color = LegendColor.splash_light
    #                     tile_2.bold_text.append(bold_2)
    #                     tile_2.text = "Strengthen your " + body_part_text_2
    #                     tile_2.description = mobilize_suffix
    #                     tile_2.statistic_text = statistic_text
    #                     tile_2.bold_statistic_text = bold_statistic_text
    #                     tile_2.trigger_type = t.trigger_type
    #                     tiles.append(tile_2)
    #
    #                 tile_3 = TriggerTile()
    #                 body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
    #                 if body_part_text_3 not in prevention_heat_body_parts:
    #                     prevention_heat_body_parts.add(body_part_text_3)
    #                     tile_3.text = "Heat your " + body_part_text_3 + " before training"
    #                     tile_3.description = "to temporarily improve mobility & increase the efficacy of stretching"
    #                     bold_3 = BoldText()
    #                     bold_3.text = "Heat"
    #                     bold_3.color = LegendColor.error_light
    #                     tile_3.bold_text.append(bold_3)
    #                     tile_3.statistic_text = statistic_text
    #                     tile_3.bold_statistic_text = bold_statistic_text
    #                     tile_3.trigger_type = t.trigger_type
    #                     tiles.append(tile_3)
    #
    #             else:
    #                 mobilize_suffix = "to correct imbalances exacerbating your pain"
    #                 a_a = []
    #                 a_a.extend(t.agonists)
    #                 a_a.extend(t.antagonists)
    #                 tile_1 = TriggerTile()
    #                 body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(a_a, 0)
    #                 if len(body_part_text_1) == 0:
    #                     body_part_text_1 = "PRIME MOVER"
    #                 if body_part_text_1 not in prevention_fr_body_parts:
    #                     prevention_fr_body_parts.add(body_part_text_1)
    #                     tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #                     tile_1.description = mobilize_suffix
    #                     bold_1 = BoldText()
    #                     bold_1.text = "Foam Roll & Static Stretch"
    #                     bold_1.color = LegendColor.splash_light
    #                     tile_1.bold_text.append(bold_1)
    #                     tile_1.statistic_text = statistic_text
    #                     tile_1.bold_statistic_text = bold_statistic_text
    #                     tile_1.trigger_type = t.trigger_type
    #                     tiles.append(tile_1)
    #
    #                 tile_2 = TriggerTile()
    #                 body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(a_a, 0)
    #                 if body_part_text_2 not in prevention_strenghten_body_parts:
    #                     prevention_strenghten_body_parts.add(body_part_text_2)
    #                     tile_2.text = "Strengthen your " + body_part_text_2
    #                     tile_2.description = mobilize_suffix
    #                     bold_2 = BoldText()
    #                     bold_2.text = "Strengthen"
    #                     bold_2.color = LegendColor.splash_light
    #                     tile_2.bold_text.append(bold_2)
    #                     tile_2.statistic_text = statistic_text
    #                     tile_2.bold_statistic_text = bold_statistic_text
    #                     tile_2.trigger_type = t.trigger_type
    #                     tiles.append(tile_2)
    #                 tile_3 = TriggerTile()
    #                 body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
    #                 if body_part_text_3 not in prevention_heat_body_parts:
    #                     prevention_heat_body_parts.add(body_part_text_3)
    #                     tile_3.text = "Heat your " + body_part_text_3 + " before training"
    #                     tile_3.description = "to temporarily improve mobility & increase the efficacy of stretching"
    #                     bold_3 = BoldText()
    #                     bold_3.text = "Heat"
    #                     bold_3.color = LegendColor.error_light
    #                     tile_3.bold_text.append(bold_3)
    #                     tile_3.statistic_text = statistic_text
    #                     tile_3.bold_statistic_text = bold_statistic_text
    #                     tile_3.trigger_type = t.trigger_type
    #                     tiles.append(tile_3)
    #
    #         elif t.trigger_type in [TriggerType.no_hist_pain_pain_today_severity_1_2,
    #                                 TriggerType.no_hist_pain_pain_today_high_severity_3_5,
    #                                 TriggerType.hist_pain_pain_today_severity_1_2,
    #                                 TriggerType.hist_pain_pain_today_severity_3_5]:
    #             statistic_text = ""
    #             bold_statistic_text = []
    #             if t.severity is not None:
    #                 if t.body_part.body_part_location not in pain_body_part_severity:
    #                     pain_body_part_severity[t.body_part.body_part_location] = t.severity
    #                 else:
    #                     pain_body_part_severity[t.body_part.body_part_location] = max(t.severity, pain_body_part_severity[t.body_part.body_part_location])
    #                 statistic_text = self.get_severity_descriptor(pain_body_part_severity[t.body_part.body_part_location]) + " Pain Reported"
    #                 bold_stat_text = BoldText()
    #                 bold_stat_text.text = self.get_severity_descriptor(pain_body_part_severity[t.body_part.body_part_location])
    #                 bold_statistic_text.append(bold_stat_text)
    #             if not body_part_factory.is_joint(t.body_part):
    #                 mobilize_suffix = "to minimize effects of compensations resulting from pain"
    #                 tile_1 = TriggerTile()
    #                 body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.agonists, 0)
    #                 if len(body_part_text_1) == 0:
    #                     body_part_text_1 = "PRIME MOVER"
    #                 if body_part_text_1 not in care_fss_body_parts:
    #                     care_fss_body_parts.add(body_part_text_1)
    #                     tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #                     tile_1.description = mobilize_suffix
    #                     bold_1 = BoldText()
    #                     bold_1.text = "Foam Roll & Static Stretch"
    #                     bold_1.color = LegendColor.error_light
    #                     tile_1.bold_text.append(bold_1)
    #                     tile_1.statistic_text = statistic_text
    #                     tile_1.bold_statistic_text = bold_statistic_text
    #                     tile_1.trigger_type = t.trigger_type
    #                     tiles.append(tile_1)
    #
    #                 tile_2 = TriggerTile()
    #                 body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(t.synergists, 0)
    #                 if body_part_text_2 not in care_fs_body_parts:
    #                     care_fs_body_parts.add(body_part_text_2)
    #                     bold_2 = BoldText()
    #                     bold_2.text = "Foam Roll & Stretch"
    #                     bold_2.color = LegendColor.splash_x_light
    #                     tile_2.bold_text.append(bold_2)
    #                     tile_2.text = "Foam Roll & Stretch your " + body_part_text_2
    #                     tile_2.description = mobilize_suffix
    #                     tile_2.statistic_text = statistic_text
    #                     tile_2.bold_statistic_text = bold_statistic_text
    #                     tile_2.trigger_type = t.trigger_type
    #                     tiles.append(tile_2)
    #
    #                 tile_3 = TriggerTile()
    #                 body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
    #                 if body_part_text_3 not in care_ice_body_parts:
    #                     care_ice_body_parts.add(body_part_text_3)
    #                     tile_3.text = "Ice your " + body_part_text_3 + " after training"
    #                     tile_3.description = "to reduce inflammation and muscle damage"
    #                     bold_3 = BoldText()
    #                     bold_3.text = "Ice"
    #                     bold_3.color = LegendColor.error_light
    #                     tile_3.bold_text.append(bold_3)
    #                     tile_3.statistic_text = statistic_text
    #                     tile_3.bold_statistic_text = bold_statistic_text
    #                     tile_3.trigger_type = t.trigger_type
    #                     tiles.append(tile_3)
    #             else:
    #                 mobilize_suffix = "to minimize effects of compensations resulting from pain"
    #                 tile_1 = TriggerTile()
    #                 body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.synergists, 0)
    #                 if len(body_part_text_1) == 0:
    #                     body_part_text_1 = "PRIME MOVER"
    #                 if body_part_text_1 not in care_fss_body_parts:
    #                     care_fss_body_parts.add(body_part_text_1)
    #                     tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #                     tile_1.description = mobilize_suffix
    #                     bold_1 = BoldText()
    #                     bold_1.text = "Foam Roll & Static Stretch"
    #                     bold_1.color = LegendColor.splash_x_light
    #                     tile_1.bold_text.append(bold_1)
    #                     tile_1.statistic_text = statistic_text
    #                     tile_1.bold_statistic_text = bold_statistic_text
    #                     tile_1.trigger_type = t.trigger_type
    #                     tiles.append(tile_1)
    #
    #                 tile_2 = TriggerTile()
    #                 body_part_text_2, is_plural_1 = self.get_title_text_for_body_parts([t.body_part], 0)
    #                 if len(body_part_text_2) == 0:
    #                     body_part_text_2 = "PRIME MOVER"
    #                 if body_part_text_2 not in care_ice_body_parts:
    #                     care_ice_body_parts.add(body_part_text_2)
    #                     tile_2.text = "Ice your " + body_part_text_2 + " after training"
    #                     tile_2.description = "to reduce inflammation and tissue damage"
    #                     bold_2 = BoldText()
    #                     bold_2.text = "Ice"
    #                     bold_2.color = LegendColor.error_light
    #                     tile_2.bold_text.append(bold_2)
    #                     tile_2.statistic_text = statistic_text
    #                     tile_2.bold_statistic_text = bold_statistic_text
    #                     tile_2.trigger_type = t.trigger_type
    #                     tiles.append(tile_2)
    #
    #         elif t.trigger_type in [TriggerType.sore_today_doms,
    #                                 TriggerType.hist_sore_less_30_sore_today,
    #                                 TriggerType.hist_sore_greater_30_sore_today]:
    #
    #             statistic_text = ""
    #             bold_statistic_text = []
    #             if t.severity is not None:
    #                 if t.body_part.body_part_location not in soreness_body_part_severity:
    #                     soreness_body_part_severity[t.body_part.body_part_location] = t.severity
    #                 else:
    #                     soreness_body_part_severity[t.body_part.body_part_location] = max(t.severity, soreness_body_part_severity[t.body_part.body_part_location])
    #                 statistic_text = self.get_severity_descriptor( soreness_body_part_severity[t.body_part.body_part_location]) + " Soreness Reported"
    #                 bold_stat_text = BoldText()
    #                 bold_stat_text.text = self.get_severity_descriptor(soreness_body_part_severity[t.body_part.body_part_location])
    #                 bold_statistic_text.append(bold_stat_text)
    #             mobilize_suffix = "to reduce soreness & restore range of motion"
    #             tile_1 = TriggerTile()
    #             body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.agonists, 0)
    #             if len(body_part_text_1) == 0:
    #                 body_part_text_1 = "PRIME MOVER"
    #             if body_part_text_1 not in care_fss_body_parts:
    #                 care_fss_body_parts.add(body_part_text_1)
    #                 tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
    #                 tile_1.description = mobilize_suffix
    #                 bold_1 = BoldText()
    #                 bold_1.text = "Foam Roll & Static Stretch"
    #                 bold_1.color = LegendColor.warning_light
    #                 tile_1.bold_text.append(bold_1)
    #                 tile_1.statistic_text = statistic_text
    #                 tile_1.bold_statistic_text = bold_statistic_text
    #                 tile_1.trigger_type = t.trigger_type
    #                 tiles.append(tile_1)
    #
    #             tile_2 = TriggerTile()
    #             body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(t.synergists, 0)
    #             if len(body_part_text_2) == 0:
    #                 body_part_text_2 = "PRIME MOVER"
    #             if body_part_text_2 not in care_fs_body_parts:
    #                 care_fs_body_parts.add(body_part_text_2)
    #                 tile_2.text = "Foam Roll & Stretch your " + body_part_text_2
    #                 tile_2.description = "to minimize effects of compensations resulting from soreness"
    #                 bold_2 = BoldText()
    #                 bold_2.text = "Foam Roll & Stretch"
    #                 bold_2.color = LegendColor.splash_x_light
    #                 tile_2.bold_text.append(bold_2)
    #                 tile_2.statistic_text = statistic_text
    #                 tile_2.bold_statistic_text = bold_statistic_text
    #                 tile_2.trigger_type = t.trigger_type
    #                 tiles.append(tile_2)
    #
    #             tile_3 = TriggerTile()
    #             body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
    #             if body_part_text_3 not in care_ice_body_parts:
    #                 care_ice_body_parts.add(body_part_text_3)
    #                 tile_3.text = "Ice your " + body_part_text_3 + " after training"
    #                 tile_3.description = "to reduce inflammation and muscle damage"
    #                 bold_3 = BoldText()
    #                 bold_3.text = "Ice"
    #                 bold_3.color = LegendColor.warning_light
    #                 tile_3.bold_text.append(bold_3)
    #                 tile_3.statistic_text = statistic_text
    #                 tile_3.bold_statistic_text = bold_statistic_text
    #                 tile_3.trigger_type = t.trigger_type
    #                 tiles.append(tile_3)
    #
    #         elif t.trigger_type == TriggerType.high_volume_intensity:
    #
    #             mobilize_suffix = "to increase blood flow & expedite tissue regeneration"
    #             statistic_text = ""
    #             bold_statistic_text = []
    #             if t.metric is not None:
    #                 statistic_text = str(t.metric) + "% of Max Workload"
    #                 bold_stat_text = BoldText()
    #                 bold_stat_text.text = str(t.metric) + "%"
    #                 bold_statistic_text.append(bold_stat_text)
    #             sport = SportName(t.sport_name).get_display_name()
    #             tile_1 = TriggerTile()
    #             tile_1.sport_name = t.sport_name
    #             tile_1.text = "Mobilize muscles used in " + sport
    #             tile_1.description = mobilize_suffix
    #             bold_1 = BoldText()
    #             bold_1.text = "Mobilize"
    #             bold_1.color = LegendColor.splash_x_light
    #             tile_1.bold_text.append(bold_1)
    #             tile_1.statistic_text = statistic_text
    #             tile_1.bold_statistic_text = bold_statistic_text
    #             tile_1.trigger_type = t.trigger_type
    #             tile_2 = TriggerTile()
    #             tile_2.sport_name = t.sport_name
    #             tile_2.text = "Cold Water Bath your lower body"
    #             tile_2.description = "to reduce inflammation & muscle damage"
    #             bold_2 = BoldText()
    #             bold_2.text = "Cold Water Bath"
    #             bold_2.color = LegendColor.splash_x_light
    #             tile_2.bold_text.append(bold_2)
    #             tile_2.statistic_text = statistic_text
    #             tile_2.bold_statistic_text = bold_statistic_text
    #             tile_2.trigger_type = t.trigger_type
    #             # tile_3 = TriggerTile()
    #             # tile_3.text = "Dynamic Stretch muscles stressed in " + sport
    #             # tile_3.description = "to increase blood flow & retain mobility"
    #             # bold_3 = BoldText()
    #             # bold_3.text = "Dynamic Stretch"
    #             # tile_3.bold_text.append(bold_3)
    #             # tile_3.statistic_text = statistic_text
    #             # tile_3.trigger_type = t.trigger_type
    #             tiles.append(tile_1)
    #             tiles.append(tile_2)
    #             #tiles.append(tile_3)
    #
    #     return tiles

    # def get_severity_descriptor(self, severity):
    #
    #     if severity <= 2:
    #         return "Mild"
    #     elif 2 < severity <= 3:
    #         return "Moderate"
    #     else:
    #         return "Severe"




