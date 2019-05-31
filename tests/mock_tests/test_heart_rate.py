from models.heart_rate import HeartRateData, SessionHeartRate
from logic.heart_rate_processing import HeartRateProcessing
from datetime import datetime, timedelta
from utils import format_datetime
import random


def get_heart_rate_data(low_value, high_value, observations):

    current_date_time = datetime.now()

    heart_rate_list = []

    heart_rate = {}
    heart_rate['start_date'] = format_datetime(current_date_time)
    heart_rate['end_date'] = format_datetime(current_date_time)
    heart_rate['value'] = low_value

    data = HeartRateData(heart_rate)
    heart_rate_list.append(data)

    next_date_time = current_date_time

    for d in range(1, observations):
        next_date_time = next_date_time + timedelta(seconds=(4*d))
        heart_rate = {}
        heart_rate['start_date'] = format_datetime(next_date_time)
        heart_rate['end_date'] = format_datetime(next_date_time)
        value = random.randint(low_value, high_value)
        heart_rate['value'] = value
        data = HeartRateData(heart_rate)
        heart_rate_list.append(data)

    return heart_rate_list


def test_get_shrz_simple():

    heart_rate_list = get_heart_rate_data(103, 145, 100)

    heart_rate_processing = HeartRateProcessing(30)

    shrz = heart_rate_processing.get_shrz(heart_rate_list)

    assert shrz is not None






