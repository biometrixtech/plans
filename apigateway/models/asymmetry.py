from serialisable import Serialisable
from utils import format_datetime, parse_datetime


class TimeBlockAsymmetry(Serialisable):
    def __init__(self, time_block, left, right, significant):
        self.left = left
        self.right = right
        self.time_block = time_block
        self.significant = significant

    def json_serialise(self, api=False):
        if api:
            ret = {
                'flag': int(self.significant),
                'x': self.time_block,
                'y1': self.left,
                'y2': -self.right
            }
        else:
            ret = {
                'left': self.left,
                'right': self.right,
                'time_block': self.time_block,
                'significant': self.significant
            }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        time_block = input_dict.get('time_block', 0) if input_dict.get('time_block') is not None else 0
        left = input_dict.get('left', 0) if input_dict.get('left') is not None else 0
        right = input_dict.get('right', 0) if input_dict.get('right') is not None else 0
        significant = input_dict.get('significant', False) if input_dict.get('time_block') is not None else False

        asymmetry = cls(time_block, left, right, significant)

        return asymmetry


class SessionAsymmetry(Serialisable):
    def __init__(self, session_id):
        self.session_id = session_id
        self.event_date = None
        self.left_apt = 0
        self.right_apt = 0
        self.time_blocks = []
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
                                    'text': 'No Asymmetry Identified',
                                },
                                {
                                    'color': [1, 4],
                                    'text': 'Significant Asymmetry Identified',
                                },
                            ],
                        'detail_data': [t.json_serialise(api) for t in self.time_blocks],
                        'detail_text': {}
                    }
                }
            }
        else:
            ret = {
                'session_id': self.session_id,
                'event_date': format_datetime(self.event_date),
                'left_apt': self.left_apt,
                'right_apt': self.right_apt,
                'time_blocks': [t.json_serialise() for t in self.time_blocks],
            }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        session = cls(session_id=input_dict['session_id'])
        session.event_date = parse_datetime(input_dict['event_date']) if input_dict.get('event_date') is not None else None
        session.left_apt = input_dict.get('left_apt', 0)
        session.right_apt = input_dict.get('right_apt', 0)
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


