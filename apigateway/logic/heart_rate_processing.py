from models.heart_rate import HeartRateData, SessionHeartRate
from datetime import timedelta
from utils import parse_datetime

class HeartRateProcessing(object):
    def __init__(self, user_age):
        self.user_age = user_age

    def get_shrz(self, heart_rate_data):

        max_heart_rate = float(220) - float(self.user_age)

        zone_1_duration = 0
        zone_2_duration = 0
        zone_3_duration = 0
        zone_4_duration = 0
        zone_5_duration = 0

        full_heart_data = self.extrapolate_heart_rate_data(heart_rate_data)

        for h in full_heart_data:
            if max_heart_rate * 0.5 <= float(h) < max_heart_rate * 0.6:
                zone_1_duration += 1
            elif max_heart_rate * 0.6 <= float(h) < max_heart_rate * 0.7:
                zone_2_duration += 1
            elif max_heart_rate * 0.7 <= float(h) < max_heart_rate * 0.8:
                zone_3_duration += 1
            elif max_heart_rate * 0.8 <= float(h) < max_heart_rate * 0.9:
                zone_4_duration += 1
            elif max_heart_rate * 0.9 <= float(h) <= max_heart_rate:
                zone_5_duration += 1

        zone_1_duration = zone_1_duration * 1
        zone_2_duration = zone_2_duration * 2
        zone_3_duration = zone_3_duration * 3
        zone_4_duration = zone_4_duration * 4
        zone_5_duration = zone_5_duration * 5

        total_duration = zone_1_duration + zone_2_duration + zone_3_duration + zone_4_duration + zone_5_duration

        total_possible_duration = len(full_heart_data) * 5

        shrz = (total_duration / total_possible_duration) * 10

        shrz = max(1, shrz)

        return shrz

    def extrapolate_heart_rate_data(self, heart_rate_data):
        heart_rate_data = sorted(heart_rate_data, key=lambda k: k.start_date)
        new_heart_rate_data = []

        for h in range(0, len(heart_rate_data) - 1):
            last_date_time = parse_datetime(heart_rate_data[h].start_date)
            next_date_time = parse_datetime(heart_rate_data[h + 1].start_date)
            seconds_diff = (next_date_time - last_date_time).seconds
            new_heart_rate_data.append(heart_rate_data[h].value)
            if seconds_diff > 0:
                for s in range(1, seconds_diff):
                    new_heart_rate = ((heart_rate_data[h + 1].value - heart_rate_data[h].value) / seconds_diff * s) + heart_rate_data[h].value
                    new_heart_rate_data.append(new_heart_rate)

        new_heart_rate_data.append(heart_rate_data[len(heart_rate_data) - 1].value)

        return new_heart_rate_data


