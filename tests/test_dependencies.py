# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

import pytest
from werkzeug.exceptions import NotFound

from projects.controllers.dependencies import list_dependencies, list_next_operators, \
    create_dependency, delete_dependency
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME

DEPENDENCY_ID = str(uuid_alpha())
OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
NAME = "foo"
DESCRIPTION = "long foo"
PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
COMPONENT_ID = str(uuid_alpha())
PARAMETERS = {"coef": 0.1}
DATASET = "iris"
TARGET = "col4"
POSITION = 0
PARAMETERS = {}
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
PARAMETERS_JSON = dumps(PARAMETERS)
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/components/{COMPONENT_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/components/{COMPONENT_ID}/Deployment.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestDependencies(TestCase):
    def setUp(self):
        self.maxDiff = None

        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES ('{PROJECT_ID}', '{NAME}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES ('{EXPERIMENT_ID}', '{NAME}', '{PROJECT_ID}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO components (uuid, name, description, commands, tags, experiment_notebook_path, deployment_notebook_path, created_at, updated_at) "
            f"VALUES ('{COMPONENT_ID}', '{NAME}', '{DESCRIPTION}', '{COMMANDS_JSON}', '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, component_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{COMPONENT_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, component_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID_2}', '{EXPERIMENT_ID}', '{COMPONENT_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO dependencies (uuid, operator_id, dependency) "
            f"VALUES ('{DEPENDENCY_ID}', '{OPERATOR_ID}', '{OPERATOR_ID_2}')"
        )
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM dependencies WHERE operator_id = '{OPERATOR_ID}'"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM components WHERE uuid = '{COMPONENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_dependencies(self):
        result = list_dependencies(OPERATOR_ID)
        expected = [
            {
                "uuid": DEPENDENCY_ID,
                "operatorId": OPERATOR_ID,
                "dependency": OPERATOR_ID_2
            }
        ]
        self.assertListEqual(expected, result)

    def test_list_next_operators(self):
        result = list_next_operators(OPERATOR_ID_2)
        expected = [OPERATOR_ID]
        self.assertListEqual(expected, result)

    def test_create_dependency(self):
        result = create_dependency(OPERATOR_ID, OPERATOR_ID_2)
        expected = {
            "operatorId": OPERATOR_ID,
            "dependency": OPERATOR_ID_2
        }

        # uuid are machine-generated
        # we assert it exist, but we don't assert your values
        machine_generated = ["uuid"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

    def test_delete_dependency(self):
        with pytest.raises(NotFound) as e:
            assert delete_dependency("unk")
        assert str(e.value) == "404 Not Found: The specified dependency does not exist"

        result = delete_dependency(DEPENDENCY_ID)
        expected = {"message": "Dependency deleted"}
        self.assertDictEqual(expected, result)
