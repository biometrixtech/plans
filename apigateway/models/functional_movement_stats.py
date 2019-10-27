from models.soreness_base import BodyPartSide, BodyPartLocation

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


class InjuryCycleSummaryProcessor(object):
    def __init__(self, injury_cycle_summary_dict, side):
        self.injury_cycle_summary_dict = injury_cycle_summary_dict
        self.side = side

    def get_body_part_side(self, body_part_info):

        if isinstance(body_part_info, int):
            body_part_side = BodyPartSide(BodyPartLocation(body_part_info), self.side)
        else:
            body_part_side = BodyPartSide(body_part_info, self.side)

        return body_part_side

    def increment_overactive_short(self, body_part_enum):

        body_part_side = self.get_body_part_side(body_part_enum)
        if body_part_side not in self.injury_cycle_summary_dict:
            self.injury_cycle_summary_dict[body_part_side] = InjuryCycleSummary()
        self.injury_cycle_summary_dict[body_part_side].overactive_short_count += 1

    def increment_overactive_short_by_list(self, body_part_enum_list):

        for b in body_part_enum_list:
            self.increment_overactive_short(b)

    def increment_underactive_long(self, body_part_enum):

        body_part_side = self.get_body_part_side(body_part_enum)
        if body_part_side not in self.injury_cycle_summary_dict:
            self.injury_cycle_summary_dict[body_part_side] = InjuryCycleSummary()
        self.injury_cycle_summary_dict[body_part_side].underactive_long_count += 1

    def increment_underactive_long_by_list(self, body_part_enum_list):

        for b in body_part_enum_list:
            self.increment_underactive_long(b)

    def increment_short(self, body_part_enum):

        body_part_side = self.get_body_part_side(body_part_enum)
        if body_part_side not in self.injury_cycle_summary_dict:
            self.injury_cycle_summary_dict[body_part_side] = InjuryCycleSummary()
        self.injury_cycle_summary_dict[body_part_side].overactive_short_count += 1
        self.injury_cycle_summary_dict[body_part_side].underactive_short_count += 1

    def increment_short_by_list(self, body_part_enum_list):

        for b in body_part_enum_list:
            self.increment_short(b)

    def increment_underactive(self, body_part_enum):

        body_part_side = self.get_body_part_side(body_part_enum)
        if body_part_side not in self.injury_cycle_summary_dict:
            self.injury_cycle_summary_dict[body_part_side] = InjuryCycleSummary()
        self.injury_cycle_summary_dict[body_part_side].underactive_long_count += 1
        self.injury_cycle_summary_dict[body_part_side].underactive_short_count += 1

    def increment_underactive_by_list(self, body_part_enum_list):

        for b in body_part_enum_list:
            self.increment_underactive(b)