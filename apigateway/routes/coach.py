from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from fathomapi.utils.exceptions import NoSuchEntityException, ForbiddenException
from flask import Blueprint
from datastores.datastore_collection import DatastoreCollection
from models.dashboard import TeamDashboardData, AthleteDashboardData
from utils import format_date
import datetime
import os


app = Blueprint('coach', __name__)
USERS_API_VERSION = os.environ['USERS_API_VERSION']


@app.route('/<uuid:coach_id>/dashboard', methods=['GET'])
@require.authenticated.any
@xray_recorder.capture('routes.team.dashboard.get')
def get_dashboard_data(coach_id):
    try:
        team_ids, tz = _get_teams(coach_id)
    except NoSuchEntityException as e:
        raise e
    except:
        return {'message': 'Could not get the teams associated with the user'}, 500
    else:
        minute_offset = _get_offset(tz)
        current_time = datetime.datetime.now() + datetime.timedelta(minutes=minute_offset)

        athlete_stats_datastore = DatastoreCollection().athlete_stats_datastore
        daily_plan_datastore = DatastoreCollection().daily_plan_datastore
        teams = []
        for team_id in team_ids:
            try:
                team_name, user_ids, users = _get_team_info(coach_id, team_id)
            except ForbiddenException as e:
                raise e
            except:
                return {'message': 'Error Getting users for the team'}, 500
            else:
                team = TeamDashboardData(team_name)
                daily_plan_list = daily_plan_datastore.get(user_ids,
                                                           start_date=format_date(current_time),
                                                           end_date=format_date(current_time))
                team.get_compliance_data(user_ids, users, daily_plan_list)
                athlete_stats_list = athlete_stats_datastore.get(user_ids)

                for athlete_stats in athlete_stats_list:
                    user_id = athlete_stats.athlete_id
                    user_dict = users[user_id]
                    athlete = AthleteDashboardData(user_dict['user_id'], user_dict['first_name'], user_dict['last_name'])
                    athlete.aggregate(athlete_stats.metrics)
                    team.insert_user(athlete)
                    team.athletes.append(athlete)

                teams.append(team.json_serialise())
        return {'teams': teams}, 200


def _get_teams(user_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"user/{user_id}")
    team_ids = response['user']['account_ids']
    if len(team_ids) == 0:
        raise NoSuchEntityException("User does not belong to any team")
    return team_ids, response['user']['timezone']


def _get_team_info(user_id, account_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"account/{account_id}/users")
    user_ids = response['account']['users']
    if user_id in user_ids:
        raise ForbiddenException("Must be a coach to view the dashboard")
    team_name = response['account']['name']
    users = {}
    for user in response['users']:
        users[user['id']] = {'user_id': user['id'],
                             'first_name': user['personal_data']['first_name'],
                             'last_name': user['personal_data']['last_name']}
    return team_name, user_ids, users


def _get_offset(tz):
    if tz is None:
        tz = "-05:00"
    offset = tz.split(":")
    hour_offset = int(offset[0])
    minute_offset = int(offset[1])
    if hour_offset < 0:
        minute_offset = hour_offset * 60 - minute_offset
    else:
        minute_offset += hour_offset * 60
    return minute_offset
