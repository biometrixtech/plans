import os
import json

def get_cardio_data(provider='fathom'):
    file_name = f'cardiorespiratory_data_{provider}.json'
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, file_name)
    with open(file_path, 'r') as f:
        cardio_data = json.load(f)
    return cardio_data
