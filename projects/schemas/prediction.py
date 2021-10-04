# -*- coding: utf-8 -*-
"""Prediction schema."""


from pydantic import BaseModel


class Prediction(BaseModel):
    uuid: str
    deployment_id: str
    status: str

    @classmethod
    def from_orm(cls, model):
        return Prediction(
            uuid=model.uuid, deployment_id=model.deployment_id, status=model.status
        )
