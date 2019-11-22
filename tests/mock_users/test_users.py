domain = "@200.com"

users = [

    #"full_fte", #6a91a0cb-2c90-4b93-94d2-a943c6284af7
    #"sore_fte",
    #"near_clear",
    #"two_sore",
    #"two_pain", #c82d4f18-efba-421e-b28f-bab349ebd3c1
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
    # "tread_a", #6fc48b46-23c8-4490-9885-e109ff63c20e
    #"tread_b", #4673998d-5206-4275-a048-da5dda6a7342
    #"tread_run", #bdb8b194-e748-4197-819b-b356f1fb0629
    #"run_a", #2b4a1792-42c7-460e-9e4c-98627e72cc6f
    # "sym", #7fd0c1d4-61ac-4ce5-9621-16d69501b211
    # "half_sym", #7cf2f832-a043-468c-8f61-13d07765d2a2
    #"run_a_2", #5c695e58-0aba-4eec-9af1-fa93970d3132
    # "sym_2" #aa1534d0-4abd-41c0-9b84-4e414b3d86d4
    # "long_3s", #928f64b5-a761-4278-8724-95a908499fae
    # "run_a_3",  #9e90e3ef-c6e0-4e2d-a430-a52f1e61a962
    # "sym_3",  #34b47309-7ad5-4222-b865-0f825680541e
    #"tread_a_2", #441a296a-6d37-4de3-ba04-bd725da05613
    # "tread_b_2", #e72bfb85-9c66-4cbe-8a77-20e5eda0a793
    # "tread_run_2", #4c8792b2-d5e2-475b-b55d-c16e70dc47aa
    # "long_3s_2", #06a112b3-b07f-4da7-a6bb-16558c5345ea
    # "half_sym_2", #d81af04a-385e-4a43-ad95-63222549ecc4
    #"run_a_mazen", #110e14e6-8630-48e8-b75d-0caad447d661
    #"tread_run_2_mazen", #23e93c04-c7cc-40b3-8e34-e43a9cab286a
    #"tread_b_mazen", #1569f9bb-6de3-49a9-913c-f69d7d763d25
]

merged_users = [
    "nc_long",  #7bb3e792-41ff-43cb-861e-87cf2bdeeadf
    # "nc_sore_tread",  #917e94bc-3f56-4519-8d25-ae54878748f2
    # "ts_pain_long", #e602620d-2040-4ecc-87cc-f392d9db5eab
    # "ts_tread",  #18ad5cde-92a8-4cd4-8295-71a91c7d3aac
    # # "two_pain_tread", #25c38e39-357a-456d-84b7-61547364a2ba
    # "full_fte_long", #024a6807-eef6-4556-b3b8-1c8639dd1758
    # "full_fte_tread", #33293741-bf30-479e-83e9-bc6b3a1cb7c2
    # "nc_long_2",  #8f6ff382-9314-43d2-9bb5-54bd8416a682
    # "nc_sore_tread_2",  #3f4bd8a2-c76b-4296-8c75-7302c31468c2
    # "ts_pain_long_2",  #5dd7a148-1c0e-4ddf-a1b1-020a99347069
    # "ts_tread_2",  #93b7a075-8168-4fad-961f-cfebdee392fc
    # # # "two_pain_tread_2",  #84a5e6fd-19f2-44ed-8bbd-ed2c03769ecf
    #"full_fte_long_2",  #24882bdf-69df-4043-b832-74d6c1f7052c
    #"full_fte_tread_2",  #703b5309-78cd-46b1-82ec-45e86b6d71de

    # production only
    # "ivonna+demo1@fathomai.com",#82b1450c-9487-4573-86f7-a0dfeb612774
    # "ivonna+demo2@fathomai.com",#9c2477e8-6113-44cc-b31e-cae950ede76e

    #merged dev
    #7ac23cc0-2c04-4b33-b3d4-cfebbcc787ef
    #a8359749-5c2f-48f2-aeec-40d2a9285d8d
    #ae511bd4-7d41-4a62-9913-e617bf424632
    #92eb7de1-709f-4af5-8b3f-d0973d5b8a43
    #87a42219-aafa-4d82-a598-143ed5440140
    #0d4a193e-8dfb-44e3-b676-47d22f19a0b6
    #bfc006e8-9ad8-412f-94e0-089715e2ea57
    #45a6351c-d9a8-44b6-8e98-cc4754ce9b56
    #6fc1b032-67b6-4436-86ae-3f0e94493b22
    #102017ae-3a2e-4477-9cc6-6d1745ba6b3b
    #0676696d-709f-4a59-8301-62e1d3aa130e
    #214e0ed9-172c-4d94-8c94-1e34ed9eb141
    #"full_fte_long_2", #4b2f895e-a3b6-43b9-86b5-5cfc26190caa
    #f0bc5f88-2909-4f88-b839-5fbfcbeb8f0b
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

def get_merged_users():

    user_list = []

    for u in merged_users:
        if "@" not in u:
            email = u + domain
        else:
            email = u
        user_list.append(email)

    return user_list