from models.training_volume import StandardErrorRange


class TrainingLoadCalculator(object):

    def __init__(self, current_week_load_values: [StandardErrorRange],
                 previous_week_1_load_values: [StandardErrorRange],
                 previous_week_2_load_values: [StandardErrorRange],
                 previous_week_3_load_values: [StandardErrorRange],
                 previous_week_4_load_values: [StandardErrorRange]):

        self.current_week_load_values = current_week_load_values
        self.previous_week_1_load_values = previous_week_1_load_values
        self.previous_week_2_load_values = previous_week_2_load_values
        self.previous_week_3_load_values = previous_week_3_load_values
        self.previous_week_4_load_values = previous_week_4_load_values

        self.current_week_sum = None
        self.previous_week_1_sum = None
        self.previous_week_2_sum = None
        self.previous_week_3_sum = None
        self.previous_week_4_sum = None
        self.chronic_average = None

        self.sum_weeks()
        self.calculate_averages()

    def sum_weeks(self):

        self.current_week_sum = StandardErrorRange.get_sum_from_error_range_list(self.current_week_load_values)
        self.previous_week_1_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_1_load_values)
        self.previous_week_2_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_2_load_values)
        self.previous_week_3_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_3_load_values)
        self.previous_week_4_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_4_load_values)

    def calculate_averages(self):

        chronic_weeks = [self.previous_week_1_sum,
                         self.previous_week_2_sum,
                         self.previous_week_3_sum,
                         self.previous_week_4_sum]

        self.chronic_average = StandardErrorRange.get_average_from_error_range_list(chronic_weeks)

    def get_ramp(self):

        current_week_total_load = self.current_week_sum.plagiarize()

        current_week_total_load.divide_range(self.previous_week_1_sum)

        return current_week_total_load

    def get_acwr(self):

        current_week_sum = self.current_week_sum.plagiarize()

        current_week_sum.divide_range(self.chronic_average)

        return current_week_sum

    def get_freshness(self):

        current_week_sum = self.current_week_sum.plagiarize()

        current_week_sum.subtract(self.previous_week_1_sum)

        return current_week_sum

    def get_monotony(self, weekly_load_values):

        # ideal less than 1.5, bad over 2.0

        average = StandardErrorRange.get_average_from_error_range_list(weekly_load_values)
        std_dev = StandardErrorRange.get_stddev_from_error_range_list(weekly_load_values)

        average.divide_range(std_dev)

        return average

    def get_strain(self, weekly_load_values):

        weekly_load = StandardErrorRange.get_sum_from_error_range_list(weekly_load_values)

        monotony = self.get_monotony(weekly_load_values)

        weekly_load.multiply_range(monotony)

        return weekly_load

    def get_strain_spike(self):

        # don't want an event with strain > 1.2
        current_week_strain = self.get_strain(self.current_week_load_values)
        previous_week_1_strain = self.get_strain(self.previous_week_1_load_values)
        previous_week_2_strain = self.get_strain(self.previous_week_2_load_values)
        previous_week_3_strain = self.get_strain(self.previous_week_3_load_values)
        previous_week_4_strain = self.get_strain(self.previous_week_4_load_values)

        strain_list = [
            current_week_strain,
            previous_week_1_strain,
            previous_week_2_strain,
            previous_week_3_strain,
            previous_week_4_strain
        ]

        strain_average = StandardErrorRange.get_average_from_error_range_list(strain_list)
        strain_stddev = StandardErrorRange.get_stddev_from_error_range_list(strain_list)

        current_week_strain.subtract(strain_average)
        current_week_strain.divide_range(strain_stddev)

        return current_week_strain








