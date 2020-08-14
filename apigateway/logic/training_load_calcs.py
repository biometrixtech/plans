from models.training_volume import StandardErrorRange
from models.training_load import LoadType, DetailedTrainingLoad, TrainingLoad
from statistics import mean


class TrainingLoadCalculator(object):

    # def __init__(self,
    #              last_week_load_list: [StandardErrorRange],
    #              previous_week_1_load_list: [StandardErrorRange],
    #              previous_week_2_load_list: [StandardErrorRange],
    #              previous_week_3_load_list: [StandardErrorRange],
    #              previous_week_4_load_list: [StandardErrorRange],
    #              calculate_averages=True,
    #              calculate_detailes=False):

    #     self.last_week_load_list = last_week_load_list
    #     self.previous_week_1_load_list = previous_week_1_load_list
    #     self.previous_week_2_load_list = previous_week_2_load_list
    #     self.previous_week_3_load_list = previous_week_3_load_list
    #     self.previous_week_4_load_list = previous_week_4_load_list
    #
    #     self.last_week_rpe_load_values = []
    #     self.previous_week_1_rpe_load_values = []
    #     self.previous_week_2_rpe_load_values = []
    #     self.previous_week_3_rpe_load_values = []
    #     self.previous_week_4_rpe_load_values = []
    #
    #     self.last_week_power_load_values = []
    #     self.previous_week_1_power_load_values = []
    #     self.previous_week_2_power_load_values = []
    #     self.previous_week_3_power_load_values = []
    #     self.previous_week_4_power_load_values = []
    #
    #     self.last_week_rpe_values = []
    #     self.previous_week_1_rpe_values = []
    #     self.previous_week_2_rpe_values = []
    #     self.previous_week_3_rpe_values = []
    #     self.previous_week_4_rpe_values = []
    #
    #     self.last_week_rpe_load_sum = None
    #     self.previous_week_1_rpe_load_sum = None
    #     self.previous_week_2_rpe_load_sum = None
    #     self.previous_week_3_rpe_load_sum = None
    #     self.previous_week_4_rpe_load_sum = None
    #     self.chronic_rpe_load_average = None
    #
    #     self.last_week_power_load_sum = None
    #     self.previous_week_1_power_load_sum = None
    #     self.previous_week_2_power_load_sum = None
    #     self.previous_week_3_power_load_sum = None
    #     self.previous_week_4_power_load_sum = None
    #     self.chronic_power_load_average = None
    #
    #     self.average_session_load = TrainingLoad()
    #     self.average_session_rpe = None
    #     self.average_sessions_per_week = None
    #
    #     self.last_weeks_detailed_load = DetailedTrainingLoad()
    #     self.previous_1_weeks_detailed_load = DetailedTrainingLoad()
    #     self.previous_2_weeks_detailed_load = DetailedTrainingLoad()
    #     self.previous_3_weeks_detailed_load = DetailedTrainingLoad()
    #     self.previous_4_weeks_detailed_load = DetailedTrainingLoad()
    #
    #     self.populate_values()
    #     self.sum_weeks()
    #     if calculate_averages:
    #         self.calculate_averages()
    #
    #     if calculate_detailes:
    #         self.calculate_weekly_detailed_training_load()
    #
    # def populate_values(self):
    #
    #     self.last_week_rpe_load_values = [l.rpe_load for l in self.last_week_load_list]
    #     self.previous_week_1_rpe_load_values = [l.rpe_load for l in self.previous_week_1_load_list]
    #     self.previous_week_2_rpe_load_values = [l.rpe_load for l in self.previous_week_2_load_list]
    #     self.previous_week_3_rpe_load_values = [l.rpe_load for l in self.previous_week_3_load_list]
    #     self.previous_week_4_rpe_load_values = [l.rpe_load for l in self.previous_week_4_load_list]
    #
    #     self.last_week_power_load_values = [l.power_load for l in self.last_week_load_list]
    #     self.previous_week_1_power_load_values = [l.power_load for l in self.previous_week_1_load_list]
    #     self.previous_week_2_power_load_values = [l.power_load for l in self.previous_week_2_load_list]
    #     self.previous_week_3_power_load_values = [l.power_load for l in self.previous_week_3_load_list]
    #     self.previous_week_4_power_load_values = [l.power_load for l in self.previous_week_4_load_list]
    #
    #     self.last_week_rpe_values = [l.session_RPE for l in self.last_week_load_list]
    #     self.previous_week_1_rpe_values = [l.session_RPE for l in self.previous_week_1_load_list]
    #     self.previous_week_2_rpe_values = [l.session_RPE for l in self.previous_week_2_load_list]
    #     self.previous_week_3_rpe_values = [l.session_RPE for l in self.previous_week_3_load_list]
    #     self.previous_week_4_rpe_values = [l.session_RPE for l in self.previous_week_4_load_list]
    #
    # def sum_weeks(self):
    #
    #     self.last_week_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.last_week_rpe_load_values)
    #     self.previous_week_1_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_1_rpe_load_values)
    #     self.previous_week_2_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_2_rpe_load_values)
    #     self.previous_week_3_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_3_rpe_load_values)
    #     self.previous_week_4_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_4_rpe_load_values)
    #
    #     self.last_week_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
    #         self.last_week_power_load_values)
    #     self.previous_week_1_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
    #         self.previous_week_1_power_load_values)
    #     self.previous_week_2_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
    #         self.previous_week_2_power_load_values)
    #     self.previous_week_3_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
    #         self.previous_week_3_power_load_values)
    #     self.previous_week_4_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
    #         self.previous_week_4_power_load_values)
    #
    # def calculate_averages(self):
    #
    #     rpe_chronic_weeks = [self.previous_week_1_rpe_load_sum,
    #                          self.previous_week_2_rpe_load_sum,
    #                          self.previous_week_3_rpe_load_sum,
    #                          self.previous_week_4_rpe_load_sum]
    #
    #     power_chronic_weeks = [self.previous_week_1_power_load_sum,
    #                            self.previous_week_2_power_load_sum,
    #                            self.previous_week_3_power_load_sum,
    #                            self.previous_week_4_power_load_sum]
    #
    #     self.chronic_rpe_load_average = StandardErrorRange.get_average_from_error_range_list(rpe_chronic_weeks)
    #     self.chronic_power_load_average = StandardErrorRange.get_average_from_error_range_list(power_chronic_weeks)
    #
    #     last_two_weeks_sessions = self.last_week_power_load_values
    #     last_two_weeks_sessions.extend(self.previous_week_1_power_load_values)
    #     if len(self.last_week_power_load_values) <= 1:
    #         last_two_weeks_sessions.extend(self.previous_week_2_power_load_values)
    #
    #     self.average_session_load = StandardErrorRange.get_average_from_error_range_list(last_two_weeks_sessions)
    #
    #     last_two_weeks_rpes = self.last_week_rpe_values
    #     last_two_weeks_rpes.extend(self.previous_week_1_rpe_values)
    #     if len(self.last_week_rpe_values) <= 1:
    #         last_two_weeks_rpes.extend(self.previous_week_2_rpe_values)
    #
    #     self.average_session_rpe = StandardErrorRange.get_average_from_error_range_list(last_two_weeks_rpes)
    #
    #     sessions_per_week = []
    #     started = False
    #     if len(self.previous_week_4_load_list) > 0:
    #         sessions_per_week.append(len(self.previous_week_4_load_list))
    #         started = True
    #     if len(self.previous_week_3_load_list) > 0 or started:
    #         sessions_per_week.append(len(self.previous_week_3_load_list))
    #         started = True
    #     if len(self.previous_week_2_load_list) > 0 or started:
    #         sessions_per_week.append(len(self.previous_week_2_load_list))
    #     sessions_per_week.append(len(self.previous_week_1_load_list))
    #
    #     self.average_sessions_per_week = StandardErrorRange(lower_bound=min(sessions_per_week), observed_value=mean(sessions_per_week), upper_bound=max(sessions_per_week))
    @staticmethod
    def aggregate_detailed_training_load(self, load_list):

        detailed_load = DetailedTrainingLoad()

        for c in load_list:
            detailed_load.add(c.session_detailed_load)

        detailed_load.rank_adaptation_types()

        return detailed_load

    @staticmethod
    def get_load_values_for_load_type(load_type, load_list):

        load_values = []

        if load_type == LoadType.rpe:
            load_values = [l.rpe_load for l in load_list]
        elif load_type == LoadType.power:
            load_values = [l.power_load for l in load_list]

        return load_values

    @staticmethod
    def get_ramp(load_type, current_week_load_list, previous_week_load_list):

        current_week_load_values = TrainingLoadCalculator.get_load_values_for_load_type(load_type, current_week_load_list)
        previous_week_load_values = TrainingLoadCalculator.get_load_values_for_load_type(load_type,
                                                                                         previous_week_load_list)

        current_week_sum = StandardErrorRange.get_sum_from_error_range_list(current_week_load_values)
        previous_week_load_sum = StandardErrorRange.get_sum_from_error_range_list(previous_week_load_values)

        current_week_sum.divide_range(previous_week_load_sum)

        return current_week_sum

    @staticmethod
    def get_acwr(load_type, acute_week_load_list, chronic_week_load_list):

        acute_week_load_values = TrainingLoadCalculator.get_load_values_for_load_type(load_type,
                                                                                        acute_week_load_list)
        acute_week_sum = StandardErrorRange.get_sum_from_error_range_list(acute_week_load_values)

        chronic_week_load_values = []
        for c in chronic_week_load_list:
            week_load_values = TrainingLoadCalculator.get_load_values_for_load_type(load_type, c)
            week_load_sum = StandardErrorRange.get_sum_from_error_range_list(week_load_values)
            chronic_week_load_values.append(week_load_sum)

        chronic_week_average = StandardErrorRange.get_average_from_error_range_list(chronic_week_load_values)

        acute_week_sum.divide_range(chronic_week_average)

        return acute_week_sum

    @staticmethod
    def get_freshness(load_type, acute_week_load_list, chronic_week_load_list):

        acute_week_load_values = TrainingLoadCalculator.get_load_values_for_load_type(load_type,
                                                                                        acute_week_load_list)
        acute_week_sum = StandardErrorRange.get_sum_from_error_range_list(acute_week_load_values)

        chronic_week_load_values = []
        for c in chronic_week_load_list:
            week_load_values = TrainingLoadCalculator.get_load_values_for_load_type(load_type, c)
            week_load_sum = StandardErrorRange.get_sum_from_error_range_list(week_load_values)
            chronic_week_load_values.append(week_load_sum)

        chronic_week_average = StandardErrorRange.get_average_from_error_range_list(chronic_week_load_values)

        chronic_week_average.subtract(acute_week_sum)

        return chronic_week_average

    @staticmethod
    def get_monotony(load_type, weekly_load_list):

        # ideal less than 1.5, bad over 2.0
        weekly_load_values = TrainingLoadCalculator.get_load_values_for_load_type(load_type, weekly_load_list)

        average = StandardErrorRange.get_average_from_error_range_list(weekly_load_values)
        std_dev = StandardErrorRange.get_stddev_from_error_range_list(weekly_load_values)

        average.divide_range(std_dev)

        return average

    @staticmethod
    def get_strain(load_type, weekly_load_list):

        weekly_load_values = TrainingLoadCalculator.get_load_values_for_load_type(load_type, weekly_load_list)

        weekly_load = StandardErrorRange.get_sum_from_error_range_list(weekly_load_values)

        monotony = TrainingLoadCalculator().get_monotony(load_type, weekly_load_list)

        weekly_load.multiply_range(monotony)

        return weekly_load

    @staticmethod
    def get_strain_spike(load_type, list_of_load_value_lists):

        strain_list = []

        for load_value_list in list_of_load_value_lists:
            # don't want an event with strain > 1.2
            strain = TrainingLoadCalculator().get_strain(load_type, load_value_list)
            strain_list.append(strain)

        if len(strain_list) == 0:
            last_week_strain = None
        else:
            last_week_strain = strain_list[0]
            strain_average = StandardErrorRange.get_average_from_error_range_list(strain_list)
            strain_stddev = StandardErrorRange.get_stddev_from_error_range_list(strain_list)

            last_week_strain.subtract(strain_average)
            last_week_strain.divide_range(strain_stddev)

        return last_week_strain








