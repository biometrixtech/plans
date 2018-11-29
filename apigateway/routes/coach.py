from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from fathomapi.utils.exceptions import NoSuchEntityException, ForbiddenException
from flask import Blueprint, request
from datastores.datastore_collection import DatastoreCollection
from models.metrics import MetricType, DailyHighLevelInsight, WeeklyHighLevelInsight, MetricColor
from models.dashboard import TeamDashboardData, AthleteDashboardData, AthleteDashboardSummary
from utils import format_date
import datetime


app = Blueprint('coach', __name__)
USERS_API_VERSION = '2_1'


@app.route('/<uuid:coach_id>/dashboard', methods=['GET'])
@require.authenticated.any
@xray_recorder.capture('routes.team.dashboard.get')
def get_dashboard_data(coach_id):
    team_ids, tz = _get_teams(coach_id)
    minute_offset = _get_offset(tz)
    current_time = datetime.datetime.now() + datetime.timedelta(minutes=minute_offset)
    start_time = datetime.datetime(
                                   year=current_time.year, 
                                   month=current_time.month,
                                   day=current_time.day,
                                   hour=3,
                                   minute=0,
                                   second=0
                                  )
    end_time = datetime.datetime(
                                 year=current_time.year, 
                                 month=current_time.month,
                                 day=current_time.day,
                                 hour=23,
                                 minute=59,
                                 second=59
                                )
    athlete_stats_datastore = DatastoreCollection().athlete_stats_datastore
    daily_readiness_datastore = DatastoreCollection().daily_readiness_datastore
    teams = []
    for team_id in team_ids:
        team_name, user_ids, users = _get_team_info(coach_id, team_id)
        team = TeamDashboardData(team_name)
        completed = []
        incomplete = []
        athlete_stats_list = athlete_stats_datastore.get(user_ids)
        readiness_survey_list = daily_readiness_datastore.get(user_ids,
                                                              start_date=start_time,
                                                              end_date=end_time,
                                                              last_only=False)
        completed_users = [survey.user_id for survey in readiness_survey_list]

        for athlete_stats in athlete_stats_list:
            if athlete_stats is not None:
                user_id = athlete_stats.athlete_id
                user_dict = users[user_id]
                if user_id in completed_users:
                    completed.append(user_dict)
                else:
                    incomplete.append(user_dict)
                athlete = AthleteDashboardData(user_dict['user_id'], user_dict['first_name'], user_dict['last_name'])
                for metric in athlete_stats.metrics:
                    # update athlete card based on insight
                    if metric.specific_insight_training_volume != "":
                        athlete.insights.append(metric.specific_insight_training_volume)
                    if metric.specific_insight_recovery != "":
                        athlete.insights.append(metric.specific_insight_recovery)
                    athlete.color = MetricColor(max([athlete.color.value, metric.color.value]))
                    athlete.cleared_to_train = False if athlete.color.value == 2 else True
                    # update team card for the athlete
                    if metric.metric_type == MetricType.daily:
                        team.add_user_to_daily_report(user_dict, metric)
                        athlete.daily_recommendation.update([m.text for m in metric.specific_actions if m.display])
                    elif metric.metric_type == MetricType.longitudinal:
                        team.add_user_to_weekly_report(user_dict, metric)
                        athlete.weekly_recommendation.update([m.text for m in metric.specific_actions if m.display])
                if len(athlete_stats.metrics) == 0:
                    # add user to all good
                    user = AthleteDashboardSummary(user_dict['user_id'], user_dict['first_name'], user_dict['last_name'])
                    getattr(team.daily_insights, 'all_good').append(user)
                team.athletes.append(athlete)

        # consodilate weekly and daily card for team
        for k, v in team.daily_insights_dict.items():
            high_insight = DailyHighLevelInsight(k).name
            for user_id, user in v.items():
                getattr(team.daily_insights, high_insight).append(user)
        for k, v in team.weekly_insights_dict.items():
            high_insight = WeeklyHighLevelInsight(k).name
            for user_id, user in v.items():
                getattr(team.weekly_insights, high_insight).append(user)

        team.compliance['completed'] = completed
        team.compliance['incomplete'] = incomplete
        teams.append(team.json_serialise())
    return {'teams': teams}, 200


def _get_teams(user_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"user/{user_id}")
    team_ids = response['user']['account_ids']
    # if len(team_ids) == 0:
    #     raise NoSuchEntityException("User does not belong to any team")
    return team_ids, response['user']['timezone']


def _get_team_info(user_id, account_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"account/{account_id}/users")
    user_ids = response['account']['users']
    # if user_id in user_ids:
    #     raise ForbiddenException("Must be a coach to view the dashboard")
    team_name = response['account']['name']
    users = {}
    for user in response['users']:
        users[user['id']] = {'user_id': user['id'],
                             'first_name': user['personal_data']['first_name'],
                             'last_name': user['personal_data']['last_name']}
    return team_name, user_ids, users


def _get_offset(tz):
    offset = tz.split(":")
    hour_offset = int(offset[0])
    minute_offset = int(offset[1])
    if hour_offset < 0:
        minute_offset = hour_offset * 60 - minute_offset
    else:
        minute_offset += hour_offset * 60
    return minute_offset
