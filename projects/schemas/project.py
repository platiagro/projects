# -*- coding: utf-8 -*-
"""Project schema."""
import re
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, validator
from projects.exceptions import BadRequest

from projects.schemas.deployment import Deployment
from projects.schemas.experiment import Experiment
from projects.utils import to_camel_case

FORBIDDEN_CHARACTERS_REGEX = "[!*'():;@&=+$,\/?%#\[\]]"
MAX_CHARS_ALLOWED = 50

def raise_if_exceeded(max_chars_allowed, value):
    if len(value) > max_chars_allowed:
        raise BadRequest(
            code="ExceededACharAmount",
            message="Char quantity exceeded maximum allowed",
            )
   
def raise_if_forbidden_character(forbidden_char_regex, value):
        if re.findall(forbidden_char_regex, value):
            raise BadRequest(
                code="NotAllowedChar",
                message="Not allowed char in search field",
            )

# This is necessary to mysql consider special character
# maybe this logic won't work on another database
# maybe we can refactor this!            
def escaped_format(value):
        """
        This function will escape string so mysql database be able to read special characters.

        Parameters
        ----------
        value: str
        Returns
        -------
        str
            string escaped
        """
        escaped_string = ""
        # to avoid the trouble of identify every special character we gonna escape all!
        for character in value:
            if character.isalnum():
                escaped_string = escaped_string + character
            else:
                escaped_string = escaped_string + "\\" + character
        return escaped_string            

class ProjectBase(BaseModel):
    class Config:
        alias_generator = to_camel_case
        allow_population_by_field_name = True
        orm_mode = True

#Request
class ProjectCreate(ProjectBase):
    name: str
    description: Optional[str]
    
    @validator("name")
    def validate_name(cls, v):
        raise_if_exceeded(MAX_CHARS_ALLOWED,v)
        raise_if_forbidden_character(FORBIDDEN_CHARACTERS_REGEX,v)
        return v
        
#Request
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
    def validate_name_in_filters(cls, v):
        if v.get("name"):
            name = v.get("name")
            raise_if_exceeded(MAX_CHARS_ALLOWED, name)
            raise_if_forbidden_character(FORBIDDEN_CHARACTERS_REGEX, name)
            v['name'] = escaped_format(name)
        return v
