# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.database import engine
from projects.object_storage import BUCKET_NAME
from uuid import uuid4

OPERATOR_ID = str(uuid4())
NAME = "foo"
DESCRIPTION = "long foo"
PROJECT_ID = str(uuid4())
EXPERIMENT_ID = str(uuid4())
COMPONENT_ID = str(uuid4())
DATASET = "iris"
TARGET = "col4"
POSITION = 0
TAGS = ["PREDICTOR"]
TRAINING_NOTEBOOK_PATH = "minio://{}/components/{}/Training.ipynb".format(BUCKET_NAME, COMPONENT_ID)
INFERENCE_NOTEBOOK_PATH = "minio://{}/components/{}/Inference.ipynb".format(BUCKET_NAME, COMPONENT_ID)
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestOperators(TestCase):
    def setUp(self):
        conn = engine.connect()
        text = "INSERT INTO projects (uuid, name, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}')".format(PROJECT_ID, NAME, CREATED_AT, UPDATED_AT)
        conn.execute(text)

        text = "INSERT INTO experiments (uuid, name, project_id, dataset, target, position, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(EXPERIMENT_ID, NAME, PROJECT_ID, DATASET, TARGET, POSITION, CREATED_AT, UPDATED_AT)
        conn.execute(text)

        text = "INSERT INTO components (uuid, name, description, tags, training_notebook_path, inference_notebook_path, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(COMPONENT_ID, NAME, DESCRIPTION, dumps(TAGS), TRAINING_NOTEBOOK_PATH, INFERENCE_NOTEBOOK_PATH, CREATED_AT, UPDATED_AT)
        conn.execute(text)

        text = "INSERT INTO operators (uuid, experiment_id, component_id, position, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(OPERATOR_ID, EXPERIMENT_ID, COMPONENT_ID, POSITION, CREATED_AT, UPDATED_AT)
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = "DELETE FROM operators WHERE experiment_id = '{}'".format(EXPERIMENT_ID)
        conn.execute(text)

        text = "DELETE FROM components WHERE uuid = '{}'".format(COMPONENT_ID)
        conn.execute(text)

        text = "DELETE FROM experiments WHERE project_id = '{}'".format(PROJECT_ID)
        conn.execute(text)

        text = "DELETE FROM projects WHERE uuid = '{}'".format(PROJECT_ID)
        conn.execute(text)
        conn.close()

    def test_list_operators(self):
        with app.test_client() as c:
            rv = c.get("/projects/unk/experiments/{}/operators".format(EXPERIMENT_ID))
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get("/projects/{}/experiments/unk/operators".format(PROJECT_ID))
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get("/projects/{}/experiments/{}/operators".format(PROJECT_ID, EXPERIMENT_ID))
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_operator(self):
        with app.test_client() as c:
            rv = c.post("/projects/unk/experiments/{}/operators".format(EXPERIMENT_ID), json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post("/projects/{}/experiments/unk/operators".format(PROJECT_ID), json={})
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post("/projects/{}/experiments/{}/operators".format(PROJECT_ID, EXPERIMENT_ID), json={})
            result = rv.get_json()
            expected = {"message": "componentId is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/projects/{}/experiments/{}/operators".format(PROJECT_ID, EXPERIMENT_ID), json={
                "componentId": COMPONENT_ID,
            })
            result = rv.get_json()
            expected = {
                "experimentId": EXPERIMENT_ID,
                "componentId": COMPONENT_ID,
                "position": 1,
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
            rv = c.patch("/projects/unk/experiments/{}/operators/{}".format(EXPERIMENT_ID, OPERATOR_ID), json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch("/projects/{}/experiments/unk/operators/{}".format(PROJECT_ID, OPERATOR_ID), json={})
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch("/projects/{}/experiments/{}/operators/foo".format(PROJECT_ID, EXPERIMENT_ID), json={})
            result = rv.get_json()
            expected = {"message": "The specified operator does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch("/projects/{}/experiments/{}/operators/{}".format(PROJECT_ID, EXPERIMENT_ID, OPERATOR_ID), json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch("/projects/{}/experiments/{}/operators/{}".format(PROJECT_ID, EXPERIMENT_ID, OPERATOR_ID), json={
                "position": 0,
            })
            result = rv.get_json()
            expected = {
                "uuid": OPERATOR_ID,
                "experimentId": EXPERIMENT_ID,
                "componentId": COMPONENT_ID,
                "position": 0,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_operator(self):
        with app.test_client() as c:
            rv = c.delete("/projects/unk/experiments/{}/operators/{}".format(EXPERIMENT_ID, OPERATOR_ID))
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete("/projects/{}/experiments/unk/operators/{}".format(PROJECT_ID, OPERATOR_ID))
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete("/projects/{}/experiments/{}/operators/unk".format(PROJECT_ID, EXPERIMENT_ID))
            result = rv.get_json()
            expected = {"message": "The specified operator does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete("/projects/{}/experiments/{}/operators/{}".format(PROJECT_ID, EXPERIMENT_ID, OPERATOR_ID))
            result = rv.get_json()
            expected = {"message": "Operator deleted"}
            self.assertDictEqual(expected, result)
