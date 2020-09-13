from models.athlete_capacity import AthleteBaselineCapacities, AthleteDefaultCapacityFactory, TrainingUnit
from models.movement_tags import DetailedAdaptationType
from models.training_volume import StandardErrorRange


class AthleteCapacityProcessor(object):

    def get_capacity_from_workout_history(self, workouts):

        capacities = AthleteBaselineCapacities()

        detailed_adaptation_types = list(DetailedAdaptationType)

        # creating a dictionary of lists.  One list for each adaptation type.
        training_exposure_dictionary = {}

        for detailed_adaptation_type in detailed_adaptation_types:
            training_exposure_dictionary[detailed_adaptation_type] = []

        for workout in workouts:
            for training_exposure in workout.training_exposures:
                training_exposure_dictionary[training_exposure.detailed_adaptation_type].append(training_exposure)

        # now find the training exposures with the highest load
        for detailed_adaptation_type, training_exposures in training_exposure_dictionary.items():
            if len(training_exposures) >= 2:
                training_exposure_dictionary[detailed_adaptation_type].sort(key=lambda x:x.rpe_load.highest_value(), reverse=True)

                rpe_list = [training_exposures[0].rpe, training_exposures[1].rpe]
                volume_list = [training_exposures[0].volume, training_exposures[1].volume]

                avg_rpe = StandardErrorRange.get_average_from_error_range_list(rpe_list)
                avg_volume = StandardErrorRange.get_average_from_error_range_list(volume_list)

                training_unit = TrainingUnit(rpe=avg_rpe,
                                             volume=avg_volume)
                setattr(capacities, detailed_adaptation_type.name, training_unit)

            elif len(training_exposures) == 1:
                training_unit = TrainingUnit(rpe=training_exposures[0].rpe,
                                             volume=training_exposures[0].volume)
                setattr(capacities, detailed_adaptation_type.name, training_unit)

        return capacities

    def combine_default_capacities(self, athlete_default_cardio_capacities, athlete_default_power_capacities, athlete_default_strength_capacities):

        athlete_default_capacities = AthleteBaselineCapacities()

        athlete_default_capacities.base_aerobic_training = athlete_default_cardio_capacities.base_aerobic_training
        athlete_default_capacities.anaerobic_threshold_training = athlete_default_cardio_capacities.anaerobic_threshold_training
        athlete_default_capacities.high_intensity_anaerobic_training = athlete_default_cardio_capacities.high_intensity_anaerobic_training

        athlete_default_capacities.speed = athlete_default_power_capacities.speed
        athlete_default_capacities.power = athlete_default_power_capacities.power
        athlete_default_capacities.sustained_power = athlete_default_power_capacities.sustained_power
        athlete_default_capacities.maximal_power = athlete_default_power_capacities.maximal_power

        athlete_default_capacities.strength_endurance = athlete_default_strength_capacities.strength_endurance
        athlete_default_capacities.muscular_endurance = athlete_default_strength_capacities.muscular_endurance
        athlete_default_capacities.hypertrophy = athlete_default_strength_capacities.hypertrophy
        athlete_default_capacities.maximal_strength = athlete_default_strength_capacities.maximal_strength

        return athlete_default_capacities

    def update_capacity_with_defaults(self, athlete_capacities, sub_adaption_type_training_personas):

        factory = AthleteDefaultCapacityFactory()
        athlete_default_cardio_capacities = factory.get_cardio_capacities(sub_adaption_type_training_personas.cardio_persona)
        athlete_default_power_capacities = factory.get_power_capacities(sub_adaption_type_training_personas.power_persona)
        athlete_default_strength_capacities = factory.get_strength_capacities(sub_adaption_type_training_personas.strength_persona)

        athlete_default_capacities = self.combine_default_capacities(athlete_default_cardio_capacities,
                                                                     athlete_default_power_capacities,
                                                                     athlete_default_strength_capacities)

        athlete_capacities.base_aerobic_training = self.get_highest_capacity(athlete_capacities,
                                                                             athlete_default_capacities,
                                                                             "base_aerobic_training")
        athlete_capacities.anaerobic_threshold_training = self.get_highest_capacity(athlete_capacities,
                                                                                    athlete_default_capacities,
                                                                                    "anaerobic_threshold_training")
        athlete_capacities.high_intensity_anaerobic_training = self.get_highest_capacity(athlete_capacities,
                                                                                         athlete_default_capacities,
                                                                                         "high_intensity_anaerobic_training")
        athlete_capacities.muscular_endurance = self.get_highest_capacity(athlete_capacities,
                                                                          athlete_default_capacities,
                                                                          "muscular_endurance")
        athlete_capacities.strength_endurance = self.get_highest_capacity(athlete_capacities,
                                                                          athlete_default_capacities,
                                                                          "strength_endurance")
        athlete_capacities.hypertrophy = self.get_highest_capacity(athlete_capacities,
                                                                   athlete_default_capacities,
                                                                   "hypertrophy")
        athlete_capacities.hypertrophy = self.get_highest_capacity(athlete_capacities,
                                                                   athlete_default_capacities,
                                                                   "hypertrophy")
        athlete_capacities.maximal_strength = self.get_highest_capacity(athlete_capacities,
                                                                        athlete_default_capacities,
                                                                        "maximal_strength")
        athlete_capacities.speed = self.get_highest_capacity(athlete_capacities,
                                                             athlete_default_capacities,
                                                             "speed")
        athlete_capacities.sustained_power = self.get_highest_capacity(athlete_capacities,
                                                                       athlete_default_capacities,
                                                                       "sustained_power")
        athlete_capacities.power = self.get_highest_capacity(athlete_capacities,
                                                             athlete_default_capacities,
                                                             "power")
        athlete_capacities.maximal_power = self.get_highest_capacity(athlete_capacities,
                                                                     athlete_default_capacities,
                                                                     "maximal_power")

        return athlete_capacities

    def get_highest_capacity(self, existing_capacities, candidate_capacities, attribute_name):

        existing_capacity = getattr(existing_capacities, attribute_name)
        candidate_capacity = getattr(candidate_capacities, attribute_name)

        if existing_capacity is None:
            setattr(existing_capacities, attribute_name, candidate_capacity)
            existing_capacity = getattr(existing_capacities, attribute_name)
        elif candidate_capacity.rpe.highest_value() > existing_capacity.rpe.highest_value():
            existing_capacity.rpe = candidate_capacity.rpe
            existing_capacity.volume = candidate_capacity.volume

        return existing_capacity

