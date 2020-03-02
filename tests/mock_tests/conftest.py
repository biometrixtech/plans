import os
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from fathomapi.api.config import Config


def pytest_configure():
    os.environ['ENVIRONMENT'] = 'dev'
    Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                                 'body_part_mapping_filename': 'body_part_mapping_fathom.json',
                                 'movement_library_filename': 'movement_library_soflete.json',
                                 'cardio_data_filename': 'cardiorespiratory_data_soflete.json'})
