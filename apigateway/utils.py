import boto3
import datetime
import json
import os
import uuid
from flask import request
from exceptions import InvalidSchemaException


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


def run_async(method, endpoint, body=None):
    endpoint = endpoint.strip('/')
    payload = {
        "path": f"/plans/{os.environ['API_VERSION']}/endpoint",
        "httpMethod": method,
        "headers": {
            "Accept": "*/*",
            "Authorization": request.headers.get('Authorization', None),
            "Content-Type": "application/json",
            "Host": "apis.{}.fathomai.com".format(os.environ['ENVIRONMENT']),
            "User-Agent": "Biometrix/Plans API",
            "X-Forwarded-Port": "443",
            "X-Forwarded-Proto": "https"
        },
        "queryStringParameters": None,
        "pathParameters": {"endpoint": endpoint},
        "stageVariables": None,
        "requestContext": {"identity": {"sourceIp": "0.0.0.0"}},
        "body": json.dumps(body) if body is not None else None,
        "isBase64Encoded": False
    }

    boto3.client('sqs').send_message(
        QueueUrl=os.environ['ASYNC_QUEUE_URL'],
        MessageBody=json.dumps(payload)
    )
