from models.insights import AthleteInsight, InsightType
from models.soreness import TriggerType


class AlertsProcessing(object):

    @classmethod
    def aggregate_alerts(cls, trigger_date_time, alerts, exposed_triggers, longitudinal_insights):
        existing_triggers = []
        insights = []
        for alert in alerts:
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
            elif alert.goal.trigger_type.is_grouped_trigger() and parent_group_exists(alert.goal.trigger_type, existing_triggers):
                insight = [insight for insight in insights if insight.trigger_type.belongs_to_same_group(alert.goal.trigger_type)][0]
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

        current_trigger_types = [insight.trigger_type for insight in insights]
        if TriggerType(9) in exposed_triggers:
            insights = [insight for insight in insights if insight.trigger_type != TriggerType(9)]
        for l_insight in longitudinal_insights:
            if l_insight.trigger_type not in current_trigger_types:
                l_insight.cleared = True
        insights.extend([insight for insight in longitudinal_insights if insight.cleared])
        longitudinal_insights = [insight for insight in longitudinal_insights if not insight.cleared]

        existing_longitudinal_trigger_types = [insight.trigger_type for insight in longitudinal_insights]
        for insight in insights:
            if insight.trigger_type not in exposed_triggers:
                if not any([insight.trigger_type.belongs_to_same_group(e) for e in exposed_triggers]):
                    insight.first = True
            insight.goal_targeted = list(set(insight.goal_targeted))
            insight.sport_names = list(set(insight.sport_names))
            insight.body_parts = list(set(insight.body_parts))
            insight.get_title_and_text()
            if insight.insight_type == InsightType.longitudinal:
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

        return insights, longitudinal_insights


def parent_group_exists(trigger_type, existing_triggers):
    for e in existing_triggers:
        if trigger_type.belongs_to_same_group(e):
            return True
    return False
