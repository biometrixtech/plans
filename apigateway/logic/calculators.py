import math
from models.training_volume import StandardErrorRange, Assignment
from models.movement_tags import Gender, RunningDistances
from time import gmtime


cardio_mets_table = {
    "run": 8.0,
    "sprint": 23.0,
    "row": 7.0,
    "cycle": 7.0,
    "ski_erg": 6.8,
    "swim": 7.0,
    "ruck": 5.0,
    "stairmaster": 9.0,
    "pilates": 3.0,
    "airdyne": 4.3,
    "yoga": 3.0,
    "power_yoga": 4.0,
    "elliptical": 5.0,
    "rope_skipping": 12.3,
    "bicycling_stationary": 7.0,
    "race_walking": 6.5
}


class Calculators(object):

    @classmethod
    def get_running_distance_from_type(cls, distance_type):

        if distance_type == RunningDistances.m100:
            return 100.00
        elif distance_type == RunningDistances.m200:
            return 200.00
        elif distance_type == RunningDistances.m300:
            return 300.00
        elif distance_type == RunningDistances.m400:
            return 400.00
        elif distance_type == RunningDistances.m500:
            return 500.00
        elif distance_type == RunningDistances.m600:
            return 600.00
        elif distance_type == RunningDistances.m800:
            return 800.00
        elif distance_type == RunningDistances.m1000:
            return 1000.00
        elif distance_type == RunningDistances.m1200:
            return 1200.00
        elif distance_type == RunningDistances.m1600:
            return 1600.00
        elif distance_type == RunningDistances.m4000:
            return 4000.00
        elif distance_type == RunningDistances.mile3:
            return 4828.03
        elif distance_type == RunningDistances.k5:
            return 5000.00
        elif distance_type == RunningDistances.mile5:
            return 8046.72
        elif distance_type == RunningDistances.k10:
            return 10000.00
        elif distance_type == RunningDistances.k12:
            return 12000.00
        elif distance_type == RunningDistances.marathon_half:
            return 20921.50
        elif distance_type == RunningDistances.mile15:
            return 24140.20
        elif distance_type == RunningDistances.k25:
            return 25000.00
        elif distance_type == RunningDistances.marathon:
            return 42197.00
        elif distance_type == RunningDistances.k50:
            return 50000.00
        elif distance_type == RunningDistances.mile50:
            return 80467.2
        else:
            return 0

    @classmethod
    def get_running_speed_for_running_pace_distance(cls, running_pace_distance):
        current_race_times = cls.get_mcmillan_race_time_tuples()

        for c in range(0, len(current_race_times)):
            if current_race_times[c][0] == running_pace_distance:
                target_meters_second = current_race_times[c][0] / current_race_times[c][1]
                break
            if current_race_times[c][0] < running_pace_distance < current_race_times[c + 1][0]:
                less_distance = current_race_times[c][0]
                less_time = current_race_times[c][1]
                more_distance = current_race_times[c + 1][0]
                more_time = current_race_times[c + 1][1]

                more_distance_diff = more_distance - running_pace_distance
                full_distance_diff = more_distance - less_distance
                diff_ratio = more_distance_diff / full_distance_diff

                less_meters_second = less_distance / less_time
                more_meters_second = more_distance / more_time
                adjusted_meters_second = ((more_meters_second - less_meters_second) * diff_ratio) + less_meters_second
                target_meters_second = adjusted_meters_second
                break

            elif running_pace_distance < current_race_times[c][0]:
                more_distance = current_race_times[c][0]
                more_time = current_race_times[c][1]

                more_meters_second = more_distance / more_time
                target_meters_second = more_meters_second
                break
            elif c == len(current_race_times) - 1:
                more_distance = current_race_times[c][0]
                more_time = current_race_times[c][1]

                more_meters_second = more_distance / more_time
                target_meters_second = more_meters_second

        return target_meters_second

    @classmethod
    def get_running_speed_from_known_time(cls, known_distance, known_time, running_pace_distance):

        baseline_speed = cls.get_running_speed_for_running_pace_distance(known_distance)
        known_speed = known_distance / known_time

        know_baseline_ratio = known_speed / baseline_speed

        running_pace_speed = cls.get_running_speed_for_running_pace_distance(running_pace_distance)

        adjusted_running_speed = running_pace_speed * know_baseline_ratio

        return adjusted_running_speed

    @classmethod
    def vo2_max_estimation_demographics(cls, age, user_weight, user_height=1.7, gender=Gender.female, activity_level=5):
        """

        :param age:
        :param user_weight: kg
        :param user_height: m
        :param gender:
        :param activity_level: 1-7 scale based on duration and intensity of activity per week as defined in nhanes
        :return:
        """
        bmi = user_weight / user_height ** 2
        vo2_max_population = Calculators.vo2max_population(age, gender, activity_level)
        vo2_max_nhanes = Calculators.vo2max_nhanes(age, bmi, gender, activity_level)
        vo2_max_schembre = Calculators.vo2max_schembre(age, user_weight, user_height, gender, activity_level)
        vo2_max_matthews = Calculators.vo2max_matthews(age, user_weight, user_height, gender, activity_level)
        vo2_max = StandardErrorRange()
        all_values = [vo2_max_population, vo2_max_nhanes, vo2_max_schembre, vo2_max_matthews]
        vo2_max.lower_bound = min(all_values)
        vo2_max.upper_bound = max(all_values)
        vo2_max.observed_value = round(sum(all_values) / len(all_values), 1)

        return vo2_max

    @classmethod
    def rpe_from_percent_vo2_max(cls, percent_vo2max):
        """

        :param percent_vo2max:
        :return:
        """
        if percent_vo2max >= 100:
            return 10.0
        rpe_lookup_tuples = cls.get_acsm_rpe_vo2_max_lookup()

        rpe_tuple = [r for r in rpe_lookup_tuples if r[1] <= percent_vo2max <= r[2]]

        if len(rpe_tuple) > 0:

            perc_diff = percent_vo2max - rpe_tuple[0][1]
            rpe_diff = perc_diff / float(rpe_tuple[0][2] - rpe_tuple[0][1])
            rpe = rpe_tuple[0][0] + rpe_diff

            rpe = min(10.0, rpe)
            rpe = max(1.0, rpe)

        else:
            rpe = 1.0

        return round(rpe, 1)

    @classmethod
    def percent_vo2_max_from_rpe_range(cls, rpe):

        """

        :param rpe:
        :return: StandardErrorRange
        """
        if rpe.lowest_value() >= 10:
            return StandardErrorRange(lower_bound=100, observed_value=100, upper_bound=100)
        rpe_lookup_tuples = cls.get_acsm_rpe_vo2_max_lookup()

        rpe_tuple_lower = [r for r in rpe_lookup_tuples if r[0] <= rpe.lowest_value()]
        rpe_tuple_upper = [r for r in rpe_lookup_tuples if r[0] <= rpe.highest_value()]

        if len(rpe_tuple_lower) > 0:
            sorted_tuple = sorted(rpe_tuple_lower, key=lambda x:[0], reverse=True)
            vo2_max_range_lower = StandardErrorRange(lower_bound=sorted_tuple[0][1], upper_bound= sorted_tuple[0][2])
        else:
            vo2_max_range_lower = None

        if len(rpe_tuple_upper) > 0:
            sorted_tuple = sorted(rpe_tuple_upper, key=lambda x:[0], reverse=True)
            vo2_max_range_upper = StandardErrorRange(lower_bound=sorted_tuple[0][1], upper_bound= sorted_tuple[0][2])
        else:
            vo2_max_range_upper = None

        if vo2_max_range_lower is None and vo2_max_range_upper is not None:
            vo2_max_range = vo2_max_range_upper
        elif vo2_max_range_upper is None and vo2_max_range_lower is not None:
            vo2_max_range = vo2_max_range_lower
        elif vo2_max_range_upper is not None and vo2_max_range_lower is not None:
            vo2_max_range = StandardErrorRange()
            vo2_max_range.lower_bound = max(vo2_max_range_lower.lowest_value(), vo2_max_range_upper.lowest_value())
            vo2_max_range.upper_bound = max(vo2_max_range_lower.highest_value(), vo2_max_range_upper.highest_value())
            vo2_max_range.observed_value = (vo2_max_range.lowest_value() + vo2_max_range.highest_value()) / 2
        else:
            vo2_max_range = StandardErrorRange()

        return vo2_max_range

    @classmethod
    def get_mcmillan_race_time_tuples(cls):
        race_times = list()
        race_times.append((100, 29.30))
        race_times.append((200, 58.70))
        race_times.append((400, 2 * 60 + 2.70))
        race_times.append((500, 2 * 60 + 40.00))
        race_times.append((600, 3 * 60 + 16.50))
        race_times.append((800, 4 * 60 + 29.30))
        race_times.append((1000, 5 * 60 + 54.10))
        race_times.append((1500, 9 * 60 + 14.70))
        race_times.append((1600, 9 * 60 + 56.10))
        race_times.append((1609.34, 60 * 10)) # 1 mile
        race_times.append((2000, 12 * 60 + 41.90))
        race_times.append((2414.01, 15 * 60 + 37.30)) # 1.5 mile
        race_times.append((3000, 19 * 60 + 45.60))
        race_times.append((3200, 21 * 60 + 6.70))
        race_times.append((3218.68, 21 * 60 + 14.70)) # 2mile
        race_times.append((4000, 27 * 60 + 10.90))
        race_times.append((4828.02, 33 * 60 + 15.00)) # 3 mile
        race_times.append((5000, 34 * 60 + 43.00))
        race_times.append((6000, 42 * 60 + 0.00))
        race_times.append((6437.36, 45 * 60 + 7.00))
        race_times.append((8000, 57 * 60 + 12.00))
        race_times.append((8046.7, 57 * 60 + 33.00)) # 5 mile
        race_times.append((10000, 72 * 60 + 5.00))
        race_times.append((12000, 87 * 60 + 39.00))
        race_times.append((15000, 91 * 60 + 41.00))
        race_times.append((16093.4, 120 * 60 + 29.00))
        race_times.append((20000, 151 * 60 + 57.00))
        race_times.append((21082.354, 160 * 60 + 43.00)) # half marathon
        race_times.append((24140.1, 185 * 60 + 57.00))  # 15 miles
        race_times.append((25000, 193 * 60 + 4.00))
        race_times.append((30000, 234 * 60 + 48.00))
        race_times.append((1609.34*20, 252 * 60 + 59.00))
        race_times.append((1609.34 * 25, 320 * 60 + 16.00))
        race_times.append((1609.34 * 26.2, 338 * 60 + 13.00))
        race_times.append((50000, 410 * 60 + 17.00))
        race_times.append((1609.34 * 50, 750 * 60 + 24.00))
        race_times.append((100000, 988 * 60 + 40.00))
        race_times.append((1609.34 * 100, 1952 * 60 + 50.00)) # wth!!!
        return race_times

    @classmethod
    def get_acsm_rpe_vo2_max_lookup(cls):
        rpe_lookup_tuples = list()
        rpe_lookup_tuples.append((10, 95, 100))
        rpe_lookup_tuples.append((9, 90, 95))
        rpe_lookup_tuples.append((8, 85, 90))
        rpe_lookup_tuples.append((7, 80, 85))
        rpe_lookup_tuples.append((6, 72.5, 80))
        rpe_lookup_tuples.append((5, 65, 72.5))
        rpe_lookup_tuples.append((4, 60, 65))
        rpe_lookup_tuples.append((3, 55, 60))
        rpe_lookup_tuples.append((2, 50, 55))
        rpe_lookup_tuples.append((1, 0, 50))
        return rpe_lookup_tuples

    @classmethod
    def get_percent_max_hr_from_rpe(cls, rpe):
        """
        Using the table from ACSM

        :param rpe:
        :return:
        """
        percent_max_hr_lookup = list()
        percent_max_hr_lookup.append(((0, 1), (35, 35)))
        percent_max_hr_lookup.append(((1, 2), (35, 55)))
        percent_max_hr_lookup.append(((2, 3), (55, 70)))
        percent_max_hr_lookup.append(((3, 6), (70, 90)))
        percent_max_hr_lookup.append(((6, 9), (90, 100)))
        percent_max_hr_lookup.append(((9, 10), (100, 100)))

        rpe_tuple = [r for r in percent_max_hr_lookup if r[0][0] <= rpe <= r[0][1]]
        if len(rpe_tuple) > 0:
            rpe_range = rpe_tuple[0][0]
            perc_max_hr_range = rpe_tuple[0][1]
            rpe_diff = rpe - rpe_range[0]
            rpe_range_min_max_diff = float(rpe_range[1] - rpe_range[0])
            perc_range = float(perc_max_hr_range[1] - perc_max_hr_range[0])
            perc_diff = 0
            if rpe_range_min_max_diff > 0:
                perc_diff = round(rpe_diff / rpe_range_min_max_diff * perc_range, 2)

            perc = perc_max_hr_range[0] + perc_diff
            perc = min(100, perc)
            perc = max(35, perc)

        else:
            perc = 35
        return perc / 100

    @classmethod
    def vo2max_schembre(cls, age, weight, height, gender=Gender.female, activity_level=5):
        """

        :param age:
        :param weight: kg
        :param height: meters
        :param gender:  Gender enum
        :param activity_level
        :return:
        """
        athletic_level_dict = {
            0: {'walking': 0, 'moderate': 0, 'vigorous': 0},
            1: {'walking': 30, 'moderate': 0, 'vigorous': 0},
            2: {'walking': 0, 'moderate': 30, 'vigorous': 0},
            3: {'walking': 0, 'moderate': 90, 'vigorous': 0},
            4: {'walking': 0, 'moderate': 0, 'vigorous': 20},
            5: {'walking': 0, 'moderate': 0, 'vigorous': 45},
            6: {'walking': 0, 'moderate': 0, 'vigorous': 120},
            7: {'walking': 0, 'moderate': 0, 'vigorous': 180}
        }
        athletic_level = athletic_level_dict.get(activity_level)

        walking = math.sqrt(3.3 * athletic_level.get('walking'))
        moderate = math.sqrt(4.0 * athletic_level.get('moderate'))
        vigorous = math.sqrt(8.0 * athletic_level.get('vigorous'))
        gender = 2 if gender == Gender.female else 1  # male = 1, female = 2
        vo2max = round(68.959 - 8.323 * gender + .213 * age - 0.166 * weight - 5.248 * height - 0.096 * walking + .011 * moderate + 0.158 * vigorous, 1)
        return vo2max

    @classmethod
    def vo2max_matthews(cls, age, weight, height, gender=Gender.female, activity_level=5.0):
        """

        :param age:
        :param height: meters
        :param weight: kg
        :param gender:
        :param activity_level: same as NHANES classification
        :return:
        """
        # gender = 0 if female else 1
        vo2max = round(34.142 + 11.403 * gender.value + .133 * age - .005 * age**2 + 9.17 * height - .254 * weight + 1.463 * activity_level, 1)
        return vo2max

    @classmethod
    def vo2max_nhanes(cls, age, bmi=22.0, gender=Gender.female, activity_level=5.0):
        """

        :param age:
        :param bmi:
        :param activity_level: 1-7 scale based on duration and intensity of activity per week
        :param gender:
        :return:
        """
        # gender = 0 if female else 1
        vo2_max = round(56.363 + 1.921 * activity_level - 0.381 * age - 0.754 * bmi + 10.987 * gender.value, 1)
        return vo2_max

    @classmethod
    def vo2max_population(cls, age, gender, activity_level=2):
        """
        based on: https://www8.garmin.com/manuals/webhelp/edge520/EN-US/GUID-1FBCCD9E-19E1-4E4C-BD60-1793B5B97EB3.html
        :param age:
        :param activity_level: 1-7 scale based on duration and intensity of activity per week same as nhanes, needs to be  converted to
        :param gender:
        :return:
        """

        athletic_level_dict = {
            0: 'untrained',
            1: 'untrained',
            2: 'fair',
            3: 'fair',
            4: 'good',
            5: 'good',
            6: 'excellent',
            7: 'superior'
        }
        athletic_level = athletic_level_dict.get(activity_level)

        population_fpt = {
            'male': {
                'superior':  {30: 55.4, 40: 54.0, 50: 52.5, 60: 48.9, 70: 45.7, 200: 42.1},
                'excellent': {30: 51.1, 40: 48.3, 50: 46.4, 60: 43.4, 70: 39.5, 200: 36.7},
                'good':      {30: 45.4, 40: 44.0, 50: 42.4, 60: 39.2, 70: 35.5, 200: 32.3},
                'fair':      {30: 41.7, 40: 40.5, 50: 38.5, 60: 35.6, 70: 32.3, 200: 29.4},
                'untrained': {30: 37.0, 40: 35.0, 50: 33.0, 60: 30.0, 70: 27.0, 200: 25}
             },
            'female': {
                'superior':  {30: 49.6, 40: 47.4, 50: 45.3, 60: 41.1, 70: 37.8, 200: 36.7},
                'excellent': {30: 43.9, 40: 43.4, 50: 39.7, 60: 36.7, 70: 33.0, 200: 30.9},
                'good':      {30: 39.5, 40: 37.8, 50: 36.3, 60: 33.0, 70: 30.0, 200: 28.1},
                'fair':      {30: 36.1, 40: 34.4, 50: 33.0, 60: 30.1, 70: 27.5, 200: 25.9},
                'untrained': {30: 33.0, 40: 31.0, 50: 29.0, 60: 26.0, 70: 24.0, 200: 22.0}
             }
        }
        if gender.name == 'female':
            vo2_max_age_dict = population_fpt.get('female').get(athletic_level)  # use fair as default
        else:
            vo2_max_age_dict = population_fpt.get('male').get(athletic_level)  # use fair as default
        vo2_max = max([value for key, value in vo2_max_age_dict.items() if age <= key])
        return vo2_max

    @classmethod
    def vo2max_rowing(cls, time_2000m, weight):
        """
        2000m test based

        :param time_2000m: time taken for best 2000m row
        :param weight: in kg
        :return: vo2_max float
        """
        time_500m = time_2000m / 4
        pace = time_500m / 500
        power = 2.8 / (pace ** 3)
        total_volume = power * 14.4 + 65
        vo2_max = round(total_volume / weight, 1)

        return vo2_max

    @classmethod
    def vo2max_rowing_c2(cls, time_2000m, weight, gender=Gender.female, highly_trained=False):
        """
        concept2's formula

        :param time_2000m: time taken for best 2000mrow
        :param weight: in kg
        :param gender: Gender enum
        :param highly_trained: bool
        :return: vo2_max float
        """

        if gender.name == 'female':
            if highly_trained:
                if weight <= 61.36:
                    y = 14.6 - 1.5 * time_2000m
                else:
                    y = 14.9 - 1.5 * time_2000m
            else:
                y = 10.26 - 0.93 * time_2000m
        else:
            if highly_trained:
                if weight <= 75:
                    y = 15.1 - 1.5 * time_2000m
                else:
                    y = 15.7 - 1.5 * time_2000m
            else:
                y = 10.7 - 0.9 * time_2000m
        vo2_max = y * 1000 / weight
        return vo2_max

    @classmethod
    def vo2max_resting_hr(cls, resting_hr, max_hr):
        """

        :param resting_hr: int
        :param max_hr: int
        :return: float
        """
        vo2_max = round(15.3 * max_hr / resting_hr, 1)
        return vo2_max

    @classmethod
    def vo2max_running_jack_daniels(cls, time, distance):
        """

        :param time: seconds
        :param distance: meters
        :return:
        """
        time /= 60 # convert to minutes as we need m/min
        velocity = distance / time
        percent_max = 0.8 + 0.1894393 * math.exp(-0.012778 * time) + 0.2989558 * math.exp(-0.1932605 * time)
        vo2 = -4.60 + 0.182258 * velocity + 0.000104 * (velocity ** 2)
        vo2_max = round(vo2 / percent_max, 1)
        return vo2_max

    @classmethod
    def vo2max_percent_hr_max(cls, percent_hr_max, work_vo2):
        """

        :param percent_hr_max:
        :param work_vo2:
        :return:
        """
        vo2_max = work_vo2 / percent_hr_max
        return vo2_max

    @classmethod
    def percent_vo2_max_from_percent_hr_max(cls, percent_hr_max):
        """

        :param percent_hr_max:
        :return:
        """
        percent_vo2_max = (percent_hr_max - 37) / .64
        return percent_vo2_max

    @classmethod
    def work_vo2_running(cls, speed, grade=0.0):
        """
        greater than 5.0 mph - or 3.0 mph or greater if the subject is jogging)

        :param speed: meters/s
        :param grade: float ( 0-1)
        :return:
        """
        speed *= 60  # convert to m/min
        work_vo2 = 0.2 * speed + 0.9 * speed * grade + 3.5
        return work_vo2

    @classmethod
    def work_vo2_running_alternate(cls, speed, grade=0.0):
        """
        based on this https://www.ajconline.org/article/S0002-9149(17)30873-1/fulltext
        This is a modification of work_vo2_running()

        :param speed: meters/sec
        :param grade: float (0-1)
        :return:
        """
        speed *= 60  # convert to m/min
        work_vo2 = speed * (0.17 + grade * 0.79) + 3.5
        return work_vo2

    @classmethod
    def work_vo2_running_from_power(cls, power, user_weight):
        """

        :param power:
        :param user_weight:
        :return:
        """
        mets = cls.watts_to_mets(power, user_weight, efficiency=.22)
        work_vo2 = round(mets * 3.5, 1)
        return work_vo2

    @classmethod
    def power_running_from_work_vo2(cls, work_vo2, user_weight, efficiency=.22):

        mets = round(work_vo2 / 3.5, 1)
        watts = cls.mets_to_watts(mets, user_weight, efficiency)

        return watts

    @classmethod
    def work_vo2_cycling(cls, power, weight):
        """
        for power outputs of 300–1,200 kgm/min, or 50-200 watts, and speeds of 50–60 rpm
        definition of constants
        1.8 = oxygen cost of producing 1 kgm/min of power output
        7 = oxygen cost of unloaded cycling plus resting oxygen consumption
        :param power: watts
        :param weight: kg
        :return:
        """
        power *= 6  # convert watts to kgm/min
        work_vo2 = 1.8 * power / weight + 7
        return work_vo2

    @classmethod
    def work_vo2_cycling_alternate(cls, power, weight):
        """
        for power outputs of 300–1,200 kgm/min, or 50-200 watts, and speeds of 50–60 rpm
        :param power: watts
        :param weight: kg
        :return:
        """
        work_vo2 = 1.74 * (power * 6.12 / weight) + 3.5
        return work_vo2

    @classmethod
    def work_vo2_rowing_from_power(cls, power, weight):
        """
        TODO: This is way overestimating work_vo2, check/find better solution
        :param power: watts
        :param weight: kg
        :return:
        """
        # work_vo2 = (power * 14.4 + 65) / weight
        # return work_vo2
        # TODO: alternate approach which still seems a litle too high, getting work_vo2 of > 75 using actual OTF data
        mets = cls.watts_to_mets(power, weight, efficiency=.22)
        work_vo2 = round(mets * 3.5, 1)
        return work_vo2

    @classmethod
    def work_vo2_cardio(cls, cardio_type, gender=Gender.female):
        """

        :param cardio_type:
        :param gender:
        :return:
        """
        mets = cls.mets_cardio(cardio_type, gender)
        work_vo2 = mets * 3.5
        return work_vo2

    @classmethod
    def work_vo2_mets(cls, mets):
        """

        :param mets:
        :return:
        """
        work_vo2 = mets * 3.5
        return work_vo2

    @classmethod
    def convert_vo2max_to_ftp(cls, vo2_max, weight):
        """
        ftp is:
        rider weight (kg)
        x VO2Max (ml/kg/min)
        x efficiency (%) (approx 21%)
        x % of VO2Max that can be sustained for ~ 1hr (typically 70-80%) (using 75%)
        x energy contained in 1L of O2 (20.9kj)
        x conversion factor (16.7W/kj)

        :param vo2_max:
        :param weight:
        :return:
        """
        ftp = round(weight * vo2_max * .21 * .75 * 20.9 * 16.7 / 1000, 1)
        return ftp

    @classmethod
    def convert_ftp_to_vo2_max(cls, ftp, weight):
        """
        This is from cycling application which assumes the efficiency and %vo2max sustained for 1 hr
        using ftp =
            rider weight (kg)
            x VO2Max (ml/kg/min)
            x efficiency (%) (approx 21%)
            x % of VO2Max that can be sustained for ~ 1hr (typically 70-80%) (using 75%)
            x energy contained in 1L of O2 (20.9kj)
            x conversion factor (16.7W/kj)

        :param ftp:
        :param weight:
        :return:
        """
        vo2_max = round(ftp / (weight * .21 * .75 * 20.9 * 16.7 / 1000), 1)
        # ftp = round(weight * vo2_max * .21 * .75 * 20.9 * 16.7 / 1000, 1)
        return vo2_max

    @classmethod
    def get_ftp_age_weight(cls, age, weight, gender=Gender.female):
        """
        This seems to be what you should be striving for after proper training.
        :param age:
        :param weight: kg
        :param gender:
        :return:
        """
        ftp = weight * 2.2 * 2
        age_based_adjustment = (1 - .005 * max([0, age - 35]))
        ftp *= age_based_adjustment
        if gender.name == 'female':
            ftp *= .9
        return round(ftp, 1)

    @classmethod
    def ftp_from_population(cls, weight, athletic_level=None, gender=Gender.female):
        """
        from Garmin
        https://www8.garmin.com/manuals/webhelp/edge520/EN-US/GUID-1F58FA8E-09FF-4E51-B9B4-C4B83ED1D6CE.html
        male = {
            'superior': (5.05, None),
            'excellent': (3.93, 5.04),
            'good': (2.79, 3.92),
            'fair': (2.23, 2.78),
            'untrained': (0, 2.23)
         }

        female = {
            'superior': (4.5, None),
            'excellent': (3.33, 4.29),
            'good': (2.36, 3.32),
            'fair': (1.90, 2.35),
            'untrained': (0, 1.90)
         }

        :param weight:
        :param athletic_level:
        :param gender:
        :return:
        """
        population_fpt = {
            'male': {
                'superior': 5.05,
                'excellent':  4.49,
                'good': 3.35,
                'fair': 2.5,
                'untrained': 1.12
             },
            'female': {
                'superior': 4.5,
                'excellent': 3.81,
                'good': 2.84,
                'fair': 2.12,
                'untrained': .95
             }
        }
        if gender.name == 'female':
            ftp_per_kg = population_fpt.get('female').get(athletic_level, 2.12)  # use fair as default
        else:
            ftp_per_kg = population_fpt.get('male').get(athletic_level, 2.5)  # use fair as default

        return ftp_per_kg * weight

    @classmethod
    def mets_to_watts(cls, mets, weight, efficiency=1.0):
        """

        :param mets:
        :param weight: kg
        :param efficiency: float
        :return:
        """
        watts = round((mets * 3.5 * weight * 5.05) / (.01435 * 1000) * efficiency, 2)

        return watts

    @classmethod
    def watts_to_mets(cls, watts, weight, efficiency=1.0):
        """

        :param watts:
        :param weight: kg
        :param efficiency: float
        :return:
        """
        mets = round((watts * 1000 * .01435) / (3.5 * weight * 5.05 * efficiency), 2)
        return mets

    @classmethod
    def power_cycling(cls, speed, user_weight=None, grade=None, wind_speed=None, cycle_weight=None, altitude=None, handlebar_position=None):
        """

        :param speed: m/s
        :param user_weight: kg
        :param grade:
        :param wind_speed: m/s, positive for headwind default 5km/hr
        :param cycle_weight: kg, default to 15kg
        :param altitude: m, average altitude over sea level
        :param handlebar_position: used for drag
        :return:
        """
        user_weight = 60.0 if user_weight is None else user_weight
        grade = .01 if grade is None else grade
        wind_speed = 1.4 if wind_speed is None else wind_speed
        cycle_weight = 15.0 if cycle_weight is None else cycle_weight
        altitude = 0.0 if altitude is None else altitude
        handlebar_position = 'tops' if handlebar_position is None else handlebar_position

        g = 9.805
        rolling_resistance = .005  # .002 to .038 based on tires and surface. .005 is for slick tires in asphalt
        loss = .045  # 1.5% on pulleys 3-5% based on condition of the chain
        drag_values = {'tops': 0.408, 'hoods': 0.324, 'drops': 0.307, 'aerobars': 0.2914}
        drag = drag_values.get(handlebar_position, 'tops')

        force_gravity = g * math.sin(math.atan(grade)) * (user_weight + cycle_weight)
        force_rolling_resistance = g * math.cos(math.atan(grade)) * (user_weight + cycle_weight) * rolling_resistance
        air_density = 1.225 * math.exp(-0.00011856 * altitude)
        force_air_resistance = 0.5 * drag * air_density * (speed + wind_speed) ** 2
        power = (force_gravity + force_rolling_resistance + force_air_resistance) * speed / (1 - loss)
        return power

    @classmethod
    def speed_from_work_vo2_running(cls, work_vo2, grade=0.0):

        min_speed = (work_vo2 - 3.5) / (0.17 + grade * 0.79)  # speed in m/min
        speed = min_speed / float(60) # speed in m/s

        return speed

    @classmethod
    def speed_from_watts_running(cls, watts, user_weight, grade, efficiency=.22):

        if isinstance(grade, Assignment):
            if grade.assigned_value is not None:
                grade = grade.assigned_value
            elif grade.min_value is not None and grade.max_value is not None:
                grade = (grade.min_value + grade.max_value) / 2
            else:
                grade = 0.0
        mets = cls.watts_to_mets(watts, user_weight, efficiency)
        work_vo2 = mets * 3.5
        speed = cls.speed_from_work_vo2_running(work_vo2, grade)

        return speed

    @classmethod
    def speed_from_watts_rowing(cls, watts):

        pace = (2.8 / watts) ** (1/float(3))
        speed = 1 / pace

        return speed

    @classmethod
    def power_running(cls, speed, grade=None, user_weight=None):
        """
        running power based on speed, grade and users weight
        :param speed: m/s
        :param grade: fractional
        :param user_weight: kg
        :return:
        """
        user_weight = 60.0 if user_weight is None else user_weight
        grade = .01 if grade is None else grade
        efficiency = .22
        work_vo2 = cls.work_vo2_running_alternate(speed, grade)
        mets = work_vo2 / 3.5
        power = cls.mets_to_watts(mets, user_weight, efficiency=efficiency)
        return power

    @classmethod
    def power_rowing(cls, speed):
        """

        :param speed: m/s
        :return:
        """
        pace = 1 / speed
        power = 2.8 / (pace ** 3)
        return power

    @classmethod
    def power_resistance_exercise(cls, external_weight, actions, duration_per_rep=None, user_weight=60, user_height=1.65):
        """

        :param external_weight:
        :param actions:
        :param user_weight:
        power is added for simultaneous action and weighted averaged for consecutive ones
        :return:
        """
        if isinstance(external_weight, Assignment):
            external_weight = external_weight.plagiarize()
        else:
            external_weight = Assignment(assigned_value=external_weight)
        if len(actions) > 0:
            average_power = StandardErrorRange()
            total_duration = 0
            for action in actions:
                duration = action.time
                total_duration += duration
                # if action.muscle_action.name != 'no_load':
                # duration = action.time
                action_power = StandardErrorRange()
                if duration > 0:
                    for i in range(len(action.percent_bodyweight)):
                        muscle_action = action.muscle_action[i]
                        if muscle_action.name != 'no_load':
                            total_weight = external_weight.plagiarize()
                            total_weight.add_value(action.percent_bodyweight[i] * user_weight)
                            perc_bodyheight = action.percent_bodyheight[i]
                            if perc_bodyheight == 0 and muscle_action.name == 'isometric':
                                distance = .05  # move 5 cm
                            elif perc_bodyheight < 0:
                                distance = 0
                            else:
                                distance = perc_bodyheight * user_height
                            accel = cls.get_accel(distance, duration)
                            if muscle_action.name == 'eccentric':
                                accel *= -1
                            force = cls.get_force(total_weight, accel)
                            velocity = distance / duration
                            sub_action_power = force.plagiarize()
                            sub_action_power.multiply(velocity)
                            action_power.add(sub_action_power)
                    action_power.multiply(duration)
                    average_power.add(action_power)
            if duration_per_rep is not None:
                average_power.divide(duration_per_rep)
            else:
                average_power.divide(total_duration)
        else:
            total_weight = external_weight.plagiarize()

            distance = .5
            if duration_per_rep is not None:
                duration = duration_per_rep / 2
            else:
                duration = 1.5
            accel = cls.get_accel(distance, duration)
            force = cls.get_force(total_weight, accel)
            velocity = distance / duration
            average_power = force.plagiarize()
            average_power.multiply(velocity)

        return average_power


    # @classmethod
    # def power_resistance_exercise(cls, weight_used, user_weight, distance_moved=None, time_eccentric=None, time_concentric=None):
    #     """

    #     :param weight_used: kg, weight of equipment used
    #     :param user_weight: kg
    #     :param distance_moved: m, expected distance moved in each concentric and eccentric direction, default of .5m is used (about halfway between squat and bench press)
    #     :param time_eccentric: s, time taken for eccentric movement, default of 1.5s
    #     :param time_concentric: s, time taken for concentric movement, default of 1.5s
    #     :return:
    #     """
    #     if isinstance(weight_used, Assignment):
    #         total_weight = weight_used.plagiarize()
    #         total_weight.add_value(user_weight)
    #     else:
    #         total_weight = weight_used + user_weight
    #     distance_moved = distance_moved or .5
    #     time_concentric = time_concentric or 1.5
    #     time_eccentric = time_eccentric or 1.5
    #     accel_concentric = cls.get_accel(distance_moved, time_concentric)
    #     accel_eccentric = cls.get_accel(distance_moved, time_eccentric)
    #     force_concentric = cls.get_force(total_weight, accel_concentric)
    #     force_eccentric = cls.get_force(total_weight, -accel_eccentric)
    #     velocity_concentric = distance_moved / time_concentric
    #     velocity_eccentric = distance_moved / time_eccentric
    #     power_concentric = force_concentric.plagiarize()
    #     power_eccentric = force_eccentric.plagiarize()
    #     power_concentric.multiply(velocity_concentric)
    #     power_eccentric.multiply(velocity_eccentric)
    #     power_concentric.multiply(time_concentric)
    #     power_eccentric.multiply(time_eccentric)
    #     average_power = power_concentric.plagiarize()
    #     average_power.add(power_eccentric)
    #     average_power.divide(time_concentric + time_eccentric)
    #     # average_power = round((power_concentric * time_concentric + power_eccentric * time_eccentric) / (time_concentric + time_eccentric), 1)
    #     return average_power

    @classmethod
    def force_resistance_exercise(cls, weight, distance_moved=None, time_down=None, time_up=None):
        """

        :param weight: kg or Assignment, weight of equipment used
        :param distance_moved: m, expected distance moved in both up and down direction
        :param time_down: s, time taken to move weight down
        :param time_up: s, time taken to move weight up
        :return:
        """
        if distance_moved is not None and time_down is not None and time_up is not None:
            accel_down = cls.get_accel(distance_moved, time_down)
            accel_up = cls.get_accel(distance_moved, time_up)
            force_down = cls.get_force(weight, -accel_down)
            force_up = cls.get_force(weight, accel_up)
            force_up.multiply(time_up)
            force_down.multiply(time_down)
            average_force = force_up.plagiarize()
            average_force.add(force_down)
            average_force.divide(time_down + time_up)
            # average_force = round((force_down + force_up) / (time_down + time_up), 1)
        else:
            average_force = cls.get_force(weight)
        return average_force

    @classmethod
    def power_cardio(cls, cardio_type, user_weight, gender=Gender.female):
        """

        :param cardio_type: string
        :param user_weight: kg
        :param gender: Gender enum
        :return:
        """
        cardio_name = cardio_type.name if cardio_type is not None else None
        # cardio_name = cardio_type.name or None
        mets = cls.mets_cardio(cardio_name, gender)
        power = cls.mets_to_watts(mets, user_weight, efficiency=.22)
        return power

    @classmethod
    def force_running(cls, power, speed=None):
        """

        :param power: watts
        :param speed: m/s, default assumes ~10 min mile pace
        :return:
        """
        if speed is None:
            speed = 2.7
        force = round(power / speed, 2)
        return force

    @classmethod
    def force_rowing(cls, power, speed=None):
        """

        :param power: watts
        :param speed: m/s, default assumes 2:05 split
        :return:
        """
        if speed is None:
            speed = 4.0
        force = round(power / speed, 2)
        return force

    @classmethod
    def force_cycling(cls, power, speed=None):
        """

        :param power: watts
        :param speed: m/s, default is ~12mph
        :return:
        """
        if speed is None:
            speed = 5.4
        force = round(power / speed, 2)
        return force

    @classmethod
    def force_cardio(cls, cardio_type, user_weight=60.0, gender=Gender.female):
        """

        :param cardio_type:
        :param user_weight:
        :param gender:
        :return:
        """
        cardio_name = cardio_type.name if cardio_type is not None else None
        mets = cls.mets_cardio(cardio_name, gender)
        force = round(mets * 3.5 * user_weight * 427 / (200 * 60), 2)
        return force

    @classmethod
    def get_force(cls, weight, accel=0.0):
        """

        :param weight: kg or Assignment with range of possible weights, weight lifted
        :param accel: m/s^2, acceleration +ve is against gravity, -ve is with gravity
        :return: force N
        """
        g = 9.8
        if isinstance(weight, Assignment):
            force = Assignment().multiply_assignment_by_scalar(weight, (g + accel))
            force_range = StandardErrorRange(lower_bound=force.min_value, observed_value=force.assigned_value, upper_bound=force.max_value)
        else:
            force_range = StandardErrorRange(observed_value=round(weight * (g + accel), 1))

        return force_range

    @classmethod
    def get_accel(cls, distance_moved, time_taken):
        """

        :param distance_moved:
        :param time_taken:
        :return:
        """
        accel = 2 * distance_moved / (time_taken ** 2)
        return accel

    @classmethod
    def mets_cardio(cls, cardio_type, gender=Gender.female):
        """

        :param cardio_type:
        :param gender:
        :return:
        """
        mets = cardio_mets_table.get(cardio_type, 5)  # default to 5
        if gender.name == 'female':
            mets -= 1
        return mets

    @classmethod
    def get_power_from_rpe(cls, rpe_range, weight=None, vo2_max=None):
        weight = weight or 60

        vo2_max_range = cls.percent_vo2_max_from_rpe_range(rpe_range)
        # this happens for "none: intensity where rpe=0
        if vo2_max_range.lower_bound is None and vo2_max_range.observed_value is None and vo2_max_range.upper_bound is None:
            return StandardErrorRange()
        if vo2_max is not None:

            vo2_max_list = [vo2_max.lower_bound, vo2_max.observed_value, vo2_max.upper_bound]
            vo2_max_list = [v for v in vo2_max_list if v is not None]
            vo2_max_range_list = [vo2_max_range.lower_bound, vo2_max_range.upper_bound]
            work_vo2_list = [v_max * percent / 100 for v_max in vo2_max_range_list for percent in vo2_max_list]
            # work_vo2_list = [
            #     (vo2_max_range.lower_bound / 100) * vo2_max.lower_bound,
            #     (vo2_max_range.upper_bound / 100) * vo2_max.lower_bound,
            #     (vo2_max_range.lower_bound / 100) * vo2_max.upper_bound,
            #     (vo2_max_range.upper_bound / 100) * vo2_max.upper_bound]

            work_vo2_lower_bound = min(work_vo2_list)
            work_vo2_upper_bound = max(work_vo2_list)

            watts_lower = cls.power_running_from_work_vo2(work_vo2_lower_bound, weight, efficiency=.22)
            watts_upper = cls.power_running_from_work_vo2(work_vo2_upper_bound, weight, efficiency=.22)
            watts_observed = (watts_lower + watts_upper) / 2
            watts_range = StandardErrorRange(lower_bound=watts_lower, observed_value=watts_observed, upper_bound=watts_upper)
        else:
            watts_range = StandardErrorRange()

        return watts_range

    @classmethod
    def get_mets_from_rpe_acsm(cls, rpe, age):
        """
        ACSM based table
        :param rpe:
        :param age:
        :return:
        """
        mets_lookup_tables = cls.mets_lookup_tables()
        if age < 40:
            age_group = 'young'
        elif age < 65:
            age_group = 'middle_aged'
        elif age < 80:
            age_group = 'old'
        else:
            age_group = 'very_old'
        mets_lookup = mets_lookup_tables[age_group]
        rpe_tuple = [r for r in mets_lookup if r[0][0] <= rpe <= r[0][1]]
        if len(rpe_tuple) > 0:
            rpe_range = rpe_tuple[0][0]
            mets_min_max = rpe_tuple[0][1]
            rpe_diff = rpe - rpe_range[0]
            rpe_range_min_max_diff = float(rpe_range[1] - rpe_range[0])
            mets_range = float(mets_min_max[1] - mets_min_max[0])
            mets_diff = 0
            if rpe_range_min_max_diff > 0:
                mets_diff = round(rpe_diff / rpe_range_min_max_diff * mets_range, 2)
            mets = mets_min_max[0] + mets_diff

        else:
            mets = 1
        return mets

    @classmethod
    def mets_lookup_tables(cls):
        all_mets_lookup = {}

        mets_lookup_young = list()
        mets_lookup_young.append(((0, 1), (1.2, 2.4)))
        mets_lookup_young.append(((1, 2), (2.4, 4.7)))
        mets_lookup_young.append(((2, 3), (4.7, 7.1)))
        mets_lookup_young.append(((3, 6), (7.1, 10.1)))
        mets_lookup_young.append(((6, 9), (10.1, 12.0)))
        mets_lookup_young.append(((9, 10), (12.0, 14.0)))
        all_mets_lookup['young'] = mets_lookup_young

        mets_lookup_middle_aged = list()
        mets_lookup_middle_aged.append(((0, 1), (1.0, 2.0)))
        mets_lookup_middle_aged.append(((1, 2), (2.0, 3.9)))
        mets_lookup_middle_aged.append(((2, 3), (3.9, 5.9)))
        mets_lookup_middle_aged.append(((3, 6), (5.9, 8.4)))
        mets_lookup_middle_aged.append(((6, 9), (8.4, 10.0)))
        mets_lookup_middle_aged.append(((9, 10), (10.0, 11.5)))
        all_mets_lookup['middle_aged'] = mets_lookup_middle_aged

        mets_lookup_old = list()
        mets_lookup_old.append(((0, 1), (0.8, 1.6)))
        mets_lookup_old.append(((1, 2), (1.6, 3.1)))
        mets_lookup_old.append(((2, 3), (3.1, 4.7)))
        mets_lookup_old.append(((3, 6), (4.7, 6.7)))
        mets_lookup_old.append(((6, 9), (6.7, 8.0)))
        mets_lookup_old.append(((9, 10), (8.0, 9.0)))
        all_mets_lookup['old'] = mets_lookup_old

        mets_lookup_very_old = list()
        mets_lookup_very_old.append(((0, 1), (0.5, 1.0)))
        mets_lookup_very_old.append(((1, 2), (1.0, 1.9)))
        mets_lookup_very_old.append(((2, 3), (1.9, 2.9)))
        mets_lookup_very_old.append(((3, 6), (2.9, 4.2)))
        mets_lookup_very_old.append(((6, 9), (4.2, 5.0)))
        mets_lookup_very_old.append(((9, 10), (5.0, 5.6)))
        all_mets_lookup['very_old'] = mets_lookup_very_old

        return all_mets_lookup

    @classmethod
    def get_force_level(cls, speed, resistance, displacement):
        # force_level = None
        if displacement is None or displacement.name in ['none', 'partial_rom', 'full_rom'] or resistance.name == 'none':
            force_dict = {
                'none': {'none': 'bit_of_force', 'slow': 'bit_of_force', 'mod': 'no_force', 'fast': 'bit_of_force', 'explosive': 'bit_of_force'},
                'very_low': {'none': 'low_force', 'slow': 'low_force', 'mod': 'no_force', 'fast': 'low_force', 'explosive': 'low_force'},
                'low': {'none': 'low_force', 'slow': 'low_force', 'mod': 'bit_of_force', 'fast': 'mod_force', 'explosive': 'mod_force'},
                'mod': {'none': 'mod_force', 'slow': 'mod_force', 'mod': 'low_force', 'fast': 'high_force', 'explosive': 'high_force'},
                'mod_high': {'none': 'mod_force', 'slow': 'mod_force', 'mod': 'mod_force', 'fast': 'high_force', 'explosive': 'high_force'},
                'high': {'none': 'high_force', 'slow': 'high_force', 'mod': 'high_force', 'fast': 'max_force', 'explosive': 'max_force'},
                'max': {'none': 'max_force', 'slow': 'max_force', 'mod': 'max_force', 'fast': 'max_force', 'explosive': 'max_force'},
            }
            resistance_dict = force_dict.get(resistance.name)
            if resistance_dict is not None:
                force_level = resistance_dict.get(speed.name)
        elif resistance is None or resistance.name == 'very_low':
            force_dict = {
                'min': {'mod': 'bit_of_force', 'fast': 'low_force', 'explosive': 'low_force'},
                'mod': {'mod': 'low_force', 'fast': 'mod_force', 'explosive': 'mod_force'},
                'large': {'mod': 'mod_force', 'fast': 'high_force', 'explosive': 'high_force'},
                'max': {'mod': 'high_force', 'fast': 'max_force', 'explosive': 'max_force'}
            }
            displacement_dict = force_dict.get(displacement.name)
            if displacement_dict is not None:
                force_level = displacement_dict.get(speed.name)
        elif resistance.name == 'low':
            force_dict = {
                'min': {'mod': 'mod_force', 'fast': 'mod_force', 'explosive': 'high_force'},
                'mod': {'mod': 'mod_force', 'fast': 'high_force', 'explosive': 'max_force'},
                'large': {'mod': 'high_force', 'fast': 'high_force', 'explosive': 'max_force'},
                'max': {'mod': 'high_force', 'fast': 'max_force', 'explosive': 'max_force'}
            }
            displacement_dict = force_dict.get(displacement.name)
            if displacement_dict is not None:
                force_level = displacement_dict.get(speed.name)
        else:
            raise ValueError("not found in lookup table")

        return force_level

    @classmethod
    def get_percent_intensity_from_force_level(cls, force_level):
        force_level_dict = {
            "no_force": .5,
            "bit_of_force": .6,
            "low_force": .65,
            "mod_force": .72,
            "high_force": .86,
            "max_force": 1
        }
        return force_level_dict[force_level.name]

    @classmethod
    def get_rpe_from_force_level(cls, force_level, reps=None):
        if force_level.name == 'no_force':
            if reps is None:
                rpe = StandardErrorRange(lower_bound=1, upper_bound=2, observed_value=1.5)
            elif reps <= 20:
                rpe = StandardErrorRange(lower_bound=1, upper_bound=2, observed_value=1.5)
            elif reps <= 30:
                rpe = StandardErrorRange(lower_bound=2, upper_bound=4, observed_value=3)
            elif reps <= 40:
                rpe = StandardErrorRange(lower_bound=3, upper_bound=6, observed_value=4.5)
            elif reps <= 50:
                rpe = StandardErrorRange(lower_bound=5, upper_bound=7, observed_value=6)
            elif reps <= 60:
                rpe = StandardErrorRange(lower_bound=6, upper_bound=8, observed_value=7)
            elif reps <= 70:
                rpe = StandardErrorRange(lower_bound=7, upper_bound=9, observed_value=8)
            else:  # reps > 60
                rpe = StandardErrorRange(lower_bound=9, upper_bound=10, observed_value=9.5)
        elif force_level.name == 'bit_of_force':
            if reps is None:
                rpe = StandardErrorRange(lower_bound=2, upper_bound=3, observed_value=2.5)
            elif reps <= 20:
                rpe = StandardErrorRange(lower_bound=1, upper_bound=3.5, observed_value=2.5)
            elif reps <= 30:
                rpe = StandardErrorRange(lower_bound=3.5, upper_bound=6, observed_value=3)
            elif reps <= 35:
                rpe = StandardErrorRange(lower_bound=6, upper_bound=8, observed_value=5.5)
            elif reps <= 40:
                rpe = StandardErrorRange(lower_bound=8, upper_bound=9, observed_value=8.5)
            else:  # reps > 40
                rpe = StandardErrorRange(lower_bound=9, upper_bound=10, observed_value=9.5)
        elif force_level.name == 'low_force':
            if reps is None:
                rpe = StandardErrorRange(lower_bound=4, upper_bound=5, observed_value=1.5)
            elif reps <= 3:
                rpe = StandardErrorRange(lower_bound=1, upper_bound=3.5, observed_value=2.5)
            elif reps <= 6:
                rpe = StandardErrorRange(lower_bound=2, upper_bound=4.5, observed_value=3)
            elif reps <= 12:
                rpe = StandardErrorRange(lower_bound=3.5, upper_bound=5.5, observed_value=4.5)
            elif reps <= 16:
                rpe = StandardErrorRange(lower_bound=4.5, upper_bound=6.5, observed_value=5.5)
            elif reps <= 20:
                rpe = StandardErrorRange(lower_bound=5.5, upper_bound=7.5, observed_value=6)
            elif reps <= 26:
                rpe = StandardErrorRange(lower_bound=7, upper_bound=9, observed_value=8)
            else:  # reps > 26
                rpe = StandardErrorRange(lower_bound=9, upper_bound=10, observed_value=9.5)
        elif force_level.name == 'mod_force':
            if reps is None:
                rpe = StandardErrorRange(lower_bound=5, upper_bound=6, observed_value=1.5)
            elif reps <= 3:
                rpe = StandardErrorRange(lower_bound=2, upper_bound=5, observed_value=3.5)
            elif reps <= 9:
                rpe = StandardErrorRange(lower_bound=5, upper_bound=7, observed_value=6)
            elif reps <= 12:
                rpe = StandardErrorRange(lower_bound=6.5, upper_bound=7.5, observed_value=7)
            elif reps <= 18:
                rpe = StandardErrorRange(lower_bound=7, upper_bound=9, observed_value=8)
            else:  # reps > 18
                rpe = StandardErrorRange(lower_bound=9, upper_bound=10, observed_value=9.5)
        elif force_level.name == 'high_force':
            if reps is None:
                rpe = StandardErrorRange(lower_bound=7, upper_bound=8, observed_value=7.5)
            elif reps <= 3:
                rpe = StandardErrorRange(lower_bound=6, upper_bound=8, observed_value=7.5)
            elif reps <= 5:
                rpe = StandardErrorRange(lower_bound=7, upper_bound=9, observed_value=8)
            elif reps <= 10:
                rpe = StandardErrorRange(lower_bound=8, upper_bound=9, observed_value=8.5)
            else:  # reps > 10
                rpe = StandardErrorRange(lower_bound=9, upper_bound=10, observed_value=9.5)
        elif force_level.name == 'max_force':
            if reps is None:
                rpe = StandardErrorRange(lower_bound=9, upper_bound=10, observed_value=9.5)
            elif reps <= 3:
                rpe = StandardErrorRange(lower_bound=8, upper_bound=10, observed_value=9)
            else:  # reps > 3
                rpe = StandardErrorRange(lower_bound=9, upper_bound=10, observed_value=9.5)
        else:
            rpe = StandardErrorRange(lower_bound=2, upper_bound=3, observed_value=2.5)

        # # update based on expected reps
        # if reps is not None and adaptation_type is not None:
        #     expected_rep_counts_by_adaptation_type = {
        #         'strength_endurance_strength': (12, 20),
        #         'power_drill': (1, 10),
        #         'maximal_strength_hypertrophic': (1, 12),
        #         'power_explosive_action': (1, 10)
        #     }
        #     expected_reps = expected_rep_counts_by_adaptation_type.get(adaptation_type.name, (0, 100))
        #     if reps < expected_reps[0]:
        #         rpe.subtract_value(1)
        #     elif reps > expected_reps[1]:
        #         rpe.add_value(1)
        #         if rpe.observed_value > 10:
        #             rpe.observed_value = 10
        #         if rpe.upper_bound > 10:
        #             rpe.upper_bound = 10
        return rpe
