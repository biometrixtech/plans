from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from fathomapi.utils.exceptions import NoSuchEntityException
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
    event_date = format_date(datetime.datetime.now() + datetime.timedelta(minutes=minute_offset))
    athlete_stats_datastore = DatastoreCollection().athlete_stats_datastore
    count = 0
    teams = []
    for team_id in team_ids:
        team_name = 'Team'+str(count)
        team = TeamDashboardData(team_name)
        completed = []
        incomplete = []
        users = _get_users_in_team(team_id)
        for user_id in users:
            user = _get_user(user_id)
            if DatastoreCollection().daily_plan_datastore.get(user_id, event_date, event_date)[0].daily_readiness_survey_completed():
                completed.append(user)
            else:
                incomplete.append(user)
            team.compliance['completed'] = completed
            team.compliance['incomplete'] = incomplete
            athlete_stats = athlete_stats_datastore.get(user_id)
            if athlete_stats is not None:
                athlete = AthleteDashboardData(user['user_id'], user['first_name'], user['last_name'])
                for metric in athlete_stats.metrics:
                    # update athlete card based on insight
                    athlete.insights.append(metric.specific_insight_training_volume)
                    athlete.insights.append(metric.specific_insight_recovery)
                    athlete.color = MetricColor(max([athlete.color.value, metric.color.value]))
                    athlete.cleared_to_train = False if athlete.color.value == 2 else True
                    # update team card for the athlete
                    if metric.metric_type == MetricType.daily:
                        team.add_user_to_daily_report(user, metric)
                        athlete.daily_recommendation.extend(metric.specific_actions)
                    elif metric.metric_type == MetricType.longitudional:
                        team.add_user_to_weekly_report(user, metric)
                        athlete.weekly_recommendation.extend(metric.specific_actions)
                athlete.insights = [i for i in athlete.insights if i != '']
                athlete.daily_recommendation = list(set(athlete.daily_recommendation))
                athlete.weekly_recommendation = list(set(athlete.weekly_recommendation))
                if len(athlete_stats.metrics) == 0:
                    # add user to all good
                    user = AthleteDashboardSummary(user['user_id'], user['first_name'], user['last_name'])
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
        teams.append(team.json_serialise())
        count += 1
    return {'teams': teams}, 200


def _get_teams(user_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"user/{user_id}")
    return response['user']['account_ids'], response['user']['timezone']


def _get_users_in_team(account_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"account/{account_id}")
    return response['account']['users']


def _get_user(user_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"user/{user_id}")
    return {"user_id": user_id,
            "first_name": response['user']['personal_data']['first_name'],
            "last_name": response['user']['personal_data']['first_name']}

def _get_offset(tz):
    offset = tz.split(":")
    hour_offset = int(offset[0])
    minute_offset = int(offset[1])
    if hour_offset < 0:
        minute_offset = hour_offset * 60 - minute_offset
    else:
        minute_offset += hour_offset * 60
    return minute_offset
