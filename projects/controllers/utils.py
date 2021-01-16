# -*- coding: utf-8 -*-
"""Shared functions."""
import base64
import csv
import random
import re
import uuid

from werkzeug.exceptions import BadRequest, NotFound
from kfp_server_api.exceptions import ApiException

from projects.kfp import kfp_client


def raise_if_run_does_not_exist(run_id):
    """
    Raises an exception if the specified run does not exist.

    Parameters
    ----------
    run_id : str

    Raises
    ------
    NotFound
    """
    try:
        kfp_client().get_run(run_id=run_id)
    except ApiException:
        raise NotFound("The specified run does not exist")


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


def list_objects(list_object):
    """
    Extracting uuids from informed json.

    Parameters
    ----------
    list_object : list
        String containing the project's uuid.

    Returns
    -------
    list
        All uuids.
    """
    all_projects_ids = []
    for i in list_object:
        all_projects_ids.append(i["uuid"])
    return all_projects_ids


def objects_uuid(list_object):
    """
    Recovering uuids from information projects.

    Parameters
    ----------
    list_object : lits
        List of project ids.

    Returns
    -------
    list
        All uuids.
    """
    uuids = []
    for i in list_object:
        uuids.append(i.uuid)
    return uuids


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
        File buffer.

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
        # read file content and parse to string
        file_buffer = file.read()
        file_buffer_str = file_buffer.decode("utf-8")

        if not csv.Sniffer().has_header(file_buffer_str):
            raise BadRequest("file needs a header.")

        # infer file delimiter
        dialect = csv.Sniffer().sniff(file_buffer_str, delimiters=";,")

        # build seldon request
        lines = file_buffer_str.split('\n')
        # split values and remove blank lines
        lines_splitted = [line.split(dialect.delimiter) for line in lines if line]
        columns = lines_splitted[0]
        data = lines_splitted[1:]

        return {
            "data": {
                "names": columns,
                "ndarray": data,
            }
        }

    except UnicodeDecodeError:
        file.seek(0)
        bin_data = base64.b64encode(file.read()).decode("utf-8")
        return {
            "binData": bin_data
        }

    except csv.Error:
        file.seek(0)
        return {
            "strData": file.read().decode("utf-8")
        }
