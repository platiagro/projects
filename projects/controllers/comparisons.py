# -*- coding: utf-8 -*-
"""Comparison controller."""
from datetime import datetime

from projects import models, schemas
from projects.controllers.experiments import ExperimentController
from projects.controllers.utils import uuid_alpha
from projects.exceptions import BadRequest, NotFound

NOT_FOUND = NotFound("The specified comparison does not exist")


class ComparisonController:
    def __init__(self, session):
        self.session = session
        self.experiment_controller = ExperimentController(session)

    def raise_if_comparison_does_not_exist(self, comparison_id: str):
        """
        Raises an exception if the specified comparison does not exist.

        Parameters
        ----------
        comparison_id : str

        Raises
        ------
        NotFound
        """
        exists = self.session.query(models.Comparison.uuid) \
            .filter_by(uuid=comparison_id) \
            .scalar() is not None

        if not exists:
            raise NOT_FOUND

    def list_comparisons(self, project_id: str):
        """
        Lists all comparisons under a project.

        Parameters
        ----------
        project_id : str

        Returns
        -------
        projects.schemas.comparison.ComparisonList

        Raises
        ------
        NotFound
            When project_id does not exist.
        """
        comparisons = self.session.query(models.Comparison) \
            .filter_by(project_id=project_id) \
            .order_by(models.Comparison.created_at.asc()) \
            .all()

        return schemas.ComparisonList.from_model(comparisons, len(comparisons))

    def create_comparison(self, project_id: str):
        """
        Creates a new comparison in our database.

        Parameters
        ----------
        project_id : str

        Returns
        -------
        projects.schemas.comparison.Comparison
        """
        comparison = models.Comparison(uuid=uuid_alpha(), project_id=project_id)
        self.session.add(comparison)
        self.session.commit()
        self.session.refresh(comparison)

        return schemas.Comparison.from_model(comparison)

    def update_comparison(self, comparison: schemas.ComparisonUpdate, project_id: str, comparison_id: str):
        """
        Updates a comparison in our database.

        Parameters
        ----------
        comparison: projects.schemas.comparison.ComparisonUpdate
        project_id : str
        comparison_id : str

        Returns
        -------
        projects.schemas.comparison.Comparison

        Raises
        ------
        BadRequest
            When comparison attributes are invalid.
        NotFound
            When comparison_id does not exist.
        """
        self.raise_if_comparison_does_not_exist(comparison_id)

        if comparison.experiment_id:
            stored_experiment = self.session.query(models.Experiment).get(comparison.experiment_id)
            if stored_experiment is None:
                raise BadRequest("The specified experiment does not exist")

        update_data = comparison.dict(exclude_unset=True)
        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Comparison).filter_by(uuid=comparison_id).update(update_data)
        self.session.commit()

        comparison = self.session.query(models.Comparison).get(comparison_id)

        return schemas.Comparison.from_model(comparison)

    def delete_comparison(self, project_id: str, comparison_id: str):
        """
        Delete a comparison in our database.

        Parameters
        ----------
        project_id : str
        comparison_id : str

        Returns
        -------
        projects.schemas.message.Message

        Raises
        ------
        NotFound
            When comparison_id does not exist.
        """
        comparison = self.session.query(models.Comparison).get(comparison_id)

        if comparison is None:
            raise NOT_FOUND

        self.session.delete(comparison)

        return schemas.Message(message="Comparison deleted")
