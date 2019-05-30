from enum import Enum
from logic.text_generator import TextGenerator
from models.chart_data import BodyPartChartData, DataSeriesBooleanData, DataSeriesData, TrainingVolumeChartData
from models.insights import InsightType
from models.soreness import BodyPartSide
from models.sport import SportName
from models.trigger import TriggerType
from models.trigger_data import TriggerData


class LegendColor(Enum):
    green = 0
    yellow = 1
    red = 2
    slate = 3


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
        self.insight_type = InsightType.stress
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
        self.cta = set()
        self.priority = 0
        self.present_in_trends = True
        self.cleared = False
        self.longitudinal = False

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
            'data_source': self.data_source.value,
            'insight_type': self.insight_type.value,
            'cta': list(self.cta),
            'priority': self.priority,
            'present_in_trends': self.present_in_trends,
            'cleared': self.cleared,
            'longitudinal': self.longitudinal
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
        trend.insight_type = InsightType(input_dict.get('insight_type', 0))
        trend.priority = input_dict.get('priority', 0)
        trend.cta = set(input_dict.get('cta', []))
        trend.present_in_trends = input_dict.get('present_in_trends', True)
        trend.cleared = input_dict.get('cleared', False)
        trend.longitudinal = input_dict.get('longitudinal', False)
        if trend.visualization_type == VisualizationType.load:
            trend.data = []
        elif trend.visualization_type == VisualizationType.session:
            trend.data = [DataSeriesBooleanData.json_deserialise(body_part_data) for body_part_data in input_dict.get('data', [])]
        elif trend.visualization_type == VisualizationType.body_part:
            trend.data = [BodyPartChartData.json_deserialise(body_part_data) for body_part_data in input_dict.get('data', [])]
        elif trend.visualization_type in [VisualizationType.doms, VisualizationType.muscular_strain]:
            trend.data = [DataSeriesData.json_deserialise(data) for data in input_dict.get('data', [])]
        elif trend.visualization_type == VisualizationType.sensor:
            trend.data = []
        else:
            trend.data = []
        return trend

    def add_data(self):
        # read insight data
        trigger_data = TriggerData().get_trigger_data(self.trigger_type.value)
        data_source = trigger_data['data_source']
        trend_data = trigger_data['trends']
        plot_data = trigger_data['plots']
        cta_data = trigger_data['cta']
        self.visualization_type = VisualizationType(plot_data['visualization_type'])

        # read visualization data
        visualization_data = TriggerData().get_visualization_data(self.visualization_type.value)
        self.visualization_data.y_axis_1 = visualization_data['y_axis_1']
        self.visualization_data.y_axis_2 = visualization_data['y_axis_2']
        if self.visualization_type == VisualizationType.body_part:
            if data_source == 'pain':
                legends = [legend for legend in visualization_data['legend'] if legend['color'] == 2]
            else:
                legends = [legend for legend in visualization_data['legend'] if legend['color'] == 1]
        else:
            legends = visualization_data['legend']
        self.visualization_data.plot_legends = [Legend.json_deserialise(legend) for legend in legends]
        for legend in self.visualization_data.plot_legends:
            legend.text = TextGenerator.get_cleaned_text(legend.text, body_parts=self.body_parts)

        self.visualization_title.text = TextGenerator.get_cleaned_text(plot_data['title'], body_parts=self.body_parts)
        self.visualization_title.body_part_text = [TextGenerator.get_body_part_text(self.body_parts)]
        self.visualization_title.color = self.visualization_data.plot_legends[0].color
        if data_source != "":
            self.data_source = DataSource[data_source]
        if self.cleared:
            title = trend_data['cleared_title']
            text = trend_data['cleared_body']
        else:
            title = trend_data['new_title']
            text = trend_data['ongoing_body']
        self.text = TextGenerator.get_cleaned_text(text, goals=self.goal_targeted, body_parts=self.body_parts, sport_names=self.sport_names)
        self.title = TextGenerator.get_cleaned_text(title, goals=self.goal_targeted, body_parts=self.body_parts, sport_names=self.sport_names)
        self.insight_type = InsightType[trigger_data['trend_type'].lower()]
        if trigger_data['insight_priority_trend_type'] != "":
            self.priority = int(trigger_data['insight_priority_trend_type'])
        self.present_in_trends = trend_data['present_in_trends']
        if trigger_data['length_of_impact'] == "multiple_days":
            self.longitudinal = True
        if cta_data['heat']:
            self.cta.add('heat')
        if cta_data['warmup']:
            self.cta.add('warm_up')
        if cta_data['cooldown']:
            self.cta.add('active_recovery')
        if cta_data['active_rest']:
            self.cta.add('mobilize')
        if cta_data['ice']:
            self.cta.add('ice')
        if cta_data['cwi']:
            self.cta.add('cwi')

    def get_trigger_type_body_part_sport_tuple(self):
        if len(self.body_parts) != 0:
            body_part = self.body_parts[0]
        else:
            body_part = None
        return self.trigger_type, body_part


class CallToAction(object):
    def __init__(self, name):
        self.name = name
        self.header = ""
        self.benefit = ""
        self.proximity = ""

    def json_serialise(self):
        return {
            'name': self.name,
            'header': self.header,
            'benefit': self.benefit,
            'proximity': self.proximity
        }

    @classmethod
    def json_deserialise(cls, input_dict):
        cta = cls(input_dict['name'])
        cta.header = input_dict.get('header', "")
        cta.benefit = input_dict.get('benefit', "")
        cta.proximity = input_dict.get('proximity', "")
        return cta


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
            'cta': [cta.json_serialise() for cta in self.cta],
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend_category = cls(InsightType(input_dict['insight_type']))
        trend_category.goals = set(input_dict.get('goals', []))
        trend_category.cta = [CallToAction.json_deserialise(cta) for cta in input_dict.get('cta', [])]
        trend_category.alerts = [Trend.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
        return trend_category

    def get_cta(self):
        cta_names = [alert.cta for alert in self.alerts if not alert.cleared]
        cta_names = set([item for items in cta_names for item in items])
        for cta_name in cta_names:
            cta_data = TriggerData().get_cta_data(cta_name)
            cta = CallToAction(cta_name)
            cta.header = cta_data['header'][self.insight_type.name]
            cta.benefit = cta_data['benefit'][self.insight_type.name]
            cta.proximity = cta_data['proximity'][self.insight_type.name]
            self.cta.append(cta)

    def check_no_trend(self):
        data_sources = [alert.data_source for alert in self.alerts]
        if self.insight_type == InsightType.stress:
            if DataSource.training_volume not in data_sources:
                trend = Trend(TriggerType(201))
                trend.add_data()
                self.alerts.append(trend)
        elif self.insight_type == InsightType.response:
            if DataSource.soreness not in data_sources:
                trend = Trend(TriggerType(202))
                trend.add_data()
                self.alerts.append(trend)
            if DataSource.pain not in data_sources:
                trend = Trend(TriggerType(203))
                trend.add_data()
                self.alerts.append(trend)
        elif self.insight_type == InsightType.biomechanics:
            if DataSource.soreness not in data_sources:
                trend = Trend(TriggerType(205))
                trend.add_data()
                self.alerts.append(trend)
            if DataSource.pain not in data_sources:
                trend = Trend(TriggerType(206))
                trend.add_data()
                self.alerts.append(trend)

    def sort_trends(self):
        self.alerts = sorted(self.alerts, key=lambda x: (x.priority, -int(x.cleared)))

    def remove_not_present_in_trends_page(self):
        self.alerts = [alert for alert in self.alerts if alert.present_in_trends]


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

    def add_cta(self):
        self.stress.get_cta()
        self.response.get_cta()
        self.biomechanics.get_cta()

    def add_no_trigger(self):
        self.stress.check_no_trend()
        self.response.check_no_trend()
        self.biomechanics.check_no_trend()

    def sort_by_priority(self):
        self.stress.sort_trends()
        self.response.sort_trends()
        self.biomechanics.sort_trends()

    def remove_trend_not_present_in_trends_page(self):
        self.stress.remove_not_present_in_trends_page()
        self.response.remove_not_present_in_trends_page()
        self.biomechanics.remove_not_present_in_trends_page()

    def cleanup(self):
        self.add_cta()
        self.remove_trend_not_present_in_trends_page()
        self.add_no_trigger()
        self.sort_by_priority()
