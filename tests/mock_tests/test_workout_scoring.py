from logic.workout_scoring import WorkoutScoringProcessor
from models.exposure import TargetTrainingExposure, TrainingExposure
from models.movement_tags import DetailedAdaptationType
from models.athlete_capacity import AthleteBaselineCapacities, TrainingUnit
from models.training_volume import StandardErrorRange


def get_athlete_baseline_capacities(rpe_range):

    capacities = AthleteBaselineCapacities()
    capacities.base_aerobic_training = TrainingUnit(rpe=rpe_range, volume=StandardErrorRange(observed_value=5 * 60))
    return capacities


def get_base_training_long_exposure_needs():

    # assumes this will get set elsewhere (it's the percentage of weekly load)
    base_training_exposure_long = TrainingExposure(DetailedAdaptationType.base_aerobic_training,rpe=StandardErrorRange(observed_value=3.0), volume=StandardErrorRange(observed_value=60))
    one_required_count = StandardErrorRange(observed_value=1)

    base_target_training_exposure_long = TargetTrainingExposure(training_exposures=[base_training_exposure_long],
                                                                exposure_count=one_required_count, priority=1)

    training_exposure_needs = [base_target_training_exposure_long]

    return training_exposure_needs


def get_anaerobic_threshold_training_exposure_needs():

    # assumes this will get set elsewhere (it's the percentage of weekly load)
    training_exposure = TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training,rpe=StandardErrorRange(observed_value=5.0), volume=StandardErrorRange(observed_value=240))
    one_required_count = StandardErrorRange(observed_value=1)

    base_target_training_exposure_long = TargetTrainingExposure(training_exposures=[training_exposure],
                                                                exposure_count=one_required_count, priority=1)

    training_exposure_needs = [base_target_training_exposure_long]

    return training_exposure_needs


def get_base_training_workout_exposures():

    base_training_exposure = TrainingExposure(DetailedAdaptationType.base_aerobic_training, rpe=StandardErrorRange(lower_bound=2.9, upper_bound=3.1), volume=StandardErrorRange(observed_value=65))

    training_exposures = [base_training_exposure]

    return training_exposures


def test_safe_base_training():

    proc = WorkoutScoringProcessor()

    athlete_baseline_capacities = get_athlete_baseline_capacities(StandardErrorRange(observed_value=3.0))
    workout_training_exposures = get_base_training_workout_exposures()

    safe = proc.is_safe(athlete_baseline_capacities, workout_training_exposures)

    assert True is safe


def test_relevant_score_20():

    proc = WorkoutScoringProcessor()

    athlete_training_exposure_needs = get_base_training_long_exposure_needs()
    workout_training_exposures = get_base_training_workout_exposures()

    score = proc.get_relevant_score(athlete_training_exposure_needs, workout_training_exposures)

    assert 20 == score


def test_relevant_score_0():

    proc = WorkoutScoringProcessor()

    athlete_training_exposure_needs = get_anaerobic_threshold_training_exposure_needs()
    workout_training_exposures = get_base_training_workout_exposures()

    score = proc.get_relevant_score(athlete_training_exposure_needs, workout_training_exposures)

    assert 0 == score


def test_relevant_score_10():

    proc = WorkoutScoringProcessor()

    athlete_training_exposure_needs = []

    athlete_training_exposure_needs.extend(get_base_training_long_exposure_needs())
    athlete_training_exposure_needs.extend(get_anaerobic_threshold_training_exposure_needs())
    workout_training_exposures = get_base_training_workout_exposures()

    score = proc.get_relevant_score(athlete_training_exposure_needs, workout_training_exposures)

    assert 10 == score


def test_necessary_score_20():

    proc = WorkoutScoringProcessor()

    athlete_training_exposure_needs = get_base_training_long_exposure_needs()
    workout_training_exposures = get_base_training_workout_exposures()

    score = proc.get_necessary_score(athlete_training_exposure_needs, workout_training_exposures)

    assert 20 == score


def test_necessary_score_0():

    proc = WorkoutScoringProcessor()

    athlete_training_exposure_needs = get_base_training_long_exposure_needs()
    athlete_training_exposure_needs[0].exposure_count = 0

    workout_training_exposures = get_base_training_workout_exposures()

    score = proc.get_necessary_score(athlete_training_exposure_needs, workout_training_exposures)

    assert 0 == score


def test_necessary_score_10():

    proc = WorkoutScoringProcessor()

    athlete_training_exposure_needs = []

    athlete_training_exposure_needs.extend(get_base_training_long_exposure_needs())
    athlete_training_exposure_needs.extend(get_anaerobic_threshold_training_exposure_needs())
    workout_training_exposures = get_base_training_workout_exposures()

    score = proc.get_necessary_score(athlete_training_exposure_needs, workout_training_exposures)

    assert 10 == score


# TODO include ideal score
def test_total_score_75():

    proc = WorkoutScoringProcessor()

    capacities = get_athlete_baseline_capacities(StandardErrorRange(observed_value=3.0))
    athlete_training_exposure_needs = get_base_training_long_exposure_needs()
    workout_training_exposures = get_base_training_workout_exposures()

    score = proc.score_workout(capacities, athlete_training_exposure_needs, workout_training_exposures)

    assert 75 == score
