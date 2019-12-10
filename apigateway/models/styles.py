from enum import Enum

from serialisable import Serialisable


class BoldText(Serialisable):
    def __init__(self):
        self.text = ""
        self.color = None

    def json_serialise(self):
        return {
            'text': self.text,
            'color': self.color.value if self.color is not None else None
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        bold_text = cls()
        bold_text.color = LegendColor(input_dict['color']) if input_dict['color'] is not None else None
        bold_text.text = input_dict['text']
        return bold_text


class LegendColor(Enum):
    green = 0
    yellow = 1
    red = 2
    slate_x_light = 3
    splash_light = 4
    warning_light = 5
    error_light = 6
    splash_x_light = 7
    purple_light_opacity = 8
    splash_light_opacity = 9
    purple_light = 10
    slate_light = 11
    slate = 12
    success_light = 13
    splash_half = 14
    splash_xx_light = 15
    warning_x_light = 16
    error_x_light = 17
    error_xx_light = 18
    splash_m_light = 19
    success_x_light = 20
    success_xx_light = 21
    warning_xx_light = 22
    yellow_light = 23
    yellow_x_light = 24
    yellow_xx_light = 25
    splash = 26
    error = 27


class Legend(object):
    def __init(self):
        self.color = LegendColor(0)
        self.type = LegendType(0)
        self.text = ""
        self.series = ""

    def json_serialise(self):
        return {
            'color': self.color.value,
            'type': self.type.value,
            'text': self.text,
            'series': self.series
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        legend = cls()
        legend.color = LegendColor(input_dict['color'])
        legend.type = LegendType(input_dict['type'])
        legend.text = input_dict['text']
        legend.series = input_dict.get('series', "")
        return legend


class LegendType(Enum):
    circle = 0
    solid_line = 1
    dashed_line = 2
    pill = 3


class VisualizationType(Enum):
    load = 1
    session = 2
    body_part = 3
    doms = 4
    muscular_strain = 5
    sensor = 6
    body_response = 7
    workload = 8
    personalized_recovery = 9
    prevention = 10
    care_today = 11
    prevention3s = 12
    recovery = 13
    care = 14
    biomechanics = 20


class VisualizationData(object):
    def __init__(self):
        self.y_axis_1 = "training volume"
        self.y_axis_2 = ""
        self.plot_legends = []

    def json_serialise(self):
        return {
            'y_axis_1': self.y_axis_1,
            'y_axis_2': self.y_axis_2,
            'plot_legends': [legend.json_serialise() for legend in self.plot_legends]
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        viz_data = cls()
        viz_data.y_axis_1 = input_dict['y_axis_1']
        viz_data.y_axis_2 = input_dict['y_axis_2']
        viz_data.plot_legends = [Legend.json_deserialise(legend) for legend in input_dict['plot_legends']]
        return viz_data


class VisualizationTitle(object):
    def __init__(self):
        self.text = ""
        self.body_part_text = []
        self.color = LegendColor(0)

    def json_serialise(self):
        return {
            'text': self.text,
            'body_part_text': self.body_part_text,
            'color': self.color.value
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        viz_title = cls()
        viz_title.text = input_dict['text']
        viz_title.body_part_text = input_dict['body_part_text']
        viz_title.color = LegendColor(input_dict['color'])
        return viz_title

class MovementVariableType(Enum):
    apt = 0
    ankle_pitch = 1
    hip_drop = 2
    knee_valgus = 3
    hip_rotation = 4
