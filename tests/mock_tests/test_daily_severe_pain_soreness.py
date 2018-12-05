from datetime import datetime
from models.soreness import BodyPart, BodyPartLocation, Soreness
from models.stats import AthleteStats


def test_daily_soreness_update_expired_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = "2018-12-03"

    soreness = Soreness()
    soreness.side = 1
    soreness.body_part = BodyPart(BodyPartLocation(9), None)
    soreness.severity = 4
    soreness.pain = False
    soreness.reported_date_time = datetime(2018, 12, 1, 12, 0, 0)
    athlete_stats.daily_severe_soreness = [soreness]

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.pain = False
    new_soreness.reported_date_time = datetime(2018, 12, 3, 17, 0, 0)
    survey_soreness = [new_soreness]

    athlete_stats.update_daily_soreness(survey_soreness)
    assert len(athlete_stats.daily_severe_soreness) == 1
    assert athlete_stats.daily_severe_soreness[0]. severity == 2

def test_daily_soreness_update_two_day_consecutive_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = "2018-12-03"

    soreness = Soreness()
    soreness.side = 1
    soreness.body_part = BodyPart(BodyPartLocation(9), None)
    soreness.severity = 4
    soreness.pain = False
    soreness.reported_date_time = datetime(2018, 12, 2, 12, 0, 0)
    athlete_stats.daily_severe_soreness = [soreness]

    new_soreness = Soreness()
    new_soreness.side = 1
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.pain = False
    new_soreness.reported_date_time = datetime(2018, 12, 3, 17, 0, 0)
    survey_soreness = [new_soreness]

    athlete_stats.update_daily_soreness(survey_soreness)
    assert len(athlete_stats.daily_severe_soreness) == 1
    assert athlete_stats.daily_severe_soreness[0]. severity == 4