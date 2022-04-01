# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestTemplates(unittest.TestCase):
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

    def test_list_templates_no_args(self):
        """
        Should return an empty list.
        """
        rv = TEST_CLIENT.get("/templates")
        result = rv.json()

        expected = util.MOCK_TEMPLATE_LIST
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_template_invalid_request_body(self):
        """
        Should return http status 422 when invalid request body is given.
        """
        rv = TEST_CLIENT.post("/templates", json={})
        self.assertEqual(rv.status_code, 422)

    def test_create_template_experiment_or_deployment_needed_to_create(self):
        """
        Should return http status 400 and a message 'experimentId or deploymentId needed to create template'.
        """
        rv = TEST_CLIENT.post(
            "/templates",
            json={
                "name": "foo",
            },
        )
        result = rv.json()

        expected = {
            "message": "experimentId or deploymentId needed to create template.",
            "code": "MissingRequiredExperimentIdOrDeploymentId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_template_given_name_already_exists(self):
        """
        Should return http status 400 and a message 'a template with given name already exists'.
        """
        template_name = util.MOCK_TEMPLATE_NAME_1
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            "/templates",
            json={
                "name": template_name,
                "experimentId": experiment_id,
            },
        )
        result = rv.json()

        expected = {
            "message": "a template with that name already exists",
            "code": "TemplateNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_create_template_with_experiment_id_success(self):
        """
        Should create and return a template successfully.
        """
        template_name = "template-3"
        experiment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            "/templates",
            json={
                "name": template_name,
                "experimentId": experiment_id,
            },
        )
        result = rv.json()

        expected = {
            "uuid": mock.ANY,
            "name": template_name,
            "tasks": [
                {
                    "uuid": util.MOCK_UUID_1,
                    "task_id": util.MOCK_UUID_1,
                    "dependencies": [],
                    "position_x": 0.0,
                    "position_y": 0.0,
                },
                {
                    "uuid": util.MOCK_UUID_4,
                    "task_id": util.MOCK_UUID_1,
                    "dependencies": [util.MOCK_UUID_1],
                    "position_x": 0.0,
                    "position_y": 0.0,
                },
            ],
            "experimentId": experiment_id,
            "deploymentId": None,
            "createdAt": mock.ANY,
            "updatedAt": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_create_template_with_deployment_id_success(self):
        """
        Should create and return a template successfully.
        """
        template_name = "template-3"
        deployment_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.post(
            "/templates",
            json={
                "name": template_name,
                "deploymentId": deployment_id,
            },
        )
        result = rv.json()

        expected = {
            "uuid": mock.ANY,
            "name": template_name,
            "tasks": [
                {
                    "uuid": util.MOCK_UUID_2,
                    "task_id": util.MOCK_UUID_1,
                    "dependencies": [],
                    "position_x": 0.0,
                    "position_y": 0.0,
                }
            ],
            "experimentId": None,
            "deploymentId": deployment_id,
            "createdAt": mock.ANY,
            "updatedAt": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_get_template_not_found(self):
        """
        Should return a http error 404 and a message 'specified template does not exist'.
        """
        template_id = "foo"

        rv = TEST_CLIENT.get(f"/templates/{template_id}")
        result = rv.json()

        expected = {
            "message": "The specified template does not exist",
            "code": "TemplateNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_get_template_success(self):
        """
        Should return a template successfully.
        """
        template_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(f"/templates/{template_id}")
        result = rv.json()

        expected = util.MOCK_TEMPLATE_1
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_update_template_not_found(self):
        """
        Should return a http error 404 and a message 'specified template does not exist'.
        """
        template_id = "foo"

        rv = TEST_CLIENT.patch(f"/templates/{template_id}", json={})
        result = rv.json()

        expected = {
            "message": "The specified template does not exist",
            "code": "TemplateNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_template_given_name_already_exists(self):
        """
        Should return http status 400 and a message 'a template with given name already exists'.
        """
        template_id = util.MOCK_UUID_1
        template_name = util.MOCK_TEMPLATE_NAME_2
        rv = TEST_CLIENT.patch(
            f"/templates/{template_id}", json={"name": template_name}
        )
        result = rv.json()

        expected = {
            "message": "a template with that name already exists",
            "code": "TemplateNameExists",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_update_template_success(self):
        """
        Should update and return a template successfully.
        """
        template_id = util.MOCK_UUID_1
        template_name = "template-3"

        rv = TEST_CLIENT.patch(
            f"/templates/{template_id}", json={"name": template_name}
        )
        result = rv.json()

        expected = {
            "uuid": template_id,
            "name": template_name,
            "tasks": [
                {
                    "uuid": util.MOCK_UUID_1,
                    "task_id": util.MOCK_UUID_1,
                    "dependencies": [],
                    "position_x": 0.0,
                    "position_y": 0.0,
                }
            ],
            "experimentId": util.MOCK_UUID_1,
            "deploymentId": None,
            "createdAt": util.MOCK_CREATED_AT_1.isoformat(),
            "updatedAt": mock.ANY,
        }
        self.assertEqual(result, expected)
        self.assertEqual(rv.status_code, 200)

    def test_delete_template_not_found(self):
        """
        Should return a http error 404 and a message 'specified template does not exist'.
        """
        template_id = "unk"

        rv = TEST_CLIENT.delete(f"/templates/{template_id}")
        result = rv.json()

        expected = {
            "message": "The specified template does not exist",
            "code": "TemplateNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_delete_template_success(self):
        """
        Should delete template successfully.
        """
        template_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.delete(f"/templates/{template_id}")
        result = rv.json()

        expected = {"message": "Template deleted"}
        self.assertDictEqual(expected, result)

    def test_delete_multiple_templates_at_least_one_template_error(self):
        """
        Should return a http error 400 and a message 'inform at least one template'.
        """
        rv = TEST_CLIENT.post("/templates/deletetemplates", json=[])
        result = rv.json()

        expected = {
            "message": "inform at least one template",
            "code": "MissingRequiredTemplateId",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 400)

    def test_delete_multiple_templates_success(self):
        """
        Should delete templates successfully.
        """
        template_id_1 = util.MOCK_UUID_1
        template_id_2 = util.MOCK_UUID_2

        rv = TEST_CLIENT.post(
            "/templates/deletetemplates", json=[template_id_1, template_id_2]
        )
        result = rv.json()

        expected = {"message": "Successfully removed templates"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
