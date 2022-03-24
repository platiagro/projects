# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestOperatorsDeployments(unittest.TestCase):
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

    def test_list_operators_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/operators"
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_operators_deployment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/operators"
        )
        result = rv.json()
        expected = {
            "message": "The specified deployment does not exist",
            "code": "DeploymentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_operators_success(self):
        """
        Should return a list of operators successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/operators"
        )
        result = rv.json()
        expected = util.MOCK_OPERATOR_LIST_DEPLOYMENTS
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_update_operator_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        deployment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}/operators/{operator_id}",
            json={},
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_operator_deployment_not_found(self):
        """
        Should return a http error 404 and a message 'specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}/operators/{operator_id}",
            json={},
        )
        result = rv.json()
        expected = {
            "message": "The specified deployment does not exist",
            "code": "DeploymentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_operator_operator_not_found(self):
        """
        Should return a http error 404 and a message 'specified operator does not exist'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        operator_id = "unk"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}/operators/{operator_id}",
            json={},
        )
        result = rv.json()
        expected = {
            "message": "The specified operator does not exist",
            "code": "OperatorNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_operator_dependencies_are_not_valid_error_1(self):
        """
        Should return http status 400 and a message 'The specified dependencies are not valid'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1
        dependencies = [operator_id]

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}/operators/{operator_id}",
            json={
                "dependencies": dependencies,
            },
        )
        result = rv.json()
        expected = {
            "message": "The specified dependencies are not valid.",
            "code": "InvalidDependencies",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_operator_dependencies_are_not_valid_error_2(self):
        """
        Should return http status 400 and a message 'The specified dependencies are not valid'.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1
        dependencies = ["unk"]

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}/operators/{operator_id}",
            json={
                "dependencies": dependencies,
            },
        )
        result = rv.json()
        expected = {
            "message": "The specified dependencies are not valid.",
            "code": "InvalidDependencies",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_operator_with_empty_success(self):
        """
        Should update and return an operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}/operators/{operator_id}",
            json={},
        )
        result = rv.json()
        expected = {
            "uuid": operator_id,
            "name": util.MOCK_TASK_NAME_1,
            "taskId": util.MOCK_UUID_1,
            "task": {
                "name": util.MOCK_TASK_NAME_1,
                "tags": [],
                "parameters": [],
            },
            "dependencies": [],
            "parameters": {"dataset": util.IRIS_DATASET_NAME},
            "experimentId": experiment_id,
            "deploymentId": None,
            "positionX": 0,
            "positionY": 0,
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "updatedAt": mock.ANY,
            "status": "Unset",
            "statusMessage": None,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_update_operator_with_parameters_success(self):
        """
        Should update and return an operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1
        parameters = {"coef": 0.2}
        position_x = 100
        position_y = 200

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}/operators/{operator_id}",
            json={
                "parameters": parameters,
                "positionX": position_x,
                "positionY": position_y,
            },
        )
        result = rv.json()
        expected = {
            "uuid": operator_id,
            "name": util.MOCK_TASK_NAME_1,
            "taskId": util.MOCK_UUID_1,
            "task": {
                "name": util.MOCK_TASK_NAME_1,
                "tags": [],
                "parameters": [],
            },
            "dependencies": [],
            "parameters": parameters,
            "experimentId": experiment_id,
            "deploymentId": None,
            "positionX": position_x,
            "positionY": position_y,
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "updatedAt": mock.ANY,
            "status": "Setted up",  # Status should change to "Setted up"
            "statusMessage": None,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_update_operator_with_dependencies_success(self):
        """
        Should update and return an operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_4
        dependencies = [util.MOCK_UUID_1]

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/deployments/{deployment_id}/operators/{operator_id}",
            json={
                "dependencies": dependencies,
            },
        )
        result = rv.json()
        expected = {
            "uuid": operator_id,
            "name": util.MOCK_TASK_NAME_1,
            "taskId": util.MOCK_UUID_1,
            "task": {
                "name": util.MOCK_TASK_NAME_1,
                "tags": [],
                "parameters": [],
            },
            "dependencies": dependencies,
            "parameters": {},
            "experimentId": experiment_id,
            "deploymentId": None,
            "positionX": 0,
            "positionY": 0,
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "updatedAt": mock.ANY,
            "status": "Unset",
            "statusMessage": None,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)
