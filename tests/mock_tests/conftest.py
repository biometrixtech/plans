import os
from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False, context_missing='LOG_ERROR')
xray_recorder.begin_segment(name="test")
from fathomapi.api.config import Config
os.environ['UNIT_TESTS'] = 'TRUE'


def pytest_configure():
    os.environ['ENVIRONMENT'] = 'dev'
    Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                                 'body_part_mapping_filename': 'body_part_mapping_fathom.json',
                                 'movement_library_filename': 'movement_library_demo.json',
                                 'cardio_data_filename': 'cardiorespiratory_data_soflete.json'})
