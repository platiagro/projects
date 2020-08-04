# -*- coding: utf-8 -*-
"""Datasets controller."""

import platiagro

from werkzeug.exceptions import NotFound

from .utils import raise_if_experiment_does_not_exist, \
    raise_if_project_does_not_exist, pagination_datasets
from ..models import Operator

def get_dataset_pagination(project_id, experiment_id, operator_id, page, page_size):
    """Retrieves a dataset as json.

    Args:
        project_id (str): the project uuid.
        experiment_id (str): the experiment uuid.
        operator_id (str): the operator uuid.
    """
    raise_if_project_does_not_exist(project_id)

    raise_if_experiment_does_not_exist(experiment_id)

    operator = Operator.query.get(operator_id)
    if operator is None:
        raise NotFound("The specified operator does not exist")

    # get dataset name
    dataset = operator.parameters.get('dataset')
    if dataset is None:
        raise NotFound()

    try:
        metadata = platiagro.stat_dataset(name=dataset, operator_id=operator_id)
        if "run_id" not in metadata:
            raise FileNotFoundError()

        dataset = platiagro.load_dataset(name=dataset,
                                         run_id="latest",
                                         operator_id=operator_id)
        dataset = dataset.to_dict(orient="split")
        del dataset["index"]
    except FileNotFoundError as e:
        raise NotFound(str(e))
    return pagination_datasets(page=page, page_size=page_size, elements=dataset)
