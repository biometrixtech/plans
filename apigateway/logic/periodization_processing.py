from models.periodization_plan import PeriodizationPlan, PeriodizationProgressionFactory, TrainingPhaseFactory
from models.periodization_goal import PeriodizationGoalFactory
from models.exposure import AthleteTargetTrainingExposure
from models.athlete_capacity import AthleteBaselineCapacities
from logic.athlete_capacity_processing import AthleteCapacityProcessor


class PeriodizationPlanProcessor(object):

    def create_periodization_plan(self, event_date, periodization_goals, training_phase_type, athlete_persona, training_persona, existing_athlete_capacities=None):

        periodization_plan = PeriodizationPlan(event_date, periodization_goals, training_phase_type, athlete_persona)

        target_training_exposures = periodization_plan.periodization_goals[0].training_exposures
        # progression_factory = PeriodizationProgressionFactory()
        # progressions = progression_factory.create(periodization_plan.athlete_persona,
        #                                           periodization_plan.training_phase_type)
        #
        # training_phase_factory = TrainingPhaseFactory()
        # training_phase = training_phase_factory.create(periodization_plan.training_phase_type)

        proc = AthleteCapacityProcessor()

        if existing_athlete_capacities is None:
            athlete_capacities = AthleteBaselineCapacities()
        else:
            athlete_capacities = existing_athlete_capacities

        periodization_plan.athlete_capacities = proc.update_capacity_with_defaults(athlete_capacities, training_persona)

        training_exposures_to_progress = {}

        for target_training_exposure in target_training_exposures:
            athlete_target_training_exposure = AthleteTargetTrainingExposure(target_training_exposure.training_exposures,
                                                                             target_training_exposure.exposure_count,
                                                                             target_training_exposure.priority,
                                                                             progression_week=0)

            periodization_plan.target_training_exposures.append(athlete_target_training_exposure)

            for training_exposure in athlete_target_training_exposure.training_exposures:
                if training_exposure.detailed_adaptation_type not in training_exposures_to_progress:
                    training_exposures_to_progress[
                        training_exposure.detailed_adaptation_type] = athlete_target_training_exposure.progression_week
                else:
                    training_exposures_to_progress[training_exposure.detailed_adaptation_type] = max(
                        athlete_target_training_exposure.progression_week,
                        training_exposures_to_progress[training_exposure.detailed_adaptation_type])


        # Let's not do this out of the gate and invalidate our initial defaults

        # self.update_athlete_capacity(periodization_plan.athlete_capacities, training_exposures_to_progress,
        #                              progressions, training_phase)

        return periodization_plan

    def update_periodization_plan_week(self,  periodization_plan: PeriodizationPlan, event_date):

        if self.is_week_start_date(periodization_plan.start_date, event_date):
            goal_factory = PeriodizationGoalFactory()
            target_training_exposures = goal_factory.create(periodization_plan.periodization_goals[0])
            progression_factory = PeriodizationProgressionFactory()
            progressions = progression_factory.create(periodization_plan.athlete_persona,
                                                      periodization_plan.training_phase_type)

            training_phase_factory = TrainingPhaseFactory()
            training_phase = training_phase_factory.create(periodization_plan.training_phase_type)

            training_exposures_to_progress = {}

            for athlete_target_training_exposure in periodization_plan.target_training_exposures:
                if athlete_target_training_exposure.exposure_count == 0:  # they completed them all!
                    # advance training exposure to next week of the program!
                    athlete_target_training_exposure.progression_week = min(athlete_target_training_exposure.progression_week + 1,
                                                                            len(progressions) - 1)
                    for training_exposure in athlete_target_training_exposure.training_exposures:
                        if training_exposure.detailed_adaptation_type not in training_exposures_to_progress:
                            training_exposures_to_progress[training_exposure.detailed_adaptation_type] = athlete_target_training_exposure.progression_week
                        else:
                            training_exposures_to_progress[training_exposure.detailed_adaptation_type] = max(athlete_target_training_exposure.progression_week,
                                                                                                             training_exposures_to_progress[training_exposure.detailed_adaptation_type])
                # reset the expected counts to original goal
                for target_training_exposure in target_training_exposures:
                    if athlete_target_training_exposure == target_training_exposure:
                        athlete_target_training_exposure.exposure_count = target_training_exposure.expected_count

            # update the athlete capacities based on training phase and progression rules
            # need to loop through the capacities (vs the training exposures) to keep from increasing something 2x

            self.update_athlete_capacity(periodization_plan.athlete_capacities, training_exposures_to_progress,
                                         progressions, training_phase)

        return periodization_plan

    def is_week_start_date(self, start_date, event_date):

        if (event_date - start_date).days in [7, 14, 21, 28, 35]:
            return True
        else:
            return False

    def update_athlete_capacity(self, athlete_capacities, training_exposures_to_progress, progressions, training_phase):

        for training_exposure, progression_week in training_exposures_to_progress.items():
            athlete_capacity = getattr(athlete_capacities, training_exposure.name)
            progression = progressions[progression_week]
            rpe_lower_ratio = (training_phase.acwr.lower_bound - 1) * progression.rpe_load_contribution
            volume_lower_ratio = (training_phase.acwr.lower_bound - 1) * progression.volume_load_contribution
            rpe_upper_ratio = (training_phase.acwr.upper_bound - 1) * progression.rpe_load_contribution
            volume_upper_ratio = (training_phase.acwr.upper_bound - 1) * progression.volume_load_contribution
            if athlete_capacity.rpe.lower_bound is not None:
                athlete_capacity.rpe.lower_bound = athlete_capacity.rpe.lower_bound * (1 + rpe_lower_ratio)
            if athlete_capacity.rpe.observed_value is not None:
                athlete_capacity.rpe.observed_value = athlete_capacity.rpe.observed_value * (1 + ((rpe_lower_ratio + rpe_upper_ratio)/float(2)))
            if athlete_capacity.rpe.upper_bound is not None:
                athlete_capacity.rpe.upper_bound = athlete_capacity.rpe.upper_bound * (1 + rpe_upper_ratio)
            if athlete_capacity.volume.lower_bound is not None:
                athlete_capacity.volume.lower_bound = athlete_capacity.volume.lower_bound * (1 + volume_lower_ratio)
            if athlete_capacity.volume.observed_value is not None:
                athlete_capacity.volume.observed_value = athlete_capacity.volume.observed_value * (1 + ((volume_lower_ratio + volume_upper_ratio)/float(2)))
            if athlete_capacity.volume.upper_bound is not None:
                athlete_capacity.volume.upper_bound = athlete_capacity.volume.upper_bound * (1 + volume_upper_ratio)
        return athlete_capacities






