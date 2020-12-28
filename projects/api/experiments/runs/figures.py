# -*- coding: utf-8 -*-
"""Experiment Figures blueprint."""
from flask import Blueprint, jsonify

from projects.controllers.experiments.runs.figures import list_figures

bp = Blueprint("figures", __name__)


@bp.route("", methods=["GET"])
def handle_list_figures(project_id, experiment_id, run_id, operator_id):
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
    figures = list_figures(project_id=project_id,
                           experiment_id=experiment_id,
                           run_id=run_id,
                           operator_id=operator_id)
    return jsonify(figures)
