from serialisable import Serialisable
from models.styles import LegendColor, BoldText, DataCardIcon, DataCardVisualType
from utils import format_date
from enum import Enum


class DataCardData(Enum):
    symmetry = 0
    dysfunction = 1
    fatigue = 2


class MovementVariableType(Enum):
    apt = 0
    ankle_pitch = 1
    hip_drop = 2
    knee_valgus = 3
    hip_rotation = 4


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
        data.active = input_dict.get('active', False)

        return data

    def __setattr__(self, name, value):
        if name == 'color' and value is not None and not isinstance(value, LegendColor):
            value = LegendColor(value)
        super().__setattr__(name, value)


class MovementSummaryPill(object):
    def __init__(self):
        self.text = ""
        self.color = None
        self.severity = 0

    def json_serialise(self):
        ret = {
            'text': self.text,
            'color': self.color.value if self.color is not None else None,
            'severity': self.severity
        }

        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls()
        data.text = input_dict.get('text', '')
        data.color = input_dict.get('color')

        return data

    def __setattr__(self, name, value):
        if name == 'color' and value is not None and not isinstance(value, LegendColor):
            value = LegendColor(value)
        super().__setattr__(name, value)


class MovementVariableScores(object):
    def __init__(self, var_type):
        self.movement_variable_type = var_type
        self.asymmetry_regression_coefficient_score = 0
        self.asymmetry_medians_score = 0
        self.asymmetry_fatigue_score = 0
        self.asymmetry_score = MovementVariableScore()
        self.movement_dysfunction_score = MovementVariableScore()
        self.fatigue_score = MovementVariableScore()
        self.overall_score = MovementVariableScore()
        self.change = MovementVariableScore()
        self.asymmetry_regression_coefficient_score_influencers = []
        self.asymmetry_fatigue_score_influencers = []
        self.movement_dysfunction_influencers = []
        self.fatigue_score_influencers = []
        self.medians_score_side = 0

    def __setattr__(self, name, value):
        if name == 'movement_variable_type' and value is not None and not isinstance(value, MovementVariableType):
            value = MovementVariableType(value)
        super().__setattr__(name, value)


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
        self.summary_pills = []
        self.all_data_cards = []

    def get_data_points(self):
        page = 0
        if self.apt is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(0), index='apt', page=page))
            page += 1
        if self.hip_drop is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(2), index='hip_drop', page=page))
            page += 1
        if self.knee_valgus is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(3), index='knee_valgus', page=page))
            page += 1
        if self.hip_rotation is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(4), index='hip_rotation', page=page))
            page += 1
        if self.ankle_pitch is not None:
            self.data_points.append(DataPoint(data_type=MovementVariableType(1), index='ankle_pitch', page=page))

    def get_summary_pills(self):
        symmetry_data_cards = [c for c in self.all_data_cards if c.data == DataCardData.symmetry]
        dysfunction_data_cards = [c for c in self.all_data_cards if c.data == DataCardData.dysfunction]
        fatigue_data_cards = [c for c in self.all_data_cards if c.data == DataCardData.fatigue]

        if len(symmetry_data_cards) > 0:
            worst_symmetry_category = min([c.category for c in symmetry_data_cards])
            worst_symmetry_card = [c for c in symmetry_data_cards if c.category == worst_symmetry_category][0]
            if worst_symmetry_card.value < worst_symmetry_card.max_value:
                symmetry_pill = MovementSummaryPill()
                symmetry_pill.color = worst_symmetry_card.color
                symmetry_pill.text = worst_symmetry_card.pill_text
                self.summary_pills.append(symmetry_pill)

        if len(dysfunction_data_cards) > 0:
            worst_dysfunction_category = min([c.category for c in dysfunction_data_cards])
            worst_dysfunction_card = [c for c in dysfunction_data_cards if c.category == worst_dysfunction_category][0]
            if worst_dysfunction_card.category < worst_dysfunction_card.max_value:
                dysfunction_pill = MovementSummaryPill()
                dysfunction_pill.text = worst_dysfunction_card.pill_text
                dysfunction_pill.color = worst_dysfunction_card.color
                self.summary_pills.append(dysfunction_pill)

        if len(fatigue_data_cards) > 0:
            fatigue_pill = MovementSummaryPill()
            fatigue_pill.text = "Fatigue"
            fatigue_pill.color = 5
            self.summary_pills.append(fatigue_pill)


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
        self.left_y_legend_color = LegendColor(26)
        self.right_start_angle = 0
        self.right_y = 0.0
        self.right_y_legend = 0.0
        self.right_y_legend_color = LegendColor(7)
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
    def __init__(self, card_type):
        self.type = card_type
        self.value = 0
        self.title_text = ""
        self.color = None
        self.summary_text = DataCardSummaryText()
        self.icon = None
        self.max_value = None
        self.data = None
        self.score = None
        self.pill_text = ""
        self.movement_variable = None
        self.category = 0
        self.movement_scores = None

    def json_serialise(self):
        ret = {
            'type': self.type.value if self.type is not None else None,
            'value': self.value,
            'title_text': self.title_text,
            'color': self.color.value if self.color is not None else None,
            'summary_text': self.summary_text.json_serialise() if self.summary_text is not None else None,
            'icon': self.icon.value if self.icon is not None else None,
            'max_value': self.max_value
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        data = cls(input_dict.get('type', None))
        data.value = input_dict.get('value', 0)
        data.title_text = input_dict.get('title_text', "")
        data.color = LegendColor(input_dict['color']) if input_dict.get('color') is not None else None
        data.summary_text = DataCardSummaryText.json_deserialise(input_dict['summary_text']) if input_dict.get('summary_text') is not None else None
        data.icon = input_dict.get('icon')
        data.max_value = input_dict.get('max_value')
        return data

    def __setattr__(self, name, value):
        if name == 'type' and value is not None and not isinstance(value, DataCardVisualType):
            value = DataCardVisualType(value)
        elif name == 'color' and value is not None and not isinstance(value, LegendColor):
            value = LegendColor(value)
        elif name == 'icon' and value is not None and not isinstance(value, DataCardIcon):
            value = DataCardIcon(value)
        super().__setattr__(name, value)

    def assign_score_value(self, score):
        self.score = score
        if self.data == DataCardData.symmetry:
            self.max_value = 4
            if score is not None:
                if score == 100:
                    self.value = 4
                    self.category = 4
                    self.title_text = "Symmetric Movement"
                    self.pill_text = ""
                    self.color = 13
                elif score > 75:
                    self.value = 3
                    self.category = 3
                    self.title_text = "Slightly Asymmetric Movement"
                    self.pill_text = "Slight Asymmetry"
                    self.color = 23
                elif score > 60:
                    self.value = 2
                    self.category = 2
                    self.title_text = "Moderately Asymmetric Movement"
                    self.pill_text = "Moderate Asymmetry"
                    self.color = 5
                elif score > 50:
                    self.value = 1
                    self.category = 1
                    self.title_text = "Excessively Asymmetric Movement"
                    self.pill_text = "Excessive Asymmetry"
                    self.color = 6
                else:
                    self.value = 1
                    self.category = 0
                    self.title_text = "Extremely Asymmetric Movement"
                    self.pill_text = "Severe Asymmetry"
                    self.color = 27
            else:
                self.value = 4
                self.category = 4
                self.title_text = "Symmetric Movement"
                self.pill_text = ""
                self.color = 13
        elif self.data == DataCardData.dysfunction:
            self.max_value = 3
            if score is not None:
                self.value = score
                if score > 99:
                    self.color = 13
                    self.title_text = "Functional Movement"
                    self.pill_text = ""
                    self.category = 3
                elif score > 80:
                    self.color = 23
                    self.title_text = "Slightly Maladapted Movement"
                    self.pill_text = "Slight Dysfunction"
                    self.category = 2
                elif score > 65:
                    self.color = 5
                    self.title_text = "Moderately Maladapted Movement"
                    self.pill_text = "Moderate Dysfunction"
                    self.category = 1
                else:
                    self.color = 6
                    self.title_text = "Excessively Maladapted Movement"
                    self.pill_text = "Excessive Dysfunction"
                    self.category = 0
            else:
                self.value = 100
                self.color = 13
                self.title_text = "Functional Movement"
                self.pill_text = ""
                self.category = 3

    def get_symmetry_text(self, movement_scores):

        if self.movement_variable is not None:
            if self.movement_variable == MovementVariableType.apt:
                self.get_apt_symmetry_text(movement_scores)
            elif self.movement_variable == MovementVariableType.ankle_pitch:
                self.get_ankle_pitch_symmetry_text(movement_scores)
            elif self.movement_variable == MovementVariableType.hip_drop:
                self.get_hip_drop_symmetry_text(movement_scores)
            elif self.movement_variable == MovementVariableType.knee_valgus:
                self.get_knee_valgus_symmetry_text(movement_scores)
            elif self.movement_variable == MovementVariableType.hip_rotation:
                self.get_hip_rotation_symmetry_text(movement_scores)

    def get_dysfunction_text(self, movement_scores):

        if self.movement_variable is not None:
            if self.movement_variable == MovementVariableType.apt:
                self.get_apt_dysfunction_text(movement_scores)
            elif self.movement_variable == MovementVariableType.ankle_pitch:
                self.get_ankle_pitch_dysfunction_text(movement_scores)
            elif self.movement_variable == MovementVariableType.hip_drop:
                self.get_hip_drop_dysfunction_text(movement_scores)
            elif self.movement_variable == MovementVariableType.knee_valgus:
                self.get_knee_valgus_dysfunction_text(movement_scores)
            elif self.movement_variable == MovementVariableType.hip_rotation:
                self.get_hip_rotation_dysfunction_text(movement_scores)

    def get_fatigue_text(self):

        if self.movement_variable is not None:
            if self.movement_variable == MovementVariableType.apt:
                self.summary_text.text = "We noticied a significant change in your Pelvic Tilt range of motion over the course of your run."
                text_item = DataCardSummaryTextItem()
                text_item.text = "This may have been due to insufficient musclar endurance in xyz, or inadequate preparation for training."
                self.summary_text.text_items.append(text_item)
                self.summary_text.active = True
            elif self.movement_variable == MovementVariableType.ankle_pitch:
                self.summary_text.text = "Lorem ipsum iolor sit amet, consetetur saiipscing elitr, sed dia elitr, sed dia seri"
                self.summary_text.active = True
            elif self.movement_variable == MovementVariableType.hip_drop:
                self.summary_text.text = "Lorem ipsum iolor sit amet, consetetur saiipscing elitr, sed dia elitr, sed dia seri"
                self.summary_text.active = True
            elif self.movement_variable == MovementVariableType.knee_valgus:
                self.summary_text.text = "Lorem ipsum iolor sit amet, consetetur saiipscing elitr, sed dia elitr, sed dia seri"
                self.summary_text.active = True
            elif self.movement_variable == MovementVariableType.hip_rotation:
                self.summary_text.text = "Lorem ipsum iolor sit amet, consetetur saiipscing elitr, sed dia elitr, sed dia seri"
                self.summary_text.active = True

    def get_apt_symmetry_text(self, movement_scores=None):
        if self.category == 4:  # APT asymmetry not present
            self.summary_text.text = "Your pelvic tilt did not differ between your left and right ground contacts."
            self.summary_text.active = True
        elif self.category == 3:  # APT asymmetry lowest
            self.summary_text.text = "Your pelvic tilt differed slightly for left vs right ground contacts, distributing stress through your body unevenly. A pattern of this can lead to injury and interferes with optimal performance."
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "Your pelvic tilt differed moderately for left vs right ground contacts, distributing stress through your body unevenly. A pattern of this can lead to injury and interferes with optimal performance."
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "Your pelvic tilt differed excessively for left vs right ground contacts, distributing stress through your body unevenly. A pattern of this can lead to injury and interferes with optimal performance."
            self.summary_text.active = True
        elif self.category == 0:  # APT asymmetry highest
            self.summary_text.text = "Your pelvic tilt differed extremely for left vs right ground contacts, distributing stress through your body unevenly. A pattern of this can lead to injury and interferes with optimal performance."
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 4:
            # add elasticity diff bullet
            for influencer in movement_scores.asymmetry_regression_coefficient_score_influencers:
                text_item = DataCardSummaryTextItem()
                if influencer.side == 1:
                    text_item.text = "you displayed more severe signs of movement impairement during left steps vs right steps"
                else:
                    text_item.text = "you displayed more severe signs of movement impairement during right steps vs left steps"
                self.summary_text.text_items.append(text_item)
            # add medians score bullet
            if movement_scores.medians_score_side == 1:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during left foot steps"
                self.summary_text.text_items.append(text_item)
            elif movement_scores.medians_score_side == 2:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during right foot steps"
                self.summary_text.text_items.append(text_item)
            # add fatigue bullet
            if len(movement_scores.asymmetry_fatigue_score_influencers) > 0:
                influencer = movement_scores.asymmetry_fatigue_score_influencers[0]
                text_item = DataCardSummaryTextItem()
                if influencer.side == 1:
                    text_item.text = "your Pelvic Tilt range of motion during left steps had a more significant change over the course of your run than your right steps"
                else:
                    text_item.text = "your Pelvic Tilt range of motion during right steps had a more significant change over the course of your run than your left steps"
                self.summary_text.text_items.append(text_item)

    def get_ankle_pitch_symmetry_text(self, movement_scores=None):
        if self.category == 4:  # ankle_pitch asymmetry not present
            self.summary_text.text = "4 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 3:  # ankle_pitch asymmetry lowest
            self.summary_text.text = "3 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "2 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "1 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 0:  # ankle_pitch asymmetry highest
            self.summary_text.text = "0 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 4:
            # add elasticity diff bullet
            for influencer in movement_scores.asymmetry_regression_coefficient_score_influencers:
                if influencer.equation_type == EquationType.apt_ankle_pitch:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
                elif influencer.equation_type == EquationType.hip_rotation_ankle_pitch:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
            # add medians score bullet
            if movement_scores.medians_score_side == 1:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during left foot steps"
                self.summary_text.text_items.append(text_item)
            elif movement_scores.medians_score_side == 2:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during right foot steps"
                self.summary_text.text_items.append(text_item)
            # add fatigue bullet
            if len(movement_scores.asymmetry_fatigue_score_influencers) > 0:
                influencer = movement_scores.asymmetry_fatigue_score_influencers[0]
                text_item = DataCardSummaryTextItem()
                if influencer.side == 1:
                    text_item.text = f"{influencer.equation_type.name}, left, fatigue"
                else:
                    text_item.text = f"{influencer.equation_type.name}, right, fatigue"
                self.summary_text.text_items.append(text_item)

    def get_hip_drop_symmetry_text(self, movement_scores=None):
        if self.category == 4:  # hip_drop asymmetry not present
            self.summary_text.text = "4 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 3:  # hip_drop asymmetry lowest
            self.summary_text.text = "3 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "2 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "1 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 0:  # hip_drop asymmetry highest
            self.summary_text.text = "0 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 4:
            # add elasticity diff bullet
            for influencer in movement_scores.asymmetry_regression_coefficient_score_influencers:
                if influencer.equation_type == EquationType.hip_drop_apt:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
                elif influencer.equation_type == EquationType.hip_drop_pva:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
            # add medians score bullet
            if movement_scores.medians_score_side == 1:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during left foot steps"
                self.summary_text.text_items.append(text_item)
            elif movement_scores.medians_score_side == 2:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during right foot steps"
                self.summary_text.text_items.append(text_item)
            # add fatigue bullet
            if len(movement_scores.asymmetry_fatigue_score_influencers) > 0:
                influencer = movement_scores.asymmetry_fatigue_score_influencers[0]
                text_item = DataCardSummaryTextItem()
                if influencer.side == 1:
                    text_item.text = f"{influencer.equation_type.name}, left, fatigue"
                else:
                    text_item.text = f"{influencer.equation_type.name}, right, fatigue"
                self.summary_text.text_items.append(text_item)

    def get_knee_valgus_symmetry_text(self, movement_scores=None):
        if self.category == 4:  # knee_valgus asymmetry lowest
            self.summary_text.text = "4 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 3:  # knee_valgus asymmetry lowest
            self.summary_text.text = "3 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "2 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "1 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 0:  # knee_valgus asymmetry highest
            self.summary_text.text = "0 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 4:
            # add elasticity diff bullet
            for influencer in movement_scores.asymmetry_regression_coefficient_score_influencers:
                if influencer.equation_type == EquationType.knee_valgus_hip_drop:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
                elif influencer.equation_type == EquationType.knee_valgus_pva:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
                elif influencer.equation_type == EquationType.knee_valgus_apt:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
            # add medians score bullet
            if movement_scores.medians_score_side == 1:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during left foot steps"
                self.summary_text.text_items.append(text_item)
            elif movement_scores.medians_score_side == 2:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during right foot steps"
                self.summary_text.text_items.append(text_item)
            # add fatigue bullet
            if len(movement_scores.asymmetry_fatigue_score_influencers) > 0:
                influencer = movement_scores.asymmetry_fatigue_score_influencers[0]
                text_item = DataCardSummaryTextItem()
                if influencer.side == 1:
                    text_item.text = f"{influencer.equation_type.name}, left, fatigue"
                else:
                    text_item.text = f"{influencer.equation_type.name}, right, fatigue"
                self.summary_text.text_items.append(text_item)

    def get_hip_rotation_symmetry_text(self, movement_scores=None):
        if self.category == 4:  # hip_rotation asymmetry not present
            self.summary_text.text = "4 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 3:  # hip_rotation asymmetry lowest
            self.summary_text.text = "3 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "2 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "1 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 0:  # hip_rotation asymmetry highest
            self.summary_text.text = "0 ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 4:
            # add elasticity diff bullet
            for influencer in movement_scores.asymmetry_regression_coefficient_score_influencers:
                if influencer.equation_type == EquationType.hip_rotation_ankle_pitch:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
                elif influencer.equation_type == EquationType.hip_rotation_apt:
                    text_item = DataCardSummaryTextItem()
                    if influencer.side == 1:
                        text_item.text = f"{influencer.equation_type.name}, left, coeff"
                    else:
                        text_item.text = f"{influencer.equation_type.name}, right, coeff"
                    self.summary_text.text_items.append(text_item)
            # add medians score bullet
            if movement_scores.medians_score_side == 1:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during left foot steps"
                self.summary_text.text_items.append(text_item)
            elif movement_scores.medians_score_side == 2:
                text_item = DataCardSummaryTextItem()
                text_item.text = "you had greater range of motion during right foot steps"
                self.summary_text.text_items.append(text_item)
            # add fatigue bullet
            if len(movement_scores.asymmetry_fatigue_score_influencers) > 0:
                influencer = movement_scores.asymmetry_fatigue_score_influencers[0]
                text_item = DataCardSummaryTextItem()
                if influencer.side == 1:
                    text_item.text = f"{influencer.equation_type.name}, left, fatigue"
                else:
                    text_item.text = f"{influencer.equation_type.name}, right, fatigue"
                self.summary_text.text_items.append(text_item)

    def get_apt_dysfunction_text(self, movement_scores):
        if self.category == 3:  # APT dysfunction lowest
            self.summary_text.text = "Your biomechanics are apropriately aligned to receive and distribute load most efficiently throughout your body."
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "Your biomechanics show slight signs of potential strength and length imbalances which places excessive strain on your lower back and hamstrings."
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "Your biomechanics show moderate signs of potential strength and length imbalances which places excessive strain on your lower back and hamstrings."
            self.summary_text.active = True
        elif self.category == 0:  # APT dysfunction highest
            self.summary_text.text = "Your biomechanics show excessive signs of potential strength and length imbalances which places excessive strain on your lower back and hamstrings."
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 3:
            text_item1 = DataCardSummaryTextItem()
            text_item1.text = "You arch your lower back, changing the position of your pelvis, in order to achieve greater leg extension."
            text_item2 = DataCardSummaryTextItem()
            text_item2.text = "This is correlated with tight xyz and weak or inhibited mno"
            self.summary_text.text_items = [text_item1, text_item2]

    def get_ankle_pitch_dysfunction_text(self, movement_scores):
        if self.category == 3:  # ankle_pitch dysfunction lowest
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 0:  # ankle_pitch dysfunction highest
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 3:
            for influencer in movement_scores.movement_dysfunction_influencers:
                if influencer.equation_type == EquationType.apt_ankle_pitch:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "apt_ankle_pitch 1"
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "apt_ankle_pitch 2"
                    self.summary_text.text_items.extend([text_item1, text_item2])
                elif influencer.equation_type == EquationType.hip_rotation_ankle_pitch:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "hip_rotation_ankle_pitch 1"
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "hip_rotation_ankle_pitch 2"
                    self.summary_text.text_items.extend([text_item1, text_item2])

    def get_hip_drop_dysfunction_text(self, movement_scores):
        if self.category == 3:  # hip_drop dysfunction lowest
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 0:  # hip_drop dysfunction highest
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 3:
            for influencer in movement_scores.movement_dysfunction_influencers:
                if influencer.equation_type == EquationType.hip_drop_apt:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "You drop your opposite side hip"
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "This is correlated with tight xyz and weak or inhibited mno"
                    self.summary_text.text_items.extend([text_item1, text_item2])
                elif influencer.equation_type == EquationType.hip_drop_pva:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "You do not have adequate core stability to maintain your posture while loading your body."
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "This is correlated with tight xyz and weak or inhibited mno"
                    self.summary_text.text_items.extend([text_item1, text_item2])

    def get_knee_valgus_dysfunction_text(self, movement_scores):
        if self.category == 3:  # knee_valgus dysfunction lowest
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 0:  # knee_valgus dysfunction highest
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 3:
            for influencer in movement_scores.movement_dysfunction_influencers:
                if influencer.equation_type == EquationType.knee_valgus_hip_drop:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "knee_valgus_hip_drop 1"
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "knee_valgus_hip_drop 2"
                    self.summary_text.text_items.extend([text_item1, text_item2])
                elif influencer.equation_type == EquationType.knee_valgus_pva:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "knee_valgus_pva 1"
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "knee_valgus_pva 2"
                    self.summary_text.text_items.extend([text_item1, text_item2])
                elif influencer.equation_type == EquationType.knee_valgus_apt:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "knee_valgus_apt 1"
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "knee_valgus_apt 2"
                    self.summary_text.text_items.extend([text_item1, text_item2])

    def get_hip_rotation_dysfunction_text(self, movement_scores):
        if self.category == 3:  # hip_rotation dysfunction lowest
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 2:
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 1:
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True
        elif self.category == 0:  # hip_rotation dysfunction highest
            self.summary_text.text = "Lorem ipsum dolor sit amet, consetetur sadipscing elitr, sed dia elitr, sed dia"
            self.summary_text.active = True

        # add bulleted text if needed
        if self.category != 3:
            for influencer in movement_scores.movement_dysfunction_influencers:
                if influencer.equation_type == EquationType.hip_rotation_ankle_pitch:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "hip_rotation_ankle_pitch 1"
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "hip_rotation_ankle_pitch 2"
                    self.summary_text.text_items.extend([text_item1, text_item2])
                elif influencer.equation_type == EquationType.hip_rotation_apt:
                    text_item1 = DataCardSummaryTextItem()
                    text_item1.text = "hip_rotation_apt 1"
                    text_item2 = DataCardSummaryTextItem()
                    text_item2.text = "hip_rotation_apt 2"
                    self.summary_text.text_items.extend([text_item1, text_item2])


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


class ScoreInfluencer(object):
    def __init__(self):
        self.equation_type = 0
        self.side = 0

    def __setattr__(self, name, value):
        if name == 'equation_type' and value is not None and not isinstance(value, EquationType):
            value = EquationType(value)
        super().__setattr__(name, value)


class EquationType(Enum):
    apt_ankle_pitch = 0
    hip_drop_apt = 1
    hip_drop_pva = 2
    knee_valgus_hip_drop = 3
    knee_valgus_pva = 4
    knee_valgus_apt = 5
    hip_rotation_ankle_pitch = 6
    hip_rotation_apt = 7
