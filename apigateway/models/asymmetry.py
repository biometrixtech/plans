from enum import Enum
from serialisable import Serialisable
from utils import format_datetime, parse_datetime
from models.styles import BoldText


class TimeBlockDetail(object):
    def __init__(self, left, right, significant):

        self.left = left
        self.right = right
        self.significant = significant

    def json_serialise(self):
        ret = {
            'left': self.left,
            'right': self.right,
            'significant': self.significant
        }

        return ret

    # @classmethod
    # def json_deserialise(cls, input_dict):
    #     time_block = input_dict.get('time_block', 0) if input_dict.get('time_block') is not None else 0
    #     left = input_dict.get('left', 0) if input_dict.get('left') is not None else 0
    #     right = input_dict.get('right', 0) if input_dict.get('right') is not None else 0
    #     significant = input_dict.get('significant', False) if input_dict.get('time_block') is not None else False
    #
    #     asymmetry = cls(time_block, left, right, significant)
    #
    #     return asymmetry


class TimeBlockAsymmetry(Serialisable):
    def __init__(self, time_block):
        self.time_block = time_block
        self.anterior_pelvic_tilt = None
        # self.left = left
        # self.right = right
        # self.significant = significant

    def get_left(self):
        if self.anterior_pelvic_tilt is not None:
            return self.anterior_pelvic_tilt.left

    def get_right(self):
        if self.anterior_pelvic_tilt is not None:
            return self.anterior_pelvic_tilt.right

    def get_significant(self):
        if self.anterior_pelvic_tilt is not None:
            return int(self.anterior_pelvic_tilt.significant)

    def json_serialise(self, api=False):
        if api:
            ret = {
                'flag': self.get_significant(),
                'x': self.time_block,
                'y1': self.get_left(),
                'y2': -self.get_right()
            }
        else:
            ret = {
                'time_block': self.time_block,
                'anterior_pelvic_tilt': self.anterior_pelvic_tilt.json_serialise()
            }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        time_block = input_dict.get('time_block', 0) if input_dict.get('time_block') is not None else 0

        asymmetry = cls(time_block)

        left = input_dict.get('left')
        right = input_dict.get('right')
        significant = input_dict.get('significant')

        if left is not None or right is not None or significant is not None:
            anterior_pelvic_tilt = TimeBlockDetail(left, right, significant)
            asymmetry.anterior_pelvic_tilt = anterior_pelvic_tilt
        else:
            apt = input_dict.get('apt')
            if apt is not None:
                asymmetry.anterior_pelvic_tilt = TimeBlockDetail(apt.get('left', 0), apt.get('right', 0), apt.get('significant', False))

        return asymmetry


class SessionAsymmetry(Serialisable):
    def __init__(self, session_id):
        self.session_id = session_id
        self.event_date = None
        self.time_blocks = []
        self.anterior_pelvic_tilt = None
        # self.left_apt = 0
        # self.right_apt = 0
        # self.percent_events_asymmetric = 0
        # self.symmetric_events = 0
        # self.asymmetric_events = 0

        self.seconds_duration = 0

    def json_serialise(self, api=False):
        if api:
            ret = {
                'session_id': self.session_id,
                'seconds_duration': self.seconds_duration,
                'asymmetry': {
                    'apt': {
                        'detail_legend': [
                                {
                                    'color': [8, 9],
                                    'text': 'Symmetric',
                                },
                                {
                                    'color': [10, 4],
                                    'text': 'Asymmetric',
                                },
                            ],
                        'detail_data': [t.json_serialise(api) for t in self.time_blocks],
                        'detail_text': self.anterior_pelvic_tilt.get_detail_text() if self.anterior_pelvic_tilt is not None else '',
                        'detail_bold_text': [b.json_serialise() for b in self.anterior_pelvic_tilt.get_detail_bold_text() if self.anterior_pelvic_tilt is not None],
                        'detail_bold_side': self.anterior_pelvic_tilt.get_detail_bold_side() if self.anterior_pelvic_tilt is not None else ''
                    }
                }
            }
        else:
            ret = {
                'session_id': self.session_id,
                'event_date': format_datetime(self.event_date),
                'anterior_pelvic_tilt': self.anterior_pelvic_tilt.json_serialise() if self.anterior_pelvic_tilt is not None else None,
                'time_blocks': [t.json_serialise() for t in self.time_blocks],
            }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        session = cls(session_id=input_dict['session_id'])
        session.event_date = parse_datetime(input_dict['event_date']) if input_dict.get('event_date') is not None else None
        left_apt = input_dict.get('left_apt')
        right_apt = input_dict.get('right_apt')
        if left_apt is not None or right_apt is not None:
            anterior_pelvic_tilt = AnteriorPelvicTilt(left_apt, right_apt)
            anterior_pelvic_tilt.asymmetric_events = input_dict.get('asymmetric_events', 0)
            anterior_pelvic_tilt.symmetric_events = input_dict.get('symmetric_events', 0)
            anterior_pelvic_tilt.percent_events_asymmetric = input_dict.get('percent_events_asymmetric', 0)
            session.anterior_pelvic_tilt =  anterior_pelvic_tilt
        else:
            session.anterior_pelvic_tilt = AnteriorPelvicTilt.json_deserialise(
                input_dict['anterior_pelvic_tilt']) if input_dict.get('anterior_pelvic_tilt') is not None else None
        session.time_blocks = [TimeBlockAsymmetry.json_deserialise(tb) for tb in input_dict.get('time_blocks', [])]
        session.seconds_duration = input_dict.get('seconds_duration', 0)

        return session


class VisualizedLeftRightAsymmetry(object):
    def __init__(self, left_start_angle, right_start_angle, left_y, right_y):
        self.left_start_angle = round(left_start_angle, 2)
        self.right_start_angle = round(right_start_angle, 2)
        self.left_y = round(left_y, 2)
        self.right_y = round(right_y, 2)

    def json_serialise(self):
        ret = {
            "left_start_angle": self.left_start_angle,
            "left_y": self.left_y,
            "right_start_angle": self.right_start_angle,
            "right_y": self.right_y
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls(left_start_angle=input_dict.get('left_start_angle',0),
                      right_start_angle=input_dict.get('right_start_angle',0),
                      left_y=input_dict.get('left_y',0),
                      right_y=input_dict.get('right_y',0))
        return data


class Asymmetry(object):
    def __init__(self):
        self.anterior_pelvic_tilt = None
        # self.left_apt = left_apt
        # self.right_apt = right_apt
        # self.symmetric_events = 0
        # self.asymmetric_events = 0

    def json_serialise(self):
        ret = {
            "anterior_pelvic_tilt": self.anterior_pelvic_tilt.json_serialise() if self.anterior_pelvic_tilt is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        asymmetry = cls()
        left_apt = input_dict.get('left_apt')
        right_apt = input_dict.get('right_apt')
        if left_apt is not None or right_apt is not None:
            anterior_pelvic_tilt = AnteriorPelvicTilt.json_deserialise(input_dict)
            anterior_pelvic_tilt.asymmetric_events = input_dict.get("asymmetric_events", 0)
            anterior_pelvic_tilt.symmetric_events = input_dict.get("symmetric_events", 0)
            asymmetry.anterior_pelvic_tilt = anterior_pelvic_tilt
        else:
            asymmetry.anterior_pelvic_tilt = AnteriorPelvicTilt.json_deserialise(input_dict['anterior_pelvic_tilt']) if input_dict.get('anterior_pelvic_tilt') is not None else None
        return asymmetry


class AnteriorPelvicTilt(object):
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.symmetric_events = 0
        self.asymmetric_events = 0
        self.percent_events_asymmetric = 0

    def json_serialise(self):
        ret = {
            "left": self.left,
            "right": self.right,
            "asymmetric_events": self.asymmetric_events,
            "symmetric_events": self.symmetric_events
        }
        return ret

    def get_detail_text(self):

        if self.percent_events_asymmetric > 0:

            percentage = self.percent_events_asymmetric
            return str(percentage) + "% of this workout has asymmetric range of motion."

        else:

            return "We didn’t find any statistically significant pelvic range of motion asymmetry in this workout."

    def get_detail_bold_text(self):

        if self.percent_events_asymmetric > 0:

            percentage = self.percent_events_asymmetric
            bold_text = BoldText()
            bold_text.text = str(percentage) + "%"
            return [bold_text]

        else:
            return []

    def get_detail_bold_side(self):

        if self.left > self.right > 0:

            return "1"

        elif self.right > self.left > 0:

            return "2"

        else:
            return "0"

    @classmethod
    def json_deserialise(cls, input_dict):
        left_apt = input_dict.get('left_apt')
        right_apt = input_dict.get('right_apt')
        if left_apt is not None or right_apt is not None:
            asymmetry = cls(input_dict.get('left_apt', 0), input_dict.get('right_apt', 0))
        else:
            asymmetry = cls(input_dict.get('left', 0), input_dict.get('right', 0))
        asymmetry.asymmetric_events = input_dict.get("asymmetric_events", 0)
        asymmetry.symmetric_events = input_dict.get("symmetric_events", 0)
        return asymmetry


class AsymmetryType(Enum):
    anterior_pelvic_tilt = 0
    ankle_pitch = 1


class HistoricAsymmetry(Serialisable):
    def __init__(self, asymmetry_type):
        self.asymmetry_type = asymmetry_type
        self.asymmetric_events_15_days = None
        self.symmetric_events_15_days = None
        self.asymmetric_events_30_days = None
        self.symmetric_events_30_days = None

    def json_serialise(self):
        ret = {
            "asymmetry_type": self.asymmetry_type.value,
            "asymmetric_events_15_days": self.asymmetric_events_15_days,
            "symmetric_events_15_days": self.symmetric_events_15_days,
            "asymmetric_events_30_days": self.asymmetric_events_30_days,
            "symmetric_events_30_days": self.symmetric_events_30_days
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        asymmetry = cls(AsymmetryType(input_dict.get("asymmetry_type", 0)))
        asymmetry.asymmetric_events_15_days = input_dict.get("asymmetric_events_15_days")
        asymmetry.symmetric_events_15_days = input_dict.get("symmetric_events_15_days")
        asymmetry.asymmetric_events_30_days = input_dict.get("asymmetric_events_30_days")
        asymmetry.symmetric_events_30_days = input_dict.get("symmetric_events_30_days")
        return asymmetry

