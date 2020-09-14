class PeriodizationUtilities(object):

    def is_athlete_need_in_workout_exposures(self, athlete_target_training_exposure_need, workout_training_exposures,
                                             include_count=False, factor=1.05):
        if include_count:
            if athlete_target_training_exposure_need.exposure_count == 0:
                return False

        # there may be optional training exposures for a single athlete exposure need,
        # i.e., "you need to have one of the following..."
        possible_target_training_exposures = athlete_target_training_exposure_need.training_exposures

        for possible_target_training_exposure in possible_target_training_exposures:
            for workout_training_exposure in workout_training_exposures:
                if (
                        possible_target_training_exposure.detailed_adaptation_type == workout_training_exposure.detailed_adaptation_type
                        and possible_target_training_exposure.volume.lowest_value() <= workout_training_exposure.volume.lowest_value()
                        and (
                        workout_training_exposure.rpe.lowest_value() * factor) >= possible_target_training_exposure.rpe.lowest_value()
                        and workout_training_exposure.rpe.highest_value() <= possible_target_training_exposure.rpe.highest_value() * factor):  # allow a workout to be 5% higher and still be relevant
                    return True

        return False

    def does_workout_exposure_meet_athlete_need(self, athlete_target_training_exposure_need, workout_training_exposures, include_count=False):
        if include_count:
            if athlete_target_training_exposure_need.exposure_count == 0:
                return False

        # there may be optional training exposures for a single athlete exposure need,
        # i.e., "you need to have one of the following..."
        possible_target_training_exposures = athlete_target_training_exposure_need.training_exposures

        for possible_target_training_exposure in possible_target_training_exposures:
            for workout_training_exposure in workout_training_exposures:
                if (
                        possible_target_training_exposure.detailed_adaptation_type == workout_training_exposure.detailed_adaptation_type
                        and possible_target_training_exposure.volume.lowest_value() <= workout_training_exposure.volume.lowest_value()
                        and possible_target_training_exposure.rpe.lowest_value() <= workout_training_exposure.rpe.highest_value()):  # allow a workout to be higher and still be relevant
                    return True

        return False