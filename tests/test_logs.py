# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestLogs(unittest.TestCase):
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
        "kubernetes.config.load_kube_config",
    )
    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.client.CustomObjectsApi",
        return_value=util.MOCK_CUSTOM_OBJECTS_API,
    )
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_list_experiment_logs_success(
        self,
        mock_kfp_client,
        mock_custom_objects_api,
        mock_core_v1_api,
        mock_load_config,
    ):
        """
        Should return a list of experiment logs successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        run_id = "latest"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/runs/{run_id}/logs"
        )
        result = rv.json()
        expected = util.MOCK_LOG_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_load_config.assert_any_call()
        mock_core_v1_api.assert_any_call()
        mock_custom_objects_api.assert_any_call()

    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_list_deployment_logs_success(
        self,
        mock_kfp_client,
        mock_core_v1_api,
        mock_load_config,
    ):
        """
        Should return a list of deployment logs successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        run_id = "latest"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/runs/{run_id}/logs"
        )
        result = rv.json()
        expected = util.MOCK_LOG_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_load_config.assert_any_call()
        mock_core_v1_api.assert_any_call()
