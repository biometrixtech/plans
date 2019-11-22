def extend_with_nones(existing_dict, number_of_nones):

    dict_length = len(existing_dict)

    for x in range(0, number_of_nones):
        existing_dict[dict_length + x] = None

    return existing_dict


def pre_pad_with_nones(existing_dict, total_days=35):
    if len(existing_dict) > total_days:
        raise ValueError('History is too long')
    elif len(existing_dict) == total_days:
        return existing_dict
    else:
        for x in range(0, total_days):
            existing_dict[x] = None

        return existing_dict


def create_elastticity_adf(history):
    return {
                "apt_ankle_pitch": {
                    "left": {
                        "elasticity": history["left_apt_ankle_pitch_elasticity"],
                        "y_adf": history["left_apt_ankle_pitch_y_adf"]
                    },
                    "right": {
                        "elasticity": history["right_apt_ankle_pitch_elasticity"],
                        "y_adf": history["right_apt_ankle_pitch_y_adf"]
                    }
                },
                "hip_drop_apt": {
                    "left": {
                        "elasticity": history["left_hip_drop_apt_elasticity"],
                        "y_adf": history["left_hip_drop_apt_y_adf"]
                    },
                    "right": {
                        "elasticity": history["right_hip_drop_apt_elasticity"],
                        "y_adf":  history["right_hip_drop_apt_y_adf"]
                    }
                },
                "hip_drop_pva": {
                    "left": {
                        "elasticity": history["left_hip_drop_pva_elasticity"],
                        "y_adf": history["left_hip_drop_pva_y_adf"]
                    },
                    "right": {
                        "elasticity": history["right_hip_drop_pva_elasticity"],
                        "y_adf":  history["right_hip_drop_pva_y_adf"]
                    }
                },
                "knee_valgus_hip_drop": {
                    "left": {
                        "elasticity": history["left_knee_valgus_hip_drop_elasticity"],
                        "y_adf": history["left_knee_valgus_hip_drop_y_adf"]
                    },
                    "right": {
                        "elasticity": history["right_knee_valgus_hip_drop_elasticity"],
                        "y_adf":  history["right_knee_valgus_hip_drop_y_adf"]
                    }
                },
                "knee_valgus_pva": {
                    "left": {
                        "elasticity": history["left_knee_valgus_pva_elasticity"],
                        "y_adf": history["left_knee_valgus_pva_y_adf"]
                    },
                    "right": {
                        "elasticity": history["right_knee_valgus_pva_elasticity"],
                        "y_adf":  history["right_knee_valgus_pva_y_adf"]
                    }
                },
                "knee_valgus_apt": {
                    "left": {
                        "elasticity": history["left_knee_valgus_apt_elasticity"],
                        "y_adf": history["left_knee_valgus_apt_y_adf"]
                    },
                    "right": {
                        "elasticity": history["right_knee_valgus_apt_elasticity"],
                        "y_adf":  history["right_knee_valgus_apt_y_adf"]
                    }
                }}


def run_fake_regressions_a():
    full_session_history = {}
    full_session_history = pre_pad_with_nones(full_session_history, 22)

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 22)
    n = 22

    history = {}
    history["left_apt_ankle_pitch_elasticity"] = 0.26862678142297
    history["left_apt_ankle_pitch_y_adf"] = -8.87018607908235
    history["right_apt_ankle_pitch_elasticity"] = 0.0
    history["right_apt_ankle_pitch_y_adf"] = -5.87247463469296

    history["left_hip_drop_apt_elasticity"] = -0.109925542103301
    history["left_hip_drop_apt_y_adf"] = 0.0
    history["right_hip_drop_apt_elasticity"] = -0.560416499724003
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = -0.0933318324347078
    history["left_hip_drop_pva_y_adf"] = 0.0
    history["right_hip_drop_pva_elasticity"] = -0.195678136071858
    history["right_hip_drop_pva_y_adf"] = 0.0

    history["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = -0.357556927181195
    history["right_knee_valgus_pva_y_adf"] = 0.0

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = 0.0
    history["right_knee_valgus_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 941
    session_details["session_id"] = '7bbff8e0-189a-5643-93bc-9730e0fdcd20'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n + 1] = None
    full_session_history[n + 1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = 0.7511842599502640
    history_2["left_apt_ankle_pitch_y_adf"] = -17.037490300922
    history_2["right_apt_ankle_pitch_elasticity"] = 0.0
    history_2["right_apt_ankle_pitch_y_adf"] = -3.76373127249762

    history_2["left_hip_drop_apt_elasticity"] = 0.0
    history_2["left_hip_drop_apt_y_adf"] = 0.0
    history_2["right_hip_drop_apt_elasticity"] = 0.293869832196777
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = 0.0798247205126612
    history_2["left_hip_drop_pva_y_adf"] = 0.0
    history_2["right_hip_drop_pva_elasticity"] = 0.0
    history_2["right_hip_drop_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_2["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_2["left_knee_valgus_pva_elasticity"] = 0.0
    history_2["left_knee_valgus_pva_y_adf"] = 0.0
    history_2["right_knee_valgus_pva_elasticity"] = 0.350647636838605
    history_2["right_knee_valgus_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_apt_elasticity"] = 0.0
    history_2["left_knee_valgus_apt_y_adf"] = 0.0
    history_2["right_knee_valgus_apt_elasticity"] = 0.211949329970997
    history_2["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_2 = {}
    session_details_2["seconds_duration"] = 1073
    session_details_2["session_id"] = '39f243c2-6baf-5558-a2df-4f051f88c06f'

    full_history[n + 2] = history_2
    full_session_history[n + 2] = session_details_2
    full_history[n + 3] = None
    full_session_history[n + 3] = None

    history_3 = {}
    history_3["left_apt_ankle_pitch_elasticity"] = 0.0405437554208033
    history_3["left_apt_ankle_pitch_y_adf"] = -9.39596330120844
    history_3["right_apt_ankle_pitch_elasticity"] = 0.227381329976232
    history_3["right_apt_ankle_pitch_y_adf"] = -6.0165804994854

    history_3["left_hip_drop_apt_elasticity"] = 0.182511298204295
    history_3["left_hip_drop_apt_y_adf"] = 0.0
    history_3["right_hip_drop_apt_elasticity"] = 0.192888729470617
    history_3["right_hip_drop_apt_y_adf"] = 0.0

    history_3["left_hip_drop_pva_elasticity"] = 0.083491795703273
    history_3["left_hip_drop_pva_y_adf"] = 0.0
    history_3["right_hip_drop_pva_elasticity"] = 0.0
    history_3["right_hip_drop_pva_y_adf"] = 0.0

    history_3["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_3["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_3["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history_3["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_3["left_knee_valgus_pva_elasticity"] = 0.0
    history_3["left_knee_valgus_pva_y_adf"] = 0.0
    history_3["right_knee_valgus_pva_elasticity"] = 0.0
    history_3["right_knee_valgus_pva_y_adf"] = 0.0

    history_3["left_knee_valgus_apt_elasticity"] = 0.0
    history_3["left_knee_valgus_apt_y_adf"] = 0.0
    history_3["right_knee_valgus_apt_elasticity"] = 0.171639396375845
    history_3["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_3 = {}
    session_details_3["seconds_duration"] = 8640
    session_details_3["session_id"] = 'c14f1728-b4f5-5fb4-845c-9dc830b3e9bf'

    full_history[n + 4] = history
    full_session_history[n + 4] = session_details_3

    full_history[n + 5] = None
    full_session_history[n + 5] = None

    history_4 = {}
    history_4["left_apt_ankle_pitch_elasticity"] = 0.7647161302258
    history_4["left_apt_ankle_pitch_y_adf"] = -6.29717390092538
    history_4["right_apt_ankle_pitch_elasticity"] = 0.71044788722549
    history_4["right_apt_ankle_pitch_y_adf"] = -6.20017183934644

    history_4["left_hip_drop_apt_elasticity"] = 0.0880329043655969
    history_4["left_hip_drop_apt_y_adf"] = 0.0
    history_4["right_hip_drop_apt_elasticity"] = 0.0669797704603473
    history_4["right_hip_drop_apt_y_adf"] = 0.0

    history_4["left_hip_drop_pva_elasticity"] = 0.0
    history_4["left_hip_drop_pva_y_adf"] = 0.0
    history_4["right_hip_drop_pva_elasticity"] = 0.0
    history_4["right_hip_drop_pva_y_adf"] = 0.0

    history_4["left_knee_valgus_hip_drop_elasticity"] = 0.00962908280374767
    history_4["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_4["right_knee_valgus_hip_drop_elasticity"] = 0.0538153795962701
    history_4["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_4["left_knee_valgus_pva_elasticity"] = 0.121025513699043
    history_4["left_knee_valgus_pva_y_adf"] = 0.0
    history_4["right_knee_valgus_pva_elasticity"] = 0.0
    history_4["right_knee_valgus_pva_y_adf"] = 0.0

    history_4["left_knee_valgus_apt_elasticity"] = 0.0425231654150508
    history_4["left_knee_valgus_apt_y_adf"] = 0.0
    history_4["right_knee_valgus_apt_elasticity"] = 0.0122256675077994
    history_4["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_4 = {}
    session_details_4["seconds_duration"] = 8166
    session_details_4["session_id"] = '958dba09-c338-5118-86a3-d20a559f09c2'

    full_history[n + 6] = history_4
    full_session_history[n + 6] = session_details_4
    
    full_history[n + 7] = None
    full_session_history[n + 7] = None

    history_5 = {}
    history_5["left_apt_ankle_pitch_elasticity"] = 0.08181299759617
    history_5["left_apt_ankle_pitch_y_adf"] = -3.10152770502242
    history_5["right_apt_ankle_pitch_elasticity"] = 0.78245291776496
    history_5["right_apt_ankle_pitch_y_adf"] = -3.19917420441908

    history_5["left_hip_drop_apt_elasticity"] = 0.178092796366487
    history_5["left_hip_drop_apt_y_adf"] = 0.0
    history_5["right_hip_drop_apt_elasticity"] = 0.0
    history_5["right_hip_drop_apt_y_adf"] = 0.0

    history_5["left_hip_drop_pva_elasticity"] = 0.0
    history_5["left_hip_drop_pva_y_adf"] = 0.0
    history_5["right_hip_drop_pva_elasticity"] = 0.0
    history_5["right_hip_drop_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_5["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_5["right_knee_valgus_hip_drop_elasticity"] = 0.144239542774656
    history_5["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_5["left_knee_valgus_pva_elasticity"] = 0.0
    history_5["left_knee_valgus_pva_y_adf"] = 0.0
    history_5["right_knee_valgus_pva_elasticity"] = 0.0
    history_5["right_knee_valgus_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_apt_elasticity"] = 0.133339194910961
    history_5["left_knee_valgus_apt_y_adf"] = 0.0
    history_5["right_knee_valgus_apt_elasticity"] = 0.159290632566094
    history_5["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_5 = {}
    session_details_5["seconds_duration"] = 243
    session_details_5["session_id"] = 'f93e004d-7dd0-56b3-bb22-353750586f5e'

    full_history[n + 8] = history_5
    full_session_history[n + 8] = session_details_5
    full_history[n + 9] = None
    full_session_history[n + 9] = None

    history_6 = {}
    history_6["left_apt_ankle_pitch_elasticity"] = 0.429038632704596
    history_6["left_apt_ankle_pitch_y_adf"] = -6.60672795200826
    history_6["right_apt_ankle_pitch_elasticity"] = 0.0
    history_6["right_apt_ankle_pitch_y_adf"] = -3.19917420441908

    history_6["left_hip_drop_apt_elasticity"] = 0.0
    history_6["left_hip_drop_apt_y_adf"] = 0.0
    history_6["right_hip_drop_apt_elasticity"] = 0.058083362051412
    history_6["right_hip_drop_apt_y_adf"] = 0.0

    history_6["left_hip_drop_pva_elasticity"] = 0.229877359561652
    history_6["left_hip_drop_pva_y_adf"] = 0.0
    history_6["right_hip_drop_pva_elasticity"] = 0.0870156440654099
    history_6["right_hip_drop_pva_y_adf"] = 0.0

    history_6["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_6["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_6["right_knee_valgus_hip_drop_elasticity"] = 0.126430147448765
    history_6["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_6["left_knee_valgus_pva_elasticity"] = 0.0
    history_6["left_knee_valgus_pva_y_adf"] = 0.0
    history_6["right_knee_valgus_pva_elasticity"] = 0.0
    history_6["right_knee_valgus_pva_y_adf"] = 0.0

    history_6["left_knee_valgus_apt_elasticity"] = 0.0431147083237144
    history_6["left_knee_valgus_apt_y_adf"] = 0.0
    history_6["right_knee_valgus_apt_elasticity"] = 0.0768290349343447
    history_6["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_6 = {}
    session_details_6["seconds_duration"] = 1495
    session_details_6["session_id"] = 'f78a9e26-6003-5ac7-8590-3ae4a421dac7'

    full_history[n + 10] = history_6
    full_session_history[n + 10] = session_details_6
    full_history[n + 11] = None
    full_session_history[n + 11] = None
    
    history_7 = {}
    history_7["left_apt_ankle_pitch_elasticity"] = 0.429038632704596
    history_7["left_apt_ankle_pitch_y_adf"] = -6.60672795200826
    history_7["right_apt_ankle_pitch_elasticity"] = 0.0
    history_7["right_apt_ankle_pitch_y_adf"] = -3.19917420441908

    history_7["left_hip_drop_apt_elasticity"] = 0.0
    history_7["left_hip_drop_apt_y_adf"] = 0.0
    history_7["right_hip_drop_apt_elasticity"] = 0.058083362051412
    history_7["right_hip_drop_apt_y_adf"] = 0.0

    history_7["left_hip_drop_pva_elasticity"] = 0.229877359561652
    history_7["left_hip_drop_pva_y_adf"] = 0.0
    history_7["right_hip_drop_pva_elasticity"] = 0.0870156440654099
    history_7["right_hip_drop_pva_y_adf"] = 0.0

    history_7["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_7["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_7["right_knee_valgus_hip_drop_elasticity"] = 0.126430147448765
    history_7["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_7["left_knee_valgus_pva_elasticity"] = 0.0
    history_7["left_knee_valgus_pva_y_adf"] = 0.0
    history_7["right_knee_valgus_pva_elasticity"] = 0.0
    history_7["right_knee_valgus_pva_y_adf"] = 0.0

    history_7["left_knee_valgus_apt_elasticity"] = 0.0431147083237144
    history_7["left_knee_valgus_apt_y_adf"] = 0.0
    history_7["right_knee_valgus_apt_elasticity"] = 0.0768290349343447
    history_7["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_7 = {}
    session_details_7["seconds_duration"] = 242
    session_details_7["session_id"] = '2f26eee8-455a-5678-a384-ed5a14c6e54a'

    full_history[n + 12] = history_7
    full_session_history[n + 12] = session_details_7

    return full_history, full_session_history


def run_a_regressions():

    full_session_history = {}
    full_session_history = pre_pad_with_nones(full_session_history, 32)

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 32)
    n = 32

    history = {}
    history["left_apt_ankle_pitch_elasticity"] = 0.26862678142297
    history["left_apt_ankle_pitch_y_adf"] = -8.87018607908235
    history["right_apt_ankle_pitch_elasticity"] = 0.0
    history["right_apt_ankle_pitch_y_adf"] = -5.87247463469296

    history["left_hip_drop_apt_elasticity"] = -0.109925542103301
    history["left_hip_drop_apt_y_adf"] = 0.0
    history["right_hip_drop_apt_elasticity"] = -0.560416499724003
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = -0.0933318324347078
    history["left_hip_drop_pva_y_adf"] = 0.0
    history["right_hip_drop_pva_elasticity"] = -0.195678136071858
    history["right_hip_drop_pva_y_adf"] = 0.0

    history["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = -0.357556927181195
    history["right_knee_valgus_pva_y_adf"] = 0.0

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = 0.0
    history["right_knee_valgus_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 941
    session_details["session_id"] = '7bbff8e0-189a-5643-93bc-9730e0fdcd20'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n+1] = None
    full_session_history[n+1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = 0.0
    history_2["left_apt_ankle_pitch_y_adf"] = -17.037490300922
    history_2["right_apt_ankle_pitch_elasticity"] = 0.7511842599502640
    history_2["right_apt_ankle_pitch_y_adf"] = -3.76373127249762

    history_2["left_hip_drop_apt_elasticity"] = 0.0
    history_2["left_hip_drop_apt_y_adf"] = 0.0
    history_2["right_hip_drop_apt_elasticity"] = -0.293869832196777
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = 0.0798247205126612
    history_2["left_hip_drop_pva_y_adf"] = 0.0
    history_2["right_hip_drop_pva_elasticity"] = 0.0
    history_2["right_hip_drop_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_2["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_2["left_knee_valgus_pva_elasticity"] = 0.0
    history_2["left_knee_valgus_pva_y_adf"] = 0.0
    history_2["right_knee_valgus_pva_elasticity"] = -0.350647636838605
    history_2["right_knee_valgus_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_apt_elasticity"] = 0.0
    history_2["left_knee_valgus_apt_y_adf"] = 0.0
    history_2["right_knee_valgus_apt_elasticity"] = -0.211949329970997
    history_2["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_2 = {}
    session_details_2["seconds_duration"] = 1073
    session_details_2["session_id"] = '39f243c2-6baf-5558-a2df-4f051f88c06f'

    full_history[n+2] = history_2
    full_session_history[n+2] = session_details_2

    return full_history, full_session_history


def long_regressions():

    full_session_history = {}
    full_session_history = pre_pad_with_nones(full_session_history, 32)

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 32)
    n = 32

    history = {}
    history["left_apt_ankle_pitch_elasticity"] = 0.0405437554208033
    history["left_apt_ankle_pitch_y_adf"] = -9.39596330120844
    history["right_apt_ankle_pitch_elasticity"] = 0.227381329976232
    history["right_apt_ankle_pitch_y_adf"] =-6.0165804994854

    history["left_hip_drop_apt_elasticity"] = 0.182511298204295
    history["left_hip_drop_apt_y_adf"] = 0.0
    history["right_hip_drop_apt_elasticity"] = 0.192888729470617
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = 0.083491795703273
    history["left_hip_drop_pva_y_adf"] = 0.0
    history["right_hip_drop_pva_elasticity"] = 0.0
    history["right_hip_drop_pva_y_adf"] = 0.0

    history["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = 0.0
    history["right_knee_valgus_pva_y_adf"] = 0.0

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = -0.171639396375845
    history["right_knee_valgus_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 8640
    session_details["session_id"] = 'c14f1728-b4f5-5fb4-845c-9dc830b3e9bf'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n+1] = None
    full_session_history[n+1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = -3.7647161302258
    history_2["left_apt_ankle_pitch_y_adf"] = -6.29717390092538
    history_2["right_apt_ankle_pitch_elasticity"] = -1.71044788722549
    history_2["right_apt_ankle_pitch_y_adf"] = -6.20017183934644

    history_2["left_hip_drop_apt_elasticity"] = -0.0880329043655969
    history_2["left_hip_drop_apt_y_adf"] = 0.0
    history_2["right_hip_drop_apt_elasticity"] = 0.0669797704603473
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = 0.0
    history_2["left_hip_drop_pva_y_adf"] = 0.0
    history_2["right_hip_drop_pva_elasticity"] = 0.0
    history_2["right_hip_drop_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_hip_drop_elasticity"] = 0.00962908280374767
    history_2["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_2["right_knee_valgus_hip_drop_elasticity"] = -0.0538153795962701
    history_2["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_2["left_knee_valgus_pva_elasticity"] = 0.121025513699043
    history_2["left_knee_valgus_pva_y_adf"] = 0.0
    history_2["right_knee_valgus_pva_elasticity"] = 0.0
    history_2["right_knee_valgus_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_apt_elasticity"] = 0.0425231654150508
    history_2["left_knee_valgus_apt_y_adf"] = 0.0
    history_2["right_knee_valgus_apt_elasticity"] = 0.0122256675077994
    history_2["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_2 = {}
    session_details_2["seconds_duration"] = 8166
    session_details_2["session_id"] = '958dba09-c338-5118-86a3-d20a559f09c2'

    full_history[n+2] = history_2
    full_session_history[n+2] = session_details_2

    return full_history, full_session_history

def tread_regressions():

    full_session_history = {}
    full_session_history = pre_pad_with_nones(full_session_history, 26)

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 26)
    n = 26

    history = {}
    history["left_apt_ankle_pitch_elasticity"] = 0.0
    history["left_apt_ankle_pitch_y_adf"] = -4.88759012994597
    history["right_apt_ankle_pitch_elasticity"] = 0.0
    history["right_apt_ankle_pitch_y_adf"] = 0.0

    history["left_hip_drop_apt_elasticity"] = 0.0
    history["left_hip_drop_apt_y_adf"] = 0.0
    history["right_hip_drop_apt_elasticity"] = 0.0
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = 0.0
    history["left_hip_drop_pva_y_adf"] = 0.0
    history["right_hip_drop_pva_elasticity"] = 0.0
    history["right_hip_drop_pva_y_adf"] = 0.0

    history["left_knee_valgus_hip_drop_elasticity"] = 0.303545853437089
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0745365137141311
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = 0.0
    history["right_knee_valgus_pva_y_adf"] = 0.0

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = 0.0
    history["right_knee_valgus_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 243
    session_details["session_id"] = '07b9b744-3e85-563d-b69a-822148673f58'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n+1] = None
    full_session_history[n+1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = 0.0
    history_2["left_apt_ankle_pitch_y_adf"] = 0.0
    history_2["right_apt_ankle_pitch_elasticity"] = 0.0
    history_2["right_apt_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_drop_apt_elasticity"] = 0.0
    history_2["left_hip_drop_apt_y_adf"] = 0.0
    history_2["right_hip_drop_apt_elasticity"] = 0.0
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = 0.0
    history_2["left_hip_drop_pva_y_adf"] = 0.0
    history_2["right_hip_drop_pva_elasticity"] = 0.0
    history_2["right_hip_drop_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_2["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_2["left_knee_valgus_pva_elasticity"] = 0.0
    history_2["left_knee_valgus_pva_y_adf"] = 0.0
    history_2["right_knee_valgus_pva_elasticity"] = 0.0
    history_2["right_knee_valgus_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_apt_elasticity"] = 0.0
    history_2["left_knee_valgus_apt_y_adf"] = 0.0
    history_2["right_knee_valgus_apt_elasticity"] = 0.0
    history_2["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_2 = {}
    session_details_2["seconds_duration"] = 177
    session_details_2["session_id"] = '398ad5bf-3792-5b63-b07f-60a1e6bda875'

    full_history[n+2] = history_2
    full_session_history[n+2] = session_details_2
    full_history[n+3] = None
    full_session_history[n+3] = None
    
    history_3 = {}
    history_3["left_apt_ankle_pitch_elasticity"] = 0.0
    history_3["left_apt_ankle_pitch_y_adf"] = 0.0
    history_3["right_apt_ankle_pitch_elasticity"] = 0.0
    history_3["right_apt_ankle_pitch_y_adf"] = 0.0

    history_3["left_hip_drop_apt_elasticity"] = 0.0
    history_3["left_hip_drop_apt_y_adf"] = 0.0
    history_3["right_hip_drop_apt_elasticity"] = 0.0
    history_3["right_hip_drop_apt_y_adf"] = 0.0

    history_3["left_hip_drop_pva_elasticity"] = 0.0
    history_3["left_hip_drop_pva_y_adf"] = 0.0
    history_3["right_hip_drop_pva_elasticity"] = 0.0
    history_3["right_hip_drop_pva_y_adf"] = 0.0

    history_3["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_3["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_3["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history_3["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_3["left_knee_valgus_pva_elasticity"] = 0.0
    history_3["left_knee_valgus_pva_y_adf"] = 0.0
    history_3["right_knee_valgus_pva_elasticity"] = 0.0
    history_3["right_knee_valgus_pva_y_adf"] = 0.0

    history_3["left_knee_valgus_apt_elasticity"] = 0.0
    history_3["left_knee_valgus_apt_y_adf"] = 0.0
    history_3["right_knee_valgus_apt_elasticity"] = 0.0
    history_3["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_3 = {}
    session_details_3["seconds_duration"] = 242
    session_details_3["session_id"] = '2f26eee8-455a-5678-a384-ed5a14c6e54a'

    full_history[n+4] = history_3
    full_session_history[n+4] = session_details_3
    full_history[n+5] = None
    full_session_history[n+5] = None
    
    history_4 = {}
    history_4["left_apt_ankle_pitch_elasticity"] = -1.08181299759617
    history_4["left_apt_ankle_pitch_y_adf"] = -3.10152770502242
    history_4["right_apt_ankle_pitch_elasticity"] = -1.78245291776496
    history_4["right_apt_ankle_pitch_y_adf"] = -3.19917420441908

    history_4["left_hip_drop_apt_elasticity"] = 0.178092796366487
    history_4["left_hip_drop_apt_y_adf"] = 0.0
    history_4["right_hip_drop_apt_elasticity"] = 0.0
    history_4["right_hip_drop_apt_y_adf"] = 0.0

    history_4["left_hip_drop_pva_elasticity"] = 0.0
    history_4["left_hip_drop_pva_y_adf"] = 0.0
    history_4["right_hip_drop_pva_elasticity"] = 0.0
    history_4["right_hip_drop_pva_y_adf"] = 0.0

    history_4["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_4["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_4["right_knee_valgus_hip_drop_elasticity"] = 0.144239542774656
    history_4["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_4["left_knee_valgus_pva_elasticity"] = 0.0
    history_4["left_knee_valgus_pva_y_adf"] = 0.0
    history_4["right_knee_valgus_pva_elasticity"] = 0.0
    history_4["right_knee_valgus_pva_y_adf"] = 0.0

    history_4["left_knee_valgus_apt_elasticity"] = -0.133339194910961
    history_4["left_knee_valgus_apt_y_adf"] = 0.0
    history_4["right_knee_valgus_apt_elasticity"] = -0.159290632566094
    history_4["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_4 = {}
    session_details_4["seconds_duration"] = 243
    session_details_4["session_id"] = 'f93e004d-7dd0-56b3-bb22-353750586f5e'

    full_history[n+6] = history_4
    full_session_history[n+6] = session_details_4
    full_history[n+7] = None
    full_session_history[n+7] = None
    
    history_5 = {}
    history_5["left_apt_ankle_pitch_elasticity"] = -0.429038632704596
    history_5["left_apt_ankle_pitch_y_adf"] = -6.60672795200826
    history_5["right_apt_ankle_pitch_elasticity"] = 0.0
    history_5["right_apt_ankle_pitch_y_adf"] = -3.19917420441908

    history_5["left_hip_drop_apt_elasticity"] = 0.0
    history_5["left_hip_drop_apt_y_adf"] = 0.0
    history_5["right_hip_drop_apt_elasticity"] = -0.058083362051412
    history_5["right_hip_drop_apt_y_adf"] = 0.0

    history_5["left_hip_drop_pva_elasticity"] = -0.229877359561652
    history_5["left_hip_drop_pva_y_adf"] = 0.0
    history_5["right_hip_drop_pva_elasticity"] = -0.0870156440654099
    history_5["right_hip_drop_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_5["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_5["right_knee_valgus_hip_drop_elasticity"] = 0.126430147448765
    history_5["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_5["left_knee_valgus_pva_elasticity"] = 0.0
    history_5["left_knee_valgus_pva_y_adf"] = 0.0
    history_5["right_knee_valgus_pva_elasticity"] = 0.0
    history_5["right_knee_valgus_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_apt_elasticity"] = -0.0431147083237144
    history_5["left_knee_valgus_apt_y_adf"] = 0.0
    history_5["right_knee_valgus_apt_elasticity"] = -0.0768290349343447
    history_5["right_knee_valgus_apt_y_adf"] = 0.0

    session_details_5 = {}
    session_details_5["seconds_duration"] = 1495
    session_details_5["session_id"] = 'f78a9e26-6003-5ac7-8590-3ae4a421dac7'

    full_history[n + 8] = history_5
    full_session_history[n + 8] = session_details_5

    return full_history, full_session_history