# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestComparisons(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        """
        Sets up the test before running it.
        """
        util.create_mocks()

    def tearDown(self):
        """
        Deconstructs the test after running it.
        """
        util.delete_mocks()

    def test_list_comparisons_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"

        rv = TEST_CLIENT.get(f"/projects/{project_id}/comparisons")
        result = rv.json()

        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_comparisons_success(self):
        """
        Should a list of comparisons successfully.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/comparisons")
        result = rv.json()

        expected = util.MOCK_COMPARISON_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_comparison_project_not_found_error(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/comparisons",
            json={},
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_create_comparison_success(self):
        """
        Should create and return an comparison successfully.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/comparisons",
            json={},
        )
        result = rv.json()

        expected = {
            "activeTab": "1",
            "createdAt": mock.ANY,
            "experimentId": None,
            "layout": None,
            "operatorId": None,
            "projectId": project_id,
            "runId": None,
            "updatedAt": mock.ANY,
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_update_comparison_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "foo"
        comparison_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/comparisons/{comparison_id}", json={}
        )
        result = rv.json()

        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_comparison_not_found(self):
        """
        Should return a http error 404 and a message 'specified comparison does not exist'.
        """
        project_id = util.MOCK_UUID_1
        comparison_id = "foo"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/comparisons/{comparison_id}", json={}
        )
        result = rv.json()

        expected = {"message": "The specified comparison does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_comparison_with_experiment_id_success(self):
        """
        Should update and return an comparison successfully.
        """
        project_id = util.MOCK_UUID_1
        comparison_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_2

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/comparisons/{comparison_id}",
            json={
                "experimentId": experiment_id,
                "operatorId": None,
                "runId": None,
            },
        )
        result = rv.json()

        expected = {
            "activeTab": "1",
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "experimentId": experiment_id,
            "layout": {"x": 0, "y": 0, "w": 0, "h": 0},
            "operatorId": None,
            "projectId": project_id,
            "runId": None,
            "updatedAt": mock.ANY,
            "uuid": comparison_id,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_delete_comparison_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        comparison_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/comparisons/{comparison_id}")
        result = rv.json()

        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_comparison_not_found(self):
        """
        Should return a http error 404 and a message 'specified comparison does not exist'.
        """
        project_id = util.MOCK_UUID_1
        comparison_id = "unk"

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/comparisons/{comparison_id}")
        result = rv.json()

        expected = {"message": "The specified comparison does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_comparison_success(self):
        """
        Should delete comparison successfully.
        """
        project_id = util.MOCK_UUID_1
        comparison_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/comparisons/{comparison_id}")
        result = rv.json()

        expected = {"message": "Comparison deleted"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
