# -*- coding: utf-8 -*-
"""Datasets controller."""

import platiagro

from werkzeug.exceptions import NotFound

from .utils import raise_if_operator_does_not_exist, \
    raise_if_project_does_not_exist, pagination_datasets
from ..models import Experiment


def get_dataset(project_id, experiment_id, operator_id):
    """Retrieves a dataset as json.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        operator_id (str): the operator uuid.
    """
    raise_if_project_does_not_exist(project_id)

    experiment = Experiment.query.get(experiment_id)

    if experiment is None:
        raise NotFound("The specified experiment does not exist")

    raise_if_operator_does_not_exist(operator_id)

    try:
        metadata = platiagro.stat_dataset(name=experiment.dataset,
                                          operator_id=operator_id)
        if "run_id" not in metadata:
            raise FileNotFoundError()

        dataset = platiagro.load_dataset(name=experiment.dataset,
                                         run_id="latest",
                                         operator_id=operator_id)
        dataset = dataset.to_dict(orient="split")
        del dataset["index"]
    except FileNotFoundError as e:
        raise NotFound(str(e))

    return dataset


def get_dataset_pagination(project_id, experiment_id, operator_id, page, page_size):
    """Retrieves a dataset as json.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        operator_id (str): the operator uuid.
    """
    raise_if_project_does_not_exist(project_id)

    experiment = Experiment.query.get(experiment_id)

    if experiment is None:
        raise NotFound("The specified experiment does not exist")

    raise_if_operator_does_not_exist(operator_id)

    try:
        metadata = platiagro.stat_dataset(name=experiment.dataset,
                                          operator_id=operator_id)
        if "run_id" not in metadata:
            raise FileNotFoundError()

        dataset = platiagro.load_dataset(name=experiment.dataset,
                                         run_id="latest",
                                         operator_id=operator_id)
        dataset = dataset.to_dict(orient="split")
        del dataset["index"]
    except FileNotFoundError as e:
        raise NotFound(str(e))
    return pagination_datasets(page=page, page_size=page_size, elements=dataset)
