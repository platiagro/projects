# -*- coding: utf-8 -*-
import unittest

from fastapi.testclient import TestClient

from projects.api.main import app
from projects.database import session_scope

import tests.util as util

app.dependency_overrides[session_scope] = util.override_session_scope
TEST_CLIENT = TestClient(app)


class TestOperatorParameters(unittest.TestCase):
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

    def test_update_parameters_project_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = "unk"
        experiment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1
        parameter_name = "foo"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}/parameters/{parameter_name}",
            json={},
        )
        result = rv.json()
        expected = {
            "message": "The specified project does not exist",
            "code": "ProjectNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_parameters_experiment_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = "unk"
        operator_id = util.MOCK_UUID_1
        parameter_name = "foo"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}/parameters/{parameter_name}",
            json={},
        )
        result = rv.json()
        expected = {
            "message": "The specified experiment does not exist",
            "code": "ExperimentNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_parameters_operator_not_found(self):
        """
        Should return an http status 404 and an error message.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        operator_id = "unk"
        parameter_name = "foo"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}/parameters/{parameter_name}",
            json={},
        )
        result = rv.json()
        expected = {
            "message": "The specified operator does not exist",
            "code": "OperatorNotFound",
        }
        self.assertDictEqual(expected, result)
        self.assertEqual(rv.status_code, 404)

    def test_update_parameters_success(self):
        """
        Should update and return a parameter successfully.
        """
        project_id = util.MOCK_UUID_1
        experiment_id = util.MOCK_UUID_1
        operator_id = util.MOCK_UUID_1
        parameter_name = "foo"
        value = "foo"

        rv = TEST_CLIENT.patch(
            f"/projects/{project_id}/experiments/{experiment_id}/operators/{operator_id}/parameters/{parameter_name}",
            json={"value": value},
        )
        result = rv.json()
        expected = "foo"
        self.assertEqual(expected, result)
        self.assertEqual(rv.status_code, 200)
