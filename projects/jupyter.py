# -*- coding: utf-8 -*-
"""Functions that access Jupyter Notebook API."""
import json
import os

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry

from projects.utils import remove_ansi_escapes

DEFAULT_ENDPOINT = "http://server.anonymous:80/notebook/anonymous/server"
JUPYTER_ENDPOINT = os.getenv("JUPYTER_ENDPOINT", DEFAULT_ENDPOINT)
SUPPORTED_TYPES = ["Deployment", "Experiment"]

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
        r = SESSION.get(url=f"{JUPYTER_ENDPOINT}/api/contents/{path}")
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
        content = json.loads(content.decode("utf-8"))

    filetype = "directory" if is_folder else "notebook"
    payload = {"type": filetype, "content": content}

    SESSION.put(
        url=f"{JUPYTER_ENDPOINT}/api/contents/{path}",
        data=json.dumps(payload),
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
        url=f"{JUPYTER_ENDPOINT}/api/contents/{path}",
        data=json.dumps(payload),
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
        url=f"{JUPYTER_ENDPOINT}/api/contents/{path}",
    )


def get_notebook_logs(experiment_id, operator_id):
    """
    Get logs from a Experiment notebook.

    Parameters
    ----------
    experiment_id : str
    operator_id : str

    Returns
    -------
    dict or None
        Operator's notebook logs. Or None when the notebook file is not found.
    """
    notebook = get_jupyter_notebook(experiment_id, operator_id)

    if not notebook:
        return None

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


def get_jupyter_notebook(experiment_id, operator_id, notebook_type="Experiment"):
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
        r = SESSION.get(url=f"{JUPYTER_ENDPOINT}/api/contents/{operator_endpoint}").content
        content = json.loads(r.decode("utf-8"))

        return content
    except HTTPError as e:
        status_code = e.response.status_code
        if status_code == 404:
            return {}
        raise HTTPError("Error occured while trying to access Jupyter API.")
