# -*- coding: utf-8 -*-
"""Utility functions."""

import re
from itertools import chain


def to_camel_case(snake_str):
    """
    Transforms a snake_case string into camelCase.

    Parameters
    ----------
    snake_str :str

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
    camel_case_str :str

    Returns
    -------
    str
    """
    parts = re.sub("(.)([A-Z][a-z]+)", r"\1_\2", camel_str)
    return re.sub("([a-z0-9])([A-Z])", r"\1_\2", parts).lower()


def remove_ansi_escapes(traceback):
    compiler = re.compile(r"(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]")
    readable_text = [compiler.sub("", line).split("\n") for line in traceback]

    return list(chain.from_iterable(readable_text))


def search_for_pod_name(details, operator_id):
    """
    Get operator pod name.

    Parameters
    ----------
    details : dict
        Workflow manifest from pipeline runtime.
    operator_id : str

    Returns
    -------
    dict
    """
    try:
        if "nodes" in details["status"]:
            for node in [*details["status"]["nodes"].values()]:
                if node["displayName"] == operator_id:
                    return {
                        "name": node["id"],
                        "status": node["phase"],
                        "message": node["message"],
                    }
    except KeyError:
        pass
