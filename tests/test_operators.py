# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestOperators(unittest.TestCase):
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
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/operators"
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_operators_experiment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/operators"
        )
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_operators_success(self):
        """
        Should return a list of operators successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/experiments/{experiment_id}/operators"
        )
        result = rv.json()
        expected = util.MOCK_OPERATOR_LIST
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_create_operator_project_not_found_error(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        experiment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={
                "taskId": task_id,
                "positionX": 0,
                "positionY": 0,
            },
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_create_operator_experiment_not_found_error(self):
        """
        Should return a http error 404 and a message 'specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={
                "taskId": task_id,
                "positionX": 0,
                "positionY": 0,
            },
        )
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_create_operator_invalid_request_body_error(self):
        """
        Should return http status 422 when invalid request body is given.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators", json={}
        )
        self.assertEqual(rv.status_code, 422)

    def test_create_operator_task_does_not_exist(self):
        """
        Should return a http error 400 and a message 'The specified task does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        task_id = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={
                "taskId": task_id,
                "positionX": 0,
                "positionY": 0,
            },
        )
        result = rv.json()
        expected = {"message": "The specified task does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_operator_invalid_request_body_error_2(self):
        """
        Should return http status 422 when invalid request body is given.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1
        dependencies = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={
                "taskId": task_id,
                "dependencies": dependencies,
            },  # only lists are accepted
        )
        self.assertEqual(rv.status_code, 422)

    def test_create_operator_invalid_request_body_error_3(self):
        """
        Should return http status 422 when invalid request body is given.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1
        dependencies = ["unk"]

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={"taskId": task_id, "dependencies": dependencies},
        )
        self.assertEqual(rv.status_code, 422)

    def test_create_operator_invalid_request_body_error_4(self):
        """
        Should return http status 422 when invalid request body is given.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1
        dependencies = [util.MOCK_UUID_1, util.MOCK_UUID_1]

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={"taskId": task_id, "dependencies": dependencies},
        )
        self.assertEqual(rv.status_code, 422)

    def test_create_operator_success_1(self):
        """
        Should create and return an operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={
                "taskId": task_id,
                "positionX": 0,
                "positionY": 0,
            },
        )
        result = rv.json()
        expected = {
            "uuid": mock.ANY,
            "name": util.MOCK_TASK_NAME_1,
            "taskId": util.MOCK_UUID_1,
            "task": {
                "name": util.MOCK_TASK_NAME_1,
                "tags": [],
                "parameters": [],
            },
            "dependencies": [],
            "parameters": {},
            "experimentId": experiment_id,
            "deploymentId": None,
            "positionX": 0,
            "positionY": 0,
            "createdAt": mock.ANY,
            "updatedAt": mock.ANY,
            "status": "Unset",
            "statusMessage": None,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_operator_success_2(self):
        """
        Should create and return an operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1
        parameters = {"coef": None}  # None is allowed!

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={
                "taskId": task_id,
                "positionX": 0,
                "positionY": 0,
                "parameters": parameters,
            },
        )
        result = rv.json()
        expected = {
            "uuid": mock.ANY,
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
            "positionX": 0,
            "positionY": 0,
            "createdAt": mock.ANY,
            "updatedAt": mock.ANY,
            "status": "Unset",
            "statusMessage": None,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_operator_success_3(self):
        """
        Should create and return an operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1
        parameters = {"coef": 1.0}

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={
                "taskId": task_id,
                "positionX": 0,
                "positionY": 0,
                "parameters": parameters,
            },
        )
        result = rv.json()
        expected = {
            "uuid": mock.ANY,
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
            "positionX": 0,
            "positionY": 0,
            "createdAt": mock.ANY,
            "updatedAt": mock.ANY,
            "status": "Unset",
            "statusMessage": None,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_operator_success_4(self):
        """
        Should create and return an operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        task_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments/{experiment_id}/operators",
            json={
                "taskId": task_id,
                "positionX": 0,
                "positionY": 0,
                "dependencies": [],
            },
        )
        result = rv.json()
        expected = {
            "uuid": mock.ANY,
            "name": util.MOCK_TASK_NAME_1,
            "taskId": util.MOCK_UUID_1,
            "task": {
                "name": util.MOCK_TASK_NAME_1,
                "tags": [],
                "parameters": [],
            },
            "dependencies": [],
            "parameters": {},
            "experimentId": experiment_id,
            "deploymentId": None,
            "positionX": 0,
            "positionY": 0,
            "createdAt": mock.ANY,
            "updatedAt": mock.ANY,
            "status": "Unset",
            "statusMessage": None,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_update_operator_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        experiment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
            json={},
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_operator_experiment_not_found(self):
        """
        Should return a http error 404 and a message 'specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
            json={},
        )
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_operator_operator_not_found(self):
        """
        Should return a http error 404 and a message 'specified operator does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        operator_id = "unk"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
            json={},
        )
        result = rv.json()
        expected = {"message": "The specified operator does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_operator_dependencies_are_not_valid_error_1(self):
        """
        Should return http status 400 and a message 'The specified dependencies are not valid'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1
        dependencies = [operator_id]

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
            json={
                "dependencies": dependencies,
            },
        )
        result = rv.json()
        expected = {"message": "The specified dependencies are not valid."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_operator_dependencies_are_not_valid_error_2(self):
        """
        Should return http status 400 and a message 'The specified dependencies are not valid'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1
        dependencies = ["unk"]

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
            json={
                "dependencies": dependencies,
            },
        )
        result = rv.json()
        expected = {"message": "The specified dependencies are not valid."}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    # def test_update_operator_cyclical_dependencies_error(self):
    #     """
    #     Should return http status 400 and a message 'Cyclical dependencies.'.
    #     """
    #     project_id = util.MOCK_UUID_1
    #     experiment_id = util.MOCK_UUID_1
    #     operator_id = util.MOCK_UUID_4
    #     dependencies = [util.MOCK_UUID_1]

    #     rv = TEST_CLIENT.patch(
    #         f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
    #         json={
    #             "dependencies": dependencies,
    #         },
    #     )
    #     result = rv.json()
    #     expected = {"message": "Cyclical dependencies."}
    #     self.assertDictEqual(expected, result)
    #     self.assertEqual(rv.status_code, 400)

    def test_update_operator_with_empty_success(self):
        """
        Should update and return an operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
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
        operator_id = util.MOCK_UUID_1
        parameters = {"coef": 0.2}
        position_x = 100
        position_y = 200

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
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

    # def test_update_operator_with_dependencies_success(self):
    #     """
    #     Should update and return an operator successfully.
    #     """
    #     project_id = util.MOCK_UUID_1
    #     experiment_id = util.MOCK_UUID_1
    #     operator_id = util.MOCK_UUID_1
    #     dependencies = [util.MOCK_UUID_4]

    #     rv = TEST_CLIENT.patch(
    #         f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}",
    #         json={
    #             "dependencies": dependencies,
    #         },
    #     )
    #     result = rv.json()
    #     expected = {
    #         "uuid": operator_id,
    #         "name": util.MOCK_TASK_NAME_1,
    #         "taskId": util.MOCK_UUID_1,
    #         "task": {
    #             "name": util.MOCK_TASK_NAME_1,
    #             "tags": [],
    #             "parameters": [],
    #         },
    #         "dependencies": dependencies,
    #         "parameters": {"dataset": util.IRIS_DATASET_NAME},
    #         "experimentId": experiment_id,
    #         "deploymentId": None,
    #         "positionX": 0,
    #         "positionY": 0,
    #         "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
    #         "updatedAt": mock.ANY,
    #         "status": "Setted up",  # Status should change to "Setted up"
    #         "statusMessage": None,
    #     }
    #     self.assertEqual(result, expected)
    #     self.assertEqual(rv.status_code, 200)

    def test_delete_operator_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        experiment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}"
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_operator_experiment_not_found(self):
        """
        Should return a http error 404 and a message 'specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}"
        )
        result = rv.json()
        expected = {"message": "The specified experiment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_operator_operator_not_found(self):
        """
        Should return a http error 404 and a message 'specified operator does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        operator_id = "unk"

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}"
        )
        result = rv.json()
        expected = {"message": "The specified operator does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_operator_success(self):
        """
        Should delete operator successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}"
        )
        result = rv.json()
        expected = {"message": "Operator deleted"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
