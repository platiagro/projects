# -*- coding: utf-8 -*-
"""Functions that access Jupyter Notebook API."""
from json import dumps, loads, JSONDecodeError
from os import getenv
from os.path import dirname
from re import compile, sub

from minio.error import NoSuchKey
from requests import Session

from .object_storage import BUCKET_NAME, get_object

JUPYTER_ENDPOINT = getenv("JUPYTER_ENDPOINT", "http://server.anonymous:80/notebook/anonymous/server")
URL_CONTENTS = f"{JUPYTER_ENDPOINT}/api/contents"
URL_WORKSPACES = f"{JUPYTER_ENDPOINT}/lab/api/workspaces/lab"

COOKIES = {"_xsrf": "token"}
HEADERS = {"content-type": "application/json", "X-XSRFToken": "token"}

SESSION = Session()
SESSION.cookies.update(COOKIES)
SESSION.headers.update(HEADERS)
SESSION.hooks = {
    "response": lambda r, *args, **kwargs: r.raise_for_status(),
}


def list_files(path):
    """Lists the files in the specified path.

    Args:
        path (str): path to a folder.

    Returns:
        list: A list of filenames.
    """
    r = SESSION.get(url=f"{URL_CONTENTS}/{path}")
    return r.json()


def create_new_file(path, is_folder, content=None):
    """Creates a new file or directory in the specified path.

    Args:
        path (str): path to the file or folder.
        is_folder (bool): whether to create a file or a folder.
        content (bool, optional): the file content.
    """
    if content is not None:
        content = loads(content.decode("utf-8"))

    filetype = "directory" if is_folder else "notebook"
    payload = {"type": filetype, "content": content}

    SESSION.put(
        url=f"{URL_CONTENTS}/{path}",
        data=dumps(payload),
    )


def delete_file(path):
    """Deletes a file or directory in the given path.

    Args:
        path (str): path to the file.
    """
    SESSION.delete(
        url=f"{URL_CONTENTS}/{path}",
    )


def set_workspace(*args):
    """Sets the notebooks that are open in the default workspace.

    Args:
        *args: list of notebook paths.
    """
    r = SESSION.get(url=URL_WORKSPACES)
    resp = r.json()

    prefixed_args = [f"notebook:{arg}" for arg in args]

    data = resp["data"]
    data["layout-restorer:data"] = {
        "main": {
            "dock": {
                "type": "tab-area",
                "currentIndex": 0,
                "widgets": prefixed_args,
            },
            "mode": "multiple-document",
            "current": next(iter(prefixed_args), None),
        }
    }

    if len(args) > 0:
        data["file-browser-filebrowser:cwd"] = {
            "path": dirname(args[-1]),
        }

    for path, prefix_path in zip(args, prefixed_args):
        data[prefix_path] = {
            "data": {
                "path": path,
                "factory": "Notebook",
            }
        }

    SESSION.put(
        url=URL_WORKSPACES,
        data=dumps(resp),
    )


def read_parameters(path):
    """Lists the parameters declared in a notebook.

    Args:
        path (str): path to the .ipynb file.

    Returns:
        list: a list of parameters (name, default, type, label, description).
    """
    object_name = path[len(f"minio://{BUCKET_NAME}/"):]
    try:
        training_notebook = loads(get_object(object_name).decode("utf-8"))
    except (NoSuchKey, JSONDecodeError):
        return []

    parameters = []
    cells = training_notebook.get("cells", [])
    for cell in cells:
        cell_type = cell["cell_type"]
        tags = cell["metadata"].get("tags", [])
        if cell_type == "code" and "parameters" in tags:
            source = cell["source"]

            parameters.extend(
                read_parameters_from_source(source),
            )

    return parameters


def read_parameters_from_source(source):
    """Lists the parameters declared in source code.

    Args:
        source (list): source code lines.

    Returns:
        list: a list of parameters (name, default, type, label, description).
    """
    parameters = []
    # Regex to capture a parameter declaration
    # Inspired by Google Colaboratory Forms
    # Example of a parameter declaration:
    # name = "value" #@param ["1st option", "2nd option"] {type:"string", label:"Foo Bar", description:"Foo Bar"}
    pattern = compile(r"^(\w+)\s*=\s*(.+)\s+#@param(?:(\s+\[.*\]))?(\s+\{.*\})")

    for line in source:
        match = pattern.search(line)
        if match:
            try:
                name = match.group(1)
                default = match.group(2)
                options = match.group(3)
                metadata = match.group(4)

                parameter = {"name": name, "default": loads(default)}

                if options:
                    parameter["options"] = loads(options)

                # adds quotes to metadata keys
                metadata = sub(r"(\w+):", r'"\1":', metadata)
                parameter.update(loads(metadata))

                parameters.append(parameter)
            except JSONDecodeError:
                pass

    return parameters
