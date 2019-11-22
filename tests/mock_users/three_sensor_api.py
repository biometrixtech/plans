from collections import OrderedDict
from tests.mock_users.movement_pattern import MovementPatterns, MovementPatternType


class ThreeSensorAPIRequestProcessor(object):
    def __init__(self, event_date, session_id, seconds_duration, end_date):
        self.event_date = event_date
        self.session_id = session_id
        self.seconds_duration = seconds_duration
        self.end_date = end_date

    def get_body(self, asymmetry_events, movement_patterns):
        body = OrderedDict()
        body["event_date"] = self.event_date
        body["session_id"] = self.session_id
        body["seconds_duration"] = self.seconds_duration
        body["end_date"] = self.end_date

        if asymmetry_events is not None:
            body['asymmetry'] = {
                "apt": {
                    "left": asymmetry_events.anterior_pelvic_tilt_summary.left,
                    "right": asymmetry_events.anterior_pelvic_tilt_summary.right,
                    "asymmetric_events": asymmetry_events.anterior_pelvic_tilt_summary.asymmetric_events,
                    "symmetric_events": asymmetry_events.anterior_pelvic_tilt_summary.symmetric_events,
                    "percent_events_asymmetric": asymmetry_events.anterior_pelvic_tilt_summary.percent_events_asymmetric
                },
                "ankle_pitch": {
                    "left": asymmetry_events.ankle_pitch_summary.left,
                    "right": asymmetry_events.ankle_pitch_summary.right,
                    "asymmetric_events": asymmetry_events.ankle_pitch_summary.asymmetric_events,
                    "symmetric_events": asymmetry_events.ankle_pitch_summary.symmetric_events,
                    "percent_events_asymmetric": asymmetry_events.ankle_pitch_summary.percent_events_asymmetric
                },
                "hip_drop": {
                    "left": asymmetry_events.hip_drop_summary.left,
                    "right": asymmetry_events.hip_drop_summary.right,
                    "asymmetric_events": asymmetry_events.hip_drop_summary.asymmetric_events,
                    "symmetric_events": asymmetry_events.hip_drop_summary.symmetric_events,
                    "percent_events_asymmetric": asymmetry_events.hip_drop_summary.percent_events_asymmetric
                }
            }
        if movement_patterns is not None:
            body['movement_patterns'] = {
                "apt_ankle_pitch": {
                    "left": {
                        "elasticity": movement_patterns.get_elasticity(1, MovementPatternType.apt_ankle_pitch),
                        "y_adf": movement_patterns.get_adf(1, MovementPatternType.apt_ankle_pitch)
                    },
                    "right": {
                        "elasticity": movement_patterns.get_elasticity(2, MovementPatternType.apt_ankle_pitch),
                        "y_adf": movement_patterns.get_adf(2, MovementPatternType.apt_ankle_pitch)
                    }
                },
                "hip_drop_apt": {
                    "left": {
                        "elasticity": movement_patterns.get_elasticity(1, MovementPatternType.hip_drop_apt),
                        "y_adf": movement_patterns.get_adf(1, MovementPatternType.hip_drop_apt)
                    },
                    "right": {
                        "elasticity": movement_patterns.get_elasticity(2, MovementPatternType.hip_drop_apt),
                        "y_adf": movement_patterns.get_adf(2, MovementPatternType.hip_drop_apt)
                    }
                },
                "hip_drop_pva": {
                    "left": {
                        "elasticity": movement_patterns.get_elasticity(1, MovementPatternType.hip_drop_pva),
                        "y_adf": movement_patterns.get_adf(1, MovementPatternType.hip_drop_pva)
                    },
                    "right": {
                        "elasticity": movement_patterns.get_elasticity(2, MovementPatternType.hip_drop_pva),
                        "y_adf": movement_patterns.get_adf(2, MovementPatternType.hip_drop_pva)
                    }
                },
                "knee_valgus_hip_drop": {
                    "left": {
                        "elasticity": movement_patterns.get_elasticity(1, MovementPatternType.knee_valgus_hip_drop),
                        "y_adf": movement_patterns.get_adf(1, MovementPatternType.knee_valgus_hip_drop)
                    },
                    "right": {
                        "elasticity": movement_patterns.get_elasticity(2, MovementPatternType.knee_valgus_hip_drop),
                        "y_adf": movement_patterns.get_adf(2, MovementPatternType.knee_valgus_hip_drop)
                    }
                },
                "knee_valgus_pva": {
                    "left": {
                        "elasticity": movement_patterns.get_elasticity(1, MovementPatternType.knee_valgus_pva),
                        "y_adf": movement_patterns.get_adf(1, MovementPatternType.knee_valgus_pva)
                    },
                    "right": {
                        "elasticity": movement_patterns.get_elasticity(2, MovementPatternType.knee_valgus_pva),
                        "y_adf": movement_patterns.get_adf(2, MovementPatternType.knee_valgus_pva)
                    }
                },
                "knee_valgus_apt": {
                    "left": {
                        "elasticity": movement_patterns.get_elasticity(1, MovementPatternType.knee_valgus_apt),
                        "y_adf": movement_patterns.get_adf(1, MovementPatternType.knee_valgus_apt)
                    },
                    "right": {
                        "elasticity": movement_patterns.get_elasticity(2, MovementPatternType.knee_valgus_apt),
                        "y_adf": movement_patterns.get_adf(2, MovementPatternType.knee_valgus_apt)
                    }
                },
            }
        return body
