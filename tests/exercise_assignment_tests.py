import pytest
import exercise


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
    assert exercise.ExercisePriority(0) == priority


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
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_3_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(3, exercise.Phase(3))
    assert exercise.ExercisePriority(0) == priority


def test_get_priority_4_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(4, exercise.Phase(3))
    assert exercise.ExercisePriority(2) == priority


def test_get_priority_5_severity_integrate():
    recs = exercise.ExerciseRecommendations()
    priority = recs.get_exercise_priority_from_soreness_level(5, exercise.Phase(3))
    assert exercise.ExercisePriority(2) == priority

