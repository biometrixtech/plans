import datetime
import pytz
import math
import uuid
from fathomapi.utils.exceptions import InvalidSchemaException
from config import get_mongo_collection


def format_date(date_input):
    """
    Formats a date in ISO8601 short format.
    Handles the case where the input is None
    :param date_input:
    :return:
    """
    if date_input is None:
        return None
    if isinstance(date_input, datetime.datetime):
        if date_input.hour < 3 and not (date_input.hour == 0 and date_input.minute == 0 and date_input.second == 0):
            date_input = date_input - datetime.timedelta(days=1)
        return date_input.strftime("%Y-%m-%d")
    elif isinstance(date_input, datetime.date):
        return date_input.strftime("%Y-%m-%d")
    else:
        for format_string in ('%Y-%m-%d', '%m/%d/%y', '%Y-%m'):
            try:
                date_input = datetime.datetime.strptime(date_input, format_string)
                return date_input.strftime("%Y-%m-%d")
            except ValueError:
                pass
        return None
        # raise ValueError('no valid date format found')


def format_datetime(datetime_input):
    """
    Formats a date in ISO8601 short format.
    Handles the case where the input is None
    :param datetime_input:
    :return:
    """
    if datetime_input is None:
        return None
    if not isinstance(datetime_input, datetime.datetime):
        datetime_input = parse_datetime(datetime_input)  # datetime.datetime.strptime(datetime_input, "%Y-%m-%dT%H:%M:%SZ")
    if datetime_input.microsecond != 0:
        format_string = "%Y-%m-%dT%H:%M:%S.%f%z"
    else:
        format_string = "%Y-%m-%dT%H:%M:%S%z"
    if datetime_input.tzinfo == pytz.utc:
        format_string = format_string.replace("%z", "Z")
    return datetime_input.strftime(format_string)


def parse_datetime(datetime_string):
    format_strings = [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
        "%Y-%m-%dT%H:%M:%S.%f%z",
        "%Y-%m-%dT%H:%M:%S%z",

    ]
    for format_string in format_strings:
        try:
            date_time = datetime.datetime.strptime(datetime_string, format_string)
            if date_time.tzinfo is None:
                date_time = date_time.replace(tzinfo=pytz.UTC)
            return date_time
            # return datetime.datetime.strptime(datetime_string, format_string)
        except ValueError:
            continue
    raise InvalidSchemaException('date_time must be in ISO8601 format')


def parse_date(date_string):
    for format_string in ('%Y-%m-%d', '%m/%d/%y'):
        try:
            date_time = datetime.datetime.strptime(date_string, format_string)
            if date_time.tzinfo is None:
                date_time = date_time.replace(tzinfo=pytz.UTC)
            return date_time
        except ValueError:
            pass
    raise InvalidSchemaException('date_time must be in ISO8601 format')


def validate_uuid4(uuid_string):
    try:
        val = uuid.UUID(uuid_string, version=4)
        # If the uuid_string is a valid hex code, but an invalid uuid4, the UUID.__init__
        # will convert it to a valid uuid4. This is bad for validation purposes.
        return val.hex == uuid_string.replace('-', '')
    except ValueError:
        # If it's a value error, then the string is not a valid hex code for a UUID.
        return False


def fix_early_survey_event_date(event_date):
    if event_date.hour < 3:
        event_date = event_date - datetime.timedelta(days=1)
        return datetime.datetime(
                            year=event_date.year, 
                            month=event_date.month,
                            day=event_date.day,
                            hour=23,
                            minute=59,
                            second=59
                            )
    else:
        return event_date


def get_timezone(local_time):
    if local_time.tzinfo is not None and local_time.tzinfo != pytz.utc:
        tz_name = local_time.strftime('%z')
        return f"{tz_name[:3]}:{tz_name[3:]}"
    try:
        utc_time = datetime.datetime.utcnow().replace(tzinfo=pytz.utc)
        diff = (local_time - utc_time).total_seconds()
        thirty_mins = round(diff / (30 * 60), 0)
        hour_diff = int(abs(thirty_mins) // 2)
        min_diff = int(math.ceil(thirty_mins % 2) * 30)
        if min_diff == 0:
            min_diff = f"0{min_diff}"
        else:
            min_diff = f"{min_diff}"
        sign = "-" if diff < 0 else "+"
        if hour_diff >= 10:
            tz = f"{sign}{hour_diff}:{min_diff}"
        else:
            tz = f"{sign}0{hour_diff}:{min_diff}"
        return tz
    except Exception as e:
        print(e)
        return '-04:00'


def get_local_time(utc_time, timezone):
    offset = _get_time_offset(timezone)
    return utc_time + datetime.timedelta(minutes=offset)


def _get_time_offset(timezone):
    offset = timezone.split(":")
    hour_offset = int(offset[0])
    minute_offset = int(offset[1])
    if hour_offset < 0:
        minute_offset = hour_offset * 60 - minute_offset
    else:
        minute_offset += hour_offset * 60
    return minute_offset


def none_max(value_array):
    filtered = [v for v in value_array if v is not None]
    if len(filtered) > 0:
        return max(filtered)
    else:
        return None


def _check_plan_exists(user_id, event_date):
    mongo_collection = get_mongo_collection('dailyplan')
    return mongo_collection.count({"user_id": user_id, "date": event_date}) == 1
