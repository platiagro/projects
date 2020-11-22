# -*- coding: utf-8 -*-
"""Experiment Runs blueprint."""
from flask import Blueprint, jsonify

from projects.controllers.experiments.runs import create_run, get_run, \
    list_runs, terminate_run, retry_run

bp = Blueprint("experiment_runs", __name__)


@bp.route("", methods=["GET"])
def handle_list_runs(project_id, experiment_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str

    Returns
    -------
    str
    """
    runs = list_runs(project_id=project_id,
                     experiment_id=experiment_id)
    return jsonify(runs)


@bp.route("", methods=["POST"])
def handle_post_run(project_id, experiment_id):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    experiment_id : str

    Returns
    -------
    str
    """
    run = create_run(project_id=project_id,
                     experiment_id=experiment_id)
    return jsonify(run)


@bp.route("<run_id>", methods=["GET"])
def handle_get_run(project_id, experiment_id, run_id):
    """
    Handles GET requests to /<run_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str

    Returns
    -------
    str
    """
    run = get_run(project_id=project_id,
                  experiment_id=experiment_id,
                  run_id=run_id)
    return jsonify(run)


@bp.route("<run_id>", methods=["DELETE"])
def handle_delete_run(project_id, experiment_id, run_id):
    """
    Handles DELETE requests to /<run_id>.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str

    Returns
    -------
    str
    """
    run = terminate_run(project_id=project_id,
                        experiment_id=experiment_id,
                        run_id=run_id)
    return jsonify(run)


@bp.route("<run_id>/retry", methods=["POST"])
def handle_post_retry_run(project_id, experiment_id, run_id):
    """
    Handles POST requests to /<run_id>/retry.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str

    Returns
    -------
    str
    """
    run = retry_run(project_id=project_id,
                    experiment_id=experiment_id,
                    run_id=run_id)
    return jsonify(run)
