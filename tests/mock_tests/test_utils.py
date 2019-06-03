import datetime
from utils import format_datetime, format_date, parse_datetime, parse_date, fix_early_survey_event_date


def test_format_date_datetime():
    event_date = datetime.datetime(2018, 11, 30, 12, 30, 30)
    assert format_date(event_date) == '2018-11-30'

def test_format_date_date():
    event_date = datetime.datetime(2018, 11, 30, 12, 30, 30).date()
    assert format_date(event_date) == '2018-11-30'

def test_format_date_before_3_am():
    event_date = datetime.datetime(2018, 11, 30, 1, 30, 30)
    assert format_date(event_date) == '2018-11-29'
    event_date = datetime.datetime(2018, 11, 30, 0, 30, 30)
    assert format_date(event_date) == '2018-11-29'
    event_date = datetime.datetime(2018, 11, 30, 1, 0, 30)
    assert format_date(event_date) == '2018-11-29'
    event_date = datetime.datetime(2018, 11, 30, 1, 30, 0)
    assert format_date(event_date) == '2018-11-29'

def test_format_date_parse_date():
    event_date = parse_date('2018-11-30')
    assert format_date(event_date) == '2018-11-30'
    event_date = datetime.datetime(2018, 11, 30, 0, 0, 0)
    assert format_date(event_date) == '2018-11-30'

def test_format_date_none():
    assert format_date(None) == None

def test_format_datetime():
    event_date = datetime.datetime(2018, 11, 30, 12, 30, 30)
    assert format_datetime(event_date) == '2018-11-30T12:30:30Z'

def test_format_datetime_none():
    assert format_datetime(None) == None

def test_parse_datetime():
    event_date = "2018-11-30T12:30:30Z"
    assert parse_datetime(event_date) == datetime.datetime(2018, 11, 30, 12, 30, 30)

def test_parse_date():
    event_date = "2018-11-30"
    assert parse_date(event_date) == datetime.datetime(2018, 11, 30, 0, 0, 0)

def test_fix_early_survey_event_date_before_3_am():
    event_date = datetime.datetime(2018, 6, 1, 1, 0, 0)
    fixed_date_time = fix_early_survey_event_date(event_date)
    assert fixed_date_time == datetime.datetime(2018, 5, 31, 23, 59, 59)

def test_fix_early_survey_event_date_after_3_am():
    event_date = datetime.datetime(2018, 11, 30, 3, 0, 0)
    assert fix_early_survey_event_date(event_date) == datetime.datetime(2018, 11, 30, 3, 00, 00)
