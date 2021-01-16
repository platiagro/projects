# -*- coding: utf-8 -*-
"""Experiment Runs blueprint."""
from flask import Blueprint, jsonify

from projects.controllers import ExperimentController, ProjectController
from projects.controllers.experiments.runs import RunController
from projects.database import session_scope

bp = Blueprint("experiment_runs", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_runs(session, project_id, experiment_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    runs = run_controller.list_runs(project_id=project_id,
                                    experiment_id=experiment_id)
    return jsonify(runs)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_run(session, project_id, experiment_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run = run_controller.create_run(project_id=project_id,
                                    experiment_id=experiment_id)
    return jsonify(run)


@bp.route("<run_id>", methods=["GET"])
@session_scope
def handle_get_run(session, project_id, experiment_id, run_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run = run_controller.get_run(project_id=project_id,
                                 experiment_id=experiment_id,
                                 run_id=run_id)
    return jsonify(run)


@bp.route("<run_id>", methods=["DELETE"])
@session_scope
def handle_delete_run(session, project_id, experiment_id, run_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run = run_controller.terminate_run(project_id=project_id,
                                       experiment_id=experiment_id,
                                       run_id=run_id)
    return jsonify(run)


@bp.route("<run_id>/retry", methods=["POST"])
@session_scope
def handle_post_retry_run(session, project_id, experiment_id, run_id):
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
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run = run_controller.retry_run(project_id=project_id,
                                   experiment_id=experiment_id,
                                   run_id=run_id)
    return jsonify(run)
