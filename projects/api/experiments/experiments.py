# -*- coding: utf-8 -*-
"""Experiments blueprint."""
from flask import Blueprint, jsonify, request

from projects.controllers import ExperimentController, ProjectController
from projects.database import session_scope
from projects.utils import to_snake_case

bp = Blueprint("experiments", __name__)


@bp.route("", methods=["GET"])
@session_scope
def handle_list_experiments(session, project_id):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiments = experiment_controller.list_experiments(project_id=project_id)
    return jsonify(experiments)


@bp.route("", methods=["POST"])
@session_scope
def handle_post_experiments(session, project_id):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str

    Returns
    -------
    str
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    experiment = experiment_controller.create_experiment(project_id=project_id, **kwargs)
    return jsonify(experiment)


@bp.route("<experiment_id>", methods=["GET"])
@session_scope
def handle_get_experiment(session, project_id, experiment_id):
    """
    Handles GET requests to /<experiment_id>.

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
    experiment = experiment_controller.get_experiment(experiment_id=experiment_id,
                                                      project_id=project_id)
    return jsonify(experiment)


@bp.route("<experiment_id>", methods=["PATCH"])
@session_scope
def handle_patch_experiment(session, project_id, experiment_id):
    """
    Handles PATCH requests to /<experiment_id>.

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
    kwargs = request.get_json(force=True)
    kwargs = {to_snake_case(k): v for k, v in kwargs.items()}
    experiment = experiment_controller.update_experiment(experiment_id=experiment_id,
                                                         project_id=project_id,
                                                         **kwargs)
    return jsonify(experiment)


@bp.route("<experiment_id>", methods=["DELETE"])
@session_scope
def handle_delete_experiment(session, project_id, experiment_id):
    """
    Handles DELETE requests to /<experiment_id>.

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
    experiment = experiment_controller.delete_experiment(experiment_id=experiment_id,
                                                         project_id=project_id)
    return jsonify(experiment)
