from models.athlete_capacity import AthleteBaselineCapacities, AthleteDefaultCapacityFactory


class AthleteCapacityProcessor(object):

    def get_capacity_from_workout_history(self):

        capacities = AthleteBaselineCapacities()

        return capacities

    def update_capacity_with_defaults(self, athlete_capacities: AthleteBaselineCapacities, training_persona):

        factory = AthleteDefaultCapacityFactory()
        athlete_default_capacities = factory.get_default_capacities(training_persona)

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

