from models.modalities import ModalityBase
from models.soreness import AthleteGoal, AthleteGoalType, Exercise, ExerciseDosage, Soreness
from datetime import datetime

goal_types = [AthleteGoalType.sore, AthleteGoalType.preempt_corrective]


def get_daily_dosage(goal, soreness, priority):

    dosage = ExerciseDosage()
    dosage.efficient_reps_assigned = 0
    dosage.efficient_sets_assigned = 0
    dosage.complete_reps_assigned = 0
    dosage.complete_sets_assigned = 0
    dosage.comprehensive_reps_assigned = 0
    dosage.comprehensive_sets_assigned = 0
    dosage.soreness_source = soreness
    dosage.goal = goal
    dosage.priority = priority

    return dosage


# priority 1

def test_daily_sore_0_4_severity_priority_1_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 0.4
    soreness.daily = True
    exercise.min_reps = 30

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "1")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.min_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.min_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_1_4_severity_priority_1_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 1.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "1")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.min_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_2_4_severity_priority_1_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 2.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "1")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.min_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.min_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_3_4_severity_priority_1_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 3.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "1")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.min_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_4_4_severity_priority_1_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 4.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "1")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.min_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.max_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 2


def test_daily_sore_4_9_severity_priority_1_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 4.9
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "1")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.max_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.max_reps
        assert dosage.complete_sets_assigned == 2
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 3

# priority 2


def test_daily_sore_0_4_severity_priority_2_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 0.4
    soreness.daily = True
    exercise.min_reps = 30

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "2")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == 0
        assert dosage.efficient_sets_assigned == 0
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.min_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_1_4_severity_priority_2_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 1.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "2")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == 0
        assert dosage.efficient_sets_assigned == 0
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_2_4_severity_priority_2_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 2.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "2")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == 0
        assert dosage.efficient_sets_assigned == 0
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.min_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_3_4_severity_priority_2_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 3.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "2")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.min_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_4_4_severity_priority_2_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 4.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "2")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.min_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.max_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 2


def test_daily_sore_4_9_severity_priority_2_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 4.9
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "2")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.max_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.max_reps
        assert dosage.complete_sets_assigned == 2
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 3

# priority 3


def test_daily_sore_0_4_severity_priority_3_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 0.4
    soreness.daily = True
    exercise.min_reps = 30

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "3")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == 0
        assert dosage.efficient_sets_assigned == 0
        assert dosage.complete_reps_assigned == 0
        assert dosage.complete_sets_assigned == 0
        assert dosage.comprehensive_reps_assigned == 0
        assert dosage.comprehensive_sets_assigned == 0


def test_daily_sore_1_4_severity_priority_3_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 1.4
    soreness.daily = True
    exercise.min_reps = 30

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "3")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == 0
        assert dosage.efficient_sets_assigned == 0
        assert dosage.complete_reps_assigned == 0
        assert dosage.complete_sets_assigned == 0
        assert dosage.comprehensive_reps_assigned == 0
        assert dosage.comprehensive_sets_assigned == 0


def test_daily_sore_2_4_severity_priority_3_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 2.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "3")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == 0
        assert dosage.efficient_sets_assigned == 0
        assert dosage.complete_reps_assigned == 0
        assert dosage.complete_sets_assigned == 0
        assert dosage.comprehensive_reps_assigned == exercise.min_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_3_4_severity_priority_3_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 3.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "3")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == 0
        assert dosage.efficient_sets_assigned == 0
        assert dosage.complete_reps_assigned == exercise.min_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 1


def test_daily_sore_4_4_severity_priority_3_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 4.4
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "3")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.min_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.max_reps
        assert dosage.complete_sets_assigned == 1
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 2


def test_daily_sore_4_9_severity_priority_3_table_1():

    mod_base = ModalityBase(datetime.now())
    exercise = Exercise("1")
    soreness = Soreness()

    soreness.severity = 4.9
    soreness.daily = True
    exercise.min_reps = 30
    exercise.max_reps = 50

    for g in goal_types:
        goal = AthleteGoal("test", "1", g)

        dosage = get_daily_dosage(goal, soreness, "3")

        dosage = mod_base.update_dosage(dosage, exercise)
        assert dosage.efficient_reps_assigned == exercise.max_reps
        assert dosage.efficient_sets_assigned == 1
        assert dosage.complete_reps_assigned == exercise.max_reps
        assert dosage.complete_sets_assigned == 2
        assert dosage.comprehensive_reps_assigned == exercise.max_reps
        assert dosage.comprehensive_sets_assigned == 3