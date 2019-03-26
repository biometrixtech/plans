from flask import request, Blueprint

from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder

from datastores.season_datastore import AthleteSeasonDatastore
from models.athlete_season import AthleteSeason, Season


app = Blueprint('athlete_season', __name__)


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.athlete_season.create')
def handle_season_create():
    seasons = []
    for season in request.json['seasons']:
        seasons.append(Season(sport=season['sport'],
                              competition_level=season['competition_level'],
                              positions=season['positions'],
                              start_date=season['start_date'],
                              end_date=season['end_date']))
    athlete_season = AthleteSeason(user_id=request.json['user_id'],
                                   seasons=seasons)
    store = AthleteSeasonDatastore()

    store.put(athlete_season)

    return {'message': 'success'}, 201
