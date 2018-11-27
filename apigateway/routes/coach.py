from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
# from fathomapi.utils.exceptions import NoSuchEntityException
from flask import Blueprint, request
# from datastores.datastore_collection import DatastoreCollection
# from serialisable import json_serialise
# from models.metrics import MetricType, DailyHighLevelInsight, WeeklyHighLevelInsight, MetricColor
# from utils import parse_date, parse_datetime, format_date, format_datetime
# import boto3
# import json
# import os
# import datetime
# import random


app = Blueprint('coach', __name__)
USERS_API_VERSION = '2_1'


@app.route('/<uuid:user_id>/dashboard', methods=['GET'])
@require.authenticated.any
@xray_recorder.capture('routes.team.dashboard.get')
def get_dashboard_data(user_id):
    # team_ids = _get_teams(user_id)
    # athlete_stats_datastore = DatastoreCollection().athlete_stats_datastore
    # count = 0
    # for team_id in team_ids:
    #   team_name = str(count)
    #     team = TeamDashboardData(team)
    #     completed = []
    #     incomplete = []
    #     users = _get_users_in_team(team_id)
    #     for user_id in users:
    #         user = _get_user(user_id)
    #         start_date = '2018-11-27'
    #         end_date = '2018-11-27'
    #         if DatastoreCollection().daily_plan_datastore.get(user_id, start_date, end_date)[0].daily_readiness_survey_completed():
    #             completed.append(user)
    #         else:
    #             incomplete.append(user)
    #         athlete_stats = athlete_stats_datastore.get(user_id)
    #         if athlete_stats is not None:
    #             athlete = AthleteDashboardData(user['user_id'], user['first_name'], usser['last_name'])
    #             for metric in athlete.metrics:
    #                 athlete.insights.append(metric.specific_insight_training_volume)
    #                 athlete.insights.append(metric.specific_insight_recovery)
    #                 if metric.metric_type == MetricType.daily:
    #                     team.add_user_to_daily_report(user, metric)
    #                     athlete.daily_recommendation.extend(metric.specific_actions)
    #                 elif metric.metric_type == MetricType.longitudional:
    #                     team.add_user_to_weekly_report(user, metric)
    #                     athlete.weekly_recommendation.extend(metric.specific_actions)
    #                 athlete.color = MetricColor(max([athlete.color.value, metric.color.value]))
    #                 athlete.cleared_to_train = athlete.determine_if_cleared_to_play()
    #
    #   count += 1


    teams = [{"name": "fathom",
            "compliance": {
                            "complete" : [{"first_name": "Dipesh", "last_name": "Gautam"},
                                          {"first_name": "Mazen", "last_name": "Chami"}
                                          ],
                            "incomplete" : [{"first_name": "Paul", "last_name": "LaForge"},
                                            {"first_name": "Gabby", "last_name": "Levac"},
                                            {"first_name": "Chris", "last_name": "Perry"},
                                            {"first_name": "Melissa", "last_name": "White"},
                                            {"first_name": "Ivonna", "last_name": "Dumanyan"}]

                            },
            "weekly_insights": [
                                {
                                 "address_pain_soreness": [{"user_id": "1",
                                                           "first_name": "Dipesh",
                                                           "last_name": "Gautam",
                                                           "cleared_to_train": True,
                                                           "color": 0},
                                                           {"user_id": "3",
                                                            "first_name": "Paul",
                                                            "last_name": "LaForge",
                                                            "cleared_to_train": False,
                                                            "color": 2}
                                                          ],
                                 "increase_workload": [{"user_id": "2",
                                                        "first_name": "Mazen",
                                                        "last_name": "Chami",
                                                        "cleared_to_train": True,
                                                        "color": 1}
                                                      ],
                                 "balance_overtraining_risk": [{"user_id": "4",
                                                           "first_name": "Melissa",
                                                           "last_name": "White",
                                                           "cleared_to_train": False,
                                                           "color": 2}],
                                 "add_variety": []
                                }
                             ],
            "daily_insights": [
                                {
                                 "limit_time_intensity": [{"user_id": "1",
                                                           "first_name": "Dipesh",
                                                           "last_name": "Gautam",
                                                           "cleared_to_train": True,
                                                           "color": 1}
                                                          ],
                                 "increase_workload": [{"user_id": "2",
                                                        "first_name": "Mazen",
                                                        "last_name": "Chami",
                                                        "cleared_to_train": True,
                                                        "color": 1}
                                                      ],
                                 "monitor_training": [{"user_id": "3",
                                                       "first_name": "Paul",
                                                       "last_name": "LaForge",
                                                       "cleared_to_train": True,
                                                       "color": 1}],
                                 "not_cleared": [{"user_id": "7",
                                                  "first_name": "Ivonna",
                                                  "last_name": "Dumanyan",
                                                   "cleared_to_train": False,
                                                   "color": 2},
                                                 {"user_id": "4",
                                                  "first_name": "Melissa",
                                                  "last_name": "White",
                                                  "cleared_to_train": False,
                                                  "color": 2}],
                                 "all_good": [{"user_id": "5",
                                               "first_name": "Chris",
                                               "last_name": "Perry",
                                               "cleared_to_train": True,
                                               "color": 0},
                                              {"user_id": "6",
                                               "first_name": "Gabby",
                                               "last_name": "Levac",
                                               "cleared_to_train": True,
                                               "color": 0}
                                               ]
                                }
                              ],
            "athletes": [{"user_id": 1},
                         {"user_id": 2},
                         {"user_id": 3},
                         {"user_id": 4},
                         {"user_id": 5},
                         {"user_id": 6},
                         {"user_id": 7}]

                 },
            {"name": "fathom-2",
            "compliance": {
                            "complete" : [{"first_name": "Dipesh", "last_name": "Gautam"},
                                          {"first_name": "Mazen", "last_name": "Chami"}
                                          ],
                            "incomplete" : [{"first_name": "Paul", "last_name": "LaForge"},
                                            {"first_name": "Gabby", "last_name": "Levac"},
                                            {"first_name": "Chris", "last_name": "Perry"},
                                            {"first_name": "Melissa", "last_name": "White"},
                                            {"first_name": "Ivonna", "last_name": "Dumanyan"}]

                            },
            "weekly_insights": [
                                {
                                 "address_pain_soreness": [{"user_id": "1",
                                                           "first_name": "Dipesh",
                                                           "last_name": "Gautam",
                                                           "cleared_to_train": True,
                                                           "color": 0},
                                                           {"user_id": "3",
                                                            "first_name": "Paul",
                                                            "last_name": "LaForge",
                                                            "cleared_to_train": False,
                                                            "color": 2}
                                                          ],
                                 "increase_workload": [{"user_id": "2",
                                                        "first_name": "Mazen",
                                                        "last_name": "Chami",
                                                        "cleared_to_train": True,
                                                        "color": 1}
                                                      ],
                                 "balance_overtraining_risk": [{"user_id": "4",
                                                           "first_name": "Melissa",
                                                           "last_name": "White",
                                                           "cleared_to_train": False,
                                                           "color": 2}],
                                 "add_variety": []
                                }
                             ],
            "daily_insights": [
                                {
                                 "limit_time_intensity": [{"user_id": "1",
                                                           "first_name": "Dipesh",
                                                           "last_name": "Gautam",
                                                           "cleared_to_train": True,
                                                           "color": 1}
                                                          ],
                                 "increase_workload": [{"user_id": "2",
                                                        "first_name": "Mazen",
                                                        "last_name": "Chami",
                                                        "cleared_to_train": True,
                                                        "color": 1}
                                                      ],
                                 "monitor_training": [{"user_id": "3",
                                                       "first_name": "Paul",
                                                       "last_name": "LaForge",
                                                       "cleared_to_train": True,
                                                       "color": 1}],
                                 "not_cleared": [{"user_id": "7",
                                                  "first_name": "Ivonna",
                                                  "last_name": "Dumanyan",
                                                   "cleared_to_train": False,
                                                   "color": 2},
                                                 {"user_id": "4",
                                                  "first_name": "Melissa",
                                                  "last_name": "White",
                                                  "cleared_to_train": False,
                                                  "color": 2}],
                                 "all_good": [{"user_id": "5",
                                               "first_name": "Chris",
                                               "last_name": "Perry",
                                               "cleared_to_train": True,
                                               "color": 0},
                                              {"user_id": "6",
                                               "first_name": "Gabby",
                                               "last_name": "Levac",
                                               "cleared_to_train": True,
                                               "color": 0}
                                               ]
                                }
                              ],
            "athletes": [{"user_id": "1",
                          "first_name": "Dipesh",
                          "last_name": "Gautam",
                          "cleared_to_train": True,
                          "color": 1,
                          "weekly_recommendation": ["Consider decreasing weekly workload"],
                          "daily_recommendation": ["Increase variety in your training regimen", "Complete Prep"],
                          "insights": ["Workload increasing at a rate associated with a Moderate risk of injury", "Elevated hip pain which should be monitored to prevent injury"]},
                         {"user_id": "2",
                          "first_name": "Mazen",
                          "last_name": "Chami",
                          "cleared_to_train": True,
                          "color": 1,
                          "weekly_recommendation": ["Consider decreasing weekly workload"],
                          "daily_recommendation": ["Increase variety in your training regimen", "Complete Prep"],
                          "insights": ["Workload increasing at a rate associated with a Moderate risk of injury", "Elevated hip pain which should be monitored to prevent injury"]},
                         {"user_id": "3",
                          "first_name": "Paul",
                          "last_name": "LaForge",
                          "cleared_to_train": True,
                          "color": 1,
                          "weekly_recommendation": ["Consider decreasing weekly workload"],
                          "daily_recommendation": ["Increase variety in your training regimen", "Complete Prep"],
                          "insights": ["Workload increasing at a rate associated with a Moderate risk of injury", "Elevated hip pain which should be monitored to prevent injury"]},
                         {"user_id": "4",
                          "first_name": "Melissa",
                          "last_name": "White",
                          "cleared_to_train": False,
                          "color": 2,
                          "weekly_recommendation": [],
                          "daily_recommendation": [],
                          "insights": []},
                         {"user_id": "5",
                          "first_name": "Chris",
                          "last_name": "Perry",
                          "cleared_to_train": True,
                          "color": 0,
                          "weekly_recommendation": [],
                          "daily_recommendation": [],
                          "insights": []},
                         {"user_id": "6",
                          "first_name": "Gabby",
                          "last_name": "Levac",
                          "cleared_to_train": True,
                          "color": 0,
                          "weekly_recommendation": [],
                          "daily_recommendation": [],
                          "insights": []},
                         {"user_id": "7",
                          "first_name": "Ivonna",
                          "last_name": "Dumanyan",
                          "cleared_to_train": False,
                          "color": 2,
                          "weekly_recommendation": [],
                          "daily_recommendation": ["Considering not training today"],
                          "insights": ["Hip pain severity that is too high to train today and may indicate injury"]}
                        ]

                 }]

    return {'message': teams}, 200



def _get_teams(user_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"user/{user_id}")
    return response['user']['account_ids']


def _get_users_in_team(account_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"account/{account_id}")
    return response['account']['users']


def _get_user(user_id):
    response = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"user/{user_id}")
    return {"user_id": user_id,
            "first_name": response['user']['personal_data']['first_name'],
            "last_name": response['user']['personal_data']['first_name']}

