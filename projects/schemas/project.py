# -*- coding: utf-8 -*-
"""Project schema."""
import re
from datetime import datetime
from typing import List, Optional, Literal

from pydantic import BaseModel, validator
from projects.exceptions import BadRequest, NotFound

from projects.schemas.deployment import Deployment
from projects.schemas.experiment import Experiment
from projects.utils import to_camel_case

FORBIDDEN_CHARACTERS_REGEX = "[!*'():;@&=+$,\/?%#\[\]]"
MAX_CHARS_ALLOWED = 50


class ProjectBase(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True


class ProjectCreate(ProjectBase):
    name: str
    description: Optional[str]


class ProjectUpdate(ProjectBase):
    name: Optional[str]
    description: Optional[str]


class Project(ProjectBase):
    uuid: str
    name: str
    description: Optional[str]
    experiments: List[Experiment]
    deployments: List[Deployment]
    has_experiment: bool
    has_deployment: bool
    has_pre_deployment: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_orm(cls, model):
        return Project(
            uuid=model.uuid,
            name=model.name,
            description=model.description,
            experiments=model.experiments,
            deployments=model.deployments,
            has_experiment=model.has_experiment,
            has_deployment=model.has_deployment,
            has_pre_deployment=model.has_pre_deployment,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )


class ProjectList(BaseModel):
    projects: List[Project]
    total: int

    @classmethod
    def from_orm(cls, models, total):
        return ProjectList(
            projects=[Project.from_orm(model) for model in models],
            total=total,
        )


class ProjectListRequest(BaseModel):
    filters: Optional[dict] = {}
    page: Optional[int] = 1
    page_size: Optional[int] = 10
    order: Optional[str]

    @validator("filters")
    def name_has_forbidden_character(cls, v):
        """
        Identifies if string has forbidden character based in some regex

        Parameters
        ----------
        string: str

        forbidden_special_character_regex : str
            string symbolizing a regex pattern to identify the forbidden regex

        Returns
        -------
        bool
        """
        if v.get("name") and re.findall(FORBIDDEN_CHARACTERS_REGEX, v.get("name")):
            raise BadRequest(
                code="NotAllowedChar",
                message="Not allowed char in search field",
            )
        return v

    @validator("filters")
    def name_exceeded_max_amount_chars(cls, v):
        """
        Identifies if string has more character than maximum characters allowed

        Parameters
        ----------
        string: str

        max_chars_allowed: str
            string symbolizing a regex pattern to identify the forbidden regex


        Returns
        -------
        bool
        """

        if v.get("name") and len(v.get("name")) > MAX_CHARS_ALLOWED:
            raise BadRequest(
                code="Exceeded",
                message="Char quantity exceeded maximum allowed",
            )
        return v

    # This is necessary to mysql consider special character
    # maybe this logic won't work on another database
    # maybe we can refactor this!
    @validator("filters")
    def escaped_format(cls, v):
        """
        This function will escape string so mysql database be able to read special characters.

        Parameters
        ----------
        string : str
        Returns
        -------
        str
        """
        escaped_string = ""
        # to avoid the trouble of identify every special character we gonna escape all!
        if v.get("name"):
            for character in v.get("name"):
                if character.isalnum():
                    escaped_string = escaped_string + character
                else:
                    escaped_string = escaped_string + "\\" + character
                v["name"] = escaped_string
        return v
