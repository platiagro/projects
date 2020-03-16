# -*- coding: utf-8 -*-
import unittest

from projects.api.main import app
from projects.database import engine

UUID = "6814cdae-d88d-4c4d-bfb6-9ea6d6086dc4"
NAME = "foo"
DESCRIPTION = "long foo"
TRAINING_NOTEBOOK_PATH = "minio://anonymous/components/{}/Training.ipynb".format(UUID)
INFERENCE_NOTEBOOK_PATH = "minio://anonymous/components/{}/Inference.ipynb".format(UUID)
IS_DEFAULT = False
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestComponents(unittest.TestCase):
    def setUp(self):
        conn = engine.connect()
        text = "INSERT INTO components (uuid, name, description, training_notebook_path, inference_notebook_path, is_default, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(UUID, NAME, DESCRIPTION, TRAINING_NOTEBOOK_PATH, INFERENCE_NOTEBOOK_PATH, 0, CREATED_AT, UPDATED_AT)
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = "DELETE FROM components WHERE uuid = '{}'".format(UUID)
        conn.execute(text)
        conn.close()

    def test_list_components(self):
        with app.test_client() as c:
            rv = c.get("/components")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_component(self):
        with app.test_client() as c:
            rv = c.post("/components", json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/components", json={
                "name": "test",
                "description": "long test",
            })
            result = rv.get_json()
            expected = {
                "name": "test",
                "description": "long test",
                "isDefault": IS_DEFAULT,
            }
            # uuid, training_notebook_path, inference_notebook_path, created_at, updated_at
            # are machine-generated we assert they exist, but we don't assert their values
            machine_generated = [
                "uuid",
                "trainingNotebookPath",
                "inferenceNotebookPath",
                "createdAt",
                "updatedAt",
            ]
            test_uuid = result["uuid"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

            rv = c.post("/components", json={
                "name": "test",
                "description": "long test",
                "copyFrom": test_uuid,
            })
            result = rv.get_json()
            expected = {
                "name": "test",
                "description": "long test",
                "isDefault": IS_DEFAULT,
            }
            machine_generated = [
                "uuid",
                "trainingNotebookPath",
                "inferenceNotebookPath",
                "createdAt",
                "updatedAt",
            ]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_get_component(self):
        with app.test_client() as c:
            rv = c.get("/components/foo")
            result = rv.get_json()
            expected = {"message": "The specified component does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get("/components/{}".format(UUID))
            result = rv.get_json()
            expected = {
                "uuid": UUID,
                "name": "foo",
                "description": DESCRIPTION,
                "trainingNotebookPath": TRAINING_NOTEBOOK_PATH,
                "inferenceNotebookPath": INFERENCE_NOTEBOOK_PATH,
                "isDefault": IS_DEFAULT,
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_component(self):
        with app.test_client() as c:
            rv = c.patch("/components/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified component does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch("/components/{}".format(UUID), json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch("/components/{}".format(UUID), json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": UUID,
                "name": "bar",
                "description": DESCRIPTION,
                "trainingNotebookPath": TRAINING_NOTEBOOK_PATH,
                "inferenceNotebookPath": INFERENCE_NOTEBOOK_PATH,
                "isDefault": IS_DEFAULT,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)