from models.periodization_goal import TrainingPersona
from models.athlete_capacity import AthleteBaselineCapacities, AthleteDefaultCapacityFactory, TrainingUnit
from logic.athlete_capacity_processing import AthleteCapacityProcessor
from models.training_volume import StandardErrorRange


def training_units_equal(training_unit_1, training_unit_2):

    if training_unit_1 is None:
        if training_unit_2 is None:
            return True
        else:
            return False

    if training_unit_2 is None:
        if training_unit_1 is None:
            return True
        else:
            return False

    if training_unit_1.rpe.lower_bound != training_unit_2.rpe.lower_bound:
        return False
    if training_unit_1.rpe.observed_value != training_unit_2.rpe.observed_value:
        return False
    if training_unit_1.rpe.upper_bound != training_unit_2.rpe.upper_bound:
        return False
    if training_unit_1.volume.lower_bound != training_unit_2.volume.lower_bound:
        return False
    if training_unit_1.volume.observed_value != training_unit_2.volume.observed_value:
        return False
    if training_unit_1.volume.upper_bound != training_unit_2.volume.upper_bound:
        return False

    return True


def test_all_default_if_all_none():

    training_personas = list(TrainingPersona)
    factory = AthleteDefaultCapacityFactory()

    for training_persona in training_personas:

        # completely null object
        athlete_capacities = AthleteBaselineCapacities()

        assert athlete_capacities.base_aerobic_training is None
        assert athlete_capacities.anaerobic_threshold_training is None
        assert athlete_capacities.high_intensity_anaerobic_training is None
        assert athlete_capacities.muscular_endurance is None
        assert athlete_capacities.hypertrophy is None
        assert athlete_capacities.maximal_strength is None

        default_capacities = factory.get_default_capacities(training_persona)

        proc = AthleteCapacityProcessor()

        athlete_capacities = proc.update_capacity_with_defaults(athlete_capacities, training_persona)

        assert training_units_equal(default_capacities.base_aerobic_training, athlete_capacities.base_aerobic_training)
        assert training_units_equal(default_capacities.anaerobic_threshold_training, athlete_capacities.anaerobic_threshold_training)
        assert training_units_equal(default_capacities.high_intensity_anaerobic_training, athlete_capacities.high_intensity_anaerobic_training)
        assert training_units_equal(default_capacities.muscular_endurance, athlete_capacities.muscular_endurance)
        assert training_units_equal(default_capacities.hypertrophy, athlete_capacities.hypertrophy)
        assert training_units_equal(default_capacities.maximal_strength, athlete_capacities.maximal_strength)


def test_ignore_default_if_higher():

    training_personas = list(TrainingPersona)
    factory = AthleteDefaultCapacityFactory()

    for training_persona in training_personas:

        # completely null object
        athlete_capacities = AthleteBaselineCapacities()

        athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.6),volume=StandardErrorRange(observed_value=16 * 60))

        default_capacities = factory.get_default_capacities(training_persona)

        proc = AthleteCapacityProcessor()

        athlete_capacities = proc.update_capacity_with_defaults(athlete_capacities, training_persona)

        assert not training_units_equal(default_capacities.anaerobic_threshold_training, athlete_capacities.anaerobic_threshold_training)
