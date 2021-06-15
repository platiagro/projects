# -*- coding: utf-8 -*-
"""Experiment Results API Router."""
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from projects.controllers import ExperimentController, ProjectController, \
    OperatorController, ResultController
from projects.controllers.experiments.runs import RunController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}",
)

@router.get("/results")
async def handle_get_results(project_id: str,
                             experiment_id: str,
                             run_id: str,
                             session: Session = Depends(session_scope)):
    """
    Handles GET requests to /results.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    starlette.responses.StreamingResponse
        ZipFile of the run results
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    run_controller = RunController(session)
    run_controller.raise_if_run_does_not_exist(run_id, experiment_id)

    result_controller = ResultController(session)
    results = result_controller.get_results(experiment_id=experiment_id,
                                            run_id=run_id)

    response = StreamingResponse(results, media_type="application/x-zip-compressed")
    response.headers["Content-Disposition"] = "attachment; filename=results.zip"
    return response


@router.get("/operators/{operator_id}/results")
async def handle_get_operator_results(project_id: str,
                                      experiment_id: str,
                                      run_id: str,
                                      operator_id: str,
                                      session: Session = Depends(session_scope)):
    """
    Handles GET requests to /operators/<operator_id>/results.

    Parameters
    ----------
    project_id : str
    experiment_id : str
    run_id: str
    operator_id: str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    starlette.responses.StreamingResponse]
        ZipFile of the operator_results
    """
    project_controller = ProjectController(session)
    project_controller.raise_if_project_does_not_exist(project_id)

    experiment_controller = ExperimentController(session)
    experiment_controller.raise_if_experiment_does_not_exist(experiment_id)

    operator_controller = OperatorController(session)
    operator_controller.raise_if_operator_does_not_exist(operator_id)

    run_controller = RunController(session)
    run_controller.raise_if_run_does_not_exist(run_id, experiment_id)

    result_controller = ResultController(session)
    results = result_controller.get_operator_results(experiment_id=experiment_id,
                                                     run_id=run_id,
                                                     operator_id=operator_id)

    response = StreamingResponse(results, media_type="application/x-zip-compressed")
    response.headers["Content-Disposition"] = "attachment; filename=results.zip"
    return response