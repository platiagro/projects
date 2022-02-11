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
FORBIDDEN_CHARACTERS_REGEX =  "[^A-Za-z0-9-_\s]"
ESCAPE_MAP = {
        "-":"\-",
        "_": "\_",
        " ": " "
    }

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


def escaped_format(string):
    escaped_string = string
    for character in ALLOWED_SPECIAL_CHARACTERS_LIST:
        escaped_string = escaped_string.replace(character, ESCAPE_MAP.get(character)) 
    return escaped_string

def has_special_character(allowed_special_character_regex, string):
    if re.findall(allowed_special_character_regex, string):
        return True
    else:
        return False

def has_forbidden_character(forbidden_special_character_regex, string):
    if re.findall(forbidden_special_character_regex, string):
        return True
    else:
        return False

def process_filter_value(value, column):
    
    # actually this rule is only applied in column name
    if column == 'name':
        if has_forbidden_character(FORBIDDEN_CHARACTERS_REGEX, value):
            is_valid = False
            return ("Filter contains not allowed characters",is_valid)
        elif has_special_character(ALLOWED_SPECIAL_CHARACTERS_REGEX, value):
            is_valid = True
            return (escaped_format(value), is_valid)
        else:
            is_valid = True
            return (value, is_valid)
    else:
        is_valid = True
        return (value, is_valid)