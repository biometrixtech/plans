from fathomapi.api.config import Config
from fathomapi.comms.service import Service
from fathomapi.utils.decorators import require
from fathomapi.utils.xray import xray_recorder
from fathomapi.utils.exceptions import NoSuchEntityException
from flask import Blueprint, request
from datastores.datastore_collection import DatastoreCollection
from serialisable import json_serialise
from utils import parse_date, parse_datetime, format_date, format_datetime
import boto3
import json
import os
import datetime
import random


app = Blueprint('coach', __name__)
USERS_API_VERSION = '2_0'


@app.route('/<uuid:user_id>/dashboard', methods=['GET'])
@require.authenticated.any
@xray_recorder.capture('routes.team.dashboard.get')
def get_dashboard_data(user_id):
    # team_ids = _get_teams(user_id)

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
                                {"cleared_to_play": {
                                                     "address_pain_soreness": [{"user_id": "1",
                                                                               "first_name": "Dipesh",
                                                                               "last_name": "Gautam"}
                                                                              ],
                                                     "increase_workload": [{"user_id": "2",
                                                                            "first_name": "Mazen",
                                                                            "last_name": "Chami"}
                                                                          ],
                                                     "balance_overtraining_risk": [],
                                                     "add_variety": [],
                                                     "reevaluate_training": []
                                                    }
                                },
                                {"not_cleared_to_play": {
                                                         "address_pain_soreness": [{"user_id": "3",
                                                                                    "first_name": "Paul",
                                                                                    "last_name": "LaForge"}
                                                                                  ],
                                                         "increase_workload": [{"user_id": "4",
                                                                               "first_name": "Melissa",
                                                                               "last_name": "White"}
                                                                              ],
                                                         "balance_overtraining_risk": [],
                                                         "add_variety": [],
                                                         "reevaluate_training": []
                                                        }

                                }
                             ],
            "daily_insights": [
                                {"cleared_to_play": {
                                                     "limit_time_intensity": [{"user_id": "1",
                                                                               "first_name": "Dipesh",
                                                                               "last_name": "Gautam"}
                                                                              ],
                                                     "increase_workload": [{"user_id": "2",
                                                                            "first_name": "Mazen",
                                                                            "last_name": "Chami"}
                                                                          ],
                                                     "monitor_training": [],
                                                     "not_cleared": [],
                                                     "all_good": [{"user_id": "5",
                                                                   "first_name": "Mazen",
                                                                   "last_name": "Chami"},
                                                                  {"user_id": "6",
                                                                   "first_name": "Gabby",
                                                                   "last_name": "Levac"}
                                                                   ]
                                                    }
                                },
                                {"not_cleared_to_play": {
                                                         "limit_time_intensity": [{"user_id": "3",
                                                                                   "first_name": "Paul",
                                                                                   "last_name": "LaForge"}
                                                                                  ],
                                                         "increase_workload": [{"user_id": "4",
                                                                               "first_name": "Melissa",
                                                                               "last_name": "White"}
                                                                              ],
                                                         "monitor_training": [],
                                                         "not_cleared": [{"user_id": "7",
                                                                          "first_name": "Ivonna",
                                                                          "last_name": "Dumanyan"}],
                                                         "all_good": []
                                                        }

                                }
                              ],
            "athletes": [{"user_id": 1},
                         {"user_id": 2},
                         {"user_id": 3},
                         {"user_id": 4},
                         {"user_id": 5},
                         {"user_id": 6},
                         {"user_id": 7}]

                 }]

    return {'message': teams}, 200



def _get_teams(user_id):
    user = Service('users', USERS_API_VERSION).call_apigateway_sync('GET', f"user/{user_id}")
    print(user)
    # teams = json.loads


