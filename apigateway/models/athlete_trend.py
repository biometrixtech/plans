from enum import Enum
from models.insights import InsightType, InsightsData
from models.chart_data import TrainingVolumeChartData
from models.sport import SportName
from models.soreness import BodyPartLocationText, BodyPartSide
from models.trends_data import TrendsData
from models.trigger import TriggerType
from models.chart_data import BodyPartChartData, DataSeriesBooleanData, DataSeriesData


class LegendColor(Enum):
    green = 0
    yellow = 1
    red = 2


class LegendType(Enum):
    circle = 0
    solid_line = 1
    dashed_line = 2


class VisualizationType(Enum):
    load = 1
    session = 2
    body_part = 3
    doms = 4
    muscular_strain = 5
    sensor = 6


class DataSource(Enum):
    training_volume = 0
    pain = 1
    soreness = 2
    three_sensor = 4


class Legend(object):
    def __init(self):
        self.color = LegendColor(0)
        self.type = LegendType(0)
        self.text = ""

    def json_serialise(self):
        return {
            'color': self.color.value,
            'type': self.type.value,
            'text': self.text
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        legend = cls()
        legend.color = LegendColor(input_dict['color'])
        legend.type = LegendType(input_dict['type'])
        legend.text = input_dict['text']
        return legend


class VisualizaitonData(object):
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


class Trend(object):
    def __init__(self, trigger_type):
        self.trigger_type = trigger_type
        self.title = ""
        self.text = ""
        self.visualization_title = VisualizationTitle()
        self.visualization_type = VisualizationType(1)
        self.visualization_data = VisualizaitonData()
        self.goal_targeted = []
        self.body_parts = []
        self.sport_names = []
        self.data_source = DataSource(0)
        self.data = []

    def json_serialise(self):
        ret = {
            'trigger_type': self.trigger_type.value,
            'title': self.title,
            'text': self.text,
            'visualization_title': self.visualization_title.json_serialise(),
            'visualization_type': self.visualization_type.value,
            'visualization_data': self.visualization_data.json_serialise(),
            'goal_targeted': self.goal_targeted,
            'body_parts': [body_part.json_serialise() for body_part in self.body_parts],
            'sport_names': [sport_name.value for sport_name in self.sport_names],
            'data': [data.json_serialise() for data in self.data],
            'data_source': self.data_source.value
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend = cls(TriggerType(input_dict['trigger_type']))
        trend.title = input_dict['title']
        trend.text = input_dict['text']
        trend.visualization_title = VisualizationTitle.json_deserialise(input_dict['visualization_title'])
        trend.visualization_type = VisualizationType(input_dict['visualization_type'])
        trend.visualization_data = VisualizaitonData.json_deserialise(input_dict['visualization_data'])
        trend.goal_targeted = input_dict['goal_targeted']
        trend.body_parts = [BodyPartSide.json_deserialise(body_part) for body_part in input_dict['body_parts']]
        trend.sport_names = [SportName(sport_name) for sport_name in input_dict['sport_names']]
        trend.data_source = DataSource(input_dict.get('data_source', 0))
        if trend.visualization_type == VisualizationType.load:
            trend.data = []
        elif trend.visualization_type == VisualizationType.session:
            trend.data = [DataSeriesBooleanData.json_deserialise(body_part_data) for body_part_data in input_dict.get('data', [])]
        elif trend.visualization_type == VisualizationType.body_part:
            trend.data = [BodyPartChartData.json_deserialise(body_part_data) for body_part_data in input_dict.get('data', [])]
        elif trend.visualization_type == VisualizationType.doms:
            trend.data = []
        elif trend.visualization_type == VisualizationType.muscular_strain:
            trend.data = [DataSeriesData.json_deserialise(muscular_strain_data) for muscular_strain_data in input_dict.get('data', [])]
        elif trend.visualization_type == VisualizationType.sensor:
            trend.data = []
        else:
            trend.data = []
        return trend

    def add_data(self):
        # read insight data
        insight_data = InsightsData(self.trigger_type.value).data()
        data_source = insight_data['data_source']
        trend_data = insight_data['trend']
        self.visualization_type = VisualizationType(trend_data['visualization_type'])

        # read visualization data
        visualization_data = TrendsData(self.visualization_type.value).data()
        self.visualization_data.y_axis_1 = visualization_data['y_axis_1']
        self.visualization_data.y_axis_2 = visualization_data['y_axis_2']
        if self.visualization_type == VisualizationType.body_part:
            if data_source == 'pain':
                legends = [legend for legend in visualization_data['legend'] if legend['color'] == 2]
            else:
                legends = [legend for legend in visualization_data['legend'] if legend['color'] == 1]
        else:
            legends = visualization_data['legend']
        for legend in legends:
            self.visualization_data.plot_legends.append(Legend.json_deserialise(legend))

        self.visualization_title.text = TextGenerator.get_cleaned_text(trend_data['visualization_title'], body_parts=self.body_parts)
        self.visualization_title.body_part_text = [TextGenerator.get_body_part_text(self.body_parts)]
        self.visualization_title.color = self.visualization_data.plot_legends[0].color
        if data_source != "":
            self.data_source = DataSource[data_source]
        title = trend_data['new_title']
        text = trend_data['ongoing_body']
        self.text = TextGenerator.get_cleaned_text(text, goals=self.goal_targeted, body_parts=self.body_parts, sport_names=self.sport_names)
        self.title = TextGenerator.get_cleaned_text(title, goals=self.goal_targeted, body_parts=self.body_parts, sport_names=self.sport_names)


class TrendCategory(object):
    def __init__(self, insight_type):
        self.insight_type = insight_type
        self.goals = set()
        self.cta = []
        self.alerts = []

    def json_serialise(self):
        ret = {
            'insight_type': self.insight_type.value,
            'goals': list(self.goals),
            'cta': self.cta,
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend_category = cls(InsightType(input_dict['insight_type']))
        trend_category.goals = set(input_dict.get('goals', []))
        trend_category.cta = input_dict.get('cta', [])
        trend_category.alerts = [Trend.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
        return trend_category


class TrendsDashboard(object):
    def __init__(self):
        self.training_volume_data = []

    def json_serialise(self):
        ret = {
            'training_volume_data': [tv_data.json_serialise() for tv_data in self.training_volume_data],
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        dashboard = cls()
        dashboard.training_volume_data = [TrainingVolumeChartData.json_deserialise(tv_data) for tv_data in input_dict.get('training_volume_data', [])]
        return dashboard


class AthleteTrends(object):
    def __init__(self):
        self.dashboard = TrendsDashboard()
        self.stress = TrendCategory(InsightType.stress)
        self.response = TrendCategory(InsightType.response)
        self.biomechanics = TrendCategory(InsightType.biomechanics)
        # self.stress = None
        # self.response = None
        # self.biomechanics = None

    def json_serialise(self):
        ret = {
            'dashboard': self.dashboard.json_serialise() if self.dashboard is not None else None,
            'stress': self.stress.json_serialise() if self.stress is not None else None,
            'response': self.response.json_serialise() if self.response is not None else None,
            'biomechanics': self.biomechanics.json_serialise() if self.biomechanics is not None else None,

        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trends = cls()
        trends.dashboard = TrendsDashboard.json_deserialise(input_dict['dashboard']) if input_dict.get('dashboard', None) is not None else None
        trends.stress = TrendCategory.json_deserialise(input_dict['stress']) if input_dict.get('stress', None) is not None else None
        trends.response = TrendCategory.json_deserialise(input_dict['response']) if input_dict.get('response', None) is not None else None
        trends.biomechanics = TrendCategory.json_deserialise(input_dict['biomechanics']) if input_dict.get('biomechanics', None) is not None else None

        return trends


class TextGenerator(object):

    @classmethod
    def get_cleaned_text(cls, text, goals=None, body_parts=None, sport_names=None, severity=None):
        if body_parts is not None:
            body_part_text = cls.get_body_part_text(body_parts)
        else:
            body_part_text = ""
        if goals is not None:
            if len(goals) == 0:
                goal_text = ""
            elif len(goals) == 1:
                goal_text = goals[0]
            elif len(goals) == 2:
                goal_text = " and ".join(goals)
            else:
                joined_text = ", ".join(goals)
                pos = joined_text.rfind(",")
                goal_text = joined_text[:pos] + " and" + joined_text[pos+1:]
        else:
            goal_text = ""

        if sport_names is not None:
            sport_names = [sport_name.get_display_name() for sport_name in sport_names]
            if len(sport_names) == 0:
                sport_text = ""
            elif len(sport_names) == 1:
                sport_text = sport_names[0]
            elif len(sport_names) == 2:
                sport_text = " and ".join(sport_names)
            else:
                joined_text = ", ".join(sport_names)
                pos = joined_text.rfind(",")
                sport_text = joined_text[:pos] + " and" + joined_text[pos+1:]
        else:
            sport_text = ""

        if severity is not None:
            severity = "moderate"
        else:
            severity = "moderate"

        text = text.format(bodypart=body_part_text, sport_name=sport_text, goal=goal_text, severity=severity)
        if len(text) > 1:
            return text[0].upper() + text[1:]
        else:
            return text

    @classmethod
    def get_body_part_text(cls, body_parts):
        body_part_list = []
        body_parts.sort(key=lambda x: x.body_part_location.value, reverse=False)
        for body_part in body_parts:
            part = BodyPartLocationText(body_part.body_part_location).value()
            side = body_part.side
            if side == 1:
                body_text = " ".join(["left", part])
            elif side == 2:
                body_text = " ".join(["right", part])
            else:  # side == 0:
                body_text = part
            body_part_list.append(body_text)

        body_part_list = cls.merge_bilaterals(body_part_list)
        body_part_text = ""
        if len(body_part_list) > 2:
            joined_text = ", ".join(body_part_list)
            pos = joined_text.rfind(",")
            body_part_text = joined_text[:pos] + " and" + joined_text[pos+1:]
        elif len(body_part_list) == 2:
            if "left and right" not in body_part_list[0] and "left and right" not in body_part_list[1]:
                joined_text = ", ".join(body_part_list)
                pos = joined_text.rfind(",")
                body_part_text = joined_text[:pos] + " and" + joined_text[pos + 1:]
            else:
                body_part_text = ", ".join(body_part_list)
        elif len(body_part_list) == 1:
            body_part_text = body_part_list[0]
        return body_part_text

    @classmethod
    def merge_bilaterals(cls, body_part_list):
        last_part = ""

        for b in range(0, len(body_part_list)):

            cleaned_part = body_part_list[b].replace("left ", "").replace("right ", "")
            if cleaned_part == last_part:
                body_part_list[b] = "left and right " + cleaned_part
                body_part_list[b - 1] = ""
            last_part = cleaned_part

        new_body_part_list = [x for x in body_part_list if x != ""]

        return new_body_part_list
