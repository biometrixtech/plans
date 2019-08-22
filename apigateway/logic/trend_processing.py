from models.athlete_trend import TrendDashboardCategory, PlanAlert, Trend, TrendCategory, TrendData, \
    FirstTimeExperienceElement, CategoryFirstTimeExperienceModal
from models.styles import BoldText, LegendColor, VisualizationType
from models.trigger import TriggerType, Trigger
from models.chart_data import PainFunctionalLimitationChartData, TightOverUnderactiveChartData, CareTodayChartData
from models.insights import InsightType
from models.body_parts import BodyPartFactory
from models.soreness_base import BodyPartSide, BodyPartLocation
from logic.goal_focus_text_generator import RecoveryTextGenerator


class TrendProcessor(object):
    def __init__(self, trigger_list, athlete_trend_categories=None, dashboard_categories=None):
        self.athlete_trend_categories = [] if athlete_trend_categories is None else athlete_trend_categories
        self.trigger_list = trigger_list
        self.dashboard_categories = [] if dashboard_categories is None else dashboard_categories

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

        if len(self.athlete_trend_categories) == 0:

            personalized_recovery_category = self.create_personalized_recovery_category()
            prevention_category = self.create_prevention_category()
            care_category = self.create_care_category()

            self.athlete_trend_categories.append(personalized_recovery_category)
            self.athlete_trend_categories.append(prevention_category)
            self.athlete_trend_categories.append(care_category)

    def get_care_trend(self, category_index):

        care_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                                 x.visualization_type == VisualizationType.care_today), -1)
        if care_index == -1:
            care_trend = self.create_daily_trend()
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

    def get_limitation_trend(self, category_index):

        limitation_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                                 x.visualization_type == VisualizationType.pain_functional_limitation), -1)
        if limitation_index == -1:
            limitation_trend = self.create_limitation_trend()
            self.athlete_trend_categories[category_index].trends.append(limitation_trend)
            limitation_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[limitation_index]

    def set_limitation_trend(self, category_index, limitation_trend):

        index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.pain_functional_limitation), -1)

        if index == -1:
            self.athlete_trend_categories[category_index].trends.append(limitation_trend)
        else:
            self.athlete_trend_categories[category_index].trends[index] = limitation_trend

    def get_muscle_trend(self, category_index):

        muscle_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.tight_overactice_underactive), -1)
        if muscle_index == -1:
            muscle_trend = self.create_muscle_trend()
            self.athlete_trend_categories[category_index].trends.append(muscle_trend)
            muscle_index = len(self.athlete_trend_categories[category_index].trends) - 1

        return self.athlete_trend_categories[category_index].trends[muscle_index]

    def set_muscle_trend(self, category_index, muscle_trend):

        muscle_index = next((i for i, x in enumerate(self.athlete_trend_categories[category_index].trends) if
                             x.visualization_type == VisualizationType.tight_overactice_underactive), -1)

        if muscle_index == -1:
            self.athlete_trend_categories[category_index].trends.append(muscle_trend)
        else:
            self.athlete_trend_categories[category_index].trends[muscle_index] = muscle_trend

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

        muscle_trend = self.create_muscle_trend()
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

        limitation_trend = self.create_limitation_trend()
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

        daily_trend = self.create_daily_trend()
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

    def create_daily_trend(self):
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

    def create_limitation_trend(self):
        limitation_trend = Trend(TriggerType.hist_sore_greater_30)
        limitation_trend.title = "Injury Cycle Risks"
        limitation_trend.title_color = LegendColor.error_light
        limitation_trend.text.append("Your pain may lead to elevated strain on other muscles and soft tissue injury.")
        limitation_trend.text.append("Most people, knowingly or not, change the way they move to distribute force away from areas of pain. "+
                                     "This over-stresses supporting tissues and limbs which adopt more force and stress than they’re used to. "+
                                     "This often leads accumulated muscle damage and the eventual development of new injuries. See your factors below.")


        limitation_trend.icon = "view3icon.png"
        limitation_trend.video_url = "https://d2xll36aqjtmhz.cloudfront.net/view3context.mp4"
        limitation_trend.visualization_type = VisualizationType.pain_functional_limitation
        limitation_trend.visible = False
        limitation_trend.first_time_experience = True
        return limitation_trend

    def create_muscle_trend(self):
        muscle_trend = Trend(TriggerType.hist_pain)
        muscle_trend.title = "Muscle Over & Under-Activity"
        muscle_trend.title_color = LegendColor.warning_light
        muscle_trend.text.append("Your data suggests you may have some imbalances in muscle activation which can lead to performance inefficiencies like decreased speed and power output.")
        muscle_trend.text.append("If these imbalances persist, they can turn into strength dysfunctions which alter your biomechanics and elevate soft tissue injury risk."+
                                 " Addressing these imbalances early is important for athletic resilience.")

        muscle_trend.icon = "view1icon.png"
        muscle_trend.video_url = "https://d2xll36aqjtmhz.cloudfront.net/view1context.mp4"
        muscle_trend.visualization_type = VisualizationType.tight_overactice_underactive
        muscle_trend.visible = False
        muscle_trend.first_time_experience = True
        return muscle_trend

    def process_triggers(self):

        personalized_recovery_category_index = self.get_category_index(InsightType.personalized_recovery)
        prevention_category_index = self.get_category_index(InsightType.prevention)
        care_category_index = self.get_category_index(InsightType.care)
        self.set_tight_over_under_muscle_view(personalized_recovery_category_index)
        self.set_pain_functional_limitation(prevention_category_index)
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

                    sorted_trends = sorted(visible_trends, key=lambda v: v.last_date_time, reverse=True)

                    if (len(self.athlete_trend_categories[c].plan_alerts) > 0 and
                            (self.athlete_trend_categories[c].plan_alerts[0].cleared_date_time is None)):

                        # clear this out so we can update the plan alert
                        self.athlete_trend_categories[c].plan_alerts = []

                    if (len(self.athlete_trend_categories[c].plan_alerts) == 0 or
                        (self.athlete_trend_categories[c].plan_alerts[0].cleared_date_time is not None
                         and sorted_trends[0].last_date_time > self.athlete_trend_categories[c].plan_alerts[0].cleared_date_time)):

                        # clear this out so we can update the plan alert
                        self.athlete_trend_categories[c].plan_alerts = []

                        # plans alert text
                        plan_alert = self.get_plan_alert(new_modified_trigger_count, plan_alert_short_title,
                                                         personalized_recovery_category_index, visible_trends)
                        self.athlete_trend_categories[c].plan_alerts.append(plan_alert)

                    # Now create dashboard category card
                    self.dashboard_categories = []

                    trend_dashboard_category = None

                    if sorted_trends[0].visualization_type == VisualizationType.tight_overactice_underactive:
                        trend_dashboard_category = self.get_over_under_active_dashboard_card(c, sorted_trends[0])

                    elif sorted_trends[0].visualization_type == VisualizationType.pain_functional_limitation:
                        trend_dashboard_category = self.get_functional_limitation_dashboard_card(c, sorted_trends[0])

                    if trend_dashboard_category is not None:
                        trend_dashboard_category.unread_alerts = (
                                    len(self.athlete_trend_categories[c].plan_alerts) > 0)
                        self.dashboard_categories.append(trend_dashboard_category)
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

    def set_tight_over_under_muscle_view(self, category_index):

        triggers_7 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.hist_sore_less_30)
        for t in triggers_7:
            t.priority = 1

        triggers_110 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.movement_error_apt_asymmetry)
        for t in triggers_110:
            t.priority = 2

        # since we're reverse sorting, 2 is a higher priority than 1

        if len(triggers_7) > 0 or len(triggers_110) > 0:

            antagonists_7, synergists_7 = self.get_antagonists_syngergists(triggers_7)
            #antagonists_110, synergists_110 = self.get_antagonists_syngergists(triggers_110)

            trend = self.get_muscle_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.tight_overactice_underactive
            trend_data.add_visualization_data()
            tight_under_data = TightOverUnderactiveChartData()
            tight_under_data.overactive.extend([t.body_part for t in triggers_7])
            tight_under_data.underactive_needing_care.extend([s for s in synergists_7])

            for t in triggers_110:
                tight_under_data.overactive.extend([a for a in t.overactive_tight_first])
                tight_under_data.overactive.extend([s for s in t.overactive_tight_second])
                tight_under_data.underactive_needing_care.extend([s for s in t.elevated_stress])

            tight_under_data.remove_duplicates()
            trend_data.data = [tight_under_data]

            all_triggers = []
            all_triggers.extend(triggers_7)
            all_triggers.extend(triggers_110)

            # rank triggers
            sorted_triggers = sorted(all_triggers, key=lambda x: (x.created_date_time, x.priority), reverse=True)

            text_generator = RecoveryTextGenerator()
            body_part_factory = BodyPartFactory()

            top_candidates = list(s for s in sorted_triggers if s.created_date_time == sorted_triggers[0].created_date_time and s.priority == sorted_triggers[0].priority)

            trend.top_priority_trigger, is_body_part_plural = self.get_highest_priority_body_part_from_triggers(body_part_factory, top_candidates)

            if is_body_part_plural:
                side = 0
            else:
                side = trend.top_priority_trigger.body_part.side

            if is_body_part_plural and trend.top_priority_trigger.priority == 2:
                body_part_text = text_generator.get_body_part_text_plural(
                    trend.top_priority_trigger.body_part.body_part_location, None)
            else:
                body_part_text = text_generator.get_body_part_text(trend.top_priority_trigger.body_part.body_part_location, None)
            body_part_text = body_part_text.title()

            if trend.top_priority_trigger.priority == 1:
                title_body_part_text, is_title_plural = self.get_title_text_for_body_parts(trend.top_priority_trigger.synergists, side)
                trend_data.title = "Elevated strain on " + title_body_part_text
                trend.plan_alert_short_title = "elevated strain on " + title_body_part_text
                clean_title_body_part_text = title_body_part_text.replace('&', 'and')
                body_text = ("Signs of " + body_part_text + " overactivity in your soreness data suggest that supporting tissues like the " + clean_title_body_part_text +
                            " are experiencing elevated levels of strain which can lead to tissue fatigue and strength imbalances that affect performance and increase injury risk.")
                trend.dashboard_body_part, trend.dashboard_body_part_text = self.get_title_body_part_and_text(trend.top_priority_trigger.synergists, side)
            else:
                title_body_part_text, is_title_plural = self.get_title_text_for_body_parts(trend.top_priority_trigger.antagonists, side)
                title_body_part_text_not_plural, is_title_plural_false = self.get_title_text_for_body_parts(trend.top_priority_trigger.antagonists, side, use_plural=False)
                trend_data.title = title_body_part_text + " may lack strength"
                #trend.plan_alert_short_title = title_body_part_text + " weakness"
                trend.plan_alert_short_title = title_body_part_text_not_plural + " weakness"
                clean_title_body_part_text = title_body_part_text.replace('&','and')

                if is_title_plural:
                    for_a_weak_phrase = "for weak"
                else:
                    for_a_weak_phrase = "for a weak"

                body_text = ("Patterns in your soreness data suggest that your " + body_part_text + " may actually be overactive due to a chronic over-compensation " + for_a_weak_phrase + " "
                             + clean_title_body_part_text + ".  This dysfunction could exacerbate movement imbalances and elevate your risk of chronic injury.")

                temp_body_parts = []
                for o in tight_under_data.overactive:
                    bp = body_part_factory.get_body_part(BodyPartSide(BodyPartLocation(o), side))
                    temp_body_parts.append(bp)
                trend.dashboard_body_part, trend.dashboard_body_part_text = self.get_title_body_part_and_text(temp_body_parts, side)

            trend_data.text = body_text

            bold_text_3 = BoldText()
            bold_text_3.text = body_part_text
            bold_text_3.color = LegendColor.warning_light
            trend_data.bold_text.append(bold_text_3)

            if trend.top_priority_trigger.priority == 1:

                bold_text_4 = BoldText()
                bold_text_4.text = clean_title_body_part_text
                bold_text_4.color = LegendColor.splash_light

                trend_data.bold_text.append(bold_text_4)

            else:

                bold_text_4 = BoldText()
                bold_text_4.text = clean_title_body_part_text
                bold_text_4.color = LegendColor.splash_x_light

                trend_data.bold_text.append(bold_text_4)

            trend.trend_data = trend_data

            trend.visible = True
            trend.priority = 0

            trend.triggers = all_triggers

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)

            self.set_muscle_trend(category_index, trend)

        else:
            trend = self.create_muscle_trend()
            self.set_muscle_trend(category_index, trend)

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
                body_part = body_part_factory.get_body_part(t.body_part)
                t.body_part_priority = body_part.treatment_priority

            # still could have a tie (two body parts)
            sorted_triggers = sorted(top_candidates, key=lambda x: x.body_part_priority)

            if len(sorted_triggers) > 1:
                if sorted_triggers[0].body_part_priority == sorted_triggers[1].body_part_priority:
                    return sorted_triggers[0], True
                else:
                    return sorted_triggers[0], sorted_triggers[0].body_part.side == 0
            else:
                return sorted_triggers[0], sorted_triggers[0].body_part.side == 0

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
            t.priority = 1

        sore_triggers = [TriggerType.sore_today_doms,
                         TriggerType.hist_sore_less_30_sore_today,
                         TriggerType.hist_sore_greater_30_sore_today]

        triggers_sore = list(t for t in self.trigger_list if t.trigger_type in sore_triggers)
        for t in triggers_sore:
            t.priority = 2

        triggers_load = list(t for t in self.trigger_list if t.trigger_type == TriggerType.high_volume_intensity)
        for t in triggers_load:
            t.priority = 3

        if len(triggers_pain) > 0 or len(triggers_sore) > 0 or len(triggers_load) > 0:

            trend = self.get_care_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.care_today
            trend_data.add_visualization_data()
            care_data = CareTodayChartData()

            body_part_factory = BodyPartFactory()

            for t in triggers_pain:
                care_data.overactive.extend([t.body_part])  # pain
                if body_part_factory.is_joint(t.body_part):
                    care_data.underactive_needing_care.extend([a for a in t.agonists])  # elevated strain
                    care_data.underactive_needing_care.extend([a for a in t.antagonists])  # elevated strain
                    care_data.underactive_needing_care.extend([a for a in t.synergists])  # elevated strain
                else:
                    care_data.underactive_needing_care.extend([s for s in t.synergists])  # elevated strain

            for t in triggers_sore:
                care_data.underactive.extend([t.body_part])  # soreness
                care_data.underactive_needing_care.extend([s for s in t.synergists])  # elevated strain

            for t in triggers_load:
                body_part_sport = body_part_factory.get_body_part_for_sports([t.sport_name])
                care_data.underactive_needing_care.extend([a for a in body_part_sport.agonists])  # elevated strain
                care_data.underactive_needing_care.extend([s for s in body_part_sport.synergists])  # elevated strain

            care_data.remove_duplicates()
            trend_data.data = [care_data]

            all_triggers = []
            all_triggers.extend(triggers_pain)
            all_triggers.extend(triggers_sore)
            all_triggers.extend(triggers_load)

            # rank triggers
            sorted_triggers = sorted(all_triggers, key=lambda x: (x.created_date_time, x.priority), reverse=True)

            trend.triggers = all_triggers

            text_generator = RecoveryTextGenerator()
            body_part_factory = BodyPartFactory()

            top_candidates = list(
                s for s in sorted_triggers if s.created_date_time == sorted_triggers[0].created_date_time)

            trend.top_priority_trigger, is_body_part_plural = self.get_highest_priority_body_part_from_triggers(
                body_part_factory, top_candidates)

            if is_body_part_plural:
                side = 0
            else:
                side = trend.top_priority_trigger.body_part.side

            if trend.top_priority_trigger.body_part is not None:
                body_part_text = text_generator.get_body_part_text(trend.top_priority_trigger.body_part.body_part_location,
                                                                   None)
            else:
                body_part_text = ""

            body_part_text = body_part_text.title()

            title_body_part_text, is_title_plural = self.get_title_text_for_body_parts(
                trend.top_priority_trigger.synergists, side)
            trend_data.title = "Elevated strain on " + title_body_part_text
            trend.plan_alert_short_title = "elevated strain on " + title_body_part_text
            clean_title_body_part_text = title_body_part_text.replace('&', 'and')
            body_text = (
                        "Athletes struggling with recurring " + body_part_text + " pain often develop misalignments that over-stress their " + clean_title_body_part_text +
                        ". Without proactive measures, this can lead to accumulated micro-trauma in the tissues and new areas of pain or injury over time.")
            trend.dashboard_body_part, trend.dashboard_body_part_text = self.get_title_body_part_and_text(
                trend.top_priority_trigger.synergists, side)

            bold_text_3 = BoldText()
            bold_text_3.text = body_part_text
            bold_text_3.color = LegendColor.error_light
            trend_data.bold_text.append(bold_text_3)
            trend_data.text = body_text

            bold_text_4 = BoldText()
            bold_text_4.text = clean_title_body_part_text
            bold_text_4.color = LegendColor.splash_x_light
            trend_data.bold_text.append(bold_text_4)

            trend.trend_data = trend_data
            trend.visible = True
            trend.priority = 1

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)

            self.set_care_trend(category_index, trend)

        else:
            trend = self.create_daily_trend()
            self.set_care_trend(category_index, trend)

    def set_pain_functional_limitation(self, category_index):

        triggers_19 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.hist_sore_greater_30)
        for t in triggers_19:
            t.priority = 1

        triggers_16 = list(t for t in self.trigger_list if t.trigger_type == TriggerType.hist_pain)
        for t in triggers_16:
            t.priority = 2

        # since we're reverse sorting, 2 is a higher priority than 1

        if len(triggers_19) > 0 or len(triggers_16) > 0:

            antagonists_19, synergists_19 = self.get_antagonists_syngergists(triggers_19)

            trend = self.get_limitation_trend(category_index)

            trend_data = TrendData()
            trend_data.visualization_type = VisualizationType.pain_functional_limitation
            trend_data.add_visualization_data()
            pain_functional_data = PainFunctionalLimitationChartData()

            pain_functional_data.overactive.extend([t.body_part for t in triggers_19])
            pain_functional_data.underactive.extend([a for a in antagonists_19]) # weakness
            pain_functional_data.underactive_needing_care.extend([s for s in synergists_19]) # elevated strain

            body_part_factory = BodyPartFactory()

            for t in triggers_16:
                if body_part_factory.is_joint(t.body_part):
                    pain_functional_data.overactive.extend([a for a in t.agonists])  # overactive
                    pain_functional_data.overactive.extend([a for a in t.antagonists])  # overactive
                    pain_functional_data.underactive_needing_care.extend([t.body_part])  # elevated strain
                else:
                    pain_functional_data.underactive_needing_care.extend(
                        [t.body_part])  # elevated strain
                    pain_functional_data.underactive_needing_care.extend(
                        [s for s in t.synergists])  # elevated strain
                    pain_functional_data.underactive.extend([a for a in t.antagonists])  # weakness

            pain_functional_data.remove_duplicates()
            trend_data.data = [pain_functional_data]

            all_triggers = []
            all_triggers.extend(triggers_19)
            all_triggers.extend(triggers_16)

            # rank triggers
            sorted_triggers = sorted(all_triggers, key=lambda x: (x.created_date_time, x.priority), reverse=True)

            trend.triggers = all_triggers

            # rank triggers
            sorted_triggers = sorted(all_triggers, key=lambda x: x.created_date_time, reverse=True)

            text_generator = RecoveryTextGenerator()
            body_part_factory = BodyPartFactory()

            top_candidates = list(
                s for s in sorted_triggers if s.created_date_time == sorted_triggers[0].created_date_time)

            trend.top_priority_trigger, is_body_part_plural = self.get_highest_priority_body_part_from_triggers(
                body_part_factory, top_candidates)

            if is_body_part_plural:
                side = 0
            else:
                side = trend.top_priority_trigger.body_part.side

            body_part_text = text_generator.get_body_part_text(trend.top_priority_trigger.body_part.body_part_location, None)
            body_part_text = body_part_text.title()

            title_body_part_text, is_title_plural = self.get_title_text_for_body_parts(trend.top_priority_trigger.synergists, side)
            trend_data.title = "Elevated strain on " + title_body_part_text
            trend.plan_alert_short_title = "elevated strain on " + title_body_part_text
            clean_title_body_part_text = title_body_part_text.replace('&','and')
            body_text = ("Athletes struggling with recurring " + body_part_text + " pain often develop misalignments that over-stress their "+ clean_title_body_part_text +
                         ". Without proactive measures, this can lead to accumulated micro-trauma in the tissues and new areas of pain or injury over time.")
            trend.dashboard_body_part, trend.dashboard_body_part_text = self.get_title_body_part_and_text(
                trend.top_priority_trigger.synergists, side)

            bold_text_3 = BoldText()
            bold_text_3.text = body_part_text
            bold_text_3.color = LegendColor.error_light
            trend_data.bold_text.append(bold_text_3)
            trend_data.text = body_text

            bold_text_4 = BoldText()
            bold_text_4.text = clean_title_body_part_text
            bold_text_4.color = LegendColor.splash_x_light
            trend_data.bold_text.append(bold_text_4)

            trend.trend_data = trend_data
            trend.visible = True
            trend.priority = 1

            trend.last_date_time = self.get_latest_trigger_date_time(all_triggers)

            self.set_limitation_trend(category_index, trend)

        else:
            trend = self.create_limitation_trend()
            self.set_limitation_trend(category_index, trend)

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




