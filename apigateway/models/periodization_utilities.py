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
                        and (possible_target_training_exposure.rpe.lowest_value() >= workout_training_exposure.rpe.lowest_value())
                        and workout_training_exposure.rpe.highest_value() <= possible_target_training_exposure.rpe.highest_value() * factor):  # allow a workout to be 5% higher and still be relevant
                    return True
                elif possible_target_training_exposure.weekly_load_percentage is not None:# use load instead of volume:
                    if (possible_target_training_exposure.weekly_load_percentage.lower_bound is not None or
                            possible_target_training_exposure.weekly_load_percentage.observed_value is not None or
                            possible_target_training_exposure.weekly_load_percentage.upper_bound is not None):
                        if possible_target_training_exposure.detailed_adaptation_type == workout_training_exposure.detailed_adaptation_type:
                            if (possible_target_training_exposure.rpe_load.lowest_value()  <= workout_training_exposure.rpe_load.lowest_value()
                                    and workout_training_exposure.rpe_load.highest_value() >= possible_target_training_exposure.rpe_load.lowest_value() * factor):  # allow a workout to be higher and still be relevant
                                return True
        return False

    def does_workout_exposure_meet_athlete_need(self, athlete_target_training_exposure_need, workout_training_exposures, include_count=False):

        found_match = False

        if include_count:
            if athlete_target_training_exposure_need.exposure_count == 0:
                return found_match, workout_training_exposures

        # there may be optional training exposures for a single athlete exposure need,
        # i.e., "you need to have one of the following..."
        possible_target_training_exposures = athlete_target_training_exposure_need.training_exposures

        for possible_target_training_exposure in possible_target_training_exposures:
            for w in range(0, len(workout_training_exposures)):
                if (possible_target_training_exposure.detailed_adaptation_type == workout_training_exposures[w].detailed_adaptation_type and
                        possible_target_training_exposure.volume is None):
                    del workout_training_exposures[w]
                    found_match = True
                    return found_match, workout_training_exposures
                elif (possible_target_training_exposure.detailed_adaptation_type == workout_training_exposures[w].detailed_adaptation_type and
                        possible_target_training_exposure.volume.highest_value() is None):
                    del workout_training_exposures[w]
                    found_match = True
                    return found_match, workout_training_exposures
                elif (possible_target_training_exposure.detailed_adaptation_type == workout_training_exposures[w].detailed_adaptation_type
                        and possible_target_training_exposure.volume.lowest_value() <= workout_training_exposures[w].volume.lowest_value()
                        and possible_target_training_exposure.rpe.lowest_value() <= workout_training_exposures[w].rpe.highest_value()):  # allow a workout to be higher and still be relevant
                    del workout_training_exposures[w]
                    found_match = True
                    return found_match, workout_training_exposures
                elif possible_target_training_exposure.weekly_load_percentage is not None:# use load instead of volume:
                    if (possible_target_training_exposure.weekly_load_percentage.lower_bound is not None or
                            possible_target_training_exposure.weekly_load_percentage.observed_value is not None or
                            possible_target_training_exposure.weekly_load_percentage.upper_bound is not None):
                        if possible_target_training_exposure.detailed_adaptation_type == workout_training_exposures[w].detailed_adaptation_type:
                            if (workout_training_exposures[w].rpe_load.lowest_value() >= possible_target_training_exposure.rpe_load.lowest_value()
                                    or workout_training_exposures[w].rpe_load.highest_value() >= possible_target_training_exposure.rpe_load.lowest_value()):  # allow a workout to be higher and still be relevant
                                del workout_training_exposures[w]
                                found_match = True
                                return found_match, workout_training_exposures
        return found_match, workout_training_exposures
