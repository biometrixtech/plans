domain = "@200.com"

users = [
    # "full_fte",
    # "sore_fte",
    # "near_clear",
    #"two_sore",
    "two_pain"
]

def get_test_users():

    user_list = []

    for u in users:
        email = u + domain
        user_list.append(email)

    return user_list