from models.insights import AthleteInsight, InsightType
from models.soreness import TriggerType, BodyPartSide


class AlertsProcessing(object):

    @classmethod
    def aggregate_alerts(cls, trigger_date_time, alerts, previous_insights, exposed_triggers, longitudinal_insights):

        insights = cls.combine_alerts_to_insights(alerts)
        if TriggerType(9) in exposed_triggers:
            insights = [insight for insight in insights if insight.trigger_type != TriggerType(9)]
        insights, longitudinal_insights = cls.clear_insight(insights, longitudinal_insights)

        existing_longitudinal_trigger_types = [insight.trigger_type for insight in longitudinal_insights]
        for insight in insights:
            if insight.trigger_type not in exposed_triggers:
                if not any([AthleteInsight.get_parent_group(insight.trigger_type) == AthleteInsight.get_parent_group(e) for e in exposed_triggers]):
                    insight.first = True
            insight.goal_targeted = list(set(insight.goal_targeted))
            insight.sport_names = list(set(insight.sport_names))
            insight.body_parts = [BodyPartSide.json_deserialise(dict(t)) for t in {tuple(d.json_serialise().items()) for d in insight.body_parts}]
            insight.add_data()
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
        insights = cls.combine_new_insights_with_previous(insights, previous_insights)

        return insights, longitudinal_insights

    @classmethod
    def clear_insight(cls, new_insights, existing_longitudinal_insights):
        current_trigger_types = [insight.trigger_type for insight in new_insights]
        for l_insight in existing_longitudinal_insights:
            if l_insight.trigger_type not in current_trigger_types:  # if trigger type does not exist, everything was cleared
                l_insight.cleared = True
                new_insights.append(l_insight)
            else:  # if it exists make check to see if body parts contributing to existing insight were cleared
                current_insight = [insight for insight in new_insights if insight.trigger_type == l_insight.trigger_type][0]
                cleared_parts = []
                current_body_parts = [d.json_serialise() for d in current_insight.body_parts]
                for body_part in l_insight.body_parts:
                    if body_part.json_serialise() not in current_body_parts:
                        cleared_parts.append(body_part)
                if len(cleared_parts) > 0:   # check if any body part was cleared
                    l_insight.cleared = True
                    l_insight.body_parts = cleared_parts
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

    @classmethod
    def combine_alerts_to_insights(cls, alerts):
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
            elif alert.goal.trigger_type.is_grouped_trigger() and cls.parent_group_exists(alert.goal.trigger_type, existing_triggers):
                insight = [insight for insight in insights if AthleteInsight.get_parent_group(insight.trigger_type) == AthleteInsight.get_parent_group(alert.goal.trigger_type)][0]
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

    @classmethod
    def parent_group_exists(cls, trigger_type, existing_triggers):
        for e in existing_triggers:
            if AthleteInsight.get_parent_group(trigger_type) == AthleteInsight.get_parent_group(e):
                return True
        return False
