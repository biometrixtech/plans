domain = "@200.com"

users = [
    #"full_fte", #6a91a0cb-2c90-4b93-94d2-a943c6284af7
    #"sore_fte",
    # "near_clear",
    #"two_sore",
    #"two_pain",
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

three_sensor_users = [
    #"tread_a", #6fc48b46-23c8-4490-9885-e109ff63c20e
    #"tread_b", #4673998d-5206-4275-a048-da5dda6a7342
    #"tread_run", #bdb8b194-e748-4197-819b-b356f1fb0629
    "run_a", #2b4a1792-42c7-460e-9e4c-98627e72cc6f
    "sym" #7fd0c1d4-61ac-4ce5-9621-16d69501b211
    #"half_sym" #7cf2f832-a043-468c-8f61-13d07765d2a2
]

def get_test_users():

    user_list = []

    for u in users:
        email = u + domain
        user_list.append(email)

    return user_list


def get_three_sensor_test_users():

    user_list = []

    for u in three_sensor_users:
        email = u + domain
        user_list.append(email)

    return user_list