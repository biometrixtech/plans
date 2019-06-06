# import logic.training_plan_management as tpm
# from tests.mocks.mock_datastore_collection import DatastoreCollection
# from models.daily_plan import DailyPlan
#
#
#
# def create_prep_recovery(recovery, impact_score, minutes):
#     recovery.impact_score = impact_score
#     recovery.goal_text = "Text generated"
#     recovery.display_exercises = True
#     recovery.duration_minutes = minutes
#
# def training_plan_manager():
#     mgr = tpm.TrainingPlanManager("test", DatastoreCollection())
#     return mgr
#
#
# def test_screen_no_readiness():
#     daily_plan = DailyPlan('2018-12-11')
#     land_screen, nav_bar = daily_plan.define_landing_screen()
#     assert land_screen == 0.0
#
#
# def test_screen_only_prep_present_not_completed():
#     daily_plan = DailyPlan('2018-12-11')
#     daily_plan.daily_readiness_survey = '2018-12-11'
#     create_prep_recovery(daily_plan.pre_recovery, 3, 12)
#     land_screen, nav_bar = daily_plan.define_landing_screen()
#     assert land_screen == 0.0
#
#
# # def test_screen_only_prep_present_low_impact_score_no_exercises():
# #     daily_plan = DailyPlan('2018-12-11')
# #     daily_plan.daily_readiness_survey = '2018-12-11'
# #     create_prep_recovery(daily_plan.pre_recovery, 1.3, 0.0)
# #     land_screen, nav_bar = daily_plan.define_landing_screen()
# #     assert land_screen == 0.0
# #     assert nav_bar == 1.0
#
# # def test_screen_only_prep_present_low_impact_score_no_exercises_training_session_present():
# #     daily_plan = DailyPlan('2018-12-11')
# #     daily_plan.daily_readiness_survey = '2018-12-11'
# #     create_prep_recovery(daily_plan.pre_recovery, 1.3, 0.0)
# #     daily_plan.training_sessions = ['test']
# #     daily_plan.pre_recovery.display_exercises = False
# #     land_screen, nav_bar = daily_plan.define_landing_screen()
# #     assert land_screen == 0.0
# #     assert nav_bar == 1.0
#
# def test_screen_only_prep_present_high_impact_score_no_exercises():
#     daily_plan = DailyPlan('2018-12-11')
#     daily_plan.daily_readiness_survey = '2018-12-11'
#     create_prep_recovery(daily_plan.pre_recovery, 4, 0.0)
#     land_screen, nav_bar = daily_plan.define_landing_screen()
#     assert land_screen == 0.0
#
#
# def test_screen_only_prep_present_completed():
#     daily_plan = DailyPlan('2018-12-11')
#     daily_plan.daily_readiness_survey = '2018-12-11'
#     create_prep_recovery(daily_plan.pre_recovery, 3, 12)
#     daily_plan.pre_recovery.display_exercises = False
#     land_screen, nav_bar = daily_plan.define_landing_screen()
#     assert land_screen == 1.0
#
#
# def test_screen_only_recovery_present():
#     daily_plan = DailyPlan('2018-12-11')
#     daily_plan.daily_readiness_survey = '2018-12-11'
#     create_prep_recovery(daily_plan.post_recovery, 3, 12)
#     land_screen, nav_bar = daily_plan.define_landing_screen()
#     assert land_screen == 2.0
#
# #
# # def test_screen_only_recovery_present_low_impact_score():
# #     daily_plan = DailyPlan('2018-12-11')
# #     daily_plan.daily_readiness_survey = '2018-12-11'
# #     create_prep_recovery(daily_plan.post_recovery, 1.4, 0.0)
# #     daily_plan.training_sessions = ['test']
# #     daily_plan.post_recovery.display_exercises = False
# #     land_screen, nav_bar = daily_plan.define_landing_screen()
# #     assert land_screen == 2.0
# #     assert nav_bar is None
#
#
# def test_screen_only_recovery_present_high_impact_score():
#     daily_plan = DailyPlan('2018-12-11')
#     daily_plan.daily_readiness_survey = '2018-12-11'
#     create_prep_recovery(daily_plan.post_recovery, 5, 0.0)
#     land_screen, nav_bar = daily_plan.define_landing_screen()
#     assert land_screen == 2.0
#
# def test_screen_only_recovery_present_completed():
#     daily_plan = DailyPlan('2018-12-11')
#     daily_plan.daily_readiness_survey = '2018-12-11'
#     create_prep_recovery(daily_plan.post_recovery, 3.5, 9.0)
#     daily_plan.post_recovery.completed = True
#     daily_plan.post_recovery.display_exercises = False
#     land_screen, nav_bar = daily_plan.define_landing_screen()
#     assert land_screen == 2.0