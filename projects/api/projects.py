# -*- coding: utf-8 -*-
"""Projects API Router."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

import projects.schemas.project
from projects import database
from projects.controllers import ProjectController

router = APIRouter(
    prefix="/projects",
)


@router.post("/list-projects", response_model=projects.schemas.project.ProjectList)
async def handle_list_projects(
    request_schema: projects.schemas.project.ProjectListRequest,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header(database.DB_TENANT),
):
    """
    Handles POST requests to /list-projects.
    Parameters
    ----------
    request_schema : projects.schemas.project.ProjectListRequest
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header
    Returns
    -------
    projects.schemas.project.ProjectList
    """

    request_as_dict = request_schema.dict()

    filters = request_as_dict.get("filters")
    order_by = request_as_dict.get("order")
    page = request_as_dict.get("page")
    page_size = request_as_dict.get("page_size")

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
