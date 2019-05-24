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


def validate_pre_active_rest_exercise_counts(daily_plan, inhibit_present, static_stretch_present,
                                             active_stretch_present, isolated_activate_present,
                                             static_integrate_present):

    if (not inhibit_present and not static_stretch_present and not active_stretch_present
            and not isolated_activate_present and not static_integrate_present):
        assert len(daily_plan.pre_active_rest) == 0
    else:
        assert len(daily_plan.pre_active_rest) == 1
        assert (len(daily_plan.pre_active_rest[0].inhibit_exercises) > 0) is inhibit_present
        assert (len(daily_plan.pre_active_rest[0].active_stretch_exercises) > 0) is active_stretch_present
        assert (len(daily_plan.pre_active_rest[0].static_stretch_exercises) > 0) is static_stretch_present
        assert (len(daily_plan.pre_active_rest[0].isolated_activate_exercises) > 0) is isolated_activate_present
        assert (len(daily_plan.pre_active_rest[0].static_integrate_exercises) > 0) is static_integrate_present


def validate_post_active_rest_exercise_counts(daily_plan, inhibit_present, static_stretch_present,
                                             isolated_activate_present, static_integrate_present):
    if (not inhibit_present and not static_stretch_present and not isolated_activate_present
            and not static_integrate_present):
        assert len(daily_plan.post_active_rest) == 0
    else:
        assert len(daily_plan.post_active_rest) == 1
        assert (len(daily_plan.post_active_rest[0].inhibit_exercises) > 0) is inhibit_present
        assert (len(daily_plan.post_active_rest[0].static_stretch_exercises) > 0) is static_stretch_present
        assert (len(daily_plan.post_active_rest[0].isolated_activate_exercises) > 0) is isolated_activate_present
        assert (len(daily_plan.post_active_rest[0].static_integrate_exercises) > 0) is static_integrate_present


def validate_biomechanics(daily_plan, expected_triggers):
    pass


def validate_response(daily_plan, expected_triggers):
    for t in expected_triggers:
        response = list(
            i for i in daily_plan.trends.response.alerts if i.insight_type == InsightType.response and i.trigger_type == t)
        assert len(response) > 0


def validate_response_chart_data(daily_plan, trigger_type, last_expected_values):

    response = list(
        i for i in daily_plan.trends.response.alerts if
        i.insight_type == InsightType.response and i.trigger_type == trigger_type)[0]

    last_expected_values_counter = 0
    for v in range(14 - len(last_expected_values), 14):
        assert response.data[v].value == last_expected_values[last_expected_values_counter]
        last_expected_values_counter += 1


def validate_stress(daily_plan, expected_triggers):
    for t in expected_triggers:
        response = list(
            i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress and i.trigger_type == t)
        assert len(response) > 0


def validate_stress_chart_data(daily_plan, trigger_type, last_expected_values):

    stress = list(
        i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress and i.trigger_type == trigger_type)[0]

    last_expected_values_counter = 0
    for v in range(14-len(last_expected_values), 14):
        assert stress.data[v].value == last_expected_values[last_expected_values_counter]
        last_expected_values_counter += 1


def validate_insights(daily_plan, expected_types, expected_triggers, expected_first, expected_cleared):

    assert len(daily_plan.insights) == len(expected_types)
    assert len(daily_plan.insights) == len(expected_triggers)
    assert len(daily_plan.insights) == len(expected_first)
    assert len(daily_plan.insights) == len(expected_cleared)

    for t in range(0, len(expected_triggers)):

        response = list(i for i in daily_plan.insights if i.insight_type == expected_types[t]
                        and i.trigger_type == expected_triggers[t] and i.first == expected_first[t]
                        and i.cleared == expected_cleared[t])
        assert len(response) > 0


def validate_response_cta_names(daily_plan, cta_name_list):

    assert len(daily_plan.trends.response.cta) == len(cta_name_list)

    for t in cta_name_list:
        assert len(list(c for c in daily_plan.trends.response.cta if c.name == t)) == 1


def validate_daily_plan(daily_plan, event_date):

    target_date = base_date - timedelta(days=35)

    if event_date == target_date + timedelta(days=3):

        # modalities
        assert daily_plan.cold_water_immersion is None
        assert daily_plan.heat is None
        assert daily_plan.ice is None

        validate_pre_active_rest_exercise_counts(daily_plan, True, True, True, False, False)
        validate_post_active_rest_exercise_counts(daily_plan, False, False, False, False)

        # insights
        validate_insights(daily_plan,
                          expected_types=[InsightType.response, InsightType.stress],
                          expected_triggers=[TriggerType.no_hist_pain_pain_today_severity_1_2,
                                             TriggerType.high_volume_intensity],
                          expected_first=[True, True],
                          expected_cleared=[False, False])

        # response
        validate_response(daily_plan, [TriggerType.no_hist_pain_pain_today_severity_1_2])

        validate_response_chart_data(daily_plan, TriggerType.no_hist_pain_pain_today_severity_1_2, [0, 0, 1])

        validate_response_cta_names(daily_plan, ['mobilize', 'ice'])

        # stress
        validate_stress(daily_plan, [TriggerType.high_volume_intensity])

        validate_stress_chart_data(daily_plan, TriggerType.high_volume_intensity, [False, False, True])

    elif event_date == target_date + timedelta(days=5):
        recover_alert = list(i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress)[0]
        assert recover_alert.trigger_type == TriggerType.high_volume_intensity

        assert recover_alert.data[11].value is True
        assert recover_alert.data[12].value is False
        assert recover_alert.data[13].value is True

    elif event_date == target_date + timedelta(days=7):
        recover_alert = list(i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress)[0]
        assert recover_alert.trigger_type == TriggerType.high_volume_intensity

        assert recover_alert.data[9].value is True
        assert recover_alert.data[10].value is False
        assert recover_alert.data[11].value is True
        assert recover_alert.data[12].value is False
        assert recover_alert.data[13].value is True

    elif event_date == target_date + timedelta(days=9):
        recover_alert = list(i for i in daily_plan.trends.stress.alerts if i.insight_type == InsightType.stress)[0]
        assert recover_alert.trigger_type == TriggerType.high_volume_intensity

        assert recover_alert.data[7].value is True
        assert recover_alert.data[8].value is False
        assert recover_alert.data[9].value is True
        assert recover_alert.data[10].value is False
        assert recover_alert.data[11].value is True
        assert recover_alert.data[12].value is False
        assert recover_alert.data[13].value is True

    elif event_date == target_date + timedelta(days=13):
        assert len(daily_plan.trends.stress.alerts) == 0

