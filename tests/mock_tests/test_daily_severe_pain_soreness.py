from datetime import datetime
from models.soreness import BodyPart, BodyPartLocation, Soreness
from models.stats import AthleteStats
from utils import parse_date


def test_persist_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")

    soreness1 = Soreness()
    soreness1.body_part = BodyPart(BodyPartLocation(9), None)
    soreness1.reported_date_time = datetime(2018, 12, 1, 12, 0, 0)

    soreness2 = Soreness()
    soreness2.body_part = BodyPart(BodyPartLocation(9), None)
    soreness2.reported_date_time = datetime(2018, 12, 2, 12, 0, 0)

    soreness3 = Soreness()
    soreness3.body_part = BodyPart(BodyPartLocation(9), None)
    soreness3.reported_date_time = datetime(2018, 12, 3, 12, 0, 0)

    assert athlete_stats.persist_soreness(soreness1) == False
    assert athlete_stats.persist_soreness(soreness2) == True
    assert athlete_stats.persist_soreness(soreness3) == True


def test_readiness_soreness_update_expired_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(9), None)
    soreness.severity = 4
    soreness.reported_date_time = datetime(2018, 12, 1, 12, 0, 0)
    athlete_stats.readiness_soreness = [soreness]
    athlete_stats.readiness_pain = [soreness]

    new_soreness = Soreness()
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.reported_date_time = datetime(2018, 12, 3, 17, 0, 0)
    athlete_stats.update_readiness_soreness([new_soreness])
    athlete_stats.update_readiness_pain([new_soreness])

    assert len(athlete_stats.readiness_soreness) == 1
    assert athlete_stats.readiness_soreness[0]. severity == 2

    assert len(athlete_stats.readiness_pain) == 1
    assert athlete_stats.readiness_pain[0]. severity == 2

def test_readiness_soreness_update_consecutive_days():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(9), None)
    soreness.severity = 4
    soreness.reported_date_time = datetime(2018, 12, 2, 12, 0, 0)
    athlete_stats.readiness_soreness = [soreness]
    athlete_stats.readiness_pain = [soreness]

    new_soreness = Soreness()
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.reported_date_time = datetime(2018, 12, 3, 17, 0, 0)
    athlete_stats.update_readiness_soreness([new_soreness])
    athlete_stats.update_readiness_pain([new_soreness])

    assert len(athlete_stats.readiness_soreness) == 2
    assert len(athlete_stats.readiness_pain) == 2

def test_ps_soreness_update_expired_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(9), None)
    soreness.severity = 4
    soreness.reported_date_time = datetime(2018, 12, 1, 12, 0, 0)
    athlete_stats.post_session_soreness = [soreness]
    athlete_stats.post_session_pain = [soreness]

    new_soreness = Soreness()
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.reported_date_time = datetime(2018, 12, 3, 17, 0, 0)
    athlete_stats.update_post_session_soreness([new_soreness])
    athlete_stats.update_post_session_pain([new_soreness])

    assert len(athlete_stats.post_session_soreness) == 1
    assert athlete_stats.post_session_soreness[0].severity == 2

    assert len(athlete_stats.post_session_pain) == 1
    assert athlete_stats.post_session_pain[0]. severity == 2

def test_ps_soreness_update_consecutive_days():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(9), None)
    soreness.severity = 4
    soreness.reported_date_time = datetime(2018, 12, 2, 12, 0, 0)
    athlete_stats.post_session_soreness = [soreness]
    athlete_stats.post_session_pain = [soreness]

    new_soreness = Soreness()
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.reported_date_time = datetime(2018, 12, 3, 17, 0, 0)
    athlete_stats.update_post_session_soreness([new_soreness])
    athlete_stats.update_post_session_pain([new_soreness])

    assert len(athlete_stats.post_session_soreness) == 2
    assert len(athlete_stats.post_session_pain) == 2


def test_daily_soreness_update_expired_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(9), None)
    soreness.severity = 4
    soreness.reported_date_time = datetime(2018, 12, 1, 12, 0, 0)
    athlete_stats.daily_severe_soreness = [soreness]
    athlete_stats.daily_severe_pain = [soreness]

    new_soreness = Soreness()
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.reported_date_time = datetime(2018, 12, 3, 17, 0, 0)
    athlete_stats.update_readiness_soreness([new_soreness])
    athlete_stats.update_readiness_pain([new_soreness])

    athlete_stats.update_daily_soreness()
    assert len(athlete_stats.daily_severe_soreness) == 1
    assert athlete_stats.daily_severe_soreness[0]. severity == 2
    athlete_stats.update_daily_pain()
    assert len(athlete_stats.daily_severe_pain) == 1
    assert athlete_stats.daily_severe_pain[0]. severity == 2

def test_daily_soreness_update_two_day_consecutive_soreness():
    athlete_stats = AthleteStats("tester")
    athlete_stats.event_date = parse_date("2018-12-03")

    soreness = Soreness()
    soreness.body_part = BodyPart(BodyPartLocation(9), None)
    soreness.severity = 4
    soreness.reported_date_time = datetime(2018, 12, 2, 12, 0, 0)
    athlete_stats.daily_severe_soreness = [soreness]
    athlete_stats.readiness_soreness = [soreness]
    athlete_stats.daily_severe_pain = [soreness]
    athlete_stats.readiness_pain = [soreness]

    new_soreness = Soreness()
    new_soreness.body_part = BodyPart(BodyPartLocation(9), None)
    new_soreness.severity = 2
    new_soreness.reported_date_time = datetime(2018, 12, 3, 17, 0, 0)
    athlete_stats.update_readiness_soreness([new_soreness])
    athlete_stats.update_readiness_pain([new_soreness])

    athlete_stats.update_daily_soreness()
    assert len(athlete_stats.daily_severe_soreness) == 1
    assert athlete_stats.daily_severe_soreness[0]. severity == 4

    athlete_stats.update_daily_pain()
    assert len(athlete_stats.daily_severe_pain) == 1
    assert athlete_stats.daily_severe_pain[0]. severity == 4