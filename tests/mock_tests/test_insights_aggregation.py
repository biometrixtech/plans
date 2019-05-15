import datetime
from models.insights import AthleteInsight, InsightType
from models.soreness import TriggerType, BodyPartSide, BodyPartLocation, Alert, AthleteGoal, AthleteGoalType
from models.sport import SportName
from logic.alerts_processing import AlertsProcessing


def test_insights_text():
    insight = AthleteInsight(TriggerType(20))
    insight.goal_targeted = ['Recover From Sport']
    insight.parent = False
    insight.first = False
    insight.body_parts = [BodyPartSide(BodyPartLocation(11), 1)]
    insight.sport_names = [SportName(13)]
    insight.get_title_and_text()
    assert insight.text != ""
    assert insight.title == "Mitigate Overuse Injury"


def test_aggregate_alerts():
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(14)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alert2 = Alert(goal)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 2)
    exposed_triggers = []

    alerts = [alert1, alert2]
    insights = AlertsProcessing.aggregate_alerts(datetime.datetime.now(), alerts, exposed_triggers, [])
    assert len(insights) == 1
    assert insights[0].first == True
    assert insights[0].parent == False
    assert insights[0].insight_type == InsightType.daily


def test_aggregate_alerts_exposed():
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(14)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]
    insights = AlertsProcessing.aggregate_alerts(datetime.datetime.now(), alerts, [TriggerType(14)], [])
    assert len(insights) == 1
    assert insights[0].first == False
    assert insights[0].parent == False
    assert insights[0].insight_type == InsightType.daily


def test_aggregate_alerts_exposed_group():
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(6)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]
    insights = AlertsProcessing.aggregate_alerts(datetime.datetime.now(), alerts, [TriggerType(7)], [])
    assert len(insights) == 1
    assert insights[0].first == False
    assert insights[0].parent == False
    assert insights[0].insight_type == InsightType.longitudinal

def test_aggregate_alerts_longitutinal():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(6)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]
    insights = AlertsProcessing.aggregate_alerts(current_date_time - datetime.timedelta(days=5), alerts, [], [])
    assert len(insights) == 1
    assert insights[0].first == True
    assert insights[0].parent == False
    assert insights[0].insight_type == InsightType.longitudinal
    assert insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)

    insights = AlertsProcessing.aggregate_alerts(current_date_time, alerts, [TriggerType(6)], insights)
    assert len(insights) == 1
    assert insights[0].first == False
    assert insights[0].parent == False
    assert insights[0].insight_type == InsightType.longitudinal
    assert insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)


def test_aggregate_alerts_cleared():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(6)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]
    existing_insights = AlertsProcessing.aggregate_alerts(current_date_time - datetime.timedelta(days=5), alerts, [], [])
    assert len(existing_insights) == 1
    assert existing_insights[0].first == True
    assert existing_insights[0].parent == False
    assert existing_insights[0].insight_type == InsightType.longitudinal
    assert existing_insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)

    insights = AlertsProcessing.aggregate_alerts(current_date_time, [], [TriggerType(6)], existing_insights)
    assert len(insights) == 1
    assert insights[0].first == True
    assert insights[0].parent == False
    assert insights[0].insight_type == InsightType.longitudinal
    assert insights[0].cleared == True
    assert insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)
