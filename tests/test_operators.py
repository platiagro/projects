# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME

TEST_CLIENT = TestClient(app)

OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
OPERATOR_ID_3 = str(uuid_alpha())
OPERATOR_ID_4 = str(uuid_alpha())
OPERATOR_ID_5 = str(uuid_alpha())
OPERATOR_ID_6 = str(uuid_alpha())
DEPENDENCY_ID = str(uuid_alpha())
DEPENDENCY_ID_2 = str(uuid_alpha())
NAME = "foo"
NAME_2 = "bar"
DESCRIPTION = "long foo"
PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
EXPERIMENT_ID_2 = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
PARAMETERS = {"coef": 0.1}
POSITION = 0
POSITION_2 = 1
POSITION_X = 0
POSITION_Y = 0
PARAMETERS = {}
IMAGE = "platiagro/platiagro-experiment-image:0.2.0"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
PARAMETERS_JSON = dumps(PARAMETERS)
PARAMETERS_2 = {"foo": "bar"}
PARAMETERS_JSON_2 = dumps(PARAMETERS_2)
EXPERIMENT_NOTEBOOK_PATH = "Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = "Deployment.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"

DEPENDENCIES_EMPTY = []
DEPENDENCIES_EMPTY_JSON = dumps(DEPENDENCIES_EMPTY)
DEPENDENCIES_OP_ID = [OPERATOR_ID]
DEPENDENCIES_OP_ID_JSON = dumps(DEPENDENCIES_OP_ID)
DEPENDENCIES_OP_ID_2 = [OPERATOR_ID_2]
DEPENDENCIES_OP_ID_2_JSON = dumps(DEPENDENCIES_OP_ID_2)

TASK_DATASET_ID = str(uuid_alpha())
TASK_DATASET_TAGS = ["DATASETS"]
TASK_DATASET_TAGS_JSON = dumps(TASK_DATASET_TAGS)


class TestOperators(TestCase):
    def setUp(self):
        self.maxDiff = None

        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, POSITION, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID_2, NAME_2, PROJECT_ID, POSITION_2, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_ID, NAME, DESCRIPTION, IMAGE, COMMANDS_JSON, ARGUMENTS_JSON, TAGS_JSON,
                            dumps([]), EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, parameters, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (TASK_DATASET_ID, NAME, DESCRIPTION, IMAGE, COMMANDS_JSON, ARGUMENTS_JSON, TASK_DATASET_TAGS_JSON,
                            dumps([]), EXPERIMENT_NOTEBOOK_PATH, DEPLOYMENT_NOTEBOOK_PATH, 0, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON, POSITION_X,
                            POSITION_Y, DEPENDENCIES_OP_ID_2_JSON, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_2, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON,
                            POSITION_X, POSITION_X, DEPENDENCIES_EMPTY_JSON, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_3, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON,
                            POSITION_X, POSITION_X, DEPENDENCIES_EMPTY_JSON, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_4, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON,
                            POSITION_X, POSITION_X, DEPENDENCIES_OP_ID_JSON, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_5, None, "Unset", None, EXPERIMENT_ID_2, TASK_ID, PARAMETERS_JSON,
                            POSITION_X, POSITION_X, DEPENDENCIES_EMPTY_JSON, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO operators (uuid, name, status, status_message, experiment_id, task_id, parameters, position_x, position_y, dependencies, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (OPERATOR_ID_6, None, "Unset", None, EXPERIMENT_ID, TASK_ID, PARAMETERS_JSON_2,
                            POSITION_X, POSITION_X, DEPENDENCIES_EMPTY_JSON, CREATED_AT, UPDATED_AT,))

        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = (
            f"DELETE FROM operators WHERE experiment_id in"
            f"(SELECT uuid  FROM experiments where project_id = '{PROJECT_ID}')"
        )
        conn.execute(text)

        text = (
            f"DELETE FROM operators WHERE experiment_id in"
            f"(SELECT uuid  FROM experiments where name = '{NAME}')"
        )
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid IN ('{TASK_ID}', '{TASK_DATASET_ID}')"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_operators(self):
        rv = TEST_CLIENT.get(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/unk/operators")
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators")
        result = rv.json()
        self.assertIsInstance(result["operators"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

    def test_create_operator(self):
        rv = TEST_CLIENT.post(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_ID,
            "positionX": 0,
            "positionY": 0,
        })
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/unk/operators", json={
            "taskId": TASK_ID,
            "positionX": 0,
            "positionY": 0,
        })
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={})
        result = rv.json()
        self.assertEqual(rv.status_code, 422)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": "unk",
            "positionX": 0,
            "positionY": 0,
        })
        result = rv.json()
        expected = {"message": "The specified task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_ID,
            "dependencies": "unk"  # only lists are accepted
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 422)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_ID,
            "dependencies": ["unk"]
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 422)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_ID,
            "dependencies": [OPERATOR_ID, OPERATOR_ID]
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 422)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_ID,
            "positionX": 0,
            "positionY": 0,
        })
        result = rv.json()
        expected = {
            "name": NAME,
            "experimentId": EXPERIMENT_ID,
            "taskId": TASK_ID,
            "task": {
                "name": NAME,
                "tags": TAGS,
            },
            "dependencies": [],
            "parameters": {},
            "positionX": 0,
            "positionY": 0,
            "status": "Unset",
            "statusMessage": None,
            "deploymentId": None
        }
        # uuid, created_at, updated_at are machine-generated
        # we assert they exist, but we don't assert their values
        machine_generated = ["uuid", "createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_ID,
            "positionX": 0,
            "positionY": 0,
            "parameters": {"coef": None},  # None is allowed!
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 200)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_ID,
            "positionX": 0,
            "positionY": 0,
            "parameters": {"coef": 1.0}
        })
        result = rv.json()
        expected = {
            "name": NAME,
            "experimentId": EXPERIMENT_ID,
            "taskId": TASK_ID,
            "task": {
                "name": NAME,
                "tags": TAGS,
            },
            "dependencies": [],
            "parameters": {"coef": 1.0},
            "positionX": 0,
            "positionY": 0,
            "status": "Unset",
            "statusMessage": None,
            "deploymentId": None
        }
        # uuid, created_at, updated_at are machine-generated
        # we assert they exist, but we don't assert their values
        machine_generated = ["uuid", "createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_ID,
            "positionX": 0,
            "positionY": 0,
            "dependencies": []
        })
        result = rv.json()
        expected = {
            "name": NAME,
            "experimentId": EXPERIMENT_ID,
            "taskId": TASK_ID,
            "task": {
                "name": NAME,
                "tags": TAGS,
            },
            "dependencies": [],
            "positionX": 0,
            "positionY": 0,
            "parameters": {},
            "status": "Unset",
            "statusMessage": None,
            "deploymentId": None
        }
        # uuid, created_at, updated_at are machine-generated
        # we assert they exist, but we don't assert their values
        machine_generated = ["uuid", "createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

        # Test operator status Unset with dataset task without params
        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_DATASET_ID,
            "positionX": 0,
            "positionY": 0,
        })
        result = rv.json()
        expected = {
            "name": NAME,
            "experimentId": EXPERIMENT_ID,
            "taskId": TASK_DATASET_ID,
            "task": {
                "name": NAME,
                "tags": ["DATASETS"],
            },
            "dependencies": [],
            "parameters": {},
            "positionX": 0,
            "positionY": 0,
            "status": "Unset",
            "statusMessage": None,
            "deploymentId": None
        }
        # uuid, created_at, updated_at are machine-generated
        # we assert they exist, but we don't assert their values
        machine_generated = ["uuid", "createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

        # Test operator status Setted up with dataset task with param
        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
            "taskId": TASK_DATASET_ID,
            "positionX": 0,
            "positionY": 0,
            "parameters": {"dataset": "iris.csv"}
        })
        result = rv.json()
        expected = {
            "name": NAME,
            "experimentId": EXPERIMENT_ID,
            "taskId": TASK_DATASET_ID,
            "task": {
                "name": NAME,
                "tags": ["DATASETS"],
            },
            "dependencies": [],
            "parameters": {"dataset": 'iris.csv'},
            "positionX": 0,
            "positionY": 0,
            "status": "Unset",
            "statusMessage": None,
            "deploymentId": None
        }
        # uuid, created_at, updated_at are machine-generated
        # we assert they exist, but we don't assert their values
        machine_generated = ["uuid", "createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

    def test_update_operator(self):
        rv = TEST_CLIENT.patch(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={})
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/unk/operators/{OPERATOR_ID}", json={})
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/foo", json={})
        result = rv.json()
        expected = {"message": "The specified operator does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
            "dependencies": [OPERATOR_ID],
        })
        result = rv.json()
        expected = {"message": "The specified dependencies are not valid."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
            "dependencies": [str(uuid_alpha())],
        })
        result = rv.json()
        expected = {"message": "The specified dependencies are not valid."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID_2}", json={
            "dependencies": [OPERATOR_ID],
        })
        result = rv.json()
        expected = {"message": "Cyclical dependencies."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={})
        result = rv.json()
        expected = {
            "uuid": OPERATOR_ID,
            "name": NAME,
            "experimentId": EXPERIMENT_ID,
            "taskId": TASK_ID,
            "task": {
                "name": NAME,
                "tags": TAGS,
            },
            "dependencies": result['dependencies'],
            "parameters": PARAMETERS,
            "positionX": POSITION_X,
            "positionY": POSITION_Y,
            "createdAt": CREATED_AT_ISO,
            "status": "Unset",
            "statusMessage": None,
            "deploymentId": None
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
            "parameters": {"coef": 0.2},
            "positionX": 100,
            "positionY": 200,
        })
        result = rv.json()
        expected = {
            "uuid": OPERATOR_ID,
            "name": NAME,
            "experimentId": EXPERIMENT_ID,
            "taskId": TASK_ID,
            "task": {
                "name": NAME,
                "tags": TAGS,
            },
            "dependencies": result['dependencies'],
            "parameters": {"coef": 0.2},
            "positionX": 100,
            "positionY": 200,
            "createdAt": CREATED_AT_ISO,
            "status": "Setted up",
            "statusMessage": None,
            "deploymentId": None
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
            "dependencies": [OPERATOR_ID_3],
        })
        result = rv.json()
        expected = {
            "uuid": OPERATOR_ID,
            "name": NAME,
            "experimentId": EXPERIMENT_ID,
            "taskId": TASK_ID,
            "task": {
                "name": NAME,
                "tags": TAGS,
            },
            "dependencies": [OPERATOR_ID_3],
            "parameters": {"coef": 0.2},
            "positionX": 100,
            "positionY": 200,
            "createdAt": CREATED_AT_ISO,
            "status": "Setted up",
            "statusMessage": None,
            "deploymentId": None
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
            "parameters": {"coef": None},
        })
        result = rv.json()
        self.assertEqual(rv.status_code, 200)  # None is allowed

    def test_delete_operator(self):
        rv = TEST_CLIENT.delete(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/experiments/unk/operators/{OPERATOR_ID}")
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/unk")
        result = rv.json()
        expected = {"message": "The specified operator does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}")
        result = rv.json()
        expected = {"message": "Operator deleted"}
        self.assertDictEqual(expected, result)

    def test_patch_parameter(self):
        rv = TEST_CLIENT.patch(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID_6}/parameters/foo", json={})
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/unk/operators/{OPERATOR_ID_6}/parameters/foo", json={})
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/unk/parameters/foo", json={})
        result = rv.json()
        expected = {"message": "The specified operator does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID_6}/parameters/foo",
                               json={"value": "foo"})
        result = rv.json()
        expected = {"foo": "foo"}
        self.assertDictEqual(expected, result["parameters"])
        self.assertEqual(rv.status_code, 200)
