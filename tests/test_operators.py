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
            f"INSERT INTO experiments (uuid, name, project_id, dataset, target, position, is_active, created_at, updated_at) "
            f"VALUES ('{EXPERIMENT_ID}', '{NAME}', '{PROJECT_ID}', '{DATASET}', '{TARGET}', '{POSITION}', 1, '{CREATED_AT}', '{UPDATED_AT}')"
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
            f"INSERT INTO operators (uuid, experiment_id, component_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID_3}', '{EXPERIMENT_ID}', '{COMPONENT_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO operators (uuid, experiment_id, component_id, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID_4}', '{EXPERIMENT_ID}', '{COMPONENT_ID}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
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
        text = f"DELETE FROM dependencies WHERE operator_id = '{OPERATOR_ID}' OR operator_id = '{OPERATOR_ID_4}'"
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
            expected = {"message": "componentId is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "componentId": "unk",
            })
            result = rv.get_json()
            expected = {"message": "The specified component does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "componentId": COMPONENT_ID,
                "parameters": [{"name": "coef", "value": 0.1}],
            })
            result = rv.get_json()
            expected = {"message": "The specified parameters are not valid"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "componentId": COMPONENT_ID,
                "parameters": {"coef": None},
            })
            result = rv.get_json()
            expected = {"message": "The specified parameters are not valid"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "componentId": COMPONENT_ID,
                "dependencies": "unk" #only lists are accepted
            })
            result = rv.get_json()
            expected = {"message": "The specified dependencies are not valid."}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "componentId": COMPONENT_ID,
                "dependencies": ["unk"]
            })
            result = rv.get_json()
            expected = {"message": "The specified dependencies are not valid."}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "componentId": COMPONENT_ID,
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "componentId": COMPONENT_ID,
                "dependencies": [],
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

            rv = c.post(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}/operators", json={
                "componentId": COMPONENT_ID,
                "parameters": {"coef": 1.0}
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "componentId": COMPONENT_ID,
                "dependencies": [],
                "parameters": {"coef": 1.0},
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
                "componentId": COMPONENT_ID,
                "dependencies": []
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "componentId": COMPONENT_ID,
                "dependencies": [],
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
                "componentId": COMPONENT_ID,
                "dependencies": [OPERATOR_ID_2],
                "parameters": PARAMETERS,
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
            })
            result = rv.get_json()
            expected = {
                "uuid": OPERATOR_ID,
                "experimentId": EXPERIMENT_ID,
                "componentId": COMPONENT_ID,
                "dependencies": [OPERATOR_ID_2],
                "parameters": {"coef": 0.2},
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
                "dependencies": [OPERATOR_ID_3],
                "parameters": {"coef": 0.2},
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
