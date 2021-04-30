# -*- coding: utf-8 -*-
"""Functions that access Jupyter Notebook API."""
import json
import os

from requests import Session
from requests.adapters import HTTPAdapter
from requests.exceptions import HTTPError
from requests.packages.urllib3.util.retry import Retry


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
    allowed_methods=["HEAD", "GET", "PUT", "OPTIONS", "DELETE"],
)
ADAPTER = HTTPAdapter(max_retries=RETRY_STRATEGY)
SESSION.mount("http://", ADAPTER)


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
