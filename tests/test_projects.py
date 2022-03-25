# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects import models
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
        rv = TEST_CLIENT.post("/projects/listprojects", json={})
        result = rv.json()

        expected = util.MOCK_PROJECT_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_projects_order_name_desc(self):
        """
        Should return a list of projects sorted by name descending.
        """
        rv = TEST_CLIENT.post("/projects/listprojects", json={"order": "name desc"})
        result = rv.json()

        expected = util.MOCK_PROJECT_LIST_SORTED_BY_NAME_DESC
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_projects_invalid_order_argument(self):
        """
        Should return a http error 400 and a message 'invalid order argument'.
        """
        rv = TEST_CLIENT.post("/projects/listprojects", json={"order": "name foo"})
        result = rv.json()

        expected = {
            "message": "Invalid order argument",
            "code": "InvalidOrderBy",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_list_projects_page_size_1_page_3(self):
        """
        Should return a list of projects with one element.
        """
        rv = TEST_CLIENT.post(
            "/projects/listprojects", json={"page_size": 1, "page": 3}
        )
        result = rv.json()
        total = util.TestingSessionLocal().query(models.Project).count()
        expected = {"projects": [util.MOCK_PROJECT_3], "total": total}
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_projects_with_filter(self):
        """
        Should return a list of projects compatible with some filter.
        """
        rv = TEST_CLIENT.post(
            "/projects/listprojects",
            json={"filters": {"name": util.MOCK_PROJECT_TO_BE_FILTERED_NAME}},
        )
        result = rv.json()
        expected = util.MOCK_PROJECT_LIST_FILTERED
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_list_projects_with_forbidden_characters(self):
        """
        Should return http status 400 if project name contains any forbidden char
        """
        for char in util.FORBIDDEN_CHARACTERS_LIST:
            rv = TEST_CLIENT.post(
                "/projects/listprojects",
                json={"filters": {"name": char}},
            )
            result = rv.json()
            expected = {
                "code": "NotAllowedChar",
                "message": "Not allowed char",
            }
            self.assertEqual(result, expected)
            self.assertEqual(rv.status_code, 400)

    def test_list_projects_exceeded_amount_characters(self):
        """
        Should return http status 400 when project name has a exceeded amount of char .
        """
        rv = TEST_CLIENT.post(
            "/projects/listprojects",
            json={
                "filters": {
                    "name": "LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc"
                }
            },
        )
        result = rv.json()
        expected = {
            "code": "ExceededACharAmount",
            "message": "Char quantity exceeded maximum allowed",
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

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

        expected = {
            "message": "a project with that name already exists",
            "code": "ProjectNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_project_with_forbidden_characters(self):
        """
        Should return http status 400 if name contains any forbidden char.
        """
        for char in util.FORBIDDEN_CHARACTERS_LIST:
            rv = TEST_CLIENT.post(
                "/projects",
                json={"name": char},
            )
            result = rv.json()
            expected = {
                "code": "NotAllowedChar",
                "message": "Not allowed char",
            }
            self.assertEqual(result, expected)
            self.assertEqual(rv.status_code, 400)

    def test_create_projects_exceeded_amount_characters(self):
        """
        Should return http status 400 when project name has a exceeded amount of char .
        """
        rv = TEST_CLIENT.post(
            "/projects",
            json={
                "name": "LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc"
            },
        )
        result = rv.json()
        expected = {
            "code": "ExceededACharAmount",
            "message": "Char quantity exceeded maximum allowed",
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 400)

    def test_create_projects_exceeded_amount_characters_in_description(self):
        """
        Should return http status 400 when project name has a exceeded amount of char .
        """
        rv = TEST_CLIENT.post(
            "/projects",
            json={
                "description": "LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc\
                LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc\
                LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc\
                LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc\
                LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc\
                LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc\
                LoremipsumdolorsitametconsecteturadipiscingelitInteerelitexauc"
            },
        )
        result = rv.json()
        expected = {
            "code": "ExceededACharAmount",
            "message": "Char quantity exceeded maximum allowed",
        }
        self.assertEqual(result, expected)
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

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
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

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
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

        expected = {
            "message": "a project with that name already exists",
            "code": "ProjectNameExists",
        }
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

        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
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
    def test_delete_project_success(
        self,
        mock_config_load,
        mock_kfp_client,
        mock_custom_objects_api,
    ):
        """
        Should delete project successfully.
        """
        project_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/projects/{project_id}")
        result = rv.json()

        expected = {"message": "Project deleted"}
        self.assertDictEqual(expected, result)

        mock_custom_objects_api.assert_any_call()
        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_config_load.assert_any_call()

    def test_delete_multiple_projects_at_least_one_project_error(self):
        """
        Should return a http error 400 and a message 'inform at least one project'.
        """
        rv = TEST_CLIENT.post("/projects/deleteprojects", json=[])
        result = rv.json()

        expected = {
            "message": "inform at least one project",
            "code": "MissingRequiredProjectId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

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
    def test_delete_multiple_projects_success(
        self, mock_config_load, mock_kfp_client, mock_custom_objects_api
    ):
        """
        Should delete projects successfully.
        """
        project_id_1 = util.MOCK_UUID_1
        project_id_2 = util.MOCK_UUID_2

        rv = TEST_CLIENT.post(
            "/projects/deleteprojects", json=[project_id_1, project_id_2]
        )
        result = rv.json()

        expected = {"message": "Successfully removed projects"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)

        mock_custom_objects_api.assert_any_call()
        mock_kfp_client.assert_any_call(host="http://ml-pipeline.kubeflow:8888")
        mock_config_load.assert_any_call()
