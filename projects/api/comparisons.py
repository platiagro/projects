# -*- coding: utf-8 -*-
"""Comparisons API Router."""
from typing import Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

import projects.schemas.comparison
from projects.controllers import ComparisonController, ProjectController
from projects.database import session_scope

router = APIRouter(
    prefix="/projects/{project_id}/comparisons",
)


@router.get("", response_model=projects.schemas.comparison.ComparisonList)
async def handle_list_comparisons(project_id: str,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles GET requests to /.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.comparison.ComparisonList
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    comparison_controller = ComparisonController(session)
    comparisons = comparison_controller.list_comparisons(project_id=project_id)
    return comparisons


@router.post("", response_model=projects.schemas.comparison.Comparison)
async def handle_post_comparisons(project_id: str,
                                  session: Session = Depends(session_scope),
                                  kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.comparison.Comparison
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    comparison_controller = ComparisonController(session)
    comparison = comparison_controller.create_comparison(project_id=project_id)
    return comparison


@router.patch("/{comparison_id}", response_model=projects.schemas.comparison.Comparison)
async def handle_patch_comparisons(project_id: str,
                                   comparison_id: str,
                                   comparison: projects.schemas.comparison.ComparisonUpdate,
                                   session: Session = Depends(session_scope),
                                   kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles PATCH requests to /<comparison_id>.

    Parameters
    ----------
    project_id : str
    comparison_id : str
    comparison : projects.schemas.comparison.ComparisonUpdate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.comparison.Comparison
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    comparison_controller = ComparisonController(session)
    comparison = comparison_controller.update_comparison(
        comparison_id=comparison_id,
        project_id=project_id,
        comparison=comparison,
    )
    return comparison


@router.delete("/{comparison_id}")
async def handle_delete_comparisons(project_id: str,
                                    comparison_id: str,
                                    session: Session = Depends(session_scope),
                                    kubeflow_userid: Optional[str] = Header("anonymous")):
    """
    Handles DELETE requests to /<comparison_id>.

    Parameters
    ----------
    project_id : str
    comparison_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project_controller.raise_if_project_does_not_exist(project_id)

    comparison_controller = ComparisonController(session)
    comparison = comparison_controller.delete_comparison(
        comparison_id=comparison_id,
        project_id=project_id,
    )
    return comparison
