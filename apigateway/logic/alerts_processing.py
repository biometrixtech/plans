from models.insights import AthleteInsight
from models.soreness import  TriggerType


class AlertsProcessing(object):

    @classmethod
    def aggregate_alerts(cls, alerts, displayed_alerts):
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

        for insight in insights:
            if insight.trigger_type not in displayed_alerts:
                insight.first = True
            # if len(insight.trigger_type) > 0:
            #     insight.parent = True
            insight.goal_targeted = list(set(insight.goal_targeted))
            insight.sport_names = list(set(insight.sport_names))
            insight.body_parts = list(set(insight.body_parts))
            insight.get_title_and_text()
        return insights


grouped_triggers = {0: [TriggerType(6), TriggerType(7), TriggerType(8)],
                    1: [TriggerType(10), TriggerType(11)]}
