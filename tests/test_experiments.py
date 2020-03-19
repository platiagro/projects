# -*- coding: utf-8 -*-
from unittest import TestCase

from projects.api.main import app
from projects.database import engine

UUID = "2b42d7b7-3a32-4678-b59e-91b2ad9e1fcf"
NAME = "foo"
PROJECT_ID = "84af0bb0-345f-449b-b586-0dfe40aacd4e"
DATASET = "iris"
TARGET = "col4"
POSITION = 0
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestExperiments(TestCase):
    def setUp(self):
        conn = engine.connect()
        text = "INSERT INTO projects (uuid, name, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}')".format(PROJECT_ID, NAME, CREATED_AT, UPDATED_AT)
        conn.execute(text)

        text = "INSERT INTO experiments (uuid, name, project_id, dataset, target, position, created_at, updated_at) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}')".format(UUID, NAME, PROJECT_ID, DATASET, TARGET, POSITION, CREATED_AT, UPDATED_AT)
        conn.execute(text)
        conn.close()

    def tearDown(self):
        conn = engine.connect()
        text = "DELETE FROM experiments WHERE project_id = '{}'".format(PROJECT_ID)
        conn.execute(text)

        text = "DELETE FROM projects WHERE uuid = '{}'".format(PROJECT_ID)
        conn.execute(text)
        conn.close()

    def test_list_experiments(self):
        with app.test_client() as c:
            rv = c.get("/projects/{}/experiments".format(PROJECT_ID))
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_experiment(self):
        with app.test_client() as c:
            rv = c.post("/projects/{}/experiments".format(PROJECT_ID), json={})
            result = rv.get_json()
            expected = {"message": "name is required"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 400)

            rv = c.post("/projects/{}/experiments".format(PROJECT_ID), json={
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
            rv = c.get("/projects/{}/experiments/foo".format(PROJECT_ID))
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get("/projects/{}/experiments/{}".format(PROJECT_ID, UUID))
            result = rv.get_json()
            expected = {
                "uuid": UUID,
                "name": NAME,
                "projectId": PROJECT_ID,
                "dataset": DATASET,
                "target": TARGET,
                "position": POSITION,
                "operators": [],
                "createdAt": CREATED_AT_ISO,
                "updatedAt": UPDATED_AT_ISO,
            }
            self.assertDictEqual(expected, result)

    def test_update_experiment(self):
        with app.test_client() as c:
            rv = c.patch("/projects/{}/experiments/foo".format(PROJECT_ID), json={})
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch("/projects/{}/experiments/{}".format(PROJECT_ID, UUID), json={
                "unk": "bar",
            })
            result = rv.get_json()
            self.assertEqual(rv.status_code, 400)

            rv = c.patch("/projects/{}/experiments/{}".format(PROJECT_ID, UUID), json={
                "name": "bar",
            })
            result = rv.get_json()
            expected = {
                "uuid": UUID,
                "name": "bar",
                "projectId": PROJECT_ID,
                "dataset": DATASET,
                "target": TARGET,
                "position": POSITION,
                "operators": [],
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_delete_experiment(self):
        with app.test_client() as c:
            rv = c.delete("/projects/{}/experiments/unk".format(PROJECT_ID))
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete("/projects/{}/experiments/{}".format(PROJECT_ID, UUID))
            result = rv.get_json()
            expected = {"message": "Experiment deleted"}
            self.assertDictEqual(expected, result)
