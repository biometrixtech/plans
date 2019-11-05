from models.soreness_base import BodyPartSide, BodyPartLocation
from models.functional_movement import BodyPartInjuryRisk

class FunctionalMovementSummary(object):
    def __init__(self):
        self.percent_total_volume_compensating = 0
        self.percent_eccentric_volume_compensating = 0
        self.caused_compensation_count = 0


class InjuryCycleSummary(object):
    def __init__(self):
        self.overactive_short_count = 0
        self.overactive_long_count = 0
        self.underactive_short_count = 0
        self.underactive_long_count = 0
        self.weak_count = 0
        self.last_updated_date_time = None

    def get_percentage(self, count_attribute):

        attribute_list = ["overactive_short_count", "overactive_long_count", "underactive_short_count", "underactive_long_count"]

        total_count = 0

        for a in attribute_list:
            total_count += getattr(self, a)

        if total_count == 0:
            return 0.0

        percent = (getattr(self, count_attribute) / total_count) * 100

        return percent

    def is_highest_count(self, count_attribute):

        attribute_list = ["overactive_short_count", "overactive_long_count", "underactive_short_count",
                          "underactive_long_count"]

        new_attribute_list = [a for a in attribute_list if a != count_attribute]

        if getattr(self, count_attribute) == 0:
            return False

        for n in new_attribute_list:
            if getattr(self, count_attribute) < getattr(self, n):
                return False

        return True


class InjuryCycleSummaryProcessor(object):
    def __init__(self, injury_risk_dict, side, event_date_time, current_symptom_body_parts=[], historic_body_parts=[]):
        self.injury_risk_dict = injury_risk_dict
        self.side = side
        self.event_date_time = event_date_time
        self.current_symptom_body_parts = current_symptom_body_parts
        self.historic_body_parts = historic_body_parts

    def get_increment_level(self, target_body_parts):

        matching_parts = [i for i in target_body_parts if i in self.current_symptom_body_parts]

        if len(matching_parts) == 0:
            return 2
        else:
            return 1

    def set_last_updated(self, body_part_enum, last_updated_date_time):

        body_part_side = self.get_body_part_side(body_part_enum)
        if body_part_side not in self.injury_risk_dict:
            self.injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
        self.injury_risk_dict[body_part_side].last_vote_updated_date_time = last_updated_date_time

    def get_body_part_side(self, body_part_info):

        if isinstance(body_part_info, int):
            body_part_side = BodyPartSide(BodyPartLocation(body_part_info), self.side)
        else:
            body_part_side = BodyPartSide(body_part_info, self.side)

        return body_part_side

    def increment_weak(self, body_part_enum, increment_amount=1):

        if body_part_enum not in self.current_symptom_body_parts:
            body_part_side = self.get_body_part_side(body_part_enum)
            if body_part_side not in self.injury_risk_dict:
                self.injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
            self.injury_risk_dict[body_part_side].weak_vote_count += increment_amount
            self.set_last_updated(body_part_enum, self.event_date_time)

    def increment_weak_by_list(self, body_part_enum_list):

        vote_level = self.get_increment_level(body_part_enum_list)

        for b in body_part_enum_list:
            if b in self.historic_body_parts:
                self.increment_weak(b, 3)
            else:
                self.increment_weak(b, vote_level)

    def increment_overactive_short(self, body_part_enum, increment_amount=1):

        if body_part_enum not in self.current_symptom_body_parts:
            body_part_side = self.get_body_part_side(body_part_enum)
            if body_part_side not in self.injury_risk_dict:
                self.injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
            self.injury_risk_dict[body_part_side].overactive_short_vote_count += increment_amount
            self.set_last_updated(body_part_enum, self.event_date_time)

    def increment_overactive_short_by_list(self, body_part_enum_list):

        vote_level = self.get_increment_level(body_part_enum_list)

        for b in body_part_enum_list:
            if b in self.historic_body_parts:
                self.increment_overactive_short(b, 3)
            else:
                self.increment_overactive_short(b, vote_level)

    def increment_underactive_long(self, body_part_enum, increment_amount=1):

        if body_part_enum not in self.current_symptom_body_parts:
            body_part_side = self.get_body_part_side(body_part_enum)
            if body_part_side not in self.injury_risk_dict:
                self.injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
            self.injury_risk_dict[body_part_side].underactive_long_vote_count += increment_amount
            self.set_last_updated(body_part_enum, self.event_date_time)

    def increment_underactive_long_by_list(self, body_part_enum_list):

        vote_level = self.get_increment_level(body_part_enum_list)

        for b in body_part_enum_list:
            if b in self.historic_body_parts:
                self.increment_underactive_long(b, 3)
            else:
                self.increment_underactive_long(b, vote_level)

    def increment_short(self, body_part_enum, increment_amount=1):

        if body_part_enum not in self.current_symptom_body_parts:
            body_part_side = self.get_body_part_side(body_part_enum)
            if body_part_side not in self.injury_risk_dict:
                self.injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
            self.injury_risk_dict[body_part_side].overactive_short_vote_count += increment_amount
            self.injury_risk_dict[body_part_side].underactive_short_vote_count += increment_amount
            self.set_last_updated(body_part_enum, self.event_date_time)

    def increment_short_by_list(self, body_part_enum_list):

        vote_level = self.get_increment_level(body_part_enum_list)

        for b in body_part_enum_list:
            if b in self.historic_body_parts:
                self.increment_short(b, 3)
            else:
                self.increment_short(b, vote_level)

    def increment_underactive(self, body_part_enum, increment_amount=1):

        if body_part_enum not in self.current_symptom_body_parts:
            body_part_side = self.get_body_part_side(body_part_enum)
            if body_part_side not in self.injury_risk_dict:
                self.injury_risk_dict[body_part_side] = BodyPartInjuryRisk()
            self.injury_risk_dict[body_part_side].underactive_long_vote_count += increment_amount
            self.injury_risk_dict[body_part_side].underactive_short_vote_count += increment_amount
            self.set_last_updated(body_part_enum, self.event_date_time)

    def increment_underactive_by_list(self, body_part_enum_list):

        vote_level = self.get_increment_level(body_part_enum_list)

        for b in body_part_enum_list:
            if b in self.historic_body_parts:
                self.increment_underactive(b, 3)
            else:
                self.increment_underactive(b, vote_level)