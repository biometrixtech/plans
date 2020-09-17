from models.periodization_plan import PeriodizationPlan, PeriodizationProgressionFactory, TrainingPhaseFactory
from models.periodization_goal import PeriodizationGoalFactory
from models.exposure import AthleteTargetTrainingExposure, TargetTrainingExposure, TrainingExposure
from models.athlete_capacity import AthleteBaselineCapacities
from logic.athlete_capacity_processing import AthleteCapacityProcessor
from models.periodization_utilities import PeriodizationUtilities
from models.training_volume import StandardErrorRange


class PeriodizationPlanProcessor(object):

    def create_periodization_plan(self, start_date, athlete_periodization_goals, training_phase_type, athlete_persona, sub_adaptation_type_personas, user_stats):

        periodization_plan = PeriodizationPlan(start_date,athlete_periodization_goals, training_phase_type, athlete_persona, sub_adaptation_type_personas)

        if user_stats.total_historical_sessions < 5:
            raise ValueError("Periodization plans require at least 5 training sessions in the last 35 days")

        periodization_plan.target_weekly_rpe_load = self.get_target_weekly_rpe_load(user_stats.average_weekly_internal_load, training_phase_type)

        periodization_plan = self.initialize_periodization_plan(periodization_plan,
                                                                existing_athlete_capacities=user_stats.athlete_capacities)

        return periodization_plan

    def update_exposure_needs(self, athlete_exposure_needs, training_exposures):

        utils = PeriodizationUtilities()

        total_needs = len(athlete_exposure_needs)

        if total_needs > 0:

            #for athlete_exposure_need in athlete_exposure_needs:
            for a in range(0, len(athlete_exposure_needs)):
                if utils.does_workout_exposure_meet_athlete_need(athlete_exposure_needs[a], training_exposures, include_count=True):
                    if athlete_exposure_needs[a].exposure_count.lowest_value() > 0:
                        athlete_exposure_needs[a].exposure_count.subtract_value(1)

    def get_target_weekly_rpe_load(self, average_weekly_internal_load, training_phase_type):

        weekly_load_target = None

        if average_weekly_internal_load is None:
            return weekly_load_target

        training_phase_factory = TrainingPhaseFactory()
        training_phase = training_phase_factory.create(training_phase_type)

        weekly_load_target = self.get_weekly_load_target(average_weekly_internal_load, training_phase.acwr)

        return weekly_load_target

    def get_weekly_load_target(self, average_training_load, acwr_range):

        load_calcs_load = [average_training_load.lower_bound * acwr_range.lower_bound,
                           average_training_load.lower_bound * acwr_range.upper_bound,
                           average_training_load.upper_bound * acwr_range.lower_bound,
                           average_training_load.upper_bound * acwr_range.upper_bound]

        min_load_calcs_load = min(load_calcs_load)
        max_load_calcs_load = max(load_calcs_load)
        load = StandardErrorRange(lower_bound=min_load_calcs_load, upper_bound=max_load_calcs_load,
                                  observed_value=(min_load_calcs_load + max_load_calcs_load) / float(2))
        return load

    def initialize_periodization_plan(self, periodization_plan, existing_athlete_capacities=None):

        #target_training_exposures = periodization_plan.periodization_goals[0].target_training_exposures

        new_target_training_exposures = []

        for target_training_exposure in periodization_plan.periodization_goals[0].target_training_exposures:
            new_target_training_exposure = TargetTrainingExposure([])
            new_target_training_exposure.exposure_count = target_training_exposure.exposure_count.plagiarize()
            new_target_training_exposure.priority = target_training_exposure.priority
            for training_exposure in target_training_exposure.training_exposures:
                new_training_exposure = TrainingExposure(training_exposure.detailed_adaptation_type)
                if training_exposure.volume is not None:
                    new_training_exposure.volume = training_exposure.volume.plagiarize()
                else:
                    new_training_exposure.volume = None
                if training_exposure.rpe is not None:
                    new_training_exposure.rpe = training_exposure.rpe.plagiarize()
                else:
                    new_training_exposure.rpe = None
                if training_exposure.rpe_load is not None:
                    new_training_exposure.rpe_load = training_exposure.rpe_load.plagiarize()
                else:
                    new_training_exposure.rpe_load = None
                if training_exposure.weekly_load_percentage is not None:
                    new_training_exposure.weekly_load_percentage = training_exposure.weekly_load_percentage.plagiarize()
                else:
                    new_training_exposure.weekly_load_percentage = None
                new_training_exposure.volume_measure = training_exposure.volume_measure
                new_target_training_exposure.training_exposures.append(new_training_exposure)
            new_target_training_exposures.append(new_target_training_exposure)

        proc = AthleteCapacityProcessor()

        if existing_athlete_capacities is None:
            athlete_capacities = AthleteBaselineCapacities()
        else:
            athlete_capacities = existing_athlete_capacities

        periodization_plan.athlete_capacities = proc.update_capacity_with_defaults(athlete_capacities,
                                                                                   periodization_plan.sub_adaptation_type_personas)

        training_exposures_to_progress = {}

        for target_training_exposure in new_target_training_exposures:
            athlete_target_training_exposure = AthleteTargetTrainingExposure(target_training_exposure.training_exposures,
                                                                             target_training_exposure.exposure_count,
                                                                             target_training_exposure.priority,
                                                                             progression_week=0)

            # populate values from athlete's capacity
            for training_exposure in athlete_target_training_exposure.training_exposures:
                detailed_adaptation_type = training_exposure.detailed_adaptation_type.name
                athlete_capacity = getattr(periodization_plan.athlete_capacities, detailed_adaptation_type)
                training_exposure.rpe = athlete_capacity.rpe.plagiarize()
                if training_exposure.weekly_load_percentage is None:
                    training_exposure.volume = athlete_capacity.volume
                else:
                    training_exposure.rpe_load = self.get_load_for_weekly_percentage(periodization_plan.target_weekly_rpe_load,
                                                                                   periodization_plan.expected_weekly_workouts,
                                                                                   training_exposure.weekly_load_percentage)

                    training_exposure.volume = training_exposure.rpe_load.plagiarize()
                    training_exposure.volume.divide_range(training_exposure.rpe)

                    stop_here = 0

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

    def get_load_for_weekly_percentage(self, weekly_load_range, expected_workouts_range, percentage_range):

        loads = [weekly_load_range.lower_bound * (percentage_range.lower_bound/float(100)),
                   weekly_load_range.lower_bound * (percentage_range.upper_bound / float(100)),
                   weekly_load_range.upper_bound * (percentage_range.lower_bound / float(100)),
                   weekly_load_range.upper_bound * (percentage_range.upper_bound / float(100))]

        min_load = min(loads)
        max_load = max(loads)

        load = StandardErrorRange(lower_bound=min_load, upper_bound=max_load)

        return load


    def update_periodization_plan_for_week(self, periodization_plan: PeriodizationPlan, event_date, user_stats):

        if self.is_week_start_date(periodization_plan.start_date, event_date):
            goal_factory = PeriodizationGoalFactory()
            goal = goal_factory.create(periodization_plan.periodization_goals[0].periodization_goal_type)
            target_training_exposures = goal.target_training_exposures
            progression_factory = PeriodizationProgressionFactory()
            progressions = progression_factory.create(periodization_plan.athlete_persona,
                                                      periodization_plan.training_phase_type)

            training_phase_factory = TrainingPhaseFactory()
            training_phase = training_phase_factory.create(periodization_plan.training_phase_type)

            training_exposures_to_progress = {}

            periodization_plan.target_weekly_rpe_load = self.get_target_weekly_rpe_load(
                user_stats.average_weekly_internal_load, periodization_plan.training_phase_type)

            capacity_proc = AthleteCapacityProcessor()
            periodization_plan.athlete_capacities = capacity_proc.update_capacity_with_defaults(periodization_plan.athlete_capacities,
                                                                                                periodization_plan.sub_adaptation_type_personas)

            for athlete_target_training_exposure in periodization_plan.target_training_exposures:
                if athlete_target_training_exposure.exposure_count.highest_value() == 0:  # they completed them all!
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
                    if self.training_exposures_match(athlete_target_training_exposure.training_exposures,
                                                     target_training_exposure.training_exposures):
                        athlete_target_training_exposure.exposure_count = target_training_exposure.exposure_count

            # update the athlete capacities based on training phase and progression rules
            # need to loop through the capacities (vs the training exposures) to keep from increasing something 2x

            periodization_plan.athlete_capacities = self.update_athlete_capacity(periodization_plan.athlete_capacities,
                                                                                 training_exposures_to_progress,
                                                                                 progressions, training_phase)

            # update values from athlete's capacity
            for target_training_exposure in periodization_plan.target_training_exposures:
                for training_exposure in target_training_exposure.training_exposures:
                    detailed_adaptation_type = training_exposure.detailed_adaptation_type.name
                    athlete_capacity = getattr(periodization_plan.athlete_capacities, detailed_adaptation_type)
                    training_exposure.rpe = athlete_capacity.rpe.plagiarize()
                    if training_exposure.weekly_load_percentage is None:
                        training_exposure.volume = athlete_capacity.volume
                    else:
                        training_exposure.rpe_load = self.get_load_for_weekly_percentage(periodization_plan.target_weekly_rpe_load,
                                                                                         periodization_plan.expected_weekly_workouts,
                                                                                         training_exposure.weekly_load_percentage)
                        training_exposure.volume = training_exposure.rpe_load.plagiarize()
                        training_exposure.volume.divide_range(training_exposure.rpe)

            periodization_plan.target_training_exposures = self.update_athlete_training_exposures(periodization_plan.target_training_exposures,
                                                                                                  training_exposures_to_progress,
                                                                                                  progressions,training_phase)

        return periodization_plan

    def training_exposures_match(self, exposure_list_1, exposure_list_2):

        found_times = 0

        if len(exposure_list_1) != len(exposure_list_2):
            return False

        for exposure_1 in exposure_list_1:
            for exposure_2 in exposure_list_2:
                if exposure_1.detailed_adaptation_type.value == exposure_2.detailed_adaptation_type.value:
                    if exposure_1.weekly_load_percentage is not None and exposure_2.weekly_load_percentage is not None:
                        if (exposure_1.weekly_load_percentage.lower_bound == exposure_2.weekly_load_percentage.lower_bound and
                                exposure_1.weekly_load_percentage.observed_value == exposure_2.weekly_load_percentage.observed_value and
                                exposure_1.weekly_load_percentage.upper_bound == exposure_2.weekly_load_percentage.upper_bound):
                            found_times += 1
                    if exposure_1.weekly_load_percentage is None and exposure_2.weekly_load_percentage is None:
                        found_times += 1

        if found_times == len(exposure_list_1):
            return True
        else:
            return False

    def is_week_start_date(self, start_date, event_date):

        if (event_date.date() - start_date.date()).days % 7 == 0:
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

    def update_athlete_training_exposures(self, athlete_training_exposures, training_exposures_to_progress, progressions, training_phase):

        for detailed_adaptation_type, progression_week in training_exposures_to_progress.items():
            for athlete_training_exposure in athlete_training_exposures:
                for training_exposure in athlete_training_exposure.training_exposures:
                    if training_exposure.detailed_adaptation_type == detailed_adaptation_type:
                        progression = progressions[progression_week]
                        rpe_lower_ratio = (training_phase.acwr.lower_bound - 1) * progression.rpe_load_contribution
                        volume_lower_ratio = (training_phase.acwr.lower_bound - 1) * progression.volume_load_contribution
                        rpe_upper_ratio = (training_phase.acwr.upper_bound - 1) * progression.rpe_load_contribution
                        volume_upper_ratio = (training_phase.acwr.upper_bound - 1) * progression.volume_load_contribution
                        if training_exposure.rpe.lower_bound is not None:
                            training_exposure.rpe.lower_bound = min(training_exposure.rpe.lower_bound * (1 + rpe_lower_ratio), 10)
                        if training_exposure.rpe.observed_value is not None:
                            training_exposure.rpe.observed_value = min(training_exposure.rpe.observed_value * (1 + ((rpe_lower_ratio + rpe_upper_ratio)/float(2))),10)
                        if training_exposure.rpe.upper_bound is not None:
                            training_exposure.rpe.upper_bound = min(training_exposure.rpe.upper_bound * (1 + rpe_upper_ratio), 10)
                        if training_exposure.volume.lower_bound is not None:
                            training_exposure.volume.lower_bound = training_exposure.volume.lower_bound * (1 + volume_lower_ratio)
                        if training_exposure.volume.observed_value is not None:
                            training_exposure.volume.observed_value = training_exposure.volume.observed_value * (1 + ((volume_lower_ratio + volume_upper_ratio)/float(2)))
                        if training_exposure.volume.upper_bound is not None:
                            training_exposure.volume.upper_bound = training_exposure.volume.upper_bound * (1 + volume_upper_ratio)
        return athlete_training_exposures






