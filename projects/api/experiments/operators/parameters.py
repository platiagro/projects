# -*- coding: utf-8 -*-
"""Operators blueprint."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

import projects.schemas.operator
from projects.controllers import ExperimentController, OperatorController, \
    OperatorParameterController, ProjectController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}/parameters",
)


@router.patch("/{name}")
async def handle_patch_parameter(project_id: str,
                                 experiment_id: str,
                                 operator_id: str,
                                 name: str,
                                 parameter: projects.schemas.operator.ParameterUpdate,
                                 session: Session = Depends(session_scope),
                                 kubeflow_userid: Optional[str] = Header(None)):
    """
    Handles PATCH requests to /{name}.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    operator_id : str
    name : str
    parameter : projects.schemas.Operator.ParameterUpdate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    returns the updated value.
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator_controller.raise_if_operator_does_not_exist(operator_id)

    parameter_controller = OperatorParameterController(session)
    operator = parameter_controller.update_parameter(name=name,
                                                     operator_id=operator_id,
                                                     parameter=parameter)
    return operator
