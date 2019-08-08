from models.soreness_base import BodyPartLocationText


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

        text = text.format(bodypart=body_part_text, sport=sport_text, goal=goal_text, severity=severity).strip()
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
