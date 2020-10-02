from models.movement_tags import DetailedAdaptationType
from models.periodization_utilities import PeriodizationUtilities
from models.workout_score import WorkoutScore

class WorkoutScoringProcessor(object):

    def score_workout(self, athlete_baseline_capacities, athlete_exposure_needs, training_exposures):

        workout_score = WorkoutScore()

        workout_score.total_score = 0

        workout_score.is_safe = self.is_safe(athlete_baseline_capacities, training_exposures)

        if workout_score.is_safe:

            workout_score.total_score += 35

            workout_score.is_relevant = self.is_relevant(athlete_exposure_needs, training_exposures)

            if workout_score.is_relevant:
                workout_score.total_score += 20

            workout_score.is_necessary = self.is_necessary(athlete_exposure_needs, training_exposures)

            if workout_score.is_necessary:
                workout_score.total_score += 20

            #ideal_score = self.get_ideal_score(athlete_exposure_needs, training_exposures)

            #total_score += ideal_score

        return workout_score

    def is_safe(self, athlete_baseline_capacities, training_exposures, injury_risk_dict=None,
                session_load_dict=None):

        safe = True

        for training_exposure in training_exposures:
            exposure_adaptation_name = training_exposure.detailed_adaptation_type.name
            athlete_capacity = getattr(athlete_baseline_capacities, exposure_adaptation_name)
            if athlete_capacity is None:
                return False
            if athlete_capacity.rpe is None or athlete_capacity.volume is None:
                return False
            # TEMP FIX
            # if training_exposure.volume.highest_value() is None:
            #     return False
            # if athlete_capacity.volume.highest_value() is None:
            #     return False
            if athlete_capacity.rpe.highest_value() * 1.10 < training_exposure.rpe.highest_value():
                if athlete_capacity.volume.highest_value() is None:
                    return False
                elif athlete_capacity.volume.highest_value() * 1.10 < training_exposure.volume.highest_value():
                    return False

        return safe

    def is_relevant(self, athlete_exposure_needs, training_exposures):

        relevant = False

        utils = PeriodizationUtilities()

        total_needs = len(athlete_exposure_needs)

        if total_needs > 0:

            exposures_found = 0

            for athlete_exposure_need in athlete_exposure_needs:
                if utils.is_athlete_need_in_workout_exposures(athlete_exposure_need, training_exposures, factor=1.10):
                    exposures_found += 1

            #found_ratio = exposures_found / float(total_needs)

            #score = found_ratio * 20

            if exposures_found > 0:
                #score = 20
                relevant = True

        return relevant

    def is_necessary(self, athlete_exposure_needs, training_exposures):

        necessary = False

        utils = PeriodizationUtilities()

        total_needs = len(athlete_exposure_needs)

        if total_needs > 0:

            exposures_found = 0

            for athlete_exposure_need in athlete_exposure_needs:
                if utils.is_athlete_need_in_workout_exposures(athlete_exposure_need, training_exposures, include_count=True):
                    exposures_found += 1

            #found_ratio = exposures_found / float(total_needs)

            #score = found_ratio * 20
            if exposures_found > 0:
                #score = 20
                necessary = True

        return necessary

    def get_ideal_score(self, athlete_exposure_needs, training_exposures):

        score = 0

        return score


