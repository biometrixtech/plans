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


def create_asymmetry(history):

    apt_history = history["apt"]
    ankle_pitch_history = history["ankle_pitch"]
    hip_drop_history = history["hip_drop"]
    knee_valgus_history = history["knee_valgus"]
    hip_rotation_history = history["hip_rotation"]

    return {
        "apt": {
            "left": apt_history["left"],
            "right": apt_history["right"],
            "asymmetric_events": apt_history["asymmetric_events"],
            "symmetric_events": apt_history["symmetric_events"],
            "percent_events_asymmetric": apt_history["percent_events_asymmetric"]
        },
        "ankle_pitch": {
            "left": ankle_pitch_history["left"],
            "right": ankle_pitch_history["right"],
            "asymmetric_events": ankle_pitch_history["asymmetric_events"],
            "symmetric_events": ankle_pitch_history["symmetric_events"],
            "percent_events_asymmetric": ankle_pitch_history["percent_events_asymmetric"]
        },
        "hip_drop": {
            "left": hip_drop_history["left"],
            "right": hip_drop_history["right"],
            "asymmetric_events": hip_drop_history["asymmetric_events"],
            "symmetric_events": hip_drop_history["symmetric_events"],
            "percent_events_asymmetric": hip_drop_history["percent_events_asymmetric"]
        },
        "knee_valgus": {
            "left": knee_valgus_history["left"],
            "right": knee_valgus_history["right"],
            "asymmetric_events": knee_valgus_history["asymmetric_events"],
            "symmetric_events": knee_valgus_history["symmetric_events"],
            "percent_events_asymmetric": knee_valgus_history["percent_events_asymmetric"]
        },
        "hip_rotation": {
            "left": hip_rotation_history["left"],
            "right": hip_rotation_history["right"],
            "asymmetric_events": hip_rotation_history["asymmetric_events"],
            "symmetric_events": hip_rotation_history["symmetric_events"],
            "percent_events_asymmetric": hip_rotation_history["percent_events_asymmetric"]
        }
    }


def create_elasticity_adf(history):
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
                },
                "hip_rotation_ankle_pitch": {
                    "left": {
                        "elasticity": history["left_hip_rotation_ankle_pitch_elasticity"],
                        "y_adf": history["left_hip_rotation_ankle_pitch_y_adf"]
                    },
                    "right": {
                        "elasticity": history["right_hip_rotation_ankle_pitch_elasticity"],
                        "y_adf":  history["right_hip_rotation_ankle_pitch_y_adf"]
                    }
                },
                "hip_rotation_apt": {
                    "left": {
                        "elasticity": history["left_hip_rotation_apt_elasticity"],
                        "y_adf": history["left_hip_rotation_apt_y_adf"]
                    },
                    "right": {
                        "elasticity": history["right_hip_rotation_apt_elasticity"],
                        "y_adf":  history["right_hip_rotation_apt_y_adf"]
                    }
                }}


def get_asymmetry_dict(left, right, asymmetric_events, symmetric_events, percent_events_asymmetric):

    dict = {}
    dict["left"] = left
    dict["right"] = right
    dict["asymmetric_events"] = asymmetric_events
    dict["symmetric_events"] = symmetric_events
    dict["percent_events_asymmetric"] = percent_events_asymmetric

    return dict


def get_asymmetry_a():

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 32)
    n = 32

    # session 39f243c2-6baf-5558-a2df-4f051f88c06f
    asymmetry = {}
    asymmetry["apt"] = get_asymmetry_dict(10.54, 9.44, 9, 20, 31)
    asymmetry["ankle_pitch"] = get_asymmetry_dict(93.105, 95.3, 11, 17, 39)
    asymmetry["hip_drop"] = get_asymmetry_dict(6.43, 2.89, 29, 0, 100)
    asymmetry["knee_valgus"] = get_asymmetry_dict(3.62, 1.22, 16, 13, 55)
    asymmetry["hip_rotation"] = get_asymmetry_dict(1.27, 2.15, 23, 6, 79)

    full_history[n] = asymmetry
    full_history[n + 1] = None

    # session 7bbff8e0-189a-5643-93bc-9730e0fdcd20
    asymmetry_2 = {}
    asymmetry_2["apt"] = get_asymmetry_dict(10.4575, 7.36, 32, 0, 100)
    asymmetry_2["ankle_pitch"] = get_asymmetry_dict(93.6725, 89.265, 26, 6, 81)
    asymmetry_2["hip_drop"] = get_asymmetry_dict(6.065, 5.8375, 0, 32, 0)
    asymmetry_2["knee_valgus"] = get_asymmetry_dict(2.78, 5.3775, 32, 0, 100)
    asymmetry_2["hip_rotation"] = get_asymmetry_dict(1.125, 2.1525, 32, 0, 100)

    full_history[n + 2] = asymmetry_2

    return full_history

def get_asymmetry_long():

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 32)
    n = 32

    # session c14f1728-b4f5-5fb4-845c-9dc830b3e9bf
    asymmetry = {}
    asymmetry["apt"] = get_asymmetry_dict(5.225, 4.4475, 177, 95, 65)
    asymmetry["ankle_pitch"] = get_asymmetry_dict(71.4725, 71.8225, 12, 152, 7)
    asymmetry["hip_drop"] = get_asymmetry_dict(5.4825, 5.395, 72, 200, 26)
    asymmetry["knee_valgus"] = get_asymmetry_dict(0.0, 4.8325, 22, 214, 9)
    asymmetry["hip_rotation"] = get_asymmetry_dict(0.1, 0.54, 137, 122, 53)

    full_history[n] = asymmetry
    full_history[n + 1] = None

    # session 958dba09-c338-5118-86a3-d20a559f09c2
    asymmetry_2 = {}
    asymmetry_2["apt"] = get_asymmetry_dict(2.305, 2.89, 166, 100, 62)
    asymmetry_2["ankle_pitch"] = get_asymmetry_dict(73.66, 72.49, 28, 237, 11)
    asymmetry_2["hip_drop"] = get_asymmetry_dict(1.825, 3.415, 248, 18, 93)
    asymmetry_2["knee_valgus"] = get_asymmetry_dict(2.29, 5.3175, 266, 0, 100)
    asymmetry_2["hip_rotation"] = get_asymmetry_dict(0.0, 0.28, 0, 135, 0)

    full_history[n + 2] = asymmetry_2

    return full_history


def get_asymmetry_tread():

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 26)
    n = 26

    # session 07b9b744-3e85-563d-b69a-822148673f58
    asymmetry = {}
    asymmetry["apt"] = get_asymmetry_dict(7.36, 8.21, 1, 4, 20)
    asymmetry["ankle_pitch"] = get_asymmetry_dict(80.6975, 79.8525, 0, 4, 0)
    asymmetry["hip_drop"] = get_asymmetry_dict(9.25, 3.78, 5, 0, 100)
    asymmetry["knee_valgus"] = get_asymmetry_dict(5.815, 5.16, 2, 3, 40)
    asymmetry["hip_rotation"] = get_asymmetry_dict(2.605, 2.53, 4, 1, 80)

    full_history[n] = asymmetry
    full_history[n + 1] = None

    # session 398ad5bf-3792-5b63-b07f-60a1e6bda875
    asymmetry_2 = {}
    asymmetry_2["apt"] = get_asymmetry_dict(5.4375, 6.3, 5, 3, 62)
    asymmetry_2["ankle_pitch"] = get_asymmetry_dict(75.7775, 78.37, 4, 4, 50)
    asymmetry_2["hip_drop"] = get_asymmetry_dict(5.725, 6.285, 1, 7, 12)
    asymmetry_2["knee_valgus"] = get_asymmetry_dict(6.545, 5.3625, 7, 1, 88)
    asymmetry_2["hip_rotation"] = get_asymmetry_dict(1.1975, 1.02, 5, 3, 62)

    full_history[n + 2] = asymmetry_2
    full_history[n + 3] = None

    # session 2f26eee8-455a-5678-a384-ed5a14c6e54a
    asymmetry_3 = {}
    asymmetry_3["apt"] = get_asymmetry_dict(4.67, 5.23, 2, 5, 29)
    asymmetry_3["ankle_pitch"] = get_asymmetry_dict(81.185, 88.0475, 3, 1, 75)
    asymmetry_3["hip_drop"] = get_asymmetry_dict(5.95, 4.23, 5, 2, 71)
    asymmetry_3["knee_valgus"] = get_asymmetry_dict(5.395, 4.28, 5, 2, 71)
    asymmetry_3["hip_rotation"] = get_asymmetry_dict(1.2, 0.44, 5, 2, 71)

    full_history[n + 4] = asymmetry_3
    full_history[n + 5] = None

    # session f93e004d-7dd0-56b3-bb22-353750586f5e
    asymmetry_4 = {}
    asymmetry_4["apt"] = get_asymmetry_dict(4.32, 5.7425, 5, 1, 83)
    asymmetry_4["ankle_pitch"] = get_asymmetry_dict(79.745, 82.1425, 1, 5, 17)
    asymmetry_4["hip_drop"] = get_asymmetry_dict(5.7325, 5.085, 1, 5, 17)
    asymmetry_4["knee_valgus"] = get_asymmetry_dict(6.7, 5.165, 6, 0, 100)
    asymmetry_4["hip_rotation"] = get_asymmetry_dict(1.0725, 0.405, 5, 1, 83)

    full_history[n + 6] = asymmetry_4
    full_history[n + 7] = None

    # session f78a9e26-6003-5ac7-8590-3ae4a421dac7
    asymmetry_5 = {}
    asymmetry_5["apt"] = get_asymmetry_dict(4.66, 5.6, 24, 8, 75)
    asymmetry_5["ankle_pitch"] = get_asymmetry_dict(85.685, 86.765, 7, 25, 22)
    asymmetry_5["hip_drop"] = get_asymmetry_dict(5.695, 5.505, 4, 28, 12)
    asymmetry_5["knee_valgus"] = get_asymmetry_dict(7.755, 6.125, 30, 2, 94)
    asymmetry_5["hip_rotation"] = get_asymmetry_dict(0.2575, 0.2275, 7, 25, 22)

    full_history[n + 8] = asymmetry_5

    return full_history


def get_asymmetry_fake():

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 22)
    n = 22

    asymmetry = {}
    asymmetry["apt"] = get_asymmetry_dict(7.36, 8.21, 1, 4, 20)
    asymmetry["ankle_pitch"] = get_asymmetry_dict(80.6975, 79.8525, 0, 4, 0)
    asymmetry["hip_drop"] = get_asymmetry_dict(9.25, 3.78, 5, 0, 100)
    asymmetry["knee_valgus"] = get_asymmetry_dict(5.815, 5.16, 2, 3, 40)
    asymmetry["hip_rotation"] = get_asymmetry_dict(2.605, 2.53, 4, 1, 80)

    full_history[n] = asymmetry
    full_history[n + 1] = None

    asymmetry_2 = {}
    asymmetry_2["apt"] = get_asymmetry_dict(5.4375, 6.3, 5, 3, 62)
    asymmetry_2["ankle_pitch"] = get_asymmetry_dict(75.7775, 78.37, 4, 4, 50)
    asymmetry_2["hip_drop"] = get_asymmetry_dict(5.725, 6.285, 1, 7, 12)
    asymmetry_2["knee_valgus"] = get_asymmetry_dict(6.545, 5.3625, 7, 1, 88)
    asymmetry_2["hip_rotation"] = get_asymmetry_dict(1.1975, 1.02, 5, 3, 62)

    full_history[n + 2] = asymmetry_2
    full_history[n + 3] = None

    asymmetry_3 = {}
    asymmetry_3["apt"] = get_asymmetry_dict(4.67, 5.23, 2, 5, 29)
    asymmetry_3["ankle_pitch"] = get_asymmetry_dict(81.185, 88.0475, 3, 1, 75)
    asymmetry_3["hip_drop"] = get_asymmetry_dict(5.95, 4.23, 5, 2, 71)
    asymmetry_3["knee_valgus"] = get_asymmetry_dict(5.395, 4.28, 5, 2, 71)
    asymmetry_3["hip_rotation"] = get_asymmetry_dict(1.2, 0.44, 5, 2, 71)

    full_history[n + 4] = asymmetry_3
    full_history[n + 5] = None

    asymmetry_4 = {}
    asymmetry_4["apt"] = get_asymmetry_dict(4.32, 5.7425, 5, 1, 83)
    asymmetry_4["ankle_pitch"] = get_asymmetry_dict(79.745, 82.1425, 1, 5, 17)
    asymmetry_4["hip_drop"] = get_asymmetry_dict(5.7325, 5.085, 1, 5, 17)
    asymmetry_4["knee_valgus"] = get_asymmetry_dict(6.7, 5.165, 6, 0, 100)
    asymmetry_4["hip_rotation"] = get_asymmetry_dict(1.0725, 0.405, 5, 1, 83)

    full_history[n + 6] = asymmetry_4
    full_history[n + 7] = None

    asymmetry_5 = {}
    asymmetry_5["apt"] = get_asymmetry_dict(4.66, 5.6, 24, 8, 75)
    asymmetry_5["ankle_pitch"] = get_asymmetry_dict(85.685, 86.765, 7, 25, 22)
    asymmetry_5["hip_drop"] = get_asymmetry_dict(5.695, 5.505, 4, 28, 12)
    asymmetry_5["knee_valgus"] = get_asymmetry_dict(7.755, 6.125, 30, 2, 94)
    asymmetry_5["hip_rotation"] = get_asymmetry_dict(0.2575, 0.2275, 7, 25, 22)

    full_history[n + 8] = asymmetry_5
    full_history[n + 9] = None

    asymmetry_6 = {}
    asymmetry_6["apt"] = get_asymmetry_dict(5.225, 4.4475, 177, 95, 65)
    asymmetry_6["ankle_pitch"] = get_asymmetry_dict(71.4725, 71.8225, 12, 152, 7)
    asymmetry_6["hip_drop"] = get_asymmetry_dict(5.4825, 5.395, 72, 200, 26)
    asymmetry_6["knee_valgus"] = get_asymmetry_dict(0.0, 4.8325, 22, 214, 9)
    asymmetry_6["hip_rotation"] = get_asymmetry_dict(0.1, 0.54, 137, 122, 53)

    full_history[n + 10] = asymmetry_6
    full_history[n + 11] = None

    asymmetry_7 = {}
    asymmetry_7["apt"] = get_asymmetry_dict(2.305, 2.89, 166, 100, 62)
    asymmetry_7["ankle_pitch"] = get_asymmetry_dict(73.66, 72.49, 28, 237, 11)
    asymmetry_7["hip_drop"] = get_asymmetry_dict(1.825, 3.415, 248, 18, 93)
    asymmetry_7["knee_valgus"] = get_asymmetry_dict(2.29, 5.3175, 266, 0, 100)
    asymmetry_7["hip_rotation"] = get_asymmetry_dict(0.0, 0.28, 0, 135, 0)

    full_history[n + 12] = asymmetry_7

    return full_history


def run_fake_regressions_a():

    full_session_history = {}
    full_session_history = pre_pad_with_nones(full_session_history, 22)

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 22)
    n = 22

    history = {}
    history["left_apt_ankle_pitch_elasticity"] = 0.26862678142297
    history["left_apt_ankle_pitch_y_adf"] = 0.0
    history["right_apt_ankle_pitch_elasticity"] = 0.0
    history["right_apt_ankle_pitch_y_adf"] = -2.83438094570226

    history["left_hip_drop_apt_elasticity"] = 0.109925542103301
    history["left_hip_drop_apt_y_adf"] = -2.62682304912778
    history["right_hip_drop_apt_elasticity"] = 0.560416499724003
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = 0.0933318324347078
    history["left_hip_drop_pva_y_adf"] = -2.66670310044273
    history["right_hip_drop_pva_elasticity"] = 0.195678136071858
    history["right_hip_drop_pva_y_adf"] = 0.0

    history["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = 0.357556927181195
    history["right_knee_valgus_pva_y_adf"] = 0.0

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = 0.0
    history["right_knee_valgus_apt_y_adf"] = 0.0

    history["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history["left_hip_rotation_ankle_pitch_y_adf"] = -2.54095280579048
    history["right_hip_rotation_ankle_pitch_elasticity"] = 2.13109736042987
    history["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history["left_hip_rotation_apt_elasticity"] = 0.0
    history["left_hip_rotation_apt_y_adf"] = 0.0
    history["right_hip_rotation_apt_elasticity"] = 0.564494521164848
    history["right_hip_rotation_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 941
    session_details["session_id"] = '7bbff8e0-189a-5643-93bc-9730e0fdcd20'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n + 1] = None
    full_session_history[n + 1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = 0.0
    history_2["left_apt_ankle_pitch_y_adf"] = 0.0
    history_2["right_apt_ankle_pitch_elasticity"] = 0.7511842599502640
    history_2["right_apt_ankle_pitch_y_adf"] = -0.981737705145077

    history_2["left_hip_drop_apt_elasticity"] = 0.0
    history_2["left_hip_drop_apt_y_adf"] = 0.0
    history_2["right_hip_drop_apt_elasticity"] = 0.293869832196777
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = 0.0798247205126612
    history_2["left_hip_drop_pva_y_adf"] = 0.0
    history_2["right_hip_drop_pva_elasticity"] = 0.0
    history_2["right_hip_drop_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["left_knee_valgus_hip_drop_y_adf"] = -1.96728993333675
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

    history_2["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_2["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_2["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_2["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_rotation_apt_elasticity"] = 0.0
    history_2["left_hip_rotation_apt_y_adf"] = 0.0
    history_2["right_hip_rotation_apt_elasticity"] = 0.0
    history_2["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_2 = {}
    session_details_2["seconds_duration"] = 1073
    session_details_2["session_id"] = '39f243c2-6baf-5558-a2df-4f051f88c06f'

    full_history[n + 2] = history_2
    full_session_history[n + 2] = session_details_2
    full_history[n + 3] = None
    full_session_history[n + 3] = None

    history_3 = {}
    history_3["left_apt_ankle_pitch_elasticity"] = 0.0405437554208033
    history_3["left_apt_ankle_pitch_y_adf"] = 0.0
    history_3["right_apt_ankle_pitch_elasticity"] = 0.227381329976232
    history_3["right_apt_ankle_pitch_y_adf"] = 0.0

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

    history_3["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_3["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_3["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_3["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_3["left_hip_rotation_apt_elasticity"] = 0.0
    history_3["left_hip_rotation_apt_y_adf"] = 0.0
    history_3["right_hip_rotation_apt_elasticity"] = 0.0
    history_3["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_3 = {}
    session_details_3["seconds_duration"] = 8640
    session_details_3["session_id"] = 'c14f1728-b4f5-5fb4-845c-9dc830b3e9bf'

    full_history[n + 4] = history
    full_session_history[n + 4] = session_details_3

    full_history[n + 5] = None
    full_session_history[n + 5] = None

    history_4 = {}
    history_4["left_apt_ankle_pitch_elasticity"] = .7647161302258
    history_4["left_apt_ankle_pitch_y_adf"] = 0.0
    history_4["right_apt_ankle_pitch_elasticity"] = .71044788722549
    history_4["right_apt_ankle_pitch_y_adf"] = 0.0

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

    history_4["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_4["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_4["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_4["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_4["left_hip_rotation_apt_elasticity"] = 0.0
    history_4["left_hip_rotation_apt_y_adf"] = 0.0
    history_4["right_hip_rotation_apt_elasticity"] = 0.0
    history_4["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_4 = {}
    session_details_4["seconds_duration"] = 8166
    session_details_4["session_id"] = '958dba09-c338-5118-86a3-d20a559f09c2'

    full_history[n + 6] = history_4
    full_session_history[n + 6] = session_details_4
    
    full_history[n + 7] = None
    full_session_history[n + 7] = None

    history_5 = {}
    history_5["left_apt_ankle_pitch_elasticity"] = .08181299759617
    history_5["left_apt_ankle_pitch_y_adf"] = -2.44379631010323
    history_5["right_apt_ankle_pitch_elasticity"] = .78245291776496
    history_5["right_apt_ankle_pitch_y_adf"] = -2.59745729790358

    history_5["left_hip_drop_apt_elasticity"] = 0.178092796366487
    history_5["left_hip_drop_apt_y_adf"] = 0.0
    history_5["right_hip_drop_apt_elasticity"] = 0.0
    history_5["right_hip_drop_apt_y_adf"] = 0.0

    history_5["left_hip_drop_pva_elasticity"] = 0.0
    history_5["left_hip_drop_pva_y_adf"] = 0.0
    history_5["right_hip_drop_pva_elasticity"] = 0.0
    history_5["right_hip_drop_pva_y_adf"] = -1.96315960872926

    history_5["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_5["left_knee_valgus_hip_drop_y_adf"] = -2.39749903278379
    history_5["right_knee_valgus_hip_drop_elasticity"] = 0.144239542774656
    history_5["right_knee_valgus_hip_drop_y_adf"] = -2.41061792838523

    history_5["left_knee_valgus_pva_elasticity"] = 0.0
    history_5["left_knee_valgus_pva_y_adf"] = -2.74864901159945
    history_5["right_knee_valgus_pva_elasticity"] = 0.0
    history_5["right_knee_valgus_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_apt_elasticity"] = 0.133339194910961
    history_5["left_knee_valgus_apt_y_adf"] = 0.0
    history_5["right_knee_valgus_apt_elasticity"] = 0.159290632566094
    history_5["right_knee_valgus_apt_y_adf"] = 0.0

    history_5["left_hip_rotation_ankle_pitch_elasticity"] = 2.16194197102348
    history_5["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_5["right_hip_rotation_ankle_pitch_elasticity"] = 3.85946494374415
    history_5["right_hip_rotation_ankle_pitch_y_adf"] = -2.03806539732218

    history_5["left_hip_rotation_apt_elasticity"] = 0.0
    history_5["left_hip_rotation_apt_y_adf"] = 0.0
    history_5["right_hip_rotation_apt_elasticity"] = 0.9709372075516
    history_5["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_5 = {}
    session_details_5["seconds_duration"] = 243
    session_details_5["session_id"] = 'f93e004d-7dd0-56b3-bb22-353750586f5e'

    full_history[n + 8] = history_5
    full_session_history[n + 8] = session_details_5
    full_history[n + 9] = None
    full_session_history[n + 9] = None

    history_6 = {}
    history_6["left_apt_ankle_pitch_elasticity"] = 0.429038632704596
    history_6["left_apt_ankle_pitch_y_adf"] = 0.0
    history_6["right_apt_ankle_pitch_elasticity"] = 0.0
    history_6["right_apt_ankle_pitch_y_adf"] = 0.0

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

    history_6["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_6["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_6["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_6["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_6["left_hip_rotation_apt_elasticity"] = 0.0
    history_6["left_hip_rotation_apt_y_adf"] = 0.0
    history_6["right_hip_rotation_apt_elasticity"] = 0.0
    history_6["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_6 = {}
    session_details_6["seconds_duration"] = 1495
    session_details_6["session_id"] = 'f78a9e26-6003-5ac7-8590-3ae4a421dac7'

    full_history[n + 10] = history_6
    full_session_history[n + 10] = session_details_6
    full_history[n + 11] = None
    full_session_history[n + 11] = None

    history_7 = {}
    history_7["left_apt_ankle_pitch_elasticity"] = 0.429038632704596
    history_7["left_apt_ankle_pitch_y_adf"] = 0.0
    history_7["right_apt_ankle_pitch_elasticity"] = 0.0
    history_7["right_apt_ankle_pitch_y_adf"] = 0.0

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

    history_7["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_7["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_7["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_7["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_7["left_hip_rotation_apt_elasticity"] = 0.0
    history_7["left_hip_rotation_apt_y_adf"] = 0.0
    history_7["right_hip_rotation_apt_elasticity"] = 0.0
    history_7["right_hip_rotation_apt_y_adf"] = 0.0

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
    history["left_apt_ankle_pitch_elasticity"] = 0.0
    history["left_apt_ankle_pitch_y_adf"] = 0.0
    history["right_apt_ankle_pitch_elasticity"] = 0.7511842599502640
    history["right_apt_ankle_pitch_y_adf"] = -0.981737705145077

    history["left_hip_drop_apt_elasticity"] = 0.0
    history["left_hip_drop_apt_y_adf"] = 0.0
    history["right_hip_drop_apt_elasticity"] = -0.293869832196777
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = 0.0798247205126612
    history["left_hip_drop_pva_y_adf"] = 0.0
    history["right_hip_drop_pva_elasticity"] = 0.0
    history["right_hip_drop_pva_y_adf"] = 0.0

    history["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history["left_knee_valgus_hip_drop_y_adf"] = -1.96728993333675
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = -0.350647636838605
    history["right_knee_valgus_pva_y_adf"] = 0.0

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = -0.211949329970997
    history["right_knee_valgus_apt_y_adf"] = 0.0

    history["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history["left_hip_rotation_apt_elasticity"] = 0.0
    history["left_hip_rotation_apt_y_adf"] = 0.0
    history["right_hip_rotation_apt_elasticity"] = 0.0
    history["right_hip_rotation_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 1073
    session_details["session_id"] = '39f243c2-6baf-5558-a2df-4f051f88c06f'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n+1] = None
    full_session_history[n+1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = 0.26862678142297
    history_2["left_apt_ankle_pitch_y_adf"] = 0.0
    history_2["right_apt_ankle_pitch_elasticity"] = 0.0
    history_2["right_apt_ankle_pitch_y_adf"] = -2.83438094570226

    history_2["left_hip_drop_apt_elasticity"] = -0.109925542103301
    history_2["left_hip_drop_apt_y_adf"] = -2.62682304912778
    history_2["right_hip_drop_apt_elasticity"] = -0.560416499724003
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = -0.0933318324347078
    history_2["left_hip_drop_pva_y_adf"] = -2.66670310044273
    history_2["right_hip_drop_pva_elasticity"] = -0.195678136071858
    history_2["right_hip_drop_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_2["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_2["left_knee_valgus_pva_elasticity"] = 0.0
    history_2["left_knee_valgus_pva_y_adf"] = 0.0
    history_2["right_knee_valgus_pva_elasticity"] = -0.357556927181195
    history_2["right_knee_valgus_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_apt_elasticity"] = 0.0
    history_2["left_knee_valgus_apt_y_adf"] = 0.0
    history_2["right_knee_valgus_apt_elasticity"] = 0.0
    history_2["right_knee_valgus_apt_y_adf"] = 0.0

    history_2["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_2["left_hip_rotation_ankle_pitch_y_adf"] = -2.54095280579048
    history_2["right_hip_rotation_ankle_pitch_elasticity"] = 2.13109736042987
    history_2["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_rotation_apt_elasticity"] = 0.0
    history_2["left_hip_rotation_apt_y_adf"] = 0.0
    history_2["right_hip_rotation_apt_elasticity"] = 0.564494521164848
    history_2["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_2 = {}
    session_details_2["seconds_duration"] = 941
    session_details_2["session_id"] = '7bbff8e0-189a-5643-93bc-9730e0fdcd20'

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
    history["left_apt_ankle_pitch_y_adf"] = 0.0
    history["right_apt_ankle_pitch_elasticity"] = 0.227381329976232
    history["right_apt_ankle_pitch_y_adf"] = 0.0

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

    history["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history["left_hip_rotation_apt_elasticity"] = 0.0
    history["left_hip_rotation_apt_y_adf"] = 0.0
    history["right_hip_rotation_apt_elasticity"] = 0.0
    history["right_hip_rotation_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 8640
    session_details["session_id"] = 'c14f1728-b4f5-5fb4-845c-9dc830b3e9bf'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n+1] = None
    full_session_history[n+1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = -3.7647161302258
    history_2["left_apt_ankle_pitch_y_adf"] = 0.0
    history_2["right_apt_ankle_pitch_elasticity"] = -1.71044788722549
    history_2["right_apt_ankle_pitch_y_adf"] = 0.0

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

    history_2["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_2["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_2["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_2["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_rotation_apt_elasticity"] = 0.0
    history_2["left_hip_rotation_apt_y_adf"] = 0.0
    history_2["right_hip_rotation_apt_elasticity"] = 0.0
    history_2["right_hip_rotation_apt_y_adf"] = 0.0

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
    history["left_apt_ankle_pitch_y_adf"] = -2.46228739132714
    history["right_apt_ankle_pitch_elasticity"] = 0.0
    history["right_apt_ankle_pitch_y_adf"] = 0.0

    history["left_hip_drop_apt_elasticity"] = 0.0
    history["left_hip_drop_apt_y_adf"] = 0.0
    history["right_hip_drop_apt_elasticity"] = 0.0
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = 0.0
    history["left_hip_drop_pva_y_adf"] = 0.0
    history["right_hip_drop_pva_elasticity"] = 0.0
    history["right_hip_drop_pva_y_adf"] = -2.27058232342159

    history["left_knee_valgus_hip_drop_elasticity"] = 0.303545853437089
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0745365137141311
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = 0.0
    history["right_knee_valgus_pva_y_adf"] = -1.09409318758823

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = 0.0
    history["right_knee_valgus_apt_y_adf"] = 0.0

    history["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history["left_hip_rotation_apt_elasticity"] = 0.0
    history["left_hip_rotation_apt_y_adf"] = 0.0
    history["right_hip_rotation_apt_elasticity"] = 0.0
    history["right_hip_rotation_apt_y_adf"] = 0.0

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

    history_2["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_2["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_2["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_2["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_rotation_apt_elasticity"] = 0.0
    history_2["left_hip_rotation_apt_y_adf"] = 0.0
    history_2["right_hip_rotation_apt_elasticity"] = 0.0
    history_2["right_hip_rotation_apt_y_adf"] = 0.0

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

    history_3["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_3["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_3["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_3["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_3["left_hip_rotation_apt_elasticity"] = 0.0
    history_3["left_hip_rotation_apt_y_adf"] = 0.0
    history_3["right_hip_rotation_apt_elasticity"] = 0.0
    history_3["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_3 = {}
    session_details_3["seconds_duration"] = 242
    session_details_3["session_id"] = '2f26eee8-455a-5678-a384-ed5a14c6e54a'

    full_history[n+4] = history_3
    full_session_history[n+4] = session_details_3
    full_history[n+5] = None
    full_session_history[n+5] = None
    
    history_4 = {}
    history_4["left_apt_ankle_pitch_elasticity"] = -1.08181299759617
    history_4["left_apt_ankle_pitch_y_adf"] = -2.44379631010323
    history_4["right_apt_ankle_pitch_elasticity"] = -1.78245291776496
    history_4["right_apt_ankle_pitch_y_adf"] = -2.59745729790358

    history_4["left_hip_drop_apt_elasticity"] = 0.178092796366487
    history_4["left_hip_drop_apt_y_adf"] = 0.0
    history_4["right_hip_drop_apt_elasticity"] = 0.0
    history_4["right_hip_drop_apt_y_adf"] = 0.0

    history_4["left_hip_drop_pva_elasticity"] = 0.0
    history_4["left_hip_drop_pva_y_adf"] = 0.0
    history_4["right_hip_drop_pva_elasticity"] = 0.0
    history_4["right_hip_drop_pva_y_adf"] = -1.96315960872926

    history_4["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_4["left_knee_valgus_hip_drop_y_adf"] = -2.39749903278379
    history_4["right_knee_valgus_hip_drop_elasticity"] = 0.144239542774656
    history_4["right_knee_valgus_hip_drop_y_adf"] = -2.41061792838523

    history_4["left_knee_valgus_pva_elasticity"] = 0.0
    history_4["left_knee_valgus_pva_y_adf"] = -2.74864901159945
    history_4["right_knee_valgus_pva_elasticity"] = 0.0
    history_4["right_knee_valgus_pva_y_adf"] = 0.0

    history_4["left_knee_valgus_apt_elasticity"] = -0.133339194910961
    history_4["left_knee_valgus_apt_y_adf"] = 0.0
    history_4["right_knee_valgus_apt_elasticity"] = -0.159290632566094
    history_4["right_knee_valgus_apt_y_adf"] = 0.0

    history_4["left_hip_rotation_ankle_pitch_elasticity"] = 2.16194197102348
    history_4["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_4["right_hip_rotation_ankle_pitch_elasticity"] = 3.85946494374415
    history_4["right_hip_rotation_ankle_pitch_y_adf"] = -2.03806539732218

    history_4["left_hip_rotation_apt_elasticity"] = 0.0
    history_4["left_hip_rotation_apt_y_adf"] = 0.0
    history_4["right_hip_rotation_apt_elasticity"] = -0.9709372075516
    history_4["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_4 = {}
    session_details_4["seconds_duration"] = 243
    session_details_4["session_id"] = 'f93e004d-7dd0-56b3-bb22-353750586f5e'

    full_history[n+6] = history_4
    full_session_history[n+6] = session_details_4
    full_history[n+7] = None
    full_session_history[n+7] = None
    
    history_5 = {}
    history_5["left_apt_ankle_pitch_elasticity"] = -0.429038632704596
    history_5["left_apt_ankle_pitch_y_adf"] = 0.0
    history_5["right_apt_ankle_pitch_elasticity"] = 0.0
    history_5["right_apt_ankle_pitch_y_adf"] = 0.0

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
    history_5["right_knee_valgus_hip_drop_y_adf"] =0.0

    history_5["left_knee_valgus_pva_elasticity"] = 0.0
    history_5["left_knee_valgus_pva_y_adf"] = 0.0
    history_5["right_knee_valgus_pva_elasticity"] = 0.0
    history_5["right_knee_valgus_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_apt_elasticity"] = -0.0431147083237144
    history_5["left_knee_valgus_apt_y_adf"] = 0.0
    history_5["right_knee_valgus_apt_elasticity"] = -0.0768290349343447
    history_5["right_knee_valgus_apt_y_adf"] = 0.0

    history_5["left_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_5["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_5["right_hip_rotation_ankle_pitch_elasticity"] = 0.0
    history_5["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_5["left_hip_rotation_apt_elasticity"] = 0.0
    history_5["left_hip_rotation_apt_y_adf"] = 0.0
    history_5["right_hip_rotation_apt_elasticity"] = 0.0
    history_5["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_5 = {}
    session_details_5["seconds_duration"] = 1495
    session_details_5["session_id"] = 'f78a9e26-6003-5ac7-8590-3ae4a421dac7'

    full_history[n + 8] = history_5
    full_session_history[n + 8] = session_details_5

    return full_history, full_session_history