# -*- coding: utf-8 -*-
"""Prediction schema."""


from pydantic import BaseModel


class PredictionBase(BaseModel):
    uuid: str
    deployment_id: str
    status: str

    @classmethod
    def from_orm(cls, model):
        return PredictionBase(
            uuid=model.uuid, deployment_id=model.deployment_id, status=model.status
        )


class Prediction(PredictionBase):
    request_body: str
    response_body: str
    created_at: str
    updated_at: str

    @classmethod
    def from_orm(cls, model):
        return Prediction(
            uuid=model.uuid,
            deployment_id=model.deployment_id,
            request_body=model.request_body,
            response_body=model.response_body,
            status=model.status,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
