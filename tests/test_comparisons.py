# -*- coding: utf-8 -*-
from unittest import TestCase

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine

TEST_CLIENT = TestClient(app)

EXPERIMENT_ID = str(uuid_alpha())
PROJECT_ID = str(uuid_alpha())
COMPARISON_ID = str(uuid_alpha())
NAME = "foo"
POSITION = 0
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"
TENANT = None


class TestComparisons(TestCase):
    def setUp(self):
        self.maxDiff = None
        conn = engine.connect()
        text = (
            f"INSERT INTO projects (uuid, name, created_at, updated_at, tenant) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (PROJECT_ID, NAME, CREATED_AT, UPDATED_AT, TENANT,))

        text = (
            f"INSERT INTO experiments (uuid, name, project_id, position, is_active, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s, %s, %s)"
        )
        conn.execute(text, (EXPERIMENT_ID, NAME, PROJECT_ID, POSITION, 1, CREATED_AT, UPDATED_AT,))

        text = (
            f"INSERT INTO comparisons (uuid, project_id, active_tab, created_at, updated_at) "
            f"VALUES (%s, %s, %s, %s, %s)"
        )
        conn.execute(text, (COMPARISON_ID, PROJECT_ID, 1, CREATED_AT, UPDATED_AT,))

        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM comparisons WHERE project_id in ('{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id in ('{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        conn.close()

    def test_list_comparisons(self):
        rv = TEST_CLIENT.get("/projects/unk/comparisons")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.get(f"/projects/{PROJECT_ID}/comparisons")
        result = rv.json()
        self.assertIsInstance(result["comparisons"], list)
        self.assertIsInstance(result["total"], int)

    def test_create_comparison(self):
        rv = TEST_CLIENT.post("/projects/unk/comparisons", json={})
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.post(f"/projects/{PROJECT_ID}/comparisons", json={})
        result = rv.json()
        expected = {
            "projectId": PROJECT_ID,
            "experimentId": None,
            "operatorId": None,
            "activeTab": "1",
            "runId": None,
            "layout": None,
        }
        # uuid, created_at, updated_at are machine-generated
        # we assert they exist, but we don't assert their values
        machine_generated = ["uuid", "createdAt", "updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)

    def test_update_comparison(self):
        rv = TEST_CLIENT.patch(f"/projects/foo/comparisons/{COMPARISON_ID}", json={})
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/comparisons/foo", json={})
        result = rv.json()
        expected = {"message": "The specified comparison does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/comparisons/{COMPARISON_ID}", json={
            "experimentId": "unk",
        })
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

        rv = TEST_CLIENT.patch(f"/projects/{PROJECT_ID}/comparisons/{COMPARISON_ID}", json={
            "experimentId": EXPERIMENT_ID,
        })
        result = rv.json()
        expected = {
            "uuid": COMPARISON_ID,
            "projectId": PROJECT_ID,
            "experimentId": EXPERIMENT_ID,
            "operatorId": None,
            "activeTab": "1",
            "runId": None,
            "layout": None,
            "createdAt": CREATED_AT_ISO,
        }
        machine_generated = ["updatedAt"]
        for attr in machine_generated:
            self.assertIn(attr, result)
            del result[attr]
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_delete_comparison(self):
        rv = TEST_CLIENT.delete(f"/projects/foo/comparisons/{COMPARISON_ID}")
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/comparisons/unk")
        result = rv.json()
        expected = {"message": "The specified comparison does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        rv = TEST_CLIENT.delete(f"/projects/{PROJECT_ID}/comparisons/{COMPARISON_ID}")
        result = rv.json()
        expected = {"message": "Comparison deleted"}
        self.assertDictEqual(expected, result)
