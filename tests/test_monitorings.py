# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope
from projects.kfp.monitorings import create_monitoring_task_config_map, delete_monitoring_task_config_map
import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestMonitorings(unittest.TestCase):
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

    def test_list_monitorings_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings"
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_monitorings_deployment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings"
        )
        result = rv.json()
        expected = {
            "message": "The specified deployment does not exist",
            "code": "DeploymentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_monitorings_success(self):
        """
        Should return a list of monitorings successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings"
        )
        result = rv.json()
        expected = util.MOCK_MONITORING_LIST
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_create_monitoring_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        deployment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings",
            json={
                "taskId": task_id,
            },
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_create_monitoring_deployment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings",
            json={
                "taskId": task_id,
            },
        )
        result = rv.json()
        expected = {
            "message": "The specified deployment does not exist",
            "code": "DeploymentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_create_monitoring_task_does_not_exist(self):
        """
        Should return a http error 400 and a message 'The specified task does not exist'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        task_id = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings",
            json={
                "taskId": task_id,
            },
        )
        result = rv.json()
        expected = {
            "message": "The specified task does not exist",
            "code": "InvalidTaskId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_create_monitoring_success(
        self,
        mock_kfp_client,
    ):
        """
        Should create and return a monitoring successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings",
            json={
                "taskId": task_id,
            },
        )
        result = rv.json()
        expected = {
            "createdAt": mock.ANY,
            "deploymentId": deployment_id,
            "taskId": task_id,
            "task": {"name": util.MOCK_TASK_NAME_1, "tags": []},
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")

    def test_delete_monitoring_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        deployment_id = util.MOCK_UUID_1
        monitoring_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}"
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_monitoring_deployment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"
        monitoring_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}"
        )
        result = rv.json()
        expected = {
            "message": "The specified deployment does not exist",
            "code": "DeploymentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_monitoring_monitoring_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        monitoring_id = "unk"

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}"
        )
        result = rv.json()
        expected = {
            "message": "The specified monitoring does not exist",
            "code": "MonitoringNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "kubernetes.client.CustomObjectsApi",
        return_value=util.MOCK_CUSTOM_OBJECTS_API,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_delete_monitoring_success(
        self,
        mock_load_config,
        mock_custom_objects_api,
        mock_kfp_client,
    ):
        """
        Should delete monitoring successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        monitoring_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}"
        )
        result = rv.json()
        expected = {"message": "Monitoring deleted"}
        self.assertDictEqual(expected, result)

        mock_custom_objects_api.assert_any_call()
        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_load_config.assert_any_call()

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_create_monitoring_task_config_map(self, mock_core_v1_api, mock_load_kube_config):
        self.assertIsNone(create_monitoring_task_config_map("id", {"data": "data"}))

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_delete_monitoring_task_config_map_success(self, mock_core_v1_api, mock_load_kube_config):
        self.assertIsNone(delete_monitoring_task_config_map("id"))

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API_NOT_BOUND,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_delete_monitoring_task_config_map_fail(self, mock_core_v1_api, mock_load_kube_config):
        self.assertIsNone(delete_monitoring_task_config_map("id"))
