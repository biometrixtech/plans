from aws_xray_sdk.core import xray_recorder
from flask import request, Blueprint
import json
import datetime

from decorators import authentication_required
from exceptions import InvalidSchemaException
from datastores.season_datastore import AthleteSeasonDatastore
from models.season import AthleteSeason, Sport


app = Blueprint('athlete_season', __name__)


@app.route('/', methods=['POST'])
@authentication_required
@xray_recorder.capture('routes.athlete_season.create')
def handle_season_create():
    sports = []
    for sport in request.json['sports']:
        sports.append(Sport(name=sport['name'],
                      competition_level=sport['competition_level'],
                      positions=sport['positions'],
                      start_date=sport['start_date'],
                      end_date=sport['end_date'])
                     )       
    season = AthleteSeason(user_id=request.json['user_id'],
                           sports=sports)
    store = AthleteSeasonDatastore()

    store.put(season)

    return {'message': 'success'}, 201



