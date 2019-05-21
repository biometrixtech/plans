import datetime
from enum import Enum
from serialisable import Serialisable
from models.soreness import BodyPartLocationText, BodyPartSide
from models.trigger import TriggerType
from models.sport import SportName
from utils import format_datetime, parse_datetime


class AthleteInsight(Serialisable):
    def __init__(self, trigger_type):
        self.trigger_type = trigger_type
        self.goal_targeted = []
        self.start_date_time = None
        self.title = ""
        self.text = ""
        self.parent = False
        self.first = False
        self.body_parts = []
        self.sport_names = []
        self.severity = []
        self.cleared = False
        self.insight_type = InsightType.stress
        self.longitudinal = self.get_insight_duration()
        self.priority = None
        self.styling = self.get_styling()
        self.read = False
        self.parent_group = TriggerType.get_parent_group(self.trigger_type)

    def json_serialise(self):
        ret = {
            'trigger_type': self.trigger_type.value,
            'title': self.title,
            'goal_targeted': self.goal_targeted,
            'start_date_time': format_datetime(self.start_date_time) if self.start_date_time is not None else None,
            'text': self.text,
            'parent': self.parent,
            'first': self.first,
            'body_parts': [body_part.json_serialise() for body_part in self.body_parts],
            'sport_names': [sport_name.value for sport_name in self.sport_names],
            'severity': self.severity,
            'cleared': self.cleared,
            'insight_type': self.insight_type.value,
            'longitudinal': self.longitudinal,
            'priority': self.priority,
            'styling': self.styling,
            'read': self.read
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        insight = cls(TriggerType(input_dict['trigger_type']))
        insight.title = input_dict.get('title', "")
        insight.goal_targeted = input_dict.get('goal_targeted', [])
        insight.start_date_time = input_dict.get('start_date_time', None)
        insight.text = input_dict.get('text', "")
        insight.parent = input_dict.get('parent', False)
        insight.first = input_dict.get('first', False)
        insight.body_parts = [BodyPartSide.json_deserialise(body_part) for body_part in input_dict['body_parts']]
        insight.sport_names = [SportName(sport_name) for sport_name in input_dict['sport_names']]
        insight.severity = input_dict.get('severity', [])
        insight.cleared = input_dict.get('cleared', False)
        insight.priority = input_dict.get('priority', 0)
        insight.styling = input_dict.get('styling', 0)
        insight.read = input_dict.get('read', False)
        insight.insight_type = InsightType(input_dict.get('insight_type', 0))

        return insight

    def add_data(self):
        insight_data = InsightsData(self.trigger_type.value).data()
        if self.parent:
            if self.cleared:
                title = "Symptoms Cleared!"
                text = insight_data['parent']['clear']
            else:
                title = insight_data['parent']['title']
                if self.first:
                    text = insight_data['parent']['first']
                else:
                    text = insight_data['parent']['subsequent']
        else:
            if self.cleared:
                title = "Symptoms Cleared!"
                text = insight_data['child']['clear']
            else:
                title = insight_data['child']['title']
                if self.first:
                    text = insight_data['child']['first']
                else:
                    text = insight_data['child']['subsequent']
        self.text = TextGenerator().get_cleaned_text(text, self.goal_targeted, self.body_parts, self.sport_names, severity=self.severity)
        self.title = TextGenerator().get_cleaned_text(title, self.goal_targeted, self.body_parts, self.sport_names, severity=self.severity)
        if self.parent and self.parent_group == 2:
            self.priority = 1
        else:
            self.priority = insight_data['priority']

        self.insight_type = InsightType(insight_data['insight_type'])

    def get_insight_duration(self):
        if self.trigger_type.value in [6, 7, 8, 12, 16, 17, 18, 19, 20]:
            return True
        else:
            return False

    def get_styling(self):
        if self.trigger_type.value in [15]:
            return 1
        else:
            return 0

    def __setattr__(self, name, value):
        if name in ['start_date_time'] and value is not None and not isinstance(value, datetime.datetime):
            value = parse_datetime(value)
        super().__setattr__(name, value)


class InsightType(Enum):
    daily = 0
    longitudinal = 1


class InsightType(Enum):
    stress = 0
    response = 1
    biomechanics = 2


class TextGenerator(object):

    def get_cleaned_text(self, text, goals, body_parts, sports, severity):
        body_parts = body_parts
        body_part_list = []
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

        sport_names = [sport_name.get_display_name() for sport_name in sports]
        if len(sport_names) == 0:
            sport_text = ""
        elif len(sports) == 1:
            sport_text = sport_names[0]
        elif len(sports) == 2:
            sport_text = " and ".join(sport_names)
        else:
            joined_text = ", ".join(sport_names)
            pos = joined_text.rfind(",")
            sport_text = joined_text[:pos] + " and" + joined_text[pos+1:]

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

        body_part_list = self.merge_bilaterals(body_part_list)
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
        text = text.format(bodypart=body_part_text, sport_name=sport_text, goal=goal_text, severity="moderate")
        if len(text) > 1:
            return text[0].upper() + text[1:]
        else:
            return text

    @staticmethod
    def merge_bilaterals(body_part_list):

        last_part = ""

        for b in range(0, len(body_part_list)):

            cleaned_part = body_part_list[b].replace("left ", "").replace("right ", "")
            if cleaned_part == last_part:
                body_part_list[b] = "left and right " + cleaned_part
                body_part_list[b - 1] = ""
            last_part = cleaned_part

        new_body_part_list = [x for x in body_part_list if x != ""]

        return new_body_part_list


class InsightsData(object):
    def __init__(self, trigger):
        self.trigger = trigger

    def data(self):
        insights = {
            0: {
                "priority": 8,
                "insight_type": 0,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Avoid Soreness Tomorrow",
                    "first": "We added activities to {goal} because this workout is likely to trigger Delayed Onset Muscle Soreness (DOMS) tomorrow.",
                    "subsequent": "We've added activities to {goal} to mitigate the likelihood of Delayed Onset Muscle Soreness (DOMS).",
                    "clear": ""
                },
                "trend": {
                    "new_title": "Get the greatest gains from your training",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "Make more positive- you worked hard, now recover to make the most of your training.",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 2,
                    "visualization_title": "Personal High Loads"
                }
            },
            1: {
                "priority": 8,
                "insight_type": 0,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed in your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some imbalances we've previously noticed.",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            2: {
                "priority": 8,
                "insight_type": 0,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed in your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some imbalances we've previously noticed.",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            3: {
                "priority": 8,
                "insight_type": 0,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed in your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some imbalances we've previously noticed.",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            4: {
                "priority": 8,
                "insight_type": 0,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed in your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some imbalances we've previously noticed.",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            5: {
                "priority": 8,
                "insight_type": 0,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed in your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some imbalances we've previously noticed.",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            6: {
                "priority": 7,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "Signs of Poor Adaptation",
                    "first": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "subsequent": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "clear": "Great work! Your body is showing signs that it's adapting well and no longer overstressing or overreaching in response to training."
                },
                "child": {
                    "title": "Overstressing Your {bodypart}",
                    "first": "We add activities to {goal} because we've noticed a pattern of post-workout soreness which indicates you may be overstressing or underrecovering your {bodypart}. It should resolve with adequate recovery measures so we've updated your plan to help.",
                    "subsequent": "We add activities to {goal} to help address a pattern of soreness which indicates possible {bodypart} overstressing. ",
                    "clear": "Nicely done! Your no longer showing signs of {bodypart} overstressing! Your plan will be updated to reflect it!"
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            7: {
                "priority": 7,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "Signs of Poor Adaptation",
                    "first": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "subsequent": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "clear": "Great work! Your body is showing signs that it's adapting well and no longer overstressing or overreaching in response to training."
                },
                "child": {
                    "title": "Overstressing Your {bodypart}",
                    "first": "We added activities to {goal} because we've noticed you may be trending toward Overreaching. Increasing the comprehensiveness of your prep & recovery practces can expedite tissue healing to sustain your current training cadence so we've updated our recommendations to help.",
                    "subsequent": "We add activities to {goal} because we've noticed a pattern negative response which is trending toward \"Overreaching\".",
                    "clear": "Good work! Your no longer trending toward overreaching! We'll scale your recommnedations to reflect that!"
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            8: {
                "priority": 7,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "Signs of Poor Adaptation",
                    "first": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "subsequent": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "clear": "Great work! Your body is showing signs that it's adapting well and no longer overstressing or overreaching in response to training."
                },
                "child": {
                    "title": "Signs of Overreaching",
                    "first": "We added activities to {goal} because we've noticed signs that your body is now in a cycle of negative adaptation called \"Overreaching\". To help sustain your current training we suggest significantly increasing recovery practices to expodite healing of training-enduced muscle damage.",
                    "subsequent": "We added activities to {goal} because you've shown signs of negative adaptation to training called \"Overreaching\".",
                    "clear": "Kudos! You've broken the cycle of negative adaptation (Overreaching) and are on track for healthy, sustainable training! We'll update your plan accordingly."
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            9: {
                "priority": 9,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Did We Miss a Workout?",
                    "first": "SORENESS, NOT LINKED TO A SESSION \n We've added {goal} to your plan today, but couldn't find a workout associated with your soreness. In the future, help us improve our recovery and response estimates for you by logging your workouts.",
                    "subsequent": "",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            10: {
                "priority": 9,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "Recover Faster from DOMS",
                    "first": "We've added activities to {goal} to your plan to help tackle Delayed Onset Muscle Sorness (DOMS). We're constantly learning what recovery activities are most effective for your body given your sports & training intensities. So to help us, please do your best to log completed workouts, Fathom activities, and follow-on-soreness so we can optimize our calculations to help you recover faster.",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "How Soreness Turns to Strength:",
                    "first": "MILD SORENESS, LINKED TO A SESSION \n When you report soreness, we provide {goal} activities to expedite tissue healing & retain range of motion. Our recommendations become more personalized as we learn your patterns of training, response, & recovery in order to sustainably turn the minor tissue damage responsible for post-workout soreness into strength.",
                    "subsequent": "",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            11: {
                "priority": 9,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "Recover Faster from DOMS",
                    "first": "We've added activities to {goal} to your plan to help tackle Delayed Onset Muscle Sorness (DOMS). We're constantly learning what recovery activities are most effective for your body given your sports & training intensities. So to help us, please do your best to log completed workouts, Fathom activities, and follow-on-soreness so we can optimize our calculations to help you recover faster.",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "",
                    "first": "",
                    "subsequent": "We've added {goal} to help reduce the severity of DOMS and expedite tissue recovery.",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            12: {
                "priority": 99,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            13: {
                "priority": 99,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            14: {
                "priority": 4,
                "insight_type": 1,
                "data_source": "pain",
                "parent": {
                    "title": "Listen to your body",
                    "first": "Your pain could be a sign that something is wrong. Please avoid and modify any movements that cause discomfort or aggravate your pain.",
                    "subsequent": "Your pain could be a sign that something is wrong. Please avoid and modify any movements that cause discomfort or aggravate your pain.",
                    "clear": ""
                },
                "child": {
                    "title": "How We Help Address Pain:",
                    "first": "{bodypart} pain is typically a sign of misalignments or movement impairments elsewhere. When you have pain, we provide activities to {goal} by correcting the most likely source of these misalignments. Please remember to avoid any activity which aggravates your pain.",
                    "subsequent": "We added activities to {goal} that address the most likely source of misalignment. Pease avoid any modify any movements which cause pain.",
                    "clear": ""
                },
                "trend": {
                    "new_title": "How We Help Address Pain:",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "{bodypart} pain is not normal and typically a sign of misalignments or movement impairments elsewhere.",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 3,
                    "visualization_title": "Pain in {bodypart}"
                }
            },
            15: {
                "priority": 1,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "Listen to your body",
                    "first": "Your pain could be a sign that something is wrong. Please avoid and modify any movements that cause discomfort or aggravate your pain.",
                    "subsequent": "Your pain could be a sign that something is wrong. Please avoid and modify any movements that cause discomfort or aggravate your pain.",
                    "clear": ""
                },
                "child": {
                    "title": "Listen to your body",
                    "first": "Your pain could be a sign that something is wrong. Please avoid and modify any movements that cause discomfort or aggravate your pain.",
                    "subsequent": "Your pain could be a sign that something is wrong. Please avoid and modify any movements that cause discomfort or aggravate your pain.",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            21: {
                "priority": 99,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                }
            },
            22: {
                "priority": 99,
                "insight_type": 1,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            16: {
                "priority": 3,
                "insight_type": 2,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Sign of Possible Injury",
                    "first": "Recurring pain is often caused by movement impairments which frequently result in chronic & overuse injury so we'll help you {goal} which are likely to cause {bodypart} pain. Please avoid any activity which aggravate your pain.",
                    "subsequent": "We've added preventitive activities to {goal} commonly attributed to persistant {bodypart} pain.",
                    "clear": "Well Done! We've haven't seen that {bodypart} pain come back so we'll update your plan to reflect your progress!"
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            17: {
                "priority": 2,
                "insight_type": 2,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Sign of Possible Injury",
                    "first": "We've noticed {sport_name} typically causes {bodypart} pain so we've added activities to {goal}. Please avoid any activity that causes pain.",
                    "subsequent": "We've noticed {sport_name} typically causes {bodypart} pain so we've added activities to {goal}. Please avoid any activity that causes pain.",
                    "clear": "Well Done! We've haven't seen that {bodypart} pain come back so we'll update your plan to reflect your progress!"
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            18: {
                "priority": 99,
                "insight_type": 2,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            19: {
                "priority": 6,
                "insight_type": 2,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Possible Strength Imbalance",
                    "first": "We've added activities to {goal}. Given your training patterns & persistant [body parts] soreness, you may have a strength imbalance or movement dysfuntion which elevates your risk of injury. With these ativities we'll try to address the most likely source.",
                    "subsequent": "Your pattern of persistant {bodypart} soreness points to a biomechanical imbalance so we've added activities to help {goal}.",
                    "clear": "Congrats! It looks like you've resolved that persistant {bodypart} soreness (a possible sign of strength or movement imbalance)! We'll update your plan to reflect that, but will still keep an eye on it!"
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
            20: {
                "priority": 5,
                "insight_type": 2,
                "data_source": "",
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Mitigate Overuse Injury",
                    "first": "We added activities to {goal} because we've noticed a pattern of {bodypart} soreness after {sport_name} which may indicate a sport-related strength imbalance or movement dysfuntion that could lead to overuse injury. Given this data, we'll adapt your plan to enhance long term prevention efforts until we see signs that it's been resolved.",
                    "subsequent": "We noticed a {sport_name}-related imbalance which could lead to overuse injury so we've updated your plan to {goal}.",
                    "clear": "Congrats! It looks like you've resolved that persistant post-{sport_name} {bodypart} soreness- a possible sign of strength or movement imbalance! We'll update your plan to reflect that, but will still keep an eye on it!"
                },
                "trend": {
                    "new_title": "",
                    "new_body": "",
                    "ongoing_title": "",
                    "ongoing_body": "",
                    "cleared_title": "",
                    "cleared_body": "",
                    "visualization_type": 1,
                    "visualization_title": ""
                }
            },
               
        }

        return insights[self.trigger]
