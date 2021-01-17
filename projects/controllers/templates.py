# -*- coding: utf-8 -*-
"""Templates controller."""
import re
from datetime import datetime

from projects import models, schemas
from projects.controllers.experiments import ExperimentController
from projects.controllers.utils import uuid_alpha
from projects.exceptions import BadRequest, NotFound

NOT_FOUND = NotFound("The specified template does not exist")


class TemplateController:
    def __init__(self, session):
        self.session = session
        self.experiment_controller = ExperimentController(session)

    def raise_if_template_does_not_exist(self, template_id: str):
        """
        Raises an exception if the specified template does not exist.

        Parameters
        ----------
        template_id :str

        Raises
        ------
        NotFound
        """
        exists = self.session.query(models.Template.uuid) \
            .filter_by(uuid=template_id) \
            .scalar() is not None

        if not exists:
            raise NOT_FOUND

    def list_templates(self):
        """
        Lists all templates from our database.

        Returns
        -------
        projects.schemas.template.TemplateList
        """
        templates = self.session.query(models.Template) \
            .all()
        # sort the list in place, using natural sort
        templates.sort(key=lambda o: [int(t) if t.isdigit() else t.lower() for t in re.split(r"(\d+)", o.name)])

        return schemas.TemplateList.from_model(templates, len(templates))

    def create_template(self, template: schemas.TemplateCreate):
        """
        Creates a new template in our database.

        Parameters
        ----------
        template : projects.schemas.template.TemplateCreate

        Returns
        -------
        projects.schemas.template.Template

        Raises
        ------
        BadRequest
            When the project attributes are invalid.
        """
        if not isinstance(template.name, str):
            raise BadRequest("name is required")

        if not isinstance(template.experiment_id, str):
            raise BadRequest("experimentId is required")

        try:
            self.experiment_controller.raise_if_experiment_does_not_exist(template.experiment_id)
        except NotFound as e:
            raise BadRequest(e.message)

        operators = self.session.query(models.Operator) \
            .filter_by(experiment_id=template.experiment_id) \
            .all()

        stored_template = self.session.query(models.Template) \
            .filter_by(name=template.name) \
            .first()
        if stored_template:
            raise BadRequest("a template with that name already exists")

        # order operators by dependencies
        operators_ordered = []
        while len(operators) != len(operators_ordered):
            for operator in operators:
                self.order_operators_by_dependencies(operators_ordered, operator)

        # JSON array order of elements are preserved, so there is no need to save positions
        tasks = []
        for uuid in operators_ordered:
            operator = next((op for op in operators if op.uuid == uuid), None)
            task = {
                "uuid": operator.uuid,
                "task_id": operator.task_id,
                "dependencies": operator.dependencies,
                "position_x": operator.position_x,
                "position_y": operator.position_y,
            }
            tasks.append(task)

        template = models.Template(uuid=uuid_alpha(), name=template.name, tasks=tasks)
        self.session.add(template)
        self.session.commit()
        self.session.refresh(template)

        return schemas.Template.from_model(template)

    def get_template(self, template_id: str):
        """
        Details a template from our database.

        Parameters
        ----------
        template_id : str

        Returns
        -------
        projects.schemas.template.Template

        Raises
        ------
        NotFound
            When template_id does not exist.
        """
        template = self.session.query(models.Template).get(template_id)

        if template is None:
            raise NOT_FOUND

        return schemas.Template.from_model(template)

    def update_template(self, template: schemas.TemplateUpdate, template_id: str):
        """
        Updates a template in our database.

        Parameters
        ----------
        template: projects.schemas.template.TemplateUpdate
        template_id : str

        Returns
        -------
        projects.schemas.template.Template

        Raises
        ------
        NotFound
            When template_id does not exist.
        """
        self.raise_if_template_does_not_exist(template_id)

        stored_template = self.session.query(models.Template) \
            .filter_by(name=template.name) \
            .first()
        if stored_template and stored_template.uuid != template_id:
            raise BadRequest("a template with that name already exists")

        update_data = template.dict(exclude_unset=True)
        update_data.update({"updated_at": datetime.utcnow()})

        self.session.query(models.Template).filter_by(uuid=template_id).update(update_data)
        self.session.commit()

        template = self.session.query(models.Template).get(template_id)

        return schemas.Template.from_model(template)

    def delete_template(self, template_id: str):
        """
        Delete a template in our database.

        Parameters
        ----------
        template_id : str

        Returns
        -------
        projects.schemas.message.Message

        Raises
        ------
        NotFound
            When template_id does not exist.
        """
        template = self.session.query(models.Template).get(template_id)

        if template is None:
            raise NOT_FOUND

        self.session.delete(template)

        return schemas.Message(message="Template deleted")

    def order_operators_by_dependencies(self, operators_ordered, operator):
        """
        Order operators by dependencies.

        Parameters
        ----------
        operators_ordered : list
        operator : dict
        """
        uuid = operator.uuid
        dependencies = operator.dependencies
        if uuid not in operators_ordered:
            if len(dependencies) == 0:
                operators_ordered.append(uuid)
            else:
                check = True
                for d in dependencies:
                    if d not in operators_ordered:
                        check = False
                if check:
                    operators_ordered.append(uuid)
