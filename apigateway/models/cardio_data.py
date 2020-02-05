import os
import json
from fathomapi.api.config import Config


def get_cardio_data():
    file_name =  Config.get('PROVIDER_INFO')['cardio_data_filename']  #'cardiorespiratory_data_{provider}.json'
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, file_name)
    with open(file_path, 'r') as f:
        cardio_data = json.load(f)
    return cardio_data
