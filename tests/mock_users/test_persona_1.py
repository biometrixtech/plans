from tests.mock_users.persona import Persona
from tests.mock_users.create_persona import login_user
import soreness_history as sh
from datetime import datetime, timedelta
from utils import format_date, format_datetime
from models.insights import InsightType
from models.trigger import TriggerType

base_date = datetime.now()

def test_a_35_day_life_in_a_day():

    soreness_history = []
    right_knee_persistent2_question = sh.create_body_part_history(sh.persistent2_question(), 7, 2, True)
    soreness_history.append(right_knee_persistent2_question)
    left_knee_acute_pain_no_question = sh.create_body_part_history(sh.acute_pain_no_question(), 7, 1, True)
    soreness_history.append(left_knee_acute_pain_no_question)
    user_id = login_user("dipesh+persona1@fathomai.com")
    print(user_id)
    persona1 = Persona(user_id)
    persona1.soreness_history = soreness_history
    persona1.clear_user()

    days = 35

    event_date = base_date - timedelta(days=days)
    persona1.update_stats(event_date)

    for i in range(days):
        # date_time = format_datetime(event_date)
        today_date = format_date(event_date)
        date_time = event_date
        persona1.update_stats(event_date)
        soreness = []
        for body_part in persona1.soreness_history:
            if body_part['severity'][i] is not None:
                soreness.append({'body_part': body_part['body_part'],
                                 'side': body_part['side'],
                                 'pain': body_part['pain'],
                                 'severity': body_part['severity'][i]})

        if len(soreness) > 0:
            readiness_data = {'date_time': format_datetime(date_time),
                              'soreness': soreness}
            persona1.create_readiness(readiness_data)
            persona1.create_plan(event_date)
            validate_daily_plan(persona1.daily_plan, event_date)
            exercise_list = [ex.exercise.id for ex in persona1.daily_plan.pre_active_rest[0].inhibit_exercises.values()]
            persona1.complete_exercises(exercise_list, format_datetime(event_date + timedelta(hours=1)))
            print(today_date)

        event_date = event_date + timedelta(days=1)


def validate_daily_plan(daily_plan, event_date):

    if event_date==base_date - timedelta(days=32):
        assert daily_plan.cold_water_immersion is None
        assert daily_plan.heat is None
        assert daily_plan.ice is None
        assert len(daily_plan.insights) == 2
        assert daily_plan.insights[0].cleared is False
        assert daily_plan.insights[0].first is True
        assert daily_plan.insights[1].cleared is False
        assert daily_plan.insights[1].first is True

        response = list(i for i in daily_plan.insights if i.insight_type == InsightType.response)[0]
        assert response.trigger_type == TriggerType.no_hist_pain_pain_today_severity_1_2

        recover = list(i for i in daily_plan.insights if i.insight_type == InsightType.stress)[0]
        assert recover.trigger_type == TriggerType.high_volume_intensity

        assert len(daily_plan.post_active_rest) == 0
        assert len(daily_plan.pre_active_rest) == 1
        assert len(daily_plan.pre_active_rest[0].inhibit_exercises) > 0
        assert len(daily_plan.pre_active_rest[0].active_stretch_exercises) > 0
        assert len(daily_plan.pre_active_rest[0].static_stretch_exercises) > 0
        assert len(daily_plan.pre_active_rest[0].isolated_activate_exercises) == 0
        assert len(daily_plan.pre_active_rest[0].static_integrate_exercises) == 0
        assert len(daily_plan.trends.response.cta) == 2

        response_alert = list(i for i in daily_plan.trends.response.alerts if i.insight_type == InsightType.response and
                        response.trigger_type == TriggerType.no_hist_pain_pain_today_severity_1_2)[0]

        assert response_alert.data[11].value == 0
        assert response_alert.data[12].value == 0
        assert response_alert.data[13].value == 1

        assert len(list(c for c in daily_plan.trends.response.cta if c.name == 'mobilize')) == 1
        assert len(list(c for c in daily_plan.trends.response.cta if c.name == 'ice')) == 1

        recover_alert = list(i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress)[0]
        assert recover_alert.trigger_type == TriggerType.high_volume_intensity

        assert recover_alert.data[11].value is False
        assert recover_alert.data[12].value is False
        assert recover_alert.data[13].value is True
    elif event_date == base_date - timedelta(days=30):
        recover_alert = list(i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress)[0]
        assert recover_alert.trigger_type == TriggerType.high_volume_intensity

        assert recover_alert.data[11].value is True
        assert recover_alert.data[12].value is False
        assert recover_alert.data[13].value is True

    elif event_date == base_date - timedelta(days=28):
        recover_alert = list(i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress)[0]
        assert recover_alert.trigger_type == TriggerType.high_volume_intensity

        assert recover_alert.data[9].value is True
        assert recover_alert.data[10].value is False
        assert recover_alert.data[11].value is True
        assert recover_alert.data[12].value is False
        assert recover_alert.data[13].value is True

    elif event_date == base_date - timedelta(days=26):
        recover_alert = list(i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress)[0]
        assert recover_alert.trigger_type == TriggerType.high_volume_intensity

        assert recover_alert.data[7].value is True
        assert recover_alert.data[8].value is False
        assert recover_alert.data[9].value is True
        assert recover_alert.data[10].value is False
        assert recover_alert.data[11].value is True
        assert recover_alert.data[12].value is False
        assert recover_alert.data[13].value is True

    elif event_date == base_date - timedelta(days=22):
        assert len(daily_plan.trends.stress.alerts) == 0

