import datetime
from utils import format_datetime, format_date
import testing_utils as utils


def test_get_plan_readiness_not_completed():
    if utils.HEADERS['Authorization'] is None:
        utils.login_user(utils.USER['email'])
        utils.reset_user()
    event_date = datetime.datetime.now()
    response1 = utils.get_plan(format_date(event_date), format_datetime(event_date))
    data = response1.json()
    response2 = utils.get_previous_soreness(event_date + datetime.timedelta(seconds=15))
    readiness2 = response2.json()['readiness']

    assert response1.status_code == 200
    assert response2.status_code == 200
    assert len(data['daily_plans']) == 1
    plan = data['daily_plans'][0]
    readiness1 = data['readiness']
    assert not plan['daily_readiness_survey_completed']
    assert len(readiness1) > 0
    assert readiness1 == readiness2
    assert len(readiness1['clear_candidates']) == 1
    assert len(readiness1['hist_sore_status']) == 1


def test_get_plan_one_plan_readiness_completed():
    if utils.HEADERS['Authorization'] is None:
        utils.login_user(utils.USER['email'])
        utils.reset_user()
    event_date = datetime.datetime.now() - datetime.timedelta(days=2)
    response = utils.get_plan(format_date(event_date), format_datetime(event_date))
    data = response.json()
    readiness = data['readiness']

    assert response.status_code == 200
    assert len(data['daily_plans']) == 1
    plan = data['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert len(readiness) == 0


# 4 days ago
def test_start_and_complete_pre_active_rest():
    if utils.HEADERS['Authorization'] is None:
        utils.login_user(utils.USER['email'])
        utils.reset_user()
    event_date = datetime.datetime.now() - datetime.timedelta(days=4)
    plan = utils.get_plan(format_date(event_date), format_datetime(event_date)).json()['daily_plans'][0]

    assert plan['pre_active_rest'] is not None
    assert plan['landing_screen'] == 0

    response2 = utils.start_recovery(event_date + datetime.timedelta(minutes=2), recovery_type='pre')
    assert response2.status_code == 200

    response3 = utils.complete_recovery(event_date + datetime.timedelta(minutes=12),
                                        completed_exercises=[plan["pre_active_rest"]["inhibit_exercises"][0]['library_id']],
                                        recovery_type='pre')
    assert response3.status_code == 202
    plan = response3.json()["daily_plans"][0]
    assert plan["pre_active_rest_completed"]
    assert plan["pre_active_rest"]["completed"]
    assert plan["landing_screen"] == 1


# two days ago
def test_submit_one_session_train_later():
    if utils.HEADERS['Authorization'] is None:
        utils.login_user(utils.USER['email'])
        utils.reset_user()
    event_date = datetime.datetime.now() - datetime.timedelta(days=2)
    response = utils.submit_session(format_datetime(event_date),
                                    sport_name=72,
                                    duration=30,
                                    rpe=5,
                                    soreness=[],
                                    clear_candidates=[],
                                    sessions_planned=True)

    assert response.status_code == 201
    assert len(response.json()['daily_plans']) == 1
    plan = response.json()['daily_plans'][0]
    assert len(plan['training_sessions']) == 2
    assert plan['post_active_rest'] is None
    assert plan['landing_screen'] == 0
    assert plan['pre_active_rest'] is not None


# two days ago
def test_submit_one_session_not_train_later():
    if utils.HEADERS['Authorization'] is None:
        utils.login_user(utils.USER['email'])
        utils.reset_user()
    event_date = datetime.datetime.now() - datetime.timedelta(days=2)
    response = utils.submit_session(format_datetime(event_date),
                                    sport_name=72,
                                    duration=30,
                                    rpe=5,
                                    soreness=[],
                                    clear_candidates=[],
                                    sessions_planned=False)

    assert response.status_code == 201
    assert len(response.json()['daily_plans']) == 1
    plan = response.json()['daily_plans'][0]
    assert len(plan['training_sessions']) == 3
    assert plan['post_active_rest'] is not None
    assert plan['landing_screen'] == 2


# today
def test_submit_readiness_one_soreness():
    if utils.HEADERS['Authorization'] is None:
        utils.login_user(utils.USER['email'])
        utils.reset_user()
    event_date = datetime.datetime.now()
    soreness = [utils.get_soreness(body_part=14, side=1, pain=False, severity=2, movement=1)]
    response = utils.submit_readiness(event_date,
                                      soreness=soreness,
                                      clear_candidates=[],
                                      sessions=[])

    assert response.status_code == 201
    plan = response.json()['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert plan['pre_active_rest'] is not None
    assert plan['post_active_rest'] is None
    assert plan['post_active_rest'] is None
    assert plan['landing_screen'] == 0


# one day later
def test_submit_readiness_answer_clear_candidates_clear():
    if utils.HEADERS['Authorization'] is None:
        utils.login_user(utils.USER['email'])
        utils.reset_user()
    event_date = datetime.datetime.now() + datetime.timedelta(days=1)
    response = utils.get_plan(format_date(event_date), format_datetime(event_date))
    assert response.status_code == 200
    assert len(response.json()['readiness']) > 0
    readiness = response.json()['readiness']
    assert len(readiness['hist_sore_status']) == 1
    assert len(readiness['clear_candidates']) == 1
    soreness = readiness['clear_candidates'][0]
    clear_candidates = [utils.get_soreness(body_part=soreness['body_part'],
                                           side=soreness['side'],
                                           pain=soreness['pain'],
                                           severity=0,
                                           status=soreness['status'])]
    response2 = utils.submit_readiness(event_date,
                                       soreness=[],
                                       clear_candidates=clear_candidates,
                                       sessions=[])

    assert response2.status_code == 201
    plan = response2.json()['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert plan['pre_active_rest'] is not None
    assert plan['post_active_rest'] is None
    assert plan['landing_screen'] == 0

    response3 = utils.get_previous_soreness(event_date)
    assert response3.status_code == 200
    readiness2 = response3.json()['readiness']
    assert len(readiness2) > 0
    assert len(readiness2['hist_sore_status']) == 1
    assert len(readiness2['clear_candidates']) == 0
    utils.reset_user()


# one day later
def test_submit_readiness_answer_clear_candidates_not_clear_not_train_later():
    if utils.HEADERS['Authorization'] is None:
        utils.login_user(utils.USER['email'])
        utils.reset_user()
    event_date = datetime.datetime.now() + datetime.timedelta(days=1)
    response = utils.get_plan(format_date(event_date), format_datetime(event_date))
    assert response.status_code == 200
    assert len(response.json()['readiness']) > 0
    readiness = response.json()['readiness']
    assert len(readiness['hist_sore_status']) == 1
    assert len(readiness['clear_candidates']) == 1
    soreness = readiness['clear_candidates'][0]
    clear_candidates = [utils.get_soreness(body_part=soreness['body_part'],
                                           side=soreness['side'],
                                           pain=soreness['pain'],
                                           severity=1,
                                           status=soreness['status'])]
    response2 = utils.submit_readiness(event_date,
                                       soreness=[],
                                       clear_candidates=clear_candidates,
                                       sessions=[],
                                       sessions_planned=False)

    assert response2.status_code == 201
    plan = response2.json()['daily_plans'][0]

    assert plan['daily_readiness_survey_completed']
    assert plan['pre_active_rest'] is None
    assert plan['post_active_rest'] is not None
    assert plan['landing_screen'] == 2

    response3 = utils.get_previous_soreness(event_date)
    assert response3.status_code == 200
    readiness2 = response3.json()['readiness']
    assert len(readiness2) > 0
    assert len(readiness2['hist_sore_status']) == 2
    assert len(readiness2['clear_candidates']) == 0
    utils.reset_user()


# two days later
# def test_submit_readiness_max_pain_no_prep():
#     if utils.HEADERS['Authorization'] is None:
#         utils.login_user(utils.USER['email'])
#         utils.reset_user()
#     event_date = datetime.datetime.now() + datetime.timedelta(days=2)
#     soreness = [utils.get_soreness(body_part=14, side=1, pain=True, severity=3, movement=5)]
#     response = utils.submit_readiness(event_date,
#                                       soreness=soreness,
#                                       clear_candidates=[],
#                                       sessions=[])
#
#     assert response.status_code == 201
#     plan = response.json()['daily_plans'][0]
#
#     assert plan['daily_readiness_survey_completed']
#     assert plan['pre_recovery']['minutes_duration'] == 15
#     assert len(plan['pre_recovery']['inhibit_exercises']) == len(plan['pre_recovery']['lengthen_exercises']) == len(plan['pre_recovery']['activate_exercises']) == 0
#     assert plan['landing_screen'] == 0
