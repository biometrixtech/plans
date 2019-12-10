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
        self.ankle_pitch = None
        self.hip_drop = None
        self.knee_valgus = None
        self.hip_rotation = None
        # self.left = left
        # self.right = right
        # self.significant = significant

    def get_left(self):
        if self.anterior_pelvic_tilt is not None:
            return self.anterior_pelvic_tilt.left
        elif self.ankle_pitch is not None:
            return self.ankle_pitch.left
        elif self.hip_drop is not None:
            return self.hip_drop.left
        elif self.knee_valgus is not None:
            return self.knee_valgus.left
        elif self.hip_rotation is not None:
            return self.hip_rotation.left

    def get_right(self):
        if self.anterior_pelvic_tilt is not None:
            return self.anterior_pelvic_tilt.right
        elif self.ankle_pitch is not None:
            return self.ankle_pitch.right
        elif self.hip_drop is not None:
            return self.hip_drop.right
        elif self.knee_valgus is not None:
            return self.knee_valgus.right
        elif self.hip_rotation is not None:
            return self.hip_rotation.right

    def get_significant(self):
        if self.anterior_pelvic_tilt is not None:
            return int(self.anterior_pelvic_tilt.significant)
        elif self.ankle_pitch is not None:
            return int(self.ankle_pitch.significant)
        elif self.hip_drop is not None:
            return int(self.hip_drop.significant)
        elif self.knee_valgus is not None:
            return int(self.knee_valgus.significant)
        elif self.hip_rotation is not None:
            return int(self.hip_rotation.significant)

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
                'apt': self.anterior_pelvic_tilt.json_serialise(),
                'ankle_pitch': self.ankle_pitch.json_serialise(),
                'hip_drop': self.hip_drop.json_serialise(),
                'knee_valgus': self.knee_valgus.json_serialise(),
                'hip_rotation': self.hip_rotation.json_serialise(),
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
        ankle_pitch = input_dict.get('ankle_pitch')
        if ankle_pitch is not None:
            asymmetry.ankle_pitch = TimeBlockDetail(ankle_pitch.get('left', 0), ankle_pitch.get('right', 0),
                                                    ankle_pitch.get('significant', False))
        hip_drop = input_dict.get('hip_drop')
        if hip_drop is not None:
            asymmetry.hip_drop = TimeBlockDetail(hip_drop.get('left', 0), hip_drop.get('right', 0),
                                                 hip_drop.get('significant', False))

        knee_valgus = input_dict.get('knee_valgus')
        if knee_valgus is not None:
            asymmetry.knee_valgus = TimeBlockDetail(knee_valgus.get('left', 0), knee_valgus.get('right', 0),
                                                    knee_valgus.get('significant', False))

        hip_rotation = input_dict.get('hip_rotation')
        if hip_rotation is not None:
            asymmetry.hip_rotation = TimeBlockDetail(hip_rotation.get('left', 0), hip_rotation.get('right', 0),
                                                     hip_rotation.get('significant', False))

        return asymmetry


class SessionAsymmetry(Serialisable):
    def __init__(self, session_id):
        self.session_id = session_id
        self.event_date = None
        self.time_blocks = []
        self.anterior_pelvic_tilt = None
        self.ankle_pitch = None
        self.hip_drop = None
        self.knee_valgus = None
        self.hip_rotation = None
        # self.left_apt = 0
        # self.right_apt = 0
        # self.percent_events_asymmetric = 0
        # self.symmetric_events = 0
        # self.asymmetric_events = 0

        self.seconds_duration = 0

    def json_serialise(self, api=False, get_all=False):
        if api:
            ret = {
                'session_id': self.session_id,
                'seconds_duration': self.seconds_duration,
                'asymmetry': {}
            }
            apt = None
            ankle_pitch = None
            hip_drop = None
            knee_valgus = None
            hip_rotation = None
            if self.anterior_pelvic_tilt is not None:
                apt = self.get_mq_variable_dict(api, 'anterior_pelvic_tilt')
                # apt = self.get_apt(api)
            if self.ankle_pitch is not None:
                ankle_pitch = self.get_mq_variable_dict(api, 'ankle_pitch')
                # ankle_pitch = self.get_ankle_pitch(api)
            if self.hip_drop is not None:
                hip_drop = self.get_mq_variable_dict(api, 'hip_drop')
                # hip_drop = self.get_hip_drop(api)
            if self.knee_valgus is not None:
                knee_valgus = self.get_mq_variable_dict(api, 'knee_valgus')
                # knee_valgus = self.get_knee_valgus(api)
            if self.hip_rotation is not None:
                hip_rotation = self.get_mq_variable_dict(api, 'hip_rotation')
                # hip_rotation = self.get_hip_rotation(api)
            if get_all:
                asymmetry = {}
                asymmetry['apt'] = apt
                asymmetry['ankle_pitch'] = ankle_pitch
                asymmetry['hip_drop'] = hip_drop
                asymmetry['knee_valgus'] = knee_valgus
                asymmetry['hip_rotation'] = hip_rotation
                ret['asymmetry'] = asymmetry
            else:
                if apt is not None:
                    ret['asymmetry']['apt'] = apt
                elif ankle_pitch is not None:
                    ret['asymmetry']['ankle_pitch'] = ankle_pitch
                elif hip_drop is not None:
                    ret['asymmetry']['hip_drop'] = hip_drop
                elif knee_valgus is not None:
                    ret['asymmetry']['knee_valgus'] = knee_valgus
                elif hip_rotation is not None:
                    ret['asymmetry']['hip_rotation'] = hip_rotation



        else:
            ret = {
                'session_id': self.session_id,
                'event_date': format_datetime(self.event_date),
                'ankle_pitch': self.ankle_pitch.json_serialise() if self.ankle_pitch is not None else None,
                'apt': self.anterior_pelvic_tilt.json_serialise() if self.anterior_pelvic_tilt is not None else None,
                'hip_drop': self.hip_drop.json_serialise() if self.hip_drop is not None else None,
                'knee_valgus': self.knee_valgus.json_serialise() if self.knee_valgus is not None else None,
                'hip_rotation': self.hip_rotation.json_serialise() if self.hip_rotation is not None else None,
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
            session.anterior_pelvic_tilt = anterior_pelvic_tilt
        else:
            session.anterior_pelvic_tilt = AnteriorPelvicTilt.json_deserialise(
                input_dict['apt']) if input_dict.get('apt') is not None else None
        session.ankle_pitch = AnklePitch.json_deserialise(
                input_dict['ankle_pitch']) if input_dict.get('ankle_pitch') is not None else None
        session.hip_drop = HipDrop.json_deserialise(
                input_dict['hip_drop']) if input_dict.get('hip_drop') is not None else None
        session.knee_valgus = KneeValgus.json_deserialise(
            input_dict['knee_valgus']) if input_dict.get('knee_valgus') is not None else None
        session.hip_rotation = HipRotation.json_deserialise(
            input_dict['hip_rotation']) if input_dict.get('hip_rotation') is not None else None
        session.time_blocks = [TimeBlockAsymmetry.json_deserialise(tb) for tb in input_dict.get('time_blocks', [])]
        session.seconds_duration = input_dict.get('seconds_duration', 0)

        return session

    def get_mq_variable_dict(self, api, var):
        minutes = round(self.seconds_duration / 60)
        mq_data = getattr(self, var)
        asymmetric_minutes = round((mq_data.percent_events_asymmetric / float(100)) * minutes)
        if self.anterior_pelvic_tilt.percent_events_asymmetric > 0:
            asymmetric_minutes = max(1, asymmetric_minutes)
        return  {
                    'detail_legend': [
                        {
                            'color': [26, 4],
                            'text': 'Asymmetric Steps',
                            'active': True,
                            'flag': 1
                        },
                        {
                            'color': [11, 11],
                            'text': 'Symmetric Steps',
                            'active': False,
                            'flag': 0
                        }
                    ],
                    'detail_data': [t.json_serialise(api) for t in self.time_blocks],
                    'detail_text': mq_data.get_detail_text(asymmetric_minutes, minutes) if mq_data is not None else '',
                    # 'detail_text': "Your Pelvic Tilt was symmetric for " + str(symmetric_minutes) + " min of your " + str(minutes) + " min workout.",
                    'detail_bold_text': [b.json_serialise() for b in mq_data.get_detail_bold_text(asymmetric_minutes) if mq_data is not None],
                    'detail_bold_side': mq_data.get_detail_bold_side() if mq_data is not None else ''
                }


    # def get_apt(self, api):
    #     minutes = round(self.seconds_duration / 60)
    #
    #     asymmetric_minutes = round((self.anterior_pelvic_tilt.percent_events_asymmetric / float(100)) * minutes)
    #     if self.anterior_pelvic_tilt.percent_events_asymmetric > 0:
    #         asymmetric_minutes = max(1, asymmetric_minutes)
    #     return  {
    #                 'detail_legend': [
    #                     {
    #                         'color': [8, 9],
    #                         'text': 'Symmetric',
    #                     },
    #                     {
    #                         'color': [10, 4],
    #                         'text': 'Asymmetric',
    #                     },
    #                 ],
    #                 'detail_data': [t.json_serialise(api) for t in self.time_blocks],
    #                 'detail_text': self.anterior_pelvic_tilt.get_detail_text(asymmetric_minutes, minutes) if self.anterior_pelvic_tilt is not None else '',
    #                 # 'detail_text': "Your Pelvic Tilt was symmetric for " + str(symmetric_minutes) + " min of your " + str(minutes) + " min workout.",
    #                 'detail_bold_text': [b.json_serialise() for b in self.anterior_pelvic_tilt.get_detail_bold_text(asymmetric_minutes) if self.anterior_pelvic_tilt is not None],
    #                 'detail_bold_side': self.anterior_pelvic_tilt.get_detail_bold_side() if self.anterior_pelvic_tilt is not None else ''
    #             }
    #
    #
    # def get_ankle_pitch(self, api):
    #         minutes = round(self.seconds_duration / 60)
    #         asymmetric_minutes = round((self.ankle_pitch.percent_events_asymmetric / float(100)) * minutes)
    #         if self.ankle_pitch.percent_events_asymmetric > 0:
    #             asymmetric_minutes = max(1, asymmetric_minutes)
    #         return {
    #                 'detail_legend': [
    #                     {
    #                         'color': [8, 9],
    #                         'text': 'Symmetric',
    #                     },
    #                     {
    #                         'color': [10, 4],
    #                         'text': 'Asymmetric',
    #                     },
    #                 ],
    #                 'detail_data': [t.json_serialise(api) for t in self.time_blocks],
    #                 'detail_text': self.ankle_pitch.get_detail_text(asymmetric_minutes, minutes) if self.ankle_pitch is not None else '',
    #                 # 'detail_text': "Your Leg Extension was symmetric for " + str(
    #                 #    symmetric_minutes) + " min of your " + str(minutes) + " min workout.",
    #                 'detail_bold_text': [b.json_serialise() for b in
    #                                      self.ankle_pitch.get_detail_bold_text(asymmetric_minutes) if
    #                                      self.ankle_pitch is not None],
    #                 'detail_bold_side': self.ankle_pitch.get_detail_bold_side() if self.ankle_pitch is not None else ''
    #             }
    #
    #
    # def get_hip_drop(self, api):
    #     minutes = round(self.seconds_duration / 60)
    #     asymmetric_minutes = round((self.hip_drop.percent_events_asymmetric / float(100)) * minutes)
    #     if self.hip_drop.percent_events_asymmetric > 0:
    #         asymmetric_minutes = max(1, asymmetric_minutes)
    #     return {
    #                 'detail_legend': [
    #                     {
    #                         'color': [8, 9],
    #                         'text': 'Symmetric',
    #                     },
    #                     {
    #                         'color': [10, 4],
    #                         'text': 'Asymmetric',
    #                     },
    #                 ],
    #                 'detail_data': [t.json_serialise(api) for t in self.time_blocks],
    #                 'detail_text': self.hip_drop.get_detail_text(asymmetric_minutes, minutes) if self.hip_drop is not None else '',
    #                 # 'detail_text': "Your Leg Extension was symmetric for " + str(
    #                 #    symmetric_minutes) + " min of your " + str(minutes) + " min workout.",
    #                 'detail_bold_text': [b.json_serialise() for b in
    #                                      self.hip_drop.get_detail_bold_text(asymmetric_minutes) if
    #                                      self.hip_drop is not None],
    #                 'detail_bold_side': self.hip_drop.get_detail_bold_side() if self.hip_drop is not None else ''
    #             }
    #
    # def get_knee_valgus(self, api):
    #     minutes = round(self.seconds_duration / 60)
    #     asymmetric_minutes = round((self.knee_valgus.percent_events_asymmetric / float(100)) * minutes)
    #     if self.knee_valgus.percent_events_asymmetric > 0:
    #         asymmetric_minutes = max(1, asymmetric_minutes)
    #     return {
    #             'detail_legend': [
    #                 {
    #                     'color': [8, 9],
    #                     'text': 'Symmetric',
    #                 },
    #                 {
    #                     'color': [10, 4],
    #                     'text': 'Asymmetric',
    #                 },
    #             ],
    #             'detail_data': [t.json_serialise(api) for t in self.time_blocks],
    #             'detail_text': self.knee_valgus.get_detail_text(asymmetric_minutes, minutes) if self.knee_valgus is not None else '',
    #             'detail_bold_text': [b.json_serialise() for b in
    #                                  self.knee_valgus.get_detail_bold_text(asymmetric_minutes) if
    #                                  self.knee_valgus is not None],
    #             'detail_bold_side': self.knee_valgus.get_detail_bold_side() if self.knee_valgus is not None else ''
    #         }
    #
    # def get_hip_rotation(self, api):
    #     minutes = round(self.seconds_duration / 60)
    #     asymmetric_minutes = round((self.hip_rotation.percent_events_asymmetric / float(100)) * minutes)
    #     if self.hip_rotation.percent_events_asymmetric > 0:
    #         asymmetric_minutes = max(1, asymmetric_minutes)
    #     return {
    #             'detail_legend': [
    #                 {
    #                     'color': [8, 9],
    #                     'text': 'Symmetric',
    #                 },
    #                 {
    #                     'color': [10, 4],
    #                     'text': 'Asymmetric',
    #                 },
    #             ],
    #             'detail_data': [t.json_serialise(api) for t in self.time_blocks],
    #             'detail_text': self.hip_rotation.get_detail_text(asymmetric_minutes, minutes) if self.hip_rotation is not None else '',
    #             'detail_bold_text': [b.json_serialise() for b in
    #                                  self.hip_rotation.get_detail_bold_text(asymmetric_minutes) if
    #                                  self.hip_rotation is not None],
    #             'detail_bold_side': self.hip_rotation.get_detail_bold_side() if self.hip_rotation is not None else ''
    #             }


class VisualizedLeftRightAsymmetry(object):
    def __init__(self, left_start_angle, right_start_angle, left_y, right_y, multiplier=1.0):
        self.left_start_angle = round(left_start_angle, 2)
        self.right_start_angle = round(right_start_angle, 2)
        self.left_y = round(left_y, 2)
        self.right_y = round(right_y, 2)
        self.left_y_legend = self.left_y
        self.right_y_legend = self.right_y
        self.multiplier = multiplier

    def json_serialise(self):
        ret = {
            "left_start_angle": self.left_start_angle,
            "left_y": self.left_y,
            "left_y_legend": self.left_y_legend,
            "right_start_angle": self.right_start_angle,
            "right_y": self.right_y,
            "right_y_legend": self.right_y_legend,
            "multiplier": self.multiplier
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls(left_start_angle=input_dict.get('left_start_angle',0),
                      right_start_angle=input_dict.get('right_start_angle',0),
                      left_y=input_dict.get('left_y',0),
                      right_y=input_dict.get('right_y',0),
                      multiplier=input_dict.get('multiplier', 0))
        data.left_y_legend = input_dict.get('left_y_legend', 0)
        data.right_y_legend = input_dict.get('right_y_legend', 0)
        return data


class Asymmetry(object):
    def __init__(self):
        self.anterior_pelvic_tilt = None
        self.ankle_pitch = None
        self.hip_drop = None
        self.knee_valgus = None
        self.hip_rotation = None
        # self.left_apt = left_apt
        # self.right_apt = right_apt
        # self.symmetric_events = 0
        # self.asymmetric_events = 0

    def json_serialise(self):
        ret = {
            "apt": self.anterior_pelvic_tilt.json_serialise() if self.anterior_pelvic_tilt is not None else None,
            "ankle_pitch": self.ankle_pitch.json_serialise() if self.ankle_pitch is not None else None,
            "hip_drop": self.hip_drop.json_serialise() if self.hip_drop is not None else None,
            "knee_valgus": self.knee_valgus.json_serialise() if self.knee_valgus is not None else None,
            "hip_rotation": self.hip_rotation.json_serialise() if self.hip_rotation is not None else None,
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
            anterior_pelvic_tilt.percent_events_asymmetric = input_dict.get('percent_events_asymmetric', 0)
            asymmetry.anterior_pelvic_tilt = anterior_pelvic_tilt
        else:
            asymmetry.anterior_pelvic_tilt = AnteriorPelvicTilt.json_deserialise(input_dict['apt']) if input_dict.get('apt') is not None else None
        asymmetry.ankle_pitch = AnklePitch.json_deserialise(input_dict['ankle_pitch']) if input_dict.get('ankle_pitch') is not None else None
        asymmetry.hip_drop = HipDrop.json_deserialise(input_dict['hip_drop']) if input_dict.get(
            'hip_drop') is not None else None
        asymmetry.knee_valgus = KneeValgus.json_deserialise(input_dict['knee_valgus']) if input_dict.get(
            'knee_valgus') is not None else None
        asymmetry.hip_rotation = HipRotation.json_deserialise(input_dict['hip_rotation']) if input_dict.get(
            'hip_rotation') is not None else None
        return asymmetry


class HipRotation(object):
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
            "symmetric_events": self.symmetric_events,
            "percent_events_asymmetric": self.percent_events_asymmetric
        }
        return ret

    def get_detail_text(self, asymmetric_minutes, total_minutes):

        if self.percent_events_asymmetric > 0:

            if self.percent_events_asymmetric == 100:
                return "Your Hip Rotation was asymmetric throughout your whole workout."
            else:
                return "Your Hip Rotation was asymmetric for " + str(
                    asymmetric_minutes) + " min of your " + str(total_minutes) + " min workout."

        else:

            return "Your Hip Rotation was symmetric throughout your whole workout."

    def get_detail_bold_text(self, minutes):

        #if self.percent_events_asymmetric > 0:
        if minutes > 0:

            #percentage = self.percent_events_asymmetric
            bold_text = BoldText()
            bold_text.text = str(minutes) + " min"
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
        asymmetry = cls(input_dict.get('left', 0), input_dict.get('right', 0))
        asymmetry.asymmetric_events = input_dict.get("asymmetric_events", 0)
        asymmetry.symmetric_events = input_dict.get("symmetric_events", 0)
        asymmetry.percent_events_asymmetric = input_dict.get("percent_events_asymmetric", 0)
        return asymmetry


class KneeValgus(object):
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
            "symmetric_events": self.symmetric_events,
            "percent_events_asymmetric": self.percent_events_asymmetric
        }
        return ret

    def get_detail_text(self, asymmetric_minutes, total_minutes):

        if self.percent_events_asymmetric > 0:

            if self.percent_events_asymmetric == 100:
                return "Your Knee Valgus was asymmetric throughout your whole workout."
            else:
                return "Your Knee Valgus was asymmetric for " + str(
                    asymmetric_minutes) + " min of your " + str(total_minutes) + " min workout."

        else:

            return "Your Knee Valgus was symmetric throughout your whole workout."

    def get_detail_bold_text(self, minutes):

        #if self.percent_events_asymmetric > 0:
        if minutes > 0:

            #percentage = self.percent_events_asymmetric
            bold_text = BoldText()
            bold_text.text = str(minutes) + " min"
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
        asymmetry = cls(input_dict.get('left', 0), input_dict.get('right', 0))
        asymmetry.asymmetric_events = input_dict.get("asymmetric_events", 0)
        asymmetry.symmetric_events = input_dict.get("symmetric_events", 0)
        asymmetry.percent_events_asymmetric = input_dict.get("percent_events_asymmetric", 0)
        return asymmetry


class HipDrop(object):
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
            "symmetric_events": self.symmetric_events,
            "percent_events_asymmetric": self.percent_events_asymmetric
        }
        return ret

    def get_detail_text(self, asymmetric_minutes, total_minutes):

        if self.percent_events_asymmetric > 0:

            if self.percent_events_asymmetric == 100:
                return "Your Hip Drop was asymmetric throughout your whole workout."
            else:
                return "Your Hip Drop was asymmetric for " + str(
                    asymmetric_minutes) + " min of your " + str(total_minutes) + " min workout."

        else:

            return "Your Hip Drop was symmetric throughout your whole workout."

    def get_detail_bold_text(self, minutes):

        #if self.percent_events_asymmetric > 0:
        if minutes > 0:

            #percentage = self.percent_events_asymmetric
            bold_text = BoldText()
            bold_text.text = str(minutes) + " min"
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
        asymmetry = cls(input_dict.get('left', 0), input_dict.get('right', 0))
        asymmetry.asymmetric_events = input_dict.get("asymmetric_events", 0)
        asymmetry.symmetric_events = input_dict.get("symmetric_events", 0)
        asymmetry.percent_events_asymmetric = input_dict.get("percent_events_asymmetric", 0)
        return asymmetry


class AnklePitch(object):
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
            "symmetric_events": self.symmetric_events,
            "percent_events_asymmetric": self.percent_events_asymmetric
        }
        return ret

    def get_detail_text(self, asymmetric_minutes, total_minutes):

        if self.percent_events_asymmetric > 0:

            if self.percent_events_asymmetric == 100:
                return "Your Leg Extension was asymmetric throughout your whole workout."
            else:
                return "Your Leg Extension was asymmetric for " + str(
                    asymmetric_minutes) + " min of your " + str(total_minutes) + " min workout."

        else:

            return "Your Leg Extension was symmetric throughout your whole workout."

    def get_detail_bold_text(self, minutes):

        #if self.percent_events_asymmetric > 0:
        if minutes > 0:

            #percentage = self.percent_events_asymmetric
            bold_text = BoldText()
            bold_text.text = str(minutes) + " min"
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
        asymmetry = cls(input_dict.get('left', 0), input_dict.get('right', 0))
        asymmetry.asymmetric_events = input_dict.get("asymmetric_events", 0)
        asymmetry.symmetric_events = input_dict.get("symmetric_events", 0)
        asymmetry.percent_events_asymmetric = input_dict.get("percent_events_asymmetric", 0)
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
            "symmetric_events": self.symmetric_events,
            "percent_events_asymmetric": self.percent_events_asymmetric
        }
        return ret

    def get_detail_text(self, asymmetric_minutes, total_minutes):

        if self.percent_events_asymmetric > 0:

            if self.percent_events_asymmetric == 100:
                return "Your Pelvic Tilt was asymmetric throughout your whole workout."
            else:
                return "Your Pelvic Tilt was asymmetric for " + str(
                    asymmetric_minutes) + " min of your " + str(total_minutes) + " min workout."

        else:

            return "Your Pelvic Tilt was symmetric throughout your whole workout."

    def get_detail_bold_text(self, minutes):

        #if self.percent_events_asymmetric > 0:
        if minutes > 0:

            #percentage = self.percent_events_asymmetric
            bold_text = BoldText()
            bold_text.text = str(minutes) + " min"
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
        asymmetry.percent_events_asymmetric = input_dict.get("percent_events_asymmetric", 0)
        return asymmetry


class AsymmetryType(Enum):
    anterior_pelvic_tilt = 0
    ankle_pitch = 1
    hip_drop = 2


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

