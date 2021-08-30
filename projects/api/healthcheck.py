# -*- coding: utf-8 -*-
"""Healthcheck API Router."""

import sqlalchemy
from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy.exc import OperationalError

from projects.exceptions import ServiceUnavailable
from projects.database import session_scope

router = APIRouter(
    prefix="/healthcheck",
)


@router.get("")
def handle_healthcheck(session: Session = Depends(session_scope)):
    try:
        session.query(sqlalchemy.false()).filter(sqlalchemy.false()).all()
    except OperationalError:
        raise ServiceUnavailable("Could not connect to database")
    return "Sucessfully connected to db"