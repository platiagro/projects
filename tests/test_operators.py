# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME

OPERATOR_ID = str(uuid_alpha())
OPERATOR_ID_2 = str(uuid_alpha())
OPERATOR_ID_3 = str(uuid_alpha())
OPERATOR_ID_4 = str(uuid_alpha())
DEPENDENCY_ID = str(uuid_alpha())
DEPENDENCY_ID_2 = str(uuid_alpha())
NAME = "foo"
DESCRIPTION = "long foo"
PROJECT_ID = str(uuid_alpha())
EXPERIMENT_ID = str(uuid_alpha())
TASK_ID = str(uuid_alpha())
PARAMETERS = {"coef": 0.1}
POSITION = 0
POSITION_X = 0.3
POSITION_Y = 0.5
PARAMETERS = {}
IMAGE = "platiagro/platiagro-notebook-image-test:0.1.0"
COMMANDS = ["CMD"]
COMMANDS_JSON = dumps(COMMANDS)
ARGUMENTS = ["ARG"]
ARGUMENTS_JSON = dumps(ARGUMENTS)
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
PARAMETERS_JSON = dumps(PARAMETERS)
EXPERIMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Experiment.ipynb"
DEPLOYMENT_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/tasks/{TASK_ID}/Deployment.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"

TASK_DATASET_ID = str(uuid_alpha())
TASK_DATASET_TAGS = ["DATASETS"]
TASK_DATASET_TAGS_JSON = dumps(TASK_DATASET_TAGS)


class TestOperators(TestCase):
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
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_ID}', '{NAME}', '{DESCRIPTION}', '{IMAGE}', '{COMMANDS_JSON}', '{ARGUMENTS_JSON}', '{TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO tasks (uuid, name, description, image, commands, arguments, tags, experiment_notebook_path, deployment_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{TASK_DATASET_ID}', '{NAME}', '{DESCRIPTION}', '{IMAGE}', '{COMMANDS_JSON}', '{ARGUMENTS_JSON}', '{TASK_DATASET_TAGS_JSON}', '{EXPERIMENT_NOTEBOOK_PATH}', '{DEPLOYMENT_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, position_x, position_y, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{POSITION_X}', "
            f"'{POSITION_Y}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, position_x, position_y, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID_2}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}', '{POSITION_X}',"
            f" '{POSITION_X}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, position_x, position_y, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID_3}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}',"
            f"'{POSITION_X}', '{POSITION_X}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, task_id, parameters, position_x, position_y, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID_4}', '{EXPERIMENT_ID}', '{TASK_ID}', '{PARAMETERS_JSON}',"
            f"'{POSITION_X}', '{POSITION_X}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO dependencies (uuid, operator_id, dependency) "
            f"VALUES ('{DEPENDENCY_ID}', '{OPERATOR_ID}', '{OPERATOR_ID_2}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO dependencies (uuid, operator_id, dependency) "
            f"VALUES ('{DEPENDENCY_ID_2}', '{OPERATOR_ID_4}', '{OPERATOR_ID}')"
        )
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM dependencies WHERE operator_id in" \
               f"(SELECT uuid  FROM operators where task_id = '{TASK_ID}')"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id in" \
               f"(SELECT uuid  FROM experiments where project_id = '{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id in" \
               f"(SELECT uuid  FROM experiments where name = '{NAME}')"
        conn.execute(text)

        text = f"DELETE FROM tasks WHERE uuid IN ('{TASK_ID}', '{TASK_DATASET_ID}')"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_operators(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/unk/operators")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_operator(self):
        with app.test_client() as c:
            rv = c.post(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/unk/operators", json={})
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={})
            result = rv.get_json()
            expected = {"message": "taskId is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": "unk",
            })
            result = rv.get_json()
            expected = {"message": "The specified task does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_ID,
                "parameters": [{"name": "coef", "value": 0.1}],
            })
            result = rv.get_json()
            expected = {"message": "The specified parameters are not valid"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_ID,
                "parameters": {"coef": None},
            })
            result = rv.get_json()
            expected = {"message": "The specified parameters are not valid"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_ID,
                "dependencies": "unk"  # only lists are accepted
            })
            result = rv.get_json()
            expected = {"message": "The specified dependencies are not valid."}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_ID,
                "dependencies": ["unk"]
            })
            result = rv.get_json()
            expected = {"message": "The specified dependencies are not valid."}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_ID,
                "positionX": 3.4,
                "positionY": 5.9,
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "taskId": TASK_ID,
                "dependencies": [],
                "parameters": {},
                "positionX": 3.4,
                "positionY": 5.9,
                "status": "Setted up",
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_ID,
                "parameters": {"coef": 1.0}
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "taskId": TASK_ID,
                "dependencies": [],
                "parameters": {"coef": 1.0},
                "positionX": None,
                "positionY": None,
                "status": "Unset",
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_ID,
                "dependencies": []
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "taskId": TASK_ID,
                "dependencies": [],
                "positionX": None,
                "positionY": None,
                "parameters": {},
                "status": "Setted up",
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            # Test operator status Unset with dataset task withou params
            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_DATASET_ID
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "taskId": TASK_DATASET_ID,
                "dependencies": [],
                "parameters": {},
                "positionX": None,
                "positionY": None,
                "status": "Unset",
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            # Test operator status Setted up with dataset task with param
            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "taskId": TASK_DATASET_ID,
                "parameters": {"dataset": 'iris.csv'}
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "taskId": TASK_DATASET_ID,
                "dependencies": [],
                "parameters": {"dataset": 'iris.csv'},
                "positionX": None,
                "positionY": None,
                "status": "Setted up",
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_update_operator(self):
        with app.test_client() as c:
            rv = c.patch(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/unk/operators/{OPERATOR_ID}", json={})
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified operator does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
                "parameters": [{"name": "coef", "value": 0.1}],
            })
            result = rv.get_json()
            expected = {"message": "The specified parameters are not valid"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
                "parameters": {"coef": None},
            })
            result = rv.get_json()
            expected = {"message": "The specified parameters are not valid"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
                "dependencies": [OPERATOR_ID],
            })
            result = rv.get_json()
            expected = {"message": "The specified dependencies are not valid."}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={})
            result = rv.get_json()
            expected = {
                "uuid": OPERATOR_ID,
                "experimentId": EXPERIMENT_ID,
                "taskId": TASK_ID,
                "dependencies": result['dependencies'],
                "parameters": PARAMETERS,
                "positionX": POSITION_X,
                "positionY": POSITION_Y,
                "createdAt": CREATED_AT_ISO,
                "status": "Setted up",
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
                "parameters": {"coef": 0.2},
                "positionX": 100,
                "positionY": 200,
            })
            result = rv.get_json()
            expected = {
                "uuid": OPERATOR_ID,
                "experimentId": EXPERIMENT_ID,
                "taskId": TASK_ID,
                "dependencies": result['dependencies'],
                "parameters": {"coef": 0.2},
                "positionX": 100.0,
                "positionY": 200.0,
                "createdAt": CREATED_AT_ISO,
                "status": "Unset",
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}", json={
                "dependencies": [OPERATOR_ID_3],
            })
            result = rv.get_json()
            expected = {
                "uuid": OPERATOR_ID,
                "experimentId": EXPERIMENT_ID,
                "componentId": COMPONENT_ID,
                "taskId": TASK_ID,
                "dependencies": [OPERATOR_ID_3],
                "parameters": {"coef": 0.2},
                "positionX": 100.0,
                "positionY": 200.0,
                "createdAt": CREATED_AT_ISO,
                "status": "Unset",
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_operator(self):
        with app.test_client() as c:
            rv = c.delete(f"/projects/unk/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/unk/operators/{OPERATOR_ID}")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/unk")
            result = rv.get_json()
            expected = {"message": "The specified operator does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators/{OPERATOR_ID}")
            result = rv.get_json()
            expected = {"message": "Operator deleted"}
            self.assertDictEqual(expected, result)
