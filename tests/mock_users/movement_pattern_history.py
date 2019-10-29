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