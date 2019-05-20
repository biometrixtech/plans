from models.insights import AthleteInsight, InsightType
from models.soreness import BodyPartSide
from models.trigger import TriggerType
from models.athlete_trend import AthleteTrends


class AlertsProcessing(object):
    # def __init__(self, daily_plan, athlete_stats):
    #     self.daily_plan = daily_plan
    #     self.athlete_stats = athlete_stats

    @classmethod
    def aggregate_alerts(cls, trigger_date_time, alerts, previous_insights, exposed_triggers, longitudinal_insights):

        trends = AthleteTrends()
        insights = cls.combine_alerts_to_insights(alerts, trends)
        if TriggerType(9) in exposed_triggers:
            insights = [insight for insight in insights if insight.trigger_type != TriggerType(9)]
        insights, longitudinal_insights = cls.clear_insight(insights, longitudinal_insights)

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
        insights = cls.combine_new_insights_with_previous(insights, previous_insights)

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

    @classmethod
    def combine_alerts_to_insights(cls, alerts, trends):
        existing_triggers = []
        insights = []
        for alert in alerts:
            insight_type = InsightType(TriggerType.get_insight_type(alert.goal.trigger_type))
            if insight_type == InsightType.stress:
                trends.stress.alerts.append(alert)
                trends.stress.goals.append(alert.goal.text)
            elif insight_type == InsightType.response:
                trends.response.alerts.append(alert)
                trends.response.goals.append(alert.goal.text)
            elif insight_type == InsightType.biomechanics:
                trends.biomechanics.alerts.append(alert)
                trends.biomechanics.goals.append(alert.goal.text)
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
