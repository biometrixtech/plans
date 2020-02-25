import os
import json


def get_bodyweight_coefficients():
    script_dir = os.path.dirname(__file__)
    file_path = os.path.join(script_dir, 'bodyweight_coefficients.json')
    with open(file_path, 'r') as f:
        bodyweight_coefficients = json.load(f)
    return bodyweight_coefficients