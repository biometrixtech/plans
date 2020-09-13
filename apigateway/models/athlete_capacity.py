from models.periodization_goal import TrainingPersona
from models.training_volume import StandardErrorRange


class AthleteBaselineCapacities(object):
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


class TrainingUnit(object):
    def __init__(self, rpe=None, volume=None):
        self.rpe = rpe
        self.volume = volume


class AthleteDefaultCapacityFactory(object):

    def get_cardio_capacities(self, training_persona):

        cardio_athlete_capacities = AthleteBaselineCapacities()

        if training_persona == TrainingPersona.beginner:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=5 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange())
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.novice:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=5 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=4 * 60))
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.intermediate:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=9 * 60))
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=1 * 60))

        elif training_persona == TrainingPersona.advanced:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=12 * 60))
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=2 * 60))

        elif training_persona == TrainingPersona.elite:

            cardio_athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            cardio_athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=15 * 60))
            cardio_athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=2 * 60))

        return cardio_athlete_capacities

    def get_strength_capacities(self, training_persona):

        strength_athlete_capacities = AthleteBaselineCapacities()

        if training_persona == TrainingPersona.beginner:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                               volume=StandardErrorRange(observed_value=48))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange())
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.novice:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                               volume=StandardErrorRange(observed_value=60))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange())
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.intermediate:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                               volume=StandardErrorRange(observed_value=72))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8),
                                                        volume=StandardErrorRange(observed_value=72))
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.advanced:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=84))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange(observed_value=90))
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange(observed_value=4))

        elif training_persona == TrainingPersona.elite:

            strength_athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=96))
            strength_athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange(observed_value=108))
            strength_athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange(observed_value=5))

        return strength_athlete_capacities

    def get_power_capacities(self, training_persona):

        power_athlete_capacities = AthleteBaselineCapacities()

        if training_persona == TrainingPersona.beginner:

            # TODO: Power
            pass

        elif training_persona == TrainingPersona.novice:

            # TODO: Power
            pass

        elif training_persona == TrainingPersona.intermediate:

            # TODO: Power
            pass

        elif training_persona == TrainingPersona.advanced:

            # TODO: Power
            pass

        elif training_persona == TrainingPersona.elite:

            # TODO: Power
            pass

        return power_athlete_capacities
