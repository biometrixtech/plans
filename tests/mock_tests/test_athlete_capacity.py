from models.periodization_goal import TrainingPersona, SubAdaptionTypePersonas
from models.athlete_capacity import AthleteBaselineCapacities, AthleteDefaultCapacityFactory, TrainingUnit
from logic.athlete_capacity_processing import AthleteCapacityProcessor
from models.training_volume import StandardErrorRange
from models.session import MixedActivitySession
from models.exposure import TrainingExposure
from models.movement_tags import DetailedAdaptationType


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

        sub_adaptation_type_personas = SubAdaptionTypePersonas(cardio_persona=training_persona,
                                                               strength_persona=training_persona,
                                                               power_persona=training_persona)

        # completely null object
        athlete_capacities = AthleteBaselineCapacities()

        assert athlete_capacities.base_aerobic_training is None
        assert athlete_capacities.anaerobic_threshold_training is None
        assert athlete_capacities.high_intensity_anaerobic_training is None
        assert athlete_capacities.muscular_endurance is None
        assert athlete_capacities.hypertrophy is None
        assert athlete_capacities.maximal_strength is None

        proc = AthleteCapacityProcessor()

        default_cardio_capacities = factory.get_cardio_capacities(sub_adaptation_type_personas.cardio_persona)
        default_power_capacities = factory.get_power_capacities(sub_adaptation_type_personas.power_persona)
        default_strength_capacities = factory.get_strength_capacities(sub_adaptation_type_personas.strength_persona)

        default_capacities = proc.combine_default_capacities(default_cardio_capacities,
                                                             default_power_capacities,
                                                             default_strength_capacities)

        athlete_capacities = proc.update_capacity_with_defaults(athlete_capacities, sub_adaptation_type_personas)

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
        training_persona_1 = TrainingPersona(training_persona.value)
        training_persona_2 = TrainingPersona(training_persona.value)
        training_persona_3 = TrainingPersona(training_persona.value)
        sub_adaptation_type_personas = SubAdaptionTypePersonas(cardio_persona=training_persona_1,
                                                               strength_persona=training_persona_2,
                                                               power_persona=training_persona_3)

        # completely null object
        athlete_capacities = AthleteBaselineCapacities()

        proc = AthleteCapacityProcessor()

        default_cardio_capacities = factory.get_cardio_capacities(sub_adaptation_type_personas.cardio_persona)
        default_power_capacities = factory.get_power_capacities(sub_adaptation_type_personas.power_persona)
        default_strength_capacities = factory.get_strength_capacities(sub_adaptation_type_personas.strength_persona)

        default_capacities = proc.combine_default_capacities(default_cardio_capacities,
                                                             default_power_capacities,
                                                             default_strength_capacities)

        athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.6),volume=StandardErrorRange(observed_value=16 * 60))

        athlete_capacities = proc.update_capacity_with_defaults(athlete_capacities, sub_adaptation_type_personas)

        assert not training_units_equal(default_capacities.anaerobic_threshold_training, athlete_capacities.anaerobic_threshold_training)


def test_find_top_2_workouts_for_each_type():

    workout_1 = MixedActivitySession()
    workout_2 = MixedActivitySession()
    workout_3 = MixedActivitySession()
    workout_4 = MixedActivitySession()

    anaerobic_threshold_exposure_1 = TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training,
                                                      volume=StandardErrorRange(observed_value=150),
                                                      volume_measure=None,
                                                      rpe=StandardErrorRange(observed_value=5),
                                                      rpe_load=StandardErrorRange(observed_value=750))
    anaerobic_threshold_exposure_2 = TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training,
                                                      volume=StandardErrorRange(observed_value=125),
                                                      volume_measure=None,
                                                      rpe=StandardErrorRange(observed_value=4),
                                                      rpe_load=StandardErrorRange(observed_value=500))
    anaerobic_threshold_exposure_3 = TrainingExposure(DetailedAdaptationType.anaerobic_threshold_training,
                                                      volume=StandardErrorRange(observed_value=100),
                                                      volume_measure=None,
                                                      rpe=StandardErrorRange(observed_value=3),
                                                      rpe_load=StandardErrorRange(observed_value=300))

    muscular_endurance_exposure_1 = TrainingExposure(DetailedAdaptationType.muscular_endurance,
                                                      volume=StandardErrorRange(observed_value=150),
                                                      volume_measure=None,
                                                      rpe=StandardErrorRange(observed_value=5),
                                                      rpe_load=StandardErrorRange(observed_value=750))
    muscular_endurance_exposure_2 = TrainingExposure(DetailedAdaptationType.muscular_endurance,
                                                      volume=StandardErrorRange(observed_value=125),
                                                      volume_measure=None,
                                                      rpe=StandardErrorRange(observed_value=4),
                                                      rpe_load=StandardErrorRange(observed_value=500))

    strength_endurance_exposure_1 = TrainingExposure(DetailedAdaptationType.strength_endurance,
                                                      volume=StandardErrorRange(observed_value=150),
                                                      volume_measure=None,
                                                      rpe=StandardErrorRange(observed_value=5),
                                                      rpe_load=StandardErrorRange(observed_value=750))

    workout_1.training_exposures.append(anaerobic_threshold_exposure_1)
    workout_1.training_exposures.append(muscular_endurance_exposure_1)
    workout_1.training_exposures.append(strength_endurance_exposure_1)

    workout_2.training_exposures.append(anaerobic_threshold_exposure_2)
    workout_2.training_exposures.append(muscular_endurance_exposure_2)

    workout_3.training_exposures.append(anaerobic_threshold_exposure_3)

    workouts = [workout_1, workout_2, workout_3, workout_4]

    proc = AthleteCapacityProcessor()

    athlete_capacities = proc.get_capacity_from_workout_history(workouts)

    assert 4.5 == athlete_capacities.anaerobic_threshold_training.rpe.observed_value
    assert 137.5 == athlete_capacities.anaerobic_threshold_training.volume.observed_value

    assert 4.5 == athlete_capacities.muscular_endurance.rpe.observed_value
    assert 137.5 == athlete_capacities.muscular_endurance.volume.observed_value

    assert 5 == athlete_capacities.strength_endurance.rpe.observed_value
    assert 150 == athlete_capacities.strength_endurance.volume.observed_value

