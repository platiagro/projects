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

from projects.object_storage import BUCKET_NAME, get_object
from projects.utils import remove_ansi_escapes

JUPYTER_ENDPOINT = getenv("JUPYTER_ENDPOINT", "http://server.anonymous:80/notebook/anonymous/server")
URL_CONTENTS = f"{JUPYTER_ENDPOINT}/api/contents"
SUPPORTED_TYPES = ['Deployment', 'Experiment']

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
    """
    Lists the files in the specified path.

    Parameters
    ----------
    path : str
        Path to a folder.

    Returns
    -------
    list
        A list of filenames.
    """
    try:
        r = SESSION.get(url=f"{URL_CONTENTS}/{path}")
        return r.json()
    except HTTPError as e:
        status_code = e.response.status_code
        if status_code == 404:
            return None


def create_new_file(path, is_folder, content=None):
    """
    Creates a new file or directory in the specified path.

    Parameters
    ----------
    path : str
        Path to the file or folder.
    is_folder : bool
        Whether to create a file or a folder.
    content : bytes, optional
        The file content.
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
    """
    Update folder name.

    Parameters
    ----------
    path : str
        Path folder.
    new_path : str
        New path to the folder.
    """
    payload = {"path": new_path}
    SESSION.patch(
        url=f"{URL_CONTENTS}/{path}",
        data=dumps(payload),
    )


def delete_file(path):
    """
    Deletes a file or directory in the given path.

    Parameters
    ----------
    path : str
        Path to the file.
    """
    SESSION.delete(
        url=f"{URL_CONTENTS}/{path}",
    )


def read_parameters(path):
    """
    Lists the parameters declared in a notebook.

    Parameters
    ----------
    path : str
        Path to the .ipynb file.

    Returns
    -------
    list:
        A list of parameters (name, default, type, label, description).
    """
    if not path:
        return []

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
    """
    Lists the parameters declared in source code.

    Parameters
    ----------
    source : list
        Source code lines.

    Returns
    -------
    list:
        A list of parameters (name, default, type, label, description).
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

                if default and default != "None":
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


def get_notebook_logs(experiment_id, operator_id):
    """
    Get logs from a Experiment notebook.

    Parameters
    ----------
    experiment_id : str
    operator_id : str

    Returns
    -------
    dict
        Operator's notebook logs.
    """
    notebook = get_jupyter_notebook(experiment_id, operator_id)
    notebook = notebook["content"]
    logs = {}

    for cell in notebook["cells"]:
        try:
            metadata = cell["metadata"]["papermill"]

            if metadata["exception"] and metadata["status"] == "failed":
                for output in cell["outputs"]:
                    if output["output_type"] == "error":
                        error_log = output["traceback"]
                        traceback = remove_ansi_escapes(error_log)
                        logs = {"exception": output["ename"], "traceback": traceback}
        except KeyError:
            pass

    return logs


def get_jupyter_notebook(experiment_id, operator_id, notebook_type='Experiment'):
    """
    Get JSON content from a notebook using the JupyterLab API.

    Parameters
    ----------
    experiment_id : str
    operator_id : str
    notebook_type : str
        Notebook type: `Deployment` or `Experiment`. Default to Experiment.

    Returns
    -------
    dict
        The notebook content.

    Raises
    ------
    HTTPError
        When a error occured while trying to access Jupyter API.

    ValueError
        When the `notebook_type` isn't a supported type.
    """
    operator_endpoint = f"experiments/{experiment_id}/operators/{operator_id}/{notebook_type}.ipynb"

    if notebook_type not in SUPPORTED_TYPES:
        raise ValueError(f"The type {notebook_type} is not a valid one.")

    try:
        r = SESSION.get(url=f"{URL_CONTENTS}/{operator_endpoint}").content
        content = loads(r.decode("utf-8"))

        return content
    except HTTPError as e:
        status_code = e.response.status_code
        if status_code == 404:
            return {}
        raise HTTPError("Error occured while trying to access Jupyter API.")
