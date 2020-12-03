# -*- coding: utf-8 -*-
"""Experiments Datasets controller."""
from itertools import zip_longest
from flask import make_response
from pandas import DataFrame
from platiagro import load_dataset, stat_dataset
from werkzeug.exceptions import NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_experiment_does_not_exist, raise_if_operator_does_not_exist
from projects.database import db_session
from projects.kfp.runs import get_latest_run_id
from projects.models import Operator


def get_dataset(project_id, experiment_id, run_id, operator_id, page=1, page_size=10, application_csv=False):
    """
    Get dataset records from a run. Supports pagination.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
        The run_id. If `run_id=latest`, then returns datasets from the latest run_id.
    operator_id : str
    page : int
        The page number. First page is 1.
    page_size : int
        The page size. Default value is 10.
    application_csv : str or bool
        Whenever dataset should be returned as csv file. Default to False.

    Returns
    -------
    list
        A list of dataset records.

    Raises
    ------
    NotFound
        When any of project_id, experiment_id, run_id, or operator_id does not exist.
    """
    raise_if_project_does_not_exist(project_id)
    raise_if_experiment_does_not_exist(experiment_id)
    raise_if_operator_does_not_exist(operator_id, experiment_id)

    if run_id == "latest":
        run_id = get_latest_run_id(experiment_id)

    name = get_dataset_name(operator_id, experiment_id)
    metadata = stat_dataset(name=name, operator_id=operator_id)

    if "run_id" not in metadata:
        raise NotFound("The specified run does not contain dataset")

    dataset = load_dataset(name=name, run_id=run_id, operator_id=operator_id)
    content = dataset.values.tolist()
    paged_data = data_pagination(page, page_size, content)

    if application_csv and "application/csv" in application_csv:
        if page_size == -1:
            content = dataset.to_csv(index=False)
        else:
            dataFrame = DataFrame(columns=dataset.columns, data=paged_data)
            content = dataFrame.to_csv(index=False)

        response = make_response(content)
        response.headers["Content-Disposition"] = f"attachment; filename={name}"
        response.headers["Content-type"] = "text/csv"
        return response
    else:
        if page_size == -1:
            return dataset.to_dict(orient="split")
        else:
            return {"columns": dataset.columns, "data": paged_data, "total": len(dataset)}


def data_pagination(page, page_size, content):
    """
    Page records of a dataset.

    Parameters
    ----------
    page : int
    page_size : int
    content : pandas.DataFrame

    Returns
    -------
    list
        A list of dataset records

    Raises
    ------
    NotFound
        When a page does not exist.
    """
    # Splits records into `page_size` size
    split_into_pages = list(list(zip_longest(*(iter(content),) * abs(page_size))))

    try:
        # if the last page is not filled (has the length of page_size), `zip_longest`
        # fills with None values. Remove these values before returning
        paged_data = list(filter(None, split_into_pages[page-1]))
    except IndexError:
        raise NotFound("The specified page does not exist")

    return paged_data


def get_dataset_name(operator_id, experiment_id):
    """
    Get operator's dataset name.

    Parameters
    ----------
    operator_id : str
    experiment_id: str

    Returns
    -------
    str
        The dataset name.

    Raises
    ------
    NotFound
        When a run does not have a dataset.
    """
    operator = Operator.query.get(operator_id)
    dataset_name = operator.parameters.get("dataset")

    if dataset_name is None:
        operators = db_session.query(Operator) \
            .filter_by(experiment_id=experiment_id) \
            .filter(Operator.uuid != operator_id) \
            .all()

        for operator in operators:
            dataset_name = operator.parameters.get("dataset")
            if dataset_name:
                break

        if dataset_name is None:
            raise NotFound("No dataset assigned to the run")

    return dataset_name
