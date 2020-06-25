import pandas as pd
import numpy as np
from scipy.interpolate import interp1d

from logic.calculators import ftp_from_population, power_running, power_cycling


# def ftp_from_population(weight, athletic_level=None, gender=True):
#     """
#     from Garmin
#     https://www8.garmin.com/manuals/webhelp/edge520/EN-US/GUID-1F58FA8E-09FF-4E51-B9B4-C4B83ED1D6CE.html
#     male = {
#         'superior': (5.05, None),
#         'excellent': (3.93, 5.04),
#         'good': (2.79, 3.92),
#         'fair': (2.23, 2.78),
#         'untrained': (0, 2.23)
#      }
#
#     gender = {
#         'superior': (4.5, None),
#         'excellent': (3.33, 4.29),
#         'good': (2.36, 3.32),
#         'fair': (1.90, 2.35),
#         'untrained': (0, 1.90)
#      }
#
#     :param weight:
#     :param athletic_level:
#     :param gender:
#     :return:
#     """
#     population_fpt = {
#         'male': {
#             'superior': 5.05,
#             'excellent':  4.49,
#             'good': 3.35,
#             'fair': 2.5,
#             'untrained': 1.12
#          },
#         'gender': {
#             'superior': 4.5,
#             'excellent': 3.81,
#             'good': 2.84,
#             'fair': 2.12,
#             'untrained': .95
#          }
#     }
#     if gender:
#         ftp_per_kg = population_fpt.get('gender').get(athletic_level, 2.12)  # use fair as default
#     else:
#         ftp_per_kg = population_fpt.get('male').get(athletic_level, 2.5)  # use fair as default
#
#     return ftp_per_kg * weight

def simulate_hr_data(x, y):
    f = interp1d(x, y, kind='slinear', bounds_error=False, fill_value=(0, 10))
    data = []
    for i in range(1000):
        age = np.random.randint(20, 40)  # update range and change from uniform distribution
        max_hr = 208 - 0.7 * age
        hr = np.random.randint(.5 * max_hr, max_hr)  # change from uniform distribution
        percent_hrmax = round(hr / max_hr * 100, 1)
        rpe = round(f([percent_hrmax])[0], 2)
        data.append(
                {
                    "percent_hrmax": percent_hrmax / 100,
                    "rpe": rpe,
                    "age": age,
                    "max_hr": max_hr,
                    "hr": hr
                }
        )
    return data


def simulate_ftp_data(x, y):
    f = interp1d(x, y, kind='slinear', bounds_error=False, fill_value=(0, 10))
    data = []
    for i in range(1000):
        female = np.random.choice([True, False])
        if female:
            weight = np.random.randint(45, 90)  # change from uniform distribution
        else:
            weight = np.random.randint(55, 120)  # change from uniform distribution
        athletic_level = np.random.choice(a=['superior', 'excellent', 'good', 'fair', 'untrained'],
                                          p=[.1, .1, .3, .4, .1])
        ftp = ftp_from_population(weight, athletic_level=athletic_level, female=female)
        activity = np.random.choice(['running', 'cycling'])
        # get random based on calculations for running and cycling
        if activity == 'running':
            speed = np.random.choice([5, 6, 8, 10])  # mph
            speed *= 1609 / 60
            grade = np.random.choice([0, .01, .02, .03])
            watts = power_running(speed, grade, weight)
        else:
            speed = np.random.choice([10, 15, 20, 25, 30])  #kmph
            speed *= 1000 / 3600
            grade = np.random.choice([0, .01, .03, .05])
            watts = power_cycling(speed, weight, grade=grade)
        percent_ftp = watts / ftp * 100
        rpe = round(f([percent_ftp])[0], 2)
        data.append(
                {
                    "percent_ftp": percent_ftp / 100,
                    "rpe": rpe,
                    "weight": weight,
                    "gender": female,
                    "watts": watts,
                    "activity": activity
                }
        )
    return data

mcmillan_hr = pd.read_csv('rpe_training/mcmillan_hr.csv')
mountainpeak_hr = pd.read_csv('rpe_training/mountainpeak_hr.csv')
apex_hr = pd.read_csv('rpe_training/apex_hr.csv')
mcmillan_hr_simulated = simulate_hr_data(mcmillan_hr['percent_hrmax'].values, mcmillan_hr['rpe'].values)
mountainpeak_hr_simulated = simulate_hr_data(mountainpeak_hr['percent_hrmax'].values, mountainpeak_hr['rpe'].values)
apex_hr_simulated = simulate_hr_data(apex_hr['percent_hrmax'].values, apex_hr['rpe'].values)
all_simulated_hr_data = mcmillan_hr_simulated + mountainpeak_hr_simulated + apex_hr_simulated
simulated_data = pd.DataFrame(all_simulated_hr_data)

ftp = pd.read_csv('rpe_training/ftp.csv')
simulated_ftp_data = pd.DataFrame(simulate_ftp_data(ftp['percent_ftp'], ftp['rpe'].values))

simulated_data = simulated_data.append(simulated_ftp_data, ignore_index=True)
simulated_data.to_csv('rpe_training/simulated_data.csv', index=False)


print('here')

