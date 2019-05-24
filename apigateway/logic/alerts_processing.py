from models.insights import AthleteInsight, InsightType
from models.soreness import BodyPartSide
from models.trigger import TriggerType
from models.athlete_trend import AthleteTrends, Trend, VisualizationType, DataSource


class AlertsProcessing(object):
    def __init__(self, daily_plan, athlete_stats):
        self.daily_plan = daily_plan
        self.athlete_stats = athlete_stats

    def aggregate_alerts(self, trigger_date_time, alerts):
        previous_insights = self.daily_plan.insights
        exposed_triggers = self.athlete_stats.exposed_triggers
        longitudinal_insights = self.athlete_stats.longitudinal_insights
        trends = AthleteTrends()
        insights = self.combine_alerts_to_insights(alerts, trends)
        self.clear_trends(trends)
        if TriggerType(9) in exposed_triggers:
            insights = [insight for insight in insights if insight.trigger_type != TriggerType(9)]
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
                    insight.start_date_time = existing_insight.start_date_time
                elif insight.cleared:
                    continue
                else:
                    insight.start_date_time = trigger_date_time
                    longitudinal_insights.append(insight)
            else:
                insight.start_date_time = trigger_date_time
        insights = self.combine_new_insights_with_previous(insights, previous_insights)
        insights = [insight for insight in insights if insight.present_in_plans]
        trends.cleanup()
        self.daily_plan.insights = insights
        self.daily_plan.sort_insights()
        self.daily_plan.trends = trends
        self.daily_plan.trends.dashboard.training_volume_data = self.athlete_stats.training_volume_chart_data
        self.athlete_stats.longitudinal_insights = longitudinal_insights

        return insights, longitudinal_insights, trends

    @classmethod
    def clear_insight(cls, new_insights, existing_longitudinal_insights):
        current_trigger_types = [insight.trigger_type for insight in new_insights]
        for l_insight in existing_longitudinal_insights:
            # if trigger type (including others in same parent group) does not exist, everything was cleared
            if not TriggerType.is_in(l_insight.trigger_type, current_trigger_types):
                l_insight.cleared = True
                new_insights.append(l_insight)
            else:  # find current insight is same trigger type or same parent group
                current_insight = [insight for insight in new_insights if TriggerType.is_equivalent(insight.trigger_type, l_insight.trigger_type)][0]
                cleared_parts = []
                cleared_sports = []
                current_body_parts = [d.json_serialise() for d in current_insight.body_parts]
                for body_part in l_insight.body_parts:
                    if body_part.json_serialise() not in current_body_parts:
                        cleared_parts.append(body_part)
                for sport in l_insight.sport_names:
                    if sport not in current_insight.sport_names:
                        cleared_sports.append(sport)
                if len(cleared_parts) > 0 or len(cleared_sports) > 0:   # check if any body part was cleared
                    l_insight.cleared = True
                    l_insight.body_parts = cleared_parts
                    l_insight.sport_names = cleared_sports
                    new_insights.append(l_insight)  # add cleared insight to today
        existing_longitudinal_insights = [insight for insight in existing_longitudinal_insights if not insight.cleared]

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

    def combine_alerts_to_insights(self, alerts, trends):
        existing_triggers = []
        existing_trends = []
        insights = []
        doms_yesterday = any([trend.trigger_type == TriggerType.sore_today_doms for trend in self.athlete_stats.longitudinal_trends])
        doms_today = False
        for alert in alerts:
            if alert.goal.trigger_type == TriggerType.sore_today_doms:
                if doms_yesterday:
                    continue
                elif doms_today:
                    trend = [trend for trend in trends.response.alerts if trend.trigger_type == TriggerType.sore_today_doms][0]
                    self.add_data_to_trend(trend, alert)
                else:
                    # create new doms trend
                    doms_today = True
                    existing_trends.append((alert.goal.trigger_type, alert.sport_name, alert.body_part))
                    trend = Trend(alert.goal.trigger_type)
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
                    trends.stress.goals.add(alert.goal.text)
                elif trend.insight_type == InsightType.response:
                    trends.response.alerts.append(trend)
                    trends.response.goals.add(alert.goal.text)
                elif trend.insight_type == InsightType.biomechanics:
                    trends.biomechanics.alerts.append(trend)
                    trends.biomechanics.goals.add(alert.goal.text)
            # check if trigger already exists
            if alert.goal.trigger_type in existing_triggers:
                insight = [insight for insight in insights if insight.trigger_type == alert.goal.trigger_type][0]
                insight.goal_targeted.append(alert.goal.text)
                if alert.body_part is not None:
                    insight.body_parts.append(alert.body_part)
                if alert.sport_name is not None:
                    insight.sport_names.append(alert.sport_name)
                if alert.severity is not None:
                    insight.severity.append(alert.severity)
            # check if any other group member exists
            elif TriggerType.parent_group_exists(alert.goal.trigger_type, existing_triggers):
                insight = [insight for insight in insights if TriggerType.is_same_parent_group(alert.goal.trigger_type, insight.trigger_type)][0]
                insight.goal_targeted.append(alert.goal.text)
                insight.parent = True
                if alert.body_part is not None:
                    insight.body_parts.append(alert.body_part)
                if alert.sport_name is not None:
                    insight.sport_names.append(alert.sport_name)
                if alert.severity is not None:
                    insight.severity.append(alert.severity)
            else:
                insight = AthleteInsight(alert.goal.trigger_type)
                insight.goal_targeted.append(alert.goal.text)
                if alert.body_part is not None:
                    insight.body_parts.append(alert.body_part)
                if alert.sport_name is not None:
                    insight.sport_names.append(alert.sport_name)
                if alert.severity is not None:
                    insight.severity.append(alert.severity)
                existing_triggers.append(alert.goal.trigger_type)
                insights.append(insight)

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
                new_trends.response.alerts.append(l_trend)
            elif l_trend.insight_type == InsightType.biomechanics and \
                    l_trend.get_trigger_type_body_part_sport_tuple() not in current_biomechanics_trigger_types:
                l_trend.cleared = True
                # populate trend with text/visualization data
                l_trend.add_data()
                # populate relevant data for charts
                self.add_chart_data(l_trend)
                new_trends.biomechanics.alerts.append(l_trend)

        self.athlete_stats.longitudinal_trends = [trend for trend in new_trends.stress.alerts if trend.longitudinal and not trend.cleared]
        self.athlete_stats.longitudinal_trends.extend([trend for trend in new_trends.response.alerts if trend.longitudinal and not trend.cleared])
        self.athlete_stats.longitudinal_trends.extend([trend for trend in new_trends.biomechanics.alerts if trend.longitudinal and not trend.cleared])
        return new_trends
