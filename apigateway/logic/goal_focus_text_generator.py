from models.exercise import Phase
from models.soreness import SorenessType
from models.soreness_base import BodyPartLocation
from logic.soreness_processing import BodyPartMapping


class RecoveryTextGenerator(object):

    def get_why_text(self, rpe_impact_score, soreness_impact_score):

        message_1 = ""
        message_2 = ""

        if 0.5 <= rpe_impact_score <= .99:
            message_1 += "light effort"
        elif 1 <= rpe_impact_score <= 1.99:
            message_1 += "moderate effort"
        elif 2 <= rpe_impact_score <= 2.99:
            message_1 += "hard effort"
        elif 3 <= rpe_impact_score <= 3.99:
            message_1 += "very hard effort"
        elif 4 <= rpe_impact_score:
            message_1 += "max effort"

        if soreness_impact_score == 0:
            message_2 += "no soreness and discomfort"
        elif soreness_impact_score == 1:
            message_2 += "minimal soreness and discomfort"
        elif soreness_impact_score == 2:
            message_2 += "mild soreness and discomfort"
        elif soreness_impact_score == 3:
            message_2 += "moderate soreness and discomfort"
        elif soreness_impact_score == 4:
            message_2 += "severe soreness and discomfort"
        elif soreness_impact_score == 5:
            message_2 += "max soreness and discomfort"

        if rpe_impact_score <= soreness_impact_score:
            if len(message_1) > 0:
                message = message_2 + " and " + message_1
            else:
                message = message_2
        else:
            if len(message_1) > 0:
                message = message_1 + " and " + message_2
            else:
                message = message_2

        return message

    def get_text_from_body_part_list(self, soreness_list):

        text = ""

        for b in range(0, len(soreness_list)):
            text += self.get_body_part_text(soreness_list[b].body_part.location, soreness_list[b].side)

            if len(soreness_list) - b > 2:
                text += ", "
            if len(soreness_list) - b == 2:
                text += " and "

        return text


    def get_body_part_text(self, body_part_location, side=None):

        side_text = ""

        if side == 1:
            side_text = "left "
        elif side == 2:
            side_text = "right "
        elif side is None or side == 0:
            side_text = ""

        if body_part_location == BodyPartLocation.achilles:
            return side_text + "achilles"
        elif body_part_location == BodyPartLocation.lower_back:
            return side_text + "lower back"
        elif body_part_location == BodyPartLocation.glutes:
            return "glute"
        elif body_part_location == BodyPartLocation.foot:
            return side_text + "foot"
        elif body_part_location == BodyPartLocation.ankle:
            return side_text + "ankle"
        elif body_part_location == BodyPartLocation.shin:
            return side_text + "shin"
        elif body_part_location == BodyPartLocation.calves:
            return side_text + "calf"
        elif body_part_location == BodyPartLocation.knee:
            return side_text + "knee"
        elif body_part_location == BodyPartLocation.quads:
            return side_text + "quad"
        elif body_part_location == BodyPartLocation.groin:
            return side_text + "groin"
        elif body_part_location == BodyPartLocation.outer_thigh:
            return side_text + "outer thigh"
        elif body_part_location == BodyPartLocation.hamstrings:
            return side_text + "hamstring"
        elif body_part_location == BodyPartLocation.abdominals:
            return side_text + "abdominals"
        elif body_part_location == BodyPartLocation.hip_flexor:
            return side_text + "hip"
        elif body_part_location == BodyPartLocation.chest:
            return side_text + "pec"
        elif body_part_location == BodyPartLocation.head:
            return "head"
        elif body_part_location == BodyPartLocation.shoulder:
            return side_text + "shoulder"
        elif body_part_location == BodyPartLocation.upper_back_neck:
            return "upper back/neck"
        elif body_part_location == BodyPartLocation.lats:
            return side_text + "lat"
        elif body_part_location == BodyPartLocation.wrist:
            return side_text + "wrist"
        elif body_part_location == BodyPartLocation.elbow:
            return side_text + "elbow"
        elif body_part_location == BodyPartLocation.triceps:
            return side_text + "tricep"
        elif body_part_location == BodyPartLocation.biceps:
            return side_text + "bicep"
        else:
            return ""

    def get_body_part_text_plural(self, body_part_location, side=None):

        side_text = ""

        if side == 1:
            side_text = "left "
        elif side == 2:
            side_text = "right "
        elif side is None or side == 0:
            side_text = ""

        if body_part_location == BodyPartLocation.achilles:
            return side_text + "achilles"
        elif body_part_location == BodyPartLocation.lower_back:
            return side_text + "lower back"
        elif body_part_location == BodyPartLocation.glutes:
            return "glutes"
        elif body_part_location == BodyPartLocation.foot:
            return side_text + "feet"
        elif body_part_location == BodyPartLocation.ankle:
            return side_text + "ankles"
        elif body_part_location == BodyPartLocation.shin:
            return side_text + "shins"
        elif body_part_location == BodyPartLocation.calves:
            return side_text + "calves"
        elif body_part_location == BodyPartLocation.knee:
            return side_text + "knees"
        elif body_part_location == BodyPartLocation.quads:
            return side_text + "quads"
        elif body_part_location == BodyPartLocation.groin:
            return side_text + "groin"
        elif body_part_location == BodyPartLocation.outer_thigh:
            return side_text + "outer thighs"
        elif body_part_location == BodyPartLocation.hamstrings:
            return side_text + "hamstrings"
        elif body_part_location == BodyPartLocation.abdominals:
            return side_text + "abdominals"
        elif body_part_location == BodyPartLocation.hip_flexor:
            return side_text + "hips"
        elif body_part_location == BodyPartLocation.chest:
            return side_text + "pecs"
        elif body_part_location == BodyPartLocation.head:
            return "head"
        elif body_part_location == BodyPartLocation.shoulder:
            return side_text + "shoulders"
        elif body_part_location == BodyPartLocation.upper_back_neck:
            return "upper back/neck"
        elif body_part_location == BodyPartLocation.lats:
            return side_text + "lats"
        elif body_part_location == BodyPartLocation.wrist:
            return side_text + "wrists"
        elif body_part_location == BodyPartLocation.elbow:
            return side_text + "elbows"
        elif body_part_location == BodyPartLocation.triceps:
            return side_text + "triceps"
        elif body_part_location == BodyPartLocation.biceps:
            return side_text + "biceps"

    def get_soreness_4_text(self, body_part_text):
        return "Based on the discomfort reporting at your " + body_part_text + " we recommend you rest and " \
               "utilize available self-care techniques to help reduce swelling, ease pain, and speed up healing. " \
               "If you have pain or swelling that gets worse or doesn’t go away, please seek appropriate medical " \

    def get_soreness_5_text(self, body_part_text):
        return "Based on the discomfort reporting at your " + body_part_text + " we recommend you rest and " \
               "utilize available self-care techniques to help reduce swelling, ease pain, and speed up healing. " \
               "If you have pain or swelling that gets worse or doesn’t go away, please seek appropriate medical " \
               "attention."

    def get_goal_text(self, rpe_impact_score, soreness_impact_score, body_part_text):

        message = ""

        if 0 <= rpe_impact_score <= 1.49:
            if soreness_impact_score == 0:
                message += "Build strength and keep moving efficiently in training"
            elif soreness_impact_score == 1:
                message += "Build strength and keep your " + body_part_text + " moving efficiently in training"
            elif soreness_impact_score == 2:
                message += "Stay loose! Focus on increasing flexibility and building stamina!"
            elif soreness_impact_score == 3:
                message += "Increase the blood flow to decrease soreness and let your " + body_part_text + " recover"
            elif soreness_impact_score == 4:
                message = self.get_soreness_4_text(body_part_text)
            elif soreness_impact_score == 5:
                message = self.get_soreness_5_text(body_part_text)
        elif 1.5 <= rpe_impact_score <= 2.49:
            if soreness_impact_score == 0:
                message += "Build stamina and efficient movements during training"
            elif soreness_impact_score == 1:
                message += "Build stamina and efficient movements in your " + body_part_text + " during training"
            elif soreness_impact_score == 2:
                message += "Get stronger and move your " + body_part_text + " more efficiently to prevent fatigue"
            elif soreness_impact_score == 3:
                message += "Focus on stretching and increasing blood flow to recover from the inside out"
            elif soreness_impact_score == 4:
                message = self.get_soreness_4_text(body_part_text)
            elif soreness_impact_score == 5:
                message = self.get_soreness_5_text(body_part_text)
        elif 2.5 <= rpe_impact_score <= 3.49:
            if soreness_impact_score == 0:
                message += "Up the blood flow and prevent fatigue during training"
            elif soreness_impact_score == 1:
                message += "Up the blood flow and prevent fatigue in " + body_part_text + ""
            elif soreness_impact_score == 2:
                message += "Recover properly by stretching " + body_part_text + " to increase blood flow and prevent fatigue"
            elif soreness_impact_score == 3:
                message += "Decrease feelings of soreness and prevent fatigue by stretching out your " + body_part_text + \
                           " sufficiently"
            elif soreness_impact_score == 4:
                message = self.get_soreness_4_text(body_part_text)
            elif soreness_impact_score == 5:
                message = self.get_soreness_5_text(body_part_text)
        elif 3.5 <= rpe_impact_score <= 4.49:
            if soreness_impact_score == 0:
                message += "Focus on increasing flexibility to prevent fatigue during training"
            elif soreness_impact_score == 1:
                message += "Take a breather--focus on increasing flexibility and limiting your activity in your " + \
                           body_part_text
            elif soreness_impact_score == 2:
                message += "Recover well by decreasing your activity and get some blood moving to flush out your " + \
                           body_part_text
            elif soreness_impact_score == 3:
                message += "Limit your activity and focus on letting your body recover"
            elif soreness_impact_score == 4:
                message = self.get_soreness_4_text(body_part_text)
            elif soreness_impact_score == 5:
                message = self.get_soreness_5_text(body_part_text)
        elif 4.5 <= rpe_impact_score <= 5:
            if soreness_impact_score == 0:
                message += "Focus on increasing flexibility to prevent fatigue during training"
            elif soreness_impact_score == 1:
                message += "Take a breather--focus on increasing flexibility and limiting your activity in your " + \
                           body_part_text
            elif soreness_impact_score == 2:
                message += "Recover well by decreasing your activity and get some blood moving to flush out your " + \
                           body_part_text
            elif soreness_impact_score == 3:
                message += "Limit your activity and focus on letting your body recover"
            elif soreness_impact_score == 4:
                message = self.get_soreness_4_text(body_part_text)
            elif soreness_impact_score == 5:
                message = self.get_soreness_5_text(body_part_text)

        return message

    def get_recovery_exercise_text(self, soreness_score, exercise_phase, body_part_location):

        message = ""

        mapping = BodyPartMapping()
        soreness_type = mapping.get_soreness_type(body_part_location)

        if exercise_phase == Phase.inhibit:
            if soreness_score == 0:
                message += "Increase flexibility"
            if soreness_score == 1:
                if soreness_type == SorenessType.muscle_related:
                    message += "Increase flexibility"
                else:
                    message += "Increase range of motion"
            elif soreness_score == 2:
                message += "Increase blood flow"
            elif soreness_score == 3:
                message += "Limit overactivity"
        elif exercise_phase == Phase.lengthen:
            if soreness_score <= 1:
                message += "Prepare for movement"
            elif soreness_score == 2 or soreness_score == 3:
                if soreness_type == SorenessType.muscle_related:
                    message += "Increase flexibility"
                else:
                    message += "Increase range of motion"
        elif exercise_phase == Phase.activate:
            if soreness_score <= 1:
                message += "Increase strength"
            elif soreness_score == 2 or soreness_score == 3:
                message += "Focused muscle activation"
        elif exercise_phase == Phase.integrate:
            if soreness_score <= 0:
                message += "Total body activation"
            elif soreness_score == 2:
                message += "Total body activation"
            elif soreness_score == 3:
                message += "Improve movement efficiency"

        return message