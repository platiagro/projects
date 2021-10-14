# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestDeploymentsRuns(unittest.TestCase):
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
        Should return a run successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/deployments/{deployment_id}/runs")
        result = rv.json()
        expected = util.MOCK_DEPLOYMENT_RUN_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")

    def test_create_deployment_run(self):
        """
        Should return an http status 404 and a message 'The specified project does not exist'.
        """
        deployment_id = util.MOCK_UUID_1
        rv = TEST_CLIENT.post(f"/projects/foo/deployments/{deployment_id}/runs", json={})
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 404)
        self.assertDictEqual(result, expected)

    def test_create_project_run(self):
        """
        Should return an http status 404 and a message 'The specified deployment does not exist'.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(f"/projects/{project_id}/deployments/foo/runs", json={})
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 404)
        self.assertDictEqual(result, expected)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.client.CustomObjectsApi",
        return_value=util.MOCK_CUSTOM_OBJECTS_API,
    )
    def test_create_project_deployment_run(
        self,
        mock_custom_objects_api,
        mock_core_v1_api,
        mock_kfp_client
    ):
        """
        Should raise an exception when ...
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(f"/projects/{project_id}/deployments/{deployment_id}/runs")
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertIn("uuid", result)
        self.assertIn("operators", result)
        self.assertEqual(deployment_id, result["deploymentId"])
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_core_v1_api.assert_any_call()
        mock_custom_objects_api.assert_any_call()

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_get_run(self, mock_kfp_client):
        """
        Should raise an exception when ...
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/deployments/{deployment_id}/runs/latest")
        result = rv.json()
        self.assertIsInstance(result, dict)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")

    # @mock.patch("projects.kubernetes.kube_config.config.load_incluster_config")
    # # @mock.patch(
    # #     "kubernetes.client.CustomObjectsApi.list_namespaced_custom_object",
    # #     return_value={"items": []},
    # # )
    # @mock.patch(
    #     "kfp.Client",
    #     return_value=util.MOCK_KFP_CLIENT,
    # )
    # @mock.patch(
    #     "kubernetes.client.CoreV1Api",
    #     return_value=util.MOCK_CORE_V1_API,
    # )
    # @mock.patch(
    #     "kubernetes.client.CustomObjectsApi",
    #     return_value=util.MOCK_CUSTOM_OBJECTS_API,
    # )
    # def test_delete_run(self, mock_custom_objects_api, mock_core_v1_api, mock_kfp_client, mock_load_kube_config):
    #     """
    #     Should raise an exception when ...
    #     """
    #     project_id = util.MOCK_UUID_1
    #     deployment_id = util.MOCK_UUID_1
    #     run_id = util.MOCK_UUID_1

    #     rv = TEST_CLIENT.delete(f"/projects/{project_id}/deployments/{deployment_id}/runs/latest")
    #     result = rv.json()
    #     expected = {"message": "Deployment deleted"}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 200)

    #     mock_load_kube_config.assert_any_call()
    #     # mock_list_namespaced_custom_object.assert_any_call(
    #     #     "machinelearning.seldon.io", "v1", "anonymous", "seldondeployments"
    #     # )
    #     mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
    #     mock_core_v1_api.assert_any_call()
    #     mock_custom_objects_api.assert_any_call()
