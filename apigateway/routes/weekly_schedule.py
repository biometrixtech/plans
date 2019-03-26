from flask import request, Blueprint
import datetime

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException
from fathomapi.utils.xray import xray_recorder
from datastores.weekly_schedule_datastore import WeeklyCrossTrainingDatastore, WeeklyTrainingDatastore
from models.weekly_schedule import WeeklySchedule
from models.sport import SportName

app = Blueprint('weekly_schedule', __name__)


@app.route('/cross_training', methods=['POST'])
@require.authenticated.any
@require.body({'user_id': str})
@xray_recorder.capture('routes.weekly_schedule.cross_training.create')
def handle_crosstraining_schedule_create():
    validate_crosstraining_data(request)
    today = datetime.datetime.today()
    today_weekday = today.weekday()
    days = request.json['days_of_week']

    if today_weekday < 4:
        monday_delta = -today_weekday
    elif today_weekday >= 4:
        monday_delta =  7 - today_weekday
    week_start = (today + datetime.timedelta(days=monday_delta)).strftime("%Y-%m-%d")

    cross_training = {
                        "days_of_week": request.json['days_of_week'],
                        "activities": request.json['activities'],
                        "duration": request.json['duration'],
                    }

    schedule = WeeklySchedule(
        user_id=request.json['user_id'],
        week_start=week_start,
        cross_training=cross_training)
    store = WeeklyCrossTrainingDatastore()

    store.put(schedule, collection='training')
    return {'message': 'success'}, 201


@app.route('/cross_training/get_schedule', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.weekly_schedule.cross_training.get')
def handle_crosstraining_schedule_get():
    pass


@app.route('/cross_training/update', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.weekly_schedule.cross_training.update')
def handle_crosstraining_schedule_update():
    pass


@app.route('/training', methods=['POST'])
@require.authenticated.any
@require.body({'user_id': str})
@xray_recorder.capture('routes.weekly_schedule.training.create')
def handle_training_schedule_create():
    validate_training_data(request)
    today = datetime.datetime.today()
    today_weekday = today.weekday()

    if today_weekday < 4:
        monday_delta = -today_weekday
    elif today_weekday >= 4:
        monday_delta =  7 - today_weekday
    week_start = (today + datetime.timedelta(days=monday_delta)).strftime("%Y-%m-%d")

    schedule = WeeklySchedule(
        user_id=request.json['user_id'],
        week_start=week_start,
        sports=request.json['sports'],
    )
    store = WeeklyTrainingDatastore()

    store.put(schedule, collection='training')
    return {'message': 'success'}, 201


@app.route('/training/get_schedule', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.weekly_schedule.cross_training.get')
def handle_training_schedule_get():
    pass


@app.route('/training/update', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.weekly_schedule.cross_training.update')
def handle_training_schedule_update():
    pass


@xray_recorder.capture('routes.weekly_schedule.validate_crosstraining')
def validate_crosstraining_data(request):
    pass


@xray_recorder.capture('routes.weekly_schedule.validate_crosstraining')
def validate_training_data(request):
    for sport in request.json['sports']:
        try:
            SportName[sport['sport']]
        except KeyError:
            raise InvalidSchemaException('sport not identified')

