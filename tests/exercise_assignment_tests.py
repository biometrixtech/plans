import pytest
import logic.exercise_mapping as exercise_mapping
import models.session as session
import logic.soreness_processing as soreness_and_injury
import datastores.exercise_datastore as exercise_datastore
from models.soreness import Soreness, BodyPart, BodyPartLocation


@pytest.fixture(scope="module")
def recovery_session(soreness_list, target_minutes):
    target_recovery_session = session.RecoverySession()
    target_recovery_session.set_exercise_target_minutes(soreness_list, target_minutes)
    return target_recovery_session


@pytest.fixture(scope="module")
def soreness_one_body_part(body_enum, severity_score, treatment_priority=1):
    soreness_list = []
    soreness_item = Soreness()
    soreness_item.severity = severity_score
    soreness_body_part = BodyPart(BodyPartLocation(body_enum),
                                                  treatment_priority)
    soreness_item.body_part = soreness_body_part
    soreness_list.append(soreness_item)
    return soreness_list


@pytest.fixture(scope="module")
def soreness_two_body_parts(body_enum_1, severity_score_1, body_enum_2, severity_score_2,
                            treatment_priority_1=1, treatment_priority_2=1):
    soreness_list = []
    soreness_item_1 = Soreness()
    soreness_item_1.severity = severity_score_1
    soreness_body_part_1 = BodyPart(BodyPartLocation(body_enum_1), treatment_priority_1)
    soreness_item_1.body_part = soreness_body_part_1
    soreness_list.append(soreness_item_1)
    soreness_item_2 = Soreness()
    soreness_item_2.severity = severity_score_2
    soreness_body_part_2 = BodyPart(BodyPartLocation(body_enum_2),
                                                    treatment_priority_2)
    soreness_item_2.body_part = soreness_body_part_2
    soreness_list.append(soreness_item_2)

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


def test_recovery_session_exercises_assigned():
    calc = exercise_mapping.ExerciseAssignmentCalculator("test_user", None, exercise_datastore.ExerciseLibraryDatastore())
    soreness_list = soreness_one_body_part(12, 1)    # lower back
    target_recovery_session = recovery_session(soreness_one_body_part(12, 1), 15)
    exercise_assignments = calc.create_exercise_assignments(target_recovery_session, soreness_list)
    j = 0

def test_recovery_session_exercises_assigned_2_body_parts():
    calc = exercise_mapping.ExerciseAssignmentCalculator("test_user", None, exercise_datastore.ExerciseLibraryDatastore())
    soreness_list = soreness_two_body_parts(12, 1, 4, 1, 1, 2)    # lower back
    target_recovery_session = recovery_session(soreness_two_body_parts(12, 1, 4, 1, 1, 2), 15)
    exercise_assignments = calc.create_exercise_assignments(target_recovery_session, soreness_list)
    j = 0

def test_recovery_session_exercises_assigned_2_body_parts_diff_severity():
    calc = exercise_mapping.ExerciseAssignmentCalculator("test_user", None, exercise_datastore.ExerciseLibraryDatastore())
    soreness_list = soreness_two_body_parts(12, 1, 4, 2, 1, 2)    # lower back
    target_recovery_session = recovery_session(soreness_two_body_parts(12, 1, 4, 1, 1, 2), 15)
    exercise_assignments = calc.create_exercise_assignments(target_recovery_session, soreness_list)
    j = 0
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



