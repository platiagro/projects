# -*- coding: utf-8 -*-
"""Experiment Figures blueprint."""
from flask import Blueprint, jsonify

from projects.controllers import ExperimentController, FigureController, \
    ProjectController
from projects.database import session_scope

bp = Blueprint("figures", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_figures(session, project_id, experiment_id, run_id, operator_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    operator_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    figure_controller = FigureController(session)
    figures = figure_controller.list_figures(project_id=project_id,
                                             experiment_id=experiment_id,
                                             run_id=run_id,
                                             operator_id=operator_id)
    return jsonify(figures)
