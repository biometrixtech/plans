import datetime
from models.insights import AthleteInsight, InsightType
from models.soreness import BodyPartSide, BodyPartLocation, Alert, AthleteGoal, AthleteGoalType
from models.trigger import TriggerType
from models.sport import SportName
from logic.alerts_processing import AlertsProcessing
from models.daily_plan import DailyPlan
from models.stats import AthleteStats
from models.athlete_trend import Trend
from utils import format_date


def test_insights_text():
    insight = AthleteInsight(TriggerType(0))
    insight.goal_targeted = ['Recover From Sport']
    insight.parent = False
    insight.first = False
    insight.body_parts = [BodyPartSide(BodyPartLocation(11), 1)]
    insight.sport_names = [SportName(13)]
    insight.add_data()
    assert insight.text != ""
    assert insight.title != ""


def test_aggregate_insights_first_exposure():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(14)  # no_hist_pain_pain_today_severity_1_2
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alert2 = Alert(goal)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 2)

    alerts = [alert1, alert2]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 1
    assert insights[0].first
    assert not insights[0].parent
    assert not insights[0].longitudinal
    assert insights[0].styling == 0


def test_aggregate_insights_no_alerts():
    current_date_time = datetime.datetime.now()

    alerts = []
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 0


def test_aggregate_insights_trigger_type_not_displayed():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(12)  # hist_sore_less_30_sore_today
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 0


def test_aggregate_insights_multiple_same_body_part():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(14)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alert2 = Alert(goal)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 1)
    exposed_triggers = []

    alerts = [alert1, alert2]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = exposed_triggers
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 1
    assert insights[0].first
    assert not insights[0].parent
    assert not insights[0].longitudinal
    assert len(insights[0].body_parts) == 1


def test_aggregate_insights_multiple_same_child():
    """
    multiple of the same trigger type fired for different body parts
    Should create a single child trigger
    :return:
    """
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(14)  # no_hist_pain_pain_today_severity_1_2
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)
    alert2 = Alert(goal)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 2)
    exposed_triggers = [TriggerType(14)]
    alerts = [alert1, alert2]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = exposed_triggers
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 1
    assert not insights[0].first
    assert not insights[0].parent
    assert not insights[0].longitudinal


def test_aggregate_insights_two_same_child_one_different_same_parent():
    """
    two trigger of type 14 (different body parts) and one of type 15 fired
    Should get a single parent insight with all three body parts
    :return:
    """
    current_date_time = datetime.datetime.now()
    goal1 = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal1.trigger_type = TriggerType(14)  # no_hist_pain_pain_today_severity_1_2
    alert1 = Alert(goal1)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)
    alert2 = Alert(goal1)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 2)

    goal2 = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal2.trigger_type = TriggerType(15)  # no_hist_pain_pain_today_severity_1_2
    alert3 = Alert(goal2)
    alert3.body_part = BodyPartSide(BodyPartLocation(7), 2)
    exposed_triggers = []

    alerts = [alert1, alert2, alert3]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = exposed_triggers
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 1
    assert insights[0].first
    assert insights[0].parent
    assert not insights[0].longitudinal
    assert len(insights[0].body_parts) == 3
    assert insights[0].styling == 1
    assert insights[0].parent_group == 2


def test_aggregate_insights_exposed():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(14)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]

    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = [TriggerType(14)]
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 1
    assert not insights[0].first
    assert not insights[0].parent
    assert not insights[0].longitudinal
    assert insights[0].insight_type == InsightType.response


def test_aggregate_insights_exposed_group():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(7)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]

    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = [TriggerType(8)]
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 1
    assert not insights[0].first
    assert not insights[0].parent
    assert insights[0].longitudinal


def test_aggregate_insights_group_priority():
    current_date_time = datetime.datetime.now()
    goal1 = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal1.trigger_type = TriggerType(14)
    alert1 = Alert(goal1)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)
    goal2 = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal2.trigger_type = TriggerType(15)
    alert2 = Alert(goal2)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1, alert2]

    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(insights) == 1
    assert insights[0].first
    assert insights[0].parent
    assert not insights[0].longitudinal
    assert insights[0].priority == 1


def test_aggregate_insights_longitutinal():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(7)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]

    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time - datetime.timedelta(days=5), alerts)
    assert len(insights) == 1
    assert insights[0].first
    assert not insights[0].parent
    assert insights[0].longitudinal
    assert insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)

    daily_plan.insights = []
    athlete_stats.exposed_triggers = [TriggerType(7)]
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, [])
    assert len(insights) == 1
    assert not insights[0].parent
    assert insights[0].longitudinal
    assert insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)


def test_aggregate_insights_cleared():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(7)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    existing_insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time - datetime.timedelta(days=5), alerts)
    assert len(existing_insights) == 1
    assert existing_insights[0].first
    assert not existing_insights[0].parent
    assert existing_insights[0].longitudinal
    assert existing_insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)

    daily_plan.insights = []
    athlete_stats.exposed_triggers = [TriggerType(7)]
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, [])
    assert len(insights) == 1
    assert not insights[0].parent
    assert insights[0].longitudinal
    assert insights[0].cleared
    assert insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)


def test_aggregate_insights_cleared_same_parent_group():
    current_date_time = datetime.datetime.now()
    goal1 = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal1.trigger_type = TriggerType(7)
    alert1 = Alert(goal1)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)
    goal2 = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal2.trigger_type = TriggerType(8)
    alert2 = Alert(goal2)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 2)

    alerts = [alert1, alert2]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    existing_insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time - datetime.timedelta(days=1), alerts)

    assert len(existing_insights) == 1
    assert existing_insights[0].first
    assert existing_insights[0].parent
    assert existing_insights[0].longitudinal
    assert existing_insights[0].start_date_time == current_date_time - datetime.timedelta(days=1)

    athlete_stats.exposed_triggers = [existing_insights[0].trigger_type]
    daily_plan.insights = []
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, [alert2])
    assert len(longitudinal_insights) == 1
    assert len(insights) == 2
    for insight in insights:
        insight.add_data()
    plan = DailyPlan(format_date(current_date_time))
    plan.insights = insights
    plan.sort_insights()
    assert longitudinal_insights[0] == insights[0]

    assert not insights[0].first
    assert not insights[0].parent

    assert insights[1].first
    assert insights[1].longitudinal
    assert insights[1].cleared
    assert insights[1].start_date_time == current_date_time - datetime.timedelta(days=1)


def test_aggregate_insights_cleared_one_body_part():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Pain', 0, AthleteGoalType(0))
    goal.trigger_type = TriggerType(16)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)
    alert2 = Alert(goal)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 2)

    alerts = [alert1, alert2]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    existing_insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time - datetime.timedelta(days=5), alerts)
    assert len(existing_insights) == 1
    assert existing_insights[0].first
    assert not existing_insights[0].parent
    assert existing_insights[0].longitudinal
    assert existing_insights[0].start_date_time == current_date_time - datetime.timedelta(days=5)
    assert len(existing_insights[0].body_parts) == 2

    athlete_stats.exposed_triggers = [TriggerType(16)]
    daily_plan.insights = []
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, [alert2])
    assert len(insights) == 2
    assert insights[0].longitudinal
    assert len(longitudinal_insights) == 1
    assert len(longitudinal_insights[0].body_parts) == 1
    assert longitudinal_insights[0].body_parts[0].side == 2
    assert not longitudinal_insights[0].cleared

    plan = DailyPlan(format_date(current_date_time))
    plan.insights = insights
    plan.sort_insights()
    assert not plan.insights[0].cleared
    assert plan.insights[1].cleared


def test_insights_ordering():
    insights = []
    current_date_time = datetime.datetime.now()
    insight1 = AthleteInsight(TriggerType(15))  # priority 1
    insight1.read = True
    insights.append(insight1)
    insight2 = AthleteInsight(TriggerType(1))  # priority 8
    insight2.read = True
    insights.append(insight2)
    insight3 = AthleteInsight(TriggerType(2))  # priority 8
    insights.append(insight3)
    # insight4 = AthleteInsight(TriggerType(3))  # priority 8
    # insight4.cleared = True
    # insights.append(insight4)
    insight5 = AthleteInsight(TriggerType(8))  # priority 7
    insight5.cleared = True
    insights.append(insight5)
    insight6 = AthleteInsight(TriggerType(16))  # priority 4
    insights.append(insight6)

    for insight in insights:
        insight.add_data()

    plan = DailyPlan(format_date(current_date_time))
    plan.insights = insights
    plan.sort_insights()
    assert plan.insights[0].trigger_type == TriggerType(16)  # highest priority left of unread ones
    assert plan.insights[1].trigger_type == TriggerType(8)  # second highest priority left of unread ones
    assert plan.insights[2].trigger_type == TriggerType(2)  # same priority as next. won tie breaker (not-cleared)
    # assert plan.insights[3].trigger_type == TriggerType(3)  # same priority as previous. lost tie breaker (cleared)
    assert plan.insights[3].trigger_type == TriggerType(15)  # read - higher priority
    assert plan.insights[4].trigger_type == TriggerType(1)  # read - lower priority


def test_trigger_type_equivalency():
    trigger1 = TriggerType(8)
    trigger2 = TriggerType(7)
    trigger3 = TriggerType(8)
    trigger4 = TriggerType(9)
    assert TriggerType.is_equivalent(trigger1, trigger2)
    assert TriggerType.is_equivalent(trigger1, trigger3)
    assert not TriggerType.is_equivalent(trigger1, trigger4)


def test_trend_add_data():
    trend = Trend(TriggerType(14))
    trend.body_parts = [BodyPartSide(BodyPartLocation(11), 1)]
    trend.add_data()
    assert trend.visualization_data.plot_legends[0].color.value == 2
    trend_json = trend.json_serialise()
    trend2 = Trend.json_deserialise(trend_json)
    assert trend2.visualization_type == trend.visualization_type


def test_trend_add_data_2():
    trend = Trend(TriggerType(2))
    trend.body_parts = [BodyPartSide(BodyPartLocation(11), 2)]
    trend.add_data()
    assert trend.visualization_data.plot_legends[0].color.value == 2
    trend_json = trend.json_serialise()
    trend2 = Trend.json_deserialise(trend_json)
    assert trend2.visualization_type == trend.visualization_type


def test_aggregate_trends_multiple_trends_same_body_part():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Soreness', 0, AthleteGoalType(1))
    goal.trigger_type = TriggerType(15)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alert2 = Alert(goal)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1, alert2]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.response.alerts) == 2
    assert len(trends.response.alerts[0].body_parts) == 1
    assert trends.response.alerts[0].trigger_type == TriggerType(15)


def test_aggregate_trends_multiple_trends_same_trigger_type_multiple_sports():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Soreness', 0, AthleteGoalType(1))
    goal.trigger_type = TriggerType(0)
    alert1 = Alert(goal)
    alert1.sport_name = SportName(17)

    alert2 = Alert(goal)
    alert2.sport_name = SportName(18)

    alerts = [alert1, alert2]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.stress.alerts) == 1
    assert len(trends.stress.alerts[0].body_parts) == 0
    assert trends.stress.alerts[0].trigger_type == TriggerType(0)


def test_aggregate_trends_multiple_doms():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Soreness', 0, AthleteGoalType(1))
    goal.trigger_type = TriggerType(11)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alert2 = Alert(goal)
    alert2.body_part = BodyPartSide(BodyPartLocation(11), 2)

    alerts = [alert1, alert2]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.response.alerts) == 2
    assert len(trends.response.alerts[0].body_parts) == 2
    assert trends.response.alerts[0].trigger_type == TriggerType(11)


def test_aggregate_trends_doms_yesterday():
    current_date_time = datetime.datetime.now()
    trend = Trend(TriggerType(11))
    goal = AthleteGoal('Care for Soreness', 0, AthleteGoalType(1))
    goal.trigger_type = TriggerType(11)
    alert = Alert(goal)
    alert.body_part = BodyPartSide(BodyPartLocation(11), 2)

    alerts = [alert]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    athlete_stats.longitudinal_trends = [trend]
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.response.alerts) == 2
    assert trends.response.alerts[0].trigger_type == TriggerType(203)
    assert trends.response.alerts[1].trigger_type == TriggerType(202)


def test_aggregate_trends_cleared_trend_doms():
    current_date_time = datetime.datetime.now()
    trend = Trend(TriggerType(11))
    trend.add_data()
    goal = AthleteGoal('Care for Soreness', 0, AthleteGoalType(1))
    goal.trigger_type = TriggerType(8)
    alert = Alert(goal)
    alert.body_part = BodyPartSide(BodyPartLocation(11), 2)

    alerts = [alert]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    athlete_stats.longitudinal_trends = [trend]
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.response.alerts) == 2
    assert trends.response.alerts[0].trigger_type == TriggerType(8)
    assert trends.response.alerts[1].trigger_type == TriggerType(203)


def test_aggregate_trends_cleared_trend_not_doms():
    current_date_time = datetime.datetime.now()
    trend = Trend(TriggerType(8))
    trend.add_data()
    goal = AthleteGoal('Care for Soreness', 0, AthleteGoalType(1))
    goal.trigger_type = TriggerType(7)
    alert = Alert(goal)
    alert.body_part = BodyPartSide(BodyPartLocation(11), 2)

    alerts = [alert]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    athlete_stats.longitudinal_trends = [trend]
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.response.alerts) == 3
    assert trends.response.alerts[0].trigger_type == TriggerType(8)
    assert trends.response.alerts[1].trigger_type == TriggerType(7)
    assert trends.response.alerts[2].trigger_type == TriggerType(203)


def test_aggregate_trends_cleared_trend_different_body_part_today():
    current_date_time = datetime.datetime.now()
    trend = Trend(TriggerType(7))
    trend.body_parts = [BodyPartSide(BodyPartLocation(11), 2)]
    trend.add_data()
    goal = AthleteGoal('Care for Soreness', 0, AthleteGoalType(1))
    goal.trigger_type = TriggerType(7)
    alert = Alert(goal)
    alert.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    athlete_stats.longitudinal_trends = [trend]
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.response.alerts) == 3
    assert trends.response.alerts[0].trigger_type == TriggerType(7)
    assert trends.response.alerts[0].cleared
    assert trends.response.alerts[1].trigger_type == TriggerType(7)
    assert not trends.response.alerts[1].cleared
    assert trends.response.alerts[2].trigger_type == TriggerType(203)


def test_aggregate_trends_no_alerts():
    current_date_time = datetime.datetime.now()

    alerts = []
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    athlete_stats.longitudinal_trends = []
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.stress.alerts) == 1
    assert len(trends.response.alerts) == 2
    assert len(trends.biomechanics.alerts) == 2


def test_aggregate_trends_trigger_type_not_present_in_trends():
    current_date_time = datetime.datetime.now()
    goal = AthleteGoal('Care for Soreness', 0, AthleteGoalType(1))
    goal.trigger_type = TriggerType(12)
    alert1 = Alert(goal)
    alert1.body_part = BodyPartSide(BodyPartLocation(11), 1)

    alerts = [alert1]
    event_date_time = current_date_time
    daily_plan = DailyPlan(format_date(event_date_time))
    athlete_stats = AthleteStats('test_user')
    athlete_stats.exposed_triggers = []
    insights, longitudinal_insights, trends = AlertsProcessing(daily_plan, athlete_stats).aggregate_alerts(event_date_time, alerts)
    assert len(trends.response.alerts) == 2
    assert trends.response.alerts[0].trigger_type == TriggerType(203)
    assert trends.response.alerts[1].trigger_type == TriggerType(202)
