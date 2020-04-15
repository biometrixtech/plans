from models.functional_movement_activities import MovementIntegrationPrep
from models.dosage import ExerciseDosage
from models.exercise_phase import ExercisePhaseType
from models.goal import AthleteGoalType, AthleteGoal
import datetime


def test_get_benchmark_recovery_priority_3():
    movement_prep = MovementIntegrationPrep(datetime.datetime.now())
    dosage = ExerciseDosage()
    dosage.goal = AthleteGoal('recovery', 1, AthleteGoalType.high_load)
    dosage.priority = '3'

    dosages = [dosage]
    benchmark_isolated_activate = movement_prep.get_benchmark(dosages, ExercisePhaseType.isolated_activate)
    benchmark_static_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.static_stretch)
    benchmark_active_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.active_stretch)
    benchmark_dynamic_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.dynamic_stretch)
    benchmark_inhibit = movement_prep.get_benchmark(dosages, ExercisePhaseType.inhibit)
    assert benchmark_isolated_activate == 42 + 14 + 1
    assert benchmark_static_stretch == 42 + 14 + 2
    assert benchmark_active_stretch == 42 + 14 + 3
    assert benchmark_dynamic_stretch == 42 + 14 + 4
    assert benchmark_inhibit == 42 + 14 + 5


def test_get_benchmark_prevention_priority_2():
    movement_prep = MovementIntegrationPrep(datetime.datetime.now())
    dosage = ExerciseDosage()
    dosage.goal = AthleteGoal('prevention', 1, AthleteGoalType.corrective)
    dosage.priority = '2'

    dosages = [dosage]
    benchmark_isolated_activate = movement_prep.get_benchmark(dosages, ExercisePhaseType.isolated_activate)
    benchmark_static_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.static_stretch)
    benchmark_active_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.active_stretch)
    benchmark_dynamic_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.dynamic_stretch)
    benchmark_inhibit = movement_prep.get_benchmark(dosages, ExercisePhaseType.inhibit)
    assert benchmark_isolated_activate == 21 + 7 + 1
    assert benchmark_static_stretch == 21 + 7 + 2
    assert benchmark_active_stretch == 21 + 7 + 3
    assert benchmark_dynamic_stretch == 21 + 7 + 4
    assert benchmark_inhibit == 21 + 7 + 5


def test_get_benchmark_care_priority_3():
    movement_prep = MovementIntegrationPrep(datetime.datetime.now())
    dosage = ExerciseDosage()
    dosage.goal = AthleteGoal('care', 1, AthleteGoalType.sore)
    dosage.priority = '3'

    dosages = [dosage]
    benchmark_isolated_activate = movement_prep.get_benchmark(dosages, ExercisePhaseType.isolated_activate)
    benchmark_static_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.static_stretch)
    benchmark_active_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.active_stretch)
    benchmark_dynamic_stretch = movement_prep.get_benchmark(dosages, ExercisePhaseType.dynamic_stretch)
    benchmark_inhibit = movement_prep.get_benchmark(dosages, ExercisePhaseType.inhibit)
    assert benchmark_isolated_activate == 42 + 0 + 1
    assert benchmark_static_stretch == 42 + 0 + 2
    assert benchmark_active_stretch == 42 + 0 + 3
    assert benchmark_dynamic_stretch == 42 + 0 + 4
    assert benchmark_inhibit == 42 + 0 + 5
