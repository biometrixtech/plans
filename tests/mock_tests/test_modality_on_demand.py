import os
os.environ['ENVIRONMENT'] = 'dev'
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

import datetime

from survey_processing import add_modality_on_demand
from models.stats import AthleteStats
from models.functional_movement_modalities import ModalityType

def test_get_warm_up():
    user_id = 'templated_modality_test'
    event_date = datetime.datetime.now()
    athlete_stats = AthleteStats(user_id)
    athlete_stats.event_date = event_date
    plan = add_modality_on_demand(user_id, event_date, modality_type=2, visualizations=True, athlete_stats=athlete_stats)


def test_get_cool_down():
    user_id = 'templated_modality_test'
    event_date = datetime.datetime.now()
    athlete_stats = AthleteStats(user_id)
    athlete_stats.event_date = event_date
    plan = add_modality_on_demand(user_id, event_date, modality_type=3, visualizations=True, athlete_stats=athlete_stats)