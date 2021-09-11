# -*- coding: utf-8 -*-
"""Templates API Router."""
from typing import List, Optional

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

import projects.schemas.template
from projects import database
from projects.controllers import TemplateController

router = APIRouter(
    prefix="/templates",
)


@router.get("", response_model=projects.schemas.template.TemplateList)
async def handle_list_templates(
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles GET requests to /.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    projects.schemas.template.TemplateList
    """
    template_controller = TemplateController(session, kubeflow_userid=kubeflow_userid)
    templates = template_controller.list_templates()
    return templates


@router.post("", response_model=projects.schemas.template.Template)
async def handle_post_templates(
    template: projects.schemas.template.TemplateCreate,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles POST requests to /.

    Parameters
    ----------
    session : sqlalchemy.orm.session.Session
    template : projects.schemas.template.TemplateCreate
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.template.Template
    """
    template_controller = TemplateController(session, kubeflow_userid=kubeflow_userid)
    template = template_controller.create_template(template=template)
    return template


@router.get("/{template_id}", response_model=projects.schemas.template.Template)
async def handle_get_template(
    template_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles GET requests to /<template_id>.

    Parameters
    ----------
    template_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.template.Template
    """
    template_controller = TemplateController(session, kubeflow_userid=kubeflow_userid)
    template = template_controller.get_template(template_id=template_id)
    return template


@router.patch("/{template_id}", response_model=projects.schemas.template.Template)
async def handle_patch_template(
    template_id: str,
    template: projects.schemas.template.TemplateUpdate,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles PATCH requests to /<template_id>.

    Parameters
    ----------
    template_id : str
    template : projects.schemas.template.TemplateUpdate
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.template.Template
    """
    template_controller = TemplateController(session, kubeflow_userid=kubeflow_userid)
    template = template_controller.update_template(
        template_id=template_id, template=template
    )
    return template


@router.delete("/{template_id}")
async def handle_delete_template(
    template_id: str,
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles DELETE requests to /<template_id>.

    Parameters
    ----------
    template_id : str
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    template_controller = TemplateController(session, kubeflow_userid=kubeflow_userid)
    template = template_controller.delete_template(template_id=template_id)
    return template


@router.post("/deletetemplates")
async def handle_post_deletetemplates(
    templates: List[str],
    session: Session = Depends(database.session_scope),
    kubeflow_userid: Optional[str] = Header("anonymous"),
):
    """
    Handles POST requests to /deletetemplates.

    Parameters
    ----------
    templates : List[str]
    session : sqlalchemy.orm.session.Session
    kubeflow_userid : fastapi.Header

    Returns
    -------
    projects.schemas.message.Message
    """
    template_controller = TemplateController(session, kubeflow_userid=kubeflow_userid)
    results = template_controller.delete_multiple_templates(template_ids=templates)
    return results
