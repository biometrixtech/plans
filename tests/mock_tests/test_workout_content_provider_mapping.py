from models.workout_program import Movement, WorkoutExercise
from models.movement_tags import AdaptationType, TrainingType
from models.exercise import UnitOfMeasure


def test_training_type_flexibility():

    movement = Movement("1", "test")
    movement.training_type = TrainingType.flexibility

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.not_tracked


def test_training_type_cardiorespiratory():

    movement = Movement("1", "test")
    movement.training_type = TrainingType.cardiorespiratory

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.strength_endurance_cardiorespiratory


def test_training_type_core():

    movement = Movement("1", "test")
    movement.training_type = TrainingType.core

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.strength_endurance_strength


def test_training_type_balance():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.balance

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.strength_endurance_strength


def test_training_type_plyometrics():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.plyometrics

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.power_explosive_action


def test_training_type_plyometrics_drills():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.plyometrics_drills

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.power_drill


def test_training_type_speed_agility_quickness():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.speed_agility_quickness

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.power_drill


def test_training_type_integrated_resistance_high():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.integrated_resistance

    workout_exercise = WorkoutExercise()
    workout_exercise.intensity_pace = 80
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic


def test_training_type_integrated_resistance_low():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.integrated_resistance

    workout_exercise = WorkoutExercise()
    workout_exercise.intensity_pace = 60
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.strength_endurance_strength


def test_training_type_olympic_lifting_high():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.olympic_lifting
    movement.explosive = 3

    workout_exercise = WorkoutExercise()

    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.power_explosive_action


def test_training_type_olympic_lifting_low():
    movement = Movement("1", "test")
    movement.training_type = TrainingType.olympic_lifting
    movement.explosive = 1

    workout_exercise = WorkoutExercise()
    workout_exercise.process_movement(movement)

    assert workout_exercise.adaptation_type == AdaptationType.maximal_strength_hypertrophic


def test_get_training_volume_reps():

    workout_exercise = WorkoutExercise()
    workout_exercise.reps_per_set = 5
    workout_exercise.unit_of_measure = UnitOfMeasure.count
    workout_exercise.sets = 1

    assert workout_exercise.get_training_volume() == 5


def test_get_training_volume_reps_sets():

    workout_exercise = WorkoutExercise()
    workout_exercise.reps_per_set = 5
    workout_exercise.sets = 2
    workout_exercise.unit_of_measure = UnitOfMeasure.count

    assert workout_exercise.get_training_volume() == 10


def test_get_training_volume_reps_sets_yards():
    workout_exercise = WorkoutExercise()
    workout_exercise.reps_per_set = 50
    workout_exercise.sets = 2
    workout_exercise.unit_of_measure = UnitOfMeasure.yards

    assert workout_exercise.get_training_volume() == 20


def test_get_training_volume_reps_sets_feet():
    workout_exercise = WorkoutExercise()
    workout_exercise.reps_per_set = 150
    workout_exercise.sets = 2
    workout_exercise.unit_of_measure = UnitOfMeasure.feet

    assert workout_exercise.get_training_volume() == 20

