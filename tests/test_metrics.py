# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestMetrics(unittest.TestCase):
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

    def test_list_metrics_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        experiment_id = "unk"
        run_id = "unk"
        operator_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/metrics"
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
            "status_code": 404,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_metrics_experiment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        run_id = "unk"
        operator_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/metrics"
        )
        result = rv.json()
        expected = {
            "message": "The specified experiment does not exist",
            "code": "ExperimentNotFound",
            "status_code": 404,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "platiagro.list_metrics",
        side_effect=FileNotFoundError(),
    )
    def test_list_metrics_success_1(
        self,
        mock_list_metrics,
        mock_kfp_client,
    ):
        """
        Should return a list of metrics successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/metrics"
        )
        result = rv.json()
        self.assertIsInstance(result, list)
        self.assertEqual(result, [])

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_list_metrics.assert_any_call(
            experiment_id=experiment_id, operator_id=operator_id, run_id=run_id
        )

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "platiagro.list_metrics",
        return_value=[{"accuracy": 1.0}],
    )
    def test_list_metrics_success_2(
        self,
        mock_list_metrics,
        mock_kfp_client,
    ):
        """
        Should return a list of metrics successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/operators/{operator_id}/metrics"
        )
        result = rv.json()
        self.assertIsInstance(result, list)
        self.assertEqual(result, [{"accuracy": 1.0}])

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_list_metrics.assert_any_call(
            experiment_id=experiment_id, operator_id=operator_id, run_id=run_id
        )
