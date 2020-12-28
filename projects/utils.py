# -*- coding: utf-8 -*-
"""Utility functions."""
import ast
import re
from itertools import chain


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


def convert_json_values(value):
    """
    Convert boolean and null JSON values to Python format.

    Parameters
    ----------
    value : str

    Returns
    -------
    str or None
    """
    if value == "null":
        value = None
    elif value == "true":
        value = True
    elif value == "false":
        value = False
    else:
        try:
            # try to convert string to correct type
            value = ast.literal_eval(value)
        except Exception:
            pass

    return value
