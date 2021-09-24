# -*- coding: utf-8 -*-
"""Prediction schema."""


from pydantic import BaseModel


class Prediction(BaseModel):
    uuid: str
    deployment_id: str
    status: str
