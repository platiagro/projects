# -*- coding: utf-8 -*-
"""Functions that access Jupyter Notebook API."""
from json import dumps, loads, JSONDecodeError
from os import getenv
from re import compile, sub

from minio.error import NoSuchKey
from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry

from .object_storage import BUCKET_NAME, get_object
from .utils import remove_ansi_escapes

JUPYTER_ENDPOINT = getenv("JUPYTER_ENDPOINT", "http://server.anonymous:80/notebook/anonymous/server")
URL_CONTENTS = f"{JUPYTER_ENDPOINT}/api/contents"

COOKIES = {"_xsrf": "token"}
HEADERS = {"content-type": "application/json", "X-XSRFToken": "token"}

SESSION = Session()
SESSION.cookies.update(COOKIES)
SESSION.headers.update(HEADERS)
SESSION.hooks = {
    "response": lambda r, *args, **kwargs: r.raise_for_status(),
}
RETRY_STRATEGY = Retry(
    total=5,
    backoff_factor=0.5,
    status_forcelist=[429, 500, 502, 503, 504],
    method_whitelist=["HEAD", "GET", "PUT", "OPTIONS", "DELETE"]
)
ADAPTER = HTTPAdapter(max_retries=RETRY_STRATEGY)
SESSION.mount("http://", ADAPTER)


def list_files(path):
    """Lists the files in the specified path.

    Args:
        path (str): path to a folder.

    Returns:
        list: A list of filenames.
    """
    try:
        r = SESSION.get(url=f"{URL_CONTENTS}/{path}")
        return r.json()
    except HTTPError as e:
        status_code = e.response.status_code
        if status_code == 404:
            return None


def create_new_file(path, is_folder, content=None):
    """Creates a new file or directory in the specified path.

    Args:
        path (str): path to the file or folder.
        is_folder (bool): whether to create a file or a folder.
        content (bytes, optional): the file content.
    """
    if content is not None:
        content = loads(content.decode("utf-8"))

    filetype = "directory" if is_folder else "notebook"
    payload = {"type": filetype, "content": content}

    SESSION.put(
        url=f"{URL_CONTENTS}/{path}",
        data=dumps(payload),
    )


def update_folder_name(path, new_path):
    """Update folder name.
    Args:
        path (str): path folder.
        new_path (str): new path to the folder.
    """
    payload = {"path": new_path}
    SESSION.patch(
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


def read_parameters(path):
    """Lists the parameters declared in a notebook.

    Args:
        path (str): path to the .ipynb file.

    Returns:
        list: a list of parameters (name, default, type, label, description).
    """
    object_name = path[len(f"minio://{BUCKET_NAME}/"):]
    try:
        experiment_notebook = loads(get_object(object_name).decode("utf-8"))
    except (NoSuchKey, JSONDecodeError):
        return []

    parameters = []
    cells = experiment_notebook.get("cells", [])
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

                parameter = {"name": name}

                if default and default != 'None':
                    if default in ["True", "False"]:
                        default = default.lower()
                    parameter["default"] = loads(default)

                if options:
                    parameter["options"] = loads(options)

                # adds quotes to metadata keys
                metadata = sub(r"(\w+):", r'"\1":', metadata)
                parameter.update(loads(metadata))

                parameters.append(parameter)
            except JSONDecodeError:
                pass

    return parameters


def get_notebook_output(experiment_id: str, operator_id: str):
    """Get Experiment notebook output.

    Args:
        experiment_id (str): experiment id
        operator_id (str): operator id

    Returns:
        dict: a dictonary with output.
    """
    operator_endpoint = f"experiments/{experiment_id}/operators/{operator_id}/Experiment.ipynb"
    r = SESSION.get(url=f"{URL_CONTENTS}/{operator_endpoint}").content

    notebook_content = loads(r.decode("utf-8"))["content"]

    for cell in notebook_content["cells"]:
        try:
            metadata = cell["metadata"]["papermill"]

            if metadata["exception"] and metadata["status"] == "failed":
                output = cell["outputs"][0]
                traceback = remove_ansi_escapes(output["traceback"])

                response = {
                    "cellType": cell["cell_type"],
                    "executionCount": cell["executionCount"],
                    "output": {
                        "errorName": output["ename"],
                        "errorValue": output["evalue"],
                        "traceback": traceback,
                    }
                }

                return response
        except KeyError:
            pass
