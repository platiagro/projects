# -*- coding: utf-8 -*-
"""Experiments Datasets controller."""
import platiagro
from werkzeug.exceptions import NotFound

from projects.controllers.utils import raise_if_project_does_not_exist, \
    raise_if_experiment_does_not_exist
from projects.database import db_session
from projects.models import Operator


def list_datasets(project_id, experiment_id, run_id, operator_id, page=1, page_size=10):
    """
    Lists datasets records from a run. Supports pagination.

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

    operator = Operator.query.get(operator_id)
    if operator is None:
        raise NotFound("The specified operator does not exist")

    # get dataset name
    dataset = operator.parameters.get("dataset")
    if dataset is None:
        # try to find dataset name in other operators
        operators = db_session.query(Operator) \
            .filter_by(experiment_id=experiment_id) \
            .filter(Operator.uuid != operator_id) \
            .all()
        for operator in operators:
            dataset = operator.parameters.get("dataset")
            if dataset:
                break
        if dataset is None:
            raise NotFound()

    try:
        metadata = platiagro.stat_dataset(name=dataset, operator_id=operator_id)
        if "run_id" not in metadata:
            raise FileNotFoundError()

        dataset = platiagro.load_dataset(name=dataset,
                                         run_id=run_id,
                                         operator_id=operator_id)
        dataset = dataset.to_dict(orient="split")
        del dataset["index"]
    except FileNotFoundError as e:
        raise NotFound(str(e))

    try:
        count = 0
        new_datasets = []
        total_elements = len(dataset["data"])
        page = (page * page_size) - page_size
        for i in range(page, total_elements):
            new_datasets.append(dataset["data"][i])
            count += 1
            if page_size == count:
                response = {
                    "columns": dataset["columns"],
                    "data": new_datasets,
                    "total": len(dataset["data"])
                }
                return response
        if len(new_datasets) == 0:
            raise NotFound("The informed page does not contain records")
        else:
            response = {
                "columns": dataset["columns"],
                "data": new_datasets,
                "total": len(dataset["data"])
            }
            return response
    except RuntimeError:
        raise NotFound("The specified page does not exist")
