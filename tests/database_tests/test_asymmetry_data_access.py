import pytest
from aws_xray_sdk.core import xray_recorder
from config import get_secret
import os
import json
from models.asymmetry import SessionAsymmetry, TimeBlockAsymmetry
from datastores.asymmetry_datastore import AsymmetryDatastore

from utils import parse_date


@pytest.fixture(scope="session", autouse=True)
def add_xray_support(request):
    os.environ["ENVIRONMENT"] = "test"

    xray_recorder.configure(sampling=False)
    xray_recorder.begin_segment(name="test")

    config = get_secret('mongo')
    os.environ["MONGO_HOST"] = config['host']
    os.environ["MONGO_REPLICASET"] = config['replicaset']
    os.environ["MONGO_DATABASE"] = config['database']
    os.environ["MONGO_USER"] = config['user']
    os.environ["MONGO_PASSWORD"] = config['password']
    os.environ["MONGO_COLLECTION_ASYMMETRY"] = config['collection_asymmetry']


def test_get_session_1():
    session_id = "f78a9e26-6003-5ac7-8590-3ae4a421dac7"
    datastore = AsymmetryDatastore()
    asymmetry = datastore.get(session_id)
    assert None is not asymmetry