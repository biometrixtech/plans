from logic.periodization_processing import PeriodizationPlanProcessor
from models.athlete_capacity import AthleteBaselineCapacities, TrainingUnit
from models.periodization_plan import PeriodizationProgressionFactory, TrainingPhaseFactory, TrainingPhaseType, PeriodizationPersona
from models.periodization_goal import PeriodizationGoalType, PeriodizationGoalFactory, TrainingPersona, SubAdaptionTypePersonas
from models.movement_tags import DetailedAdaptationType
from models.training_volume import StandardErrorRange
from models.periodization_plan import PeriodizationPlan
from models.exposure import TrainingExposure, AthleteTargetTrainingExposure
from models.user_stats import UserStats
from datetime import datetime


def get_base_training_workout_exposures():

    base_training_exposure = TrainingExposure(DetailedAdaptationType.base_aerobic_training,
                                              rpe=StandardErrorRange(lower_bound=2.9, upper_bound=3.1),
                                              volume=StandardErrorRange(observed_value=65))

    training_exposures = [base_training_exposure]

    return training_exposures

def get_base_training_long_exposure_needs():

    # assumes this will get set elsewhere (it's the percentage of weekly load)
    base_training_exposure_long = TrainingExposure(DetailedAdaptationType.base_aerobic_training,rpe=StandardErrorRange(observed_value=3.0), volume=StandardErrorRange(observed_value=60))
    one_required_count = StandardErrorRange(observed_value=5)

    base_target_training_exposure_long = AthleteTargetTrainingExposure(training_exposures=[base_training_exposure_long],
                                                                       exposure_count=one_required_count, priority=1)

    training_exposure_needs = [base_target_training_exposure_long]

    return training_exposure_needs


def test_week_start_date_1():
    proc = PeriodizationPlanProcessor()

    start_date = datetime(2020, 9, 2)
    event_date = datetime(2020, 9, 9)

    is_start_date = proc.is_week_start_date(start_date, event_date)

    assert True is is_start_date


def test_week_start_date_2():
    proc = PeriodizationPlanProcessor()

    start_date = datetime(2020, 9, 2)
    event_date = datetime(2020, 9, 8)

    is_start_date = proc.is_week_start_date(start_date, event_date)

    assert False is is_start_date


def test_update_athlete_capacity():

    proc = PeriodizationPlanProcessor()

    athlete_capacities = AthleteBaselineCapacities()
    athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(lower_bound=4, upper_bound=5),
                                                                   volume=StandardErrorRange(lower_bound=200, upper_bound=250))

    training_exposures_to_progress = {}
    training_exposures_to_progress[DetailedAdaptationType.anaerobic_threshold_training] = 0  # progression week 0

    training_phase_factory = TrainingPhaseFactory()
    training_phase = training_phase_factory.create(TrainingPhaseType.increase)

    progression_factory = PeriodizationProgressionFactory()
    progressions = progression_factory.create(PeriodizationPersona.well_trained, TrainingPhaseType.increase)

    athlete_capacities = proc.update_athlete_capacity(athlete_capacities, training_exposures_to_progress, progressions, training_phase)

    assert athlete_capacities.anaerobic_threshold_training.rpe.lower_bound > 4


def test_create_periodization_plan():

    start_date = datetime(2020, 9, 1)

    proc = PeriodizationPlanProcessor()

    sub_adaptation_type_persona = SubAdaptionTypePersonas(TrainingPersona.intermediate, TrainingPersona.intermediate, TrainingPersona.intermediate)

    goal_factory = PeriodizationGoalFactory()
    periodization_goal = goal_factory.create(PeriodizationGoalType.increase_cardio_endurance)

    periodization_plan = PeriodizationPlan(start_date, [periodization_goal], TrainingPhaseType.increase, PeriodizationPersona.well_trained,sub_adaptation_type_persona)

    periodization_plan.target_weekly_rpe_load = StandardErrorRange(lower_bound=1000, upper_bound=1100)

    plan = proc.initialize_periodization_plan(periodization_plan)

    assert 5.0 == plan.athlete_capacities.anaerobic_threshold_training.rpe.observed_value


def test_update_periodization_plan_week():

    start_date = datetime(2020, 9, 1)
    event_date = datetime(2020, 9, 8)

    proc = PeriodizationPlanProcessor()

    sub_adaptation_type_persona = SubAdaptionTypePersonas(TrainingPersona.intermediate, TrainingPersona.intermediate,
                                                          TrainingPersona.intermediate)

    goal_factory = PeriodizationGoalFactory()
    periodization_goal = goal_factory.create(PeriodizationGoalType.increase_cardio_endurance)

    periodization_plan = PeriodizationPlan(start_date, [periodization_goal], TrainingPhaseType.increase, PeriodizationPersona.well_trained, sub_adaptation_type_persona)

    periodization_plan.target_weekly_rpe_load = StandardErrorRange(lower_bound=1000, upper_bound=1100)

    plan = proc.initialize_periodization_plan(periodization_plan)

    initial_volume = plan.target_training_exposures[0].training_exposures[0].volume.highest_value()

    plan.target_training_exposures[0].exposure_count.observed_value = 0
    plan.target_training_exposures[1].exposure_count.observed_value = 0

    user_stats = UserStats("tester")
    user_stats.average_weekly_internal_load=StandardErrorRange(lower_bound=1000, upper_bound=1100)

    plan = proc.update_periodization_plan_for_week(plan, event_date,user_stats)

    assert 0 < plan.target_training_exposures[0].exposure_count.observed_value
    assert 0 < plan.target_training_exposures[1].exposure_count.observed_value
    assert initial_volume < plan.target_training_exposures[0].training_exposures[0].volume.highest_value()


def test_updating_athlete_training_exposures():


    training_exposures = get_base_training_workout_exposures()
    target_training_exposures = get_base_training_long_exposure_needs()

    proc = PeriodizationPlanProcessor()

    assert 5 == target_training_exposures[0].exposure_count.highest_value()

    proc.update_exposure_needs(target_training_exposures, training_exposures)

    assert 4 == target_training_exposures[0].exposure_count.highest_value()


