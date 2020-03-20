# -*- coding: utf-8 -*-
import json
from os import getenv

import requests
from werkzeug.exceptions import BadRequest

from .object_storage import BUCKET_NAME, get_object

ENDPOINT = getenv("JUPYTER_ENDPOINT", "server.anonymous:80/notebook/anonymous/server")

URL_CONTENTS = ENDPOINT + "/api/contents/{}"

URL_WORKSPACES = ENDPOINT + "/lab/api/workspaces/lab"

COOKIES = dict(_xsrf="token")

HEADERS = {"content-type": "application/json", "X-XSRFToken": "token"}


def get_full_file_path(folder_path, filename):
    if folder_path == "":
        full_filepath = filename
    else:
        full_filepath = folder_path + "/" + filename
    return full_filepath


def get_file(folder_path, name):
    full_filepath = get_full_file_path(folder_path, name)
    r = requests.get(url=URL_CONTENTS.format(full_filepath))
    if r.status_code != requests.codes.ok:
        return
    return r.json()


def remove_file(path):
    r = requests.delete(url=URL_CONTENTS.format(path), cookies=COOKIES,
                        headers=HEADERS)
    if r.status_code != requests.codes.no_content:
        raise BadRequest(r.json())
    return


def get_files(path):
    r = requests.get(url=URL_CONTENTS.format(path))
    if r.status_code == requests.codes.ok:
        return r.json()
    return


def create_new_file(folder_path, name, is_folder, content=None):

    if content is not None:
        content = json.loads(content.decode("utf-8"))

    full_filepath = get_full_file_path(folder_path, name)

    fileType = "directory" if is_folder else "notebook"

    payload = {"type": fileType, "content": content}

    r = requests.put(
        url=URL_CONTENTS.format(full_filepath),
        cookies=COOKIES,
        headers=HEADERS,
        data=json.dumps(payload)
    )

    if r.status_code != requests.codes.created:
        return

    return r.json()


def set_workspace(path, inference_filename, training_filename):
    r = requests.get(url=URL_WORKSPACES)

    if r.status_code != requests.codes.ok:
        return

    inference = "notebook:{}/{}".format(path, inference_filename)
    training = "notebook:{}/{}".format(path, training_filename)

    resp = r.json()
    data = resp["data"]
    data["layout-restorer:data"] = {
        "main": {
            "dock": {
                "type": "tab-area",
                "currentIndex": 0,
                "widgets": [inference, training]
            },
            "mode": "multiple-document",
            "current": inference
        }
    }
    data["file-browser-filebrowser:cwd"] = {
        "path": path
    }
    data[inference] = {
        "data": {
            "path": "{}/{}".format(path, inference_filename),
            "factory": "Notebook"
        }
    }
    data[training] = {
        "data": {
            "path": "{}/{}".format(path, training_filename),
            "factory": "Notebook"
        }
    }

    r = requests.put(
        url=URL_WORKSPACES,
        cookies=COOKIES,
        headers=HEADERS,
        data=json.dumps(resp)
    )


def read_parameters(notebook_path):
    notebook_params = []
    object_name = notebook_path[len("minio://{}/".format(BUCKET_NAME)):]
    training_notebook = get_object(object_name)
    json_training_notebook = json.loads(training_notebook.decode("utf-8"))

    if "cells" not in json_training_notebook:
        return notebook_params

    cells = json_training_notebook["cells"]
    for cell in cells:
        cell_type = cell["cell_type"]
        if cell_type == "code":
            source = cell["source"]
            for line in source:
                if "#@param" in line:
                    # name = "value" #@param {type:"string"}
                    param_values = line.replace("\n", "").split("#@param")

                    # name = value
                    part1 = param_values[0].split("=")
                    param_name = part1[0].strip()
                    param_default = part1[1].replace("\"", "").strip()

                    # {type:"string"}
                    part2 = param_values[1].replace("type", '"type"').strip()

                    # create json param and add to array
                    param = json.loads(part2)
                    param["name"] = param_name
                    param["default"] = param_default
                    notebook_params.append(param)

    return notebook_params
