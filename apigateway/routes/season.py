from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import json
import datetime

from decorators import authentication_required
from exceptions import InvalidSchemaException
from datastores.season_datastore import AthleteSeasonDatastore
from models.season import AthleteSeason


app = Blueprint('athlete_season', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.athlete_season.create')
def handle_season_create():
    season = AthleteSeason(user_id=request.json['user_id'],
                           sports=request.json['sports'])
    store = AthleteSeasonDatastore()

    store.put(season)

    return {'message': 'success'}, 201



