import pytest
import exercise
import session
import soreness_and_injury


@pytest.fixture(scope="module")
def recovery_session(soreness_list, target_minutes):
    target_recovery_session = session.RecoverySession()
    target_recovery_session.set_exercise_target_minutes(soreness_list, target_minutes)
    return target_recovery_session


@pytest.fixture(scope="module")
def soreness_one_body_part(body_enum, severity_score):
    soreness_list = []
    soreness_item = soreness_and_injury.DailySoreness()
    soreness_item.severity = severity_score
    soreness_item.body_part = soreness_and_injury.BodyPartLocation(body_enum)
    soreness_list.append(soreness_item)
    return soreness_list
'''
one body part
NEED: SORENESS = 4, 5
if soreness=3 (no more than 60% of time on inhibit exercises, no more than 60% of time on lengthen exercises, 
total no more than 15 minutes)
if soreness=2 (no more than 40% of time on inhibit exercises, no more than 40% of time on lengthen exercises, 
no more than 40% on activate exercises, total no more than 15 minutes)
if soreness =1 (no more than 30% of time on inhibit exercises, no more than 30% of time on lengthen exercises, 
no more than 60% on activate exercises, total no more than 15 minutes)
if no soreness, due general program (no more than 30% of time on inhibit exercises, 
no more than 30% of time on lengthen exercises, no more than 60% on activate exercises, total no more than 15 minutes)

dosage

start at max dosage, scale down to min dosage until all exercises are at min (lowest priority to highest), 
if still too much, drop least priority, etc


> 1 body part
no activate if any body part soreness = 3 or more
if 1s and 2s, follow most severe case

dosage: 
two body parts, same severity: merge list and then drop off by priority like with 1 body part (pick which one is first 
based on body part ranking

if not same severity: find difference in time % and allocate that net gain to the more server part(s); then follow
normal protocol for the lower severity portion of time
'''

# test initial targets based on soreness levels


def test_recovery_session_no_soreness_inhibit_max_percentage():
    assert .3 == recovery_session(None, 15).inhibit_max_percentage


def test_recovery_session_no_soreness_lengthen_max_percentage():
    assert .3 == recovery_session(None, 15).lengthen_max_percentage


def test_recovery_session_no_soreness_activate_max_percentage():
    assert .6 == recovery_session(None, 15).activate_max_percentage


def test_recovery_session_no_soreness_integrate_max_percentage():
    assert None is recovery_session(None, 15).integrate_max_percentage


def test_recovery_session_no_soreness_inhibit_minutes():
    assert 3.75 == recovery_session(None, 15).inhibit_target_minutes


def test_recovery_session_no_soreness_lengthen_minutes():
    assert 3.75 == recovery_session(None, 15).lengthen_target_minutes


def test_recovery_session_no_soreness_activate_minutes():
    assert 7.5 == recovery_session(None, 15).activate_target_minutes


def test_recovery_session_no_soreness_integrate_minutes():
    assert None is recovery_session(None, 15).integrate_target_minutes


def test_recovery_session_ankle_1_soreness_inhibit_max_percentage():
    assert .3 == recovery_session(soreness_one_body_part(9, 1), 15).inhibit_max_percentage


def test_recovery_session_ankle_1_soreness_lengthen_max_percentage():
    assert .3 == recovery_session(soreness_one_body_part(9, 1), 15).lengthen_max_percentage


def test_recovery_session_ankle_1_soreness_activate_max_percentage():
    assert .6 == recovery_session(soreness_one_body_part(9, 1), 15).activate_max_percentage


def test_recovery_session_ankle_1_soreness_integrate_max_percentage():
    assert None is recovery_session(soreness_one_body_part(9, 1), 15).integrate_max_percentage


def test_recovery_session_ankle_1_soreness_inhibit_minutes():
    assert 3.75 == recovery_session(soreness_one_body_part(9, 1), 15).inhibit_target_minutes


def test_recovery_session_ankle_1_soreness_lengthen_minutes():
    assert 3.75 == recovery_session(soreness_one_body_part(9, 1), 15).lengthen_target_minutes


def test_recovery_session_ankle_1_soreness_activate_minutes():
    assert 7.5 == recovery_session(soreness_one_body_part(9, 1), 15).activate_target_minutes


def test_recovery_session_ankle_1_soreness_integrate_minutes():
    assert None is recovery_session(soreness_one_body_part(9, 1), 15).integrate_target_minutes


def test_recovery_session_ankle_2_soreness_inhibit_max_percentage():
    assert .4 == recovery_session(soreness_one_body_part(9, 2), 15).inhibit_max_percentage


def test_recovery_session_ankle_2_soreness_lengthen_max_percentage():
    assert .4 == recovery_session(soreness_one_body_part(9, 2), 15).lengthen_max_percentage


def test_recovery_session_ankle_2_soreness_activate_max_percentage():
    assert .4 == recovery_session(soreness_one_body_part(9, 2), 15).activate_max_percentage


def test_recovery_session_ankle_2_soreness_integrate_max_percentage():
    assert None is recovery_session(soreness_one_body_part(9, 2), 15).integrate_max_percentage


def test_recovery_session_ankle_2_soreness_inhibit_minutes():
    assert 5 == recovery_session(soreness_one_body_part(9, 2), 15).inhibit_target_minutes


def test_recovery_session_ankle_2_soreness_lengthen_minutes():
    assert 5 == recovery_session(soreness_one_body_part(9, 2), 15).lengthen_target_minutes


def test_recovery_session_ankle_2_soreness_activate_minutes():
    assert 5 == recovery_session(soreness_one_body_part(9, 2), 15).activate_target_minutes


def test_recovery_session_ankle_2_soreness_integrate_minutes():
    assert None is recovery_session(soreness_one_body_part(9, 2), 15).integrate_target_minutes


def test_recovery_session_ankle_3_soreness_inhibit_max_percentage():
    assert .6 == recovery_session(soreness_one_body_part(9, 3), 15).inhibit_max_percentage


def test_recovery_session_ankle_3_soreness_lengthen_max_percentage():
    assert .6 == recovery_session(soreness_one_body_part(9, 3), 15).lengthen_max_percentage


def test_recovery_session_ankle_3_soreness_activate_max_percentage():
    assert None is recovery_session(soreness_one_body_part(9, 3), 15).activate_max_percentage


def test_recovery_session_ankle_3_soreness_integrate_max_percentage():
    assert None is recovery_session(soreness_one_body_part(9, 3), 15).integrate_max_percentage


def test_recovery_session_ankle_3_soreness_inhibit_minutes():
    assert 7.5 == recovery_session(soreness_one_body_part(9, 3), 15).inhibit_target_minutes


def test_recovery_session_ankle_3_soreness_lengthen_minutes():
    assert 7.5 == recovery_session(soreness_one_body_part(9, 3), 15).lengthen_target_minutes


def test_recovery_session_ankle_3_soreness_activate_minutes():
    assert None is recovery_session(soreness_one_body_part(9, 3), 15).activate_target_minutes


def test_recovery_session_ankle_3_soreness_integrate_minutes():
    assert None is recovery_session(soreness_one_body_part(9, 3), 15).integrate_target_minutes


def test_recovery_session_ankle_4_soreness_inhibit_max_percentage():
    assert None is recovery_session(soreness_one_body_part(9, 4), 15).inhibit_max_percentage


def test_recovery_session_ankle_4_soreness_lengthen_max_percentage():
    assert None is recovery_session(soreness_one_body_part(9, 4), 15).lengthen_max_percentage


def test_recovery_session_ankle_4_soreness_activate_max_percentage():
    assert None is recovery_session(soreness_one_body_part(9, 4), 15).activate_max_percentage


def test_recovery_session_ankle_4_soreness_integrate_max_percentage():
    assert None is recovery_session(soreness_one_body_part(9, 4), 15).integrate_max_percentage


def test_recovery_session_ankle_4_soreness_inhibit_minutes():
    assert None is recovery_session(soreness_one_body_part(9, 4), 15).inhibit_target_minutes


def test_recovery_session_ankle_4_soreness_lengthen_minutes():
    assert None is recovery_session(soreness_one_body_part(9, 4), 15).lengthen_target_minutes


def test_recovery_session_ankle_4_soreness_activate_minutes():
    assert None is recovery_session(soreness_one_body_part(9, 4), 15).activate_target_minutes


def test_recovery_session_ankle_4_soreness_integrate_minutes():
    assert None is recovery_session(soreness_one_body_part(9, 4), 15).integrate_target_minutes


'''
def test_get_priority_no_severity_inhibit():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(0, exercise.Phase(0))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_1_severity_inhibit():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(1, exercise.Phase(0))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_2_severity_inhibit():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(2, exercise.Phase(0))
    assert exercise.ExercisePriority(1) == priority


def test_get_priority_3_severity_inhibit():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(3, exercise.Phase(0))
    assert exercise.ExercisePriority(1) == priority


def test_get_priority_4_severity_inhibit():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(4, exercise.Phase(0))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_5_severity_inhibit():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(5, exercise.Phase(0))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_no_severity_lengthen():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(0, exercise.Phase(1))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_1_severity_lengthen():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(1, exercise.Phase(1))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_2_severity_lengthen():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(2, exercise.Phase(1))
    assert exercise.ExercisePriority(1) == priority


def test_get_priority_3_severity_lengthen():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(3, exercise.Phase(1))
    assert exercise.ExercisePriority(1) == priority


def test_get_priority_4_severity_lengthen():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(4, exercise.Phase(1))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_5_severity_lengthen():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(5, exercise.Phase(1))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_no_severity_activate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(0, exercise.Phase(2))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_1_severity_activate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(1, exercise.Phase(2))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_2_severity_activate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(2, exercise.Phase(2))
    assert exercise.ExercisePriority(1) == priority


def test_get_priority_3_severity_activate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(3, exercise.Phase(2))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_4_severity_activate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(4, exercise.Phase(2))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_5_severity_activate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(5, exercise.Phase(2))
    assert exercise.ExercisePriority(2) == priority

def test_get_priority_no_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(0, exercise.Phase(3))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_1_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(1, exercise.Phase(3))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_2_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(2, exercise.Phase(3))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_3_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(3, exercise.Phase(3))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_4_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(4, exercise.Phase(3))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_5_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(5, exercise.Phase(3))
    assert exercise.ExercisePriority(2) == priority

'''



