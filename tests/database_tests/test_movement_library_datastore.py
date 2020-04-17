from aws_xray_sdk.core import xray_recorder
xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")
from fathomapi.api.config import Config
from datastores.movement_library_datastore import MovementLibraryDatastore


def test_read_movements_soflete():
    Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_soflete.json',
                                 'body_part_mapping_filename': 'body_part_mapping_soflete.json',
                                 'movement_library_filename': 'movement_library_soflete.json'
                                 })
    ds = MovementLibraryDatastore()
    movements = ds.get()
    assert len(movements) == 1960

def test_read_movements_fathom():
    Config.set('PROVIDER_INFO', {'exercise_library_filename': 'exercise_library_fathom.json',
                                 'body_part_mapping_filename': 'body_part_mapping_fathom.json'
                                 })
    ds = MovementLibraryDatastore()
    movements = ds.get()
    assert len(movements) == 0
