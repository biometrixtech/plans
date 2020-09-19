from logic.training_exposure_processing import TrainingExposureProcessor
from models.planned_exercise import PlannedExercise
from models.training_volume import StandardErrorRange
from models.movement_tags import DetailedAdaptationType, AdaptationType
from models.movement_actions import MovementSpeed, MovementResistance, MovementDisplacement

# def get_planned_workout(exercise):
#
#     planned_workout = PlannedWorkout()
#     section = PlannedWorkoutSection()
#     section.exercises.append(exercise)
#     planned_workout.sections.append()
#     return planned_workout



def test_get_base_aerobic_planned_workout():

    exercise = PlannedExercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    exercise.predicted_rpe = StandardErrorRange(lower_bound=3, upper_bound=4)
    exercise.duration = 350

    proc = TrainingExposureProcessor()
    exposures = proc.get_exposures(exercise)
    assert 1 == len(exposures)
    assert DetailedAdaptationType.base_aerobic_training == exposures[0].detailed_adaptation_type


def test_get_anaerobic_threshold_planned_workout():

    exercise = PlannedExercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    exercise.predicted_rpe = StandardErrorRange(lower_bound=5.5, upper_bound=6)
    exercise.duration = 250

    proc = TrainingExposureProcessor()
    exposures = proc.get_exposures(exercise)
    assert 1 == len(exposures)
    #assert DetailedAdaptationType.muscular_endurance == exposures[0].detailed_adaptation_type
    assert DetailedAdaptationType.anaerobic_threshold_training == exposures[0].detailed_adaptation_type


def test_get_high_intensity_anaerobic_planned_workout():

    exercise = PlannedExercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_cardiorespiratory
    exercise.predicted_rpe = StandardErrorRange(lower_bound=6, observed_value=7, upper_bound=8)
    exercise.duration = 25

    proc = TrainingExposureProcessor()
    exposures = proc.get_exposures(exercise)
    assert 1== len(exposures)
    assert DetailedAdaptationType.high_intensity_anaerobic_training == exposures[0].detailed_adaptation_type


def test_get_strength_endurance_planned_workout():

    exercise = PlannedExercise()
    exercise.adaptation_type = AdaptationType.strength_endurance_strength
    exercise.predicted_rpe = StandardErrorRange(lower_bound=5, observed_value=6, upper_bound=7)
    exercise.movement_speed = MovementSpeed.mod
    exercise.resistance = MovementResistance.very_low
    exercise.displacement = MovementDisplacement.mod
    exercise.reps_per_set = 10

    proc = TrainingExposureProcessor()
    exposures = proc.get_exposures(exercise)
    assert 1 == len(exposures)
    assert DetailedAdaptationType.strength_endurance == exposures[0].detailed_adaptation_type


def test_get_muscular_endurance_strength_planned_workout():

    speeds = [MovementSpeed.slow, MovementSpeed.none]

    for speed in speeds:
        exercise = PlannedExercise()
        exercise.adaptation_type = AdaptationType.strength_endurance_strength
        exercise.predicted_rpe = StandardErrorRange(lower_bound=5, observed_value=6, upper_bound=7)
        exercise.movement_speed = speed
        exercise.resistance = MovementResistance.very_low
        exercise.displacement = MovementDisplacement.partial_rom
        exercise.reps_per_set = 15

        proc = TrainingExposureProcessor()
        exposures = proc.get_exposures(exercise)
        assert 2 == len(exposures)
        assert DetailedAdaptationType.strength_endurance == exposures[0].detailed_adaptation_type
        assert DetailedAdaptationType.muscular_endurance == exposures[1].detailed_adaptation_type


def test_get_hypertrophy_planned_workout():

    exercise = PlannedExercise()
    exercise.adaptation_type = AdaptationType.maximal_strength_hypertrophic
    exercise.predicted_rpe = StandardErrorRange(lower_bound=6, observed_value=7, upper_bound=8)
    exercise.movement_speed = MovementSpeed.mod
    exercise.resistance = MovementResistance.very_low
    exercise.displacement = MovementDisplacement.max
    exercise.reps_per_set = 10

    proc = TrainingExposureProcessor()
    exposures = proc.get_exposures(exercise)
    assert 1 == len(exposures)
    assert DetailedAdaptationType.hypertrophy == exposures[0].detailed_adaptation_type


def test_get_max_strength_planned_workout():

    exercise = PlannedExercise()
    exercise.adaptation_type = AdaptationType.maximal_strength_hypertrophic
    exercise.predicted_rpe = StandardErrorRange(lower_bound=7, observed_value=8, upper_bound=9)
    exercise.movement_speed = MovementSpeed.fast
    exercise.resistance = MovementResistance.very_low
    exercise.displacement = MovementDisplacement.max
    exercise.reps_per_set = 3

    proc = TrainingExposureProcessor()
    exposures = proc.get_exposures(exercise)
    assert 1 == len(exposures)
    assert DetailedAdaptationType.maximal_strength == exposures[0].detailed_adaptation_type


def test_get_speed_power_adaptation_types_planned_workout():

    speeds = [MovementSpeed.slow, MovementSpeed.none]
    power_types = [AdaptationType.power_drill, AdaptationType.power_explosive_action]

    for speed in speeds:
        for power_type in power_types:
            exercise = PlannedExercise()
            exercise.adaptation_type = power_type
            exercise.predicted_rpe = None
            exercise.movement_speed = speed
            exercise.resistance = MovementResistance.very_low
            exercise.displacement = MovementDisplacement.partial_rom
            exercise.reps_per_set = None

            proc = TrainingExposureProcessor()
            exposures = proc.get_exposures(exercise)
            assert 1 == len(exposures)
            assert DetailedAdaptationType.speed == exposures[0].detailed_adaptation_type


def test_get_sustained_power_power_adaptation_types_planned_workout():

    speeds = [MovementSpeed.mod]
    power_types = [AdaptationType.power_drill, AdaptationType.power_explosive_action]

    for speed in speeds:
        for power_type in power_types:
            exercise = PlannedExercise()
            exercise.adaptation_type = power_type
            exercise.predicted_rpe = None
            exercise.movement_speed = speed
            exercise.resistance = MovementResistance.very_low
            exercise.displacement = MovementDisplacement.max
            exercise.reps_per_set = None
            exercise.duration = 50 * 60

            proc = TrainingExposureProcessor()
            exposures = proc.get_exposures(exercise)
            assert 2 == len(exposures)
            assert DetailedAdaptationType.power == exposures[0].detailed_adaptation_type
            assert DetailedAdaptationType.sustained_power == exposures[1].detailed_adaptation_type


def test_get_power_power_adaptation_types_planned_workout():

    power_types = [AdaptationType.power_drill, AdaptationType.power_explosive_action]

    for power_type in power_types:
        exercise = PlannedExercise()
        exercise.adaptation_type = power_type
        exercise.predicted_rpe = None
        exercise.movement_speed = MovementSpeed.mod
        exercise.resistance = MovementResistance.very_low
        exercise.displacement = MovementDisplacement.max
        exercise.reps_per_set = None

        proc = TrainingExposureProcessor()
        exposures = proc.get_exposures(exercise)
        assert 1 == len(exposures)
        assert DetailedAdaptationType.power == exposures[0].detailed_adaptation_type