from aws_xray_sdk.core import xray_recorder

xray_recorder.configure(sampling=False)
xray_recorder.begin_segment(name="test")

from datastores.local_exercise_datastore import ExerciseLibraryDatastore


def test_read_exercise():
    ds = ExerciseLibraryDatastore()
    exercises = ds.get()
    assert len(exercises) > 0

