# -*- coding: utf-8 -*-
"""Shared functions."""
import base64
import csv
import random
import re
import uuid

import filetype
import pandas


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
        order_by.append(match.group(2)) if match.group(1) is None else order_by.append(match.group(1))
    return order_by


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

    Raises
    ------
    BadRequest
        When `file` has no header.
    """
    try:
        df = pandas.read_csv(file._file, sep=None, engine='python')
        df = df.to_dict('split')

        return {
            "data": {
                "names": df['columns'],
                "ndarray": df['data'],
            }
        }

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
        return {
            "strData": file.read().decode("utf-8")
        }
