# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase
from uuid import uuid4

from projects.api.main import app
from projects.database import engine
from projects.object_storage import BUCKET_NAME

EXPERIMENT_ID = str(uuid4())
NAME = "foo"
PROJECT_ID = str(uuid4())
TEMPLATE_ID = str(uuid4())
COMPONENT_ID = str(uuid4())
OPERATOR_ID = str(uuid4())
DATASET = "iris"
TARGET = "col4"
POSITION = 0
IS_ACTIVE = True
PARAMETERS = {"coef": 0.1}
PARAMETERS_JSON = dumps(PARAMETERS)
DESCRIPTION = "long foo"
TAGS = ["PREDICTOR"]
TAGS_JSON = dumps(TAGS)
COMPONENTS_JSON = dumps([COMPONENT_ID])
TRAINING_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/components/{COMPONENT_ID}/Training.ipynb"
INFERENCE_NOTEBOOK_PATH = f"minio://{BUCKET_NAME}/components/{COMPONENT_ID}/Inference.ipynb"
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
OPERATORS = [{"uuid": OPERATOR_ID, "componentId": COMPONENT_ID, "position": POSITION, "parameters": PARAMETERS, "experimentId": EXPERIMENT_ID, "createdAt": CREATED_AT_ISO, "updatedAt": UPDATED_AT_ISO}]


class TestExperiments(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO components (uuid, name, description, tags, training_notebook_path, inference_notebook_path, is_default, created_at, updated_at) "
            f"VALUES ('{COMPONENT_ID}', '{NAME}', '{DESCRIPTION}', '{TAGS_JSON}', '{TRAINING_NOTEBOOK_PATH}', '{INFERENCE_NOTEBOOK_PATH}', 0, '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

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
            f"INSERT INTO operators (uuid, experiment_id, component_id, position, parameters, created_at, updated_at) "
            f"VALUES ('{OPERATOR_ID}', '{EXPERIMENT_ID}', '{COMPONENT_ID}', '{POSITION}', '{PARAMETERS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        text = (
            f"INSERT INTO templates (uuid, name, components, created_at, updated_at) "
            f"VALUES ('{TEMPLATE_ID}', '{NAME}', '{COMPONENTS_JSON}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = f"DELETE FROM templates WHERE uuid = '{TEMPLATE_ID}'"
        conn.execute(text)

        text = f"DELETE FROM operators WHERE experiment_id = '{EXPERIMENT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        text = f"DELETE FROM components WHERE uuid = '{COMPONENT_ID}'"
        conn.execute(text)
        conn.close()

    def test_list_experiments(self):
        with app.test_client() as c:
            rv = c.get("/projects/unk/experiments")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_experiment(self):
        with app.test_client() as c:
            rv = c.post("/projects/unk/experiments", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post(f"/projects/{PROJECT_ID}/experiments", json={
                "name": "test",
                "dataset": DATASET,
                "target": TARGET,
            })
            result = rv.get_json()
            expected = {
                "name": "test",
                "projectId": PROJECT_ID,
                "dataset": DATASET,
                "target": TARGET,
                "position": 1,
                "isActive": IS_ACTIVE,
                "operators": [],
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_get_experiment(self):
        with app.test_client() as c:
            rv = c.get(f"/projects/foo/experiments/{EXPERIMENT_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/foo")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}")
            result = rv.get_json()
            expected = {
                "uuid": EXPERIMENT_ID,
                "name": NAME,
                "projectId": PROJECT_ID,
                "dataset": DATASET,
                "target": TARGET,
                "position": POSITION,
                "isActive": IS_ACTIVE,
                "operators": OPERATORS,
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_experiment(self):
        with app.test_client() as c:
            rv = c.patch(f"/projects/foo/experiments/{EXPERIMENT_ID}", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": EXPERIMENT_ID,
                "name": "bar",
                "projectId": PROJECT_ID,
                "dataset": DATASET,
                "target": TARGET,
                "position": POSITION,
                "isActive": IS_ACTIVE,
                "operators": OPERATORS,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "templateId": "unk",
            })
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}", json={
                "templateId": TEMPLATE_ID,
            })
            result = rv.get_json()
            expected = {
                "uuid": EXPERIMENT_ID,
                "name": "bar",
                "projectId": PROJECT_ID,
                "dataset": DATASET,
                "target": TARGET,
                "position": POSITION,
                "isActive": IS_ACTIVE,
                "createdAt": CREATED_AT_ISO,
            }
            result_operators = result["operators"]
            machine_generated = ["updatedAt", "operators"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)
            expected = [{
                "componentId": COMPONENT_ID,
                "experimentId": EXPERIMENT_ID,
                "position": POSITION,
                "parameters": {},
            }]
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                for operator in result_operators:
                    self.assertIn(attr, operator)
                    del operator[attr]
            self.assertListEqual(expected, result_operators)

    def test_delete_experiment(self):
        with app.test_client() as c:
            rv = c.delete(f"/projects/foo/experiments/{EXPERIMENT_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/unk")
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/experiments/{EXPERIMENT_ID}")
            result = rv.get_json()
            expected = {"message": "Experiment deleted"}
            self.assertDictEqual(expected, result)
