from models.planned_exercise import PlannedExercise, Assignment
from models.movement_tags import CardioAction
from logic.workout_processing import WorkoutProcessor


def get_exercise(cardio_action=CardioAction.run):
    ex = PlannedExercise()
    ex.cardio_action = cardio_action
    return ex


def test_planned_power_running_both_assigned():
    exercise = get_exercise()
    exercise.grade = Assignment(assigned_value=6.0)
    exercise.speed = Assignment(assigned_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value == exercise.power.lower_bound == exercise.power.upper_bound


def test_planned_power_running_speed_assigned_grade_min():
    exercise = get_exercise()
    exercise.grade = Assignment(min_value=6.0)
    exercise.speed = Assignment(assigned_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)

    assert exercise.power.observed_value == exercise.power.upper_bound
    assert exercise.power.lower_bound <= exercise.power.observed_value


def test_planned_power_running_speed_assigned_grade_min_and_max():
    exercise = get_exercise()
    exercise.grade = Assignment(min_value=.06, max_value=.08)
    exercise.speed = Assignment(assigned_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value is not None
    assert exercise.power.lower_bound is not None
    assert exercise.power.upper_bound is not None

    assert exercise.power.lower_bound <= exercise.power.observed_value <= exercise.power.upper_bound


def test_planned_power_running_speed_min_grade_assigned():
    exercise = get_exercise()
    exercise.grade = Assignment(assigned_value=.06)
    exercise.speed = Assignment(min_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value == exercise.power.lower_bound == exercise.power.upper_bound


def test_planned_power_running_speed_min_and_max_grade_assigned():
    exercise = get_exercise()
    exercise.grade = Assignment(assigned_value=.06)
    exercise.speed = Assignment(min_value=2, max_value=4)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)

    assert exercise.power.lower_bound <= exercise.power.observed_value <= exercise.power.upper_bound


def test_planned_power_running_speed_min_and_max_grade_min_and_max():
    exercise = get_exercise()
    exercise.grade = Assignment(min_value=.06, max_value=.08)
    exercise.speed = Assignment(min_value=2, max_value=4)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value is not None
    assert exercise.power.lower_bound is not None
    assert exercise.power.upper_bound is not None

    assert exercise.power.lower_bound <= exercise.power.observed_value <= exercise.power.upper_bound


def test_planned_power_rowing_speed_assigned():
    exercise = get_exercise(cardio_action=CardioAction.row)
    exercise.speed = Assignment(assigned_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value == exercise.power.lower_bound == exercise.power.upper_bound


def test_planned_power_rowing_speed_min():
    exercise = get_exercise(cardio_action=CardioAction.row)
    exercise.speed = Assignment(min_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value == exercise.power.lower_bound == exercise.power.upper_bound


def test_planned_power_rowing_speed_min_and_max():
    exercise = get_exercise(cardio_action=CardioAction.row)
    exercise.speed = Assignment(min_value=2, max_value=4)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value is not None
    assert exercise.power.lower_bound is not None
    assert exercise.power.upper_bound is not None

    assert exercise.power.lower_bound <= exercise.power.observed_value <= exercise.power.upper_bound


def test_planned_power_cycling_both_assigned():
    exercise = get_exercise(cardio_action=CardioAction.cycle)
    exercise.grade = Assignment(assigned_value=6.0)
    exercise.speed = Assignment(assigned_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value == exercise.power.lower_bound == exercise.power.upper_bound


def test_planned_power_cycling_speed_assigned_grade_min():
    exercise = get_exercise(cardio_action=CardioAction.cycle)
    exercise.grade = Assignment(min_value=6.0)
    exercise.speed = Assignment(assigned_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value == exercise.power.upper_bound
    assert exercise.power.lower_bound <= exercise.power.observed_value


def test_planned_power_cycling_speed_assigned_grade_min_and_max():
    exercise = get_exercise(cardio_action=CardioAction.cycle)
    exercise.grade = Assignment(min_value=.06, max_value=.08)
    exercise.speed = Assignment(assigned_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value is not None
    assert exercise.power.lower_bound is not None
    assert exercise.power.upper_bound is not None

    assert exercise.power.lower_bound <= exercise.power.observed_value <= exercise.power.upper_bound


def test_planned_power_cycling_speed_min_grade_assigned():
    exercise = get_exercise(cardio_action=CardioAction.cycle)
    exercise.grade = Assignment(assigned_value=.06)
    exercise.speed = Assignment(min_value=2)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.lower_bound == exercise.power.observed_value == exercise.power.upper_bound


def test_planned_power_cycling_speed_min_and_max_grade_assigned():
    exercise = get_exercise(cardio_action=CardioAction.cycle)
    exercise.grade = Assignment(assigned_value=.06)
    exercise.speed = Assignment(min_value=2, max_value=4)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value is not None
    assert exercise.power.lower_bound is not None
    assert exercise.power.upper_bound is not None

    assert exercise.power.lower_bound <= exercise.power.observed_value <= exercise.power.upper_bound


def test_planned_power_cycling_speed_min_and_max_grade_min_and_max():
    exercise = get_exercise(cardio_action=CardioAction.cycle)
    exercise.grade = Assignment(min_value=.06, max_value=.08)
    exercise.speed = Assignment(min_value=2, max_value=4)
    processor = WorkoutProcessor()
    processor.set_planned_power(exercise)
    assert exercise.power.observed_value is not None
    assert exercise.power.lower_bound is not None
    assert exercise.power.upper_bound is not None

    assert exercise.power.lower_bound <= exercise.power.observed_value <= exercise.power.upper_bound
