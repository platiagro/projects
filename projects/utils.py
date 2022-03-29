# -*- coding: utf-8 -*-
"""Utility functions."""
import re
from itertools import chain
from urllib.parse import parse_qsl
from datetime import datetime, timezone
import sqlalchemy as sa

FORBIDDEN_CHARACTERS_REGEX = "[!*'():;@&=+$,\/?%#\[\]]"
MAX_CHARS_ALLOWED = 50
MAX_CHARS_ALLOWED_DESCRIPTION = 300


def to_camel_case(snake_str):
    """
    Transforms a snake_case string into camelCase.

    Parameters
    ----------
    snake_str : str

    Returns
    -------
    str
    """
    parts = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return parts[0] + "".join(x.title() for x in parts[1:])


def to_snake_case(camel_str):
    """
    Transforms a camelCase string into snake_case.

    Parameters
    ----------
    camel_case_str : str

    Returns
    -------
    str
    """
    parts = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", parts).lower()


def remove_ansi_escapes(traceback):
    """
    Remove ansi escapes from jupyter logs

    Parameters
    ----------
    traceback : str
        Jupyter traceback logs section

    Returns
    -------
    list
    """
    compiler = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    readable_text = [compiler.sub("", line).split("\n") for line in traceback]

    return list(chain.from_iterable(readable_text))


def format_query_params(query_params):
    """
    Format query params to dict.

    Parameters
    ----------
    query_params : str

    Returns
    -------
    dict
    """
    return dict(parse_qsl(query_params))


class TimeStamp(sa.types.TypeDecorator):
    impl = sa.types.DateTime

    def process_bind_param(self, value: datetime, dialect):
        if value.tzinfo is None:
            value = value.astimezone(timezone.utc)

        return value.astimezone(timezone.utc)

    def process_result_value(self, value, dialect):
        if value.tzinfo is None:
            return value.replace(tzinfo=timezone.utc)

        return value.astimezone(timezone.utc)


def now():
    return datetime.utcnow().replace(tzinfo=timezone.utc)
