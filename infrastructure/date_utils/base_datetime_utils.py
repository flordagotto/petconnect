import datetime
from datetime import timezone as tz
from time import time

from dateutil import parser


# System uses ISO dates and times in UTC internally
default_system_time_zone: tz = tz.utc
date_format = "%Y-%m-%d"
default_user_timezone: str = "UTC"


def date_from_iso8601_string(date_iso8601: str) -> datetime.date:
    return parser.parse(date_iso8601).date()


def datetime_from_iso8601_string(datetime_iso8601: str) -> datetime.datetime:
    return parser.parse(datetime_iso8601)


def datetime_to_iso8601_string(date: datetime.date) -> str:
    return date.isoformat()


def date_to_string(date: datetime.date) -> str:
    return date.strftime(date_format)


def datetime_from_timestamp(ts: float) -> datetime.datetime:
    return datetime.datetime.fromtimestamp(ts).replace(tzinfo=default_system_time_zone)


def datetime_now_tz() -> datetime.datetime:
    return datetime.datetime.now(tz=default_system_time_zone)


def date_now() -> datetime.date:
    return datetime_now_tz().date()


def default_project_timezone() -> tz:
    return default_system_time_zone


def float_timestamp() -> float:
    return time()
