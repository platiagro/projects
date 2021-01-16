# -*- coding: utf-8 -*-
"""Comparison controller."""
from datetime import datetime

from sqlalchemy.exc import InvalidRequestError, ProgrammingError
from werkzeug.exceptions import BadRequest, NotFound

from projects.controllers.experiments import ExperimentController
from projects.controllers.utils import uuid_alpha
from projects.models import Comparison


NOT_FOUND = NotFound("The specified comparison does not exist")


class ComparisonController:
    def __init__(self, session):
        self.session = session
        self.experiment_controller = ExperimentController(session)

    def list_comparisons(self, project_id):
        """
        Lists all comparisons under a project.

        Parameters
        ----------
        project_id : str

        Returns
        -------
        list
            A list of all comparisons.

        Raises
        ------
        NotFound
            When project_id does not exist.
        """
        comparisons = self.session.query(Comparison) \
            .filter_by(project_id=project_id) \
            .order_by(Comparison.created_at.asc()) \
            .all()

        return comparisons

    def create_comparison(self, project_id=None):
        """
        Creates a new comparison in our database.

        Parameters
        ----------
        project_id : str

        Returns
        -------
        dict
            The comparison attributes.

        Raises
        ------
        NotFound
            When project_id does not exist.
        """
        comparison = Comparison(uuid=uuid_alpha(), project_id=project_id)
        self.session.add(comparison)

        return comparison

    def update_comparison(self, project_id, comparison_id, **kwargs):
        """
        Updates a comparison in our database.

        Parameters
        ----------
        project_id : str
        comparison_id : str
        **kwargs
            Arbitrary keyword arguments.

        Returns
        -------
        dict
            The comparison attributes.

        Raises
        ------
        BadRequest
            When the `**kwargs` (comparison attributes) are invalid.
        NotFound
            When either project_id or comparison_id does not exist.
        """
        comparison = self.session.query(Comparison).get(comparison_id)

        if comparison is None:
            raise NOT_FOUND

        experiment_id = kwargs.get("experiment_id", None)
        if experiment_id:
            self.experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

        data = {"updated_at": datetime.utcnow()}
        data.update(kwargs)

        try:
            self.session.query(Comparison) \
                .filter_by(uuid=comparison_id) \
                .update(data)
        except (InvalidRequestError, ProgrammingError) as e:
            raise BadRequest(str(e))

        return comparison

    def delete_comparison(self, project_id, comparison_id):
        """
        Delete a comparison in our database.

        Parameters
        ----------
        project_id : str
        comparison_id : str

        Returns
        -------
        dict
            The deletion result.

        Raises
        ------
        NotFound
            When either project_id or comparison_id does not exist.
        """
        comparison = self.session(Comparison).get(comparison_id)

        if comparison is None:
            raise NOT_FOUND

        self.session.delete(comparison)

        return {"message": "Comparison deleted"}
