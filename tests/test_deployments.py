# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope
from projects.controllers import TaskController

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestDeployments(unittest.TestCase):
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

    def test_list_deployments_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"

        rv = TEST_CLIENT.get(f"/projects/{project_id}/deployments")
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_deployments_success(self):
        """
        Should return a list of deployments successfully.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/deployments")
        result = rv.json()

        expected = util.MOCK_DEPLOYMENT_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_deployment_project_not_found_error(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        deployment_name = "deployment-2"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={
                "name": deployment_name,
            },
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_create_deployment_invalid_request_body_error(self):
        """
        Should return a http error 400 and a message 'either experiments, templateId or copyFrom is required'.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(f"/projects/{project_id}/deployments", json={})
        result = rv.json()

        expected = {
            "message": "either experiments, templateId or copyFrom is required",
            "code": "MissingRequiredExperimentsOrTemplateIdOrCopyFrom",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_deployment_at_least_one_operator_error(self):
        """
        Should return a http error 400 and a message 'Necessary at least one operator'.
        """
        project_id = util.MOCK_UUID_1
        deployment_name = "deployment-3"
        experiments = [util.MOCK_UUID_2]

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={"name": deployment_name, "experiments": experiments},
        )
        result = rv.json()

        expected = {
            "message": "Necessary at least one operator.",
            "code": "MissingRequiredOperatorId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_deployment_experiments_not_exist_error(self):
        """
        Should return a http error 400 and a message 'some experiments do not exist'.
        """
        project_id = util.MOCK_UUID_1
        deployment_name = "deployment-3"
        experiments = ["unk"]

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={"name": deployment_name, "experiments": experiments},
        )
        result = rv.json()

        expected = {
            "message": "some experiments do not exist",
            "code": "InvalidExperiments",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_deployment_name_is_required_error(self):
        """
        Should return a http error 400 and a message 'name is required to duplicate deployment'.
        """
        project_id = util.MOCK_UUID_1
        copy_from = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={"copyFrom": copy_from},
        )
        result = rv.json()

        expected = {
            "message": "name is required to duplicate deployment",
            "code": "MissingRequiredDeploymentName",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_deployment_name_exists_error(self):
        """
        Should return a http error 400 and a message 'name is required to duplicate deployment'.
        """
        project_id = util.MOCK_UUID_1
        name = util.MOCK_DEPLOYMENT_NAME_1
        copy_from = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={"name": name, "copyFrom": copy_from},
        )
        result = rv.json()

        expected = {
            "message": "a deployment with that name already exists",
            "code": "DeploymentNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    @mock.patch.object(TaskController, "background_tasks", new_callable=mock.PropertyMock, return_value=util.MOCK_BACKGROUND_TASKS)
    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_create_deployment_with_experiments_success(
        self,
        mock_background_tasks,
        mock_load_config,
        mock_kfp_client,
        mock_core_v1_api,
    ):
        """
        Should create and return an deployment successfully.
        """
        project_id = util.MOCK_UUID_1
        experiments = [util.MOCK_UUID_1]

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={"experiments": experiments},
        )
        result = rv.json()

        expected = {
            "deployments": [
                {
                    "createdAt": mock.ANY,
                    "isActive": True,
                    "deployedAt": None,
                    "experimentId": util.MOCK_UUID_1,
                    "name": util.MOCK_EXPERIMENT_NAME_1,
                    "projectId": project_id,
                    "position": 2,
                    "operators": [
                        {
                            "createdAt": mock.ANY,
                            "dependencies": [mock.ANY],
                            "deploymentId": mock.ANY,
                            "experimentId": None,
                            "name": util.MOCK_TASK_NAME_1,
                            "parameters": {"dataset": "iris.csv"},
                            "positionX": 0,
                            "positionY": 0,
                            "status": "Setted up",
                            "statusMessage": None,
                            "task": {"name": "task-1", "parameters": [], "tags": []},
                            "taskId": util.MOCK_UUID_1,
                            "updatedAt": mock.ANY,
                            "uuid": mock.ANY,
                        },
                        {
                            "createdAt": mock.ANY,
                            "dependencies": [mock.ANY],
                            "deploymentId": mock.ANY,
                            "experimentId": None,
                            "name": util.MOCK_TASK_NAME_1,
                            "parameters": {},
                            "positionX": 0,
                            "positionY": 0,
                            "status": "Setted up",
                            "statusMessage": None,
                            "task": {"name": "task-1", "parameters": [], "tags": []},
                            "taskId": util.MOCK_UUID_1,
                            "updatedAt": mock.ANY,
                            "uuid": mock.ANY,
                        },
                        {
                            "createdAt": mock.ANY,
                            "dependencies": [],
                            "deploymentId": mock.ANY,
                            "experimentId": None,
                            "name": "Fonte de dados",
                            "parameters": {"dataset": None, "type": "L"},
                            "positionX": -300,
                            "positionY": 0,
                            "status": "Unset",
                            "statusMessage": None,
                            "task": {
                                "name": "Upload de arquivo",
                                "parameters": [],
                                "tags": ["DATASETS"],
                            },
                            "taskId": mock.ANY,
                            "updatedAt": mock.ANY,
                            "uuid": mock.ANY,
                        },
                    ],
                    "status": "Pending",
                    "updatedAt": mock.ANY,
                    "uuid": mock.ANY,
                    "url": None,
                }
            ],
            "total": 1,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_core_v1_api.assert_any_call()
        # mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        # mock_load_config.assert_any_call()

    @mock.patch.object(TaskController, "background_tasks", new_callable=mock.PropertyMock, return_value=util.MOCK_BACKGROUND_TASKS)
    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_create_deployment_with_copy_from_success(
        self,
        mock_background_tasks,
        mock_load_config,
        mock_kfp_client,
        mock_core_v1_api,
    ):
        """
        Should create and return an deployment successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_name = "deployment-3"
        copy_from = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={"name": deployment_name, "copyFrom": copy_from},
        )
        result = rv.json()

        expected = {
            "deployments": [
                {
                    "createdAt": mock.ANY,
                    "isActive": True,
                    "deployedAt": None,
                    "experimentId": util.MOCK_UUID_1,
                    "name": deployment_name,
                    "projectId": project_id,
                    "position": 2,
                    "operators": [
                        {
                            "createdAt": mock.ANY,
                            "dependencies": [mock.ANY],
                            "deploymentId": mock.ANY,
                            "experimentId": None,
                            "name": util.MOCK_TASK_NAME_1,
                            "parameters": {},
                            "positionX": 0,
                            "positionY": 0,
                            "status": "Setted up",
                            "statusMessage": None,
                            "task": {"name": "task-1", "parameters": [], "tags": []},
                            "taskId": util.MOCK_UUID_1,
                            "updatedAt": mock.ANY,
                            "uuid": mock.ANY,
                        },
                        {
                            "createdAt": mock.ANY,
                            "dependencies": [],
                            "deploymentId": mock.ANY,
                            "experimentId": None,
                            "name": "Fonte de dados",
                            "parameters": {"dataset": None, "type": "L"},
                            "positionX": -300,
                            "positionY": 0,
                            "status": "Unset",
                            "statusMessage": None,
                            "task": {
                                "name": "Upload de arquivo",
                                "parameters": [],
                                "tags": ["DATASETS"],
                            },
                            "taskId": mock.ANY,
                            "updatedAt": mock.ANY,
                            "uuid": mock.ANY,
                        },
                    ],
                    "status": "Pending",
                    "updatedAt": mock.ANY,
                    "uuid": mock.ANY,
                    "url": None,
                }
            ],
            "total": 1,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_core_v1_api.assert_any_call()
        # mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        # mock_load_config.assert_any_call()

    def test_create_deployment_source_deployment_error(self):
        """
        Should return a http error 400 and a message 'source deployment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        deployment_name = "deployment-3"
        copy_from = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={"name": deployment_name, "copyFrom": copy_from},
        )
        result = rv.json()

        expected = {
            "message": "source deployment does not exist",
            "code": "InvalidDeploymentId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    @mock.patch(
        "kubernetes.client.CoreV1Api",
        return_value=util.MOCK_CORE_V1_API,
    )
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_create_deployment_with_template_id_success(
        self,
        mock_load_config,
        mock_kfp_client,
        mock_core_v1_api,
    ):
        """
        Should create and return an deployment successfully.
        """
        project_id = util.MOCK_UUID_1
        template_id = util.MOCK_UUID_2

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/deployments",
            json={"templateId": template_id},
        )
        result = rv.json()

        expected = {
            "deployments": [
                {
                    "createdAt": mock.ANY,
                    "isActive": True,
                    "deployedAt": None,
                    "experimentId": None,
                    "name": util.MOCK_TEMPLATE_NAME_2,
                    "projectId": project_id,
                    "position": -1,
                    "operators": [
                        {
                            "createdAt": mock.ANY,
                            "dependencies": [],
                            "deploymentId": mock.ANY,
                            "experimentId": None,
                            "name": util.MOCK_TASK_NAME_1,
                            "parameters": {},
                            "positionX": 0,
                            "positionY": 0,
                            "status": "Setted up",
                            "statusMessage": None,
                            "task": {"name": "task-1", "parameters": [], "tags": []},
                            "taskId": util.MOCK_UUID_1,
                            "updatedAt": mock.ANY,
                            "uuid": mock.ANY,
                        },
                    ],
                    "status": "Pending",
                    "updatedAt": mock.ANY,
                    "uuid": mock.ANY,
                    "url": None,
                }
            ],
            "total": 1,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

        mock_core_v1_api.assert_any_call()
        # mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_load_config.assert_any_call()

    def test_get_deployment_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        deployment_id = "deployment-2"

        rv = TEST_CLIENT.get(f"/projects/{project_id}/deployments/{deployment_id}")
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_deployment_not_found(self):
        """
        Should return a http error 404 and a message 'specified deployment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "deployment-2"

        rv = TEST_CLIENT.get(f"/projects/{project_id}/deployments/{deployment_id}")
        result = rv.json()

        expected = {
            "message": "The specified deployment does not exist",
            "code": "DeploymentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_deployment_success(self):
        """
        Should return a deployment successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/deployments/{deployment_id}")
        result = rv.json()

        expected = util.MOCK_DEPLOYMENT_1
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_update_deployment_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "foo"
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}", json={}
        )
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_deployment_not_found(self):
        """
        Should return a http error 404 and a message 'specified deployment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "foo"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}", json={}
        )
        result = rv.json()

        expected = {
            "message": "The specified deployment does not exist",
            "code": "DeploymentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_deployment_given_name_already_exists(self):
        """
        Should return http status 400 and a message 'a deployment with given name already exists'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        deployment_name = util.MOCK_DEPLOYMENT_NAME_2

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}",
            json={"name": deployment_name},
        )
        result = rv.json()

        expected = {
            "message": "a deployment with that name already exists",
            "code": "DeploymentNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_deployment_success(self):
        """
        Should update and return an deployment successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        deployment_name = "deployment-4"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}",
            json={
                "name": deployment_name,
            },
        )
        result = rv.json()

        expected = {
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "deployedAt": None,
            "experimentId": util.MOCK_UUID_1,
            "isActive": True,
            "name": deployment_name,
            "position": 0,
            "projectId": project_id,
            "operators": [util.MOCK_OPERATOR_2],
            "status": "Pending",
            "updatedAt": mock.ANY,
            "url": None,
            "uuid": deployment_id,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_delete_deployment_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/deployments/{deployment_id}")
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_deployment_not_found(self):
        """
        Should return a http error 404 and a message 'specified deployment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/deployments/{deployment_id}")
        result = rv.json()

        expected = {
            "message": "The specified deployment does not exist",
            "code": "DeploymentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kubernetes.client.CustomObjectsApi",
        return_value=util.MOCK_CUSTOM_OBJECTS_API,
    )
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    @mock.patch(
        "kubernetes.config.load_kube_config",
    )
    def test_delete_deployment_success(
        self,
        mock_load_config,
        mock_kfp_client,
        mock_custom_objects_api,
    ):
        """
        Should delete deployment successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/deployments/{deployment_id}")
        result = rv.json()

        expected = {"message": "Deployment deleted"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_custom_objects_api.assert_any_call()
        # mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_load_config.assert_any_call()
