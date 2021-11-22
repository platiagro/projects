# -*- coding: utf-8 -*-
"""Projects API Router."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Header, Request
from sqlalchemy.orm import Session

import projects.schemas.project
from projects import database
from projects.controllers import ProjectController
from projects.utils import format_query_params

router = APIRouter(
    prefix="/projects",
)


@router.get("", response_model=projects.schemas.project.ProjectList)
async def handle_list_projects(
    request: Request,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles GET requests to /.

    Parameters
    ----------
    request : fastapi.Request
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.project.ProjectList
    """
    filters = format_query_params(str(request.query_params))

    order_by = filters.pop("order", None)

    page = filters.pop("page", 1)
    page = int(page) if page else 1

    page_size = filters.pop("page_size", None)
    page_size = int(page_size) if page_size else 10

    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    projects = project_controller.list_projects(
        page=page, page_size=page_size, order_by=order_by, **filters
    )
    return projects


@router.post("", response_model=projects.schemas.project.Project)
async def handle_post_projects(
    project: projects.schemas.project.ProjectCreate,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project : projects.schemas.project.ProjectCreate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.project.Project
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project = project_controller.create_project(project=project)
    return project


@router.get("/{project_id}", response_model=projects.schemas.project.Project)
async def handle_get_project(
    project_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles GET requests to /<project_id>.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.project.Project
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project = project_controller.get_project(project_id=project_id)
    return project


@router.patch("/{project_id}", response_model=projects.schemas.project.Project)
async def handle_patch_project(
    project_id: str,
    project: projects.schemas.project.ProjectUpdate,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles PATCH requests to /<project_id>.

    Parameters
    ----------
    project_id : str
    project : projects.schemas.project.ProjectUpdate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.project.Project
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    project = project_controller.update_project(project_id=project_id, project=project)
    return project


@router.delete("/{project_id}")
async def handle_delete_project(
    project_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles DELETE requests to /<project_id>.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    results = project_controller.delete_project(project_id=project_id)
    return results


@router.post("/deleteprojects")
async def handle_post_deleteprojects(
    projects: List[str],
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles POST requests to /deleteprojects.

    Parameters
    ----------
    projects : List[str]
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session, kubeflow_userid=kubeflow_userid)
    results = project_controller.delete_multiple_projects(project_ids=projects)
    return results
