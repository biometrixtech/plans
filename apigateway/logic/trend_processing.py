from models.athlete_trend import TrendDashboardCategory, PlanAlert, Trend, TrendCategory, TrendData, \
    FirstTimeExperienceElement, CategoryFirstTimeExperienceModal
from models.styles import BoldText, LegendColor, VisualizationType
from models.trigger import TriggerType, Trigger
from models.chart_data import PreventionChartData, PersonalizedRecoveryChartData, CareTodayChartData
from models.insights import InsightType
from models.body_parts import BodyPartFactory
from models.soreness_base import BodyPartSide, BodyPartLocation
from models.athlete_trend import TriggerTile
from models.sport import SportName
from logic.goal_focus_text_generator import RecoveryTextGenerator
from math import ceil


class TrendProcessor(object):
    def __init__(self, trigger_list, event_date_time, athlete_trend_categories=None, dashboard_categories=None):
        self.athlete_trend_categories = [] if athlete_trend_categories is None else athlete_trend_categories
        self.trigger_list = trigger_list
        self.dashboard_categories = [] if dashboard_categories is None else dashboard_categories
        self.event_date_time = event_date_time
        self.initialize_trend_categories()

    def get_antagonists_syngergists(self, triggers, use_agonists=False):

        antagonists = []
        synergists = []

        body_part_factory = BodyPartFactory()

        for t in triggers:
            if body_part_factory.is_joint(t.body_part) and use_agonists:
                antagonists.extend(t.agonists)
            antagonists.extend(t.antagonists)
            synergists.extend(t.synergists)

        return antagonists, synergists

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
            self.athlete_trend_categories.append(care_category)

        prevention_index = next(
            (i for i, x in enumerate(self.athlete_trend_categories) if InsightType.prevention == x.insight_type), -1)

        if prevention_index == -1:
            prevention_category = self.create_prevention_category()
            self.athlete_trend_categories.append(prevention_category)

        recovery_index = next(
            (i for i, x in enumerate(self.athlete_trend_categories) if InsightType.personalized_recovery == x.insight_type), -1)

        if recovery_index == -1:
            personalized_recovery_category = self.create_personalized_recovery_category()
            self.athlete_trend_categories.append(personalized_recovery_category)

    def get_care_trend(self, category_index):

        care_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                                 x.visualization_type == VisualizationType.care_today), -1)
        if care_index == -1:
            care_trend = self.create_care_trend()
            self.athlete_trend_categories[category_index].trends.append(care_trend)
            care_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[care_index]

    def set_care_trend(self, category_index, care_trend):

        index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.care_today), -1)

        if index == -1:
            self.athlete_trend_categories[category_index].trends.append(care_trend)
        else:
            self.athlete_trend_categories[category_index].trends[index] = care_trend

    def get_prevention_trend(self, category_index):

        limitation_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                                 x.visualization_type == VisualizationType.prevention), -1)
        if limitation_index == -1:
            limitation_trend = self.create_prevention_trend()
            self.athlete_trend_categories[category_index].trends.append(limitation_trend)
            limitation_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[limitation_index]

    def set_prevention_trend(self, category_index, prevention_trend):

        index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                      x.visualization_type == VisualizationType.prevention), -1)

        if index == -1:
            self.athlete_trend_categories[category_index].trends.append(prevention_trend)
        else:
            self.athlete_trend_categories[category_index].trends[index] = prevention_trend

    def get_personalized_recovery_trend(self, category_index):

        muscle_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.personalized_recovery), -1)
        if muscle_index == -1:
            muscle_trend = self.create_personalized_recovery_trend()
            self.athlete_trend_categories[category_index].trends.append(muscle_trend)
            muscle_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[muscle_index]

    def set_personalized_recovery_trend(self, category_index, recovery_trend):

        muscle_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.personalized_recovery), -1)

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

    def create_personalized_recovery_category(self):
        trend_category = TrendCategory(InsightType.personalized_recovery)
        trend_category.title = "Personalized Recovery"
        trend_category.first_time_experience = True

        muscle_trend = self.create_personalized_recovery_trend()
        trend_category.trends.append(muscle_trend)

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
        daily_trend.visualization_type = VisualizationType.care_today
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
        limitation_trend.visualization_type = VisualizationType.prevention
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
        muscle_trend.visualization_type = VisualizationType.personalized_recovery
        muscle_trend.visible = False
        muscle_trend.first_time_experience = True
        return muscle_trend

    def process_triggers(self):

        personalized_recovery_category_index = self.get_category_index(InsightType.personalized_recovery)
        prevention_category_index = self.get_category_index(InsightType.prevention)
        care_category_index = self.get_category_index(InsightType.care)
        self.set_personalized_recovery(personalized_recovery_category_index)
        self.set_prevention(prevention_category_index)
        self.set_daily_care(care_category_index)

        for c in range(0, len(self.athlete_trend_categories)):
            if len(self.athlete_trend_categories[c].trends) > 0:
                none_dates = list(t for t in self.athlete_trend_categories[c].trends if t.last_date_time is None)
                full_dates = list(t for t in self.athlete_trend_categories[c].trends if t.last_date_time is not None)

                self.athlete_trend_categories[c].trends = []

                new_modified_trigger_count = 0
                plan_alert_short_title = ""

                if len(full_dates) > 0:
                    full_dates = sorted(full_dates, key=lambda x: (x.last_date_time, x.priority), reverse=True)
                    if len(plan_alert_short_title) == 0:
                        plan_alert_short_title = full_dates[0].plan_alert_short_title
                    for f in full_dates:
                        new_modified_trigger_count += len(f.triggers)

                self.athlete_trend_categories[c].trends.extend(full_dates)
                self.athlete_trend_categories[c].trends.extend(none_dates)

                visible_trends = list(t for t in self.athlete_trend_categories[c].trends if t.visible)

                trends_visible = False

                if len(visible_trends) > 0:

                    trends_visible = True

                    # sorted_trends = sorted(visible_trends, key=lambda v: v.last_date_time, reverse=True)
                    #
                    # if (len(self.athlete_trend_categories[c].plan_alerts) > 0 and
                    #         (self.athlete_trend_categories[c].plan_alerts[0].cleared_date_time is None)):
                    #
                    #     # clear this out so we can update the plan alert
                    #     self.athlete_trend_categories[c].plan_alerts = []
                    #
                    # if (len(self.athlete_trend_categories[c].plan_alerts) == 0 or
                    #     (self.athlete_trend_categories[c].plan_alerts[0].cleared_date_time is not None
                    #      and sorted_trends[0].last_date_time > self.athlete_trend_categories[c].plan_alerts[0].cleared_date_time)):
                    #
                    #     # clear this out so we can update the plan alert
                    #     self.athlete_trend_categories[c].plan_alerts = []
                    #
                    #     # plans alert text
                    #     plan_alert = self.get_plan_alert(new_modified_trigger_count, plan_alert_short_title,
                    #                                      personalized_recovery_category_index, visible_trends)
                    #     self.athlete_trend_categories[c].plan_alerts.append(plan_alert)

                    # Now create dashboard category card
                    self.dashboard_categories = []

                    # trend_dashboard_category = None
                    #
                    # if sorted_trends[0].visualization_type == VisualizationType.personalized_recovery:
                    #     trend_dashboard_category = self.get_over_under_active_dashboard_card(c, sorted_trends[0])
                    #
                    # elif sorted_trends[0].visualization_type == VisualizationType.prevention:
                    #     trend_dashboard_category = self.get_functional_limitation_dashboard_card(c, sorted_trends[0])
                    #
                    # if trend_dashboard_category is not None:
                    #     trend_dashboard_category.unread_alerts = (
                    #                 len(self.athlete_trend_categories[c].plan_alerts) > 0)
                    #     self.dashboard_categories.append(trend_dashboard_category)
                else:
                    self.athlete_trend_categories[c].plan_alerts = []

                self.athlete_trend_categories[c].visible = trends_visible

    def get_plan_alert(self, new_modified_trigger_count, plan_alert_short_title, trend_category_index, visible_trends):

        #header_text = str(new_modified_trigger_count) + " Tissue Related Insights"
        #header_text = "New Tissue Related Insights"
        header_text = "Signs of Imbalance"
        body_text = "Signs of " + plan_alert_short_title
        if len(visible_trends) > 1:
            # we're bringing this back later
            # if len(visible_trends) == 2:
            #     body_text += " and " + str(len(visible_trends) - 1) + " other meaningful insight"
            # else:
            #     body_text += " and " + str(len(visible_trends) - 1) + " other meaningful insights"
            body_text += " and other insights"
        body_text += " in your data. Tap to view more."
        plan_alert = PlanAlert(self.athlete_trend_categories[trend_category_index].insight_type)
        plan_alert.title = header_text
        plan_alert.text = body_text
        bold_text_1 = BoldText()
        bold_text_1.text = plan_alert_short_title
        plan_alert.bold_text.append(bold_text_1)
        return plan_alert

    def get_title_text_for_body_parts(self, body_parts, side, use_plural=True):

        is_plural = False

        text_generator = RecoveryTextGenerator()
        body_part_factory = BodyPartFactory()

        converted_body_parts = []

        for b in body_parts:
            body_part = body_part_factory.get_body_part(b)
            if body_part.treatment_priority is None:
                body_part.treatment_priority = 99
            converted_body_parts.append(body_part)

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

    def get_latest_trigger_date_time(self, triggers):

        if len(triggers) > 0:

            last_created_date_time = None

            # turns out we are only interested when a new body part is added or when a historic soreness status changes
            created_triggers = sorted(triggers, key=lambda x: x.created_date_time, reverse=True)
            #modified_triggers = sorted(triggers, key=lambda x: x.modified_date_time, reverse=True)
            #status_changed_triggers = [t for t in triggers if t.source_date_time is not None]
            if len(created_triggers) > 0:
                status_triggers = sorted(triggers, key=lambda x: x.created_date_time, reverse=True)
                created_date_time = status_triggers[0].created_date_time

                last_created_date_time = created_triggers[0].created_date_time
            #last_modified_date_time = modified_triggers[0].modified_date_time

            #if status_changed_date_time is not None:
            #    return status_changed_date_time
            #elif last_modified_date_time is not None:
            #    return max(last_modified_date_time, last_created_date_time)
            #else:
            return last_created_date_time

        else:
            return None

    def set_personalized_recovery(self, category_index):

        # triggers_7 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.hist_sore_less_30)
        # for t in triggers_7:
        #     t.priority = 3

        triggers_load = list(t for t in self.trigger_list if t.trigger_type == TriggerType.high_volume_intensity)
        for t in triggers_load:
            t.priority = 1

        triggers_110 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.movement_error_apt_asymmetry)
        for t in triggers_110:
            t.priority = 4

        # since we're reverse sorting, 2 is a higher priority than 1

        if len(triggers_110) > 0 or len(triggers_load) > 0:

            #antagonists_7, synergists_7 = self.get_antagonists_syngergists(triggers_7)

            trend = self.get_personalized_recovery_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.personalized_recovery
            trend_data.add_visualization_data()
            recovery_data = PersonalizedRecoveryChartData()
            #recovery_data.tight.extend([t.body_part for t in triggers_7])
            #recovery_data.elevated_stress.extend([s for s in synergists_7])

            for t in triggers_110:
                recovery_data.tight.extend([a for a in t.overactive_tight_first])
                recovery_data.elevated_stress.extend([s for s in t.elevated_stress])

            for t in triggers_load:
                recovery_data.elevated_stress.extend([a for a in t.agonists])
                recovery_data.elevated_stress.extend([s for s in t.antagonists])

            recovery_data.remove_duplicates()
            trend_data.data = [recovery_data]

            all_triggers = []
            #all_triggers.extend(triggers_7)
            all_triggers.extend(triggers_110)
            all_triggers.extend(triggers_load)

            trend.trigger_tiles = self.get_trigger_tiles(all_triggers)

            # rank triggers
            # sorted_triggers = sorted(all_triggers, key=lambda x: (x.created_date_time, x.priority), reverse=True)
            #
            # text_generator = RecoveryTextGenerator()
            # body_part_factory = BodyPartFactory()
            #
            # top_candidates = list(s for s in sorted_triggers if s.created_date_time == sorted_triggers[0].created_date_time and s.priority == sorted_triggers[0].priority)
            #
            # trend.top_priority_trigger, is_body_part_plural = self.get_highest_priority_body_part_from_triggers(body_part_factory, top_candidates)
            #
            # if is_body_part_plural:
            #     side = 0
            # else:
            #     side = trend.top_priority_trigger.body_part.side
            #
            # if is_body_part_plural and trend.top_priority_trigger.priority == 2:
            #     if trend.top_priority_trigger.body_part is not None:
            #         body_part_text = text_generator.get_body_part_text_plural(
            #             trend.top_priority_trigger.body_part.body_part_location, None)
            #     else:
            #         body_part_text = ""
            # else:
            #     #body_part_text = text_generator.get_body_part_text(trend.top_priority_trigger.body_part.body_part_location, None)
            #     body_part_text = ""
            # body_part_text = body_part_text.title()
            #
            # if trend.top_priority_trigger.priority == 1:
            #     title_body_part_text, is_title_plural = self.get_title_text_for_body_parts(trend.top_priority_trigger.synergists, side)
            #     trend_data.title = "Elevated strain on " + title_body_part_text
            #     trend.plan_alert_short_title = "elevated strain on " + title_body_part_text
            #     clean_title_body_part_text = title_body_part_text.replace('&', 'and')
            #     body_text = ("Signs of " + body_part_text + " overactivity in your soreness data suggest that supporting tissues like the " + clean_title_body_part_text +
            #                 " are experiencing elevated levels of strain which can lead to tissue fatigue and strength imbalances that affect performance and increase injury risk.")
            #     #trend.dashboard_body_part, trend.dashboard_body_part_text = self.get_title_body_part_and_text(trend.top_priority_trigger.synergists, side)
            # else:
            #     title_body_part_text, is_title_plural = self.get_title_text_for_body_parts(trend.top_priority_trigger.antagonists, side)
            #     title_body_part_text_not_plural, is_title_plural_false = self.get_title_text_for_body_parts(trend.top_priority_trigger.antagonists, side, use_plural=False)
            #     trend_data.title = title_body_part_text + " may lack strength"
            #     #trend.plan_alert_short_title = title_body_part_text + " weakness"
            #     trend.plan_alert_short_title = title_body_part_text_not_plural + " weakness"
            #     clean_title_body_part_text = title_body_part_text.replace('&','and')
            #
            #     if is_title_plural:
            #         for_a_weak_phrase = "for weak"
            #     else:
            #         for_a_weak_phrase = "for a weak"
            #
            #     body_text = ("Patterns in your soreness data suggest that your " + body_part_text + " may actually be overactive due to a chronic over-compensation " + for_a_weak_phrase + " "
            #                  + clean_title_body_part_text + ".  This dysfunction could exacerbate movement imbalances and elevate your risk of chronic injury.")
            #
            #     #trend.dashboard_body_part, trend.dashboard_body_part_text = self.get_title_body_part_and_text(recovery_data.tight, side)
            #
            # trend_data.text = body_text
            #
            # bold_text_3 = BoldText()
            # bold_text_3.text = body_part_text
            # bold_text_3.color = LegendColor.warning_light
            # trend_data.bold_text.append(bold_text_3)
            #
            # if trend.top_priority_trigger.priority == 1:
            #
            #     bold_text_4 = BoldText()
            #     bold_text_4.text = clean_title_body_part_text
            #     bold_text_4.color = LegendColor.splash_light
            #
            #     trend_data.bold_text.append(bold_text_4)
            #
            # else:
            #
            #     bold_text_4 = BoldText()
            #     bold_text_4.text = clean_title_body_part_text
            #     bold_text_4.color = LegendColor.splash_x_light
            #
            #     trend_data.bold_text.append(bold_text_4)

            trend.trend_data = trend_data

            trend.visible = True
            trend.priority = 0

            trend.triggers = all_triggers

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)

            self.set_personalized_recovery_trend(category_index, trend)

        else:
            trend = self.create_personalized_recovery_trend()
            self.set_personalized_recovery_trend(category_index, trend)

    def get_over_under_active_dashboard_card(self, category_index, trend):
        trend_dashboard_category = TrendDashboardCategory(self.athlete_trend_categories[category_index].insight_type)
        trend_dashboard_category.title = "Signs of Imbalance"
        if trend.top_priority_trigger.priority == 1:
            trend_dashboard_category.text = "Elevated strain on"
        else:
            trend_dashboard_category.text = "Potential weakness in"
        trend_dashboard_category.body_part = trend.dashboard_body_part
        trend_dashboard_category.body_part_text = trend.dashboard_body_part_text
        trend_dashboard_category.color = LegendColor.splash_x_light
        body_part_set = set()
        body_part_location_set = set()
        for t in self.trigger_list:
            if t.body_part is not None:
                body_part_set.add(t.body_part)  # not sure we need this
                body_part_location_set.add(t.body_part.body_part_location)
        if len(body_part_location_set) > 1:
            trend_dashboard_category.body_part_text += " and more..."
        return trend_dashboard_category

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
                trigger_dictionary[t.body_part] = body_part.treatment_priority

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

    def get_highest_priority_body_part_from_triggers(self, body_part_factory, top_candidates):

        if len(top_candidates) == 1:
            if top_candidates[0].body_part is not None:
                return top_candidates[0], top_candidates[0].body_part.side == 0
            else:
                return top_candidates[0], True
        else:
            for t in top_candidates:
                if t.body_part is not None:
                    body_part = body_part_factory.get_body_part(t.body_part)
                    t.body_part_priority = body_part.treatment_priority

            # still could have a tie (two body parts)
            sorted_triggers = sorted(top_candidates, key=lambda x: x.body_part_priority)

            if len(sorted_triggers) > 1:
                if sorted_triggers[0].body_part_priority == sorted_triggers[1].body_part_priority:
                    return sorted_triggers[0], True
                else:
                    if sorted_triggers[0].body_part is not None:
                        return sorted_triggers[0], sorted_triggers[0].body_part.side == 0
                    else:
                        return sorted_triggers[0], True
            else:
                if sorted_triggers[0].body_part is not None:
                    return sorted_triggers[0], sorted_triggers[0].body_part.side == 0
                else:
                    return sorted_triggers[0], True

    def get_title_body_part_and_text(self, body_parts, side):

        text_generator = RecoveryTextGenerator()
        body_part_factory = BodyPartFactory()

        converted_body_parts = []

        for b in body_parts:
            body_part = body_part_factory.get_body_part(b)
            converted_body_parts.append(body_part)

        sorted_body_parts = sorted(converted_body_parts, key=lambda x: x.treatment_priority)

        if side == 0:
            body_part_side = BodyPartSide(sorted_body_parts[0].location, None)
            body_part_text = text_generator.get_body_part_text_plural(sorted_body_parts[0].location, None).title()
        else:
            if sorted_body_parts[0].bilateral:
                body_part_side = BodyPartSide(sorted_body_parts[0].location, side)
                body_part_text = text_generator.get_body_part_text(sorted_body_parts[0].location, side).title()
            else:
                body_part_side = BodyPartSide(sorted_body_parts[0].location, None)
                body_part_text = text_generator.get_body_part_text(sorted_body_parts[0].location, None).title()

        return body_part_side, body_part_text

    def set_daily_care(self, category_index):

        pain_triggers = [TriggerType.no_hist_pain_pain_today_severity_1_2,
                         TriggerType.no_hist_pain_pain_today_high_severity_3_5,
                         TriggerType.hist_pain_pain_today_severity_1_2,
                         TriggerType.hist_pain_pain_today_severity_3_5]
        triggers_pain = list(t for t in self.trigger_list if t.trigger_type in pain_triggers)
        for t in triggers_pain:
            t.priority = 3

        sore_triggers = [TriggerType.sore_today_doms,
                         TriggerType.hist_sore_less_30_sore_today,
                         TriggerType.hist_sore_greater_30_sore_today]

        triggers_sore = list(t for t in self.trigger_list if t.trigger_type in sore_triggers)
        for t in triggers_sore:
            t.priority = 2

        if len(triggers_pain) > 0 or len(triggers_sore) > 0:

            trend = self.get_care_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.care_today
            trend_data.add_visualization_data()
            care_data = CareTodayChartData()

            body_part_factory = BodyPartFactory()

            for t in triggers_pain:
                care_data.pain.extend([t.body_part])
                if body_part_factory.is_joint(t.body_part):
                    care_data.elevated_stress.extend([a for a in t.agonists])
                    care_data.elevated_stress.extend([a for a in t.antagonists])
                    care_data.elevated_stress.extend([a for a in t.synergists])
                else:
                    care_data.elevated_stress.extend([s for s in t.agonists])  # should be prime movers
                    care_data.elevated_stress.extend([s for s in t.synergists])

            for t in triggers_sore:
                care_data.soreness.extend([t.body_part])
                care_data.elevated_stress.extend([s for s in t.synergists])

            care_data.remove_duplicates()
            trend_data.data = [care_data]

            all_triggers = []
            all_triggers.extend(triggers_pain)
            all_triggers.extend(triggers_sore)

            trend.trigger_tiles = self.get_trigger_tiles(all_triggers)

            # rank triggers
            #sorted_triggers = sorted(all_triggers, key=lambda x: (x.created_date_time, x.priority), reverse=True)

            trend.triggers = all_triggers

            # text_generator = RecoveryTextGenerator()
            # body_part_factory = BodyPartFactory()
            #
            # top_candidates = list(
            #     s for s in sorted_triggers if s.created_date_time == sorted_triggers[0].created_date_time)
            #
            # trend.top_priority_trigger, is_body_part_plural = self.get_highest_priority_body_part_from_triggers(
            #     body_part_factory, top_candidates)
            #
            # if is_body_part_plural:
            #     side = 0
            # else:
            #     side = trend.top_priority_trigger.body_part.side
            #
            # if trend.top_priority_trigger.body_part is not None:
            #     body_part_text = text_generator.get_body_part_text(trend.top_priority_trigger.body_part.body_part_location,
            #                                                        None)
            # else:
            #     body_part_text = ""
            #
            # body_part_text = body_part_text.title()
            #
            # title_body_part_text, is_title_plural = self.get_title_text_for_body_parts(
            #     trend.top_priority_trigger.synergists, side)
            # trend_data.title = "Elevated strain on " + title_body_part_text
            # trend.plan_alert_short_title = "elevated strain on " + title_body_part_text
            # clean_title_body_part_text = title_body_part_text.replace('&', 'and')
            # body_text = (
            #             "Athletes struggling with recurring " + body_part_text + " pain often develop misalignments that over-stress their " + clean_title_body_part_text +
            #             ". Without proactive measures, this can lead to accumulated micro-trauma in the tissues and new areas of pain or injury over time.")
            # # trend.dashboard_body_part, trend.dashboard_body_part_text = self.get_title_body_part_and_text(
            # #     trend.top_priority_trigger.synergists, side)
            #
            # bold_text_3 = BoldText()
            # bold_text_3.text = body_part_text
            # bold_text_3.color = LegendColor.error_light
            # trend_data.bold_text.append(bold_text_3)
            # trend_data.text = body_text
            #
            # bold_text_4 = BoldText()
            # bold_text_4.text = clean_title_body_part_text
            # bold_text_4.color = LegendColor.splash_x_light
            # trend_data.bold_text.append(bold_text_4)

            trend.trend_data = trend_data
            trend.visible = True
            trend.priority = 1

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)

            self.set_care_trend(category_index, trend)

        else:
            trend = self.create_care_trend()
            self.set_care_trend(category_index, trend)

    def set_prevention(self, category_index):

        triggers_19 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.hist_sore_greater_30)
        for t in triggers_19:
            t.priority = 2

        triggers_16 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.hist_pain)
        for t in triggers_16:
            t.priority = 3

        trigger_111 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.movement_error_historic_apt_asymmetry)
        for t in trigger_111:
            t.priority = 4

        # since we're reverse sorting, 2 is a higher priority than 1

        if len(triggers_19) > 0 or len(triggers_16) > 0 or len(trigger_111) > 0:

            antagonists_19, synergists_19 = self.get_antagonists_syngergists(triggers_19)

            trend = self.get_prevention_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.prevention
            trend_data.add_visualization_data()
            prevention_data = PreventionChartData()

            prevention_data.overactive.extend([t.body_part for t in triggers_19])
            prevention_data.weak.extend([a for a in antagonists_19])

            body_part_factory = BodyPartFactory()

            for t in triggers_16:
                if body_part_factory.is_joint(t.body_part):
                    prevention_data.weak.extend([a for a in t.agonists])
                    prevention_data.weak.extend([a for a in t.antagonists])
                    prevention_data.pain.extend([t.body_part])
                else:
                    prevention_data.pain.extend([t.body_part])
                    prevention_data.weak.extend([a for a in t.antagonists])

            for t in trigger_111:
                prevention_data.overactive.extend([o for o in t.overactive_tight_first])
                prevention_data.weak.extend([u for u in t.underactive_weak])

            prevention_data.remove_duplicates()
            trend_data.data = [prevention_data]

            all_triggers = []
            all_triggers.extend(triggers_19)
            all_triggers.extend(triggers_16)
            all_triggers.extend(trigger_111)

            trend.trigger_tiles = self.get_trigger_tiles(all_triggers)

            # rank triggers
            #sorted_triggers = sorted(all_triggers, key=lambda x: (x.created_date_time, x.priority), reverse=True)

            trend.triggers = all_triggers

            # # rank triggers
            # sorted_triggers = sorted(all_triggers, key=lambda x: x.created_date_time, reverse=True)
            #
            # text_generator = RecoveryTextGenerator()
            # body_part_factory = BodyPartFactory()
            #
            # top_candidates = list(
            #     s for s in sorted_triggers if s.created_date_time == sorted_triggers[0].created_date_time)
            #
            # trend.top_priority_trigger, is_body_part_plural = self.get_highest_priority_body_part_from_triggers(
            #     body_part_factory, top_candidates)
            #
            # if is_body_part_plural:
            #     side = 0
            # else:
            #     side = trend.top_priority_trigger.body_part.side
            #
            # body_part_text = text_generator.get_body_part_text(trend.top_priority_trigger.body_part.body_part_location, None)
            # body_part_text = body_part_text.title()
            #
            # title_body_part_text, is_title_plural = self.get_title_text_for_body_parts(trend.top_priority_trigger.synergists, side)
            # trend_data.title = "Elevated strain on " + title_body_part_text
            # trend.plan_alert_short_title = "elevated strain on " + title_body_part_text
            # clean_title_body_part_text = title_body_part_text.replace('&','and')
            # body_text = ("Athletes struggling with recurring " + body_part_text + " pain often develop misalignments that over-stress their "+ clean_title_body_part_text +
            #              ". Without proactive measures, this can lead to accumulated micro-trauma in the tissues and new areas of pain or injury over time.")
            # # trend.dashboard_body_part, trend.dashboard_body_part_text = self.get_title_body_part_and_text(
            # #     trend.top_priority_trigger.synergists, side)
            #
            # bold_text_3 = BoldText()
            # bold_text_3.text = body_part_text
            # bold_text_3.color = LegendColor.error_light
            # trend_data.bold_text.append(bold_text_3)
            # trend_data.text = body_text
            #
            # bold_text_4 = BoldText()
            # bold_text_4.text = clean_title_body_part_text
            # bold_text_4.color = LegendColor.splash_x_light
            # trend_data.bold_text.append(bold_text_4)

            trend.trend_data = trend_data
            trend.visible = True
            trend.priority = 1

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)

            self.set_prevention_trend(category_index, trend)

        else:
            trend = self.create_prevention_trend()
            self.set_prevention_trend(category_index, trend)

    def get_functional_limitation_dashboard_card(self, category_index, trend):
        trend_dashboard_category = TrendDashboardCategory(self.athlete_trend_categories[category_index].insight_type)
        trend_dashboard_category.title = "Signs of Imbalance"
        trend_dashboard_category.text = "Elevated strain on"
        trend_dashboard_category.color = LegendColor.warning_light
        trend_dashboard_category.body_part = trend.dashboard_body_part
        trend_dashboard_category.body_part_text = trend.dashboard_body_part_text
        body_part_set = set()
        body_part_location_set = set()
        for t in self.trigger_list:
            if t.body_part is not None:
                body_part_set.add(t.body_part)  # not sure we need this
                body_part_location_set.add(t.body_part.body_part_location)
        if len(body_part_location_set) > 1:
            trend_dashboard_category.body_part_text += " and more..."
        return trend_dashboard_category

    def get_trigger_tiles(self, trigger_list):

        body_part_factory = BodyPartFactory()

        tiles = []

        #trigger_7_flagged = False

        # trigger_7_list = [t for t in trigger_list if t.trigger_type == TriggerType.hist_sore_less_30]
        #
        # filtered_trigger_list = [t for t in trigger_list if t.trigger_type != TriggerType.hist_sore_less_30]

        for f in trigger_list:
            if f.severity is None:
                f.severity = 0

        filtered_trigger_list = sorted(trigger_list, key=lambda x: (x.priority, x.severity), reverse=True)

        recovery_body_parts = set()
        prevention_fr_body_parts = set()
        prevention_strenghten_body_parts = set()
        prevention_heat_body_parts = set()
        care_fss_body_parts = set()
        care_fs_body_parts = set()
        care_ice_body_parts = set()
        pain_body_part_severity = {}
        soreness_body_part_severity = {}

        for t in filtered_trigger_list:
            # if t.trigger_type == TriggerType.hist_sore_less_30:
            #     if not trigger_7_flagged:
            #         statistic_text = ""
            #         if t.source_first_reported_date_time is not None:
            #             weeks = ceil((self.event_date_time.date() - t.source_first_reported_date_time.date()).days / 7)
            #             if weeks > 1:
            #                 statistic_text = str(weeks) + " Weeks of Soreness"
            #             else:
            #                 statistic_text = str(weeks) + " Week of Soreness"
            #         tile_1 = TriggerTile()
            #         tile_1.text = "Increase care for chronically sore tissues to promote positive training adaptation"
            #         bold_1 = BoldText()
            #         bold_1.text = "Increase care"
            #         tile_1.bold_text.append(bold_1)
            #         tile_1.statistic_text = statistic_text
            #         tiles.append(tile_1)
            #         trigger_7_flagged = True

            if t.trigger_type == TriggerType.movement_error_apt_asymmetry:
                mobilize_suffix = "to address asymmetric stress accumulated in training"
                statistic_text = ""
                bold_statistic_text = []
                if t.metric is not None:
                    statistic_text = str(t.metric) + "% Hip Asymmetry"
                    bold_stat_text = BoldText()
                    bold_stat_text.text = str(t.metric) + "%"
                    bold_statistic_text.append(bold_stat_text)
                tile_1 = TriggerTile()
                body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.overactive_tight_first, 0)
                if len(body_part_text_1) == 0:
                    body_part_text_1 = "PRIME MOVER"
                if body_part_text_1 not in recovery_body_parts:
                    recovery_body_parts.add(body_part_text_1)
                    tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
                    tile_1.description = mobilize_suffix
                    bold_1 = BoldText()
                    bold_1.text = "Foam Roll & Static Stretch"
                    bold_1.color = LegendColor.warning_light
                    tile_1.bold_text.append(bold_1)
                    tile_1.statistic_text = statistic_text
                    tile_1.bold_statistic_text = bold_statistic_text
                    tile_1.trigger_type = t.trigger_type
                    tiles.append(tile_1)

                tile_2 = TriggerTile()
                body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(t.elevated_stress, 0)
                if len(body_part_text_2) == 0:
                    body_part_text_2 = "PRIME MOVER"
                if body_part_text_2 not in recovery_body_parts:
                    recovery_body_parts.add(body_part_text_1)
                    tile_2.text = "Foam Roll & Stretch your " + body_part_text_2
                    tile_2.description = mobilize_suffix
                    bold_2 = BoldText()
                    bold_2.text = "Foam Roll & Stretch"
                    bold_2.color = LegendColor.splash_x_light
                    tile_2.bold_text.append(bold_2)
                    tile_2.statistic_text = statistic_text
                    tile_2.bold_statistic_text = bold_statistic_text
                    tile_2.trigger_type = t.trigger_type
                    tiles.append(tile_2)

            elif t.trigger_type == TriggerType.movement_error_historic_apt_asymmetry:
                mobilize_suffix = "to correct imbalances causing Pelvic Tilt Asymmetry"
                statistic_text = ""
                bold_statistic_text = []
                if t.metric is not None:
                    statistic_text = str(t.metric) + "% Hip Asymmetry Trend"
                    bold_stat_text = BoldText()
                    bold_stat_text.text = str(t.metric) + "%"
                    bold_statistic_text.append(bold_stat_text)
                tile_1 = TriggerTile()
                body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.overactive_tight_first, 0)
                if len(body_part_text_1) == 0:
                    body_part_text_1 = "PRIME MOVER"
                if body_part_text_1 not in recovery_body_parts:
                    recovery_body_parts.add(body_part_text_1)
                    tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
                    tile_1.description = mobilize_suffix
                    bold_1 = BoldText()
                    bold_1.text = "Foam Roll & Static Stretch"
                    bold_1.color = LegendColor.warning_light
                    tile_1.bold_text.append(bold_1)
                    tile_1.statistic_text = statistic_text
                    tile_1.bold_statistic_text = bold_statistic_text
                    tile_1.trigger_type = t.trigger_type
                    tiles.append(tile_1)

                tile_2 = TriggerTile()
                body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(t.underactive_weak, 0)
                if len(body_part_text_2) == 0:
                    body_part_text_2 = "PRIME MOVER"
                if body_part_text_2 not in recovery_body_parts:
                    recovery_body_parts.add(body_part_text_1)
                    tile_2.text = "Strengthen your " + body_part_text_2
                    tile_2.description = mobilize_suffix
                    bold_2 = BoldText()
                    bold_2.text = "Strengthen"
                    bold_2.color = LegendColor.splash_light
                    tile_2.bold_text.append(bold_2)
                    tile_2.statistic_text = statistic_text
                    tile_2.bold_statistic_text = bold_statistic_text
                    tile_2.trigger_type = t.trigger_type
                    tiles.append(tile_2)

            elif t.trigger_type == TriggerType.hist_sore_greater_30:
                mobilize_suffix = "to correct observed imbalances"
                statistic_text = ""
                bold_statistic_text = []
                if t.source_first_reported_date_time is not None:
                    weeks = ceil((self.event_date_time.date() - t.source_first_reported_date_time.date()).days / 7)
                    if weeks > 1:
                        statistic_text = str(weeks) + " Weeks of Soreness"
                    else:
                        weeks = 1
                        statistic_text = str(weeks) + " Week of Soreness"
                    bold_stat_text = BoldText()
                    bold_stat_text.text = str(weeks)
                    bold_statistic_text.append(bold_stat_text)
                tile_1 = TriggerTile()
                body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.agonists, 0)
                if len(body_part_text_1) == 0:
                    body_part_text_1 = "PRIME MOVER"
                if body_part_text_1 not in prevention_fr_body_parts:
                    prevention_fr_body_parts.add(body_part_text_1)
                    tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
                    tile_1.description = mobilize_suffix
                    bold_1 = BoldText()
                    bold_1.text = "Foam Roll & Static Stretch"
                    bold_1.color = LegendColor.warning_light
                    tile_1.bold_text.append(bold_1)
                    tile_1.statistic_text = statistic_text
                    tile_1.bold_statistic_text = bold_statistic_text
                    tile_1.trigger_type = t.trigger_type
                    tiles.append(tile_1)
                tile_2 = TriggerTile()
                a_s_2 = []
                a_s_2.extend(t.antagonists)
                #a_s_2.extend(t.synergists)
                body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(a_s_2, 0)
                if body_part_text_2 not in prevention_strenghten_body_parts:
                    prevention_strenghten_body_parts.add(body_part_text_2)
                    tile_2.text = "Strengthen your " + body_part_text_2
                    tile_2.description = mobilize_suffix
                    bold_2 = BoldText()
                    bold_2.text = "Strengthen"
                    bold_2.color = LegendColor.splash_light
                    tile_2.bold_text.append(bold_2)
                    tile_2.statistic_text = statistic_text
                    tile_2.bold_statistic_text = bold_statistic_text
                    tile_2.trigger_type = t.trigger_type
                    tiles.append(tile_2)
                tile_3 = TriggerTile()
                body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
                if body_part_text_3 not in prevention_heat_body_parts:
                    prevention_heat_body_parts.add(body_part_text_3)
                    tile_3.text = "Heat your " + body_part_text_3 + " before training"
                    tile_3.description = "to temporarily improve mobility & increase the efficacy of stretching"
                    bold_3 = BoldText()
                    bold_3.text = "Heat"
                    bold_3.color = LegendColor.warning_light
                    tile_3.bold_text.append(bold_3)
                    tile_3.statistic_text = statistic_text
                    tile_3.bold_statistic_text = bold_statistic_text
                    tile_3.trigger_type = t.trigger_type
                    tiles.append(tile_3)

            elif t.trigger_type == TriggerType.hist_pain:
                statistic_text = ""
                bold_statistic_text = []
                if t.source_first_reported_date_time is not None:
                    weeks = ceil((self.event_date_time.date() - t.source_first_reported_date_time.date()).days / 7)
                    if weeks > 1:
                        statistic_text = str(weeks) + " Weeks of Pain"
                    else:
                        weeks = 1
                        statistic_text = str(weeks) + " Week of Pain"
                    bold_stat_text = BoldText()
                    bold_stat_text.text = str(weeks)
                    bold_statistic_text.append(bold_stat_text)
                if not body_part_factory.is_joint(t.body_part):
                    mobilize_suffix = "to correct imbalances exacerbating your pain"
                    tile_1 = TriggerTile()
                    body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.agonists, 0)
                    if len(body_part_text_1) == 0:
                        body_part_text_1 = "PRIME MOVER"
                    if body_part_text_1 not in prevention_fr_body_parts:
                        prevention_fr_body_parts.add(body_part_text_1)
                        tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
                        tile_1.description = mobilize_suffix
                        bold_1 = BoldText()
                        bold_1.text = "Foam Roll & Static Stretch"
                        bold_1.color = LegendColor.error_light
                        tile_1.bold_text.append(bold_1)
                        tile_1.statistic_text = statistic_text
                        tile_1.bold_statistic_text = bold_statistic_text
                        tile_1.trigger_type = t.trigger_type
                        tiles.append(tile_1)

                    tile_2 = TriggerTile()
                    a_s_2 = []
                    a_s_2.extend(t.antagonists)
                    #a_s_2.extend(t.synergists)
                    body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(a_s_2, 0)
                    if body_part_text_2 not in prevention_strenghten_body_parts:
                        prevention_strenghten_body_parts.add(body_part_text_2)
                        bold_2 = BoldText()
                        bold_2.text = "Strengthen"
                        bold_2.color = LegendColor.splash_light
                        tile_2.bold_text.append(bold_2)
                        tile_2.text = "Strengthen your " + body_part_text_2
                        tile_2.description = mobilize_suffix
                        tile_2.statistic_text = statistic_text
                        tile_2.bold_statistic_text = bold_statistic_text
                        tile_2.trigger_type = t.trigger_type
                        tiles.append(tile_2)

                    tile_3 = TriggerTile()
                    body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
                    if body_part_text_3 not in prevention_heat_body_parts:
                        prevention_heat_body_parts.add(body_part_text_3)
                        tile_3.text = "Heat your " + body_part_text_3 + " before training"
                        tile_3.description = "to temporarily improve mobility & increase the efficacy of stretching"
                        bold_3 = BoldText()
                        bold_3.text = "Heat"
                        bold_3.color = LegendColor.error_light
                        tile_3.bold_text.append(bold_3)
                        tile_3.statistic_text = statistic_text
                        tile_3.bold_statistic_text = bold_statistic_text
                        tile_3.trigger_type = t.trigger_type
                        tiles.append(tile_3)

                else:
                    mobilize_suffix = "to correct imbalances exacerbating your pain"
                    a_a = []
                    a_a.extend(t.agonists)
                    a_a.extend(t.antagonists)
                    tile_1 = TriggerTile()
                    body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(a_a, 0)
                    if len(body_part_text_1) == 0:
                        body_part_text_1 = "PRIME MOVER"
                    if body_part_text_1 not in prevention_fr_body_parts:
                        prevention_fr_body_parts.add(body_part_text_1)
                        tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
                        tile_1.description = mobilize_suffix
                        bold_1 = BoldText()
                        bold_1.text = "Foam Roll & Static Stretch"
                        bold_1.color = LegendColor.splash_light
                        tile_1.bold_text.append(bold_1)
                        tile_1.statistic_text = statistic_text
                        tile_1.bold_statistic_text = bold_statistic_text
                        tile_1.trigger_type = t.trigger_type
                        tiles.append(tile_1)

                    tile_2 = TriggerTile()
                    body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(a_a, 0)
                    if body_part_text_2 not in prevention_strenghten_body_parts:
                        prevention_strenghten_body_parts.add(body_part_text_2)
                        tile_2.text = "Strengthen your " + body_part_text_2
                        tile_2.description = mobilize_suffix
                        bold_2 = BoldText()
                        bold_2.text = "Strengthen"
                        bold_2.color = LegendColor.splash_light
                        tile_2.bold_text.append(bold_2)
                        tile_2.statistic_text = statistic_text
                        tile_2.bold_statistic_text = bold_statistic_text
                        tile_2.trigger_type = t.trigger_type
                        tiles.append(tile_2)
                    tile_3 = TriggerTile()
                    body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
                    if body_part_text_3 not in prevention_heat_body_parts:
                        prevention_heat_body_parts.add(body_part_text_3)
                        tile_3.text = "Heat your " + body_part_text_3 + " before training"
                        tile_3.description = "to temporarily improve mobility & increase the efficacy of stretching"
                        bold_3 = BoldText()
                        bold_3.text = "Heat"
                        bold_3.color = LegendColor.error_light
                        tile_3.bold_text.append(bold_3)
                        tile_3.statistic_text = statistic_text
                        tile_3.bold_statistic_text = bold_statistic_text
                        tile_3.trigger_type = t.trigger_type
                        tiles.append(tile_3)

            elif t.trigger_type in [TriggerType.no_hist_pain_pain_today_severity_1_2,
                                    TriggerType.no_hist_pain_pain_today_high_severity_3_5,
                                    TriggerType.hist_pain_pain_today_severity_1_2,
                                    TriggerType.hist_pain_pain_today_severity_3_5]:
                statistic_text = ""
                bold_statistic_text = []
                if t.severity is not None:
                    if t.body_part.body_part_location not in pain_body_part_severity:
                        pain_body_part_severity[t.body_part.body_part_location] = t.severity
                    else:
                        pain_body_part_severity[t.body_part.body_part_location] = max(t.severity, pain_body_part_severity[t.body_part.body_part_location])
                    statistic_text = self.get_severity_descriptor(pain_body_part_severity[t.body_part.body_part_location]) + " Pain Reported"
                    bold_stat_text = BoldText()
                    bold_stat_text.text = self.get_severity_descriptor(pain_body_part_severity[t.body_part.body_part_location])
                    bold_statistic_text.append(bold_stat_text)
                if not body_part_factory.is_joint(t.body_part):
                    mobilize_suffix = "to minimize effects of compensations resulting from pain"
                    tile_1 = TriggerTile()
                    body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.agonists, 0)
                    if len(body_part_text_1) == 0:
                        body_part_text_1 = "PRIME MOVER"
                    if body_part_text_1 not in care_fss_body_parts:
                        care_fss_body_parts.add(body_part_text_1)
                        tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
                        tile_1.description = mobilize_suffix
                        bold_1 = BoldText()
                        bold_1.text = "Foam Roll & Static Stretch"
                        bold_1.color = LegendColor.error_light
                        tile_1.bold_text.append(bold_1)
                        tile_1.statistic_text = statistic_text
                        tile_1.bold_statistic_text = bold_statistic_text
                        tile_1.trigger_type = t.trigger_type
                        tiles.append(tile_1)

                    tile_2 = TriggerTile()
                    body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(t.synergists, 0)
                    if body_part_text_2 not in care_fs_body_parts:
                        care_fs_body_parts.add(body_part_text_2)
                        bold_2 = BoldText()
                        bold_2.text = "Foam Roll & Stretch"
                        bold_2.color = LegendColor.splash_x_light
                        tile_2.bold_text.append(bold_2)
                        tile_2.text = "Foam Roll & Stretch your " + body_part_text_2
                        tile_2.description = mobilize_suffix
                        tile_2.statistic_text = statistic_text
                        tile_2.bold_statistic_text = bold_statistic_text
                        tile_2.trigger_type = t.trigger_type
                        tiles.append(tile_2)

                    tile_3 = TriggerTile()
                    body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
                    if body_part_text_3 not in care_ice_body_parts:
                        care_ice_body_parts.add(body_part_text_3)
                        tile_3.text = "Ice your " + body_part_text_3 + " after training"
                        tile_3.description = "to reduce inflammation and muscle damage"
                        bold_3 = BoldText()
                        bold_3.text = "Ice"
                        bold_3.color = LegendColor.error_light
                        tile_3.bold_text.append(bold_3)
                        tile_3.statistic_text = statistic_text
                        tile_3.bold_statistic_text = bold_statistic_text
                        tile_3.trigger_type = t.trigger_type
                        tiles.append(tile_3)
                else:
                    mobilize_suffix = "to minimize effects of compensations resulting from pain"
                    tile_1 = TriggerTile()
                    body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.synergists, 0)
                    if len(body_part_text_1) == 0:
                        body_part_text_1 = "PRIME MOVER"
                    if body_part_text_1 not in care_fss_body_parts:
                        care_fss_body_parts.add(body_part_text_1)
                        tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
                        tile_1.description = mobilize_suffix
                        bold_1 = BoldText()
                        bold_1.text = "Foam Roll & Static Stretch"
                        bold_1.color = LegendColor.splash_x_light
                        tile_1.bold_text.append(bold_1)
                        tile_1.statistic_text = statistic_text
                        tile_1.bold_statistic_text = bold_statistic_text
                        tile_1.trigger_type = t.trigger_type
                        tiles.append(tile_1)

                    tile_2 = TriggerTile()
                    body_part_text_2, is_plural_1 = self.get_title_text_for_body_parts([t.body_part], 0)
                    if len(body_part_text_2) == 0:
                        body_part_text_2 = "PRIME MOVER"
                    if body_part_text_2 not in care_ice_body_parts:
                        care_ice_body_parts.add(body_part_text_2)
                        tile_2.text = "Ice your " + body_part_text_2 + " after training"
                        tile_2.description = "to reduce inflammation and tissue damage"
                        bold_2 = BoldText()
                        bold_2.text = "Ice"
                        bold_2.color = LegendColor.error_light
                        tile_2.bold_text.append(bold_2)
                        tile_2.statistic_text = statistic_text
                        tile_2.bold_statistic_text = bold_statistic_text
                        tile_2.trigger_type = t.trigger_type
                        tiles.append(tile_2)

            elif t.trigger_type in [TriggerType.sore_today_doms,
                                    TriggerType.hist_sore_less_30_sore_today,
                                    TriggerType.hist_sore_greater_30_sore_today]:

                statistic_text = ""
                bold_statistic_text = []
                if t.severity is not None:
                    if t.body_part.body_part_location not in soreness_body_part_severity:
                        soreness_body_part_severity[t.body_part.body_part_location] = t.severity
                    else:
                        soreness_body_part_severity[t.body_part.body_part_location] = max(t.severity, soreness_body_part_severity[t.body_part.body_part_location])
                    statistic_text = self.get_severity_descriptor( soreness_body_part_severity[t.body_part.body_part_location]) + " Soreness Reported"
                    bold_stat_text = BoldText()
                    bold_stat_text.text = self.get_severity_descriptor(soreness_body_part_severity[t.body_part.body_part_location])
                    bold_statistic_text.append(bold_stat_text)
                mobilize_suffix = "to reduce soreness & restore range of motion"
                tile_1 = TriggerTile()
                body_part_text_1, is_plural_1 = self.get_title_text_for_body_parts(t.agonists, 0)
                if len(body_part_text_1) == 0:
                    body_part_text_1 = "PRIME MOVER"
                if body_part_text_1 not in care_fss_body_parts:
                    care_fss_body_parts.add(body_part_text_1)
                    tile_1.text = "Foam Roll & Static Stretch your " + body_part_text_1
                    tile_1.description = mobilize_suffix
                    bold_1 = BoldText()
                    bold_1.text = "Foam Roll & Static Stretch"
                    bold_1.color = LegendColor.warning_light
                    tile_1.bold_text.append(bold_1)
                    tile_1.statistic_text = statistic_text
                    tile_1.bold_statistic_text = bold_statistic_text
                    tile_1.trigger_type = t.trigger_type
                    tiles.append(tile_1)

                tile_2 = TriggerTile()
                body_part_text_2, is_plural_2 = self.get_title_text_for_body_parts(t.synergists, 0)
                if len(body_part_text_2) == 0:
                    body_part_text_2 = "PRIME MOVER"
                if body_part_text_2 not in care_fs_body_parts:
                    care_fs_body_parts.add(body_part_text_2)
                    tile_2.text = "Foam Roll & Stretch your " + body_part_text_2
                    tile_2.description = "to minimize effects of compensations resulting from soreness"
                    bold_2 = BoldText()
                    bold_2.text = "Foam Roll & Stretch"
                    bold_2.color = LegendColor.splash_x_light
                    tile_2.bold_text.append(bold_2)
                    tile_2.statistic_text = statistic_text
                    tile_2.bold_statistic_text = bold_statistic_text
                    tile_2.trigger_type = t.trigger_type
                    tiles.append(tile_2)

                tile_3 = TriggerTile()
                body_part_text_3, is_plural_3 = self.get_title_text_for_body_parts([t.body_part], 0)
                if body_part_text_3 not in care_ice_body_parts:
                    care_ice_body_parts.add(body_part_text_3)
                    tile_3.text = "Ice your " + body_part_text_3 + " after training"
                    tile_3.description = "to reduce inflammation and muscle damage"
                    bold_3 = BoldText()
                    bold_3.text = "Ice"
                    bold_3.color = LegendColor.warning_light
                    tile_3.bold_text.append(bold_3)
                    tile_3.statistic_text = statistic_text
                    tile_3.bold_statistic_text = bold_statistic_text
                    tile_3.trigger_type = t.trigger_type
                    tiles.append(tile_3)

            elif t.trigger_type == TriggerType.high_volume_intensity:

                mobilize_suffix = "to increase blood flow & expedite tissue regeneration"
                statistic_text = ""
                bold_statistic_text = []
                if t.metric is not None:
                    statistic_text = str(t.metric) + "% of Max Workload"
                    bold_stat_text = BoldText()
                    bold_stat_text.text = str(t.metric) + "%"
                    bold_statistic_text.append(bold_stat_text)
                sport = SportName(t.sport_name).get_display_name()
                tile_1 = TriggerTile()
                tile_1.sport_name = t.sport_name
                tile_1.text = "Mobilize muscles used in " + sport
                tile_1.description = mobilize_suffix
                bold_1 = BoldText()
                bold_1.text = "Mobilize"
                bold_1.color = LegendColor.splash_x_light
                tile_1.bold_text.append(bold_1)
                tile_1.statistic_text = statistic_text
                tile_1.bold_statistic_text = bold_statistic_text
                tile_1.trigger_type = t.trigger_type
                tile_2 = TriggerTile()
                tile_2.sport_name = t.sport_name
                tile_2.text = "Cold Water Bath your lower body"
                tile_2.description = "to reduce inflammation & muscle damage"
                bold_2 = BoldText()
                bold_2.text = "Cold Water Bath"
                bold_2.color = LegendColor.splash_x_light
                tile_2.bold_text.append(bold_2)
                tile_2.statistic_text = statistic_text
                tile_2.bold_statistic_text = bold_statistic_text
                tile_2.trigger_type = t.trigger_type
                # tile_3 = TriggerTile()
                # tile_3.text = "Dynamic Stretch muscles stressed in " + sport
                # tile_3.description = "to increase blood flow & retain mobility"
                # bold_3 = BoldText()
                # bold_3.text = "Dynamic Stretch"
                # tile_3.bold_text.append(bold_3)
                # tile_3.statistic_text = statistic_text
                # tile_3.trigger_type = t.trigger_type
                tiles.append(tile_1)
                tiles.append(tile_2)
                #tiles.append(tile_3)

        return tiles

    def get_severity_descriptor(self, severity):

        if severity <= 2:
            return "Mild"
        elif 2 < severity <= 3:
            return "Moderate"
        else:
            return "Severe"




