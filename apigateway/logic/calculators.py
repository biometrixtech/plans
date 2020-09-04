import math
from models.training_volume import StandardErrorRange, Assignment
from models.movement_tags import Gender


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
            vo2_max_range.lower_bound = min(vo2_max_range_lower.lowest_value(), vo2_max_range_upper.lowest_value())
            vo2_max_range.upper_bound = min(vo2_max_range_lower.highest_value(), vo2_max_range_upper.highest_value())
            vo2_max_range.observed_value = (vo2_max_range.lowest_value() + vo2_max_range.highest_value()) / 2
        else:
            vo2_max_range = StandardErrorRange()

        return vo2_max_range

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
    def vo2max_population(cls, age, female, activity_level=2):
        """
        based on: https://www8.garmin.com/manuals/webhelp/edge520/EN-US/GUID-1FBCCD9E-19E1-4E4C-BD60-1793B5B97EB3.html
        :param age:
        :param activity_level: 1-7 scale based on duration and intensity of activity per week same as nhanes, needs to be  converted to
        :param female:
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
        if female:
            vo2_max_age_dict = population_fpt.get('female').get(athletic_level)  # use fair as default
        else:
            vo2_max_age_dict = population_fpt.get('male').get(athletic_level)  # use fair as default
        vo2_max = max([value for key, value in vo2_max_age_dict.items() if age < key])
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

        :param time: minutes
        :param distance: meters
        :return:
        """
        velocity = distance / time
        percent_max = 0.8 + 0.1894393 * math.exp(-0.012778 * time) + 0.2989558 * math.exp(-0.1932605 * time)
        vo2 = -4.60 + 0.182258 * velocity + 0.000104 * (velocity ** 2)
        vo2_max = round(vo2 / percent_max, 1)
        return vo2, vo2_max

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

        min_speed = (work_vo2 - 3.5) / (0.17 + grade * 0.79)
        speed = min_speed / float(60)

        return speed

    @classmethod
    def speed_from_watts_running(cls, watts, user_weight, grade, efficiency=.21):

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
    def power_resistance_exercise(cls, weight_used, user_weight, distance_moved=None, time_eccentric=None, time_concentric=None):
        """

        :param weight_used: kg, weight of equipment used
        :param user_weight: kg
        :param distance_moved: m, expected distance moved in each concentric and eccentric direction, default of .5m is used (about halfway between squat and bench press)
        :param time_eccentric: s, time taken for eccentric movement, default of 1.5s
        :param time_concentric: s, time taken for concentric movement, default of 1.5s
        :return:
        """
        if isinstance(weight_used, Assignment):
            total_weight = weight_used.plagiarize()
            total_weight.add_value(user_weight)
        else:
            total_weight = weight_used + user_weight
        distance_moved = distance_moved or .5
        time_concentric = time_concentric or 1.5
        time_eccentric = time_eccentric or 1.5
        accel_concentric = cls.get_accel(distance_moved, time_concentric)
        accel_eccentric = cls.get_accel(distance_moved, time_eccentric)
        force_concentric = cls.get_force(total_weight, accel_concentric)
        force_eccentric = cls.get_force(total_weight, -accel_eccentric)
        velocity_concentric = distance_moved / time_concentric
        velocity_eccentric = distance_moved / time_eccentric
        power_concentric = force_concentric.plagiarize()
        power_eccentric = force_eccentric.plagiarize()
        power_concentric.multiply(velocity_concentric)
        power_eccentric.multiply(velocity_eccentric)
        power_concentric.multiply(time_concentric)
        power_eccentric.multiply(time_eccentric)
        average_power = power_concentric.plagiarize()
        average_power.add(power_eccentric)
        average_power.divide(time_concentric + time_eccentric)
        # average_power = round((power_concentric * time_concentric + power_eccentric * time_eccentric) / (time_concentric + time_eccentric), 1)
        return average_power

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
        power = cls.mets_to_watts(mets, user_weight, efficiency=.21)
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
        if vo2_max is not None:
            work_vo2_list = [
                (vo2_max_range.lower_bound / 100) * vo2_max.lower_bound,
                (vo2_max_range.upper_bound / 100) * vo2_max.lower_bound,
                (vo2_max_range.lower_bound / 100) * vo2_max.upper_bound,
                (vo2_max_range.upper_bound / 100) * vo2_max.upper_bound]

            work_vo2_lower_bound = min(work_vo2_list)
            work_vo2_upper_bound = max(work_vo2_list)

            watts_lower = cls.power_running_from_work_vo2(work_vo2_lower_bound, weight, efficiency=.21)
            watts_upper = cls.power_running_from_work_vo2(work_vo2_upper_bound, weight, efficiency=.21)
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
    def get_power_by_speed_resistance_displacement(cls, speed, resistance, displacement, weight):
        """

        :param speed:
        :param resistance:
        :param displacement:
        :return:
        """
        mets = cls.get_mets_by_speed_resistance_displacement(speed, resistance, displacement)
        power = cls.mets_to_watts(mets=mets, weight=weight, efficiency=.21)
        return power

    @classmethod
    def get_mets_by_speed_resistance_displacement(cls, speed, resistance, displacement):
        """

        :param speed:
        :param resistance:
        :param displacement:
        :return:
        """
        if displacement is None or speed is None or resistance is None:
            return 5
        lookup_table = cls.get_mets_lookup_table_displacement(displacement)
        mets_value_speed = lookup_table.get(resistance.name)
        if mets_value_speed is None:
            raise ValueError("Invalid Resistance")
        mets = mets_value_speed.get(speed.name)
        if mets is None:
            raise ValueError("Invalid speed")
        return mets

    @classmethod
    def get_mets_lookup_table_displacement(cls, displacement):
        """

        :param displacement:
        :return:
        """
        if displacement.name in ['partial_rom', 'full_rom']:
            lookup_table = {
                'none': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'low': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'mod': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'high': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'max': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                }
            }
        elif displacement.name == 'min':
            lookup_table = {
                'none': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'low': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'mod': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'high': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'max': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                }
            }
        elif displacement.name == 'mod':
            lookup_table = {
                'none': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'low': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'mod': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'high': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'max': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                }
            }
        elif displacement.name == 'max':
            lookup_table = {
                'none': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'low': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'mod': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'high': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'max': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                }
            }
        else:
            raise ValueError('Invalid displacement')
        return lookup_table

    @classmethod
    def get_rpe_by_speed_resistance_displacement(cls, speed, resistance, displacement):
        """

        :param speed:
        :param resistance:
        :param displacement:
        :return:
        """
        if speed is None or resistance is None or displacement is None:
            return 3
        lookup_table = cls.get_rpe_lookup_table_displacement(displacement)
        rpe_values_speed = lookup_table.get(resistance.name)
        if rpe_values_speed is None:
            raise ValueError("Invalid Resistance")
        rpe = rpe_values_speed.get(speed.name)
        if rpe is None:
            raise ValueError("Invalid speed")
        return rpe

    @classmethod
    def get_rpe_lookup_table_displacement(cls, displacement):
        """

        :param displacement:
        :return:
        """
        if displacement.name in ['partial_rom', 'full_rom']:
            lookup_table = {
                'none': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'low': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'mod': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'high': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'max': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                }
            }
        elif displacement.name == 'min':
            lookup_table = {
                'none': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'low': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'mod': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'high': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'max': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                }
            }
        elif displacement.name == 'mod':
            lookup_table = {
                'none': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'low': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'mod': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'high': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'max': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                }
            }
        elif displacement.name == 'max':
            lookup_table = {
                'none': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'low': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'mod': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'high': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                },
                'max': {
                    'none': 0, 'slow': 1, 'mod': 2, 'fast': 3, 'explosive': 4
                }
            }
        else:
            raise ValueError('Invalid displacement')
        return lookup_table
