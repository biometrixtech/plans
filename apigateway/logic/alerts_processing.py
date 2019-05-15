from models.insights import AthleteInsight, InsightType
from models.soreness import TriggerType


class AlertsProcessing(object):

    @classmethod
    def aggregate_alerts(cls, trigger_date_time, alerts, displayed_alerts, longitudinal_alerts):
        existing_triggers = []
        insights = []
        for alert in alerts:
            if alert.goal.trigger_type not in existing_triggers:
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
            else:
                insight = [insight for insight in insights if insight.trigger_type == alert.goal.trigger_type][0]
                insight.goal_targeted.append(alert.goal.text)
                if alert.body_part is not None:
                    insight.body_parts.append(alert.body_part)
                if alert.sport_name is not None:
                    insight.sport_names.append(alert.sport_name)
                if alert.severity is not None:
                    insight.severity.append(alert.severity)

        current_trigger_types = [insight.trigger_type for insight in insights]
        for l_insight in longitudinal_alerts:
            if l_insight.trigger_type not in current_trigger_types:
                l_insight.cleared = True
        insights.extend([insight for insight in longitudinal_alerts if insight.cleared])
        longitudinal_alerts = [insight for insight in longitudinal_alerts if not insight.cleared]

        existing_longitudinal_trigger_types = [insight.trigger_type for insight in longitudinal_alerts]
        for insight in insights:
            if insight.trigger_type not in displayed_alerts:
                insight.first = True
            insight.goal_targeted = list(set(insight.goal_targeted))
            insight.sport_names = list(set(insight.sport_names))
            insight.body_parts = list(set(insight.body_parts))
            insight.get_title_and_text()
            if insight.insight_type == InsightType.longitudinal:
                if insight.trigger_type in existing_longitudinal_trigger_types:
                    existing_insight = [i for i in longitudinal_alerts if i.trigger_type == insight.trigger_type][0]
                    insight.start_date_time = existing_insight.start_date_time
                elif insight.cleared:
                    continue
                else:
                    insight.start_date_time = trigger_date_time
                    longitudinal_alerts.append(insight)
            else:
                insight.start_date_time = trigger_date_time

        return insights, longitudinal_alerts


grouped_triggers = {0: [TriggerType(6), TriggerType(7), TriggerType(8)],
                    1: [TriggerType(10), TriggerType(11)]}
