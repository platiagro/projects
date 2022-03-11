# -*- coding: utf-8 -*-
"""Shared functions."""
import base64
import csv
import random
import re
import uuid

import filetype
import pandas

ESCAPE_STRING = "\\"
ALLOWED_SPECIAL_CHARACTERS_LIST = ["-", "_", " "]
ALLOWED_SPECIAL_CHARACTERS_REGEX = "[-_\s]"
ESCAPE_MAP = {"-": "\-", "_": "\_", " ": " "}
MAX_CHARS_ALLOWED = 50


def uuid_alpha():
    """
    Generates an uuid that always starts with an alpha char.

    Returns
    -------
    str
    """
    uuid_ = str(uuid.uuid4())
    if not uuid_[0].isalpha():
        c = random.choice(["a", "b", "c", "d", "e", "f"])
        uuid_ = f"{c}{uuid_[1:]}"
    return uuid_


def text_to_list(order):
    """
    Turn text into list.

    Parameters
    ----------
    order : str
        Column name and order.

    Returns
    -------
    list
    """
    order_by = []
    regex = re.compile(r"\[(.*?)\]|(\S+)")
    matches = regex.finditer(order)
    for match in matches:
        order_by.append(match.group(2)) if match.group(1) is None else order_by.append(
            match.group(1)
        )
    return order_by


def parse_dataframe_to_seldon_request(dataframe):
    """
    Parse a pandas dataframe to seldon request.

    Parameters
    ----------
    dataframe : pandas.core.frame.DataFrame

    Returns
    -------
    dict
        In seldon request format.
    """
    dataframe = dataframe.to_dict("split")
    return {
        "data": {
            "names": dataframe["columns"],
            "ndarray": dataframe["data"],
        }
    }


def parse_file_buffer_to_seldon_request(file):
    """
    Reads file buffer and parse to seldon request.

    Parameters
    ----------
    file : dict
        Spooled temporary file.

    Returns
    -------
    dict
        Seldon API request
    """
    try:
        df = pandas.read_csv(file, sep=None, engine="python")

        return parse_dataframe_to_seldon_request(df)

    except UnicodeDecodeError:
        file.seek(0)
        content = file.read()
        bin_data = base64.b64encode(content).decode("utf-8")

        kind = filetype.guess(content)
        content_type = "application/octet-stream"
        if kind is not None:
            content_type = kind.mime

        return {
            "binData": bin_data,
            "meta": {
                "content-type": content_type,
            },
        }

    except csv.Error:
        file.seek(0)
        return {"strData": file.read().decode("utf-8")}


# This is necessary to mysql consider special character
# maybe this logic won't work on another database
# maybe we can refactor this!
def escaped_format(string):
    escaped_string = ""
    # to avoid the trouble of identify every special character we gonna escape all!
    for character in string:
        escaped_string = escaped_string + "\\" + character
    return escaped_string


def has_special_character(allowed_special_character_regex, string):
    if re.findall(allowed_special_character_regex, string):
        return True
    else:
        return False


def has_forbidden_character(string, forbidden_special_character_regex):
    if re.findall(forbidden_special_character_regex, string):
        return True
    else:
        return False


def has_exceed_characters_amount(string, max_chars_allowed):
    if len(string) > max_chars_allowed:
        return True
    else:
        return False


def process_filter_value(
    value, column, forbidden_characters_regex, allowed_special_characters_regex
):
    # actually this rule is only applied in column name!!
    if column == "name":

        if has_forbidden_character(
            value,
            forbidden_characters_regex,
        ):
            is_valid = False
            return ("Filter contains not allowed characters", is_valid)

        elif has_exceed_characters_amount(value, MAX_CHARS_ALLOWED):
            is_valid = False
            return ("Filter exceed maximum characters amount", is_valid)

        elif has_special_character(value, allowed_special_characters_regex):
            is_valid = True
            return (
                escaped_format(value),
                is_valid,
            )

        else:
            is_valid = True
            return (value, is_valid)
    else:
        is_valid = True
        return (value, is_valid)
