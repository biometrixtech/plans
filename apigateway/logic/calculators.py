import math


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
    def vo2max_rowing_c2(cls, time_2000m, weight, female=True, highly_trained=False):
        """
        concept2's formula

        :param time_2000m: time taken for best 2000mrow
        :param weight: in kg
        :param female: bool
        :param highly_trained: bool
        :return: vo2_max float
        """

        if female:
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
    def get_ftp_age_weight(cls, age, weight, female=True):
        """
        This seems to be what you should be striving for after proper training.
        :param age:
        :param weight: kg
        :param female:
        :return:
        """
        ftp = weight * 2.2 * 2
        age_based_adjustment = (1 - .005 * max([0, age - 35]))
        ftp *= age_based_adjustment
        if female:
            ftp *= .9
        return round(ftp, 1)

    @classmethod
    def ftp_from_population(cls, weight, athletic_level=None, female=True):
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
        :param female:
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
        if female:
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
        mets = round((watts * 1000 * .0143) / (3.5 * weight * 5.05 * efficiency), 2)
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
        power = 2.8 / pace ** 3
        return power

    @classmethod
    def power_resistance_exercise(cls, weight_used, user_weight, distance_moved=None, time_down=None, time_up=None):
        """

        :param weight_used: kg, weight of equipment used
        :param distance_moved: m, expected distance moved in both up and down direction
        :param time_down: s, time taken to move weight down
        :param time_up: s, time taken to move weight up
        :param user_weight: kg
        :return:
        """

        return 5

    @classmethod
    def force_resistance_exercise(cls, weight, distance_moved=None, time_down=None, time_up=None):
        """

        :param weight: kg, weight of equipment used
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
            average_force = round((force_down + force_up) / 2, 1)
        else:
            average_force = cls.get_force(weight)
        return average_force

    @classmethod
    def power_cardio(cls, cardio_type, user_weight, female=True):
        """

        :param cardio_type: string
        :param user_weight: kg
        :param female: bool
        :return:
        """
        cardio_name = cardio_type.name if cardio_type is not None else None
        # cardio_name = cardio_type.name or None
        mets = cls.mets_cardio(cardio_name, female)
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
    def force_cardio(cls, cardio_type, user_weight=60.0, female=True):
        """

        :param cardio_type:
        :param user_weight:
        :param female:
        :return:
        """
        cardio_name = cardio_type.name if cardio_type is not None else None
        mets = cls.mets_cardio(cardio_name, female)
        force = round(mets * 3.5 * user_weight * 427 / (200 * 60), 2)
        return force

    @classmethod
    def get_force(cls, weight, accel=0.0):
        """

        :param weight: kg, weight lifted
        :param accel: m/s^2, acceleration +ve is against gravity, -ve is with gravity
        :return: force N
        """
        g = 9.8
        force = round(weight * (g + accel), 1)

        return force

    @classmethod
    def get_accel(cls, distance_moved, time_taken):
        """

        :param distance_moved:
        :param time_taken:
        :return:
        """
        accel = 2 * distance_moved / time_taken ** 2
        return accel

    @classmethod
    def mets_cardio(cls, cardio_type, female=True):
        """

        :param cardio_type:
        :param female:
        :return:
        """
        mets = cardio_mets_table.get(cardio_type, 5)  # default to 5
        if female:
            mets -= 1
        return mets
