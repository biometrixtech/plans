from models.movement_tags import DetailedAdaptationType


class WorkoutScoringProcessor(object):

    def score_workout(self, athlete_baseline_capacities, athlete_exposure_needs, training_exposures):

        total_score = 0

        is_safe = self.is_safe(athlete_baseline_capacities, training_exposures)

        if is_safe:

            total_score += 35

            relevant_score = self.get_relevant_score(athlete_exposure_needs, training_exposures)

            total_score += relevant_score

            necessary_score = self.get_necessary_score(athlete_exposure_needs, training_exposures)

            total_score += necessary_score

            ideal_score = self.get_ideal_score(athlete_exposure_needs, training_exposures)

            total_score += ideal_score

        return total_score

    def is_safe(self, athlete_baseline_capacities, training_exposures):

        safe = True

        for training_exposure in training_exposures:
            exposure_adaptation_name = training_exposure.detailed_adaptation_type.name
            athlete_capacity = getattr(athlete_baseline_capacities, exposure_adaptation_name)
            if (athlete_capacity.rpe.highest_value() * 1.10 < training_exposure.rpe.highest_value() or
                athlete_capacity.volume.highest_value() * 1.10 < training_exposure.volume.highest_value()):
                return False

        return safe

    def get_relevant_score(self, athlete_exposure_needs, training_exposures):

        score = 0

        total_needs = len(athlete_exposure_needs)

        if total_needs > 0:

            exposures_found = 0

            for athlete_exposure_need in athlete_exposure_needs:
                if self.is_athlete_need_in_workout_exposures(athlete_exposure_need, training_exposures):
                    exposures_found += 1

            found_ratio = exposures_found / float(total_needs)

            score = found_ratio * 20

        return score

    def get_necessary_score(self, athlete_exposure_needs, training_exposures):

        score = 0

        total_needs = len(athlete_exposure_needs)

        if total_needs > 0:

            exposures_found = 0

            for athlete_exposure_need in athlete_exposure_needs:
                if self.is_athlete_need_in_workout_exposures(athlete_exposure_need, training_exposures, include_count=True):
                    exposures_found += 1

            found_ratio = exposures_found / float(total_needs)

            score = found_ratio * 20

        return score

    def get_ideal_score(self, athlete_exposure_needs, training_exposures):

        score = 0

        return score

    def is_athlete_need_in_workout_exposures(self, athlete_target_training_exposure_need, workout_training_exposures, include_count=False):

        if include_count:
            if athlete_target_training_exposure_need.exposure_count == 0:
                return False

        # there may be optional training exposures for a single athlete exposure need,
        # i.e., "you need to have one of the following..."
        possible_target_training_exposures = athlete_target_training_exposure_need.training_exposures

        for possible_target_training_exposure in possible_target_training_exposures:
            for workout_training_exposure in workout_training_exposures:
                if (possible_target_training_exposure.detailed_adaptation_type == workout_training_exposure.detailed_adaptation_type
                        and possible_target_training_exposure.volume.lowest_value() <= workout_training_exposure.volume.lowest_value()
                        and (workout_training_exposure.rpe.lowest_value() * 1.05) >= possible_target_training_exposure.rpe.lowest_value()
                        and workout_training_exposure.rpe.highest_value() <= possible_target_training_exposure.rpe.highest_value() * 1.05):  # allow a workout to be 5% higher and still be relevant
                    return True

        return False
