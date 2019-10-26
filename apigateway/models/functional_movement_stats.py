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