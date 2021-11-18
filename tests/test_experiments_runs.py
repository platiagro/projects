# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestExperimentsRuns(unittest.TestCase):
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

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_list_runs(self, mock_kfp_client):
        """
        Should return an runs successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments/{experiment_id}/runs")
        result = rv.json()
        self.assertIsInstance(result["runs"], list)
        self.assertIsInstance(result["total"], int)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_create_run(self, mock_kfp_client):
        """
        Should return the creation of a successful runs.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/runs", json={}
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertIn("operators", result)
        self.assertIn("uuid", result)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")

    def test_list_run_status_operator(self):
        """
        Should return an runs successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments/{experiment_id}")
        result = rv.json()
        operator = result["operators"][0]
        self.assertEqual("Unset", operator["status"])
        self.assertEqual(rv.status_code, 200)

    def test_list_run(self):
        """
        Should return a http error 404 and a message 'The specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        run_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}"
        )
        result = rv.json()
        expected = {
            "message": "The specified experiment does not exist",
            "code": "ExperimentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_list_run_lastest(self, mock_kfp_client):
        """
        Should return an runs successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/latest"
        )
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertIn("operators", result)
        self.assertIn("uuid", result)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_NOT_GET_RUN,
    )
    def test_terminate_not_run(self, mock_kfp_client):
        """
        Should return a http error 404 and a message 'The specified runs does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/unk"
        )
        result = rv.json()
        expected = {
            "message": "The specified run does not exist",
            "code": "RunNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_terminate_run(self, mock_kfp_client):
        """
        Should return an runs successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/latest"
        )
        result = rv.json()
        expected = {"message": "Run terminated"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
