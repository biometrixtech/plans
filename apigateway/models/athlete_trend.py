from models.soreness import Alert
from models.insights import InsightType
from models.chart_data import TrainingVolumeChartData


class Trend(object):
    def __init__(self, insight_type):
        self.insight_type = insight_type
        self.goals = []
        self.cta = []
        self.alerts = []

    def json_serialise(self):
        ret = {
            'insight_type': self.insight_type.value,
            'goals': self.goals,
            'cta': self.cta,
            'alerts': [alert.json_serialise() for alert in self.alerts]
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        trend = cls(input_dict['insight_type'])
        trend.goals = input_dict.get('goals', [])
        trend.cta = input_dict.get('cta', [])
        trend.alerts = [Alert.json_deserialise(alert) for alert in input_dict.get('alerts', [])]
        return trend


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
        self.stress = Trend(InsightType.stress)
        self.response = Trend(InsightType.response)
        self.biomechanics = Trend(InsightType.biomechanics)
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
        trends.stress = Trend.json_deserialise(input_dict['stress']) if input_dict.get('stress', None) is not None else None
        trends.response = Trend.json_deserialise(input_dict['response']) if input_dict.get('response', None) is not None else None
        trends.biomechanics = Trend.json_deserialise(input_dict['biomechanics']) if input_dict.get('biomechanics', None) is not None else None

        return trends


# class TextGenerator(object):
#
#     def get_cleaned_text(self, text, goals, body_parts, sports, severity):
#         body_parts = body_parts
#         body_part_list = []
#         if len(goals) == 0:
#             goal_text = ""
#         elif len(goals) == 1:
#             goal_text = goals[0]
#         elif len(goals) == 2:
#             goal_text = " and ".join(goals)
#         else:
#             joined_text = ", ".join(goals)
#             pos = joined_text.rfind(",")
#             goal_text = joined_text[:pos] + " and" + joined_text[pos+1:]
#
#         sport_names = [sport_name.get_display_name() for sport_name in sports]
#         if len(sport_names) == 0:
#             sport_text = ""
#         elif len(sports) == 1:
#             sport_text = sport_names[0]
#         elif len(sports) == 2:
#             sport_text = " and ".join(sport_names)
#         else:
#             joined_text = ", ".join(sport_names)
#             pos = joined_text.rfind(",")
#             sport_text = joined_text[:pos] + " and" + joined_text[pos+1:]
#
#         body_parts.sort(key=lambda x: x.body_part_location.value, reverse=False)
#         for body_part in body_parts:
#             part = BodyPartLocationText(body_part.body_part_location).value()
#             side = body_part.side
#             if side == 1:
#                 body_text = " ".join(["left", part])
#             elif side == 2:
#                 body_text = " ".join(["right", part])
#             else:  # side == 0:
#                 body_text = part
#             body_part_list.append(body_text)
#
#         body_part_list = self.merge_bilaterals(body_part_list)
#         body_part_text = ""
#         if len(body_part_list) > 2:
#             joined_text = ", ".join(body_part_list)
#             pos = joined_text.rfind(",")
#             body_part_text = joined_text[:pos] + " and" + joined_text[pos+1:]
#         elif len(body_part_list) == 2:
#             if "left and right" not in body_part_list[0] and "left and right" not in body_part_list[1]:
#                 joined_text = ", ".join(body_part_list)
#                 pos = joined_text.rfind(",")
#                 body_part_text = joined_text[:pos] + " and" + joined_text[pos + 1:]
#             else:
#                 body_part_text = ", ".join(body_part_list)
#         elif len(body_part_list) == 1:
#             body_part_text = body_part_list[0]
#         text = text.format(bodypart=body_part_text, sport_name=sport_text, goal=goal_text, severity="moderate")
#         if len(text) > 1:
#             return text[0].upper() + text[1:]
#         else:
#             return text
#
#     @staticmethod
#     def merge_bilaterals(body_part_list):
#
#         last_part = ""
#
#         for b in range(0, len(body_part_list)):
#
#             cleaned_part = body_part_list[b].replace("left ", "").replace("right ", "")
#             if cleaned_part == last_part:
#                 body_part_list[b] = "left and right " + cleaned_part
#                 body_part_list[b - 1] = ""
#             last_part = cleaned_part
#
#         new_body_part_list = [x for x in body_part_list if x != ""]
#
#         return new_body_part_list
