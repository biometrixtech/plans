import requests
import json
import test_users

headers = {"dev": {"Content-Type": "application/json"},
           "test": {"Content-Type": "application/json"},
           "production": {"Content-Type": "application/json"}
           }


def create_user(email, first_name, last_name, env="dev"):
    endpoint = "http://apis.{env}.fathomai.com/users/2_3/user".format(env=env)

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
                              "birth_date": "01/01/2006"
                              },
            #            "account_code": code,
            "first_time_experience": first_time_experience,
            "onboarding_status": onboarding_status,
            "password": "Fathom123!"}
    global headers
    response = requests.post(endpoint, data=json.dumps(body), headers=headers[env])

    return response.status_code


users = test_users.get_test_users()
users.extend(test_users.get_three_sensor_test_users())
users.extend(test_users.get_merged_users())

environment = "dev"

for user in users:

    first_name = "test"
    last_name = "tester"

    status_code = create_user(user, first_name, last_name, environment)
    print(status_code)
