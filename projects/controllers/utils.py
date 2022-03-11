# -*- coding: utf-8 -*-
"""Shared functions."""
import base64
import csv
import random
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
