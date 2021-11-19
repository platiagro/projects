# -*- coding: utf-8 -*-
"""Experiments Datasets controller."""
from typing import Optional

import numpy as np
import pandas as pd
from fastapi.responses import StreamingResponse
from platiagro import load_dataset, stat_dataset

from projects import models
from projects.exceptions import NotFound
from projects.kfp.runs import get_latest_run_id


class DatasetController:
    def __init__(self, session):
        self.session = session

    def get_dataset(
        self,
        project_id: str,
        experiment_id: str,
        run_id: str,
        operator_id: str,
        page: Optional[int] = 1,
        page_size: Optional[int] = 10,
        accept: Optional[str] = None,
    ):
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
        accept : str
            Whether dataset should be returned as csv file. Default to None.

        Returns
        -------
        list
            A list of dataset records.

        Raises
        ------
        NotFound
            When any of project_id, experiment_id, run_id, or operator_id does not exist.
        """
        if run_id == "latest":
            run_id = get_latest_run_id(experiment_id)

        name = self.get_dataset_name(operator_id, experiment_id)

        try:
            metadata = stat_dataset(name=name, operator_id=operator_id, run_id=run_id)
        except FileNotFoundError:
            raise NotFound(
                code="DatasetNotFound",
                message="The specified run does not contain dataset",
            )

        dataset = load_dataset(
            name=name,
            run_id=run_id,
            operator_id=operator_id,
            page=page,
            page_size=page_size,
        )
        if isinstance(dataset, pd.DataFrame):
            # Replaces NaN value by a text "NaN" so JSON encode doesn't fail
            dataset.replace(np.nan, "NaN", inplace=True, regex=True)
            data = dataset.to_dict(orient="split")
            total = metadata.get("total", len(dataset.index))
            return {"columns": data["columns"], "data": data["data"], "total": total}

        return StreamingResponse(
            dataset,
            media_type="application/octet-stream",
        )

    def get_dataset_name(self, operator_id, experiment_id):
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
        operator = self.session.query(models.Operator).get(operator_id)
        dataset_name = operator.parameters.get("dataset")

        if dataset_name is None:
            operators = (
                self.session.query(models.Operator)
                .filter_by(experiment_id=experiment_id)
                .filter(models.Operator.uuid != operator_id)
                .all()
            )

            for operator in operators:
                dataset_name = operator.parameters.get("dataset")
                if dataset_name:
                    break

            if dataset_name is None:
                raise NotFound(
                    code="DatasetNotFound", message="No dataset assigned to the run"
                )

        return dataset_name
