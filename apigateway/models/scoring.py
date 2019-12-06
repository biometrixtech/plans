from serialisable import Serialisable
from models.styles import LegendColor, BoldText, MovementVariableType
from utils import format_date


class MovementVariableScore(Serialisable):
    def __init__(self):
        self.value = 0
        self.text = ""
        self.color = None
        self.active = False

    def json_serialise(self):
        ret = {
            'value': self.value,
            'text': self.text,
            'color': self.color.value if self.color is not None else None,
            'active': self.active
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls()
        data.value = input_dict.get('value', 0)
        data.text = input_dict.get('text', '')
        data.color = LegendColor(input_dict['color']) if input_dict.get('color') is not None else None
        data.active - input_dict.get('active', False)

        return data


class MovementSummaryPill(object):
    def __init__(self):
        self.text = ""
        self.color = None
        self.severity = 0


class MovementVariableScores(object):
    def __init__(self):
        self.asymmetry_regression_coefficient_score = 0
        self.asymmetry_medians_score = 0
        self.asymmetry_fatigue_score = 0
        self.asymmetry_score = MovementVariableScore()
        self.movement_dysfunction_score = MovementVariableScore()
        self.fatigue_score = MovementVariableScore()
        self.overall_score = MovementVariableScore()


class RecoveryQuality(Serialisable):
    def __init__(self):
        self.date = None
        self.score = MovementVariableScore()
        self.change = MovementVariableScore()
        self.summary_text = DataCardSummaryText()
        self.active = False

    def json_serialise(self):
        ret = {
            'date': format_date(self.date) if self.date is not None else None,
            'score': self.score.json_serialise() if self.score is not None else None,
            'change': self.change.json_serialise() if self.change is not None else None,
            'summary_text': self.summary_text.json_serialise() if self.summary_text is not None else None,
            'active': self.active
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls()
        data.active = input_dict.get('active', False)
        data.date = input_dict.get('date')
        data.score = MovementVariableScore.json_deserialise(input_dict['score']) if input_dict.get('score') is not None else None,
        data.change = MovementVariableScore.json_deserialise(input_dict['change']) if input_dict.get(
            'change') is not None else None,
        data.summary_text = DataCardSummaryText.json_deserialise(input_dict['summary_text']) if input_dict.get(
            'summary_text') is not None else None

        return data


class SessionScoringSummary(object):
    def __init__(self):
        self.id = ""
        self.score = MovementVariableScore()
        self.event_date_time = None
        self.duration = 0
        self.sport_name = None
        self.apt = None
        self.ankle_pitch = None
        self.hip_drop = None
        self.knee_valgus = None
        self.hip_rotation = None
        self.data_points = []  # DataPoint

    def get_data_points(self):
        page = 0
        if self.apt is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(0), index='apt', page=page))
            page += 1
        if self.hip_drop is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(2), index='hip_drop', page=page))
            page += 1
        if self.ankle_pitch is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(1), index='ankle_pitch', page=page))
            page += 1
        if self.knee_valgus is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(3), index='knee_valgus', page=page))
            page += 1
        if self.hip_rotation is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(4), index='hip_rotation', page=page))


class MovementVariableSummary(Serialisable):
    def __init__(self):
        self.active = True  # TODO: change default to False when correct logic is in place
        self.dashboard_title = ""
        self.child_title = ""
        self.description = DataCardSummaryText()
        self.score = MovementVariableScore()
        self.summary_text = MovementVariableSummaryText()
        self.change = MovementVariableScore()
        self.body_side = 0
        self.summary_data = MovementVariableSummaryData()
        self.data_cards = []  # DataCard

    def json_serialise(self):
        ret = {
            'active': self.active,
            'dashboard_title': self.dashboard_title,
            'child_title': self.child_title,
            'description': self.description.json_serialise() if self.description is not None else None,
            'score': self.score.json_serialise() if self.score is not None else None,
            'summary_text': self.summary_text.json_serialise() if self.summary_text is not None else None,
            'change': self.change.json_serialise() if self.change is not None else None,
            'body_side': self.body_side,
            'summary_data': self.summary_data.json_serialise() if self.summary_data is not None else None,
            'data_cards': [d.json_serialise() for d in self.data_cards]
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls()
        data.active = input_dict.get('active', False)
        data.dashboard_title = input_dict.get('dashboard_title', '')
        data.child_title = input_dict.get('child_title', '')
        data.description = DataCardSummaryText.json_deserialise(input_dict['description']) if input_dict.get('description') is not None else None
        data.score = MovementVariableScore.json_deserialise(input_dict['score']) if input_dict.get('score') is not None else None
        data.summary_text = MovementVariableSummaryText.json_deserialise(input_dict['summary_text']) if input_dict.get('summary_text') is not None else None
        data.change = MovementVariableScore.json_deserialise(input_dict['change']) if input_dict.get('change') is not None else None
        data.body_side = input_dict.get('body_side', 0)
        data.summary_data = MovementVariableSummaryData.json_deserialise(input_dict['summary_data']) if input_dict.get('summary_data') is not None else None
        data.data_cards = [DataCard.json_deserialise(d) for d in input_dict.get('data_cards', [])]

        return data


class MovementVariableSummaryData(Serialisable):
    def __init__(self):
        self.left_start_angle = 0
        self.left_y = 0.0
        self.left_y_legend = 0.0
        self.left_y_legend_color = None
        self.right_start_angle = 0
        self.right_y = 0.0
        self.right_y_legend = 0.0
        self.right_y_legend_color = None
        self.multiplier = 1.0

    def json_serialise(self):
        ret = {
            'left_start_angle': self.left_start_angle,
            'left_y': self.left_y,
            'left_y_legend': self.left_y_legend,
            'left_y_legend_color': self.left_y_legend_color.value if self.left_y_legend_color is not None else None,
            'right_start_angle': self.right_start_angle,
            'right_y': self.right_y,
            'right_y_legend': self.right_y_legend,
            'right_y_legend_color': self.right_y_legend_color.value if self.right_y_legend_color is not None else None,
            'multiplier': self.multiplier
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls()
        data.left_start_angle = input_dict.get('left_start_angle', 0)
        data.left_y = input_dict.get('left_y', 0.0)
        data.left_y_legend = input_dict.get('left_y_legend', 0.0)
        data.left_y_legend_color = LegendColor(input_dict['left_y_legend_color']) if input_dict.get('left_y_legend_color') is not None else None
        data.right_start_angle = input_dict.get('right_start_angle', 0)
        data.right_y = input_dict.get('right_y', 0.0)
        data.right_y_legend = input_dict.get('right_y_legend', 0.0)
        data.right_y_legend_color = LegendColor(input_dict['right_y_legend_color']) if input_dict.get(
            'right_y_legend_color') is not None else None
        data.multiplier = input_dict.get('multiplier', 1.0)

        return data


class MovementVariableSummaryText(Serialisable):
    def __init__(self):
        self.text = ""
        self.color = None
        self.bold_text = []
        self.active = False

    def json_serialise(self):
        ret = {
            'text': self.text,
            'color': self.color.value if self.color is not None else None,
            'bold_text': [b.json_serialise() for b in self.bold_text],
            'active': self.active
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls()
        data.text = input_dict.get('text', "")
        data.color = LegendColor(input_dict['color']) if input_dict.get('color') is not None else None
        data.bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_text', [])]
        data.active = input_dict.get('active', False)

        return data


class DataCard(Serialisable):
    def __init__(self, type):
        self.type = type
        self.value = 0
        self.title_text = ""
        self.color = None
        self.summary_text = DataCardSummaryText()

    def json_serialise(self):
        ret = {
            'type': self.type.value if self.type is not None else None,
            'value': self.value,
            'title_text': self.title_text,
            'color': self.color.json_serialise() if self.color is not None else None,
            'summary_text': self.summary_text.json_serialise() if self.summary_text is not None else None
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls(input_dict.get('type', None))
        data.value = input_dict.get('value', 0)
        data.title_text = input_dict.get('title_text', "")
        data.color = LegendColor(input_dict['color']) if input_dict.get('color') is not None else None
        data.summary_text = DataCardSummaryText.json_deserialise(input_dict['summary_text']) if input_dict.get('summary_text') is not None else None
        return data

    def __setattr__(self, name, value):
        if name == 'type' and value is not None and not isinstance(value, DataCardType):
            value = DataCardType(value)
        super().__setattr__(name, value)


class DataCardSummaryText(Serialisable):
    def __init__(self):
        self.text = ""
        self.bold_text = []
        self.text_items = []  # DataCardSummaryTextItem
        self.active = False

    def json_serialise(self):
        ret = {
            'text': self.text,
            'bold_text': [b.json_serialise() for b in self.bold_text],
            'text_items': [t.json_serialise() for t in self.text_items],
            'active': self.active
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls()
        data.text = input_dict.get('text', '')
        data.bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_text', '')]
        data.text_items = [DataCardSummaryTextItem.json_deserialise(b) for b in input_dict.get('text_items', '')]
        data.active = input_dict.get('active', False)

        return data


class DataCardSummaryTextItem(Serialisable):
    def __init__(self):
        self.text = ""
        self.bold_text = []

    def json_serialise(self):
        ret = {
            'text': self.text,
            'bold_text': [b.json_serialise() for b in self.bold_text]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls()
        data.text = input_dict.get('text', '')
        data.bold_text = [BoldText.json_deserialise(b) for b in input_dict.get('bold_text', '')]

        return data


class DataPoint(Serialisable):
    def __init__(self, data_type, index='', page=0):
        self.data_type = data_type
        self.index = index
        self.page = page

    def json_serialise(self):
        ret = {
            'data_type': self.data_type.value,
            'index': self.index,
            'page': self.page
        }
        return ret

    def __setattr__(self, name, value):
        if name == 'data_type' and value is not None and not isinstance(value, MovementVariableType):
            value = MovementVariableType(value)
        super().__setattr__(name, value)

    @classmethod
    def json_deserialise(cls, input_dict):
        return cls(data_type=input_dict.get('data_type'), index=input_dict.get('index', ''), page=input_dict.get('page', 0))


class DataCardType(Enum):
    categorical = 0
    magnitude = 1
    boolean = 2
