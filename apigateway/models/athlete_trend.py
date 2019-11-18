from enum import Enum
from models.chart_data import TrainingVolumeChartData, BodyResponseChartData, WorkoutChartData, RecoveryChartData, Prevention3sChartData, BiomechanicsAPTChart, CareChartData, BiomechanicsAnklePitchChart, BiomechanicsHipDropChart
from models.chart_data import PreventionChartData, CareTodayChartData, PersonalizedRecoveryChartData
from models.insights import InsightType
from models.soreness_base import BodyPartSide, BodyPartSideViz
from models.sport import SportName
from models.styles import BoldText, LegendColor, Legend, VisualizationType, VisualizationData, VisualizationTitle
from models.trigger import Trigger, TriggerType
from models.trigger_data import TriggerData
from utils import format_datetime, parse_datetime
from serialisable import Serialisable


class DataSource(Enum):
    training_volume = 0
    pain = 1
    soreness = 2
    three_sensor = 4


class Insight(Serialisable):
    def __init__(self):
        self.active = False
        self.body_parts = []
        self.data = []

    def json_serialise(self):
        ret = {
            'active': self.active,
            'body_parts': [b.json_serialise() for b in self.body_parts],
            'data': [d.json_serialise() for d in self.data],
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        insight = cls()
        insight.active = input_dict['active']
        insight.body_parts = [BodyPartSideViz.json_deserialise(o) for o in input_dict.get('body_parts', [])]
        insight.data = [InsightData.json_deserialise(o) for o in input_dict.get('data', [])]

        return insight


class InsightData(Serialisable):
    def __init__(self):
        self.active = False
        self.body_parts = []
        self.color = None
        self.title = ''
        self.trigger_tiles = []
        self.visualization_data = []

    def json_serialise(self):
        ret = {
            'active': self.active,
            'body_parts': [b.json_serialise() for b in self.body_parts],
            'color': self.color.value if self.color is not None else None,
            'title': self.title,
            'trigger_tiles': [t.json_serialise() for t in self.trigger_tiles],
            'visualization_data': [v.json_serialise() for v in self.visualization_data]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        insight_data = cls()
        insight_data.active = input_dict['active']
        insight_data.body_parts = [BodyPartSideViz.json_deserialise(o) for o in input_dict.get('body_parts', [])]
        insight_data.color = LegendColor(input_dict['color']) if input_dict.get('color') is not None else None
        insight_data.title = input_dict['title']
        insight_data.trigger_tiles = [TriggerTile.json_deserialise(o) for o in input_dict.get('trigger_tiles', [])]
        insight_data.visualization_data = [InsightVisualizationData.json_deserialise(o) for o in
                                           input_dict.get('visualization_data', [])]

        return insight_data


class PlotLegend(Serialisable):
    def __init__(self, color, text, type):
        self.color = color
        self.text = text
        self.type = type

    def json_serialise(self):
        ret = {
            'color': self.color.value,
            'text': self.text,
            'type': self.type
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        plot_legend = cls(LegendColor(input_dict['color']), input_dict.get('text'), input_dict.get('type'))
        return plot_legend


class InsightVisualizationData(Serialisable):
    def __init__(self):
        self.plot_legends = []

    def json_serialise(self):
        ret = {
            'plot_legends': [p.json_serialise() for p in self.plot_legends]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        insight_viz_data = cls()
        insight_viz_data.plot_legends = [PlotLegend.json_deserialise(o) for o in input_dict.get('plot_legends', [])]
        return insight_viz_data


class Trend(object):
    def __init__(self, trigger_type):
        self.trigger_type = trigger_type
        # self.insight_type = InsightType.stress
        self.first_time_experience = False
        self.title = ""
        self.title_color = None
        self.icon = ""
        self.text = []
        self.bold_text = []
        # self.visualization_title = VisualizationTitle()
        self.visualization_type = VisualizationType(1)
        # self.visualization_data = VisualizationData()
        # self.goal_targeted = []
        # self.body_parts = []
        # self.sport_names = []
        # self.data_source = DataSource(0)
        # self.data = []
        self.trend_data = None
        # self.cta = set()
        self.priority = 0
        # self.present_in_trends = True
        # self.cleared = False
        # self.longitudinal = False
        self.last_date_time = None
        self.visible = False
        self.plan_alert_short_title = ""
        self.triggers = []
        self.trigger_tiles = []
        self.video_url = ""
        # these do not need to be persisted, used in logic only
        self.dashboard_body_part = None
        self.dashboard_body_part_text = ""
        self.top_priority_trigger = None

    def json_serialise(self):
        ret = {
            'trigger_type': self.trigger_type.value,
            'first_time_experience': self.first_time_experience,
            'title': self.title,
            'title_color': self.title_color.value if self.title_color is not None else None,
            'text': [t for t in self.text],
            'icon': self.icon,
            'bold_text': [b.json_serialise() for b in self.bold_text],
            # 'visualization_title': self.visualization_title.json_serialise(),
            'visualization_type': self.visualization_type.value,
            # 'visualization_data': self.visualization_data.json_serialise(),
            # 'goal_targeted': self.goal_targeted,
            # 'body_parts': [body_part.json_serialise() for body_part in self.body_parts],
            # 'sport_names': [sport_name.value for sport_name in self.sport_names],
            # 'data': [data.json_serialise() for data in self.data],
            'trend_data': self.trend_data.json_serialise() if self.trend_data is not None else None,
            # 'data_source': self.data_source.value,
            # 'insight_type': self.insight_type.value,
            # 'cta': list(self.cta),
            'priority': self.priority,
            # 'present_in_trends': self.present_in_trends,
            # 'cleared': self.cleared,
            # 'longitudinal': self.longitudinal,
            'last_date_time': format_datetime(self.last_date_time) if self.last_date_time is not None else None,
            'visible': self.visible,
            'plan_alert_short_title': self.plan_alert_short_title,
            'triggers': [t.json_serialise() for t in self.triggers],
            'trigger_tiles': [t.json_serialise() for t in self.trigger_tiles],
            'video_url': self.video_url
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend = cls(TriggerType(input_dict['trigger_type']))
        trend.title = input_dict.get('title', '')
        trend.first_time_experience = input_dict.get('first_time_experience', False)
        trend.title_color = LegendColor(input_dict['title_color']) if input_dict.get('title_color') is not None else None
        trend.text = input_dict.get('text', [])
        trend.icon = input_dict.get('icon', '')
        trend.bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_text', [])]
        # trend.visualization_title = VisualizationTitle.json_deserialise(input_dict['visualization_title'])
        trend.visualization_type = VisualizationType(input_dict['visualization_type'])
        # trend.visualization_data = VisualizationData.json_deserialise(input_dict['visualization_data'])
        # trend.goal_targeted = input_dict['goal_targeted']
        # trend.body_parts = [BodyPartSide.json_deserialise(body_part) for body_part in input_dict['body_parts']]
        # trend.sport_names = [SportName(sport_name) for sport_name in input_dict['sport_names']]
        # trend.data_source = DataSource(input_dict.get('data_source', 0))
        # trend.insight_type = InsightType(input_dict.get('insight_type', 0))
        trend.priority = input_dict.get('priority', 0)
        # trend.cta = set(input_dict.get('cta', []))
        # trend.present_in_trends = input_dict.get('present_in_trends', True)
        # trend.cleared = input_dict.get('cleared', False)
        # trend.longitudinal = input_dict.get('longitudinal', False)
        # if trend.visualization_type == VisualizationType.load:
        #     trend.data = []
        # elif trend.visualization_type == VisualizationType.session:
        #     trend.data = [DataSeriesBooleanData.json_deserialise(body_part_data) for body_part_data in input_dict.get('data', [])]
        # elif trend.visualization_type == VisualizationType.body_part:
        #     trend.data = [BodyPartChartData.json_deserialise(body_part_data) for body_part_data in input_dict.get('data', [])]
        # elif trend.visualization_type in [VisualizationType.doms, VisualizationType.muscular_strain]:
        #     trend.data = [DataSeriesData.json_deserialise(data) for data in input_dict.get('data', [])]
        # elif trend.visualization_type == VisualizationType.sensor:
        #     trend.data = []
        # else:
        #     trend.data = []
        trend.trend_data = TrendData.json_deserialise(input_dict.get('trend_data')) if input_dict.get('trend_data') is not None else None
        trend.last_date_time = parse_datetime(input_dict.get('last_date_time')) if input_dict.get('last_date_time') is not None else None
        trend.visible = input_dict.get('visible', False)
        trend.plan_alert_short_title = input_dict.get('plan_alert_short_tile', '')
        trend.triggers = [Trigger.json_deserialise(t) for t in input_dict.get('triggers', [])]
        trend.trigger_tiles = [TriggerTile.json_deserialise(t) for t in input_dict.get('trigger_tiles', [])]
        trend.video_url = input_dict.get('video_url', '')
        return trend

    # def add_data(self):
    #     # read insight data
    #     trigger_data = TriggerData().get_trigger_data(self.trigger_type.value)
    #     data_source = trigger_data['data_source']
    #     trend_data = trigger_data['trends']
    #     plot_data = trigger_data['plots']
    #     cta_data = trigger_data['cta']
    #     self.visualization_type = VisualizationType(plot_data['visualization_type'])

    #     # read visualization data
    #     visualization_data = TriggerData().get_visualization_data(self.visualization_type.value)
    #     self.visualization_data.y_axis_1 = visualization_data['y_axis_1']
    #     self.visualization_data.y_axis_2 = visualization_data['y_axis_2']
    #     if self.visualization_type == VisualizationType.body_part:
    #         if data_source == 'pain':
    #             legends = [legend for legend in visualization_data['legend'] if legend['color'] == 2]
    #         else:
    #             legends = [legend for legend in visualization_data['legend'] if legend['color'] == 1]
    #     else:
    #         legends = visualization_data['legend']
    #     self.visualization_data.plot_legends = [Legend.json_deserialise(legend) for legend in legends]
    #     for legend in self.visualization_data.plot_legends:
    #         legend.text = TextGenerator.get_cleaned_text(legend.text, body_parts=self.body_parts)

    #     self.visualization_title.text = TextGenerator.get_cleaned_text(plot_data['title'], body_parts=self.body_parts)
    #     self.visualization_title.body_part_text = [TextGenerator.get_body_part_text(self.body_parts)]
    #     self.visualization_title.color = self.visualization_data.plot_legends[0].color
    #     if data_source != "":
    #         self.data_source = DataSource[data_source]
    #     if self.cleared:
    #         title = trend_data['cleared_title']
    #         text = trend_data['cleared_body']
    #     else:
    #         title = trend_data['new_title']
    #         text = trend_data['ongoing_body']
    #     self.text = TextGenerator.get_cleaned_text(text, goals=self.goal_targeted, body_parts=self.body_parts, sport_names=self.sport_names)
    #     self.title = TextGenerator.get_cleaned_text(title, goals=self.goal_targeted, body_parts=self.body_parts, sport_names=self.sport_names)
    #     self.insight_type = InsightType[trigger_data['trend_type'].lower()]
    #     if trigger_data['insight_priority_trend_type'] != "":
    #         self.priority = int(trigger_data['insight_priority_trend_type'])
    #     self.present_in_trends = trend_data['present_in_trends']
    #     if trigger_data['length_of_impact'] == "multiple_days":
    #         self.longitudinal = True
    #     if cta_data['heat']:
    #         self.cta.add('heat')
    #     if cta_data['warmup']:
    #         self.cta.add('warm_up')
    #     if cta_data['cooldown']:
    #         self.cta.add('active_recovery')
    #     if cta_data['active_rest']:
    #         self.cta.add('mobilize')
    #     if cta_data['ice']:
    #         self.cta.add('ice')
    #     if cta_data['cwi']:
    #         self.cta.add('cwi')

    # def get_trigger_type_body_part_sport_tuple(self):
    #     if len(self.body_parts) != 0:
    #         body_part = self.body_parts[0]
    #     else:
    #         body_part = None
    #     return self.trigger_type, body_part


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


class PlanAlert(Serialisable):
    def __init__(self, insight_type):
        self.category = insight_type
        self.views = []
        self.text = ""
        self.bold_text = []
        self.title = ""
        self.cleared_date_time = None
        self.last_date_time = None

    def json_serialise(self):
        return {
            'category': self.category.value,
            'views': [v for v in self.views],
            'text': self.text,
            'bold_text': [b.json_serialise() for b in self.bold_text],
            'title': self.title,
            'cleared_date_time': format_datetime(self.cleared_date_time) if self.cleared_date_time is not None else None,
            'last_date_time': format_datetime(self.last_date_time) if self.last_date_time is not None else None

        }

    @classmethod
    def json_deserialise(cls, input_dict):
        plan_alert = PlanAlert(InsightType(input_dict['category']))
        plan_alert.views = [v for v in input_dict.get('views', [])]
        plan_alert.text = input_dict['text']
        plan_alert.bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_text', [])]
        plan_alert.title = input_dict.get('title', "")
        plan_alert.cleared_date_time = parse_datetime(input_dict['cleared_date_time']) if input_dict.get('cleared_date_time', None) is not None else None
        plan_alert.last_date_time = parse_datetime(input_dict['last_date_time']) if input_dict.get(
            'last_date_time', None) is not None else None
        return plan_alert


class TrendDashboardCategory(Serialisable):
    def __init__(self, insight_type):
        self.insight_type = insight_type
        self.title = ""
        self.body_part = None
        self.text = ""
        self.body_part_text = ""
        self.footer = ""
        self.color = None
        self.unread_alerts = False

    def json_serialise(self):
        ret = {
            'insight_type': self.insight_type.value,
            'title': self.title,
            'body_part': self.body_part.json_serialise() if self.body_part is not None else None,
            'text': self.text,
            'body_part_text': self.body_part_text,
            'footer': self.footer,
            'unread_alerts': self.unread_alerts
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend_category = cls(InsightType(input_dict['insight_type']))
        trend_category.title = input_dict.get('title', "")
        trend_category.body_part = BodyPartSide.json_deserialise(input_dict['body_part']) if input_dict.get('body_part') is not None else None
        trend_category.text = input_dict.get('text', "")
        trend_category.body_part_text = input_dict.get('body_part_text', "")
        trend_category.footer = input_dict.get('footer', "")
        trend_category.unread_alerts = input_dict.get('unread_alerts', False)
        return trend_category


class CategoryFirstTimeExperienceModal(Serialisable):
    def __init__(self):
        self.title = ""
        self.body = ""
        self.categories = []
        self.subtext = ""

    def json_serialise(self):
        ret = {
            'title': self.title,
            'body': self.body,
            'categories': [cat.json_serialise() for cat in self.categories],
            'subtext': self.subtext
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend_category = cls()
        trend_category.title = input_dict.get('title', "")
        trend_category.body = input_dict.get('body', "")
        trend_category.categories = [FirstTimeExperienceElement.json_deserialise(cat) for cat in input_dict.get('categories', [])]
        trend_category.subtext = input_dict.get('subtext', "")
        return trend_category


class FirstTimeExperienceElement(Serialisable):
    def __init__(self):
        self.title = ""
        self.image = ""

    def json_serialise(self):
        ret = {
            'title': self.title,
            'image': self.image
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        element = cls()
        element.title = input_dict.get('title', "")
        element.image = input_dict.get('image', "")
        return element


class TrendCategory(Serialisable):
    def __init__(self, insight_type):
        self.insight_type = insight_type
        # self.goals = set()
        # self.cta = []
        # self.alerts = []
        self.title = ""
        self.trends = []
        #self.trend_data = None  # new insights structure - will contain an Insight object which has a collection of InisightData for each data series in legend
        self.plan_alerts = []
        self.visible = False
        self.first_time_experience = False
        self.first_time_experience_modal = None

    def json_serialise(self, plan=False):
        if plan:
            plan_alerts = [plan_alert.json_serialise() for plan_alert in self.plan_alerts if plan_alert.cleared_date_time is None]
        else:
            plan_alerts = [plan_alert.json_serialise() for plan_alert in self.plan_alerts]
        ret = {
            'insight_type': self.insight_type.value,
            # 'goals': list(self.goals),
            # 'cta': [cta.json_serialise() for cta in self.cta],
            'title': self.title,
            # 'alerts': [alert.json_serialise() for alert in self.alerts],
            'trends': [trend.json_serialise() for trend in self.trends],
            #'trend_data': self.trend_data.json_serialise() if self.trend_data is not None else None,
            'plan_alerts': plan_alerts,
            'visible': self.visible,
            'first_time_experience': self.first_time_experience,
            'first_time_experience_modal': self.first_time_experience_modal.json_serialise() if self.first_time_experience_modal is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend_category = cls(InsightType(input_dict['insight_type']))
        # trend_category.goals = set(input_dict.get('goals', []))
        # trend_category.cta = [CallToAction.json_deserialise(cta) for cta in input_dict.get('cta', [])]
        # trend_category.alerts = [Trend.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
        trend_category.title = input_dict.get('title', "")
        trend_category.trends = [Trend.json_deserialise(trend) for trend in input_dict.get('trends', [])]
        #trend_category.trend_data = Insight.json_deserialise(input_dict['trend_data']) if input_dict.get('trend_data') is not None else None
        trend_category.plan_alerts = [PlanAlert.json_deserialise(alert) for alert in input_dict.get('plan_alerts', [])]
        trend_category.visible = input_dict.get('visible', False)
        trend_category.first_time_experience = input_dict.get('first_time_experience', False)
        trend_category.first_time_experience_modal = CategoryFirstTimeExperienceModal.json_deserialise(input_dict['first_time_experience_modal']) if input_dict.get('first_time_experience_modal') is not None else None
        return trend_category

    # def get_cta(self):
    #     cta_names = [alert.cta for alert in self.alerts if not alert.cleared]
    #     cta_names = set([item for items in cta_names for item in items])
    #     for cta_name in cta_names:
    #         cta_data = TriggerData().get_cta_data(cta_name)
    #         cta = CallToAction(cta_name)
    #         cta.header = cta_data['header'][self.insight_type.name]
    #         cta.benefit = cta_data['benefit'][self.insight_type.name]
    #         cta.proximity = cta_data['proximity'][self.insight_type.name]
    #         self.cta.append(cta)

    # def check_no_trend(self):
    #     data_sources = [alert.data_source for alert in self.alerts]
    #     if self.insight_type == InsightType.stress:
    #         if DataSource.training_volume not in data_sources:
    #             trend = Trend(TriggerType(201))
    #             trend.add_data()
    #             self.alerts.append(trend)
    #     elif self.insight_type == InsightType.response:
    #         if DataSource.soreness not in data_sources:
    #             trend = Trend(TriggerType(202))
    #             trend.add_data()
    #             self.alerts.append(trend)
    #         if DataSource.pain not in data_sources:
    #             trend = Trend(TriggerType(203))
    #             trend.add_data()
    #             self.alerts.append(trend)
    #     elif self.insight_type == InsightType.biomechanics:
    #         if DataSource.soreness not in data_sources:
    #             trend = Trend(TriggerType(205))
    #             trend.add_data()
    #             self.alerts.append(trend)
    #         if DataSource.pain not in data_sources:
    #             trend = Trend(TriggerType(206))
    #             trend.add_data()
    #             self.alerts.append(trend)

    # def sort_trends(self):
    #     self.alerts = sorted(self.alerts, key=lambda x: (x.priority, int(x.cleared)))

    # def remove_not_present_in_trends_page(self):
    #     self.alerts = [alert for alert in self.alerts if alert.present_in_trends]


class InsightCategory(Serialisable):
    def __init__(self, insight_type):
        self.insight_type = insight_type
        self.header = ""
        self.trend_data = None
        self.active = False
        self.first_time_experience = False
        self.first_time_experience_modal = None
        self.icon = ""
        self.image = ""
        self.context_text = ""
        self.context_bold_text = []
        self.empty_state_header = ""
        self.empty_state_image = ""
        self.empty_context_sensors_enabled = ""
        self.empty_context_sensors_not_enabled = ""
        self.empty_state_cta = ""

    def json_serialise(self):
        ret = {
            'insight_type': self.insight_type.value,
            'header': self.header,
            'trend_data': self.trend_data.json_serialise() if self.trend_data is not None else None,
            'active': self.active,
            'first_time_experience': self.first_time_experience,
            'first_time_experience_modal': self.first_time_experience_modal.json_serialise() if self.first_time_experience_modal is not None else None,
            'icon': self.icon,
            'image': self.image,
            'context_text': self.context_text,
            'context_bold_text': [b.json_serialise() for b in self.context_bold_text],
            'empty_state_header': self.empty_state_header,
            "empty_state_image": self.empty_state_image,
            'empty_context_sensors_enabled': self.empty_context_sensors_enabled,
            'empty_context_sensors_not_enabled': self.empty_context_sensors_not_enabled,
            'empty_state_cta': self.empty_state_cta
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        insight_category = cls(InsightType(input_dict['insight_type']))
        insight_category.header = input_dict.get('header', "")
        insight_category.trend_data = Insight.json_deserialise(input_dict['trend_data']) if input_dict.get('trend_data') is not None else None
        insight_category.active = input_dict.get('active', False)
        insight_category.first_time_experience = input_dict.get('first_time_experience', False)
        insight_category.first_time_experience_modal = CategoryFirstTimeExperienceModal.json_deserialise(input_dict['first_time_experience_modal']) if input_dict.get('first_time_experience_modal') is not None else None
        insight_category.icon = input_dict.get('icon','')
        insight_category.image = input_dict.get('image', '')
        insight_category.context_text = input_dict.get('context_text', '')
        insight_category.context_bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('context_bold_text', [])]
        insight_category.empty_state_header = input_dict.get('empty_state_header', '')
        insight_category.empty_state_image = input_dict.get('empty_state_image', '')
        insight_category.empty_context_sensors_enabled = input_dict.get('empty_context_sensors_enabled', '')
        insight_category.empty_context_sensors_not_enabled = input_dict.get('empty_context_sensors_not_enabled', '')
        insight_category.empty_state_cta = input_dict.get('empty_state_cta', '')
        return insight_category


class DataStatus(object):
    def __init__(self, text="", bolded_text=[], color=LegendColor(0), icon=None, sport_name=None, icon_type=None):
        self.text = text
        self.bolded_text = bolded_text
        self.color = color
        self.icon = icon
        self.sport_name = sport_name
        self.icon_type = icon_type

    def json_serialise(self):
        ret = {'text': self.text,
               'bolded_text': self.bolded_text,
               'color': self.color.value,
               'icon': self.icon,
               'sport_name': self.sport_name.value if self.sport_name is not None else None,
               'icon_type': self.icon_type}
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data_status = cls()
        data_status.text = input_dict.get('text', '')
        data_status.bolded_text = input_dict.get('bolded_text', [])
        data_status.color = LegendColor(input_dict.get('color', 0))
        data_status.icon = input_dict.get('icon', None)
        sport_name = input_dict.get('sport_name', None)
        data_status.sport_name = SportName(sport_name) if sport_name is not None else None
        data_status.icon_type = input_dict.get('icon_type', None)

        return data_status


class TriggerTile(Serialisable):
    def __init__(self):
        self.body_parts = []
        self.bold_text = []
        self.bold_title = []
        self.text = ""
        self.title = ""
        self.description = ""
        self.statistic_text = ""
        self.bold_statistic_text = []
        self.trigger_type = None
        self.sport_name = None

    def json_serialise(self):
        ret = {'text': self.text,
               'title': self.title,
               'description': self.description,
               'bold_text': [b.json_serialise() for b in self.bold_text],
               'bold_title': [b.json_serialise() for b in self.bold_title],
               'statistic_text': self.statistic_text,
               'bold_statistic_text': [b.json_serialise() for b in self.bold_statistic_text],
               'trigger_type': self.trigger_type.value if self.trigger_type is not None else None,
               'sport_name': self.sport_name.value if self.sport_name is not None else None,
               }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trigger_tile = cls()
        trigger_tile.text = input_dict.get('text', "")
        trigger_tile.title = input_dict.get('title', "")
        trigger_tile.bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_title', [])]
        trigger_tile.description = input_dict.get('description', '')
        trigger_tile.bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_text', [])]
        trigger_tile.statistic_text = input_dict.get('statistic_text', "")
        trigger_tile.bold_statistic_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_statistic_text', [])]
        trigger_tile.trigger_type = TriggerType(input_dict['trigger_type']) if input_dict.get('trigger_type') is not None else None
        sport_name = input_dict.get('sport_name', None)
        trigger_tile.sport_name = SportName(sport_name) if sport_name is not None else None
        return trigger_tile


class TrendData(object):
    def __init__(self):
        self.lockout = False
        self.status = DataStatus()
        self.text = ""
        self.title = ""
        self.title_color = None
        self.bold_text = []
        self.data = []
        self.visualization_type = VisualizationType(7)
        self.visualization_title = VisualizationTitle()
        self.visualization_data = VisualizationData()

    def json_serialise(self):
        ret = {'lockout': self.lockout,
               'visualization_title': self.visualization_title.json_serialise(),
               'visualization_type': self.visualization_type.value,
               'visualization_data': self.visualization_data.json_serialise(),
               'status': self.status.json_serialise(),
               'text': self.text,
               'title': self.title,
               'title_color': self.title_color.value if self.title_color is not None else None,
               'bold_text': [b.json_serialise() for b in self.bold_text],
               'data': [data.json_serialise() for data in self.data]
               }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend_data = cls()
        trend_data.lockout = input_dict['lockout']
        trend_data.status = DataStatus.json_deserialise(input_dict['status'])
        trend_data.visualization_type = VisualizationType(input_dict['visualization_type'])
        trend_data.text = input_dict.get('text', "")
        trend_data.title = input_dict.get('title', "")
        trend_data.title_color = LegendColor(input_dict['title_color']) if input_dict.get('title_color') is not None else None
        trend_data.bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_text', [])]
        if trend_data.visualization_type == VisualizationType.body_response:
            trend_data.data = [BodyResponseChartData.json_deserialise(data) for data in input_dict.get('data', [])]
        elif trend_data.visualization_type == VisualizationType.workload:
            trend_data.data = [WorkoutChartData.json_deserialise(data) for data in input_dict.get('data', [])]
        elif trend_data.visualization_type == VisualizationType.recovery:
            trend_data.data = [RecoveryChartData.json_deserialise(data) for data in input_dict.get('data', [])]
        elif trend_data.visualization_type == VisualizationType.prevention3s:
            trend_data.data = [Prevention3sChartData.json_deserialise(data) for data in input_dict.get('data', [])]
        elif trend_data.visualization_type == VisualizationType.care:
            trend_data.data = [CareChartData.json_deserialise(data) for data in
                               input_dict.get('data', [])]
        # old visualizations types for backward compatibility
        elif trend_data.visualization_type == VisualizationType.personalized_recovery:
            trend_data.data = [PersonalizedRecoveryChartData.json_deserialise(data) for data in input_dict.get('data', [])]
        elif trend_data.visualization_type == VisualizationType.prevention:
            trend_data.data = [PreventionChartData.json_deserialise(data) for data in input_dict.get('data', [])]
        elif trend_data.visualization_type == VisualizationType.care_today:
            trend_data.data = [CareTodayChartData.json_deserialise(data) for data in
                               input_dict.get('data', [])]

        else:
            trend_data.data = []

        trend_data.visualization_title = VisualizationTitle()
        trend_data.visualization_data = VisualizationData.json_deserialise(input_dict['visualization_data'])

        return trend_data

    def add_visualization_data(self):
        visualization_data = TriggerData().get_visualization_data(self.visualization_type.value)
        self.visualization_data.y_axis_1 = visualization_data['y_axis_1']
        self.visualization_data.y_axis_2 = visualization_data['y_axis_2']
        self.visualization_data.plot_legends = [Legend.json_deserialise(legend) for legend in visualization_data['legend']]


class TrendsDashboard(object):
    def __init__(self):
        self.training_volume_data = []
        self.trend_categories = []

    def json_serialise(self):
        ret = {
            'training_volume_data': [tv_data.json_serialise() for tv_data in self.training_volume_data],
            'trend_categories': [trend_category.json_serialise() for trend_category in self.trend_categories],
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        dashboard = cls()
        dashboard.training_volume_data = [TrainingVolumeChartData.json_deserialise(tv_data) for tv_data in input_dict.get('training_volume_data', [])]
        dashboard.trend_categories = [TrendDashboardCategory.json_deserialise(trend_category) for trend_category in
                                          input_dict.get('trend_categories', [])]
        return dashboard


class AthleteTrends(object):
    def __init__(self):
        self.dashboard = TrendsDashboard()
        self.stress = TrendCategory(InsightType.stress)
        self.response = TrendCategory(InsightType.response)
        self.biomechanics = TrendCategory(InsightType.biomechanics)
        #self.biomechanics_summary = None
        self.biomechanics_apt = None
        self.biomechanics_ankle_pitch = None
        self.biomechanics_hip_drop = None
        self.body_response = TrendData()
        self.workload = TrendData()
        self.trend_categories = []
        self.insight_categories = []

    def json_serialise(self, plan=False):
        ret = {
            'dashboard': self.dashboard.json_serialise() if self.dashboard is not None else None,
            'stress': self.stress.json_serialise() if self.stress is not None else None,
            'response': self.response.json_serialise() if self.response is not None else None,
            'biomechanics': self.biomechanics.json_serialise() if self.biomechanics is not None else None,
            'body_response': self.body_response.json_serialise() if self.body_response is not None else None,
            'workload': self.workload.json_serialise() if self.workload is not None else None,
            'trend_categories': [trend_category.json_serialise(plan) for trend_category in self.trend_categories],
            'biomechanics_apt': self.biomechanics_apt.json_serialise() if self.biomechanics_apt is not None else None,
            'biomechanics_ankle_pitch': self.biomechanics_ankle_pitch.json_serialise() if self.biomechanics_ankle_pitch is not None else None,
            'biomechanics_hip_drop': self.biomechanics_hip_drop.json_serialise() if self.biomechanics_hip_drop is not None else None,
            'insight_categories': [insight_category.json_serialise() for insight_category in self.insight_categories]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trends = cls()
        trends.dashboard = TrendsDashboard.json_deserialise(input_dict['dashboard']) if input_dict.get('dashboard', None) is not None else None
        trends.stress = TrendCategory.json_deserialise(input_dict['stress']) if input_dict.get('stress', None) is not None else None
        trends.response = TrendCategory.json_deserialise(input_dict['response']) if input_dict.get('response', None) is not None else None
        trends.biomechanics = TrendCategory.json_deserialise(input_dict['biomechanics']) if input_dict.get('biomechanics', None) is not None else None
        trends.body_response = TrendData.json_deserialise(input_dict['body_response']) if input_dict.get('body_response', None) is not None else None
        trends.workload = TrendData.json_deserialise(input_dict['workload']) if input_dict.get('workload', None) is not None else None
        trends.trend_categories = [TrendCategory.json_deserialise(trend_category) for trend_category in input_dict.get('trend_categories', [])]
        trends.insight_categories = [InsightCategory.json_deserialise(trend_category) for trend_category in
                                   input_dict.get('insight_categories', [])]
        trends.biomechanics_apt = BiomechanicsAPTChart.json_deserialise(
            input_dict['biomechanics_apt']) if input_dict.get('biomechanics_apt', None) is not None else None

        biomechanics_summary = input_dict.get('biomechanics_summary')

        if biomechanics_summary is not None:
            trends.biomechanics_apt = BiomechanicsAPTChart.json_deserialise(input_dict['biomechanics_summary']) if input_dict.get(
                'biomechanics_summary', None) is not None else None

        trends.biomechanics_ankle_pitch = BiomechanicsAnklePitchChart.json_deserialise(input_dict['biomechanics_ankle_pitch']) if input_dict.get(
            'biomechanics_ankle_pitch', None) is not None else None

        trends.biomechanics_hip_drop = BiomechanicsHipDropChart.json_deserialise(
            input_dict['biomechanics_hip_drop']) if input_dict.get(
            'biomechanics_hip_drop', None) is not None else None

        return trends

    # def add_cta(self):
    #     self.stress.get_cta()
    #     self.response.get_cta()
    #     self.biomechanics.get_cta()

    # def add_no_trigger(self):
    #     self.stress.check_no_trend()
    #     self.response.check_no_trend()
    #     self.biomechanics.check_no_trend()
    #     # pass

    # def sort_by_priority(self):
    #     self.stress.sort_trends()
    #     self.response.sort_trends()
    #     self.biomechanics.sort_trends()

    # def remove_trend_not_present_in_trends_page(self):
    #     self.stress.remove_not_present_in_trends_page()
    #     self.response.remove_not_present_in_trends_page()
    #     self.biomechanics.remove_not_present_in_trends_page()

    # def cleanup(self):
    #     self.add_cta()
    #     self.remove_trend_not_present_in_trends_page()
    #     self.add_no_trigger()
    #     self.sort_by_priority()

    def add_trend_data(self, athlete_stats):
        body_response_chart = athlete_stats.body_response_chart
        body_response = TrendData()
        if body_response_chart is not None:
            body_response.visualization_type = VisualizationType.body_response
            body_response.lockout = body_response_chart.lockout
            body_response.data = [data for data in body_response_chart.data.values()]
            body_response.add_visualization_data()

            if body_response_chart.max_value_today is None:
                    color = LegendColor(0)
                    icon_type = None
                    icon = None
            elif not body_response_chart.max_value_pain:
                if body_response_chart.max_value_today > 1:
                    color = LegendColor(5)
                    icon_type = "ionicon"
                    icon = "md-body"
                else:
                    color = LegendColor(0)
                    icon_type = None
                    icon = None
            else:
                color = LegendColor(6)
                if body_response_chart.max_value_today <= 1:
                    icon_type = "ionicon"
                    icon = "md-body"
                elif 1 < body_response_chart.max_value_today <= 3:
                    icon_type = "material-community"
                    icon = "alert"
                else:
                    icon_type = "material-community"
                    icon = "alert-octagon"
            body_response.status = DataStatus(body_response_chart.status,
                                              body_response_chart.bolded_text,
                                              color=color,
                                              icon=icon,
                                              icon_type=icon_type)
        self.body_response = body_response

        workout_chart = athlete_stats.workout_chart
        workload = TrendData()
        if workout_chart is not None:
            workload.visualization_type = VisualizationType.workload
            workload.lockout = workout_chart.lockout
            workload.data = [data for data in workout_chart.data.values()]
            workload.add_visualization_data()
            workload.status = DataStatus(workout_chart.status,
                                         workout_chart.bolded_text,
                                         color=LegendColor(4),
                                         sport_name=workout_chart.last_sport_name
                                         )
        self.workload = workload

        self.biomechanics_apt = athlete_stats.biomechanics_apt_chart
        self.biomechanics_ankle_pitch = athlete_stats.biomechanics_ankle_pitch_chart
        self.biomechanics_hip_drop = athlete_stats.biomechanics_hip_drop_chart
