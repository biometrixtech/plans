import os
import json
from fathomapi.api.config import Config


def get_cardio_data():
    try:
        file_name = Config.get('PROVIDER_INFO')['cardio_data_filename']
    except KeyError:
        print('Cardio data not defined or does not exist for this provider')
        file_name = 'cardiorespiratory_data_soflete.json'
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, file_name)
    with open(file_path, 'r') as f:
        cardio_data = json.load(f)
    return cardio_data
