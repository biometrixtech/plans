domain = "@200.com"

users = [
    #"full_fte", #6a91a0cb-2c90-4b93-94d2-a943c6284af7
    #"sore_fte",
    # "near_clear",
    # "two_sore",
    "two_pain",
    #"full_fte_2",
    # "sore_fte_2",
    #"near_clear_2",
    # "two_sore_2",
    #"two_pain_2", #c82d4f18-efba-421e-b28f-bab349ebd3c1
    #"pain_sore", #d295beff-701c-448b-9e17-a5aba60b1e36,
    #"three_pain", #8cc57568-073f-4aeb-9ae2-4bb7c39297a1
    #"pain_sore_2",
    #"three_pain_2",
]

def get_test_users():

    user_list = []

    for u in users:
        email = u + domain
        user_list.append(email)

    return user_list