# -*- coding: utf-8 -*-
"""Projects API Router."""
import logging
from typing import List, Optional

from fastapi import APIRouter, Depends

import projects.schemas.project
from projects.controllers import ProjectController
from projects.database import Session, session_scope

router = APIRouter(
    prefix="/projects",
)


@router.get("", response_model=projects.schemas.project.ProjectList)
async def handle_list_projects(page: Optional[int] = 1,
                               page_size: Optional[int] = 10,
                               order: Optional[str] = None,
                               session: Session = Depends(session_scope)):
    """
    Handles GET requests to /.

    Parameters
    ----------
    page : int
    page_size : int
    order : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.project.ProjectList
    """
    project_controller = ProjectController(session)
    projects = project_controller.list_projects(page=page,
                                                page_size=page_size,
                                                order_by=order)
    return projects


@router.post("", response_model=projects.schemas.project.Project)
async def handle_post_projects(project: projects.schemas.project.ProjectCreate,
                               session: Session = Depends(session_scope)):
    """
    Handles POST requests to /.

    Parameters
    ----------
    project : projects.schemas.project.ProjectCreate
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.project.Project
    """
    project_controller = ProjectController(session)
    project = project_controller.create_project(project=project)
    return project


@router.get("/{project_id}", response_model=projects.schemas.project.Project)
async def handle_get_project(project_id: str,
                             session: Session = Depends(session_scope)):
    """
    Handles GET requests to /<project_id>.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.project.Project
    """
    logging.error(project_id)
    project_controller = ProjectController(session)
    project = project_controller.get_project(project_id=project_id)
    return project


@router.patch("/{project_id}", response_model=projects.schemas.project.Project)
async def handle_patch_project(project_id: str,
                               project: projects.schemas.project.ProjectUpdate,
                               session: Session = Depends(session_scope)):
    """
    Handles PATCH requests to /<project_id>.

    Parameters
    ----------
    project_id : str
    project : projects.schemas.project.ProjectUpdate
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.project.Project
    """
    project_controller = ProjectController(session)
    project = project_controller.update_project(project_id=project_id, project=project)
    return project


@router.delete("/{project_id}")
async def handle_delete_project(project_id: str,
                                session: Session = Depends(session_scope)):
    """
    Handles DELETE requests to /<project_id>.

    Parameters
    ----------
    project_id : str
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session)
    results = project_controller.delete_project(project_id=project_id)
    return results


@router.post("/deleteprojects")
async def handle_post_deleteprojects(projects: List[str],
                                     session: Session = Depends(session_scope)):
    """
    Handles POST requests to /deleteprojects.

    Parameters
    ----------
    projects : List[str]
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.message.Message
    """
    project_controller = ProjectController(session)
    results = project_controller.delete_multiple_projects(projects=projects)
    return results
