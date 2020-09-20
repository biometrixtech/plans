from models.athlete_capacity import AthleteBaselineCapacities, AthleteDefaultCapacityFactory, TrainingUnit
from models.movement_tags import DetailedAdaptationType
from models.training_volume import StandardErrorRange
import datetime


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

    def get_clean_date(self, test_date):

        if isinstance(test_date, datetime.date):
            return test_date
        if isinstance(test_date, datetime.datetime):
            return test_date.date()

    def get_daily_readiness_scores(self, current_date, injury_risk_dict, user_stats, periodization_plan, training_phase):

        readiness_score = 0
        load_score = 0
        rpe_score = 0

        highest_acwr_allowed = training_phase.acwr.highest_value()

        power_load_acwr_ratio = None
        if user_stats.power_load_acwr is not None:
            power_load_acwr_highest = user_stats.power_load_acwr.highest_value()
            if power_load_acwr_highest is None or power_load_acwr_highest <= highest_acwr_allowed:
                power_load_acwr_ratio = None
            else:
                power_load_acwr_ratio = power_load_acwr_highest / highest_acwr_allowed

        internal_load_acwr_ratio = None
        if user_stats.internal_acwr is not None:
            internal_load_acwr_highest = user_stats.internal_acwr.highest_value()
            if internal_load_acwr_highest is None or internal_load_acwr_highest <= highest_acwr_allowed:
                internal_load_acwr_ratio = None
            else:
                internal_load_acwr_ratio = internal_load_acwr_highest / highest_acwr_allowed

        internal_strain_events = user_stats.internal_strain_events.highest_value() if user_stats.internal_strain_events is not None else None
        power_load_strain_events = user_stats.power_load_strain_events.highest_value() if user_stats.internal_strain_events is not None else None

        non_functional_overreaching_value = len(periodization_plan.non_functional_overreaching_muscles)

        functional_overreaching_value = len(periodization_plan.functional_overreaching_muscles)

        inflammation_level = self.get_inflammation_level(current_date, injury_risk_dict)

        muscle_spasm_level = self.get_muscle_spasm_level(current_date, injury_risk_dict)

        if non_functional_overreaching_value > 0 or max(inflammation_level, muscle_spasm_level) > 7: # is > 7 considered severe?

            if non_functional_overreaching_value == 0:
                readiness_score += 10
            readiness_score += (10 - muscle_spasm_level) / float(2)
            readiness_score += (10 - inflammation_level) / float(2)

            load_score = 0
            rpe_score = readiness_score / float(20)

        elif non_functional_overreaching_value == 0 and (functional_overreaching_value > 0 or
                                                         3 < inflammation_level <= 7 or 4 < muscle_spasm_level <= 7 or
                                                         (internal_load_acwr_ratio is not None and internal_load_acwr_ratio > 1.25) or
                                                         (power_load_acwr_ratio is not None and power_load_acwr_ratio <= 1.25)):

            readiness_score = 20

            if functional_overreaching_value == 0:
                readiness_score += 4

            readiness_score += (10 - muscle_spasm_level) / float(2)
            readiness_score += (10 - inflammation_level) / float(2)

            if power_load_acwr_ratio is None:
                readiness_score += 3
            if internal_load_acwr_ratio is None:
                readiness_score += 3

            if 3 < inflammation_level >= 7:
                load_score = (readiness_score / float(40)) * 50
            elif power_load_acwr_ratio is not None or internal_load_acwr_ratio is not None:
                load_score = 50
            else:
                load_score = 90

            rpe_score = (readiness_score / float(40)) + 2

        elif (non_functional_overreaching_value == 0 and functional_overreaching_value == 0 and
              (0 < inflammation_level <= 3 or 3 < muscle_spasm_level <= 4 or (internal_strain_events is not None and internal_strain_events > 2)
               or (power_load_strain_events is not None and  power_load_strain_events > 2) or
               (internal_load_acwr_ratio is None or internal_load_acwr_ratio <= 1.25) or
               (power_load_acwr_ratio is None or power_load_acwr_ratio <= 1.25))):

            readiness_score = 40

            readiness_score += (5 - muscle_spasm_level)
            readiness_score += (5 - inflammation_level)

            if internal_strain_events is None or internal_strain_events == 0:
                readiness_score += 6
            if internal_strain_events is not None and internal_strain_events == 1:
                readiness_score += 3
            if power_load_strain_events is None or power_load_strain_events == 0:
                readiness_score += 6
            if power_load_strain_events is not None and power_load_strain_events == 1:
                readiness_score += 3
            if power_load_acwr_ratio is None:
                readiness_score += 3
            if internal_load_acwr_ratio is None:
                readiness_score += 3

            load_score = ((readiness_score / float(70)) * 10) + 90
            rpe_score = ((readiness_score / float(70)) * 2) + 4

        elif (non_functional_overreaching_value == 0 and functional_overreaching_value == 0 and inflammation_level == 0 and 0 < muscle_spasm_level <= 3
              and power_load_acwr_ratio is None and internal_load_acwr_ratio is None and 0 <= internal_strain_events <= 2 and 0 <= power_load_strain_events <= 2):

            readiness_score = 70

            readiness_score += (5 - muscle_spasm_level)

            if internal_strain_events is None or internal_strain_events == 0:
                readiness_score += 7
            if internal_strain_events is not None and internal_strain_events == 1:
                readiness_score += 3.5
            if power_load_strain_events is None or power_load_strain_events == 0:
                readiness_score += 7
            if power_load_strain_events is not None and power_load_strain_events == 1:
                readiness_score += 3.5

            load_score = 100
            rpe_score = (readiness_score / float(90)) + 7

        elif (non_functional_overreaching_value == 0 and functional_overreaching_value == 0 and inflammation_level == 0
              and muscle_spasm_level == 0 and power_load_acwr_ratio is None and internal_load_acwr_ratio is None):

            readiness_score = 90

            if internal_strain_events is None or internal_strain_events == 0:
                readiness_score += 5
            if internal_strain_events is not None and internal_strain_events == 1:
                readiness_score += 2.5
            if power_load_strain_events is None or power_load_strain_events == 0:
                readiness_score += 5
            if power_load_strain_events is not None and power_load_strain_events == 1:
                readiness_score += 2.5

            load_score = ((readiness_score / float(100)) * 5) + 105
            rpe_score = (readiness_score / float(90)) + 9

        return readiness_score, load_score, rpe_score

    def get_inflammation_level(self, current_date, injury_risk_dict):

        inflammation_level = 0

        for body_part_side, body_part_injury_risk in injury_risk_dict.items():
            if body_part_injury_risk.last_sharp_date is not None and (current_date.date() == self.get_clean_date(body_part_injury_risk.last_sharp_date)):
                inflammation_level = max(body_part_injury_risk.last_sharp_level, inflammation_level)
            if body_part_injury_risk.last_ache_date is not None and (
                    current_date.date() == self.get_clean_date(body_part_injury_risk.last_ache_date)):
                inflammation_level = max(body_part_injury_risk.last_ache_level, inflammation_level)

        return inflammation_level

    def get_muscle_spasm_level(self, current_date, injury_risk_dict):

        muscle_spasm_level = 0

        for body_part_side, body_part_injury_risk in injury_risk_dict.items():
            if body_part_injury_risk.last_sharp_date is not None and (current_date.date() == self.get_clean_date(body_part_injury_risk.last_sharp_date)):
                muscle_spasm_level = max(body_part_injury_risk.last_sharp_level, muscle_spasm_level)
            if body_part_injury_risk.last_ache_date is not None and (
                    current_date.date() == self.get_clean_date(body_part_injury_risk.last_ache_date)):
                muscle_spasm_level = max(body_part_injury_risk.last_ache_level, muscle_spasm_level)
            if body_part_injury_risk.last_tight_date is not None and (
                    current_date.date() == self.get_clean_date(body_part_injury_risk.last_tight_date)):
                muscle_spasm_level = max(body_part_injury_risk.last_tight_level, muscle_spasm_level)

        return muscle_spasm_level

