# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestExperiments(unittest.TestCase):
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

    def test_list_experiments_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments")
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_experiments_success(self):
        """
        Should return a list of experiments successfully.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments")
        result = rv.json()

        expected = util.MOCK_EXPERIMENT_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_experiment_project_not_found_error(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        experiment_name = "experiment-2"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments",
            json={
                "name": experiment_name,
            },
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_create_experiment_invalid_request_body_error(self):
        """
        Should return http status 422 when invalid request body is given.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(f"/projects/{project_id}/experiments", json={})
        self.assertEqual(rv.status_code, 422)

    def test_create_experiment_name_already_exists_error(self):
        """
        Should return a http error 400 and a message 'experiment with that name already exists'.
        """
        project_id = util.MOCK_UUID_1
        experiment_name = util.MOCK_EXPERIMENT_NAME_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments",
            json={
                "name": experiment_name,
            },
        )
        result = rv.json()

        expected = {
            "message": "an experiment with that name already exists",
            "code": "ExperimentNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_experiment_success(self):
        """
        Should create and return an experiment successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_name = "experiment-3"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments",
            json={
                "name": experiment_name,
            },
        )
        result = rv.json()

        expected = {
            "name": experiment_name,
            "projectId": project_id,
            "position": 2,
            "isActive": True,
            "operators": [],
            "createdAt": mock.ANY,
            "updatedAt": mock.ANY,
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_experiment_with_copy_from_success(self):
        """
        Should create and return an experiment successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_name = "experiment-3"
        copy_from = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments",
            json={"name": experiment_name, "copyFrom": copy_from},
        )
        result = rv.json()

        expected = {
            "name": experiment_name,
            "projectId": project_id,
            "position": 2,
            "isActive": True,
            "operators": [
                {
                    "uuid": mock.ANY,
                    "name": util.MOCK_TASK_NAME_1,
                    "taskId": util.MOCK_UUID_1,
                    "task": {
                        "name": util.MOCK_TASK_NAME_1,
                        "tags": [],
                        "parameters": [],
                    },
                    "dependencies": [],
                    "parameters": {"dataset": "iris.csv"},
                    "experimentId": mock.ANY,
                    "deploymentId": None,
                    "positionX": 0,
                    "positionY": 0,
                    "createdAt": mock.ANY,
                    "updatedAt": mock.ANY,
                    "status": "Unset",
                    "statusMessage": None,
                },
                {
                    "uuid": mock.ANY,
                    "name": util.MOCK_TASK_NAME_1,
                    "taskId": util.MOCK_UUID_1,
                    "task": {
                        "name": util.MOCK_TASK_NAME_1,
                        "tags": [],
                        "parameters": [],
                    },
                    "dependencies": [mock.ANY],
                    "parameters": {},
                    "experimentId": mock.ANY,
                    "deploymentId": None,
                    "positionX": 0,
                    "positionY": 0,
                    "createdAt": mock.ANY,
                    "updatedAt": mock.ANY,
                    "status": "Unset",
                    "statusMessage": None,
                },
            ],
            "createdAt": mock.ANY,
            "updatedAt": mock.ANY,
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_experiment_source_experiment_error(self):
        """
        Should return a http error 400 and a message 'source experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_name = "experiment-3"
        copy_from = "unk"

        rv = TEST_CLIENT.post(
            f"/projects/{project_id}/experiments",
            json={"name": experiment_name, "copyFrom": copy_from},
        )
        result = rv.json()

        expected = {
            "message": "source experiment does not exist",
            "code": "InvalidExperimentId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_get_experiment_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        experiment_id = "experiment-2"

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments/{experiment_id}")
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_experiment_not_found(self):
        """
        Should return a http error 404 and a message 'specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "experiment-2"

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments/{experiment_id}")
        result = rv.json()

        expected = {
            "message": "The specified experiment does not exist",
            "code": "ExperimentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_experiment_success(self):
        """
        Should return a experiment successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}/experiments/{experiment_id}")
        result = rv.json()

        expected = {
            "name": util.MOCK_EXPERIMENT_NAME_1,
            "projectId": project_id,
            "position": 0,
            "isActive": True,
            "operators": [util.MOCK_OPERATOR_1, util.MOCK_OPERATOR_4],
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "updatedAt": util.MOCK_UPDATED_AT_1.isoformat(),
            "uuid": experiment_id,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_update_experiment_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "foo"
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}", json={}
        )
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_experiment_not_found(self):
        """
        Should return a http error 404 and a message 'specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "foo"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}", json={}
        )
        result = rv.json()

        expected = {
            "message": "The specified experiment does not exist",
            "code": "ExperimentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_experiment_given_name_already_exists(self):
        """
        Should return http status 400 and a message 'an experiment with given name already exists'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        experiment_name = util.MOCK_EXPERIMENT_NAME_2

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}",
            json={"name": experiment_name},
        )
        result = rv.json()

        expected = {
            "message": "an experiment with that name already exists",
            "code": "ExperimentNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_experiment_with_template_id_not_found(self):
        """
        Should return http status 400 and a message 'specified template does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        template_id = "unk"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}",
            json={
                "templateId": template_id,
            },
        )
        result = rv.json()

        expected = {
            "message": "The specified template does not exist",
            "code": "InvalidTemplateId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_experiment_with_template_id_success(self):
        """
        Should update and return an experiment successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        template_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}",
            json={
                "templateId": template_id,
            },
        )
        result = rv.json()

        expected = {
            "name": util.MOCK_EXPERIMENT_NAME_1,
            "projectId": project_id,
            "position": 0,
            "isActive": True,
            "operators": [
                {
                    "createdAt": mock.ANY,
                    "dependencies": [],
                    "deploymentId": None,
                    "experimentId": experiment_id,
                    "name": util.MOCK_TASK_NAME_1,
                    "parameters": {},
                    "positionX": 0,
                    "positionY": 0,
                    "status": "Unset",
                    "statusMessage": None,
                    "task": {"name": "task-1", "parameters": [], "tags": []},
                    "taskId": "uuid-1",
                    "updatedAt": mock.ANY,
                    "uuid": mock.ANY,
                }
            ],
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "updatedAt": util.MOCK_UPDATED_AT_1.isoformat(),
            "uuid": experiment_id,
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

    def test_delete_experiment_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/experiments/{experiment_id}")
        result = rv.json()

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_experiment_not_found(self):
        """
        Should return a http error 404 and a message 'specified experiment does not exist'.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/experiments/{experiment_id}")
        result = rv.json()

        expected = {
            "message": "The specified experiment does not exist",
            "code": "ExperimentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_experiment_success(self):
        """
        Should delete experiment successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/projects/{project_id}/experiments/{experiment_id}")
        result = rv.json()

        expected = {"message": "Experiment deleted"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
