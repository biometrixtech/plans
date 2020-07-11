from models.training_volume import StandardErrorRange
from models.training_load import LoadType, DetailedTrainingLoad, TrainingLoad
from statistics import mean


class TrainingLoadCalculator(object):

    def __init__(self,
                 current_week_load_list: [StandardErrorRange],
                 previous_week_1_load_list: [StandardErrorRange],
                 previous_week_2_load_list: [StandardErrorRange],
                 previous_week_3_load_list: [StandardErrorRange],
                 previous_week_4_load_list: [StandardErrorRange]):

        self.current_week_load_list = current_week_load_list
        self.previous_week_1_load_list = previous_week_1_load_list
        self.previous_week_2_load_list = previous_week_2_load_list
        self.previous_week_3_load_list = previous_week_3_load_list
        self.previous_week_4_load_list = previous_week_4_load_list

        self.current_week_rpe_load_values = []
        self.previous_week_1_rpe_load_values = []
        self.previous_week_2_rpe_load_values = []
        self.previous_week_3_rpe_load_values = []
        self.previous_week_4_rpe_load_values = []

        self.current_week_power_load_values = []
        self.previous_week_1_power_load_values = []
        self.previous_week_2_power_load_values = []
        self.previous_week_3_power_load_values = []
        self.previous_week_4_power_load_values = []

        self.current_week_rpe_values = []
        self.previous_week_1_rpe_values = []
        self.previous_week_2_rpe_values = []
        self.previous_week_3_rpe_values = []
        self.previous_week_4_rpe_values = []

        self.current_week_rpe_load_sum = None
        self.previous_week_1_rpe_load_sum = None
        self.previous_week_2_rpe_load_sum = None
        self.previous_week_3_rpe_load_sum = None
        self.previous_week_4_rpe_load_sum = None
        self.chronic_rpe_load_average = None

        self.current_week_power_load_sum = None
        self.previous_week_1_power_load_sum = None
        self.previous_week_2_power_load_sum = None
        self.previous_week_3_power_load_sum = None
        self.previous_week_4_power_load_sum = None
        self.chronic_power_load_average = None

        self.average_session_load = TrainingLoad()
        self.average_session_rpe = None
        self.average_sessions_per_week = None

        self.current_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_1_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_2_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_3_weeks_detailed_load = DetailedTrainingLoad()
        self.previous_4_weeks_detailed_load = DetailedTrainingLoad()

        self.populate_values()
        self.sum_weeks()
        self.calculate_averages()

        self.calculate_weekly_detailed_training_load()

    def populate_values(self):

        self.current_week_rpe_load_values = [l.rpe_load for l in self.current_week_load_list]
        self.previous_week_1_rpe_load_values = [l.rpe_load for l in self.previous_week_1_load_list]
        self.previous_week_2_rpe_load_values = [l.rpe_load for l in self.previous_week_2_load_list]
        self.previous_week_3_rpe_load_values = [l.rpe_load for l in self.previous_week_3_load_list]
        self.previous_week_4_rpe_load_values = [l.rpe_load for l in self.previous_week_4_load_list]

        self.current_week_power_load_values = [l.power_load for l in self.current_week_load_list]
        self.previous_week_1_power_load_values = [l.power_load for l in self.previous_week_1_load_list]
        self.previous_week_2_power_load_values = [l.power_load for l in self.previous_week_2_load_list]
        self.previous_week_3_power_load_values = [l.power_load for l in self.previous_week_3_load_list]
        self.previous_week_4_power_load_values = [l.power_load for l in self.previous_week_4_load_list]

        self.current_week_rpe_values = [l.session_rpe for l in self.current_week_load_list]
        self.previous_week_1_rpe_values = [l.session_rpe for l in self.previous_week_1_load_list]
        self.previous_week_2_rpe_values = [l.session_rpe for l in self.previous_week_2_load_list]
        self.previous_week_3_rpe_values = [l.session_rpe for l in self.previous_week_3_load_list]
        self.previous_week_4_rpe_values = [l.session_rpe for l in self.previous_week_4_load_list]

    def sum_weeks(self):

        self.current_week_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.current_week_rpe_load_values)
        self.previous_week_1_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_1_rpe_load_values)
        self.previous_week_2_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_2_rpe_load_values)
        self.previous_week_3_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_3_rpe_load_values)
        self.previous_week_4_rpe_load_sum = StandardErrorRange.get_sum_from_error_range_list(self.previous_week_4_rpe_load_values)

        self.current_week_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
            self.current_week_power_load_values)
        self.previous_week_1_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
            self.previous_week_1_power_load_values)
        self.previous_week_2_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
            self.previous_week_2_power_load_values)
        self.previous_week_3_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
            self.previous_week_3_power_load_values)
        self.previous_week_4_power_load_sum = StandardErrorRange.get_sum_from_error_range_list(
            self.previous_week_4_power_load_values)

    def calculate_averages(self):

        rpe_chronic_weeks = [self.previous_week_1_rpe_load_sum,
                             self.previous_week_2_rpe_load_sum,
                             self.previous_week_3_rpe_load_sum,
                             self.previous_week_4_rpe_load_sum]

        power_chronic_weeks = [self.previous_week_1_power_load_sum,
                               self.previous_week_2_power_load_sum,
                               self.previous_week_3_power_load_sum,
                               self.previous_week_4_power_load_sum]

        self.chronic_rpe_load_average = StandardErrorRange.get_average_from_error_range_list(rpe_chronic_weeks)
        self.chronic_power_load_average = StandardErrorRange.get_average_from_error_range_list(power_chronic_weeks)

        last_two_weeks_sessions = self.current_week_power_load_values
        last_two_weeks_sessions.extend(self.previous_week_1_power_load_values)
        if len(self.current_week_power_load_values) <= 1:
            last_two_weeks_sessions.extend(self.previous_week_2_power_load_values)

        self.average_session_load = StandardErrorRange.get_average_from_error_range_list(last_two_weeks_sessions)

        last_two_weeks_rpes = self.current_week_rpe_values
        last_two_weeks_rpes.extend(self.previous_week_1_rpe_values)
        if len(self.current_week_rpe_values) <= 1:
            last_two_weeks_rpes.extend(self.previous_week_2_rpe_values)

        self.average_session_rpe = StandardErrorRange.get_average_from_error_range_list(last_two_weeks_rpes)

        sessions_per_week = []
        started = False
        if len(self.previous_week_4_load_list) > 0:
            sessions_per_week.append(len(self.previous_week_4_load_list))
            started = True
        if len(self.previous_week_3_load_list) > 0 or started:
            sessions_per_week.append(len(self.previous_week_3_load_list))
            started = True
        if len(self.previous_week_2_load_list) > 0 or started:
            sessions_per_week.append(len(self.previous_week_2_load_list))
        sessions_per_week.append(len(self.previous_week_1_load_list))

        self.average_sessions_per_week = mean(sessions_per_week)

    def calculate_weekly_detailed_training_load(self):

        for c in self.current_week_load_list:
            self.current_weeks_detailed_load.add(c.session_detailed_load)

        for c in self.previous_week_1_load_list:
            self.previous_1_weeks_detailed_load.add(c.session_detailed_load)

        for c in self.previous_week_2_load_list:
            self.previous_2_weeks_detailed_load.add(c.session_detailed_load)

        for c in self.previous_week_3_load_list:
            self.previous_3_weeks_detailed_load.add(c.session_detailed_load)

        for c in self.previous_week_4_load_list:
            self.previous_4_weeks_detailed_load.add(c.session_detailed_load)

        self.current_weeks_detailed_load.rank_adaptation_types()
        self.previous_1_weeks_detailed_load.rank_adaptation_types()
        self.previous_2_weeks_detailed_load.rank_adaptation_types()
        self.previous_3_weeks_detailed_load.rank_adaptation_types()
        self.previous_4_weeks_detailed_load.rank_adaptation_types()

    def get_ramp(self, load_type):

        if load_type == LoadType.power:
            current_week_total_load = self.current_week_power_load_sum.plagiarize()
            current_week_total_load.divide_range(self.previous_week_1_power_load_sum)
        else:
            current_week_total_load = self.current_week_rpe_load_sum.plagiarize()
            current_week_total_load.divide_range(self.previous_week_1_rpe_load_sum)

        return current_week_total_load

    def get_acwr(self, load_type):

        if load_type == LoadType.power:
            current_week_sum = self.current_week_power_load_sum.plagiarize()
            current_week_sum.divide_range(self.chronic_power_load_average)
        else:
            current_week_sum = self.current_week_rpe_load_sum.plagiarize()
            current_week_sum.divide_range(self.chronic_rpe_load_average)

        return current_week_sum

    def get_freshness(self, load_type):

        if load_type == LoadType.power:
            current_week_sum = self.current_week_power_load_sum.plagiarize()
            current_week_sum.subtract(self.previous_week_1_power_load_sum)
        else:
            current_week_sum = self.current_week_rpe_load_sum.plagiarize()
            current_week_sum.subtract(self.previous_week_1_rpe_load_sum)

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

    def get_strain_spike(self, load_type):

        if load_type == LoadType.power:
            # don't want an event with strain > 1.2
            current_week_strain = self.get_strain(self.current_week_power_load_values)
            previous_week_1_strain = self.get_strain(self.previous_week_1_power_load_values)
            previous_week_2_strain = self.get_strain(self.previous_week_2_power_load_values)
            previous_week_3_strain = self.get_strain(self.previous_week_3_power_load_values)
            previous_week_4_strain = self.get_strain(self.previous_week_4_power_load_values)
        else:
            current_week_strain = self.get_strain(self.current_week_rpe_load_values)
            previous_week_1_strain = self.get_strain(self.previous_week_1_rpe_load_values)
            previous_week_2_strain = self.get_strain(self.previous_week_2_rpe_load_values)
            previous_week_3_strain = self.get_strain(self.previous_week_3_rpe_load_values)
            previous_week_4_strain = self.get_strain(self.previous_week_4_rpe_load_values)

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








