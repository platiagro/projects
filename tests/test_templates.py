# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase
from uuid import uuid4

from projects.api.main import app
from projects.database import engine
from projects.object_storage import BUCKET_NAME

TEMPLATE_ID = str(uuid4())
NAME = "foo"
COMPONENT_ID = str(uuid4())
PROJECT_ID = str(uuid4())
EXPERIMENT_ID = str(uuid4())
OPERATOR_ID = str(uuid4())
DATASET = "iris"
TARGET = "col4"
POSITION = 0
OPERATORS = [{"componentId": COMPONENT_ID, "position": POSITION}]
DESCRIPTION = "long foo"
TAGS = ["PREDICTOR"]
TRAINING_NOTEBOOK_PATH = "minio://{}/components/{}/Training.ipynb".format(BUCKET_NAME, COMPONENT_ID)
INFERENCE_NOTEBOOK_PATH = "minio://{}/components/{}/Inference.ipynb".format(BUCKET_NAME, COMPONENT_ID)
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestTemplates(TestCase):
    def setUp(self):
        conn = engine.connect()
        text = "INSERT INTO components (uuid, name, description, tags, training_notebook_path, inference_notebook_path, is_default, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(COMPONENT_ID, NAME, DESCRIPTION, dumps(TAGS), TRAINING_NOTEBOOK_PATH, INFERENCE_NOTEBOOK_PATH, 0, CREATED_AT, UPDATED_AT)
        conn.execute(text)

        text = "INSERT INTO projects (uuid, name, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}')".format(PROJECT_ID, NAME, CREATED_AT, UPDATED_AT)
        conn.execute(text)

        text = "INSERT INTO experiments (uuid, name, project_id, dataset, target, position, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(EXPERIMENT_ID, NAME, PROJECT_ID, DATASET, TARGET, POSITION, CREATED_AT, UPDATED_AT)
        conn.execute(text)

        text = "INSERT INTO operators (uuid, experiment_id, component_id, position, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}')".format(OPERATOR_ID, EXPERIMENT_ID, COMPONENT_ID, POSITION, CREATED_AT, UPDATED_AT)
        conn.execute(text)

        text = "INSERT INTO templates (uuid, name, components, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}')".format(TEMPLATE_ID, NAME, dumps([COMPONENT_ID]), CREATED_AT, UPDATED_AT)
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = "DELETE FROM templates WHERE uuid = '{}'".format(TEMPLATE_ID)
        conn.execute(text)

        text = "DELETE FROM operators WHERE experiment_id = '{}'".format(EXPERIMENT_ID)
        conn.execute(text)

        text = "DELETE FROM experiments WHERE project_id = '{}'".format(PROJECT_ID)
        conn.execute(text)

        text = "DELETE FROM projects WHERE uuid = '{}'".format(PROJECT_ID)
        conn.execute(text)

        text = "DELETE FROM components WHERE uuid = '{}'".format(COMPONENT_ID)
        conn.execute(text)
        conn.close()

    def test_list_templates(self):
        with app.test_client() as c:
            rv = c.get("/templates")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_template(self):
        with app.test_client() as c:
            rv = c.post("/templates", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
            })
            result = rv.get_json()
            expected = {"message": "experimentId is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
                "experimentId": "UNK",
            })
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/templates", json={
                "name": "foo",
                "experimentId": EXPERIMENT_ID,
            })
            result = rv.get_json()
            expected = {
                "name": "foo",
                "operators": OPERATORS,
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_get_template(self):
        with app.test_client() as c:
            rv = c.get("/templates/foo")
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get("/templates/{}".format(TEMPLATE_ID))
            result = rv.get_json()
            expected = {
                "uuid": TEMPLATE_ID,
                "name": NAME,
                "operators": OPERATORS,
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_template(self):
        with app.test_client() as c:
            rv = c.patch("/templates/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch("/templates/{}".format(TEMPLATE_ID), json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch("/templates/{}".format(TEMPLATE_ID), json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": TEMPLATE_ID,
                "name": "bar",
                "operators": OPERATORS,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_template(self):
        with app.test_client() as c:
            rv = c.delete("/templates/unk")
            result = rv.get_json()
            expected = {"message": "The specified template does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete("/templates/{}".format(TEMPLATE_ID))
            result = rv.get_json()
            expected = {"message": "Template deleted"}
            self.assertDictEqual(expected, result)
