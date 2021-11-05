# -*- coding: utf-8 -*-
"""Healthcheck API Router."""

import sqlalchemy
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.exc import OperationalError

from projects import database
from projects.exceptions import ServiceUnavailable

router = APIRouter(
    prefix="/healthcheck",
)


@router.get("")
def handle_healthcheck(session: Session = Depends(database.session_scope)):
    """
    Handles GET request to /.

    Parameters
    -------
    session : sqlalchemy.orm.session.Session

    Returns
    -------
    str
    """
    try:
        session.query(sqlalchemy.false()).filter(sqlalchemy.false()).all()
    except OperationalError:
        raise ServiceUnavailable("Could not connect to database")
    return "Sucessfully connected to db"
