# -*- coding: utf-8 -*-
from json import dumps
from unittest import TestCase

from projects.api.main import app
from projects.controllers.utils import uuid_alpha
from projects.database import engine
from projects.object_storage import BUCKET_NAME

EXPERIMENT_ID = str(uuid_alpha())
PROJECT_ID = str(uuid_alpha())
COMPARE_RESULT_ID = str(uuid_alpha())
NAME = "foo"
POSITION = 0
CREATED_AT = "2000-01-01 00:00:00"
CREATED_AT_ISO = "2000-01-01T00:00:00"
UPDATED_AT = "2000-01-01 00:00:00"
UPDATED_AT_ISO = "2000-01-01T00:00:00"


class TestCompareResults(TestCase):
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
            f"INSERT INTO compare_result (uuid, project_id, created_at, updated_at) "
            f"VALUES ('{COMPARE_RESULT_ID}', '{PROJECT_ID}', '{CREATED_AT}', '{UPDATED_AT}')"
        )
        conn.execute(text)

        conn.close()

    def tearDown(self):
        conn = engine.connect()

        text = f"DELETE FROM compare_result WHERE project_id in ('{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM experiments WHERE project_id in ('{PROJECT_ID}')"
        conn.execute(text)

        text = f"DELETE FROM projects WHERE uuid = '{PROJECT_ID}'"
        conn.execute(text)

        conn.close()

    def test_list_compare_results(self):
        with app.test_client() as c:
            rv = c.get("/projects/unk/compareResults")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.get(f"/projects/{PROJECT_ID}/compareResults")
            result = rv.get_json()
            self.assertIsInstance(result, list)

    def test_create_compare_result(self):
        with app.test_client() as c:
            rv = c.post("/projects/unk/compareResults")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.post(f"/projects/{PROJECT_ID}/compareResults")
            result = rv.get_json()
            expected = {
                "projectId": PROJECT_ID,
                "experimentId": None,
                "operatorId": None,
                "runId": None,
            }
            # uuid, created_at, updated_at are machine-generated
            # we assert they exist, but we don't assert their values
            machine_generated = ["uuid", "createdAt", "updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)

    def test_update_compare_result(self):
        with app.test_client() as c:
            rv = c.patch(f"/projects/foo/compareResults/{COMPARE_RESULT_ID}", json={})
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/compareResults/foo", json={})
            result = rv.get_json()
            expected = {"message": "The specified compare result does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/compareResults/{COMPARE_RESULT_ID}", json={
                "experimentId": "unk",
            })
            result = rv.get_json()
            expected = {"message": "The specified experiment does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.patch(f"/projects/{PROJECT_ID}/compareResults/{COMPARE_RESULT_ID}", json={
                "unk": "bar",
            })
            self.assertEqual(rv.status_code, 400)

            rv = c.patch(f"/projects/{PROJECT_ID}/compareResults/{COMPARE_RESULT_ID}", json={
                "experimentId": EXPERIMENT_ID,
            })
            result = rv.get_json()
            expected = {
                "uuid": COMPARE_RESULT_ID,
                "projectId": PROJECT_ID,
                "experimentId": EXPERIMENT_ID,
                "operatorId": None,
                "runId": None,
                "createdAt": CREATED_AT_ISO,
            }
            machine_generated = ["updatedAt"]
            for attr in machine_generated:
                self.assertIn(attr, result)
                del result[attr]
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 200)

    def test_delete_compare_result(self):
        with app.test_client() as c:
            rv = c.delete(f"/projects/foo/compareResults/{COMPARE_RESULT_ID}")
            result = rv.get_json()
            expected = {"message": "The specified project does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/compareResults/unk")
            result = rv.get_json()
            expected = {"message": "The specified compare result does not exist"}
            self.assertDictEqual(expected, result)
            self.assertEqual(rv.status_code, 404)

            rv = c.delete(f"/projects/{PROJECT_ID}/compareResults/{COMPARE_RESULT_ID}")
            result = rv.get_json()
            expected = {"message": "Compare result deleted"}
            self.assertDictEqual(expected, result)
