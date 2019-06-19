from models.insights import AthleteInsight, InsightType
from models.soreness import BodyPartSide
from models.trigger import TriggerType
from models.athlete_trend import AthleteTrends, Trend, VisualizationType, DataSource


class AlertsProcessing(object):
    def __init__(self, daily_plan, athlete_stats, trigger_date_time):
        self.daily_plan = daily_plan
        self.athlete_stats = athlete_stats
        self.trigger_date_time = trigger_date_time

    def aggregate_alerts(self, alerts):
        previous_insights = self.daily_plan.insights
        exposed_triggers = self.athlete_stats.exposed_triggers
        longitudinal_insights = self.athlete_stats.longitudinal_insights
        trends = AthleteTrends()
        insights = self.combine_alerts_to_insights(alerts, trends)
        self.clear_trends(trends)
        trends = self.combine_new_trends_with_previous(trends)
        insights, longitudinal_insights = self.clear_insight(insights, longitudinal_insights)

        existing_longitudinal_trigger_types = [insight.trigger_type for insight in longitudinal_insights]
        for insight in insights:
            if not TriggerType.is_in(insight.trigger_type, exposed_triggers):
                insight.first = True
            insight.goal_targeted = list(set(insight.goal_targeted))
            insight.sport_names = list(set(insight.sport_names))
            insight.body_parts = [BodyPartSide.json_deserialise(dict(t)) for t in {tuple(d.json_serialise().items()) for d in insight.body_parts}]
            insight.add_data()
            if insight.longitudinal:
                if insight.trigger_type in existing_longitudinal_trigger_types:
                    existing_insight = [i for i in longitudinal_insights if i.trigger_type == insight.trigger_type][0]
                    existing_insight.body_parts = insight.body_parts
                    existing_insight.sport_names = insight.sport_names
                    existing_insight.child_triggers = insight.child_triggers
                    existing_insight.last_triggered_date_time = self.trigger_date_time
                    insight.start_date_time = existing_insight.start_date_time
                elif insight.cleared:
                    insight.start_date_time = self.trigger_date_time
                else:
                    if insight.start_date_time is None:
                        insight.start_date_time = self.trigger_date_time
                    insight.last_triggered_date_time = self.trigger_date_time
                    longitudinal_insights.append(insight)
            else:
                insight.start_date_time = self.trigger_date_time
        insights = self.combine_new_insights_with_previous(insights, previous_insights)
        insights = [insight for insight in insights if insight.present_in_plans]
        trends.cleanup()
        self.daily_plan.insights = insights
        self.daily_plan.sort_insights()
        self.daily_plan.trends = trends
        self.daily_plan.trends.dashboard.training_volume_data = self.athlete_stats.training_volume_chart_data
        self.athlete_stats.longitudinal_insights = longitudinal_insights

    def clear_insight(self, new_insights, existing_longitudinal_insights):
        current_trigger_types = [insight.trigger_type for insight in new_insights]
        for l_insight in existing_longitudinal_insights:
            # clear doms differently
            if l_insight.trigger_type == TriggerType.sore_today_doms:
                if l_insight.last_triggered_date_time is None or l_insight.last_triggered_date_time.date() != self.trigger_date_time.date():
                    l_insight.cleared = True
            # if trigger type (including others in same parent group) does not exist, everything was cleared
            elif not TriggerType.is_in(l_insight.trigger_type, current_trigger_types):
                l_insight.cleared = True
                new_insights.append(l_insight)
            else:  # find current insight of same trigger type or same parent group
                current_insight = [insight for insight in new_insights if TriggerType.is_equivalent(insight.trigger_type, l_insight.trigger_type)][0]
                # cleared_sports = []
                for trigger_type, body_parts in l_insight.child_triggers.items():
                    if trigger_type not in current_insight.child_triggers.keys():
                        cleared_insight = AthleteInsight(trigger_type)
                        cleared_insight.cleared = True
                        cleared_insight.body_parts = body_parts
                        cleared_insight.parent = False
                        new_insights.append(cleared_insight)
                        l_insight.cleared = True
                    else:
                        cleared_parts = []
                        moved_parts = []
                        current_body_parts = [d.json_serialise() for d in current_insight.child_triggers[trigger_type]]
                        for body_part in body_parts:
                            if body_part.json_serialise() not in current_body_parts:  # if it's not in current parts, it was cleared
                                cleared_parts.append(body_part)
                            else:  # if it's in current parts, it was moved from child trigger to parent trigger
                                moved_parts.append(body_part)
                        if len(cleared_parts) > 0:
                            cleared_insight = AthleteInsight(trigger_type)
                            cleared_insight.cleared = True
                            cleared_insight.body_parts = cleared_parts
                            cleared_insight.parent = False
                            new_insights.append(cleared_insight)
                            l_insight.cleared = True
                        if len(moved_parts) > 0:  # if any parts were moved from child to parent, child should be removed
                            # also update the start date for parent to be the same as the child it inherited
                            if current_insight.start_date_time is None:
                                current_insight.start_date_time = l_insight.start_date_time
                            else:
                                current_insight.start_date_time = min(l_insight.start_date_time, current_insight.start_date_time)
                            # make sure all the body parts were moved and remove the insight
                            for moved_part in moved_parts:
                                l_insight.body_parts.remove(moved_part)
                            if len(l_insight.body_parts) == 0:
                                l_insight.cleared = True
        existing_longitudinal_insights = [insight for insight in existing_longitudinal_insights if not insight.cleared]

        # handle the case of hist_sore going from <30 days(trigger 7) to >=30 days (trigger 19) and make sure two conflicting insights don't exist for same body part
        current_trigger_types = [insight.trigger_type for insight in new_insights]
        if TriggerType(7) in current_trigger_types and TriggerType.is_in(TriggerType(19), current_trigger_types):  # only relevant if both 7 and 19 are present
            cleared_trigger_7_insight = [insight for insight in new_insights if insight.trigger_type == TriggerType(7) and insight.cleared]
            if len(cleared_trigger_7_insight) > 0:  # and if the 7 is actually "cleared"
                cleared_trigger_7_insight = cleared_trigger_7_insight[0]
                cleared_trigger_7_body_parts = [d.json_serialise() for d in cleared_trigger_7_insight.body_parts]
                parent_group_4_trigger = [insight for insight in new_insights if TriggerType.is_equivalent(insight.trigger_type, TriggerType(19)) and not insight.cleared]
                if len(parent_group_4_trigger) > 0:  # make sure parent group 4 is not cleared
                    parent_group_4_trigger = parent_group_4_trigger[0]
                    trigger_19_body_parts = []
                    if parent_group_4_trigger.parent:  # if 19 was grouped with 16 to create a parent insight
                        trigger_19_body_parts = [d.json_serialise() for d in parent_group_4_trigger.child_triggers[TriggerType(19)]]
                    elif parent_group_4_trigger.trigger_type == TriggerType(19):
                        trigger_19_body_parts = [d.json_serialise() for d in parent_group_4_trigger.child_triggers[TriggerType(19)]]
                    if len(trigger_19_body_parts) > 0:  # if we have any body parts actually present for trigger 19
                        for body_part in trigger_19_body_parts:
                            if body_part in cleared_trigger_7_body_parts:
                                cleared_trigger_7_body_parts.remove(body_part)
                    cleared_trigger_7_insight.body_parts = [BodyPartSide.json_deserialise(body_part) for body_part in cleared_trigger_7_body_parts]
                    if len(cleared_trigger_7_insight.body_parts) == 0:  # check to see body part exist after moving the ones that were moved to 19 are removed from cleared 7
                        new_insights.remove(cleared_trigger_7_insight)

        return new_insights, existing_longitudinal_insights

    @classmethod
    def combine_new_insights_with_previous(cls, new_insights, previous_insights):
        current_trigger_types = [insight.trigger_type for insight in new_insights]
        for old in previous_insights:
            if old.read and old.trigger_type in current_trigger_types:
                new = [insight for insight in new_insights if insight.trigger_type == old.trigger_type][0]
                new_json = new.json_serialise()
                old_json = old.json_serialise()
                if new_json['body_parts'] == old_json['body_parts'] and new_json['sport_names'] == old_json['sport_names']:
                    new.read = True
            if old.cleared:
                new_insights.append(old)
        return new_insights

    def combine_new_trends_with_previous(self, new_trends):
        if self.daily_plan.trends is not None:
            for old in self.daily_plan.trends.stress.alerts:
                if old.cleared:
                    new_trends.stress.alerts.append(old)
            for old in self.daily_plan.trends.response.alerts:
                if old.cleared:
                    new_trends.response.alerts.append(old)
            for old in self.daily_plan.trends.biomechanics.alerts:
                if old.cleared:
                    new_trends.biomechanics.alerts.append(old)
        return new_trends

    def combine_alerts_to_insights(self, alerts, trends):
        existing_triggers = []
        existing_trends = []
        insights = []
        existing_doms_insight = any([trend.trigger_type == TriggerType.sore_today_doms for
                                     trend in self.athlete_stats.longitudinal_insights])
        doms_today = False
        for alert in alerts:
            # triggers to trends
            if alert.goal.trigger_type == TriggerType.sore_today_doms:
                if doms_today:
                    trend = [trend for trend in trends.response.alerts if trend.trigger_type == TriggerType.sore_today_doms][0]
                    self.add_data_to_trend(trend, alert)
                else:
                    # create new doms trend
                    doms_today = True
                    existing_trends.append((alert.goal.trigger_type, alert.sport_name, alert.body_part))
                    trend = Trend(alert.goal.trigger_type)
                    trend.last_triggered_date_time = self.trigger_date_time
                    self.add_data_to_trend(trend, alert)
                    # add doms trend to response bucket
                    trends.response.alerts.append(trend)
                    trends.response.goals.add(alert.goal.text)
            elif (alert.goal.trigger_type, alert.body_part) in existing_trends and alert.goal.trigger_type == TriggerType.high_volume_intensity:
                trend = [trend for trend in trends.stress.alerts if trend.trigger_type == TriggerType.high_volume_intensity][0]
                self.add_data_to_trend(trend, alert)

            elif not (alert.goal.trigger_type, alert.body_part) in existing_trends:
                existing_trends.append((alert.goal.trigger_type, alert.body_part))
                trend = Trend(alert.goal.trigger_type)
                self.add_data_to_trend(trend, alert)

                # group trend into proper insight type bucket
                if trend.insight_type == InsightType.stress:
                    trends.stress.alerts.append(trend)
                    if alert.goal.text is not None:
                        trends.stress.goals.add(alert.goal.text)
                elif trend.insight_type == InsightType.response:
                    trends.response.alerts.append(trend)
                    if alert.goal.text is not None:
                        trends.response.goals.add(alert.goal.text)
                elif trend.insight_type == InsightType.biomechanics:
                    trends.biomechanics.alerts.append(trend)
                    if alert.goal.text is not None:
                        trends.biomechanics.goals.add(alert.goal.text)

            # triggers to insights
            # check if trigger already exists
            if alert.goal.trigger_type in existing_triggers:
                insight = [insight for insight in insights if insight.trigger_type == alert.goal.trigger_type][0]
                if alert.goal.text is not None:
                    insight.goal_targeted.append(alert.goal.text)
                if alert.body_part is not None:
                    insight.body_parts.append(alert.body_part)
                    insight.child_triggers[alert.goal.trigger_type].add(alert.body_part)
                if alert.sport_name is not None:
                    insight.sport_names.append(alert.sport_name)
                if alert.severity is not None:
                    insight.severity.append(alert.severity)
            # check if any other group member exists
            elif TriggerType.parent_group_exists(alert.goal.trigger_type, existing_triggers):
                insight = [insight for insight in insights if TriggerType.is_same_parent_group(alert.goal.trigger_type, insight.trigger_type)][0]
                if alert.goal.text is not None:
                    insight.goal_targeted.append(alert.goal.text)
                # for parent group 2 (trigger_type 14 and 15, 23, 24), if parent, should always get styling 1
                # if insight.parent_group == 2:
                #     insight.styling = 1
                insight.parent = True
                if alert.body_part is not None:
                    insight.body_parts.append(alert.body_part)
                    if alert.goal.trigger_type not in insight.child_triggers.keys():
                        insight.child_triggers[alert.goal.trigger_type] = {alert.body_part}
                    else:
                        insight.child_triggers[alert.goal.trigger_type].add(alert.body_part)
                elif alert.goal.trigger_type not in insight.child_triggers.keys():
                        insight.child_triggers[alert.goal.trigger_type] = set([])

                if alert.sport_name is not None:
                    insight.sport_names.append(alert.sport_name)
                if alert.severity is not None:
                    insight.severity.append(alert.severity)
            else:
                insight = AthleteInsight(alert.goal.trigger_type)
                if alert.goal.text is not None:
                    insight.goal_targeted.append(alert.goal.text)
                if alert.body_part is not None:
                    insight.body_parts.append(alert.body_part)
                    insight.child_triggers[alert.goal.trigger_type] = {alert.body_part}
                else:
                    insight.child_triggers[alert.goal.trigger_type] = set([])
                if alert.sport_name is not None:
                    insight.sport_names.append(alert.sport_name)
                if alert.severity is not None:
                    insight.severity.append(alert.severity)
                existing_triggers.append(alert.goal.trigger_type)
                insights.append(insight)

        # remove doms if present yesterday
        if TriggerType.sore_today_doms in existing_triggers and existing_doms_insight:  # doms present today and present in longitudinal insights
            l_insight = [insight for insight in self.athlete_stats.longitudinal_insights if insight.trigger_type == TriggerType.sore_today_doms][0]
            # if doms wasn't started earlier today, remove it (Note: that doms is present today so, we're not clearing it from longitudinal insights)
            if l_insight.start_date_time.date() != self.trigger_date_time.date():
                doms_insight = [insight for insight in insights if insight.trigger_type == TriggerType.sore_today_doms][0]
                insights.remove(doms_insight)
                l_insight.last_triggered_date_time = self.trigger_date_time

        return insights

    def add_chart_data(self, trend):
        if trend.visualization_type == VisualizationType.load:
            chart_data = []
        elif trend.visualization_type == VisualizationType.session:
            chart_data = self.athlete_stats.high_relative_load_chart_data
        elif trend.visualization_type == VisualizationType.body_part:
            body_part = trend.body_parts[0]
            if trend.data_source == DataSource.pain and body_part in self.athlete_stats.pain_chart_data.keys():
                chart_data = self.athlete_stats.pain_chart_data[body_part]
            elif trend.data_source == DataSource.soreness and body_part in self.athlete_stats.soreness_chart_data.keys():
                chart_data = self.athlete_stats.soreness_chart_data[body_part]
            else:
                chart_data = []
        elif trend.visualization_type == VisualizationType.doms:
            chart_data = self.athlete_stats.doms_chart_data
        elif trend.visualization_type == VisualizationType.muscular_strain:
            chart_data = self.athlete_stats.muscular_strain_chart_data
        elif trend.visualization_type == VisualizationType.sensor:
            chart_data = []
        else:
            chart_data = []

        trend.data = chart_data
        return trend

    def add_data_to_trend(self, trend, alert):
        if alert.goal.text is not None:
            trend.goal_targeted = [alert.goal.text]
        if alert.body_part is not None:
            trend.body_parts.append(alert.body_part)
        if alert.sport_name is not None:
            trend.sport_names.append(alert.sport_name)
        # populate trend with text/visualization data
        trend.body_parts = [BodyPartSide.json_deserialise(dict(t)) for t in {tuple(d.json_serialise().items()) for d in trend.body_parts}]
        trend.sport_names = list(set(trend.sport_names))
        trend.add_data()
        # populate relevant data for charts
        self.add_chart_data(trend)

    def clear_trends(self, new_trends):
        current_stress_trigger_types = [trend.get_trigger_type_body_part_sport_tuple() for trend in new_trends.stress.alerts]
        current_response_trigger_types = [trend.get_trigger_type_body_part_sport_tuple() for trend in new_trends.response.alerts]
        current_biomechanics_trigger_types = [trend.get_trigger_type_body_part_sport_tuple() for trend in new_trends.biomechanics.alerts]

        for l_trend in self.athlete_stats.longitudinal_trends:
            # if trigger type does not exist, it was cleared
            if l_trend.insight_type == InsightType.stress and \
                    l_trend.get_trigger_type_body_part_sport_tuple() not in current_stress_trigger_types:
                l_trend.cleared = True
                # populate trend with text/visualization data
                l_trend.add_data()
                # populate relevant data for charts
                self.add_chart_data(l_trend)
                new_trends.stress.alerts.append(l_trend)
            elif l_trend.insight_type == InsightType.response and \
                    l_trend.trigger_type != TriggerType.sore_today_doms and \
                    l_trend.get_trigger_type_body_part_sport_tuple() not in current_response_trigger_types:
                l_trend.cleared = True
                # populate trend with text/visualization data
                l_trend.add_data()
                # populate relevant data for charts
                self.add_chart_data(l_trend)
                if not (l_trend.trigger_type == TriggerType(7) and (TriggerType(19), l_trend.body_parts[0]) in current_biomechanics_trigger_types):
                    new_trends.response.alerts.append(l_trend)
            elif l_trend.insight_type == InsightType.biomechanics and \
                    l_trend.get_trigger_type_body_part_sport_tuple() not in current_biomechanics_trigger_types:
                l_trend.cleared = True
                # populate trend with text/visualization data
                l_trend.add_data()
                # populate relevant data for charts
                self.add_chart_data(l_trend)
                new_trends.biomechanics.alerts.append(l_trend)

        self.athlete_stats.longitudinal_trends = []
        self.athlete_stats.longitudinal_trends.extend([trend for trend in new_trends.stress.alerts if trend.longitudinal and not trend.cleared])
        self.athlete_stats.longitudinal_trends.extend([trend for trend in new_trends.response.alerts if trend.longitudinal and not trend.cleared])
        self.athlete_stats.longitudinal_trends.extend([trend for trend in new_trends.biomechanics.alerts if trend.longitudinal and not trend.cleared])
        return new_trends
