# -*- coding: utf-8 -*-
import unittest
import unittest.mock as mock

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestMonitoringFigures(unittest.TestCase):
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

    def test_list_figures_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        deployment_id = util.MOCK_UUID_1
        monitoring_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}/figures"
        )
        result = rv.json()
        expected = {"message": "The specified project does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_figures_deployment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = "unk"
        monitoring_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}/figures"
        )
        result = rv.json()
        expected = {"message": "The specified deployment does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_list_figures_monitoring_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        monitoring_id = "unk"

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}/figures"
        )
        result = rv.json()
        expected = {"message": "The specified monitoring does not exist"}
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    @mock.patch(
        "platiagro.list_figures",
        return_value=[],
    )
    def test_list_figures_success(
        self,
        mock_list_figures,
    ):
        """
        Should return a list of figures successfully.
        """
        project_id = util.MOCK_UUID_1
        deployment_id = util.MOCK_UUID_1
        monitoring_id = util.MOCK_UUID_1

        rv = TEST_CLIENT.get(
            f"/projects/{project_id}/deployments/{deployment_id}/monitorings/{monitoring_id}/figures"
        )
        result = rv.json()
        self.assertIsInstance(result, list)
        self.assertEqual(rv.status_code, 200)

        mock_list_figures.assert_any_call(
            deployment_id=deployment_id, monitoring_id=monitoring_id
        )
