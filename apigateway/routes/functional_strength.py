from flask import request, Blueprint

from fathomapi.utils.decorators import require
from fathomapi.utils.exceptions import InvalidSchemaException, NoSuchEntityException
from fathomapi.utils.xray import xray_recorder
from datastores.datastore_collection import DatastoreCollection
from datastores.daily_plan_datastore import DailyPlanDatastore
from datastores.athlete_stats_datastore import AthleteStatsDatastore
from datastores.completed_exercise_datastore import CompletedExerciseDatastore
from logic.training_plan_management import TrainingPlanManager
from models.soreness import CompletedExercise
from utils import format_date, parse_datetime, format_datetime
from config import get_mongo_collection
from datetime import timedelta

app = Blueprint('functional_strength', __name__)


@app.route('/', methods=['PATCH'])
@require.authenticated.any
@xray_recorder.capture('routes.functional_strength')
def handle_functional_strength_update(principal_id=None):
    user_id = principal_id
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = parse_datetime(request.json['event_date'])

    completed_exercises = request.json.get('completed_exercises', [])

    plan_event_date = format_date(event_date)
    fs_event_date = format_datetime(event_date)

    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')
    store = DailyPlanDatastore()

    plan = store.get(user_id=user_id, start_date=plan_event_date, end_date=plan_event_date)[0]

    save_exercises = True
    if plan.functional_strength_session is not None:
        if plan.functional_strength_session.completed:
            save_exercises = False
        plan.functional_strength_session.completed = True
        plan.functional_strength_session.event_date = fs_event_date
    plan.functional_strength_completed = True
    plan.completed_functional_strength_sessions = plan.completed_functional_strength_sessions + 1
    store.put(plan)

    athlete_stats_store = AthleteStatsDatastore()
    athlete_stats = athlete_stats_store.get(athlete_id=user_id)
    athlete_stats.completed_functional_strength_sessions += 1
    athlete_stats.next_functional_strength_eligible_date = format_datetime(parse_datetime(fs_event_date) + timedelta(days=1))
    athlete_stats_store.put(athlete_stats)

    if save_exercises:
        save_completed_exercises(completed_exercises, user_id, fs_event_date)

    survey_complete = plan.daily_readiness_survey_completed()
    landing_screen, nav_bar_indicator = plan.define_landing_screen()
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = survey_complete
    plan['landing_screen'] = 1.0
    plan['nav_bar_indicator'] = nav_bar_indicator
    del plan['daily_readiness_survey'], plan['user_id']

    return {'daily_plans': [plan]}, 202


@app.route('/', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.functional_strength')
def handle_functional_strength_start(principal_id=None):
    user_id = principal_id
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = parse_datetime(request.json['event_date'])

    plan_event_date = format_date(event_date)
    fs_start_date = format_datetime(event_date)

    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')
    store = DailyPlanDatastore()

    plan = store.get(user_id=user_id,
                     start_date=plan_event_date,
                     end_date=plan_event_date)[0]

    if plan.functional_strength_session is not None:
        plan.functional_strength_session.start_date = fs_start_date
        # TODO: need to implement this route
        # plans_service = Service('plans', Config.get('API_VERSION'))
        # body = {"event_date": recovery_start_date}
        # plans_service.call_apigateway_async(method='POST',
        #                                     endpoint=f'/athlete/{user_id}/fs_started',
        #                                     body=body)
    store.put(plan)

    return {'message': 'success'}, 200


@app.route('/activate', methods=['POST'])
@require.authenticated.any
@xray_recorder.capture('routes.functional_strength.activate')
def handle_functional_strength_activate(principal_id=None):
    if not isinstance(request.json, dict):
        raise InvalidSchemaException('Request body must be a dictionary')
    if 'event_date' not in request.json:
        raise InvalidSchemaException('Missing required parameter event_date')
    else:
        event_date = parse_datetime(request.json['event_date'])
    if 'current_sport_name' not in request.json:
        raise InvalidSchemaException('Missing required parameter current_sport_name')
    if 'current_position' not in request.json:
        raise InvalidSchemaException('Missing required parameter current_position')

    user_id = principal_id
    plan_event_date = format_date(event_date)

    # update athlete stats with sport/position information
    athlete_stats_store = AthleteStatsDatastore()
    athlete_stats = athlete_stats_store.get(athlete_id=user_id)
    if request.json['current_sport_name'] is not None:
        athlete_stats.current_sport_name = request.json['current_sport_name']
    else:
        raise InvalidSchemaException("current_sport_name cannot be null")
    athlete_stats.current_position = request.json['current_position']
    athlete_stats_store.put(athlete_stats)

    # get functional strength for the day and update daily_plan
    if not _check_plan_exists(user_id, plan_event_date):
        raise NoSuchEntityException('Plan not found for the user')
    daily_plan_store = DailyPlanDatastore()
    plan = daily_plan_store.get(user_id=user_id, start_date=plan_event_date, end_date=plan_event_date)[0]
    plan_manager = TrainingPlanManager(user_id, DatastoreCollection())
    plan = plan_manager.populate_functional_strength(daily_plan=plan,
                                                     athlete_stats=athlete_stats,
                                                     wants_functional_strength=True)
    daily_plan_store.put(plan)

    # return plan to user
    plan = plan.json_serialise()
    plan['daily_readiness_survey_completed'] = True
    plan['landing_screen'] = 1.0
    plan['nav_bar_indicator'] = 1.0
    del plan['daily_readiness_survey'], plan['user_id']

    return {'daily_plan': plan}, 200


def save_completed_exercises(exercise_list, user_id, event_date):
    exercise_store = CompletedExerciseDatastore()

    for exercise in exercise_list:
        exercise_store.put(CompletedExercise(athlete_id=user_id,
                                             exercise_id=exercise,
                                             event_date=event_date))


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    if mongo_collection.count({"user_id": user_id,
                               "date": event_date}) == 1:
        return True
    else:
        return False
