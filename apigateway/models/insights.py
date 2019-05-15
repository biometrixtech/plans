from enum import Enum
from serialisable import Serialisable
from models.soreness import BodyPartLocationText, TriggerType, BodyPartSide
from models.sport import SportName


class AthleteInsight(Serialisable):
    def __init__(self, trigger_type):
        self.trigger_type = trigger_type
        self.goal_targeted = []
        self.start_date = None
        self.title = ""
        self.text = ""
        self.parent = False
        self.first = False
        self.body_parts = []
        self.sport_names = []
        self.severity = []
        self.cleared = False
        self.insight_type = InsightType.daily
        self.priority = 0
        self.styling = 0

    def json_serialise(self):
        ret = {
            'trigger_type': self.trigger_type.value,
            'title': self.title,
            'goal_targeted': self.goal_targeted,
            'start_date': self.start_date,
            'text': self.text,
            'parent': self.parent,
            'first': self.first,
            'body_parts': [body_part.json_serialise() for body_part in self.body_parts],
            'sport_names': [sport_name.value for sport_name in self.sport_names],
            'severity': self.severity,
            'cleared': self.cleared,
            'insight_type': self.insight_type.value,
            'priority': self.priority,
            'styling': self.styling
        }
        return ret

    @classmethod
    def json_deserialise(cls, input_dict):
        print(input_dict)
        insight = cls(TriggerType(input_dict['trigger_type']))
        insight.title = input_dict.get('title', "")
        insight.goal_targeted = input_dict.get('goal_targeted', [])
        insight.start_date = input_dict.get('start_date', None)
        insight.text = input_dict.get('text', "")
        insight.parent = input_dict.get('parent', False)
        insight.first = input_dict.get('first', False)
        insight.body_parts = [BodyPartSide.json_deserialise(body_part) for body_part in input_dict['body_parts']]
        insight.sport_names = [SportName(sport_name) for sport_name in input_dict['sport_names']]
        insight.severity = input_dict.get('severity', [])
        insight.cleared = input_dict.get('cleared', False)
        insight.insight_type = InsightType(input_dict.get('insight_type', 0))
        insight.priority = input_dict.get('priority', 0)
        insight.styling = input_dict.get('styling', 0)

        return insight

    def get_title_and_text(self):
        alert_text = InsightsText(self.trigger_type.value).value()
        if self.parent:
            title = alert_text['parent']['title']
            if self.first:
                text = alert_text['parent']['first']
            else:
                text = alert_text['parent']['subsequent']
        else:
            title = alert_text['child']['title']
            if self.first:
                text = alert_text['child']['first']
            else:
                text = alert_text['child']['subsequent']
        self.text = TextGenerator().get_cleaned_text(text, self.goal_targeted, self.body_parts, self.sport_names, severity=self.severity)
        self.title = TextGenerator().get_cleaned_text(title, self.goal_targeted, self.body_parts, self.sport_names, seveiryt=self.severity)


class InsightType(Enum):
    daily = 0
    longitudinal = 1


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
        return text.format(bodypart=body_part_text, sport_name=sport_text, goal=goal_text, severity="moderate")

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


class InsightsText(object):
    def __init__(self, trigger):
        self.trigger = trigger

    def value(self):
        insights = {
            0: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Avoid {severity} Soreness Tomorrow",
                    "first": "We added activities to {goal} because this workout is likely to trigger {severity} Delayed Onset Muscle Soreness (DOMS) tomorrow.",
                    "subsequent": "We've added activities to {goal} to mitigate the likelihood of {severity} Delayed Onset Muscle Soreness (DOMS).",
                    "clear": ""
                }
            },
            1: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed from your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some of the possible strength and movement imbalances we've previously noticed.",
                    "clear": ""
                }
            },
            2: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed from your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some of the possible strength and movement imbalances we've previously noticed.",
                    "clear": ""
                }
            },
            3: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed from your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some of the possible strength and movement imbalances we've previously noticed.",
                    "clear": ""
                }
            },
            4: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed from your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some of the possible strength and movement imbalances we've previously noticed.",
                    "clear": ""
                }
            },
            5: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Recovery Measures Upgraded",
                    "first": "We added activities to {goal} because today's workout is likely to exaserbate & cause symptoms accociated with strength & movement imbalances we've noticed from your prior pain, soreness, & training history. These activities will help mitigate the effects.",
                    "subsequent": "We added activities to {goal} because today's workout is likely to exacerbate some of the possible strength and movement imbalances we've previously noticed.",
                    "clear": ""
                }
            },
            6: {
                "parent": {
                    "title": "Signs of Poor Adaptation",
                    "first": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence. ",
                    "subsequent": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "clear": "Great work! Your body is showing signs that it's adapting well and no longer overstressing or overreaching in response to training."
                },
                "child": {
                    "title": "Overstressing Your {bodypart}",
                    "first": "We add activities to {goal} because we've noticed a pattern of post-workout soreness which indicates you may be overstressing or underrecovering your {bodypart}. It should resolve with adequate recovery measures so we've updated your plan to help.",
                    "subsequent": "We add activities to {goal} to help address a pattern of soreness which indicates possible {bodypart} overstressing.",
                    "clear": "Nicely done! Your no longer showing signs of {bodypart} overstressing! Your plan will be updated to reflect it!"
                }
            },
            7: {
                "parent": {
                    "title": "Signs of Poor Adaptation",
                    "first": "We added {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "subsequent": "We added {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "clear": "Great work! Your body is showing signs that it's adapting well and no longer overstressing or overreaching in response to training."
                },
                "child": {
                    "title": "Overstressing Your {bodypart}",
                    "first": "We added activities to {goal} because we've noticed you may be trending toward Overreaching. Increasing the comprehensiveness of your prep & recovery practces can expedite tissue healing to sustain your current training cadence so we've updated our recommendations to help.",
                    "subsequent": "We add activities to {goal} because we've noticed a pattern negative response which is trending toward non-functional \"Overreaching\".",
                    "clear": "Great work! Your body is showing signs that it's adapting well and no longer overstressing or overreaching in response to training."
                }
            },
            8: {
                "parent": {
                    "title": "Signs of Poor Adaptation",
                    "first": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence. ",
                    "subsequent": "We added activities to {goal} because it seems your body is struggling to adequately adapt to your current training cadence.",
                    "clear": "Great work! Your body is showing signs that it's adapting well and no longer overstressing or overreaching in response to training."
                },
                "child": {
                    "title": "Signs of Overreaching",
                    "first": "We added activities to {goal} because we've noticed signs that your body is now in a cycle of negative adaptation called \"Overreaching\". To help sustain your current training we suggest significantly increasing recovery practices to expodite healing of training-enduced muscle damage.",
                    "subsequent": "We added activities to {goal} because we've noticed signs that your body is now in a cycle of negative adaptation to training called \"Overreaching\".",
                    "clear": "Kudos! You've broken the cycle of negative adaptation (Overreaching) and are on track for healthy, sustainable training! We'll update your plan accordingly."
                }
            },
            9: {
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
                }
            },
            10: {
                "parent": {
                    "title": "Recover Faster from DOMS",
                    "first": "We've added activities to {goal} to your plan to help tackle Delayed Onset Muscle Sorness (DOMS). We're constantly learning what recovery activities are most effective for your body given your sports & training intensities. So to help us, please do your best to log completed workouts, Fathom activities, and follow-on-soreness so we can optimize our calculations to help you recover faster.",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "How Soreness Turns to Strength:",
                    "first": "When you report soreness, we provide {goal} activities to expedite tissue healing & retain range of motion. Our recommendations become more personalized as we learn your patterns of training, response, & recovery in order to sustainably turn the minor tissue damage responsible for post-workout soreness into strength.",
                    "subsequent": "",
                    "clear": ""
                }
            },
            11: {
                "parent": {
                    "title": "Recover Faster from DOMS",
                    "first": "We've added activities to {goal} to your plan to help tackle Delayed Onset Muscle Sorness (DOMS). We're constantly learning what recovery activities are most effective for your body given your sports & training intensities. So to help us, please do your best to log completed workouts, Fathom activities, and follow-on-soreness so we can optimize our calculations to help you recover faster.",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "",
                    "first": "",
                    "subsequent": "We've added {goal} because we've noticed DOMS has set in. These activities should help reduce the severity of DOMS and expedite tissue recovery.",
                    "clear": ""
                }
            },
            12: {
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
            13: {
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
            14: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "How We Help Address Pain:",
                    "first": "When you report pain we try to provide you with activities to {goal} by balancing mucle tension and encouraging proper biomechanical alignment, but please remember to avoid any activities which trigger pain.",
                    "subsequent": "We added activities to {goal} to help mitigate your {bodypart} pain, but please remember to avoid any activities which trigger pain.",
                    "clear": ""
                }
            },
            15: {
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
            21: {
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
            16: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Sign of Possible Injury",
                    "first": "We added activities to {goal} because recurring {bodypart} pain could be a sign of injury. We've made some changes to avoid aggrevating the issue and encourage you to see a doctor if the pain worsens.",
                    "subsequent": "We added activities to {goal} to try to help your {bodypart} pain, but it could be sign of injury. Please see a doctor if it persists or worsens.",
                    "clear": ""
                }
            },
            17: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Sign of Possible Injury",
                    "first": "We added activities to {goal} because we've noticed that {sport_name} tends to trigger pain in your {bodypart}. This may be a sign of injury caused by a sport-related dysfunction which could lead to future compensations, pain, and injury if not addressed. We'll try to adapt your activities to help with long term prevention, but please try to avoid any acitvities that cause pain & see a doctor if it worsens.",
                    "subsequent": "We added activities to {goal} because we've noticed that {sport_name} tends to trigger pain in your {bodypart} which may be a sign of injury caused by a sport-related dysfuntion. Please remember to avoid acitvities that cause pain & see a doctor if it worsens.",
                    "clear": ""
                }
            },
            18: {
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
            19: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Possible Strength Imbalance",
                    "first": "We've added activities to {goal} to your plan. Given your training patterns and persistant {bodypart} soreness response, you may have a strength imbalance or movement dysfuntion which elevates your risk of injury. With these ativities we'll try to address the most likely source given what we've observed.",
                    "subsequent": "We added activities to {goal} to your plan wecause we've noticed a new strength or movement imbalance given your pattern of persistant {bodypart} soreness.",
                    "clear": "Congrats! It looks like you've resolved that persistant {bodypart} soreness (a possible sign of strength or movement imbalance)! We'll update your plan to reflect that, but will still keep an eye on it!"
                }
            },
            20: {
                "parent": {
                    "title": "",
                    "first": "",
                    "subsequent": "",
                    "clear": ""
                },
                "child": {
                    "title": "Mitigate Overuse Injury",
                    "first": "We added activities to {goal} because we've noticed a pattern of {bodypart} soreness after {sport_name} which may indicate a sport-related strength imbalance or movement dysfuntion that could lead to overuse injury. Given this data, we'll adapt your plan to enhance long term prevention efforts until we see signs that it's been resolved.",
                    "subsequent": "We added activities to {goal} because we've noticed a pattern of {bodypart} soreness after {sport_name} which may indicate a sport-related strength imbalance or movement dysfuntion which could lead to overuse injury.",
                    "clear": "Congrats! It looks like you've resolved that persistent post-{sport_name} {bodypart} soreness- a possible sign of strength or movement imbalance! We'll update your plan to reflect that, but will still keep an eye on it!"
                }
            },
               
        }

        return insights[self.trigger]
