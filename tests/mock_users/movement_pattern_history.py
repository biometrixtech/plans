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
    asymmetry["ankle_pitch"] = get_asymmetry_dict(92.94, 95.2, 13, 16, 45)
    asymmetry["hip_drop"] = get_asymmetry_dict(6.43, 2.89, 29, 0, 100)
    asymmetry["knee_valgus"] = get_asymmetry_dict(3.62, 1.22, 26, 3, 90)
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
    asymmetry["ankle_pitch"] = get_asymmetry_dict(74.33, 74.72, 84, 131, 39)
    asymmetry["hip_drop"] = get_asymmetry_dict(5.4825, 5.395, 72, 200, 26)
    asymmetry["knee_valgus"] = get_asymmetry_dict(0.0, 4.8325, 229, 7, 97)
    asymmetry["hip_rotation"] = get_asymmetry_dict(0.1, 0.54, 182, 77, 70)

    full_history[n] = asymmetry
    full_history[n + 1] = None

    # session 958dba09-c338-5118-86a3-d20a559f09c2
    asymmetry_2 = {}
    asymmetry_2["apt"] = get_asymmetry_dict(2.305, 2.89, 166, 100, 62)
    asymmetry_2["ankle_pitch"] = get_asymmetry_dict(73.775, 72.6175, 29, 237, 11)
    asymmetry_2["hip_drop"] = get_asymmetry_dict(1.825, 3.415, 248, 18, 93)
    asymmetry_2["knee_valgus"] = get_asymmetry_dict(2.29, 5.3175, 266, 0, 100)
    asymmetry_2["hip_rotation"] = get_asymmetry_dict(0.0, 0.28, 34, 101, 75)

    full_history[n + 2] = asymmetry_2

    return full_history


def get_asymmetry_extreme_valgus_hip_rotation():

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 32)
    n = 32

    # session 39f243c2-6baf-5558-a2df-4f051f88c06f
    asymmetry = {}
    asymmetry["apt"] = get_asymmetry_dict(10.54, 9.44, 9, 20, 31)
    asymmetry["ankle_pitch"] = get_asymmetry_dict(92.94, 95.2, 13, 16, 45)
    asymmetry["hip_drop"] = get_asymmetry_dict(6.43, 2.89, 29, 0, 100)
    asymmetry["knee_valgus"] = get_asymmetry_dict(3.62, 1.22, 26, 3, 90)
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

def get_asymmetry_tread():

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 26)
    n = 26

    # session 07b9b744-3e85-563d-b69a-822148673f58
    asymmetry = {}
    asymmetry["apt"] = get_asymmetry_dict(7.36, 8.21, 1, 4, 20)
    asymmetry["ankle_pitch"] = get_asymmetry_dict(82.685, 81.655, 0, 5, 0)
    asymmetry["hip_drop"] = get_asymmetry_dict(9.25, 3.78, 5, 0, 100)
    asymmetry["knee_valgus"] = get_asymmetry_dict(5.815, 5.16, 2, 3, 40)
    asymmetry["hip_rotation"] = get_asymmetry_dict(2.605, 2.53, 4, 1, 80)

    full_history[n] = asymmetry
    full_history[n + 1] = None

    # session 398ad5bf-3792-5b63-b07f-60a1e6bda875
    asymmetry_2 = {}
    asymmetry_2["apt"] = get_asymmetry_dict(5.4375, 6.3, 5, 3, 62)
    asymmetry_2["ankle_pitch"] = get_asymmetry_dict(75.7825, 78.3825, 5, 3, 62)
    asymmetry_2["hip_drop"] = get_asymmetry_dict(5.725, 6.285, 1, 7, 12)
    asymmetry_2["knee_valgus"] = get_asymmetry_dict(6.545, 5.3625, 7, 1, 88)
    asymmetry_2["hip_rotation"] = get_asymmetry_dict(1.1975, 1.02, 5, 3, 62)

    full_history[n + 2] = asymmetry_2
    full_history[n + 3] = None

    # session 2f26eee8-455a-5678-a384-ed5a14c6e54a
    asymmetry_3 = {}
    asymmetry_3["apt"] = get_asymmetry_dict(4.67, 5.23, 2, 5, 29)
    asymmetry_3["ankle_pitch"] = get_asymmetry_dict(82.75, 87.55, 7, 0, 100)
    asymmetry_3["hip_drop"] = get_asymmetry_dict(5.95, 4.23, 5, 2, 71)
    asymmetry_3["knee_valgus"] = get_asymmetry_dict(5.395, 4.28, 5, 2, 71)
    asymmetry_3["hip_rotation"] = get_asymmetry_dict(1.2, 0.44, 5, 2, 71)

    full_history[n + 4] = asymmetry_3
    full_history[n + 5] = None

    # session f93e004d-7dd0-56b3-bb22-353750586f5e
    asymmetry_4 = {}
    asymmetry_4["apt"] = get_asymmetry_dict(4.32, 5.7425, 5, 1, 83)
    asymmetry_4["ankle_pitch"] = get_asymmetry_dict(81.375, 84.24, 3, 3, 50)
    asymmetry_4["hip_drop"] = get_asymmetry_dict(5.7325, 5.085, 1, 5, 17)
    asymmetry_4["knee_valgus"] = get_asymmetry_dict(6.7, 5.165, 6, 0, 100)
    asymmetry_4["hip_rotation"] = get_asymmetry_dict(1.0725, 0.405, 5, 1, 83)

    full_history[n + 6] = asymmetry_4
    full_history[n + 7] = None

    # session f78a9e26-6003-5ac7-8590-3ae4a421dac7
    asymmetry_5 = {}
    asymmetry_5["apt"] = get_asymmetry_dict(4.66, 5.6, 24, 8, 75)
    asymmetry_5["ankle_pitch"] = get_asymmetry_dict(85.685, 87.015, 8, 24, 25)
    asymmetry_5["hip_drop"] = get_asymmetry_dict(5.695, 5.505, 4, 28, 12)
    asymmetry_5["knee_valgus"] = get_asymmetry_dict(7.755, 6.125, 30, 2, 94)
    asymmetry_5["hip_rotation"] = get_asymmetry_dict(0.2575, 0.2275, 7, 25, 22)

    full_history[n + 8] = asymmetry_5

    return full_history


def get_asymmetry_fake():

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 22)
    n = 22

    # session 7bbff8e0-189a-5643-93bc-9730e0fdcd20
    asymmetry = {}
    asymmetry["apt"] = get_asymmetry_dict(10.4575, 7.36, 32, 0, 100)
    asymmetry["ankle_pitch"] = get_asymmetry_dict(93.6725, 89.265, 26, 6, 81)
    asymmetry["hip_drop"] = get_asymmetry_dict(6.065, 5.8375, 0, 32, 0)
    asymmetry["knee_valgus"] = get_asymmetry_dict(2.78, 5.3775, 32, 0, 100)
    asymmetry["hip_rotation"] = get_asymmetry_dict(1.125, 2.1525, 32, 0, 100)

    full_history[n] = asymmetry
    full_history[n + 1] = None

    # session 39f243c2-6baf-5558-a2df-4f051f88c06f
    asymmetry_2 = {}
    asymmetry_2["apt"] = get_asymmetry_dict(10.54, 9.44, 9, 20, 31)
    asymmetry_2["ankle_pitch"] = get_asymmetry_dict(92.94, 95.2, 13, 16, 45)
    asymmetry_2["hip_drop"] = get_asymmetry_dict(6.43, 2.89, 29, 0, 100)
    asymmetry_2["knee_valgus"] = get_asymmetry_dict(3.62, 1.22, 26, 3, 90)
    asymmetry_2["hip_rotation"] = get_asymmetry_dict(1.27, 2.15, 23, 6, 79)

    full_history[n + 2] = asymmetry_2
    full_history[n + 3] = None

    # session c14f1728-b4f5-5fb4-845c-9dc830b3e9bf
    asymmetry_3 = {}
    asymmetry_3["apt"] = get_asymmetry_dict(5.225, 4.4475, 177, 95, 65)
    asymmetry_3["ankle_pitch"] = get_asymmetry_dict(74.33, 74.72, 84, 131, 39)
    asymmetry_3["hip_drop"] = get_asymmetry_dict(5.4825, 5.395, 72, 200, 26)
    asymmetry_3["knee_valgus"] = get_asymmetry_dict(0.0, 4.8325, 229, 7, 97)
    asymmetry_3["hip_rotation"] = get_asymmetry_dict(0.1, 0.54, 182, 77, 70)

    full_history[n + 4] = asymmetry_3
    full_history[n + 5] = None

    # session 958dba09-c338-5118-86a3-d20a559f09c2
    asymmetry_4 = {}
    asymmetry_4["apt"] = get_asymmetry_dict(2.305, 2.89, 166, 100, 62)
    asymmetry_4["ankle_pitch"] = get_asymmetry_dict(73.775, 72.6175, 29, 237, 11)
    asymmetry_4["hip_drop"] = get_asymmetry_dict(1.825, 3.415, 248, 18, 93)
    asymmetry_4["knee_valgus"] = get_asymmetry_dict(2.29, 5.3175, 266, 0, 100)
    asymmetry_4["hip_rotation"] = get_asymmetry_dict(0.0, 0.28, 34, 101, 75)

    full_history[n + 6] = asymmetry_4
    full_history[n + 7] = None

    # session f93e004d-7dd0-56b3-bb22-353750586f5e
    asymmetry_5 = {}
    asymmetry_5["apt"] = get_asymmetry_dict(4.32, 5.7425, 5, 1, 83)
    asymmetry_5["ankle_pitch"] = get_asymmetry_dict(81.375, 84.24, 3, 3, 50)
    asymmetry_5["hip_drop"] = get_asymmetry_dict(5.7325, 5.085, 1, 5, 17)
    asymmetry_5["knee_valgus"] = get_asymmetry_dict(6.7, 5.165, 6, 0, 100)
    asymmetry_5["hip_rotation"] = get_asymmetry_dict(1.0725, 0.405, 5, 1, 83)

    full_history[n + 8] = asymmetry_5
    full_history[n + 9] = None

    # session f78a9e26-6003-5ac7-8590-3ae4a421dac7
    asymmetry_6 = {}
    asymmetry_6["apt"] = get_asymmetry_dict(4.66, 5.6, 24, 8, 75)
    asymmetry_6["ankle_pitch"] = get_asymmetry_dict(85.685, 87.015, 8, 24, 25)
    asymmetry_6["hip_drop"] = get_asymmetry_dict(5.695, 5.505, 4, 28, 12)
    asymmetry_6["knee_valgus"] = get_asymmetry_dict(7.755, 6.125, 30, 2, 94)
    asymmetry_6["hip_rotation"] = get_asymmetry_dict(0.2575, 0.2275, 7, 25, 22)

    full_history[n + 10] = asymmetry_6
    full_history[n + 11] = None

    # session 2f26eee8-455a-5678-a384-ed5a14c6e54a
    asymmetry_7 = {}
    asymmetry_7["apt"] = get_asymmetry_dict(4.67, 5.23, 2, 5, 29)
    asymmetry_7["ankle_pitch"] = get_asymmetry_dict(82.75, 87.55, 7, 0, 100)
    asymmetry_7["hip_drop"] = get_asymmetry_dict(5.95, 4.23, 5, 2, 71)
    asymmetry_7["knee_valgus"] = get_asymmetry_dict(5.395, 4.28, 5, 2, 71)
    asymmetry_7["hip_rotation"] = get_asymmetry_dict(1.2, 0.44, 5, 2, 71)

    full_history[n + 12] = asymmetry_7

    return full_history


def run_fake_regressions_a():

    full_session_history = {}
    full_session_history = pre_pad_with_nones(full_session_history, 22)

    full_history = {}
    full_history = pre_pad_with_nones(full_history, 22)
    n = 22

    history = {}
    history["left_apt_ankle_pitch_elasticity"] = 0.0
    history["left_apt_ankle_pitch_y_adf"] = 0.0
    history["right_apt_ankle_pitch_elasticity"] = 0.206490226954283
    history["right_apt_ankle_pitch_y_adf"] = -0.979853570007948

    history["left_hip_drop_apt_elasticity"] = -0.159515012897757
    history["left_hip_drop_apt_y_adf"] = -2.55779037795781
    history["right_hip_drop_apt_elasticity"] = -0.277147155116258
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = 0.0723139465482049
    history["left_hip_drop_pva_y_adf"] = 0.0
    history["right_hip_drop_pva_elasticity"] = 0.0
    history["right_hip_drop_pva_y_adf"] = 0.0

    history["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = -0.350647636838605
    history["right_knee_valgus_pva_y_adf"] = 0.0

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = -0.251201252875501
    history["right_knee_valgus_apt_y_adf"] = 0.0

    history["left_hip_rotation_ankle_pitch_elasticity"] = 0.924804782628251
    history["left_hip_rotation_ankle_pitch_y_adf"] = -2.54095280579048
    history["right_hip_rotation_ankle_pitch_elasticity"] = 0.626882930247725
    history["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history["left_hip_rotation_apt_elasticity"] = 0.0
    history["left_hip_rotation_apt_y_adf"] = 0.0
    history["right_hip_rotation_apt_elasticity"] = 0.258772334759487
    history["right_hip_rotation_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 941
    session_details["session_id"] = '7bbff8e0-189a-5643-93bc-9730e0fdcd20'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n + 1] = None
    full_session_history[n + 1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = 0.231861169949236
    history_2["left_apt_ankle_pitch_y_adf"] = 0.0
    history_2["right_apt_ankle_pitch_elasticity"] = 0.0
    history_2["right_apt_ankle_pitch_y_adf"] = -2.83171173263586

    history_2["left_hip_drop_apt_elasticity"] = -0.107214126020672
    history_2["left_hip_drop_apt_y_adf"] = -2.62042909205245
    history_2["right_hip_drop_apt_elasticity"] = -0.460236691733895
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = -0.0760781836733736
    history_2["left_hip_drop_pva_y_adf"] = -2.689029578307
    history_2["right_hip_drop_pva_elasticity"] = -0.14807671437636
    history_2["right_hip_drop_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_2["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history_2["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_2["left_knee_valgus_pva_elasticity"] = 0.0
    history_2["left_knee_valgus_pva_y_adf"] = 0.0
    history_2["right_knee_valgus_pva_elasticity"] = -0.357556927181196
    history_2["right_knee_valgus_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_apt_elasticity"] = 0.0
    history_2["left_knee_valgus_apt_y_adf"] = 0.0
    history_2["right_knee_valgus_apt_elasticity"] = 0.0
    history_2["right_knee_valgus_apt_y_adf"] = 0.0

    history_2["left_hip_rotation_ankle_pitch_elasticity"] = -0.398625089772012
    history_2["left_hip_rotation_ankle_pitch_y_adf"] = -2.52965151457956
    history_2["right_hip_rotation_ankle_pitch_elasticity"] = 1.34483040792186
    history_2["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_rotation_apt_elasticity"] = 0.0
    history_2["left_hip_rotation_apt_y_adf"] = 0.0
    history_2["right_hip_rotation_apt_elasticity"] = 0.427811740484572
    history_2["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_2 = {}
    session_details_2["seconds_duration"] = 1073
    session_details_2["session_id"] = '39f243c2-6baf-5558-a2df-4f051f88c06f'

    full_history[n + 2] = history_2
    full_session_history[n + 2] = session_details_2
    full_history[n + 3] = None
    full_session_history[n + 3] = None

    history_3 = {}
    history_3["left_apt_ankle_pitch_elasticity"] = 0.0345736161517883
    history_3["left_apt_ankle_pitch_y_adf"] = 0.0
    history_3["right_apt_ankle_pitch_elasticity"] = 0.288488188735086
    history_3["right_apt_ankle_pitch_y_adf"] = 0.0

    history_3["left_hip_drop_apt_elasticity"] = 0.135184178791529
    history_3["left_hip_drop_apt_y_adf"] = 0.0
    history_3["right_hip_drop_apt_elasticity"] = 0.196180582682485
    history_3["right_hip_drop_apt_y_adf"] = 0.0

    history_3["left_hip_drop_pva_elasticity"] = 0.0510926754299412
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
    history_3["right_knee_valgus_apt_elasticity"] = -0.239635631923202
    history_3["right_knee_valgus_apt_y_adf"] = 0.0

    history_3["left_hip_rotation_ankle_pitch_elasticity"] = 0.0471320102970911
    history_3["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_3["right_hip_rotation_ankle_pitch_elasticity"] = -0.731835173000968
    history_3["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_3["left_hip_rotation_apt_elasticity"] = -0.228395501234287
    history_3["left_hip_rotation_apt_y_adf"] = 0.0
    history_3["right_hip_rotation_apt_elasticity"] = -0.531684824385146
    history_3["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_3 = {}
    session_details_3["seconds_duration"] = 8640
    session_details_3["session_id"] = 'c14f1728-b4f5-5fb4-845c-9dc830b3e9bf'

    full_history[n + 4] = history_3
    full_session_history[n + 4] = session_details_3

    full_history[n + 5] = None
    full_session_history[n + 5] = None

    history_4 = {}
    history_4["left_apt_ankle_pitch_elasticity"] = -2.11434616313849
    history_4["left_apt_ankle_pitch_y_adf"] = 0.0
    history_4["right_apt_ankle_pitch_elasticity"] = -1.08213397556769
    history_4["right_apt_ankle_pitch_y_adf"] = 0.0

    history_4["left_hip_drop_apt_elasticity"] = -0.0679901516786989
    history_4["left_hip_drop_apt_y_adf"] = 0.0
    history_4["right_hip_drop_apt_elasticity"] = 0.0702455572897758
    history_4["right_hip_drop_apt_y_adf"] = 0.0

    history_4["left_hip_drop_pva_elasticity"] = 0.0
    history_4["left_hip_drop_pva_y_adf"] = 0.0
    history_4["right_hip_drop_pva_elasticity"] = 0.0
    history_4["right_hip_drop_pva_y_adf"] = 0.0

    history_4["left_knee_valgus_hip_drop_elasticity"] = 0.0223803442718253
    history_4["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_4["right_knee_valgus_hip_drop_elasticity"] = -0.0683560849790874
    history_4["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_4["left_knee_valgus_pva_elasticity"] = 0.0517439919312008
    history_4["left_knee_valgus_pva_y_adf"] = 0.0
    history_4["right_knee_valgus_pva_elasticity"] = 0.0
    history_4["right_knee_valgus_pva_y_adf"] = 0.0

    history_4["left_knee_valgus_apt_elasticity"] = 0.0654532928133672
    history_4["left_knee_valgus_apt_y_adf"] = 0.0
    history_4["right_knee_valgus_apt_elasticity"] = 0.0203455356679933
    history_4["right_knee_valgus_apt_y_adf"] = 0.0

    history_4["left_hip_rotation_ankle_pitch_elasticity"] = 0.0141245992232984
    history_4["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_4["right_hip_rotation_ankle_pitch_elasticity"] = 0.391649213479082
    history_4["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_4["left_hip_rotation_apt_elasticity"] = 0.0
    history_4["left_hip_rotation_apt_y_adf"] = 0.0
    history_4["right_hip_rotation_apt_elasticity"] = -0.0598912980114923
    history_4["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_4 = {}
    session_details_4["seconds_duration"] = 8166
    session_details_4["session_id"] = '958dba09-c338-5118-86a3-d20a559f09c2'

    full_history[n + 6] = history_4
    full_session_history[n + 6] = session_details_4
    
    full_history[n + 7] = None
    full_session_history[n + 7] = None

    history_5 = {}
    history_5["left_apt_ankle_pitch_elasticity"] = -0.891180773774133
    history_5["left_apt_ankle_pitch_y_adf"] = -2.43515910558209
    history_5["right_apt_ankle_pitch_elasticity"] = -1.46141158488873
    history_5["right_apt_ankle_pitch_y_adf"] = -2.56962390067046

    history_5["left_hip_drop_apt_elasticity"] = 0.20416289977369
    history_5["left_hip_drop_apt_y_adf"] = 0.0
    history_5["right_hip_drop_apt_elasticity"] = 0.0
    history_5["right_hip_drop_apt_y_adf"] = 0.0

    history_5["left_hip_drop_pva_elasticity"] = 0.0
    history_5["left_hip_drop_pva_y_adf"] = 0.0
    history_5["right_hip_drop_pva_elasticity"] = 0.0
    history_5["right_hip_drop_pva_y_adf"] = -2.32138122929274

    history_5["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_5["left_knee_valgus_hip_drop_y_adf"] = -1.97735480700824
    history_5["right_knee_valgus_hip_drop_elasticity"] = 0.141232487324098
    history_5["right_knee_valgus_hip_drop_y_adf"] = -2.68913536498496

    history_5["left_knee_valgus_pva_elasticity"] = 0.0
    history_5["left_knee_valgus_pva_y_adf"] = -2.74864901159945
    history_5["right_knee_valgus_pva_elasticity"] = 0.0
    history_5["right_knee_valgus_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_apt_elasticity"] = -0.161874154731829
    history_5["left_knee_valgus_apt_y_adf"] = 0.0
    history_5["right_knee_valgus_apt_elasticity"] = -0.20458903087513
    history_5["right_knee_valgus_apt_y_adf"] = -2.56728110067398

    history_5["left_hip_rotation_ankle_pitch_elasticity"] = 1.16584437793462
    history_5["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_5["right_hip_rotation_ankle_pitch_elasticity"] = 1.31813819855037
    history_5["right_hip_rotation_ankle_pitch_y_adf"] = -2.79891654946269

    history_5["left_hip_rotation_apt_elasticity"] = 0.0
    history_5["left_hip_rotation_apt_y_adf"] = 0.0
    history_5["right_hip_rotation_apt_elasticity"] = -0.480878531935277
    history_5["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_5 = {}
    session_details_5["seconds_duration"] = 243
    session_details_5["session_id"] = 'f93e004d-7dd0-56b3-bb22-353750586f5e'

    full_history[n + 8] = history_5
    full_session_history[n + 8] = session_details_5
    full_history[n + 9] = None
    full_session_history[n + 9] = None

    history_6 = {}
    history_6["left_apt_ankle_pitch_elasticity"] = -0.343574994975232
    history_6["left_apt_ankle_pitch_y_adf"] = 0.0
    history_6["right_apt_ankle_pitch_elasticity"] = 0.0
    history_6["right_apt_ankle_pitch_y_adf"] = 0.0

    history_6["left_hip_drop_apt_elasticity"] = 0.0
    history_6["left_hip_drop_apt_y_adf"] = 0.0
    history_6["right_hip_drop_apt_elasticity"] = -0.0620144289034721
    history_6["right_hip_drop_apt_y_adf"] = 0.0

    history_6["left_hip_drop_pva_elasticity"] = -0.193114424444326
    history_6["left_hip_drop_pva_y_adf"] = 0.0
    history_6["right_hip_drop_pva_elasticity"] = -0.0750047705439414
    history_6["right_hip_drop_pva_y_adf"] = 0.0

    history_6["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_6["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_6["right_knee_valgus_hip_drop_elasticity"] = 0.152695922816337
    history_6["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_6["left_knee_valgus_pva_elasticity"] = 0.0
    history_6["left_knee_valgus_pva_y_adf"] = 0.0
    history_6["right_knee_valgus_pva_elasticity"] = 0.0
    history_6["right_knee_valgus_pva_y_adf"] = 0.0

    history_6["left_knee_valgus_apt_elasticity"] = -0.054383273746165
    history_6["left_knee_valgus_apt_y_adf"] = 0.0
    history_6["right_knee_valgus_apt_elasticity"] = -0.0877036946472387
    history_6["right_knee_valgus_apt_y_adf"] = 0.0

    history_6["left_hip_rotation_ankle_pitch_elasticity"] = 1.40767705225558
    history_6["left_hip_rotation_ankle_pitch_y_adf"] = -2.46833063247622
    history_6["right_hip_rotation_ankle_pitch_elasticity"] = 1.36207119581715
    history_6["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_6["left_hip_rotation_apt_elasticity"] = 0.0
    history_6["left_hip_rotation_apt_y_adf"] = -1.99265089264242
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
    history_7["left_apt_ankle_pitch_elasticity"] = 0.0
    history_7["left_apt_ankle_pitch_y_adf"] = 0.0
    history_7["right_apt_ankle_pitch_elasticity"] = 0.0
    history_7["right_apt_ankle_pitch_y_adf"] = 0.0

    history_7["left_hip_drop_apt_elasticity"] = 0.0
    history_7["left_hip_drop_apt_y_adf"] = 0.0
    history_7["right_hip_drop_apt_elasticity"] = 0.0
    history_7["right_hip_drop_apt_y_adf"] = 0.0

    history_7["left_hip_drop_pva_elasticity"] = 0.0
    history_7["left_hip_drop_pva_y_adf"] = 0.0
    history_7["right_hip_drop_pva_elasticity"] = 0.0
    history_7["right_hip_drop_pva_y_adf"] = 0.0

    history_7["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_7["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_7["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history_7["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_7["left_knee_valgus_pva_elasticity"] = 0.0
    history_7["left_knee_valgus_pva_y_adf"] = 0.0
    history_7["right_knee_valgus_pva_elasticity"] = 0.0
    history_7["right_knee_valgus_pva_y_adf"] = 0.0

    history_7["left_knee_valgus_apt_elasticity"] = 0.0
    history_7["left_knee_valgus_apt_y_adf"] = 0.0
    history_7["right_knee_valgus_apt_elasticity"] = 0.0
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
    history["left_apt_ankle_pitch_elasticity"] = 0.231861169949236
    history["left_apt_ankle_pitch_y_adf"] = 0.0
    history["right_apt_ankle_pitch_elasticity"] = 0.0
    history["right_apt_ankle_pitch_y_adf"] = -2.83171173263586

    history["left_hip_drop_apt_elasticity"] = -0.107214126020672
    history["left_hip_drop_apt_y_adf"] = -2.62042909205245
    history["right_hip_drop_apt_elasticity"] = -0.460236691733895
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = -0.0760781836733736
    history["left_hip_drop_pva_y_adf"] = -2.689029578307
    history["right_hip_drop_pva_elasticity"] = -0.14807671437636
    history["right_hip_drop_pva_y_adf"] = 0.0

    history["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = -0.357556927181196
    history["right_knee_valgus_pva_y_adf"] = 0.0

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = 0.0
    history["right_knee_valgus_apt_y_adf"] = 0.0

    history["left_hip_rotation_ankle_pitch_elasticity"] = -0.398625089772012
    history["left_hip_rotation_ankle_pitch_y_adf"] = -2.52965151457956
    history["right_hip_rotation_ankle_pitch_elasticity"] = 1.34483040792186
    history["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history["left_hip_rotation_apt_elasticity"] = 0.0
    history["left_hip_rotation_apt_y_adf"] = 0.0
    history["right_hip_rotation_apt_elasticity"] = 0.427811740484572
    history["right_hip_rotation_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 1073
    session_details["session_id"] = '39f243c2-6baf-5558-a2df-4f051f88c06f'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n+1] = None
    full_session_history[n+1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = 0.0
    history_2["left_apt_ankle_pitch_y_adf"] = 0.0
    history_2["right_apt_ankle_pitch_elasticity"] = 0.206490226954283
    history_2["right_apt_ankle_pitch_y_adf"] = -0.979853570007948

    history_2["left_hip_drop_apt_elasticity"] = -0.159515012897757
    history_2["left_hip_drop_apt_y_adf"] = -2.55779037795781
    history_2["right_hip_drop_apt_elasticity"] = -0.277147155116258
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = 0.0723139465482049
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
    history_2["right_knee_valgus_apt_elasticity"] = -0.251201252875501
    history_2["right_knee_valgus_apt_y_adf"] = 0.0

    history_2["left_hip_rotation_ankle_pitch_elasticity"] = 0.924804782628251
    history_2["left_hip_rotation_ankle_pitch_y_adf"] = -2.54095280579048
    history_2["right_hip_rotation_ankle_pitch_elasticity"] = 0.626882930247725
    history_2["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_rotation_apt_elasticity"] = 0.0
    history_2["left_hip_rotation_apt_y_adf"] = 0.0
    history_2["right_hip_rotation_apt_elasticity"] = 0.258772334759487
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
    history["left_apt_ankle_pitch_elasticity"] = 0.0345736161517883
    history["left_apt_ankle_pitch_y_adf"] = 0.0
    history["right_apt_ankle_pitch_elasticity"] = 0.288488188735086
    history["right_apt_ankle_pitch_y_adf"] = 0.0

    history["left_hip_drop_apt_elasticity"] = 0.135184178791529
    history["left_hip_drop_apt_y_adf"] = 0.0
    history["right_hip_drop_apt_elasticity"] = 0.196180582682485
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = 0.0510926754299412
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
    history["right_knee_valgus_apt_elasticity"] = -0.239635631923202
    history["right_knee_valgus_apt_y_adf"] = 0.0

    history["left_hip_rotation_ankle_pitch_elasticity"] = 0.0471320102970911
    history["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history["right_hip_rotation_ankle_pitch_elasticity"] = -0.731835173000968
    history["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history["left_hip_rotation_apt_elasticity"] = -0.228395501234287
    history["left_hip_rotation_apt_y_adf"] = 0.0
    history["right_hip_rotation_apt_elasticity"] = -0.531684824385146
    history["right_hip_rotation_apt_y_adf"] = 0.0

    session_details = {}
    session_details["seconds_duration"] = 8640
    session_details["session_id"] = 'c14f1728-b4f5-5fb4-845c-9dc830b3e9bf'

    full_history[n] = history
    full_session_history[n] = session_details
    full_history[n+1] = None
    full_session_history[n+1] = None

    history_2 = {}
    history_2["left_apt_ankle_pitch_elasticity"] = -2.11434616313849
    history_2["left_apt_ankle_pitch_y_adf"] = 0.0
    history_2["right_apt_ankle_pitch_elasticity"] = -1.08213397556769
    history_2["right_apt_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_drop_apt_elasticity"] = -0.0679901516786989
    history_2["left_hip_drop_apt_y_adf"] = 0.0
    history_2["right_hip_drop_apt_elasticity"] = 0.0702455572897758
    history_2["right_hip_drop_apt_y_adf"] = 0.0

    history_2["left_hip_drop_pva_elasticity"] = 0.0
    history_2["left_hip_drop_pva_y_adf"] = 0.0
    history_2["right_hip_drop_pva_elasticity"] = 0.0
    history_2["right_hip_drop_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_hip_drop_elasticity"] = 0.0223803442718253
    history_2["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_2["right_knee_valgus_hip_drop_elasticity"] = -0.0683560849790874
    history_2["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_2["left_knee_valgus_pva_elasticity"] = 0.0517439919312008
    history_2["left_knee_valgus_pva_y_adf"] = 0.0
    history_2["right_knee_valgus_pva_elasticity"] = 0.0
    history_2["right_knee_valgus_pva_y_adf"] = 0.0

    history_2["left_knee_valgus_apt_elasticity"] = 0.0654532928133672
    history_2["left_knee_valgus_apt_y_adf"] = 0.0
    history_2["right_knee_valgus_apt_elasticity"] = 0.0203455356679933
    history_2["right_knee_valgus_apt_y_adf"] = 0.0

    history_2["left_hip_rotation_ankle_pitch_elasticity"] = 0.0141245992232984
    history_2["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_2["right_hip_rotation_ankle_pitch_elasticity"] = 0.391649213479082
    history_2["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_2["left_hip_rotation_apt_elasticity"] = 0.0
    history_2["left_hip_rotation_apt_y_adf"] = 0.0
    history_2["right_hip_rotation_apt_elasticity"] = -0.0598912980114923
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
    history["left_apt_ankle_pitch_y_adf"] = -2.45761952943175
    history["right_apt_ankle_pitch_elasticity"] = 0.0
    history["right_apt_ankle_pitch_y_adf"] = 0.0

    history["left_hip_drop_apt_elasticity"] = 0.0
    history["left_hip_drop_apt_y_adf"] = 0.0
    history["right_hip_drop_apt_elasticity"] = 0.0
    history["right_hip_drop_apt_y_adf"] = 0.0

    history["left_hip_drop_pva_elasticity"] = 0.0
    history["left_hip_drop_pva_y_adf"] = 0.0
    history["right_hip_drop_pva_elasticity"] = 0.0
    history["right_hip_drop_pva_y_adf"] = -1.83154806938312

    history["left_knee_valgus_hip_drop_elasticity"] = 0.337329455016321
    history["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history["right_knee_valgus_hip_drop_elasticity"] = 0.0
    history["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history["left_knee_valgus_pva_elasticity"] = 0.0745365137141309
    history["left_knee_valgus_pva_y_adf"] = 0.0
    history["right_knee_valgus_pva_elasticity"] = 0.0
    history["right_knee_valgus_pva_y_adf"] = -1.09409318758822

    history["left_knee_valgus_apt_elasticity"] = 0.0
    history["left_knee_valgus_apt_y_adf"] = 0.0
    history["right_knee_valgus_apt_elasticity"] = 0.0
    history["right_knee_valgus_apt_y_adf"] = 0.0

    history["left_hip_rotation_ankle_pitch_elasticity"] = 1.47555114877768
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
    history_4["left_apt_ankle_pitch_elasticity"] = -0.891180773774133
    history_4["left_apt_ankle_pitch_y_adf"] = -2.43515910558209
    history_4["right_apt_ankle_pitch_elasticity"] = -1.46141158488873
    history_4["right_apt_ankle_pitch_y_adf"] = -2.56962390067046

    history_4["left_hip_drop_apt_elasticity"] = 0.20416289977369
    history_4["left_hip_drop_apt_y_adf"] = 0.0
    history_4["right_hip_drop_apt_elasticity"] = 0.0
    history_4["right_hip_drop_apt_y_adf"] = 0.0

    history_4["left_hip_drop_pva_elasticity"] = 0.0
    history_4["left_hip_drop_pva_y_adf"] = 0.0
    history_4["right_hip_drop_pva_elasticity"] = 0.0
    history_4["right_hip_drop_pva_y_adf"] = -2.32138122929274

    history_4["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_4["left_knee_valgus_hip_drop_y_adf"] = -1.97735480700824
    history_4["right_knee_valgus_hip_drop_elasticity"] = 0.141232487324098
    history_4["right_knee_valgus_hip_drop_y_adf"] = -2.68913536498496

    history_4["left_knee_valgus_pva_elasticity"] = 0.0
    history_4["left_knee_valgus_pva_y_adf"] = -2.74864901159945
    history_4["right_knee_valgus_pva_elasticity"] = 0.0
    history_4["right_knee_valgus_pva_y_adf"] = 0.0

    history_4["left_knee_valgus_apt_elasticity"] = -0.161874154731829
    history_4["left_knee_valgus_apt_y_adf"] = 0.0
    history_4["right_knee_valgus_apt_elasticity"] = -0.20458903087513
    history_4["right_knee_valgus_apt_y_adf"] = -2.56728110067398

    history_4["left_hip_rotation_ankle_pitch_elasticity"] = 1.16584437793462
    history_4["left_hip_rotation_ankle_pitch_y_adf"] = 0.0
    history_4["right_hip_rotation_ankle_pitch_elasticity"] = 1.31813819855037
    history_4["right_hip_rotation_ankle_pitch_y_adf"] = -2.79891654946269

    history_4["left_hip_rotation_apt_elasticity"] = 0.0
    history_4["left_hip_rotation_apt_y_adf"] = 0.0
    history_4["right_hip_rotation_apt_elasticity"] = -0.480878531935277
    history_4["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_4 = {}
    session_details_4["seconds_duration"] = 243
    session_details_4["session_id"] = 'f93e004d-7dd0-56b3-bb22-353750586f5e'

    full_history[n+6] = history_4
    full_session_history[n+6] = session_details_4
    full_history[n+7] = None
    full_session_history[n+7] = None

    history_5 = {}
    history_5["left_apt_ankle_pitch_elasticity"] = -0.343574994975232
    history_5["left_apt_ankle_pitch_y_adf"] = 0.0
    history_5["right_apt_ankle_pitch_elasticity"] = 0.0
    history_5["right_apt_ankle_pitch_y_adf"] = 0.0

    history_5["left_hip_drop_apt_elasticity"] = 0.0
    history_5["left_hip_drop_apt_y_adf"] = 0.0
    history_5["right_hip_drop_apt_elasticity"] = -0.0620144289034721
    history_5["right_hip_drop_apt_y_adf"] = 0.0

    history_5["left_hip_drop_pva_elasticity"] = -0.193114424444326
    history_5["left_hip_drop_pva_y_adf"] = 0.0
    history_5["right_hip_drop_pva_elasticity"] = -0.0750047705439414
    history_5["right_hip_drop_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_hip_drop_elasticity"] = 0.0
    history_5["left_knee_valgus_hip_drop_y_adf"] = 0.0
    history_5["right_knee_valgus_hip_drop_elasticity"] = 0.152695922816337
    history_5["right_knee_valgus_hip_drop_y_adf"] = 0.0

    history_5["left_knee_valgus_pva_elasticity"] = 0.0
    history_5["left_knee_valgus_pva_y_adf"] = 0.0
    history_5["right_knee_valgus_pva_elasticity"] = 0.0
    history_5["right_knee_valgus_pva_y_adf"] = 0.0

    history_5["left_knee_valgus_apt_elasticity"] = -0.054383273746165
    history_5["left_knee_valgus_apt_y_adf"] = 0.0
    history_5["right_knee_valgus_apt_elasticity"] = -0.0877036946472387
    history_5["right_knee_valgus_apt_y_adf"] = 0.0

    history_5["left_hip_rotation_ankle_pitch_elasticity"] = 1.40767705225558
    history_5["left_hip_rotation_ankle_pitch_y_adf"] = -2.46833063247622
    history_5["right_hip_rotation_ankle_pitch_elasticity"] = 1.36207119581715
    history_5["right_hip_rotation_ankle_pitch_y_adf"] = 0.0

    history_5["left_hip_rotation_apt_elasticity"] = 0.0
    history_5["left_hip_rotation_apt_y_adf"] = -1.99265089264242
    history_5["right_hip_rotation_apt_elasticity"] = 0.0
    history_5["right_hip_rotation_apt_y_adf"] = 0.0

    session_details_5 = {}
    session_details_5["seconds_duration"] = 1495
    session_details_5["session_id"] = 'f78a9e26-6003-5ac7-8590-3ae4a421dac7'

    full_history[n + 8] = history_5
    full_session_history[n + 8] = session_details_5

    return full_history, full_session_history