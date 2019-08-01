domain = "@200.com"

users = [
    #"full_fte",
    # "sore_fte",
    # "near_clear",
    # "two_sore",
    "two_pain",
    #"full_fte_2",
    # "sore_fte_2",
    # "near_clear_2",
    # "two_sore_2",
    "two_pain_2"
]

def get_test_users():

    user_list = []

    for u in users:
        email = u + domain
        user_list.append(email)

    return user_list