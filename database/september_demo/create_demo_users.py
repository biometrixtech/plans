import requests
import json
from database.september_demo.demo_users import get_users

headers = {"dev": {"Content-Type": "application/json"},
           "test": {"Content-Type": "application/json"},
           "production": {"Content-Type": "application/json"}
           }


def create_user(email, first_name, last_name, env="dev"):
    endpoint = "https://apis.{env}.fathomai.com/users/2_4/user".format(env=env)

    onboarding_status = [
        "survey-questions",
        "coach-tutorial",
        "account_setup"
    ]
    first_time_experience = [
        "all_good_body_part_tooltip",
        "active_time_tooltip",
        "exercise_description_tooltip",
        "soreness_pain_tooltip"
    ]
    body = {"personal_data": {"email": email,
                              "first_name": first_name,
                              "last_name": last_name,
                              "birth_date": "01/01/1990"
                              },
            "biometric_data": {
                "mass": {
                    "kg": 76.203
                }},
            "plans_api_version": "latest",
            #            "account_code": code,
            "first_time_experience": first_time_experience,
            "onboarding_status": onboarding_status,
            "password": "Fathom123!"}
    global headers
    response = requests.post(endpoint, data=json.dumps(body), headers=headers[env])

    return response.status_code


users = get_users()

environment = "dev"

for user in users:

    first_name = user
    last_name = "user"
    email = user + "@300.com"

    status_code = create_user(email, first_name, last_name, environment)
    print(status_code)