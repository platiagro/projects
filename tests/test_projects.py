# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestProjects(unittest.TestCase):
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

    def test_list_projects_no_args(self):
        """
        Should return an empty list.
        """
        rv = TEST_CLIENT.get("/projects")
        result = rv.json()

        expected = util.MOCK_PROJECT_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_projects_order_name_asc(self):
        """
        Should return a list of projects sorted by name descending.
        """
        rv = TEST_CLIENT.get("/projects?order=name desc")
        result = rv.json()

        expected = util.MOCK_PROJECT_LIST_SORTED_BY_NAME_DESC
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_projects_invalid_order_argument(self):
        """
        Should return a http error 400 and a message 'invalid order argument'.
        """
        rv = TEST_CLIENT.get("/projects?order=name unk")
        result = rv.json()

        expected = {"message": "Invalid order argument"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_list_projects_page_size_1(self):
        """
        Should return a list of projects with one element.
        """
        rv = TEST_CLIENT.get("/projects?page_size=1")
        result = rv.json()

        expected = {"projects": [util.MOCK_PROJECT_1], "total": 1}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_projects_page_size_1_page_3(self):
        """
        Should return a list of projects with one element.
        """
        rv = TEST_CLIENT.get("/projects?page_size=1&page=3")
        result = rv.json()

        expected = {"projects": [util.MOCK_PROJECT_3], "total": 1}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_project_invalid_request_body(self):
        """
        Should return http status 422 when invalid request body is given.
        """
        rv = TEST_CLIENT.post("/projects", json={})
        self.assertEqual(rv.status_code, 422)

    def test_create_project_given_name_already_exists(self):
        """
        Should return http status 400 and a message 'a project with given name already exists'.
        """
        rv = TEST_CLIENT.post("/projects", json={"name": util.MOCK_PROJECT_NAME_1})
        result = rv.json()

        expected = {"message": "a project with that name already exists"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_project_success(self):
        """
        Should create and return a project successfully.
        """
        project_name = "project-4"

        rv = TEST_CLIENT.post("/projects", json={"name": project_name})
        result = rv.json()
        expected = {
            "createdAt": mock.ANY,
            "deployments": [],
            "description": None,
            "experiments": [
                {
                    "createdAt": mock.ANY,
                    "isActive": True,
                    "name": "Experimento 1",
                    "operators": [],
                    "position": 0,
                    "projectId": mock.ANY,
                    "updatedAt": mock.ANY,
                    "uuid": mock.ANY,
                }
            ],
            "hasDeployment": False,
            "hasExperiment": True,
            "hasPreDeployment": False,
            "name": project_name,
            "updatedAt": mock.ANY,
            "uuid": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_get_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "foo"

        rv = TEST_CLIENT.get(f"/projects/{project_id}")
        result = rv.json()

        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_project_success(self):
        """
        Should return a project successfully.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/projects/{project_id}")
        result = rv.json()

        expected = {
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "deployments": [util.MOCK_DEPLOYMENT_1, util.MOCK_DEPLOYMENT_2],
            "description": None,
            "experiments": [util.MOCK_EXPERIMENT_1, util.MOCK_EXPERIMENT_2],
            "hasDeployment": False,
            "hasExperiment": True,
            "hasPreDeployment": True,
            "name": util.MOCK_PROJECT_NAME_1,
            "updatedAt": util.MOCK_UPDATED_AT_1.isoformat(),
            "uuid": project_id,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_update_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "foo"

        rv = TEST_CLIENT.patch(f"/projects/{project_id}", json={})
        result = rv.json()

        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_project_given_name_already_exists(self):
        """
        Should return http status 400 and a message 'a project with given name already exists'.
        """
        project_id = util.MOCK_UUID_1
        project_name = util.MOCK_PROJECT_NAME_2
        rv = TEST_CLIENT.patch(f"/projects/{project_id}", json={"name": project_name})
        result = rv.json()

        expected = {"message": "a project with that name already exists"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_project_success(self):
        """
        Should update and return a project successfully.
        """
        project_id = util.MOCK_UUID_1
        project_name = "project-4"

        rv = TEST_CLIENT.patch(f"/projects/{project_id}", json={"name": project_name})
        result = rv.json()

        expected = {
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "deployments": [util.MOCK_DEPLOYMENT_1, util.MOCK_DEPLOYMENT_2],
            "description": None,
            "experiments": [util.MOCK_EXPERIMENT_1, util.MOCK_EXPERIMENT_2],
            "hasDeployment": False,
            "hasExperiment": True,
            "hasPreDeployment": True,
            "name": project_name,
            "updatedAt": mock.ANY,
            "uuid": project_id,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_delete_project_not_found(self):
        """
        Should return a http error 404 and a message 'specified project does not exist'.
        """
        project_id = "unk"

        rv = TEST_CLIENT.delete(f"/projects/{project_id}")
        result = rv.json()

        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "kubernetes.client.CustomObjectsApi.list_namespaced_custom_object",
        return_value={"items": []},
    )
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_delete_project_success(
        self, mock_kfp_client, mock_list_namespaced_custom_object
    ):
        """
        Should delete project successfully.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/projects/{project_id}")
        result = rv.json()

        expected = {"message": "Project deleted"}
        self.assertDictEqual(expected, result)

        mock_list_namespaced_custom_object.assert_any_call(
            "machinelearning.seldon.io", "v1", "anonymous", "seldondeployments"
        )
        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")

    def test_delete_multiple_projects_at_least_one_project_error(self):
        """
        Should return a http error 400 and a message 'inform at least one project'.
        """
        rv = TEST_CLIENT.post(f"/projects/deleteprojects", json=[])
        result = rv.json()

        expected = {"message": "inform at least one project"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    @mock.patch(
        "kubernetes.client.CustomObjectsApi.list_namespaced_custom_object",
        return_value={"items": []},
    )
    @mock.patch(
        "kfp.Client",
        return_value=util.MOCK_KFP_CLIENT,
    )
    def test_delete_multiple_projects_success(
        self, mock_kfp_client, mock_list_namespaced_custom_object
    ):
        """
        Should delete projects successfully.
        """
        project_id_1 = util.MOCK_UUID_1
        project_id_2 = util.MOCK_UUID_2

        rv = TEST_CLIENT.post(
            f"/projects/deleteprojects", json=[project_id_1, project_id_2]
        )
        result = rv.json()

        expected = {"message": "Successfully removed projects"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_list_namespaced_custom_object.assert_any_call(
            "machinelearning.seldon.io", "v1", "anonymous", "seldondeployments"
        )
        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
