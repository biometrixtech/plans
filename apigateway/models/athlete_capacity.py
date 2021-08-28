from enum import Enum

from models.training_volume import StandardErrorRange
from serialisable import Serialisable


class TrainingPersona(Enum):
    """
    The different personas the determine the default baseline capacity
    """
    beginner = 0
    novice = 1
    intermediate = 2
    advanced = 3
    elite = 4


class SubAdaptionTypePersonas(object):
    """
    An athlete may identify as a different training persona by sub adaptation type
    This object stores the different training personas in one place

    """
    def __init__(self,
                 cardio_persona=TrainingPersona.beginner,
                 power_persona=TrainingPersona.beginner,
                 strength_persona=TrainingPersona.beginner):
        self.cardio_persona = cardio_persona
        self.power_persona = power_persona
        self.strength_persona = strength_persona


class AthleteReadiness(object):
    """
    This is the object which stores the results of the daily readiness score calculation.  It also stores details of the
    underlying components for diagnostic purposes.

    """

    def __init__(self):
        self.readiness_score = 0.0
        self.load_score = 0.0
        self.rpe_score = 0.0
        self.muscle_spasm_level = 0.0
        self.inflammation_level = 0.0
        self.internal_load_acwr_ratio = None
        self.power_load_acwr_ratio = None
        self.internal_acwr = None
        self.power_load_acwr = None
        self.internal_strain_events = 0
        self.power_load_strain_events = 0
        self.average_weekly_internal_load = None


class AthleteBaselineCapacities(Serialisable):
    """
    Stores the current baseline capacities for an athlete by training exposure/detailed adaptation type
    """
    def __init__(self):
        # Cardio
        self.base_aerobic_training = None
        self.anaerobic_threshold_training = None
        self.high_intensity_anaerobic_training = None
        # Strength
        self.muscular_endurance = None
        self.strength_endurance = None
        self.hypertrophy = None
        self.maximal_strength = None
        # Power
        self.speed = None
        self.sustained_power = None
        self.power = None
        self.maximal_power = None

    def json_serialise(self):
        ret = {
            'self.base_aerobic_training': self.base_aerobic_training.json_serialise() if self.base_aerobic_training is not None else None,
            'self.anaerobic_threshold_training': self.anaerobic_threshold_training.json_serialise() if self.anaerobic_threshold_training is not None else None,
            'self.high_intensity_anaerobic_training': self.high_intensity_anaerobic_training.json_serialise() if self.high_intensity_anaerobic_training is not None else None,
            'self.muscular_endurance': self.muscular_endurance.json_serialise() if self.muscular_endurance is not None else None,
            'self.strength_endurance': self.strength_endurance.json_serialise() if self.strength_endurance is not None else None,
            'self.hypertrophy': self.hypertrophy.json_serialise() if self.hypertrophy is not None else None,
            'self.maximal_strength': self.maximal_strength.json_serialise() if self.maximal_strength is not None else None,
            'self.speed': self.speed.json_serialise() if self.speed is not None else None,
            'self.sustained_power': self.sustained_power.json_serialise() if self.sustained_power is not None else None,
            'self.power': self.power.json_serialise() if self.power is not None else None,
            'self.maximal_power': self.maximal_power.json_serialise() if self.maximal_power is not None else None,
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):

        capacities = AthleteBaselineCapacities()
        capacities.base_aerobic_training = TrainingUnit(input_dict['base_aerobic_training']) if input_dict.get('base_aerobic_training') is not None else None
        capacities.anaerobic_threshold_training = TrainingUnit(input_dict['anaerobic_threshold_training']) if input_dict.get(
            'anaerobic_threshold_training') is not None else None
        capacities.high_intensity_anaerobic_training = TrainingUnit(input_dict['high_intensity_anaerobic_training']) if input_dict.get(
            'high_intensity_anaerobic_training') is not None else None
        capacities.muscular_endurance = TrainingUnit(input_dict['muscular_endurance']) if input_dict.get(
            'muscular_endurance') is not None else None
        capacities.strength_endurance = TrainingUnit(input_dict['strength_endurance']) if input_dict.get(
            'strength_endurance') is not None else None
        capacities.hypertrophy = TrainingUnit(input_dict['hypertrophy']) if input_dict.get(
            'hypertrophy') is not None else None
        capacities.maximal_strength = TrainingUnit(input_dict['maximal_strength']) if input_dict.get(
            'maximal_strength') is not None else None
        capacities.speed = TrainingUnit(input_dict['speed']) if input_dict.get(
            'speed') is not None else None
        capacities.sustained_power = TrainingUnit(input_dict['sustained_power']) if input_dict.get(
            'sustained_power') is not None else None
        capacities.power = TrainingUnit(input_dict['power']) if input_dict.get(
            'power') is not None else None
        capacities.maximal_power = TrainingUnit(input_dict['maximal_power']) if input_dict.get(
            'maximal_power') is not None else None

        return capacities


class TrainingUnit(Serialisable):

    """
    Object used to store both rpe and volume for a type of load (prevents unnecessary duplication of method names)
    """
    def __init__(self, rpe=None, volume=None):
        self.rpe = rpe
        self.volume = volume

    def json_serialise(self):
        ret = {
            'rpe': self.rpe.json_serialise() if self.rpe is not None else None,
            'volume': self.volume.json_serialise() if self.volume is not None else None,
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):

        training_unit = TrainingUnit()
        training_unit.rpe = StandardErrorRange(input_dict['rpe']) if input_dict.get('rpe') is not None else None
        training_unit.volume = StandardErrorRange(input_dict['volume']) if input_dict.get('volume') is not None else None
        return training_unit


class AthleteDefaultCapacityFactory(object):

    """
    Generates the default capacity for a given training exposure for a given training persona
    """

    def get_cardio_capacities(self, training_persona):

        cardio_athlete_capacities = AthleteBaselineCapacities()

        if training_persona == TrainingPersona.beginner:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=3.0), volume=StandardErrorRange(observed_value=5 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=5.0), volume=StandardErrorRange())
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=7.1), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.novice:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=3.0), volume=StandardErrorRange(observed_value=5 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=5.0), volume=StandardErrorRange(observed_value=4 * 60))
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=7.1), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.intermediate:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=3.0), volume=StandardErrorRange(observed_value=10 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=5.0), volume=StandardErrorRange(observed_value=9 * 60))
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=7.1), volume=StandardErrorRange(observed_value=1 * 60))

        elif training_persona == TrainingPersona.advanced:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=3.0), volume=StandardErrorRange(observed_value=10 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=5.0), volume=StandardErrorRange(observed_value=12 * 60))
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=7.1), volume=StandardErrorRange(observed_value=2 * 60))

        elif training_persona == TrainingPersona.elite:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=3.0), volume=StandardErrorRange(observed_value=10 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=5.0), volume=StandardErrorRange(observed_value=15 * 60))
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=7.1), volume=StandardErrorRange(observed_value=2 * 60))

        return cardio_athlete_capacities

    def get_strength_capacities(self, training_persona):

        strength_athlete_capacities = AthleteBaselineCapacities()

        if training_persona == TrainingPersona.beginner:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=5),
                                                               volume=StandardErrorRange(observed_value=48))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=7.2), volume=StandardErrorRange())
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.1), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.novice:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=5),
                                                               volume=StandardErrorRange(observed_value=60))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=7.2), volume=StandardErrorRange())
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.1), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.intermediate:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=5),
                                                               volume=StandardErrorRange(observed_value=72))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=7.2),
                                                        volume=StandardErrorRange(observed_value=72))
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.1), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.advanced:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=5), volume=StandardErrorRange(observed_value=84))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=7.2), volume=StandardErrorRange(observed_value=90))
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.1), volume=StandardErrorRange(observed_value=4))

        elif training_persona == TrainingPersona.elite:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=5), volume=StandardErrorRange(observed_value=96))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=7.2), volume=StandardErrorRange(observed_value=108))
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.1), volume=StandardErrorRange(observed_value=5))

        return strength_athlete_capacities

    def get_power_capacities(self, training_persona):

        power_athlete_capacities = AthleteBaselineCapacities()

        if training_persona == TrainingPersona.beginner:

            power_athlete_capacities.speed = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5),
                                                                          volume=StandardErrorRange(observed_value=48))
            power_athlete_capacities.power = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5),
                                                          volume=StandardErrorRange())
            power_athlete_capacities.maximal_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6.5),
                                                          volume=StandardErrorRange())
            power_athlete_capacities.sustained_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                                    volume=StandardErrorRange())


        elif training_persona == TrainingPersona.novice:

            power_athlete_capacities.speed = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5),
                                                          volume=StandardErrorRange(observed_value=64))
            power_athlete_capacities.power = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5),
                                                          volume=StandardErrorRange(observed_value=12))
            power_athlete_capacities.maximal_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6.5),
                                                                  volume=StandardErrorRange())
            power_athlete_capacities.sustained_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                                    volume=StandardErrorRange(4 * 60))

        elif training_persona == TrainingPersona.intermediate:

            power_athlete_capacities.speed = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5),
                                                          volume=StandardErrorRange(observed_value=80))
            power_athlete_capacities.power = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5),
                                                          volume=StandardErrorRange(observed_value=32))
            power_athlete_capacities.maximal_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6.5),
                                                                  volume=StandardErrorRange())
            power_athlete_capacities.sustained_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                                    volume=StandardErrorRange(9 * 60))

        elif training_persona == TrainingPersona.advanced:

            power_athlete_capacities.speed = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5),
                                                          volume=StandardErrorRange(observed_value=80))
            power_athlete_capacities.power = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5),
                                                          volume=StandardErrorRange(observed_value=90))
            power_athlete_capacities.maximal_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6.5),
                                                                  volume=StandardErrorRange(observed_value=60))
            power_athlete_capacities.sustained_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                                    volume=StandardErrorRange(12 * 60))

        elif training_persona == TrainingPersona.elite:

            power_athlete_capacities.speed = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5),
                                                          volume=StandardErrorRange(observed_value=80))
            power_athlete_capacities.power = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5),
                                                          volume=StandardErrorRange(observed_value=120))
            power_athlete_capacities.maximal_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6.5),
                                                                  volume=StandardErrorRange(observed_value=120))
            power_athlete_capacities.sustained_power = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                                    volume=StandardErrorRange(15 * 60))

        return power_athlete_capacities

