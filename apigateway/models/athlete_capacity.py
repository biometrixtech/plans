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
        # Personas
        self.cardio_training_persona = TrainingPersona.beginner
        self.power_training_persona = TrainingPersona.beginner
        self.strength_training_persona = TrainingPersona.beginner


class TrainingUnit(object):
    def __init__(self, rpe=None, volume=None):
        self.rpe = rpe
        self.volume = volume


class AthleteDefaultCapacityFactory(object):

    def get_default_capacities(self, training_persona):

        athlete_capacities = AthleteBaselineCapacities()

        if training_persona == TrainingPersona.beginner:

            athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=5 * 60))
            athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange())
            athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange())
            # TODO: Power
            athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                               volume=StandardErrorRange(observed_value=48))
            athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange())
            athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.novice:

            athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=5 * 60))
            athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=4 * 60))
            athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange())
            # TODO: Power
            athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                               volume=StandardErrorRange(observed_value=60))
            athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange())
            athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.intermediate:

            athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=9 * 60))
            athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=1 * 60))
            # TODO: Power
            athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6),
                                                               volume=StandardErrorRange(observed_value=72))
            athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8),
                                                        volume=StandardErrorRange(observed_value=72))
            athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange())

        elif training_persona == TrainingPersona.advanced:

            athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=12 * 60))
            athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=2 * 60))
            # TODO: Power
            athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=84))
            athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange(observed_value=90))
            athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange(observed_value=4))

        elif training_persona == TrainingPersona.elite:

            athlete_capacities.base_aerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=2.5), volume=StandardErrorRange(observed_value=10 * 60))
            athlete_capacities.anaerobic_threshold_training = TrainingUnit(rpe=StandardErrorRange(observed_value=4.5), volume=StandardErrorRange(observed_value=15 * 60))
            athlete_capacities.high_intensity_anaerobic_training = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=2 * 60))
            # TODO: Power
            athlete_capacities.strength_endurance = TrainingUnit(rpe=StandardErrorRange(observed_value=6), volume=StandardErrorRange(observed_value=96))
            athlete_capacities.hypertrophy = TrainingUnit(rpe=StandardErrorRange(observed_value=8), volume=StandardErrorRange(observed_value=108))
            athlete_capacities.maximal_strength = TrainingUnit(rpe=StandardErrorRange(observed_value=9.3), volume=StandardErrorRange(observed_value=5))

        return athlete_capacities
