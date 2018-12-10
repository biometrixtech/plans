import boto3
import datetime
import json
import os
import uuid
from flask import request
from fathomapi.utils.exceptions import InvalidSchemaException


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
        if date_input.hour < 3:
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


def format_datetime(date_input):
    """
    Formats a date in ISO8601 short format.
    Handles the case where the input is None
    :param date_input:
    :return:
    """
    if date_input is None:
        return None
    if not isinstance(date_input, datetime.datetime):
        date_input = datetime.datetime.strptime(date_input, "%Y-%m-%dT%H:%M:%SZ")
    return date_input.strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_datetime(date_input):
    try:
        return datetime.datetime.strptime(date_input, "%Y-%m-%dT%H:%M:%SZ")
    except ValueError:
        raise InvalidSchemaException('date_time must be in ISO8601 format')


def parse_date(date_input):
    for format_string in ('%Y-%m-%d', '%m/%d/%y'):
        try:
            return datetime.datetime.strptime(date_input, format_string)
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
        return datetime.datetime(
                            year=event_date.year, 
                            month=event_date.month,
                            day=event_date.day - 1,
                            hour=23,
                            minute=59,
                            second=59
                            )
    else:
        return event_date
